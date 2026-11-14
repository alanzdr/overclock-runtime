---
name: run
description: Use when the user invokes /overclock:run (often as /loop /overclock:run), or asks to move the roadmap forward, run the next step, or let the crew work on its own in a project set up by /overclock.
allowed-tools: Bash(overclock-show *), Bash(overclock-status), Bash(overclock-task *), Bash(overclock-plan-check *), Bash(overclock-doc-sizes)
---

# Overclock run

This skill **drives the flow** and does none of the specialists' work: **it doesn't read code or diffs,
doesn't write or refine tasks, doesn't design, implement or test.** It reads the state, decides the next
step, calls the right agent with the task's path, records and commits. That keeps its context small in a
long loop.

A **cycle** (`C1`, `C2`…) is a full turn: the planner creates the tasks, designers and developers build
them in waves, and QA tests everything at the end. The next cycle starts again with the planner, which
turns QA's bugs and improvements into tasks along with the next roadmap items.

Each invocation runs **one step**: a planning, **or** a wave of tasks taken to `done` (or `blocked`),
**or** the cycle's QA. A wave is the set of free tasks that run together: ten tasks with their own files
are ten agents working at the same time. **No idle time between steps:** when a step ends, start the next
one right away, in the same turn, from the pre-checks. Only "When to stop" ends the chain.

Write logs, questions and commit messages in the language the project uses. If the project is not set up
(no `.claude/overclock.md`), say so and point to `/overclock`.

## Agents

Call them with the Agent tool, as `overclock:planner`, `overclock:designer`, `overclock:developer` and
`overclock:qa`, with short, self-contained prompts: the agent doesn't see this conversation; what it
needs is in the task and the docs. Inside a task, one agent at a time; across the tasks of a wave, all at
once, in a single message.

| Agent | When | Prompt |
|---|---|---|
| `planner` | Start of each cycle, and only there | `Plan cycle C<N> of .claude/docs/roadmap.md.` |
| `designer` | Task with a `(designer)` file, before the developer | `Design .claude/tasks/T###-slug.md.` |
| `developer` | Implement or fix | `Implement .claude/tasks/T###-slug.md.` / `Fix in .claude/tasks/T###-slug.md the check errors: <output>` |
| `qa` | End of the cycle, and only there: no task | `Analyze cycle C<N>.` |

Agents run in the background and notify when they finish. On each notification, **advance only that
agent's task** and continue the same step. If the report isn't in the notification, read it from the task.
Keep each task's developer id: fixes go to the **same** developer with `SendMessage` (it has the context).
If the id is lost (new step), call a new developer with the fix prompt.

**Model and effort.** The defaults come from each agent's file. Pass `model`/`effort` only when:
`.claude/overclock.md` ("Roles" → "Models") overrides a role; the task has `Designer effort` (pass it as
`effort`; for `global`, pass `model: "fable"` and `effort: "high"`); the task has `Developer effort` (pass
it as `effort`, also on fix rounds). Name the model in the prompt's first line when you override it.

**When a model runs out.** Plans can have separate usage limits per model (Fable has its own weekly
limit), and Claude Code doesn't switch models on a usage limit: the agent just fails ("Agent terminated
early due to an API error", with a usage, rate or quota limit in the detail) or comes back cut off. Then:

1. Call the same agent again for the same work, one step down: `fable` → `opus` → `sonnet` (pass `model`;
   keep the `effort`). Add to the prompt: "A previous attempt was cut off by a usage limit: check what it
   already wrote and finish or fix it."
2. Keep using the lower model for that role for the rest of the session; write in the step log
   `Model limit: <model> → <fallback> (<role>)`, with the reset time if the error shows one.
