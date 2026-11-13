---
overclock: 0.1.0
---

# Overclock config

What the Overclock Runtime agents need to know about this project and can't find in the code. Every
agent reads this file after `CLAUDE.md`. Keep it short: rules that apply to everything stay in
`CLAUDE.md`, and the detail of each subject goes in its doc in `.claude/docs/`.

## Project

<one paragraph: what it is, for whom, current state (empty, prototype, in production)>

## Stack

<languages, frameworks, package manager, database, engine… and the versions that changed recently>

## Commands

- **Check a task:** `<command> --only <comma-separated files>` — types, lint and unit tests of those
  files, without starting the app. Exit 0 when nothing in scope fails; errors in other files are
  printed as `OTHER` and do not fail.
- **Check everything:** `<command>` — the same for the whole project. Runs at the end of each wave.
- **Full check:** `<command> --full` — the above plus the production build. Runs in QA.
- **Run the app (QA only):** `<commands to start it, ports, seed data>`
- **End-to-end tests (QA only):** `<command>`

## Exclusive resources

What only one agent may use at a time. A task that needs any of these is `Exclusive: yes` and runs
alone, between waves; QA also runs alone.
- Installing or removing dependencies (`<lockfile>`).
- <generating migrations, regenerating shared data, the editor, a device, a local server port…>

## Shared files

Files that many tasks would want to edit. Only an `integration` task (or the task named here) touches
them; the others deliver their pieces in their own files.
- `<path>` — <rule>

## Roles

- **Designer:** <ui | game | none>. Owns <docs, tokens, art folders>. <What "design" means here.>
- **Designer tools:** <image generation command and its budget per cycle | none>
- **QA matrix:** <what QA covers on every screen: locales, viewport widths, themes, scenes, devices>
- **Models:** planner `<model>`/`<effort>`, designer `<model>`/`<effort>`, developer `<model>`/`<effort>`,
  qa `<model>`/`<effort>`. Leave a role out to use the plugin default.

## Git and versions

- Branch: `<main>`. One commit per task, only with that task's files. Message: `T###: <summary> (C<N>)`.
- Never push, merge, rebase, reset or rewrite commits unless the user asks.
- Files that must never be committed: `<.env, build output, caches, .claude/qa/>`.
- Version: `<where it lives>` becomes `0.<N>.0` when cycle N ends (QA done). <or: no versioning>

## Limits

- **Secrets:** <files no agent reads or edits (e.g. .env); where the app reads its config>
- **Money:** <paid APIs or services and their caps; anything else needs the user>
- **Publishing:** <offline until the user says so | what is allowed>
- **Third-party assets and data:** <license rules; where credits are recorded>
