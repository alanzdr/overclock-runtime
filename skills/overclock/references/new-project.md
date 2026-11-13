# New project

The folder has no code yet. Everything starts from what the user wants, so this is the one mode where a
short interview is worth it.

## 1. Understand the idea

Start from what the user already said (the skill's argument, the conversation). Then ask, in **one**
`AskUserQuestion` round, only what is still missing among:

1. **What it is and for whom**, if it isn't clear: one line is enough to write `product.md`.
2. **Stack**, when the user has a preference. Offer a recommendation that fits the product (and say why);
   if the user has no preference, decide.
3. **Parts of the first version** (modules, screens, game areas): offer what you'd build first.
4. **Limits:** may the process spend money (paid APIs, image generation and its cap), publish (deploy,
   push), or create accounts? The default is no to all three until the user says otherwise.

Who designs: decide from the product (an app with screens → a UI designer; a game → a game designer and
art direction; a library or CLI → no designer) and record it as a `D#`.

## 2. Write the first docs

- `product.md`: what it is, its parts, its limits, what is out of scope. Real content, not the template's
  placeholders.
- `roadmap.md`: **C1 — Foundation** with the base everything else needs: the design base (if there is a
  designer), the scaffold of the stack with its scripts, the local environment, test infrastructure, and
  the app shell or first playable scene. Then one cycle per main part of the product, in the order that
  makes sense, each with a handful of items. The planner refines all of it; don't detail what it will
  plan.
- `architecture.md`: the stack and the intended folders and conventions, marked as "what C1 creates".
- `decisions.md`: the user's answers as `A#`, your choices as `D#`.

## 3. The config and the check

There are no commands yet. Write in `.claude/overclock.md` the commands C1 will create (from the stack's
preset) and say in "Project" that C1 creates them. Copy the preset's check script anyway: it reports
`SKIP` for tools that aren't installed yet and exits 0, so the first wave can run.
