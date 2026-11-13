"""Shared helpers for the Overclock Runtime commands in bin/.

Everything here reads the project layer that /overclock creates:
  .claude/overclock.md          project config (its presence marks an initialized project)
  .claude/docs/roadmap.md       cycles (## C<N> ...) with - [ ] / - [x] items
  .claude/tasks/T###-slug.md    open tasks; finished ones live in .claude/tasks/done/
  .claude/tasks/BACKLOG.md      one table row per task: | T### | title | type | status | deps |
  .claude/tasks/QUESTIONS.md    ## blocks; a block is answered once it has a line starting with **Answer
  .claude/tasks/logs/           one file per step; the QA of cycle N writes *-qa-c<N>.md

Labels in these files are fixed (in English) so the scripts can parse them; the prose around
them is written in whatever language the project uses.
"""
import re
from pathlib import Path

STATUSES = ("todo", "design", "dev", "done", "blocked")
OPEN_STATUSES = {"todo", "design", "dev"}
FIELD = r"^- \*\*{}:\*\*[ \t]*(.*)$"
CYCLE_HEADING = re.compile(r"^## (C\d+)\b(.*)$", re.M)
PAUSED = "[paused]"


def find_root(start=None):
    """Walks up from `start` (default: cwd) to the folder holding .claude/overclock.md.

    Returns that folder, or None if no parent is an Overclock project.
    """
    here = Path(start or Path.cwd()).resolve()
    for folder in (here, *here.parents):
        if (folder / ".claude" / "overclock.md").is_file():
            return folder
    return None


def require_root():
    root = find_root()
    if root is None:
        raise SystemExit("not an Overclock project: no .claude/overclock.md here or above (run /overclock)")
    return root


def tasks_dir(root):
    return root / ".claude" / "tasks"


def field(text, name):
    m = re.search(FIELD.format(re.escape(name)), text, re.M)
    return m.group(1).strip() if m else ""


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def task_files(root, include_done=False):
    folder = tasks_dir(root)
    files = sorted(folder.glob("T[0-9]*-*.md"))
    if include_done:
        files += sorted((folder / "done").glob("T[0-9]*-*.md"))
    return files


def task_id(path):
    return path.name.split("-")[0].upper()


def status_of(text):
    value = field(text, "Status")
    return value.split()[0].lower() if value else ""


def parse_task(path):
    text = path.read_text(encoding="utf-8")
    files = section(text, "Files")
    return {
        "id": task_id(path),
        "path": path,
        "status": status_of(text),
        "cycle": field(text, "Cycle").split()[0] if field(text, "Cycle") else "",
        "type": field(text, "Type"),
        "deps": set(re.findall(r"T\d+", field(text, "Depends on"))),
        "exclusive": field(text, "Exclusive").lower().startswith("yes"),
        "create": set(re.findall(r"^- Create: `([^`]+)`", files, re.M)),
        "change": set(re.findall(r"^- Change: `([^`]+)`", files, re.M)),
        "unowned": re.findall(r"^- (?:Create|Change): `([^`]+)`(?! \((?:designer|developer)\))", files, re.M),
        "scope": section(text, "Scope").strip(),
    }


def roadmap_cycles(root):
    """Returns the roadmap cycles in file order: dicts with id, title, paused, open, done."""
    path = root / ".claude" / "docs" / "roadmap.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    heads = list(CYCLE_HEADING.finditer(text))
    cycles = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        cycles.append({
            "id": m.group(1),
            "title": m.group(2).strip(" —-:"),
            "paused": PAUSED in m.group(0).lower(),
            "open": len(re.findall(r"^- \[ \]", body, re.M)),
            "done": len(re.findall(r"^- \[x\]", body, re.M | re.I)),
        })
    return cycles


def active_cycles(root):
    """Cycles before the first paused one."""
    active = []
    for cycle in roadmap_cycles(root):
        if cycle["paused"]:
            break
        active.append(cycle)
    return active


def has_qa_log(root, cycle_id):
    logs = tasks_dir(root) / "logs"
    return any(logs.glob(f"*-qa-{cycle_id.lower()}.md"))


def open_questions(root):
    path = tasks_dir(root) / "QUESTIONS.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = re.split(r"^## ", text, flags=re.M)[1:]
    titles = []
    for block in blocks:
        title = block.splitlines()[0].strip()
        if title.lower().startswith("notice") or re.search(r"^\*\*Answer", block, re.M):
            continue
        titles.append(title)
    return titles


def next_task_id(root):
    numbers = [int(task_id(p)[1:]) for p in task_files(root, include_done=True)]
    backlog = tasks_dir(root) / "BACKLOG.md"
    if backlog.is_file():
        text = re.sub(r"<!--.*?-->", "", backlog.read_text(encoding="utf-8"), flags=re.S)
        numbers += [int(n) for n in re.findall(r"^\| T(\d+) \|", text, re.M)]
    return f"T{max(numbers, default=0) + 1:03d}"
