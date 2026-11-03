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

    def run_offline(self, robot, action, *, challenge=None, owner=None, chrome=None):
        import profile_actions
        chrome = chrome if chrome is not None else FakeChrome()
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

    def test_real_worker_review_when_unused_chrome_tab_refuses_to_close(self):
        """An unclosed prefetch cannot vanish or produce a fake completed batch."""
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            robot.tab_flow = "ten_tabs"
            chrome = FakeChrome()
            observed = []
            visited_actions = []

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                visited_actions.append(username)
                # A global blocked state prevents action on later prepared
                # tabs. None of the three targets has a relationship click.
                self.assertEqual(username, "first.person")
                self.assertEqual(len(chrome.targets), 3)
                def cannot_close():
                    raise OSError("Chrome transport refused to close prefetched tab")
                chrome.targets[1].close = cannot_close
                return "blocked", "Owner session login check interrupted."

            def leave_review_loop(_seconds):
                observed.append({
                    "status": robot.status,
                    "message": robot.message,
                    "open_tabs": list(robot.open_review_tabs),
                })
                robot.stop_event.set()
                return True

            # The worker itself reaches its normal manual-review hold loop;
            # stop it on the first wait so offline CI never hangs.
            robot.stop_event.wait = leave_review_loop
            self.run_offline(robot, action, chrome=chrome)
            self.assertEqual(visited_actions, ["first.person"])
            self.assertTrue(observed, "Worker must stop and expose live Chrome tabs.")
            self.assertEqual(observed[0]["status"], "review")
            self.assertIn("could not confirm closure", observed[0]["message"])
            self.assertIn("NOT marked complete", observed[0]["message"])
            self.assertEqual(
                {row["username"]: row["status"]
                 for row in observed[0]["open_tabs"]},
                {"first.person": "blocked", "second.person": "prefetch_close_failed"})
            self.assertEqual(len(chrome.targets), 3,
                             "Chrome must not open or replay a fourth target.")
            saved = _read_json(robot._base(), {})
            self.assertEqual(saved["first.person"]["status"], "blocked")
            self.assertNotIn("click_intent", saved["first.person"])
            self.assertNotIn("second.person", saved)
            self.assertNotIn("third.person", saved)

    def test_confirmed_action_with_unclosed_chrome_tab_stops_next_targets(self):
        """A durable OK does not authorize another mutation while a tab remains open."""
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            robot.tab_flow = "ten_tabs"
            chrome = FakeChrome()
            observed, attempted = [], []

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                attempted.append(username)
                self.assertEqual(username, "first.person")
                self.assertEqual(len(chrome.targets), 3)
                on_pre_click("relationship_control")
                on_pre_click("cancel_request_confirmation")
                # Playwright close returns normally, but the first target tab
                # stays open. Saved OK must be retained; other targets stop.
                page.close = lambda: None
                return "ok", "Cancel Request verified after read-only refresh."

            def pause_at_review(_seconds):
                observed.append((robot.status, robot.message,
                                 list(robot.open_review_tabs)))
                robot.stop_event.set()
                return True

            robot.stop_event.wait = pause_at_review
            self.run_offline(robot, action, chrome=chrome)
            self.assertEqual(attempted, ["first.person"])
            self.assertTrue(observed)
            status, message, tabs = observed[0]
            self.assertEqual(status, "review")
            self.assertIn("recorded action", message)
            self.assertIn("NOT marked complete", message)
            self.assertEqual(tabs, [
                {"username": "first.person", "status": "tab_close_unconfirmed"}])
            saved = _read_json(robot._base(), {})
            self.assertEqual(saved["first.person"]["status"], "ok")
            self.assertTrue(saved["first.person"]["click_intent"]["outcome_recorded"])
            self.assertFalse(saved["first.person"]["click_intent"]["requires_manual_review"])
            self.assertNotIn("second.person", saved)
            self.assertNotIn("third.person", saved)
            self.assertTrue(_saved_journal_blocks_action(saved, "first.person"))
            self.assertEqual(len(chrome.targets), 3)

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



    def test_no_click_exception_stops_if_owner_cannot_be_reverified(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            tried = []

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                tried.append(username)
                raise RuntimeError("Read-only target error before WAL click barrier")

            def owner(page, handle):
                # The target exception cannot authorize the next mutation
                # when owner identity is missing or has switched.
                robot.stop_event.set()
                return False

            self.run_offline(robot, action, owner=owner)
            self.assertEqual(tried, ["first.person"])
            journal = _read_json(robot._base(), {})
            self.assertEqual(journal["first.person"]["status"], "error")
            self.assertNotIn("click_intent", journal["first.person"])
            self.assertNotIn("second.person", journal)
            self.assertNotIn("third.person", journal)
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"))

    def test_unfollow_no_click_exception_is_reviewable_and_next_target_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            robot.task = "unfollow"
            called = []
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                self.assertTrue(use_reference_transport)
                called.append(username)
                if username == "second.person":
                    raise RuntimeError("Read-only lookup failed before durable click")
                on_pre_click("relationship_control")
                return "ok", "Unfollow confirmed"
            self.run_offline(robot, action)
            self.assertEqual(called, robot.targets)
            saved = _read_json(robot._base(), {})
            self.assertEqual(saved["second.person"]["status"], "error")
            self.assertNotIn("click_intent", saved["second.person"])
            self.assertTrue(_saved_journal_blocks_action(saved, "second.person"))
            self.assertEqual(saved["third.person"]["status"], "ok")
            self.assertEqual(robot.status, "partial")


    def test_forty_profile_ten_tab_waves_continue_past_isolated_no_click_errors(self):
        """Errors at wave boundaries and the last profile never silently end a cohort."""
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            targets = [f"candidate.{number:03}" for number in range(1, 41)]
            robot.targets = targets
            robot.batch_size = 10
            robot.tab_flow = "ten_tabs"
            # Exercise failures inside waves, at wave boundaries, and as
            # the very last target, where Chrome previously closed early.
            failures = {targets[i] for i in (3, 14, 29, 39)}
            uncertain = targets[17]  # Durable first click, no verified outcome.
            observed = []

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                self.assertEqual(task, "cancel")
                observed.append(username)
                if username in failures:
                    # The durable on_pre_click callback was NEVER invoked.
                    # The original error must stay yellow, never turn green.
                    raise TimeoutError("Exact target menu failed before any click")
                on_pre_click("relationship_control")
                if username == uncertain:
                    # Playwright may time out after the actual relationship
                    # control click. Outcome is unknown and must never replay.
                    raise RuntimeError("Click outcome uncertain after first armed phase")
                on_pre_click("cancel_request_confirmation")
                return "ok", "Cancel Request verified after refresh"

            chrome = self.run_offline(robot, action)
            self.assertEqual(observed, targets)
            self.assertEqual(len(chrome.targets), 40)
            self.assertEqual(robot.status, "partial")
            saved = _read_json(robot._base(), {})
            self.assertEqual(set(saved), set(targets))
            for username in targets:
                if username in failures:
                    self.assertEqual(saved[username]["status"], "error")
                    self.assertNotIn("click_intent", saved[username])
                    self.assertTrue(_saved_journal_blocks_action(saved, username))
                elif username == uncertain:
                    self.assertEqual(saved[username]["status"], "error")
                    intent = saved[username]["click_intent"]
                    self.assertEqual(intent["phases"], ["relationship_control"])
                    self.assertTrue(intent["outcome_recorded"])
                    self.assertTrue(intent["requires_manual_review"])
                    self.assertTrue(_saved_journal_blocks_action(saved, username))
                else:
                    self.assertEqual(saved[username]["status"], "ok")
                    self.assertTrue(saved[username]["click_intent"]["outcome_recorded"])
            summary = robot.snapshot()
            self.assertEqual(summary["successful"], 35)
            self.assertEqual(summary["errors"], 5)
            self.assertEqual(summary["processed"], 40)
            self.assertEqual(summary["pending"], 0)

            # A later explicitly launched cohort with 40 old + five fresh
            # candidates must never reopen or reclick any earlier profile.
            next_robot = self.new_robot(folder)
            extra = [f"new.person.{i}" for i in range(1, 6)]
            next_robot.targets = targets + extra
            next_robot.batch_size = 10
            next_robot.tab_flow = "ten_tabs"
            later = []

            def second_action(page, username, task, expected, can_act=None,
                              on_wait=None, preloaded=False, on_pre_click=None,
                              use_reference_transport=False):
                later.append(username)
                on_pre_click("relationship_control")
                on_pre_click("cancel_request_confirmation")
                return "ok", "Verified fresh batch"

            next_chrome = self.run_offline(next_robot, second_action)
            self.assertEqual(later, extra,
                             "Saved 40 must not replay, including no-click and uncertain-click ERROR rows.")
            self.assertEqual(len(next_chrome.targets), 5)
            next_saved = _read_json(robot._base(), {})
            self.assertEqual(set(next_saved), set(targets + extra))
            blocked = failures | {uncertain}
            self.assertEqual({u for u in blocked
                              if next_saved[u]["status"] == "error"}, blocked)



    def test_legacy_unavailable_with_click_is_public_review_not_green(self):
        """Previously saved WAL never becomes harmless on a fresh launch."""
        from profile_actions import _atomic_json
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            legacy = {
                "status": "profile_unavailable",
                "message": "Profile later became unavailable.",
                "at": "2026-10-30T21:45:00Z",
                "click_intent": {
                    "batch_id": "older-batch",
                    "task": "cancel",
                    "phase": "relationship_control",
                    "phases": ["relationship_control"],
                    "outcome_recorded": True,
                    "requires_manual_review": True,
                },
            }
            _atomic_json(robot._base(), {"first.person": legacy})
            original_bytes = robot._base().read_bytes()
            snapshot = robot.snapshot()
            row = next(r for r in snapshot["rows"]
                       if r["username"] == "first.person")
            self.assertEqual(row["status"], "review")
            self.assertEqual(row["issue"], "unavailable_after_possible_click")
            self.assertIn("Outcome unknown", row["message"])
            self.assertEqual(row["click_phase"], "relationship_control")
            self.assertEqual(snapshot["errors"], 1)
            self.assertEqual(snapshot["profile_unavailable"], 0)
            self.assertEqual(snapshot["issue_count"], 1)
            history = robot.attempted_history({
                "owner": robot.owner, "account": robot.account,
                "task": robot.task})
            self.assertEqual(history["history_rows"][0]["status"], "review")
            self.assertIn("first.person", history["attempted_usernames"])
            self.assertTrue(_saved_journal_blocks_action(
                _read_json(robot._base(), {}), "first.person"))
            self.assertEqual(robot._base().read_bytes(), original_bytes,
                             "Public legacy recovery must NEVER rewrite the WAL.")

    def test_readonly_tab_cleanup_preserves_earlier_uncertain_wal(self):
        """Read-only tabs have no new click and can close safely on unavailable."""
        from profile_actions import ActionTabPool, _atomic_json
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            original = {"status": "review", "issue": "pending_cancel_unverified",
                        "message": "Earlier Cancel Request result unverified.",
                        "click_intent": {
                            "batch_id": "earlier-cohort", "task": "cancel",
                            "phase": "relationship_control",
                            "phases": ["relationship_control"],
                            "outcome_recorded": True,
                            "requires_manual_review": True}}
            _atomic_json(robot._base(), {"first.person": original})
            before = robot._base().read_bytes()
            chrome = FakeChrome()
            tabs = ActionTabPool(chrome)
            temporary = tabs.open("first.person")
            # The original action WAL describes a DIFFERENT older run. A
            # read-only recheck creates no click intent, and may therefore
            # discard its OWN temporary page without approving the old click.
            tabs.record("first.person", "profile_unavailable",
                        safe_no_click=True, possible_click=False)
            self.assertTrue(temporary.is_closed())
            self.assertFalse(tabs.has_open_tabs())
            self.assertEqual(robot._base().read_bytes(), before)
            self.assertTrue(_saved_journal_blocks_action(
                _read_json(robot._base(), {}), "first.person"))

    def test_unfollow_profile_unavailable_after_post_is_review_not_false_success(self):
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            robot.task = "unfollow"
            visited = []
            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                self.assertTrue(use_reference_transport)
                visited.append(username)
                on_pre_click("relationship_control")
                if username == "first.person":
                    return "profile_unavailable", "Read-only target now unavailable."
                return "ok", "Unfollow verified after refresh."

            self.run_offline(robot, action)
            self.assertEqual(visited, robot.targets)
            journal = _read_json(robot._base(), {})
            row = journal["first.person"]
            self.assertEqual(row["status"], "review")
            self.assertIn("Pending verification: ", row["message"])
            self.assertTrue(row["click_intent"]["requires_manual_review"])
            self.assertTrue(_saved_journal_blocks_action(journal, "first.person"))
            self.assertEqual(journal["second.person"]["status"], "ok")
            self.assertEqual(journal["third.person"]["status"], "ok")
            self.assertEqual(robot.status, "partial")

    def test_sixty_profiles_across_six_waves_with_disappearance_after_click(self):
        """Closed-after-click is Review, not green unavailable or dropped wave."""
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            targets = [f"candidate.{index:03}" for index in range(1, 61)]
            uncertain = {targets[index] for index in (4, 29, 59)}
            unavailable_before_click = {targets[index] for index in (14, 39)}
            robot.targets = targets
            robot.batch_size = 10
            robot.tab_flow = "ten_tabs"
            seen = []

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                seen.append(username)
                if username in unavailable_before_click:
                    return ("profile_unavailable",
                            "Exact profile unavailable before any relationship click.")
                on_pre_click("relationship_control")
                if username in uncertain:
                    # DOM or network says 'not available' AFTER an armed click:
                    # the original WAL must take precedence over appearance.
                    return ("profile_unavailable",
                            "Instagram now shows profile unavailable.")
                on_pre_click("cancel_request_confirmation")
                return ("ok", "Cancelled Request verified after refresh.")

            chrome = self.run_offline(robot, action)
            self.assertEqual(seen, targets,
                             "The last user and all 6 ten-profile waves must execute.")
            self.assertEqual(len(chrome.targets), 60)
            saved = _read_json(robot._base(), {})
            self.assertEqual(set(saved), set(targets))
            for username in targets:
                record = saved[username]
                if username in uncertain:
                    self.assertEqual(record["status"], "review")
                    self.assertIn("Target became unavailable", record["message"])
                    self.assertIn("Outcome unknown", record["message"])
                    self.assertEqual(record["click_intent"]["phases"],
                                     ["relationship_control"])
                    self.assertTrue(record["click_intent"]["outcome_recorded"])
                    self.assertTrue(record["click_intent"]["requires_manual_review"])
                    self.assertTrue(_saved_journal_blocks_action(saved, username))
                elif username in unavailable_before_click:
                    self.assertEqual(record["status"], "profile_unavailable")
                    self.assertNotIn("click_intent", record)
                    self.assertTrue(_saved_journal_blocks_action(saved, username))
                else:
                    self.assertEqual(record["status"], "ok")
            self.assertEqual(robot.status, "partial")
            snapshot = robot.snapshot()
            self.assertEqual(snapshot["total"], 60)
            self.assertEqual(snapshot["processed"], 60)
            self.assertEqual(snapshot["successful"], 55)
            self.assertEqual(snapshot["profile_unavailable"], 2)
            self.assertEqual(snapshot["errors"], 3)
            self.assertEqual(snapshot["pending"], 0)
            self.assertFalse(snapshot["open_review_tabs"])

            # New user-authorized cohort with 60 old + 5 genuinely fresh
            # targets must not re-visit any old username, INCLUDING the last
            # profile whose disappearance followed a possible click.
            additional = [f"brand.new.{index}" for index in range(1, 6)]
            next_robot = self.new_robot(folder)
            next_robot.targets = targets + additional
            next_robot.batch_size = 10
            next_robot.tab_flow = "ten_tabs"
            newly_visited = []
            def next_action(page, username, task, expected, can_act=None,
                            on_wait=None, preloaded=False, on_pre_click=None,
                            use_reference_transport=False):
                newly_visited.append(username)
                on_pre_click("relationship_control")
                on_pre_click("cancel_request_confirmation")
                return "ok", "New target verified."

            next_chrome = self.run_offline(next_robot, next_action)
            self.assertEqual(newly_visited, additional)
            self.assertEqual(len(next_chrome.targets), 5)
            final = _read_json(robot._base(), {})
            self.assertEqual(set(final), set(targets + additional))
            self.assertTrue(all(final[u]["status"] == "review" for u in uncertain))

    def test_disappearance_after_click_with_wrong_owner_stops_later_targets(self):
        """Never continue behind an uncertain click when owner proof fails."""
        with tempfile.TemporaryDirectory() as folder:
            robot = self.new_robot(folder)
            visited = []
            owner_changed = {"value": False}

            def action(page, username, task, expected, can_act=None,
                       on_wait=None, preloaded=False, on_pre_click=None,
                       use_reference_transport=False):
                visited.append(username)
                on_pre_click("relationship_control")
                owner_changed["value"] = True
                return "profile_unavailable", "Target disappeared after click intent."

            def owner(page, handle):
                if owner_changed["value"]:
                    robot.stop_event.set()
                    return False
                return True

            self.run_offline(robot, action, owner=owner)
            self.assertEqual(visited, ["first.person"])
            record = _read_json(robot._base(), {})
            self.assertEqual(record["first.person"]["status"], "review")
            self.assertTrue(record["first.person"]["click_intent"]["requires_manual_review"])
            self.assertNotIn("second.person", record)
            self.assertNotIn("third.person", record)



if __name__ == "__main__":
    unittest.main()
