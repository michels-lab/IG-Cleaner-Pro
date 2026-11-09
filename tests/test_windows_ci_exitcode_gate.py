"""Prevent Windows CI from hiding a failing robot regression.

Regression for the 2026-11-09 false-green integrated Windows workflow:
PowerShell continued from a failing two-account unittest to a succeeding
coordinator unittest, so the following $LASTEXITCODE checked the WRONG test.
No browser, network or Instagram account is needed to check this invariant.
"""
from pathlib import Path
import unittest


WORKFLOW = (Path(__file__).resolve().parents[1] / ".github" /
            "workflows" / "profile-counts-windows-preview.yml")


class WindowsExitCodeGuardTests(unittest.TestCase):
    def test_each_action_isolation_unittest_is_immediately_fatal_on_failure(self):
        lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        for filename in ("test_robot_interlock.py",
                         "test_action_scoped_admission.py",
                         "test_dual_action_workspaces.py"):
            command = ("python -m unittest discover -s tests -p '" +
                       filename + "' -v")
            occurrences = [i for i, line in enumerate(lines)
                           if line.strip() == command]
            with self.subTest(filename=filename):
                self.assertEqual(len(occurrences), 1)
                next_line = next(
                    (line.strip() for line in lines[occurrences[0]+1:]
                     if line.strip()), "")
                self.assertTrue(
                    next_line.startswith("if ($LASTEXITCODE -ne 0) { throw ")
                    and next_line.endswith("}"),
                    "PowerShell must stop immediately after " + filename +
                    "; a succeeding later command can otherwise hide failure.")

    def test_workflow_trigger_includes_this_regression(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("tests/test_windows_ci_exitcode_gate.py", workflow)


if __name__ == "__main__":
    unittest.main()
