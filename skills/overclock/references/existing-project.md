# Existing project

The code answers most questions. Read before asking anything, and ask only what the code can't tell.

## 1. Map the project

Use subagents (Explore) in parallel if the project is large; otherwise read it yourself.

- **Stack and commands:** the manifests (`package.json` and its scripts, lockfiles, `pyproject.toml`,
  `Cargo.toml`, `go.mod`, `*.csproj`, Unity's `ProjectSettings/ProjectVersion.txt`, `Gemfile`,
  `composer.json`, Dockerfiles, `docker-compose.yml`, CI workflows). Find how to type-check, lint, run unit
  tests, build, start the app and run end-to-end tests.
- **Shape:** the folder tree, where pure logic lives, how tests sit next to code, the naming conventions,
  the component library, the text/i18n setup.
- **Shared files:** the ones every feature would touch (route or navigation registries, schema indexes,
  dependency manifests, generated code, design tokens, translation files). They go in "Shared files".
- **Exclusive resources:** what one agent at a time may use (dependency installs, migrations, code
  generators, a game editor, a device, a fixed port).
- **What exists already:** `README`, an existing `CLAUDE.md` or `AGENTS.md`, docs, open TODOs, failing
  tests. Keep what is good; the CLAUDE.md block is added, never replacing the user's text.
- **State:** is it in production? Is there a deploy? Secrets files (`.env*`)? Those shape "Limits".

## 2. Ask what is left

One `AskUserQuestion` round, at most 4 questions, each with a recommendation. Typically:

1. **What's next:** what the first cycles should deliver (offer what you read as the natural next steps).
2. **Limits:** money, publishing, accounts (default: none until the user says so). In a project already in
   production, ask explicitly whether the process may touch anything that reaches production.
3. **Branch:** the process commits one commit per task on one branch. Offer the current branch or a new
   one (e.g. `overclock`) if the main branch is shared with other people.

## 3. Write the docs from the code

- `architecture.md`: what the code **is**, not what it should be. Real paths and names.
- `product.md`: what the product does today and what it should do next.
- `roadmap.md`: start at the next real step. If the project has known problems (failing tests, the
  check failing), the first cycle starts with an item to fix them.
- The designer's docs: if the project has a UI or art direction, describe the one that exists (tokens,
  components, patterns) so the designer extends it instead of reinventing it.

## 4. The check

Adapt a preset (see `project-layer.md`) to the real commands. Run it on the whole project once and note
the result. Run it with `--only` on one or two files to see the scoping works (errors in other files show
as `OTHER`).
