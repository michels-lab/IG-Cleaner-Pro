"""GRANADA regression: owner batch size must not impose a hidden hourly wait.

Offline-only, deterministic clocks; no Instagram account or browser mutation.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (
    ACTION_PROFILE_VISITS_PER_HOUR, ACTION_WINDOW_MINUTES,
    ActionRobot, action_wait_detail,
)


class ActionVisitPacingTests(unittest.TestCase):
    def test_twenty_visits_with_20_batch_no_longer_waits_2670_seconds(self):
        now = 1_700_000_000.0
        visits = [now - 500 + n * 20 for n in range(20)]
        delay, reason = action_wait_detail(
            visits, {"count": 0, "rest_until": 0}, batch_size=20,
            rest_minutes=1, gap_seconds=8, now=now)
        self.assertEqual(delay, 0)
        self.assertEqual(reason, "")
        self.assertEqual(ACTION_PROFILE_VISITS_PER_HOUR, 120)

    def test_one_minute_rest_after_20_targets_remains_one_minute(self):
        now = 1_700_000_000.0
        visits = [now - 500 + n * 20 for n in range(20)]
        state = {"count": 0, "rest_until": now + 60,
                 "every": 20, "minutes": 1}
        delay, reason = action_wait_detail(
            visits, state, batch_size=20, rest_minutes=1,
            gap_seconds=8, now=now)
        self.assertEqual(delay, 60)
        self.assertIn("Between-batch rest: 1 min after 20 profiles", reason)
        self.assertEqual(state["rest_until"], now + 60,
                         "The original persisted rest must not be mutated")

    def test_profile_gap_respects_exact_eight_seconds(self):
        now = 1_700_000_000.0
        delay, reason = action_wait_detail(
            [now - 3], {"rest_until": 0}, batch_size=20,
            rest_minutes=1, gap_seconds=8, now=now)
        self.assertEqual(delay, 5)
        self.assertIn("Between-profile spacing: 8 s", reason)

    def test_independent_hourly_protection_is_named_not_disguised_as_rest(self):
        now = 1_700_000_000.0
        visits = [now - 150 + n for n in range(ACTION_PROFILE_VISITS_PER_HOUR)]
        delay, reason = action_wait_detail(
            visits, {"rest_until": now + 60}, batch_size=20,
            rest_minutes=1, gap_seconds=8, now=now)
        self.assertGreater(delay, 3400)
        self.assertLess(delay, 3601)
        self.assertIn("Hourly visit safety limit: 120 visits per 60 minutes", reason)

    def test_no_reset_of_prior_visit_or_batch_rest_ledger(self):
        now = 1_700_000_000.0
        recent = [now - 100 + n for n in range(20)]
        original = list(recent)
        rest = {"rest_until": now + 80, "every": 20, "minutes": 1}
        delay, reason = action_wait_detail(
            recent, rest, batch_size=20, rest_minutes=1,
            gap_seconds=8, now=now)
        self.assertEqual(recent, original)
        self.assertEqual(rest["rest_until"], now + 80)
        self.assertEqual(delay, 80)
        self.assertIn("Between-batch rest", reason)

    def test_initial_robot_state_exposes_independent_hourly_limit(self):
        robot = ActionRobot(Mock(), Path("/tmp/igc-pacing-fixture"),
                            Path("/tmp/igc-pacing-session"))
        self.assertEqual(robot.batch_size, 30)
        self.assertEqual(robot.max_count, ACTION_PROFILE_VISITS_PER_HOUR)
        self.assertEqual(robot.window_minutes, ACTION_WINDOW_MINUTES)

    def test_pacing_messages_are_bound_to_both_wave_and_single_visit(self):
        source = (Path(__file__).resolve().parents[1] /
                  "tools/profile_actions.py").read_text(encoding="utf-8")
        self.assertEqual(source.count("delay, wait_reason = action_wait_detail("), 2)
        self.assertEqual(source.count(
            "self.batch_size if self.rest_minutes > 0 else 0,"), 2)
        self.assertIn('"hourly_visit_limit": self.max_count', source)
        self.assertIn('"batch_size": self.batch_size', source)
        self.assertNotIn(
            "self.max_count if self.rest_minutes > 0 else 0,", source)


if __name__ == "__main__":
    unittest.main()
