"""Tests for the bin/ commands against a small fake project.

Run: python3 -m unittest discover -s tests
"""
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
BIN = PLUGIN / "bin"


def task(tid, cycle="C1", status="todo", deps="—", exclusive="no", files="", scope="Do it."):
    return textwrap.dedent("""\
        # {tid} — Example

        - **Status:** {status}
        - **Cycle:** {cycle}
        - **Type:** screen
        - **Roadmap item:** Item
        - **Depends on:** {deps}
        - **Exclusive:** {exclusive}
        - **Fix rounds:** 0

        ## Goal
        Goal.

        ## Scope
        {scope}

        ## Files
        {files}

        ## Result
        """).format(tid=tid, cycle=cycle, status=status, deps=deps, exclusive=exclusive, files=files,
                    scope=scope)


class FakeProject(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="overclock-test-"))
        (self.root / ".claude" / "tasks" / "done").mkdir(parents=True)
        (self.root / ".claude" / "tasks" / "logs").mkdir()
        (self.root / ".claude" / "docs").mkdir()
        (self.root / ".claude" / "overclock.md").write_text("---\noverclock: 0.1.0\n---\n# Config\n")
        (self.root / "src").mkdir()
        (self.root / "src" / "existing.ts").write_text("export {}\n")
        (self.root / ".claude" / "docs" / "roadmap.md").write_text(textwrap.dedent("""\
            # Roadmap

            ## C1 — Foundation

            - [x] Done item
            - [ ] Open item

            ## C2 — Next [paused]

            - [ ] Later
            """))
        (self.root / ".claude" / "tasks" / "BACKLOG.md").write_text(textwrap.dedent("""\
            # Backlog

            <!--
            | T999 | Example | screen | todo | — |
            -->

            # C1

            | Task | Title | Type | Status | Depends on |
            |---|---|---|---|---|
            | T001 | Contract | contract | todo | — |
            | T002 | Screen A | screen | todo | T001 |
            | T003 | Screen B | screen | todo | T001 |
            """))
        (self.root / ".claude" / "tasks" / "QUESTIONS.md").write_text(textwrap.dedent("""\
            # Questions

            ## Which payment provider?

            Options.

            ## Already answered

            **Answer (user):** yes

            ## Notice: C0 ready to see

            Nothing to answer.
            """))
        self.write_task("T001", files="- Create: `src/contract.ts` (developer)", exclusive="yes")
        self.write_task("T002", deps="T001", files="- Create: `src/a.ts` (developer)\n- Change: `src/contract.ts` (developer)")
        self.write_task("T003", deps="T001", files="- Create: `src/b.ts` (developer)\n- Change: `src/existing.ts` (developer)")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def write_task(self, tid, **kwargs):
        (self.root / ".claude" / "tasks" / f"{tid}-example.md").write_text(task(tid, **kwargs))

    def run_cmd(self, name, *args, cwd=None):
        proc = subprocess.run(["python3", str(BIN / name), *args], cwd=cwd or self.root,
                              capture_output=True, text=True)
        return proc.returncode, proc.stdout + proc.stderr


class PlanCheckTests(FakeProject):
    def test_valid_plan_prints_waves(self):
        code, out = self.run_cmd("overclock-plan-check", "C1")
        self.assertEqual(code, 0, out)
        self.assertIn("wave 1 (1): T001*", out)
        self.assertIn("wave 2 (2): T002 T003", out)

    def test_collision_without_dependency_is_an_error(self):
        self.write_task("T003", deps="T001", files="- Create: `src/b.ts` (developer)\n- Change: `src/contract.ts` (developer)")
        code, out = self.run_cmd("overclock-plan-check", "C1")
        self.assertEqual(code, 1)
        self.assertIn("T002 and T003 both touch `src/contract.ts`", out)

    def test_missing_file_owner_and_scope_are_errors(self):
        self.write_task("T004", files="- Change: `src/nowhere.ts`", scope="")
        code, out = self.run_cmd("overclock-plan-check", "C1")
        self.assertEqual(code, 1)
        self.assertIn("T004: `src/nowhere.ts` has no owner", out)
        self.assertIn("T004: Change `src/nowhere.ts` does not exist", out)
        self.assertIn("T004: empty ## Scope", out)

    def test_dependency_cycle_is_an_error(self):
        self.write_task("T001", deps="T003", files="- Create: `src/contract.ts` (developer)")
        code, out = self.run_cmd("overclock-plan-check", "C1")
        self.assertEqual(code, 1)
        self.assertIn("dependency cycle", out)

    def test_works_from_a_subfolder(self):
        code, out = self.run_cmd("overclock-plan-check", "C1", cwd=self.root / "src")
        self.assertEqual(code, 0, out)


