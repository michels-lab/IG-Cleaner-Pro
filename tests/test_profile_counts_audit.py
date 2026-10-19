"""Offline re-audit evidence: no Instagram requests, real browser session or account actions."""
import csv
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_audit import (
    COLUMNS, audit_cycle_path, dated_history_path, ordered_audit_targets,
    new_cycle, resume_cycle, mark_attempt, append_dated_reading,
    seed_latest_readings, read_dated_page,
)
from profile_counts_bridge import Collector
from profile_counts_robot import save_results


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

    def test_append_only_progress_does_not_rewrite_large_queue(self):
        with TemporaryDirectory() as temp:
            path = audit_cycle_path(Path(temp) / "large.csv")
            users = [f"user.{i}" for i in range(3000)]
            cycle = new_cycle(path, users, {})
            initial = path.read_bytes()
            for user in users[:30]:
                mark_attempt(path, cycle, user)
            self.assertEqual(path.read_bytes(), initial,
                             "Immutable queue should never be rewritten for each visited profile")
            self.assertEqual(len(resume_cycle(path, users)["done"]), 30)
            self.assertEqual(len(list(path.parent.glob("*.done"))), 1)

    def test_windows_collector_explicit_cycle_resume_and_new_cycle(self):
        with TemporaryDirectory() as temp:
            collector = Collector(Path(temp), Path(temp) / "session")
            collector.owner, collector.account = "owner1", "account1"
            save_results(collector.result_path(), {
                "old": row("old", 100, 10, "2022-01-01T00:00:00Z"),
                "newer": row("newer", 200, 10, "2026-01-01T00:00:00Z")
            })
            request = dict(owner="owner1", account="account1",
                           usernames=["newer", "newprofile", "old"],
                           audit_mode="oldest_first")
            with patch("profile_counts_bridge.threading.Thread") as thread:
                thread.return_value.is_alive.return_value = False
                state = collector.auto_start(request)
                self.assertEqual(state["audit_mode"], "oldest_first")
                self.assertEqual(state["audit_total"], 3)
                self.assertEqual(collector.audit_cycle["targets"],
                                 ["newprofile", "old", "newer"])
                mark_attempt(audit_cycle_path(collector.result_path()),
                             collector.audit_cycle, "newprofile")
                collector.status = "paused"
                resumed = collector.continue_collection({
                    "owner": "owner1", "account": "account1"
                })
                self.assertEqual(resumed["audit_completed"], 1)
                self.assertEqual(resumed["audit_mode"], "oldest_first")
                self.assertEqual(collector.audit_cycle["done"], ["newprofile"])
                self.assertEqual(collector.audit_cycle["targets"],
                                 ["newprofile", "old", "newer"])
                # New process, same owner and Instagram: a new explicit click
                # resumes the frozen queue instead of discarding the journal.
                reopened = Collector(Path(temp), Path(temp) / "session")
                reopened.owner, reopened.account = "owner1", "account1"
                after_restart = reopened.auto_start(request)
                self.assertEqual(after_restart["audit_completed"], 1)
                self.assertEqual(reopened.audit_cycle["targets"],
                                 ["newprofile", "old", "newer"])
                cycle_path = audit_cycle_path(reopened.result_path())
                mark_attempt(cycle_path, reopened.audit_cycle, "old")
                mark_attempt(cycle_path, reopened.audit_cycle, "newer")
                reopened.status = "complete"
                fresh = reopened.auto_start(request)
                self.assertEqual(fresh["audit_completed"], 0)
                saved = read_dated_page(dated_history_path(collector.result_path()), 0, 10)
                self.assertEqual({r["followers"] for r in saved["rows"]}, {"100", "200"})

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
            done_file = p.with_name(p.name + "." + loaded["cycle_id"] + ".done")
            done_file.write_text("outsider\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid"):
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

    def test_malformed_success_claims_do_not_enter_history_or_delete_prior_evidence(self):
        with TemporaryDirectory() as temp:
            path = dated_history_path(Path(temp) / "workspace.csv")
            good = row("exact.user", 250, 47, "2026-10-18T10:00:00Z")
            append_dated_reading(path, good)
            before = path.read_bytes()
            failures = [
                {"followers": "12.3K"},
                {"followers": "1,234"},
                {"followers": "nan"},
                {"followers": "0;=IMPORT"},
                {"followers": None},
                {"following": ""},
                {"following": "99.5"},
                {"following": "-1"},
                {"checked_at": "not-a-date"},
                {"checked_at": "2026-10-18T10:00:00"},
                {"checked_at": "2099-01-01T10:00:00Z"},
                {"username": "../another-workspace"},
                {"username": "=HYPERLINK()"},
                {"status": "error"},
            ]
            for change in failures:
                invalid = dict(good, **change)
                with self.subTest(change=change):
                    append_dated_reading(path, invalid)
                    self.assertEqual(seed_latest_readings(path, {"corrupt": invalid}), 0)
                    self.assertEqual(path.read_bytes(), before)
            self.assertEqual(read_dated_page(path, 0, 20)["rows"][0]["followers"], "250")

    def test_valid_zero_and_approximate_integer_remain_supported(self):
        with TemporaryDirectory() as temp:
            path = dated_history_path(Path(temp) / "workspace.csv")
            valid = row("legit.user", 0, 12300, "2026-10-18T10:00:00+00:00")
            valid["approximate"] = "true"
            self.assertEqual(seed_latest_readings(path, {"legit.user": valid}), 1)
            saved = read_dated_page(path, 0, 10)["rows"]
            self.assertEqual(len(saved), 1)
            self.assertEqual(saved[0]["followers"], "0")
            self.assertEqual(saved[0]["following"], "12300")
            self.assertEqual(saved[0]["approximate"], "true")

    def test_invalid_ok_rows_are_prioritized_as_unmeasured_on_next_audit(self):
        valid = row("valid", 15, 30, "2026-10-18T10:00:00Z")
        no_proof = row("suspect", "12,345", 5, "2026-10-18T10:00:00Z")
        no_timestamp = row("undated", 10, 10, "not-a-date")
        queue = ordered_audit_targets(["valid", "suspect", "undated"], {
            "valid": valid, "suspect": no_proof, "undated": no_timestamp
        })
        self.assertEqual(queue[-1], "valid")
        self.assertEqual(set(queue[:-1]), {"suspect", "undated"})
        self.assertEqual(len(queue), 3)

    def test_historical_invalid_ok_rows_are_flagged_read_only_not_silently_deleted(self):
        with TemporaryDirectory() as temp:
            path = dated_history_path(Path(temp) / "a.csv")
            rows = [
                row("valid", 25, 10, "2026-10-18T13:00:00Z"),
                row("corrupt", "=IMPORTXML('http://example.test')", 10,
                    "2026-10-18T13:01:00Z"),
                row("future", 10, 10, "2099-01-01T00:00:00Z"),
                row("offline", "", "", "2026-10-18T13:02:00Z", "unavailable"),
            ]
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=COLUMNS)
                writer.writeheader()
                writer.writerows(rows)
            original = path.read_bytes()
            first = read_dated_page(path, 0, 2)
            self.assertEqual([x["status"] for x in first["rows"]],
                             ["ok", "invalid_evidence"])
            self.assertIn("recheck", first["rows"][1]["evidence_warning"])
            self.assertEqual(first["rows"][1]["followers"],
                             "=IMPORTXML('http://example.test')")
            self.assertEqual(first["next_offset"], 2)
            second = read_dated_page(path, 2, 2)
            self.assertEqual([x["status"] for x in second["rows"]],
                             ["invalid_evidence", "unavailable"])
            self.assertIsNone(second["next_offset"])
            self.assertNotIn("evidence_warning", first["rows"][0])
            self.assertEqual(path.read_bytes(), original,
                             "Old audit evidence is preserved byte for byte.")

    def test_historical_page_accepts_valid_numeric_zero_and_offset_pagination(self):
        with TemporaryDirectory() as temp:
            path = dated_history_path(Path(temp) / "zero.csv")
            successful = row("zero", 0, 0, "2026-10-18T13:00:00+00:00")
            successful["approximate"] = "true"
            append_dated_reading(path, successful)
            output = read_dated_page(path, 0, 10)
            self.assertEqual(len(output["rows"]), 1)
            self.assertEqual(output["rows"][0]["status"], "ok")
            self.assertEqual(output["rows"][0]["followers"], "0")
            self.assertEqual(output["rows"][0]["approximate"], "true")
            self.assertNotIn("evidence_warning", output["rows"][0])

    def test_unbounded_history_is_paginated(self):
        with TemporaryDirectory() as temp:
            p = dated_history_path(Path(temp) / "a.csv")
            values = {f"profile.{i}": row(f"profile_{i}", i, i+1,
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
