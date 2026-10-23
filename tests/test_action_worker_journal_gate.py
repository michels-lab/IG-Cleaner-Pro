"""GRANADA #36: normal Windows robot never replays malformed saved actions.

Offline fake Chrome only. No real Instagram session, request or mutation.
"""
import inspect
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (
    ActionRobot, _atomic_json, _saved_journal_blocks_action)
from profile_counts_bridge import Collector


class FakeTab:
    def __init__(self):
        self.url = "https://www.instagram.com/"
        self.closed = False

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True


class FakeChrome:
    def __init__(self):
        self.pages = [FakeTab()]
        self.created_targets = 0

    def new_page(self):
        self.created_targets += 1
        item = FakeTab()
        self.pages.append(item)
        return item

    def close(self):
        for item in self.pages:
            item.close()


class WorkerJournalGateTests(unittest.TestCase):
    def make_robot(self, folder):
        root = Path(folder)
        counts = Collector(root / "counts", root / "chrome")
        robot = ActionRobot(counts, root / "canonical-journal", counts.session_dir)
        robot.owner, robot.account, robot.handle = "owner", "ig-account", "owner.name"
        robot.task, robot.targets = "unfollow", ["target.one"]
        robot.active_batch_id = "approved-exact-batch"
        return robot

    def test_prefetch_and_execution_both_share_strict_no_replay_gate(self):
        run = inspect.getsource(ActionRobot._run)
        self.assertGreaterEqual(
            run.count("_saved_journal_blocks_action(journal,"), 2)
        self.assertIn("invalid or changed", run)

    def test_absent_vs_saved_no_click_and_uncertain_journal(self):
        self.assertFalse(_saved_journal_blocks_action({}, "target.one"))
        self.assertFalse(_saved_journal_blocks_action({
            "target.one": {
                "status": "blocked",
                "message": "Instagram session verification failed before the first click. No action performed."
            }}, "target.one"))
        for row in (None, [], {}, {"status": "unknown"},
                    {"status": "review", "click_intent": None},
                    {"status": "ok", "click_intent": {
                        "phase": "relationship_control", "outcome_recorded": False}},
                    {"status": "ok", "message": "Confirmed"}):
            with self.subTest(row=row):
                self.assertTrue(_saved_journal_blocks_action(
                    {"target.one": row}, "target.one"))

    def test_journal_corruption_after_login_blocks_before_opening_target_tabs(self):
        # These are zero-network objects replacing the browser entirely.
        for invalid in (27, [], {}, {"status": "review", "click_intent": None},
                        {"status": "invalid"}, {"status": "ok", "click_intent": {
                            "phase": "unfollow_menu", "outcome_recorded": False}}):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as folder:
                robot = self.make_robot(folder)
                _atomic_json(robot._base(), {"target.one": invalid})
                original = robot._base().read_bytes()
                chrome = FakeChrome()
                fake_pw = types.SimpleNamespace(
                    chromium=types.SimpleNamespace(
                        launch_persistent_context=lambda **kwargs: chrome))
                cm = MagicMock()
                cm.__enter__.return_value = fake_pw
                with patch.dict(sys.modules, {
                    "playwright": types.ModuleType("playwright"),
                    "playwright.sync_api": types.SimpleNamespace(
                        sync_playwright=lambda: cm)
                }), patch("profile_actions.preserve_instagram_auth_page",
                         return_value=True), patch(
                         "profile_actions.challenge_detected", return_value=False
                ), patch("profile_actions._find_verified_owner_tab",
                         return_value=(chrome.pages[0], None)), patch(
                         "profile_actions.perform_visible_action",
                         side_effect=AssertionError("Unfollow MUST NOT execute")
                ):
                    robot._run()
                self.assertEqual(robot.status, "blocked")
                self.assertIn("No profile action was attempted", robot.message)
                self.assertEqual(chrome.created_targets, 0)
                self.assertEqual(original, robot._base().read_bytes())

    def test_last_chance_write_ahead_guard_refuses_malformed_record(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.make_robot(folder)
            for invalid in ([], {}, {"status": "unknown"},
                            {"status": "review", "click_intent": None}):
                journal = {"target.one": invalid}
                _atomic_json(robot._base(), journal)
                original = robot._base().read_bytes()
                with self.subTest(invalid=invalid), self.assertRaisesRegex(
                        ValueError, "Invalid saved action evidence"):
                    robot._persist_action_click_intent(
                        journal, robot._base(), "target.one", "relationship_control")
                self.assertEqual(original, robot._base().read_bytes())


if __name__ == "__main__":
    unittest.main()
