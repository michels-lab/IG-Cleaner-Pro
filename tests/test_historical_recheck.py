"""Offline contracts for automatic historical read-only action re-audits."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_bridge import Collector
from profile_actions import ActionRobot, _atomic_json
from developer_audit import run_audit, ai_prompt


class HistoricalActionAuditTests(unittest.TestCase):
    def scoped(self, root):
        robot = ActionRobot(Collector(root / "counts", root / "chrome"),
                            root / "actions", root / "chrome")
        return robot

    def data(self, **changes):
        request = dict(owner="owner_test", account="account_1", task="unfollow",
                       expected_handle="owner.test", batch_size=5, gap_seconds=10,
                       rest_minutes=0, confirmation="history-read-only:unfollow")
        request.update(changes)
        return request

    def test_old_ambiguous_profiles_are_selected_without_replaying_actions(self):
        with TemporaryDirectory() as tmp:
            robot = self.scoped(Path(tmp))
            action_path = robot._base_for("owner_test", "account_1", "unfollow")
            _atomic_json(action_path, {
                "uncertain.one": {"status": "review", "message": "Possibly clicked."},
                "load.fail": {"status": "error", "message": "Site timed out."},
                "proven.done": {"status": "ok", "message": "Original action confirmed."},
                "already.gone": {"status": "already_not_following"},
            })
            before = action_path.read_bytes()
            with patch("profile_actions.threading.Thread") as mocked_thread:
                mocked_thread.return_value.is_alive.return_value = False
                result = robot.recheck_history(self.data())
                mocked_thread.return_value.start.assert_called_once()
            self.assertTrue(result["review_only"])
            self.assertTrue(result["history_recheck"])
            self.assertEqual(robot.targets, ["load.fail", "uncertain.one"])
            self.assertEqual(action_path.read_bytes(), before)
            robot._save_recheck_result("uncertain.one", "ok", "Read-only Follow observed.")
            robot._save_recheck_result("load.fail", "review", "Unverified, no clicks.")
            report = robot.historical_recheck_status(self.data())
            self.assertEqual(report["counts"]["total"], 2)
            self.assertEqual(report["counts"]["observed_not_following"], 1)
            self.assertEqual(report["counts"]["still_unresolved"], 1)
            self.assertEqual(action_path.read_bytes(), before,
                             "Observation must never overwrite original action results")
            self.assertEqual(robot.snapshot()["historical_checked"], 2)
            self.assertEqual(robot.snapshot()["historical_not_following"], 1)
            self.assertNotIn("uncertain.one", json.dumps(report),
                             "Aggregate status must never export target usernames")
            audit = run_audit(action_path.parent)
            self.assertEqual(audit["journals"], 1,
                             "Read-only ledger must not count as a relationship action journal")
            self.assertEqual(audit["historical_readonly_observations"], 2)
            self.assertNotIn("uncertain.one", ai_prompt(audit))
            self.assertTrue(any(f["code"] == "HISTORICAL_READONLY_UNRESOLVED"
                                for f in audit["findings"]))

    def test_historical_scan_rotates_unseen_profiles_after_first_page(self):
        with TemporaryDirectory() as tmp:
            robot = self.scoped(Path(tmp))
            _atomic_json(robot._base_for("owner_test", "account_1", "unfollow"), {
                "failed.01": {"status": "review"},
                "failed.02": {"status": "error"},
                "failed.03": {"status": "blocked"},
                "failed.04": {"status": "review"},
            })
            with patch("profile_actions.MAX_ACTIONS_PER_JOB", 2), \
                 patch("profile_actions.threading.Thread") as thread:
                thread.return_value.is_alive.return_value = False
                robot.recheck_history(self.data())
                self.assertEqual(robot.targets, ["failed.01", "failed.02"])
                robot._save_recheck_result("failed.01", "review", "Current state unresolved")
                robot._save_recheck_result("failed.02", "ok", "Now Follow state visible")
                robot.recheck_history(self.data())
                self.assertEqual(robot.targets, ["failed.03", "failed.04"],
                                 "A second pass must inspect previously unseen errors first")

    def test_preclick_historical_failure_can_be_observed_without_action(self):
        from unittest.mock import MagicMock
        from profile_actions import recheck_action_readonly
        page = MagicMock()
        page.url = "https://www.instagram.com/load.fail/"
        page.locator.return_value.count.return_value = 0
        previous = {"status": "review",
                    "message": "The active Instagram account cannot be verified. No action was performed."}
        with patch("profile_actions._wait_for_target_profile_shell", return_value=True), \
             patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions._verify_final_state",
                   return_value=("ok", "Action confirmed: Follow.")) as verified:
            ordinary = recheck_action_readonly(page, "load.fail", "unfollow",
                                               "owner.test", previous, preloaded=True)
            self.assertEqual(ordinary[0], "review")
            verified.assert_not_called()
            historical = recheck_action_readonly(
                page, "load.fail", "unfollow", "owner.test", previous,
                preloaded=True, allow_unacted_observation=True)
            self.assertEqual(historical[0], "ok")
            self.assertIn("Current visible state", historical[1])
            self.assertNotIn("Action confirmed", historical[1])
            verified.assert_called_once()
            page.get_by_role.assert_not_called()
            page.locator.return_value.click.assert_not_called()

    def test_confirmed_owner_task_required_and_protections_honored(self):
        with TemporaryDirectory() as tmp:
            robot = self.scoped(Path(tmp))
            _atomic_json(robot._base_for("owner_test", "account_1", "cancel"), {
                "do.not.touch": {"status": "blocked"},
                "inspect.me": {"status": "review"},
            })
            with self.assertRaisesRegex(ValueError, "Confirm"):
                robot.recheck_history(self.data(task="cancel"))
            protected = robot._protection_file()
            # Protected file is owner/account scoped, independent of task.
            robot.owner, robot.account = "owner_test", "account_1"
            protected = robot._protection_file()
            _atomic_json(protected, ["do.not.touch"])
            with patch("profile_actions.threading.Thread") as mocked_thread:
                mocked_thread.return_value.is_alive.return_value = False
                robot.recheck_history(self.data(task="cancel", confirmation="history-read-only:cancel"))
            self.assertEqual(robot.targets, ["inspect.me"])
            self.assertEqual(robot.historical_recheck_status(
                self.data(task="cancel"))["counts"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