3. A limit on the lowest model, or on every model, is not a failure of the task: stop (see "When to
   stop") with a `## Notice: usage limit` in `QUESTIONS.md` saying when it resets. Don't mark tasks
   `blocked` for it.

## Files you read and write

- `.claude/docs/roadmap.md`: only the cycle titles and the checkboxes; you mark `[x]` when an item is done.
- `.claude/tasks/BACKLOG.md` and the open tasks: only the top fields, the "Files" section (decides
  parallelism and who goes in), the file lists in the designer's return and the developer's last report
  (to commit), and the Result section. Status changes only through `overclock-task T### <status>`.
- `.claude/tasks/logs/` (one file per step: `YYYY-MM-DD-NN-description.md`, `NN` in sequence within the
  day) and `.claude/tasks/QUESTIONS.md`.
- `BUGS.md` and `IMPROVEMENTS.md`: agents write in them; you only delete what a finished task solved.
- The version, at the end of each cycle, where `.claude/overclock.md` says.
- `overclock-status` shows the current cycle and open tasks; `overclock-plan-check C<N>` shows the waves.

## Step

### 0. Pre-checks

- **Repository without commits** (`git log -1` fails): check with `git status --short` that no file the
  config protects shows up, and make the initial commit with everything.
- Branch from `.claude/overclock.md`. If it is another one, **stop** and write in `QUESTIONS.md`: the
  user may be working there.
- `git status --short`: pending changes are only acceptable when a task is in progress (`design`, `dev`).
  Otherwise **stop** and write in `QUESTIONS.md` (they may be the user's; never discard or commit them).
  Exception: changes only in `BUGS.md`, `IMPROVEMENTS.md`, `QUESTIONS.md` or `.claude/docs/` are the
  user's feedback: commit them ("Record the user's feedback") and continue.
- New answers in `QUESTIONS.md`: unblock the tasks they free (`overclock-task T### todo`).
- **Circuit breaker:** read the last two step logs. If both say `Progress: no`, or the same check error
  came back in both, **stop** (see "When to stop") instead of trying a third time.

### 1. Current cycle

Look at the `## C<N> …` sections of the roadmap, in file order. A section with `[paused]` in its title is a
limit: it and the ones after it don't enter.

1. If the last cycle with every item `[x]` has no `*-qa-c<N>.md` log yet, go to 2b.
2. Otherwise the current cycle is the first one with `- [ ]` items. Skip a planned cycle whose open tasks
   are **all** `blocked` (note it in `QUESTIONS.md` and go to the next).
3. If no cycle has open items: is there an open line in `BUGS.md`, or a `[high]` or `[medium]` one in
   `IMPROVEMENTS.md`? Then the current cycle is `C<last + 1>`, which the planner creates (2). Otherwise
   go to "When to stop".

**Finishing a cycle is not a reason to stop.** After QA, the next step goes straight to the next cycle.

### 2. Plan, if needed

Call the `planner` when the current cycle has no open task in `BACKLOG.md` (`todo`, `design`, `dev`,
`blocked`) and still has `- [ ]` items (or doesn't exist yet, case 3 above), or when its last return said
`STILL TO PLAN`. Then: check that `overclock-plan-check C<N>` exits 0 (if not, send its output back to the
planner), write the step log, commit (`Plan C<N>: T###–T###`) and go straight to the next step.

### 2b. QA at the end of the cycle

QA is not a task or a roadmap item: you call it when **every item of the cycle is `[x]`** and there is no
`*-qa-c<N>.md` log yet. It runs alone, with no task in progress: `Analyze cycle C<N>.` When it returns:

1. Write the log `YYYY-MM-DD-NN-qa-c<N>.md` with its return.
2. Bump the version as `.claude/overclock.md` says (usually `0.<N>.0`), if the project has one.
3. Commit everything (`QA of C<N>: <N> bugs, <N> improvements`).
4. Add to `QUESTIONS.md` a `## Notice: C<N> ready to see` block with QA's "HOW TO SEE", the decisions the
   cycle made (`D#`) and anything that needs the user's eyes.

A `blocked` return (the environment won't come up): note what is missing in `QUESTIONS.md` and go to
"When to stop". The cycle is over even with open bugs: the next step goes on to the next cycle.

### 3. Build the wave

First the tasks in progress (`design`, `dev`), resuming where they stopped. Then **every** `todo` task of
the current cycle whose dependencies are `done`, in any number, as long as:

- **no two agents touch the same file:** compare the "Files" sections; between two that collide, the
  first goes in and the other waits for the next wave;
- **an `Exclusive: yes` task runs alone**, between waves (QA too).

If none is free and some are `blocked`, go to "When to stop".

**One working tree, no worktrees.** So:

- **Commit only the task's files:** never `git add -A` while another task is in progress. Add by path the
  files from the designer's return and the developer's report, the task file in both places
  (`.claude/tasks/T###-*.md` and `.claude/tasks/done/T###-*.md`, since it moved) and the process files
  (`BACKLOG.md`, `BUGS.md`, `IMPROVEMENTS.md`, the log, `roadmap.md`). Check with `git status --short`
  that what is left belongs to the other tasks.
- Never stash while tasks are in progress. A task out of fix rounds:
  `git stash push -u -m "T### blocked" -- <task files>`, always by path.
- A `blocked` task doesn't stop the others.
- **The plan doesn't need to be perfect.** If too much goes wrong at once (tasks that don't fit together,
  chained collisions), finish the tasks as they are and write what went wrong in `BUGS.md`: the next
  cycle's planner solves it.

### 4. Take a task to the end

1. **`design`** (only with a `(designer)` file): the `designer` does its files and the Design section.
   `QUESTION` (only rule-1 exceptions) → task `blocked`, question in `QUESTIONS.md` with the options and
   the recommendation; the other tasks go on. A task with only designer files goes straight to "Close".
2. **`dev`**: the `developer`. `blocked` → task `blocked` (reason in the task and in `QUESTIONS.md`).
   `out of scope` (from the developer or the designer): is the requested file in a task in progress? If
   not, free it with `SendMessage` and the agent continues. If it is, wait for that task to finish and
   free it then. A dependency or generator request: free it when no other task is in progress (it is an
   exclusive command), or leave it for the end of the wave. A new file outside the list needs no release.
3. The developer returned `done` with the check at 0 → **Close**. There is no code review between tasks:
   the full check at the end of the wave and QA at the end of the cycle look at the whole.

### 5. Close a task

1. Write the Result in the task (1–3 lines and the commit) and mark it `done` with `overclock-task`, which
   updates `BACKLOG.md` and moves the file to `done/`.
2. **Roadmap:** if every task of the item ("Roadmap item" field) is `done`, mark the item `[x]`. If every
   item of the cycle is `[x]`, the next step is QA (2b).
3. **One commit** (only this task's files; see 3), in the format of `.claude/overclock.md`, ending with the
   standard co-author line. Check with `git status --short` that no protected file went in. You don't need
   to read the diff.
4. Delete from `BUGS.md` and `IMPROVEMENTS.md` the lines the task solved (`→ T###`).

**When the whole wave ends**, run the "Check everything" command. With all tasks together it must exit 0.
If it fails: find which task owns each failing file (its "Files" and reports), add 1 to its "Fix rounds"
and send its developer the output (different tasks fix in parallel); run the check again and commit the
fix (`T###: fix check errors (C<N>)`). Past **2** rounds on a task, or an error that belongs to no task:
note it in `BUGS.md` as `[critical]`, with the output, and move on.

Then write the step log: the wave's tasks with result and commit, fix rounds, the full check result, the
decisions agents recorded (`D#`), the bugs fixed and improvements made (the lines that left `BUGS.md` and
`IMPROVEMENTS.md`), and the notes agents left for later tasks or cycles (write "For T###" or "For C<N>" so
a `grep` finds them). End it with `Progress: yes` if any task reached `done` (or a plan or QA was
committed), `Progress: no` otherwise. Commit the log.

## With `/loop`: the wakeup is only a backup

- Steps chain on their own; the wakeup is **not** what moves the process. It only exists to resume the
  loop if something hangs (an agent's notification never arrives).
- Whenever you wait for agents, leave a single backup wakeup with the prompt `/loop /overclock:run` at the
  maximum delay. Never schedule short wakeups between steps.
- If a wakeup fires while an agent is still running, don't call another one for the same task or start
  another step: schedule the backup again and end the turn.
- On "When to stop", end the loop (`ScheduleWakeup` with `stop: true`).

## When to stop

The loop **doesn't stop on its own** while there is work: the end of a cycle, a `blocked` task or a
question in `QUESTIONS.md` don't stop it. Stop **only** when:

- the user says so; or
- nothing is left: no cycle (before the first `[paused]`) with an open item that can move, no open line in
  `BUGS.md`, and only `[low]` lines in `IMPROVEMENTS.md` (or everything left is `blocked` or depends only
  on the user). Note in `QUESTIONS.md` what needs unblocking; or
- every model a role can fall back to hit its usage limit (see "When a model runs out"); or
- a pre-check says so (wrong branch, pending changes with no task in progress, circuit breaker), QA
  returns `blocked`, or the project is broken by something no task solves.

When stopping, write a step log with a summary of the state and point to `QUESTIONS.md`.

## Rules

- Never `git push`, merge, rebase or reset; never discard or commit changes that belong to no task (except
  the user's feedback, in 0).
- **Publish nothing:** no deploy, no new external service, no account, unless `.claude/overclock.md`
  allows it.
- Open decisions follow rule 1 of `CLAUDE.md`: agents decide and proceed. `QUESTIONS.md` is only for its
  exceptions; don't stop the loop over a decision an agent could make.
- Never edit the app's code, its data, the product, architecture and design docs, or the content of the
  tasks: that is the agents' work.
- If an agent hangs or returns without a report, call another for the same task once; if it repeats, mark
  the task `blocked` with the reason and move on. A usage limit is not this case: see "When a model runs
  out".
