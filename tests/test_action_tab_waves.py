"""GRANADA: ten target tabs are staged before sequential verified close.

These tests use offline fake Chrome pages; no Instagram contact or mutation.
"""
from pathlib import Path
import inspect
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import ActionRobot, ActionTabPool, MAX_ACTION_TABS


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
