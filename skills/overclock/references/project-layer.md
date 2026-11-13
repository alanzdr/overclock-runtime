# The project layer

Everything the plugin's agents read in the project. Templates are in `${CLAUDE_PLUGIN_ROOT}/templates/`;
write their prose in the project's language and keep their fixed labels.

## Files

```
CLAUDE.md                     the Overclock block, between <!-- overclock:begin --> and <!-- overclock:end -->
.claude/overclock.md          the config (templates/overclock.md); its frontmatter `overclock:` is the
                              plugin version that wrote it (read it from ${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json)
.claude/settings.json         permissions, merged (below)
.claude/scripts/check.py      the check command (below), unless the project already has one that fits
.claude/docs/product.md       templates/docs/product.md
.claude/docs/architecture.md  templates/docs/architecture.md
.claude/docs/roadmap.md       templates/docs/roadmap.md
.claude/docs/decisions.md     templates/docs/decisions.md
.claude/docs/<designer docs>  design-system.md for an app (templates/docs/design-system.md); for a game,
                              the docs its designer owns (e.g. game-design.md, art-direction.md, story.md),
                              listed in the config's "Roles"; none without a designer
.claude/docs/design/          screen specs (created by the designer later; make the folder only)
.claude/tasks/BACKLOG.md      templates/tasks/BACKLOG.md
.claude/tasks/BUGS.md         templates/tasks/BUGS.md (+ the failures found while setting up, in C1)
.claude/tasks/IMPROVEMENTS.md templates/tasks/IMPROVEMENTS.md
.claude/tasks/QUESTIONS.md    templates/tasks/QUESTIONS.md
.claude/tasks/logs/.gitkeep
.claude/tasks/done/.gitkeep
.claude/roles/                optional: <role>.md with project rules for one role (planner, designer,
                              developer, qa); create one only when a rule really belongs to a single role
```

The task format is not copied: agents read it from the plugin (`templates/tasks/task.md`).

## CLAUDE.md

- No `CLAUDE.md`: create one with a short title and description of the project, then the block.
- An existing `CLAUDE.md` (or an `AGENTS.md` that `CLAUDE.md` imports): keep the user's text and append the
  block at the end. If the markers already exist, replace only what is between them.
- In the block's table, point the design row at the designer's real docs (or drop it without a designer).
- Rules that apply to everything in this project and are not in the block (language conventions of the
  code, a framework's traps) go in the user's part of `CLAUDE.md`, briefly; their detail goes in
  `architecture.md`.

## Permissions (`.claude/settings.json`)

Plugins can't ship permissions, so the project gets them here. Merge, never overwrite: read the existing
file, add the missing rules to `permissions.allow` and `permissions.deny`, keep everything else.

1. Always: the rules in `${CLAUDE_SKILL_DIR}/presets/base-settings.json` (the `overclock-*` commands, the
   check script, read-only git and the commit commands, the process folders; and the deny list for
   history-rewriting git commands).
2. The stack preset's `settings.json` (package manager, test runners, local services).
3. Deny reading and editing every secrets file the project has (`.env`, `.env.prod`, credentials).
4. Plugin activation, so collaborators get it too:
   `"enabledPlugins": { "overclock@overclock-runtime": true }` and
   `"extraKnownMarketplaces": { "overclock-runtime": { "source": { "source": "github", "repo": "alanzdr/overclock-runtime" } } }`.

## The check command

Every role validates with the same command, so its contract matters more than its implementation:

- `<check> --only a.ts,b.ts` — type-check, lint and unit tests **scoped to those files**, without starting
  the app. Prints problems in those files as `ERROR …` and problems in other files as `OTHER …` (they
  belong to tasks still in progress in the shared tree). Exit 0 when nothing in scope fails.
- `<check>` — the same for the whole project. Exit 0 only when everything passes.
- `<check> --full` — the above plus the production build (QA).
- A tool that isn't installed yet prints `SKIP` and doesn't fail (so C1 can start from an empty folder).
- Fast: it runs after every task. Never starts servers, never needs network.

Presets in `${CLAUDE_SKILL_DIR}/presets/`, each with a `check.py` and a `settings.json`:

| Preset | For |
|---|---|
| `nextjs-bun` | TypeScript web apps: `tsc`, ESLint, Vitest, `next build` (swap the tools for the project's: npm/pnpm, Jest, Vite…) |
| `unity` | Unity projects: compiles the game, editor and test assemblies with `dotnet build`, without the editor |
| `generic` | Anything else: runs the commands listed at its top, passing the scoped files where a command takes them |

Copy the closest preset to `.claude/scripts/check.py`, adapt it to the project's real tools, and run it.
If the project already has a single command that honors the contract, use it instead and say so in the
config.

## .gitignore

Add `.claude/qa/` (QA's captures and throwaway scripts).
