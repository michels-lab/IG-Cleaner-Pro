"""GRANADA: corrupt but parseable pacing journals must never silently reset limits."""
import json
import tempfile
import unittest
from pathlib import Path

from tools.profile_counts_pacing import (
    load_history, load_batch_state, wait_required,
    register_visit, finish_batch_visit, save_batch_state,
)

NOW = 1_700_000_000.0


class GranadaPacingIntegrityTests(unittest.TestCase):
    def test_persisted_array_with_invalid_types_is_rejected_without_file_changes(self):
        for items in ([NOW - 15, "bad"], [NOW - 15, None],
                      [NOW - 15, True], [NOW - 15, False],
                      [NOW - 15, {}], [NOW - 15, 0],
                      [NOW - 15, -10], [NOW - 15, NOW + 61]):
            with self.subTest(items=items), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "visits.json"
                original = json.dumps(items).encode()
                path.write_bytes(original)
                with self.assertRaisesRegex(ValueError, "invalid or future timestamps"):
                    load_history(path, now=NOW)
                self.assertEqual(path.read_bytes(), original)
                self.assertFalse(list(Path(folder).glob("*.tmp")))

    def test_nonfinite_json_timestamp_does_not_remove_prior_pacing_budget(self):
        for raw in ('[1699999980,NaN]', '[1699999980,Infinity]',
                    '[1699999980,-Infinity]'):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "visits.json"
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    load_history(path, now=NOW)
                self.assertEqual(path.read_text(), raw)

    def test_older_valid_visits_expire_without_rejecting_recent_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "visits.json"
            events = [NOW - 86401, NOW - 180, NOW - 35, NOW + 30]
            path.write_text(json.dumps(events))
            result = load_history(path, now=NOW)
            self.assertEqual(result, sorted(events[1:]))
            self.assertGreater(wait_required(result, 3, 60, 5, now=NOW), 0)
            self.assertEqual(json.loads(path.read_text()), events,
                             "Loading must never rewrite the historical journal")

    def test_normal_prefetched_visit_close_remains_loadable(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "visits.json"
            items = register_visit(path, [], at=NOW - 30)
            items = register_visit(path, items, at=NOW - 10)
            self.assertEqual(load_history(path, now=NOW), [NOW - 30, NOW - 10])

    def test_corrupt_batch_counter_and_rest_settings_do_not_reset_break(self):
        original = {"count": 2, "rest_until": NOW + 220, "every": 3, "minutes": 5.0}
        bad = [
            {**original, "count": True},
            {**original, "count": 3},
            {**original, "every": 0},
            {**original, "every": True},
            {**original, "every": "3"},
            {**original, "minutes": None},
            {**original, "minutes": False},
            {**original, "minutes": -1},
            {**original, "rest_until": True},
            {**original, "rest_until": -1},
            {"count": 2, "rest_until": NOW + 220},
        ]
        for state in bad:
            with self.subTest(state=state), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "profile.csv.batch.json"
                encoded = json.dumps(state).encode()
                path.write_bytes(encoded)
                with self.assertRaises(ValueError):
                    load_batch_state(path)
                self.assertEqual(path.read_bytes(), encoded)

    def test_valid_batch_rest_persists_and_disabled_mode_is_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profile.csv.batch.json"
            rest = {"count": 0, "rest_until": NOW + 210, "every": 4, "minutes": 5.0}
            save_batch_state(path, rest)
            self.assertEqual(load_batch_state(path), rest)
            self.assertEqual(finish_batch_visit(path, rest, 4, 5.0, now=NOW)["count"], 1)
            disabled = {"count": 0, "rest_until": 0.0, "every": 0, "minutes": 0.0}
            save_batch_state(path, disabled)
            self.assertEqual(load_batch_state(path), disabled)


if __name__ == "__main__":
    unittest.main()
