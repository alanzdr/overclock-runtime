<!-- overclock:begin (managed by /overclock; edit the text, keep the markers) -->
## How work runs here (Overclock Runtime)

This project runs on the Overclock Runtime process: `/loop /overclock:run` takes the roadmap through
cycles. Each cycle is planner → designers and developers in parallel waves → QA, and the next cycle's
planner turns QA's bugs and improvements into tasks. Project config: [.claude/overclock.md](.claude/overclock.md).

| Subject | File |
|---|---|
| What the product is, its parts, its limits | [.claude/docs/product.md](.claude/docs/product.md) |
| Stack, folders, conventions, shared files | [.claude/docs/architecture.md](.claude/docs/architecture.md) |
| Look, design system, design specs | [.claude/docs/design-system.md](.claude/docs/design-system.md) |
| Cycles and items | [.claude/docs/roadmap.md](.claude/docs/roadmap.md) |
| Who decided what, and when | [.claude/docs/decisions.md](.claude/docs/decisions.md) |
| Tasks, bugs, improvements, questions | [.claude/tasks/](.claude/tasks/) |

### Rules for Claude

1. **Decide and proceed instead of stopping to ask.** For an open product, design or technical
   decision, pick what you recommend, record it and continue. Doing first and changing later beats
   waiting for an answer.
   - Record it: the content goes in the doc of the subject; `decisions.md` gets one short line (`D#`,
     the decision in one sentence, date, who/task, where the detail is). Never write the same text in
     both. Small implementation details need no record.
   - Prefer the simplest option, the easiest to change later. Decide only what blocks the work now.
   - **Stop and ask only** when it involves money, accounts, keys or paid dependencies; publishes
     something (deploy, push, a new external service receiving our data); is hard to undo (deleting
     data, rewriting git history); or contradicts a decision of the user. Then write it in
     `.claude/tasks/QUESTIONS.md` and continue with the rest.
2. **The user's decisions are not contradicted.** They are the `A#` rows of `decisions.md` and hold
   until the user changes them. New requests, corrections and decisions come in through
   `/overclock:feedback`.
3. **Always aim at the final version.** No placeholder screens, filler text or temporary hacks: every
   delivery handles its loading, empty and error states and follows the design.
4. **Small, testable changes.** Pure domain logic with a unit test next to it. Each task delivers in
   its own files.
5. **One commit per finished task**, only with that task's files, following `.claude/overclock.md`.
6. **Language:** write docs, tasks, logs and commits in the language the user works in; code follows
   the project's conventions.
<!-- overclock:end -->
