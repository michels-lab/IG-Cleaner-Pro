"""GRANADA #9: never trust status='ok' without complete count/date evidence."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from profile_counts_robot import (
    pending_count_targets, read_results, save_results, valid_saved_measurement,
)
from profile_counts_bridge import Collector
from profile_counts_audit import dated_history_path, read_dated_page


def reading(name, following="25", followers="300", date="2026-10-18T20:00:00Z",
            status="ok", approximate="false"):
    return {
        "username": name, "followers": followers, "following": following,
        "checked_at": date, "source": "instagram_visible_profile_browser",
        "status": status, "approximate": approximate,
    }


class FalseSuccessfulCountsTests(unittest.TestCase):
    def test_cli_resume_rechecks_corrupt_ok_but_preserves_retry_opt_in_for_failures(self):
        rows = {
            "good": reading("good"),
            "rounded": reading("rounded", followers="12.3K"),
            "undated": reading("undated", date="not-a-date"),
            "future": reading("future", date="2099-01-01T00:00:00Z"),
            "missing": reading("missing", following=""),
            "failed": reading("failed", followers="", following="",
                              status="unavailable"),
            "zero": reading("zero", followers="0", following="0",
                            approximate="true"),
        }
        expected = ["rounded", "undated", "future", "missing", "new"]
        queue = list(rows) + ["new"]
        self.assertEqual(pending_count_targets(queue, rows), expected)
        self.assertEqual(pending_count_targets(queue, rows, True), expected[:-1]+["failed", "new"])
        self.assertTrue(valid_saved_measurement(rows["good"]))
        self.assertTrue(valid_saved_measurement(rows["zero"]))
        for name in ("rounded", "undated", "future", "missing", "failed"):
            self.assertFalse(valid_saved_measurement(rows[name]))

    def test_owner_read_only_load_and_resume_metrics_do_not_claim_corrupt_row_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Collector(Path(tmp) / "results", Path(tmp) / "session")
            c.owner, c.account = "owner-A", "ig-account-A"
            original = {
                "good": reading("good"),
                "suspect": reading("suspect", followers="500", following="bad"),
                "unavailable": reading("unavailable", followers="", following="",
                                       status="unavailable"),
            }
            path = c.result_path()
            save_results(path, original)
            before = path.read_bytes()
            state = c.start(dict(owner=c.owner, account=c.account,
                                 usernames=list(original)), load_only=True)
            self.assertEqual(state["successful"], 1)
            self.assertEqual(state["remaining"], 2)
            self.assertEqual(state["pending"], 1)
            self.assertEqual(state["progress"], 1)
            responses = {row["username"]: row for row in c.results()}
            self.assertEqual(responses["good"]["status"], "ok")
            self.assertEqual(responses["suspect"]["status"], "invalid_evidence")
            self.assertIn("recheck required", responses["suspect"]["evidence_warning"])
            self.assertEqual(responses["unavailable"]["status"], "unavailable")
            self.assertEqual(read_results(path)["suspect"]["status"], "ok",
                             "Historical source evidence must NOT be rewritten by displaying UI.")
            self.assertEqual(path.read_bytes(), before)
            dated = read_dated_page(dated_history_path(path), 0, 100)["rows"]
            self.assertEqual([r["username"] for r in dated], ["good"])

    def test_independent_instagram_workspaces_do_not_reuse_success_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            c = Collector(Path(tmp)/"results",Path(tmp)/"session")
            c.owner,c.account = "owner-1","instagram-1"
            save_results(c.result_path(),{"same":reading("same")})
            first_path = c.result_path()
            c.account="instagram-2"
            save_results(c.result_path(),{"same":reading("same",followers="no-data")})
            second_path = c.result_path()
            self.assertNotEqual(first_path, second_path)
            c.start(dict(owner=c.owner,account=c.account,usernames=["same"]),load_only=True)
            self.assertEqual(c.snapshot()["successful"],0)
            self.assertEqual(c.results()[0]["status"],"invalid_evidence")
            c.account = "instagram-1"
            self.assertEqual(valid_saved_measurement(read_results(c.result_path())["same"]),True)
            self.assertEqual(read_results(first_path)["same"]["followers"],"300")
            self.assertEqual(read_results(second_path)["same"]["followers"],"no-data")


if __name__ == "__main__":
    unittest.main()
