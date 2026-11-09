"""Granada: old Review events remain visible after later verified OK.

Only synthetic journals. No Instagram, Chrome, Supabase or relationship actions.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import ActionRobot, _atomic_json


class AutomationWarningHistoryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.robot = ActionRobot(None, self.root / "journals", self.root / "chrome")
        self.owner = "u_owner_42"
        self.account = "ig_first_1234567"

    def history(self, account=None, task="unfollow"):
        return self.robot.attempted_history({
            "owner": self.owner, "account": account or self.account, "task": task,
        })["history_rows"]

    def test_prior_review_and_error_survive_later_verified_action_without_secrets(self):
        old = "2026-11-08T23:45:00Z"
        latest = "2026-11-09T00:05:00Z"
        journal = self.robot._base_for(self.owner, self.account, "unfollow")
        _atomic_json(journal, {
            "example.user": {
                "status": "ok", "origin": "robot", "at": latest,
                "message": "Confirmed exact-target result",
                "attempt_history": [
                    {"status": "review", "origin": "robot", "at": old,
                     "message": "private token should never enter warning metrics",
                     "cookie": "private_session_cookie"},
                    {"status": "error", "at": "2026-11-08T23:50:00Z",
                     "password": "never-export-this"},
                    # Duplicate snapshot from an interrupted persisted retry;
                    # never count the same warning timestamp a second time.
                    {"status": "review", "origin": "robot", "at": old},
                    {"status": "ok", "origin": "robot", "at": "2026-11-08T23:55:00Z"},
                    {"status": "strange", "origin": "robot", "at": old},
                ],
            },
        })
        history = self.history()
        self.assertEqual(len(history), 1)
        row = history[0]
        self.assertEqual(row["username"], "example.user")
        self.assertEqual(row["status"], "ok")
        self.assertEqual(row["origin"], "robot")
        self.assertEqual(row["at"], latest)
        self.assertEqual(row["warning_events"], [
            {"status": "review", "origin": "robot", "at": old},
            {"status": "error", "origin": "unknown", "at": "2026-11-08T23:50:00Z"},
        ])
        for sensitive in ("private token", "cookie", "password", "never-export"):
            self.assertNotIn(sensitive, str(row["warning_events"]))

    def test_warning_events_are_scoped_by_owner_account_and_task(self):
        for account, task, user in (
            (self.account, "cancel", "cancel.user"),
            ("ig_second_123456", "unfollow", "other.user"),
        ):
            _atomic_json(self.robot._base_for(self.owner, account, task), {
                user: {"status": "review", "at": "2026-11-08T23:00:00Z",
                       "attempt_history": [{"status": "error",
                         "at": "2026-11-08T22:00:00Z"}]}
            })
        self.assertEqual(self.history(), [])
        self.assertEqual([x["username"] for x in self.history(task="cancel")],
                         ["cancel.user"])
        self.assertEqual([x["username"] for x in self.history(
            account="ig_second_123456")], ["other.user"])

    def test_malformed_history_never_breaks_panel_or_exposes_untrusted_fields(self):
        journal = self.robot._base_for(self.owner, self.account, "unfollow")
        _atomic_json(journal, {
            "bad.history": {"status": "review", "at": "2026-11-08T23:00:00Z",
                            "attempt_history": {"wrong": "shape"}},
            "mixed.history": {"status": "already_not_following", "at": "",
                              "attempt_history": [
                                  {}, None, "unexpected",
                                  {"status": "review", "at": 123},
                                  {"status": "review", "at": ""},
                                  {"status": "blocked",
                                   "at": "2026-11-08T20:00:00Z",
                                   "origin": "manual"},
                              ]},
        })
        by_name = {x["username"]: x for x in self.history()}
        self.assertEqual(by_name["bad.history"]["warning_events"], [])
        self.assertEqual(by_name["mixed.history"]["warning_events"], [
            {"status": "blocked", "origin": "unknown", "at": "2026-11-08T20:00:00Z"}
        ])


if __name__ == "__main__":
    unittest.main()
