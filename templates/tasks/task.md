# Task format

The planner creates `.claude/tasks/T###-slug.md` from this format. Each role writes **only in its own
section**; the developer report grows one round at a time (`### Round 1`, `### Round 2`…) and never
erases the previous one.

The labels in this format are fixed, in English: `overclock-task` and `overclock-plan-check` parse
them. Everything you write after a label or under a heading is in the project's language.

## Status (the `Status` field and the BACKLOG column)

`todo` → `design` → `dev` → `done`. Any step can become `blocked` (reason in "Result" and in
`QUESTIONS.md`). `design` only exists in tasks with a `(designer)` file; the others go from `todo`
straight to `dev`. A task with only `(designer)` files goes from `design` straight to `done`.

## Types

| Type | When |
|---|---|
| `screen` | One screen, route, scene or level, and the parts only it uses |
| `component` | A part shared by several screens or scenes |
| `logic` | Pure domain logic, testable without running the app |
| `data` | Data pipeline, schema, migrations, API routes, persistence |
| `design` | Design only: design docs, tokens, specs, art, images |
| `tooling` | Config, scripts, test infrastructure |
| `contract` | First-wave task with the shared types, signatures and skeletons other tasks build on |
| `integration` | Joins what several tasks delivered into a shared file; depends on all of them |

## Fields

- **Exclusive:** `yes` only if the task uses something nothing else may touch at the same time: it
  installs dependencies, generates a migration, regenerates shared data, or holds an exclusive
  resource listed in `.claude/overclock.md`. Exclusive tasks run alone, between waves.
- **Designer effort:** only in tasks with a `(designer)` file. `global` changes the base of the design
  (identity, palette, typography, art direction) and runs on the strongest model; `high` sets the
  pattern for a whole area; `medium` follows existing patterns; `low` is a small local adjustment.
  When in doubt, pick the higher one.
- **Developer effort:** only in tasks with a `(developer)` file. `low` when the Scope gives the whole
  recipe and the developer only executes; `medium` when they must measure, investigate or choose.
  When in doubt, `medium`. Fix rounds use the same effort.

## Template

```markdown
# T### — <title>

- **Status:** todo
- **Cycle:** C1
- **Type:** screen | component | logic | data | design | tooling | contract | integration
- **Roadmap item:** <text of the roadmap item>
- **Depends on:** T###, T### (or —)
- **Exclusive:** yes | no
- **Designer effort:** global | high | medium | low
- **Developer effort:** medium | low
- **Fix rounds:** 0

## Goal
<1–3 sentences: what and why>

## Scope
<planner: what to do, in words: what each file must contain, the cases that matter, what to reuse and
where the example to follow is. No code, no pseudocode.>
- Out of scope: <what NOT to do>

## Files
Closed list, with who does each file. Each agent touches only its own; this list decides which tasks
run together. If there is a `(designer)` file, the designer goes first.
- Create: `path/to/new-file` (designer)
- Create: `path/to/other` (developer)
- Change: `path/to/existing` (developer)

## Interfaces
Names shared with other tasks, so producer and consumer can work at the same time.
- Produces: <component, function, type, table, route, message key… and what it does, in words>
- Consumes: <what it uses from another task, and from which one>

## Acceptance criteria
- [ ] <verifiable by reading and by the check command>
- [ ] tests: <unit tests for the new pure logic>

## Notes
<doc links, traps; what can only be proven with the app running, for QA, with the exact steps>

## Design
<designer, before the developer (only with a (designer) file): what was delivered, what the developer
needs to know, and "How to verify">

## Developer report
<developer, one subsection per round>

## Result
<process, when closing: 1–3 lines + commit>
```
