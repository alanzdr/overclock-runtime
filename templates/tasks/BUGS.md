# Bugs

Real defects: what does not work, works wrong, or came out different from the design. Each cycle starts
with the planner turning what is here and in `IMPROVEMENTS.md` into tasks.

Who writes here: designers and developers during the cycle (what they find outside their task), QA at
the end of it, and the user through `/overclock:feedback`. Who turns it into tasks: only the planner, at
the start of the next cycle; it marks the line with `→ T###`. **When fixed, the line is deleted** and
the fix is recorded in the log of the step that fixed it: this file only keeps open bugs.

Severity: `critical` (the screen or main function does not work, wrong data, an error that breaks
use), `normal` (works, with a visible defect), `minor` (detail).

Format: `- [ ] [severity] <route or file:line> — <the defect>; reproduce: <steps or test>; suggested fix: <what> (found in T### | QA C<N> | user)`

<!-- One `## C<N>` section per cycle in which bugs were found. -->
