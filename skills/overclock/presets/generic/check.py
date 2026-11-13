#!/usr/bin/env python3
"""Runs the project's own check commands with the Overclock Runtime contract.

Overclock Runtime preset for any stack. Fill STEPS with the project's commands. A command that can
be scoped to files gets `{files}` (replaced by the --only files that match its extensions); without
--only, `{files}` is replaced by `whole` (the command to run on the whole project). A step whose
tool is not installed prints SKIP and does not fail.

This generic version can't tell errors in your files from errors in other files: with --only it runs
the scoped commands only, and whole-project commands (like a type checker without per-file mode) are
skipped. Write a stack-specific check (see the other presets) when that matters.

Run (from the project root):
    python3 .claude/scripts/check.py --only src/app.py,tests/test_app.py
    python3 .claude/scripts/check.py           # every step, whole project
    python3 .claude/scripts/check.py --full    # plus the FULL steps (build)

Exit code: 0 if every step that ran passed, 1 otherwise.
"""
import argparse
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# name: (command with {files}, whole-project replacement for {files} or None if it can't be scoped,
#        file extensions it takes). Examples for a Python project:
STEPS = {
    "lint": ("ruff check {files}", ".", {".py"}),
    "tests": ("pytest -q {files}", "", {".py"}),
}
FULL = {
    # "build": "python -m build",
}


def run(name, command):
    tool = shlex.split(command)[0]
    if shutil.which(tool) is None:
        print(f"SKIP {name}: {tool} is not installed")
        return True
    proc = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        output = (proc.stdout + proc.stderr).strip().splitlines()
        print("\n".join(output[-60:]))
    print(f"{name}: {'ok' if proc.returncode == 0 else 'failed'}")
    return proc.returncode == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", help="comma-separated files, relative to the project root")
    ap.add_argument("--full", action="store_true", help="also run the FULL steps")
    args = ap.parse_args()
    only = [p.strip() for p in (args.only or "").split(",") if p.strip()]

    results = []
    for name, (command, whole, extensions) in STEPS.items():
        if only:
            files = [p for p in only if Path(p).suffix in extensions and (ROOT / p).exists()]
            if not files:
                print(f"SKIP {name}: no matching files in scope")
                continue
            results.append(run(name, command.format(files=" ".join(shlex.quote(f) for f in files))))
        elif whole is not None:
            results.append(run(name, command.format(files=whole)))
    if args.full and not only:
        results += [run(name, command) for name, command in FULL.items()]
    ok = all(results)
    print("CHECK OK" if ok else "CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