class TaskTests(FakeProject):
    def test_read_and_set_status(self):
        self.assertEqual(self.run_cmd("overclock-task", "T002")[1].strip(), "todo")
        code, out = self.run_cmd("overclock-task", "T002", "dev")
        self.assertEqual(code, 0, out)
        self.assertIn("- **Status:** dev", (self.root / ".claude/tasks/T002-example.md").read_text())
        self.assertIn("| T002 | Screen A | screen | dev |", (self.root / ".claude/tasks/BACKLOG.md").read_text())

    def test_done_moves_the_file_and_back(self):
        self.run_cmd("overclock-task", "T002", "done")
        self.assertTrue((self.root / ".claude/tasks/done/T002-example.md").exists())
        self.run_cmd("overclock-task", "T002", "todo")
        self.assertTrue((self.root / ".claude/tasks/T002-example.md").exists())

    def test_comment_rows_are_ignored(self):
        backlog = (self.root / ".claude/tasks/BACKLOG.md").read_text()
        self.run_cmd("overclock-task", "T001", "dev")
        self.assertIn("| T999 | Example | screen | todo | — |", backlog)

    def test_invalid_status(self):
        code, out = self.run_cmd("overclock-task", "T002", "shipping")
        self.assertEqual(code, 1)
        self.assertIn("invalid status", out)

    def test_next_id(self):
        self.assertEqual(self.run_cmd("overclock-task", "--next-id")[1].strip(), "T004")


class StatusTests(FakeProject):
    def test_report(self):
        code, out = self.run_cmd("overclock-status")
        self.assertEqual(code, 0, out)
        self.assertIn("cycle C1 (Foundation)", out)
        self.assertIn("3 todo", out)
        self.assertIn("1 open question", out)
        self.assertIn("Which payment provider?", out)

    def test_qa_phase_when_all_items_done(self):
        roadmap = self.root / ".claude/docs/roadmap.md"
        roadmap.write_text(roadmap.read_text().replace("- [ ] Open item", "- [x] Open item"))
        self.assertIn("waiting for QA", self.run_cmd("overclock-status")[1])
        (self.root / ".claude/tasks/logs/2026-01-01-01-qa-c1.md").write_text("QA\n")
        self.assertIn("no open cycle", self.run_cmd("overclock-status")[1])

    def test_hook_is_silent_outside_a_project(self):
        outside = Path(tempfile.mkdtemp(prefix="overclock-outside-"))
        try:
            code, out = self.run_cmd("overclock-status", "--hook", cwd=outside)
            self.assertEqual((code, out), (0, ""))
        finally:
            shutil.rmtree(outside)

    def test_hook_line(self):
        code, out = self.run_cmd("overclock-status", "--hook")
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertIn("Overclock Runtime is set up", out)


class ShowTests(unittest.TestCase):
    def run_show(self, *args):
        proc = subprocess.run(["python3", str(BIN / "overclock-show"), *args], capture_output=True, text=True,
                              cwd=tempfile.gettempdir())
        return proc.returncode, proc.stdout + proc.stderr

    def test_prints_a_template(self):
        code, out = self.run_show("templates/tasks/task.md")
        self.assertEqual(code, 0)
        self.assertIn("- **Status:** todo", out)

    def test_refuses_paths_outside_the_plugin(self):
        self.assertEqual(self.run_show("../../etc/passwd")[0], 1)
        self.assertEqual(self.run_show("bin/overclock-show")[0], 1)

    def test_list_and_version(self):
        self.assertIn("skills/overclock/references/project-layer.md", self.run_show("--list")[1])
        self.assertRegex(self.run_show("--version")[1].strip(), r"^\d+\.\d+\.\d+$")


class DocSizesTests(FakeProject):
    def test_flags_big_docs(self):
        (self.root / ".claude/docs/architecture.md").write_text("x" * 50 * 1024)
        code, out = self.run_cmd("overclock-doc-sizes")
        self.assertEqual(code, 1)
        self.assertIn("OVER", out)
        self.assertEqual(self.run_cmd("overclock-doc-sizes", "--limit", "60")[0], 0)


if __name__ == "__main__":
    unittest.main()
