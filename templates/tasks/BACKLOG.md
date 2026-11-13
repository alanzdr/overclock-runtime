# Backlog

Index of every task, by cycle and roadmap item, one table row per task. The planner adds the rows;
the status column is changed only by `overclock-task T### <status>`, which also updates the task
file. Open tasks live in `.claude/tasks/`, finished ones in `.claude/tasks/done/`.

<!--
Example (keep the column order: the scripts depend on it):

# C1

Inventory: 3 screens, 2 shared components.

## <roadmap item>

**Wave 1:** T001 · **Wave 2:** T002, T003

| Task | Title | Type | Status | Depends on |
|---|---|---|---|---|
| T001 | Shared contracts | contract | todo | — |
| T002 | Home screen | screen | todo | T001 |
-->
