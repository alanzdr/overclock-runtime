#!/usr/bin/env python3
"""Compiles a Unity project's C# with dotnet, without the Unity editor.

Overclock Runtime preset for Unity. Several developers can validate at the same time: the editor is
not touched and each run builds in its own temp folder. Source files are taken from disk through the
globs in ASSEMBLIES, so a new .cs file counts even before Unity regenerates the .csproj files.

Adapt ASSEMBLIES to the project: one entry per .csproj Unity generates (one per asmdef, plus
Assembly-CSharp and Assembly-CSharp-Editor without asmdefs), with the folders that assembly compiles.
The .csproj files must exist (open the project in Unity once, or use "Regenerate project files").

Run (from the project root):
    python3 .claude/scripts/check.py --only Assets/Scripts/Player.cs,Assets/Tests/PlayerTests.cs
    python3 .claude/scripts/check.py           # every assembly
    python3 .claude/scripts/check.py --full    # same as above: the player build is QA's, in the editor

--only prints errors from those paths as ERROR; errors elsewhere print as OTHER and don't fail,
because they belong to another task in progress. Exit code: 0 if no error counts, 1 otherwise. Without
dotnet or without .csproj files, prints SKIP and exits 0.
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# project file -> (include globs, exclude globs). Adapt to the project's assemblies.
ASSEMBLIES = {
    "Assembly-CSharp.csproj": (["Assets/**/*.cs"], ["Assets/**/Editor/**/*.cs", "Assets/**/Tests/**/*.cs"]),
    "Assembly-CSharp-Editor.csproj": (["Assets/**/Editor/**/*.cs"], []),
}
ERROR = re.compile(r"^(?P<path>.+?)\((?P<line>\d+),\d+\): error (?P<code>\w+): (?P<msg>.+?)(?: \[.*\])?$")


def targets_file():
    groups = []
    for project, (include, exclude) in ASSEMBLIES.items():
        name = project.removesuffix(".csproj")
        groups.append(
            f"  <ItemGroup Condition=\"'$(MSBuildProjectName)' == '{name}'\">\n"
            f"    <Compile Include=\"{';'.join(include)}\" Exclude=\"{';'.join(exclude)}\" />\n"
            "  </ItemGroup>")
    return ("<Project>\n  <ItemGroup>\n    <Compile Remove=\"@(Compile)\" />\n  </ItemGroup>\n"
            + "\n".join(groups) + "\n</Project>\n")


def build(project, work):
    out = work / project.removesuffix(".csproj")
    cmd = ["dotnet", "build", project, "--nologo", "-v", "q", "-clp:ErrorsOnly;NoSummary",
           f"-p:CustomAfterMicrosoftCommonTargets={work / 'files.targets'}",
           f"-p:BaseIntermediateOutputPath={out}/obj/", f"-p:OutputPath={out}/bin/",
           "-p:BuildProjectReferences=true", "-p:UseSharedCompilation=false", "-m:1"]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--only", default="", help="comma-separated paths that count as this task's own")
    ap.add_argument("--full", action="store_true", help="same as no flag (the player build is QA's)")
    args = ap.parse_args()
    own = [p.strip() for p in args.only.split(",") if p.strip()]

    if shutil.which("dotnet") is None:
        print("SKIP compile: dotnet is not installed")
        return 0
    projects = [p for p in ASSEMBLIES if (ROOT / p).exists()]
    if not projects:
        print("SKIP compile: no .csproj files yet (open the project in Unity once)")
        return 0

    work = Path(tempfile.mkdtemp(prefix="overclock-compile-"))
    (work / "files.targets").write_text(targets_file())
    errors = {}
    try:
        for project in projects:
            result = build(project, work)
            lines = (result.stdout + result.stderr).splitlines()
            found = [m for m in map(ERROR.match, lines) if m]
            for m in found:
                path = Path(m["path"]).resolve()
                rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else m["path"]
                errors[(rel, m["line"], m["code"])] = m["msg"]
            if result.returncode != 0 and not found:
                print(f"FAIL {project}: dotnet failed without a compile error")
                print("\n".join(lines[-10:]))
                return 1
    finally:
        shutil.rmtree(work, ignore_errors=True)

    mine = {k: v for k, v in errors.items() if not own or any(k[0].endswith(p) for p in own)}
    others = {k: v for k, v in errors.items() if k not in mine}
    for (path, line, code), msg in sorted(mine.items()):
        print(f"ERROR {path}:{line} {code}: {msg}")
    for (path, line, code), msg in sorted(others.items()):
        print(f"OTHER {path}:{line} {code}: {msg}")
    print(f"{len(mine)} error(s) in scope, {len(others)} in other files")
    print("CHECK OK" if not mine else "CHECK FAILED")
    return 1 if mine else 0


if __name__ == "__main__":
    sys.exit(main())
