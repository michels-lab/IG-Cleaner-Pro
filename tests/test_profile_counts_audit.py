"""Offline re-audit evidence: no Instagram requests, real browser session or account actions."""
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_audit import (
    audit_cycle_path, dated_history_path, ordered_audit_targets,
    new_cycle, resume_cycle, mark_attempt, append_dated_reading,
    seed_latest_readings, read_dated_page,
)
from profile_counts_bridge import Collector


def row(user, followers, following, stamp, status="ok"):
    return dict(username=user, followers=str(followers), following=str(following),
                checked_at=stamp, source="visible", status=status, approximate="false")


class ProfileCountsReauditTests(unittest.TestCase):
    def test_new_first_then_oldest_and_stable_queue(self):
        saved = {
            "old": row("old", 100, 12, "2023-02-01T02:00:00Z"),
            "recent": row("recent", 200, 20, "2026-10-01T00:00:00Z"),
            "error": row("error", "", "", "2026-09-01T00:00:00Z", "error"),
            "unavailable": row("unavailable", "", "", "2026-08-01T00:00:00Z", "unavailable")
        }
        actual = ordered_audit_targets(
            ["recent", "old", "new", "error", "unavailable", "new"], saved)
        self.assertEqual(actual, ["new", "unavailable", "error", "old", "recent"])
        # Never-successful are prioritized even if their last failed attempt is recent.
        self.assertEqual(len(actual), len(set(actual)))

    def test_cycle_journal_resumes_without_repeat(self):
        with TemporaryDirectory() as temp:
            path = audit_cycle_path(Path(temp) / "account-1.csv")
            users = ["new", "old", "recent"]
            saved = {
                "old": row("old", 100, 12, "2022-01-01T00:00:00Z"),
                "recent": row("recent", 200, 40, "2026-01-01T00:00:00Z")
            }
            created = new_cycle(path, users, saved)
            self.assertEqual(created["targets"], ["new", "old", "recent"])
            mark_attempt(path, created, "new")
            mark_attempt(path, created, "new")
            resumed = resume_cycle(path, users)
            self.assertEqual(resumed["done"], ["new"])
            self.assertEqual([u for u in resumed["targets"] if u not in resumed["done"]],
                             ["old", "recent"])
            mark_attempt(path, resumed, "old")
            self.assertEqual(resume_cycle(path, users)["done"], ["new", "old"])
            # The next explicit cycle reorders by the newest stored measurement.
            next_saved = dict(saved, old=row("old", 110, 11, "2026-10-01T00:00:00Z"))
            renewed = new_cycle(path, users, next_saved)
            self.assertEqual(renewed["targets"], ["new", "recent", "old"])
            self.assertEqual(renewed["done"], [])

    def test_account_workspace_scope(self):
        with TemporaryDirectory() as temp:
            collector = Collector(Path(temp), Path(temp) / "session")
            collector.owner, collector.account = "owner-A", "instagram-A"
            a = collector.result_path()
            collector.account = "instagram-B"
            b = collector.result_path()
            collector.owner = "owner-B"
            c = collector.result_path()
            self.assertEqual(len({a, b, c}), 3)
            self.assertEqual(len({audit_cycle_path(a), audit_cycle_path(b), audit_cycle_path(c)}), 3)
            self.assertNotIn("owner-A", str(a))
            self.assertNotIn("instagram-A", str(a))

    def test_reject_foreign_or_tampered_journal(self):
        with TemporaryDirectory() as temp:
            p = audit_cycle_path(Path(temp) / "a.csv")
            new_cycle(p, ["one", "two"], {})
            with self.assertRaisesRegex(ValueError, "differs"):
                resume_cycle(p, ["two"])
            loaded = json.loads(p.read_text(encoding="utf-8"))
            loaded["done"] = ["outsider"]
            p.write_text(json.dumps(loaded), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs"):
                resume_cycle(p, ["one", "two"])

    def test_archive_legacy_and_new_snapshots_idempotently(self):
        with TemporaryDirectory() as temp:
            p = dated_history_path(Path(temp) / "a.csv")
            old = row("sample", 123, 10, "2026-01-01T00:00:00Z")
            next_one = row("sample", 150, 12, "2026-05-01T00:00:00Z")
            self.assertEqual(seed_latest_readings(p, {"sample": old}), 1)
            self.assertEqual(seed_latest_readings(p, {"sample": old}), 0)
            append_dated_reading(p, next_one)
            self.assertEqual(seed_latest_readings(p, {"sample": next_one}), 0)
            all_rows = list(csv.DictReader(p.open(encoding="utf-8")))
            self.assertEqual([r["followers"] for r in all_rows], ["123", "150"])
            self.assertEqual([r["checked_at"] for r in all_rows],
                             [old["checked_at"], next_one["checked_at"]])

    def test_failed_probes_never_enter_successful_history(self):
        with TemporaryDirectory() as temp:
            p = dated_history_path(Path(temp) / "a.csv")
            append_dated_reading(p, row("one", "", "", "2026-05-01T00:00:00Z", "error"))
            self.assertFalse(p.exists())
            good = row("one", 900, 19, "2026-05-02T00:00:00Z")
            append_dated_reading(p, good)
            seed_latest_readings(p, {"one": row("one", "", "", "2026-05-03T00:00:00Z", "error")})
            self.assertEqual(read_dated_page(p, 0, 10)["rows"][0]["followers"], "900")

    def test_unbounded_history_is_paginated(self):
        with TemporaryDirectory() as temp:
            p = dated_history_path(Path(temp) / "a.csv")
            values = {f"profile_{i}": row(f"profile_{i}", i, i+1,
                       "2026-10-15T00:00:00Z") for i in range(2501)}
            self.assertEqual(seed_latest_readings(p, values), 2501)
            first = read_dated_page(p, 0, 2000)
            second = read_dated_page(p, first["next_offset"], 2000)
            self.assertEqual(len(first["rows"]), 2000)
            self.assertEqual(len(second["rows"]), 501)
            self.assertIsNone(second["next_offset"])
            self.assertEqual(len(first["rows"])+len(second["rows"]), len(values))
            with self.assertRaises(ValueError):
                read_dated_page(p, -1, 100)
            with self.assertRaises(ValueError):
                read_dated_page(p, 0, 2001)


if __name__ == "__main__":
    unittest.main()
