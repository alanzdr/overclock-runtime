# Roadmap

## How the roadmap works

- Each `## C<N> — <name>` section is a **cycle**: one full turn of planner → designers and developers
  in parallel waves → QA.
- `/overclock:run` follows the cycles in file order without waiting for approval. It marks an item
  `[x]` when all its tasks are done.
- Each cycle starts with the planner, which creates the tasks from its items and from what the previous
  cycle left in `.claude/tasks/BUGS.md` and `.claude/tasks/IMPROVEMENTS.md`.
- When every item of a cycle is done, QA runs the whole app and logs bugs and improvements. The next
  cycle fixes them.
- **The roadmap belongs to Claude.** The planner may split, reorder and add items and cycles to reach
  what `product.md` describes. When the planned cycles run out and high or medium bugs or improvements
  remain, it creates the next cycle.
- **To hold the process, the user writes `[paused]` in a cycle title:** the process does not enter it or
  any cycle after it.

## C1 — Foundation

- [ ] <first items: design base, scaffold, local environment, test infrastructure, app shell…>
