---
name: feedback
description: Use when the user invokes /overclock:feedback, or, in a project set up by /overclock, says how they want something ("make the header more compact", "change the accent color", "this is broken", "don't use that library", "do it another way"), or answers a question from .claude/tasks/QUESTIONS.md.
---

# Overclock feedback

In an Overclock project, Claude decides everything and proceeds, **until the user says otherwise**. This
skill is the way that "otherwise" enters the process: what the user asks is written where the agents
read it, and from then on it wins over any decision of Claude's.

It only records. It doesn't implement, create tasks or call agents: the next cycle's planner turns what
is in `BUGS.md` and `IMPROVEMENTS.md` into tasks. If the user wants the change right now, outside the
process, do it directly in the conversation instead of using this skill.

Write in the language the project uses.

## Where each thing goes

| What the user said | Where to record it |
|---|---|
| Something doesn't work or came out wrong | `.claude/tasks/BUGS.md`, in the current cycle's section, in the file's format, with severity and `(user)` |
| Wants something different, better or extra in something that exists | `.claude/tasks/IMPROVEMENTS.md`, in the current cycle's section, always `[high]`, with `(user)` |
| A decision that holds from now on (look, product, technical, process) | In the doc of the subject (design docs, `product.md`, `architecture.md`, `roadmap.md`, `.claude/overclock.md`, `CLAUDE.md`) **and** one line in `.claude/docs/decisions.md`, in "Decided by the user" (`A#`, the decision in one sentence, date, where the detail is) |
| A new feature or screen | `product.md` and an item in the right cycle of `roadmap.md` |
| An answer to a question | Under the question in `.claude/tasks/QUESTIONS.md`, as a line starting with `**Answer`; if it is a decision, also as above |
| Hold or release the process | `[paused]` in a cycle title in `roadmap.md` (add or remove) |

One request may land in more than one row: "swap the gold for blue" is a decision (design docs + `A#`) and
a `[high]` improvement for the screens that already use the gold.

## Rules

1. Write what the user said, without widening it. If it is too vague to become a task ("make it
   prettier"), ask once what bothers them; if they don't want to detail it, record it as is and let the
   designer interpret.
2. A decision of the user that changes one of Claude's (`D#`): apply it in the doc of the subject, mark the
   `D#` line as "replaced by A# on <date>", and note in `IMPROVEMENTS.md` what was already built and needs
   adjusting.
3. A new decision of the user that contradicts an older one of theirs (`A#`): show the conflict and ask
   which one holds before writing.
4. Look for the same subject in the other docs and keep everything consistent (`grep` the keyword in
   `.claude/docs/`, `.claude/overclock.md` and `CLAUDE.md`).
5. The design docs belong to the designer, but you write the user's visual decisions there, in a
   "Decisions of the user" section at the top, for the designer to apply everywhere else.
6. Don't commit: `/overclock:run` commits the feedback on its next step. If the process isn't running and
   the user asks, commit only these files ("Record the user's feedback").

## Output

Say in a few lines what was recorded and where, and in which cycle it should become a task.
