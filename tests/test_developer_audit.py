"""Read-only Developer Edition regression tests."""
import json
import sys
import unittest
import threading
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from developer_audit import run_audit, ai_prompt
from ig_cleaner_desktop import chrome_app_args
from profile_counts_bridge import Collector, build_server

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


class ReadOnlyDevBridgeTest(unittest.TestCase):
    def test_diagnostics_endpoint_and_mutation_guard(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            (root/"instagram-actions-a.json").write_text(json.dumps({
                "local_test_profile":{"status":"review","issue":"requires_manual_review",
                                      "message":"Unverified action."}}))
            collector=Collector(root/"scratch",root/"browser")
            server=build_server(collector,"0123456789abcdefghijklmnop",0,
                                developer_mode=True,audit_root=root)
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            base="http://127.0.0.1:"+str(server.server_port)
            headers={"X-IGC-Bridge-Token":"0123456789abcdefghijklmnop","Content-Type":"application/json"}
            try:
                request=Request(base+"/api/developer/audit",data=b"{}",headers=headers,method="POST")
                with urlopen(request,timeout=6) as response:
                    result=json.load(response)
                self.assertEqual(result["report"]["profiles"],1)
                self.assertIn("UNCERTAIN_OR_MANUAL",result["ai_prompt"])
                self.assertNotIn("local_test_profile",json.dumps(result))
                request=Request(base+"/api/actions/start",data=b"{}",headers=headers,method="POST")
                with self.assertRaises(HTTPError) as failure:
                    urlopen(request,timeout=6)
                self.assertEqual(failure.exception.code,400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=6)

if __name__ == "__main__":
    unittest.main()
