---
name: overclock
description: Use when the user invokes /overclock, or wants to set up, adopt or update the Overclock Runtime autonomous process (planner, designers, developers, QA in parallel waves) in a new or existing project.
argument-hint: "[what the project is, for a new project]"
allowed-tools: Bash(overclock-show *), Bash(overclock-status), Bash(overclock-doc-sizes)
---

# Overclock setup

This skill prepares a project for the Overclock Runtime process and then gets out of the way: after it,
the user runs `/loop /overclock:run` and the crew works on its own. It creates the **project layer**
(config, docs, task files, permissions, a block in `CLAUDE.md`, the check script) that the plugin's
agents and the run skill read. The process itself lives in the plugin and is never copied into the
project.

Talk to the user in their language, and write every file you create in that language too (translate the
templates' prose); keep the fixed labels of the templates (field names like `Status:`, `Cycle:`,
`Files`, `Create:`/`Change:`, headings the scripts parse, file names) exactly as they are.

Plugin files (templates, references, stack presets) live outside the project: print them with
`overclock-show <path>` (`overclock-show --list` shows them all) instead of reading them, so nothing
stops to ask for permission.

## 1. Find the mode

- `.claude/overclock.md` exists → **update** mode: `overclock-show skills/overclock/references/update.md`.
- The folder is empty or nearly so (no source code, no manifest) → **new project**: 
  `overclock-show skills/overclock/references/new-project.md`.
- Otherwise → **existing project**: `overclock-show skills/overclock/references/existing-project.md`.

If the project already has a hand-made version of this kind of process (its own planner/developer agents
and a develop-style skill in `.claude/`), tell the user what you found and ask whether to keep those
files or remove them in favor of the plugin; never delete them without a yes.

Not a git repository? The process needs git (one commit per task). Run `git init` and say so.

## 2. Gather what the project layer needs

Follow the reference of the mode. The goal is to fill `templates/overclock.md` and
the first versions of the docs with real content, asking the user **only what you can't find or decide**:

- Decide and proceed (the rule the whole process runs on). What you decide becomes a `D#` line in
  `decisions.md`; what the user answers becomes an `A#` line.
- Ask in one round, with `AskUserQuestion`, at most 4 questions, each with a recommended option. Good
  questions are about intent and limits (what the product is for, what is out of scope, money, publishing),
  not about things the code or a sensible default answers.

## 3. Create the project layer

Print `skills/overclock/references/project-layer.md` and create everything it lists. In short:

| File | From |
|---|---|
| `.claude/overclock.md` | `templates/overclock.md`, filled in |
| `.claude/docs/product.md`, `architecture.md`, `roadmap.md`, `decisions.md` | `templates/docs/` |
| the designer's docs (`design-system.md` for an app; the project's equivalents for a game or other) | `templates/docs/design-system.md` or written for the domain |
| `.claude/tasks/BACKLOG.md`, `BUGS.md`, `IMPROVEMENTS.md`, `QUESTIONS.md`, `logs/`, `done/` | `templates/tasks/` |
| `.claude/scripts/check.py` (or the project's own check command) | a preset in `presets/`, adapted |
| `.claude/settings.json` | merged with the preset's permissions (never overwrite what is there) |
| `CLAUDE.md` | the block from `templates/CLAUDE-block.md`, between its markers |
| `.gitignore` | add `.claude/qa/` |

## 4. Verify

- `overclock-status` reports the project and the first cycle.
- Run the "Check everything" command once. In an existing project it may fail on errors that already
  exist: that is fine, but say so, and add them to `BUGS.md` for the first cycle.
- `overclock-doc-sizes` passes.
- Re-read `.claude/overclock.md` as an agent who never saw the project: could you work from it?

## 5. Commit and hand over

Commit **only the files this skill created or changed**, by path (`git add <paths>`), with a message like
"Set up Overclock Runtime". Leave the user's own pending changes alone. Don't push.

Then tell the user, briefly:
- what was created and the main decisions you made (`D#`), and what they decided (`A#`);
- what they may want to review before starting (usually `product.md` and the first cycle of
  `roadmap.md`);
- that Claude Code only applies the project's permissions in a trusted folder: if this session started
  without the trust dialog (a headless run, for example), open the project interactively once and accept
  it, or the agents will be asked about every write in `.claude/`;
- how to run: `/loop /overclock:run` (or `/overclock:run` for a single step), how to give feedback
  (`/overclock:feedback`), and how to hold the process (`[paused]` in a cycle title).
