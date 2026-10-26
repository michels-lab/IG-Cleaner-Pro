"""GRANADA: catch the A -> B -> ... -> A target-tab bounce.

Offline-only source and pool tests; no Instagram page or relationship mutation.
The user must be able to select the legacy ten-tab behavior explicitly.
"""
import inspect
from pathlib import Path
from unittest.mock import Mock
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (
    ActionRobot, ActionTabPool, MAX_ACTION_TABS, action_tab_stage_limit,
)


class FakeTab:
    def __init__(self, user, events):
        self.user = user
        self.events = events
        self.closed = False

    def is_closed(self):
        return self.closed

    def bring_to_front(self):
        self.events.append(("focus", self.user))

    def close(self):
        self.closed = True
        self.events.append(("close", self.user))


class FakeChrome:
    def __init__(self):
        self.events = []
        self.pages = []

    def new_page(self):
        page = FakeTab(len(self.pages), self.events)
        self.pages.append(page)
        return page


class SequentialTargetNavigationTests(unittest.TestCase):
    def test_default_robot_uses_single_visible_target(self):
        robot = ActionRobot(Mock(), Path("/tmp/igc-tabs-fixture"),
                            Path("/tmp/igc-tabs-session"))
        self.assertEqual(robot.tab_flow, "sequential")
        self.assertEqual(action_tab_stage_limit(robot.tab_flow), 1)
        self.assertEqual(MAX_ACTION_TABS, 10)

    def test_legacy_10_tabs_preserved_but_opt_in(self):
        self.assertEqual(action_tab_stage_limit("ten_tabs"), 10)
        self.assertEqual(action_tab_stage_limit("sequential"), 1)

    def test_invalid_flow_never_silently_becomes_legacy(self):
        for mode in ("all", "twenty_tabs", "10", None, "", "SEQUENTIAL"):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                action_tab_stage_limit(mode)

    def test_sequential_pool_never_opens_next_before_current_is_processed(self):
        chrome = FakeChrome()
        pool = ActionTabPool(chrome)
        users = ["person_a", "person_b", "person_c"]
        order = []
        for user in users:
            for name in users:
                if name == user:
                    break
            # Source's actual staging bound; no speculative ten-tab opening.
            for staged in [user][:action_tab_stage_limit("sequential")]:
                page = pool.open(staged)
                self.assertIsNotNone(page)
                chrome.events.append(("navigate", staged))
                self.assertIs(pool.prepared(staged), page)
            page.bring_to_front()
            order.append(("process", user))
            chrome.events.append(("process", user))
            pool.record(user, "ok")
            self.assertFalse(pool.has_open_tabs())
        self.assertEqual(
            [event for event in chrome.events if event[0] in ("navigate", "process")],
            [("navigate", "person_a"), ("process", "person_a"),
             ("navigate", "person_b"), ("process", "person_b"),
             ("navigate", "person_c"), ("process", "person_c")])
        self.assertEqual(len(chrome.pages), len(users))
        self.assertEqual(len({id(page) for page in chrome.pages}), len(users))

    def test_unverified_target_blocks_new_tab_instead_of_reopening_previous(self):
        chrome = FakeChrome()
        pool = ActionTabPool(chrome)
        first = pool.open("person_a")
        pool.record("person_a", "review", safe_no_click=False)
        self.assertIs(pool.prepared("person_a"), first)
        self.assertTrue(pool.has_open_tabs())
        # Worker's stage_next_wave guard stops here. No new Chrome target tab.
        should_stage = not pool.has_open_tabs()
        self.assertFalse(should_stage)
        self.assertEqual(len(chrome.pages), 1)

    def test_actual_worker_source_limits_staging_before_processing(self):
        source = inspect.getsource(ActionRobot._run)
        # Old implementation used a hard-coded 10 and always did all ten
        # page.goto calls before the first perform_visible_action.
        self.assertIn("stage_limit = action_tab_stage_limit(self.tab_flow)", source)
        self.assertIn("if len(stage_names) >= stage_limit:", source)
        self.assertNotIn("if len(stage_names) >= MAX_ACTION_TABS:", source)
        self.assertIn("if action_tabs.has_open_tabs():", source)
        self.assertIn("work_page.bring_to_front()", source)
        self.assertIn("preloaded=bool(prepared_item and", source)

    def test_ui_exposes_and_persists_owner_choice(self):
        html = (Path(__file__).resolve().parents[1] /
                "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
        self.assertEqual(html.count('id="igcAutoTabFlow"'), 1)
        self.assertIn('<option value="sequential" selected>', html)
        self.assertIn('<option value="ten_tabs">', html)
        self.assertIn('JSON.stringify({count,rest,gap,tab_flow})', html)
        self.assertIn('batch_size,rest_minutes,gap_seconds,tab_flow,', html)
        self.assertIn('t.tab_flow==="ten_tabs"?"ten_tabs":"sequential"', html)


if __name__ == "__main__":
    unittest.main()
