"""Regression: one target's unexpected Unfollow dialog never freezes a Cancel wave.

The actual ActionRobot._run() loop and its canonical journal/visit files are
executed. Only Playwright pages and Instagram UI mutations are faked; no live
website or account is contacted.
"""
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import ActionRobot, _saved_journal_blocks_action, _read_json
from profile_counts_bridge import Collector


class FakeLocator:
    def count(self):
        return 0


class FakeTab:
    def __init__(self, url="https://www.instagram.com/"):
        self.url = url
        self.closed = False
        self.visits = []

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True

    def goto(self, url, **kwargs):
        self.url = url
        self.visits.append(url)

    def bring_to_front(self):
        pass

    def locator(self, selector):
        return FakeLocator()


class FakeChrome:
    def __init__(self):
        self.pages = [FakeTab()]
        self.targets = []

    def new_page(self):
        tab = FakeTab()
        self.pages.append(tab)
        self.targets.append(tab)
        return tab

    def close(self):
        for tab in self.pages:
            tab.close()


class CancelWarningContinuesBatch(unittest.TestCase):
    def new_robot(self, directory):
        root = Path(directory)
        collector = Collector(root / "counts", root / "chrome")
        robot = ActionRobot(collector, root / "canonical-wal", collector.session_dir)
        robot.owner = "owner_12345"
        robot.account = "ig_account_12345"
        robot.handle = "my.profile"
        robot.task = "cancel"
        robot.targets = ["first.person", "second.person", "third.person"]
        robot.active_batch_id = "exact-approved-cohort"
        robot.batch_size = 3
        robot.tab_flow = "sequential"
        robot.rest_minutes = 0
        robot.min_delay_seconds = 1
        return robot

    def run_offline(self, robot, action, *, challenge=None, owner=None):
        import profile_actions
        chrome = FakeChrome()
        fake_playwright = types.SimpleNamespace(
            chromium=types.SimpleNamespace(
                launch_persistent_context=lambda **_kw: chrome))
        scope = MagicMock()
        scope.__enter__.return_value = fake_playwright
        with patch.dict(sys.modules, {
            "playwright": types.ModuleType("playwright"),
            "playwright.sync_api": types.SimpleNamespace(
                sync_playwright=lambda: scope)
        }), patch("profile_actions.preserve_instagram_auth_page",
                  return_value=True), patch(
                  "profile_actions.challenge_detected",
                  side_effect=(challenge or (lambda _tab: False))
        ), patch("profile_actions._verified_action_owner",
                 side_effect=(owner or (lambda *_: True))), patch(
                  "profile_actions._find_verified_owner_tab",
                  side_effect=lambda pages, _handle: (pages[0], None)), patch(
                  "profile_actions.perform_visible_action", side_effect=action
        ), patch("profile_actions.action_wait_detail",
                 return_value=(0, "offline")):
            robot._run()
        return chrome

    def test_one_cancel_warning_is_saved_and_next_two_profiles_continue(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            clicked = []
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                self.assertEqual(task, "cancel")
                self.assertEqual(expected, "my.profile")
                clicked.append(username)
                on_pre_click("relationship_control")
                if username == "first.person":
                    return ("review",
                        "Cancel pending safety stop: Instagram displayed a normal "
                        "Unfollow confirmation. No final Unfollow clicked.")
                on_pre_click("cancel_request_confirmation")
                return ("ok", "Verified Cancel Request after read-only reload.")
            chrome = self.run_offline(robot, action)
            self.assertEqual(clicked, robot.targets,
                             "The other 2 profiles must not be held by the first Warning.")
            journal = _read_json(robot._base(), {})
            self.assertEqual(journal["first.person"]["status"], "review")
            self.assertEqual(journal["first.person"]["issue"],
                             "pending_wrong_relationship_dialog")
            self.assertEqual(journal["first.person"]["click_intent"]["phases"],
                             ["relationship_control"])
            self.assertTrue(journal["first.person"]["click_intent"]["requires_manual_review"])
            self.assertEqual(journal["second.person"]["status"], "ok")
            self.assertEqual(journal["third.person"]["status"], "ok")
            self.assertEqual(robot.status, "partial")
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"),
                            "Never retry the uncertain first profile after restart.")
            self.assertEqual(len(chrome.targets), 3)
            self.assertEqual(robot.open_review_tabs, [])
            snapshot = robot.snapshot()
            self.assertEqual(snapshot["issue_count"], 1)
            self.assertEqual(snapshot["successful"], 2)
            self.assertEqual(snapshot["errors"], 1)

    def test_missing_one_target_profile_is_warning_not_session_block(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            checked = []
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                checked.append(username)
                if username == "first.person":
                    return ("blocked",
                        "The target profile heading or exact username could not be verified. "
                        "No action was performed.")
                on_pre_click("relationship_control")
                on_pre_click("cancel_request_confirmation")
                return ("ok", "Verified Cancel Request")
            self.run_offline(robot, action)
            self.assertEqual(checked, robot.targets)
            journal = _read_json(robot._base(), {})
            first = journal["first.person"]
            self.assertEqual(first["status"], "review")
            self.assertIn("Cancel Pending warning:", first["message"])
            self.assertNotIn("click_intent", first)
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"))
            self.assertEqual(journal["second.person"]["status"], "ok")
            self.assertEqual(journal["third.person"]["status"], "ok")

    def test_no_healthy_owner_session_cannot_continue_behind_warning(self):
        import threading
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            started = []
            bad_identity = threading.Event()
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                started.append(username)
                on_pre_click("relationship_control")
                bad_identity.set()
                # The first result remains journaled as REVIEW; owner check
                # prevents running any later mutation under a wrong login.
                return ("review", "Cancel pending safety stop: unexpected Unfollow.")
            def owner(page, handle):
                if bad_identity.is_set():
                    # Stop the deliberately open Review tab shortly afterward,
                    # as if the user selected Pause in the UI.
                    robot.stop_event.set()
                    return False
                return True
            self.run_offline(robot, action, owner=owner)
            self.assertEqual(started, ["first.person"])
            journal = _read_json(robot._base(), {})
            self.assertEqual(journal["first.person"]["status"], "review")
            self.assertNotIn("second.person", journal)
            self.assertNotIn("third.person", journal)
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"))

    def test_security_challenge_after_warning_blocks_rest_of_batch(self):
        import threading
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            issue_seen = threading.Event()
            called = []
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                called.append(username)
                on_pre_click("relationship_control")
                issue_seen.set()
                return ("review", "Cancel pending safety stop: normal Unfollow popup.")
            def challenge(_page):
                if issue_seen.is_set():
                    # Emulate the operator pausing after the system-wide
                    # security challenge is identified; no more action clicks.
                    robot.stop_event.set()
                    return True
                return False
            self.run_offline(robot, action, challenge=challenge)
            self.assertEqual(called, ["first.person"])
            journal = _read_json(robot._base(), {})
            self.assertEqual(journal["first.person"]["status"], "review")
            self.assertNotIn("second.person", journal)
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"))

    def test_cancel_warning_does_not_turn_into_success_or_auto_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                on_pre_click("relationship_control")
                if username == "first.person":
                    return ("review",
                        "Cancel pending safety stop: unexpected normal Unfollow.")
                on_pre_click("cancel_request_confirmation")
                return ("ok", "Verified")
            self.run_offline(robot, action)
            before = robot._base().read_bytes()
            robot_again = self.new_robot(folder)
            called = []
            def bad_replay(*args, **kwargs):
                called.append(args[1])
                return ("ok", "Do not run")
            self.run_offline(robot_again, bad_replay)
            self.assertEqual(called, [],
                             "Restart cannot replay original or already completed clicks.")
            self.assertEqual(robot._base().read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
