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
    def test_each_windows_unittest_checks_its_own_exit_status(self):
        lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        cases = [
            i for i, line in enumerate(lines)
            if line.strip().startswith(
                "python -m unittest discover -s tests -p '")
        ]
        self.assertGreaterEqual(
            len(cases), 20,
            "Check every actual Windows robot unittest, not just one fixture.")
        for index in cases:
            command = lines[index].strip()
            with self.subTest(command=command):
                following = next(
                    (line.strip() for line in lines[index + 1:]
                     if line.strip()), "")
                self.assertTrue(
                    following.startswith("if ($LASTEXITCODE -ne 0) { throw ")
                    and following.endswith("}"),
                    command + " must immediately fail the Windows job; "
                    "another succeeding command must not mask it.")

    def test_windows_dependency_installs_fail_immediately(self):
        lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
        for command in (
            "npm install --no-save playwright@1.57.0",
            "python -m pip install playwright==1.57.0 pyinstaller==6.16.0",
        ):
            indices = [i for i, line in enumerate(lines)
                       if line.strip() == command]
            with self.subTest(command=command):
                self.assertEqual(len(indices), 1)
                following = lines[indices[0] + 1].strip()
                self.assertTrue(following.startswith(
                    "if ($LASTEXITCODE -ne 0) { throw "))

    def test_workflow_trigger_includes_this_regression(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("tests/test_windows_ci_exitcode_gate.py", workflow)


if __name__ == "__main__":
    unittest.main()
