import json
import tempfile
from pathlib import Path
import unittest

from tools.profile_counts_pacing import (
    check_pacing, history_path, load_history, register_visit,
    wait_required, save_history, finish_visit,
    check_batch_rest, batch_path, load_batch_state, finish_batch_visit, batch_wait,
)


class ProfileCountsPacingTests(unittest.TestCase):
    def test_user_example_independent_window_and_delay(self):
        count, minutes, delay = check_pacing(200, 5, 5)
        self.assertEqual((count, minutes, delay), (200, 5, 5))
        clock=1_700_000_000.0
        events=[clock + i*5 for i in range(60)]
        # With visits at 0s,5s,...295s, next at 300s is allowed:
        # the first visit falls out of the rolling five-minute window.
        self.assertGreater(wait_required(events,count,minutes,delay,clock+298),1.9)
        self.assertEqual(wait_required(events,count,minutes,delay,clock+300),0.0)

    def test_window_limit_applies_even_with_zero_gap(self):
        now=1_700_000_000.0
        events=[now-40,now-30,now-20]
        self.assertAlmostEqual(wait_required(events,3,5,0,now),260.05,places=2)
        self.assertEqual(wait_required(events,3,5,0,now+261),0)

    def test_gap_applies_even_below_window_limit(self):
        now=1_700_000_000.0
        self.assertAlmostEqual(wait_required([now-2],200,5,5,now),3)
        self.assertEqual(wait_required([now-5],200,5,5,now),0)

    def test_rate_window_uses_most_recent_n_visits(self):
        now=1_700_000_000.0
        events=[now-290, now-200,now-100,now-10]
        # Four visits in the last 5 minutes; with count=3,
        # next is allowed only after the second oldest expires.
        self.assertAlmostEqual(wait_required(events,3,5,0,now),100.05,places=2)

    def test_resume_from_persistent_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            results=Path(folder)/"profile.csv"
            visits_file=history_path(results)
            clock=1_700_000_000.0
            visits=register_visit(visits_file, [], at=clock-20)
            visits=register_visit(visits_file, visits, at=clock-5)
            self.assertEqual(load_history(visits_file,now=clock),[clock-20,clock-5])
            self.assertAlmostEqual(wait_required(load_history(visits_file,now=clock),2,5,5,clock),280.05,places=2)
            self.assertFalse(visits_file.with_suffix(visits_file.suffix+".tmp").exists())

    def test_legacy_result_seeds_cooldown(self):
        clock=1_700_000_000.0
        with tempfile.TemporaryDirectory() as folder:
            stamp="2023-11-14T22:13:15+00:00"  # clock -5 seconds
            seeded=load_history(Path(folder)/"missing.json",{
                "sample":{"checked_at":stamp}
            },now=clock)
            self.assertEqual(seeded,[clock-5])
            self.assertAlmostEqual(wait_required(seeded,50,60,72,clock),67)

    def test_corrupt_log_cannot_reset_rate_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            filename=Path(folder)/"visits.json"
            filename.write_text("invalid-json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_history(filename, now=1_700_000_000.0)

    def test_wait_is_after_profile_finishes_and_survives_restart(self):
        clock=1_700_000_000.0
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"visits.json"
            events=register_visit(path, [], at=clock-9)
            # The page required seven seconds; pause still needs five more
            # seconds after the browser finishes this profile.
            events=finish_visit(path, events, at=clock-2)
            self.assertEqual(load_history(path, now=clock), [clock-2])
            self.assertEqual(wait_required(events,200,5,5,now=clock), 3)
            self.assertEqual(wait_required(events,200,5,5,now=clock+3), 0)

    def test_additional_rest_after_each_n_profiles_survives_restart(self):
        clock=1_700_000_000.0
        self.assertEqual(check_batch_rest(200,5),(200,5.0))
        with tempfile.TemporaryDirectory() as folder:
            file=batch_path(Path(folder)/"results.csv")
            state=load_batch_state(file)
            state=finish_batch_visit(file,state,3,5,now=clock)
            state=finish_batch_visit(file,state,3,5,now=clock+10)
            self.assertEqual(state["count"],2)
            self.assertEqual(batch_wait(state,3,5,now=clock+20),0)
            state=finish_batch_visit(file,state,3,5,now=clock+20)
            self.assertEqual(state["count"],0)
            self.assertEqual(batch_wait(load_batch_state(file),3,5,now=clock+25),295)
            self.assertEqual(batch_wait(load_batch_state(file),3,5,now=clock+320),0)

    def test_optional_rest_can_be_disabled_and_rejects_half_configuration(self):
        self.assertEqual(check_batch_rest(0,0),(0,0.0))
        self.assertEqual(batch_wait({"rest_until":99999},0,0,now=0),0)
        for count, minutes in [(200,0),(0,5),(-1,5),(200,-1),(200,float("inf")),(10001,1)]:
            with self.assertRaises(ValueError):
                check_batch_rest(count,minutes)

    def test_boundaries(self):
        for kwargs in [(0,5,5),(10001,5,5),(50,0,5),(50,1441,5),
                       (50,5,-1),(50,5,float("nan")),(50,5,float("inf"))]:
            with self.assertRaises(ValueError):
                check_pacing(*kwargs)
        self.assertEqual(check_pacing(10000,1440,0),(10000,1440,0.0))

if __name__ == "__main__":
    unittest.main()
