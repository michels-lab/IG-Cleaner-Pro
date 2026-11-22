"""GRANADA: ten target tabs are staged before sequential verified close.

These tests use offline fake Chrome pages; no Instagram contact or mutation.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import inspect
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (
    ActionRobot, ActionTabPool, MAX_ACTION_TABS,
    MISSING_RELATIONSHIP_CONTROL, _manual_close_review_record,
    _saved_journal_blocks_action, _invalid_saved_action_record,
    _atomic_json, _read_json,
)


class FakePage:
    def __init__(self, label):
        self.label = label
        self.closed = False
        self.focus_count = 0

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True

    def bring_to_front(self):
        self.focus_count += 1


class FakeChrome:
    def __init__(self):
        self.created = []

    def new_page(self):
        page = FakePage(len(self.created))
        self.created.append(page)
        return page


class TenTabWaveTests(unittest.TestCase):
    def test_exactly_ten_open_tabs_then_verified_sequential_closure(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        names = ["person_%02d" % i for i in range(40)]
        for user in names[:10]:
            self.assertIsNotNone(tabs.open(user))
        self.assertEqual(len(browser.created), 10)
        self.assertIsNone(tabs.open(names[10]))
        self.assertEqual(len(tabs.overview()), 10)

        for number, user in enumerate(names[:10]):
            page = tabs.prepared(user)
            self.assertIsNotNone(page)
            page.bring_to_front()
            tabs.record(user, "ok")
            self.assertTrue(page.is_closed(), user)
            self.assertEqual(page.focus_count, 1)
            self.assertEqual(len(tabs.overview()), 9-number)

        self.assertFalse(tabs.has_open_tabs())
        for user in names[10:20]:
            self.assertIsNotNone(tabs.open(user))
        self.assertEqual(len(browser.created), 20)

    def test_uncertain_click_keeps_its_tab_and_blocks_next_wave(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        for i in range(MAX_ACTION_TABS):
            tabs.open("person_%02d" % i)
        uncertain = tabs.prepared("person_03")
        tabs.record("person_03", "review", safe_no_click=False)
        for i in range(MAX_ACTION_TABS):
            if i != 3:
                tabs.record("person_%02d" % i, "ok")
        self.assertFalse(uncertain.is_closed())
        self.assertEqual(tabs.overview(),
                         [{"username": "person_03", "status": "review"}])
        self.assertTrue(tabs.has_open_tabs())
        # New complete wave may not start while an old uncertain tab exists.
        self.assertTrue(tabs.has_open_tabs(), "An unresolved tab prevents loading the next wave")
        uncertain.close()
        self.assertFalse(tabs.has_open_tabs())
        self.assertIsNotNone(tabs.open("person_10"))

    def test_no_request_outcome_closes_without_claiming_clicked(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        page = tabs.open("pending_profile")
        tabs.record("pending_profile", "already_not_requested")
        self.assertTrue(page.is_closed())
        self.assertFalse(tabs.has_open_tabs())

    def test_manually_closed_sequential_tab_never_reopens_automatically(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        first = tabs.open("profile_a")
        first.close()  # Human closes the target before an action is verified.
        self.assertIsNone(tabs.prepared("profile_a"))
        self.assertEqual(tabs.unresolved_manual_closures(),
                         {"profile_a": "checking"})
        self.assertFalse(tabs.has_open_tabs())
        self.assertIsNone(tabs.open("profile_a"))
        self.assertEqual(len(browser.created), 1)
        # A DIFFERENT approved target can still be allocated only after the
        # worker has durably acknowledged this closure.
        self.assertIsNotNone(tabs.open("profile_b"))
        self.assertEqual(len(browser.created), 2)

    def test_manually_closed_tab_in_ten_tab_wave_survives_slot_reclamation(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        for i in range(10):
            tabs.open("profile_%02d" % i)
        tabs.prepared("profile_03").close()
        self.assertEqual(tabs.unresolved_manual_closures(),
                         {"profile_03": "checking"})
        self.assertEqual(len(tabs.overview()), 9)
        self.assertIsNone(tabs.open("profile_03"))
        for i in range(10):
            if i != 3:
                tabs.record("profile_%02d" % i, "ok")
        self.assertFalse(tabs.has_open_tabs())
        self.assertEqual(tabs.unresolved_manual_closures(),
                         {"profile_03": "checking"})
        self.assertEqual(len(browser.created), 10)

    def test_final_prefetch_cleanup_preserves_external_closure(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        external = tabs.open("manually_closed")
        staged = tabs.open("internal_cleanup")
        tabs.tabs["manually_closed"]["status"] = "prefetched"
        tabs.tabs["internal_cleanup"]["status"] = "prefetched"
        external.close()
        tabs.close_unacted_prefetches()
        self.assertTrue(staged.is_closed())
        self.assertEqual(tabs.unresolved_manual_closures(),
                         {"manually_closed": "prefetched"})
        self.assertIsNone(tabs.open("manually_closed"))
        self.assertFalse(tabs.has_open_tabs())

    def test_verified_robot_close_does_not_create_false_manual_closure(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        tabs.open("confirmed")
        tabs.record("confirmed", "ok")
        self.assertEqual(tabs.unresolved_manual_closures(), {})
        self.assertFalse(tabs.has_open_tabs())

    def test_unconfirmed_manual_close_is_durable_review_not_fake_ok(self):
        record = _manual_close_review_record(None)
        self.assertEqual(record["status"], "review")
        self.assertEqual(record["issue"], "owner_closed_target_tab")
        self.assertNotIn("click_intent", record)
        self.assertTrue(_saved_journal_blocks_action(
            {"profile_a": record}, "profile_a"))
        self.assertFalse(_invalid_saved_action_record(record))

    def test_previous_proven_no_click_is_retained_as_attempt_history(self):
        prior = {
            "status": "review", "issue": "profile_load_timeout",
            "message": MISSING_RELATIONSHIP_CONTROL +
                       " Waiting timed out: No action clicked.",
            "at": "2026-11-19T00:00:00Z",
        }
        record = _manual_close_review_record(prior)
        self.assertIsNotNone(record)
        self.assertEqual(record["attempt_history"], [prior])
        self.assertTrue(_saved_journal_blocks_action({"p": record}, "p"))
        self.assertNotIn("click_intent", prior)

    def test_possible_click_or_corrupt_prior_evidence_is_not_overwritten(self):
        possible_click = {
            "status": "review", "issue": "unfollow_pending_verification",
            "click_intent": {"phase": "relationship_control",
                             "outcome_recorded": False},
        }
        for original in (possible_click, {"status": "ok"},
                         {"status": "mystery"}, {},
                         {"status": "review", "click_intent": None}):
            self.assertIsNone(_manual_close_review_record(original))
        self.assertEqual(possible_click["click_intent"]["phase"],
                         "relationship_control")

    def test_review_survives_disk_reload_without_cross_account_contamination(self):
        with TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "scope-a.json", Path(tmp) / "scope-b.json"
            prior_b = {"unrelated": {"status": "ok", "origin": "robot"}}
            _atomic_json(b, prior_b)
            _atomic_json(a, {"target": _manual_close_review_record(None)})
            self.assertTrue(_saved_journal_blocks_action(
                _read_json(a, {}), "target"))
            self.assertEqual(_read_json(b, {}), prior_b)

    def test_unknown_browser_transport_retains_slot_not_manual_tombstone(self):
        browser = FakeChrome()
        tabs = ActionTabPool(browser)
        page = tabs.open("transport")
        def unreliable():
            raise OSError("browser disconnected")
        page.is_closed = unreliable
        self.assertEqual(tabs.unresolved_manual_closures(), {})
        self.assertEqual(tabs.overview(),
                         [{"username": "transport", "status": "tab_state_unknown"}])
        self.assertIsNone(tabs.open("transport"))

    def test_worker_stops_on_closure_before_another_stage_or_action(self):
        source = inspect.getsource(ActionRobot._run)
        self.assertEqual(source.count("if stop_for_manual_target_close():"), 4)
        self.assertIn("_assert_unchanged_action_journal(path, journal)", source)
        self.assertIn("_atomic_json(path, revised)", source)
        self.assertIn("self.status = \"review\"", source)
        self.assertIn("stopped_for_review = True", source)

    def test_robot_is_wave_based_no_rolling_prefetch(self):
        source = inspect.getsource(ActionRobot._run)
        self.assertIn("def stage_next_wave(start_index):", source)
        self.assertIn("if action_tabs.has_open_tabs():", source)
        self.assertIn("work_page.bring_to_front()", source)
        self.assertIn('wait_until="domcontentloaded", timeout=30000', source)
        self.assertNotIn("paced_prefetch(phase)", source)
        self.assertNotIn('wait_until="commit", timeout=12000', source)


if __name__ == "__main__":
    unittest.main()
