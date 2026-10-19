"""Read-only Developer Edition regression tests."""
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from developer_audit import run_audit, ai_prompt
from ig_cleaner_desktop import chrome_app_args

class DeveloperAuditTest(unittest.TestCase):
    def test_redacted_evidence_preserves_journal(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            record_path = root / "instagram-actions-a.json"
            record_path.write_text(json.dumps({
                "some_test_user": {"status": "blocked", "issue": "requires_manual_review",
                                   "message": "Instagram session verification failed before the first click. No action performed."},
                "another_test_user": {"status": "ok", "message": "Action confirmed"}}))
            batch_path = root / "instagram-actions-a-batch-reviews.json"
            batch_path.write_text(json.dumps([{"targets": ["some_test_user"], "approved_at": None}]))
            before = record_path.read_bytes()
            report = run_audit(root)
            prompt = ai_prompt(report, {"uncaught_ui_errors": 2, "username": "some_test_user"})
            self.assertEqual(report["profiles"], 2)
            self.assertEqual(report["unapproved_batches"], 1)
            self.assertTrue(any(f["code"] == "RETRYABLE_ZERO_CLICK" for f in report["findings"]))
            self.assertNotIn("some_test_user", prompt)
            self.assertNotIn("another_test_user", json.dumps(report))
            self.assertIn("uncaught_ui_errors", prompt)
            self.assertEqual(before, record_path.read_bytes())

    def test_corrupt_history_is_not_exception(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "instagram-actions-corrupt.json").write_text("{corrupt")
            (root / "instagram-actions-invalid.json").write_text('{"invalid": 123}')
            result = run_audit(root)
            self.assertEqual({v["code"] for v in result["findings"]},
                             {"INVALID_ACTION_RECORD", "JOURNAL_UNREADABLE"})

    def test_distinct_developer_chrome_workspace(self):
        args = chrome_app_args(Path("chrome.exe"), Path("app.html"), Path("developer-edition"), 53001,
                               "0123456789abcdefghijklmnopqrstuvwxyz", developer=True)
        self.assertIn("igc-developer=1", args[-1])
        self.assertIn("developer-edition", args[-2])

if __name__ == "__main__":
    unittest.main()
