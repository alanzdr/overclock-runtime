# Questions for the user

Only what really needs the user (the exceptions in the CLAUDE.md rules): money, accounts, keys or paid
dependencies; publishing anything; something hard to undo; something that contradicts a decision of
the user; and process warnings (wrong branch, pending changes that belong to no task). Claude's own
decisions do **not** come here: they are in the docs and in `.claude/docs/decisions.md`.

Each question is a `## <title>` block with: what is blocked, the options, and Claude's recommendation.
To answer, write a line starting with `**Answer` under the question (or use `/overclock:feedback`); the
process unblocks the tasks on its next step. Blocks titled `Notice: …` (for example, "a cycle is ready
to look at") need no answer.
