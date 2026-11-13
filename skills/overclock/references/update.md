# Update

The project is already set up. Running `/overclock` again brings its layer up to date with the installed
plugin without stepping on what the project changed.

1. Compare the `overclock:` version in `.claude/overclock.md`'s frontmatter with the plugin's
   (`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). Read the plugin's `CHANGELOG.md` for what changed
   in between, if it exists.
2. **CLAUDE.md block:** compare the text between the markers with `templates/CLAUDE-block.md` (in the
   project's language). Bring in new or changed rules; keep the project's own additions inside the block
   if they don't contradict the template; if they do, ask.
3. **Config:** add any section the template has and the config lacks, filled from the project. Never
   rewrite values the project set.
4. **Task files:** add what the templates gained (a new section in `BUGS.md`'s header, a new format line).
   Never touch existing entries.
5. **Permissions:** merge the current base and preset rules (see `project-layer.md`).
6. **Docs:** run `overclock-doc-sizes`; if a doc is over the limit, add a `[medium]` line to
   `IMPROVEMENTS.md` asking to split it.
7. Bump the frontmatter version, commit only these files ("Update Overclock Runtime to <version>"), and
   tell the user what changed.

If the user asked for something specific ("add a designer", "switch to the pnpm commands"), do that
instead, using the same files, and record it with `/overclock:feedback`'s rules (a decision of the user
becomes an `A#`).
