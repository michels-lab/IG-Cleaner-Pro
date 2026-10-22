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

    def test_interrupted_click_aggregates_only_fixed_phases_without_identity(self):
        with TemporaryDirectory() as directory:
            root=Path(directory)
            secret="SECRET_EXACT_INSTAGRAM_TARGET_883"
            (root/"instagram-actions-a.json").write_text(json.dumps({
                secret:{"status":"review","issue":"interrupted_action_uncertain",
                        "click_intent":{"phase":"unfollow_menu",
                                        "batch_id":"PRIVATE_BATCH_529",
                                        "outcome_recorded":False},
                        "message":"private journal result"},
                "another.private.account":{"status":"ok",
                    "click_intent":{"phase":"cancel_request_confirmation",
                                    "outcome_recorded":True}},
            }),encoding="utf-8")
            report=run_audit(root)
            self.assertEqual(report["interrupted_action_intents"],1)
            self.assertEqual(report["click_phase_counts"],{"unfollow_menu":1})
            self.assertEqual(report["issue_code_counts"],
                             {"interrupted_action_uncertain":1})
            findings={x["code"]:x["count"] for x in report["findings"]}
            self.assertEqual(findings["INTERRUPTED_ACTION_INTENT"],1)
            prompt=ai_prompt(report)
            self.assertIn("INTERRUPTED_ACTION_INTENT",prompt)
            self.assertIn("unfollow_menu",prompt)
            self.assertNotIn(secret,json.dumps(report)+prompt)
            self.assertNotIn("PRIVATE_BATCH_529",json.dumps(report)+prompt)
            self.assertNotIn("another.private.account",json.dumps(report)+prompt)
            compromised={**report,"click_phase_counts":{
                "unfollow_menu":1,secret:999},
                "interrupted_action_intents":True}
            cleaned=json.loads(ai_prompt(compromised).split("\n\n",1)[1])["backend"]
            self.assertEqual(cleaned["click_phase_counts"],{"unfollow_menu":1})
            self.assertEqual(cleaned["interrupted_action_intents"],0)

    def test_pending_cohort_forensics_keep_old_batches_and_original_journals(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            secret = "SECRET_BROKEN_COUPLING_917"
            journal = root / "instagram-actions-scope-a.json"
            journal.write_text(json.dumps({
                "terminal": {"status": "ok", "message": "Unfollow verified"},
                "safeblocked": {
                    "status": "blocked", "issue": "requires_manual_review",
                    "message": "Instagram session verification failed before the first click. No action performed."},
                secret: {"status": "review", "issue": "interrupted_action_uncertain",
                         "click_intent": {"phase": "unfollow_menu",
                                          "outcome_recorded": False,
                                          "batch_id": "PRIVATE_COHORT_123"}},
                "errormaybe": {"status": "error", "message": "No action clicked."},
                "badintent": {"status": "ok", "click_intent": "malformed intent"},
            }), encoding="utf-8")
            batch = root / "instagram-actions-scope-a-batch-reviews.json"
            batch.write_text(json.dumps([
                {"id": "original cohort secret", "targets": [
                    "terminal", "safeblocked", secret, "untouched",
                    "errormaybe", "badintent"], "approved_at": None,
                 "recheck_results": {
                     "untouched": {"status": "observed_not_following"}}},
                {"id": "deferred secret", "targets": ["historical"],
                 "approved_at": None, "deferred_at": "2026-10-20T00:00:00Z"},
                {"id": "approved secret", "targets": ["other"],
                 "approved_at": "2026-10-20T00:00:00Z"},
            ]), encoding="utf-8")
            journal_before, batch_before = journal.read_bytes(), batch.read_bytes()
            report = run_audit(root)
            expected = {
                "unapproved_batches": 1, "pending_batch_targets": 6,
                "pending_batch_recorded_terminals": 1,
                "pending_batch_safe_preclick": 1,
                "pending_batch_uncertain": 3,
                "pending_batch_untouched": 1,
                "pending_batch_unknown_journal": 0,
                "pending_batch_readonly_observations": 1,
            }
            for key, value in expected.items():
                self.assertEqual(report[key], value, key)
            findings = {x["code"] for x in report["findings"]}
            self.assertIn("BATCH_UNTOUCHED_PROFILES", findings)
            self.assertIn("BATCH_UNCERTAIN_ACTIONS", findings)
            self.assertNotIn("BATCH_ZERO_RECORDED_TERMINALS", findings)
            self.assertNotIn("BATCH_JOURNAL_UNKNOWN", findings)
            self.assertEqual(journal_before, journal.read_bytes())
            self.assertEqual(batch_before, batch.read_bytes())
            exported = json.loads(ai_prompt(report).split("\n\n", 1)[1])["backend"]
            self.assertEqual(exported["pending_batch_uncertain"], 3)
            self.assertNotIn(secret, json.dumps(report) + ai_prompt(report))
            self.assertNotIn("PRIVATE_COHORT_123", json.dumps(report) + ai_prompt(report))
            self.assertNotIn("original cohort secret", json.dumps(report) + ai_prompt(report))

    def test_no_journal_or_click_intent_cannot_be_classified_as_safe_retry(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            secret = "PRIVATE_ACCOUNT_EVIDENCE_288"
            (root / "instagram-actions-known.json").write_text(json.dumps({
                secret: {
                    "status": "blocked", "issue": "requires_manual_review",
                    "message": "Instagram session verification failed before the first click. No action performed.",
                    "click_intent": {"phase": "relationship_control",
                                     "outcome_recorded": False}},
            }), encoding="utf-8")
            (root / "instagram-actions-known-batch-reviews.json").write_text(
                json.dumps([{"targets": [secret], "approved_at": None}]),
                encoding="utf-8")
            (root / "instagram-actions-missing-batch-reviews.json").write_text(
                json.dumps([{"targets": ["unrecorded", "alsounrecorded"],
                             "approved_at": None, "recheck_results": {}}]),
                encoding="utf-8")
            report = run_audit(root)
            self.assertEqual(report["unapproved_batches"], 2)
            self.assertEqual(report["pending_batch_targets"], 3)
            self.assertEqual(report["pending_batch_unknown_journal"], 2)
            self.assertEqual(report["pending_batch_untouched"], 0)
            self.assertEqual(report["pending_batch_safe_preclick"], 0)
            self.assertEqual(report["pending_batch_uncertain"], 1)
            findings = {x["code"] for x in report["findings"]}
            self.assertIn("BATCH_JOURNAL_UNKNOWN", findings)
            self.assertIn("BATCH_ZERO_RECORDED_TERMINALS", findings)
            self.assertNotIn("RETRYABLE_ZERO_CLICK", findings)
            self.assertNotIn(secret, json.dumps(report) + ai_prompt(report))

    def test_malformed_or_duplicate_cohort_targets_never_crash_audit(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "instagram-actions-shape.json").write_text("{}")
            (root / "instagram-actions-shape-batch-reviews.json").write_text(
                json.dumps([{"targets": ["one", "one", 12, {"private": "secret"},
                                         "x" * 90], "approved_at": None}]))
            report = run_audit(root)
            self.assertEqual(report["pending_batch_targets"], 1)
            self.assertEqual(report["pending_batch_untouched"], 1)
            self.assertEqual(report["unapproved_batches"], 1)
            findings = {x["code"] for x in report["findings"]}
            self.assertIn("BATCH_INVALID_TARGET", findings)
            self.assertNotIn("secret", json.dumps(report) + ai_prompt(report))

    def test_present_malformed_journal_evidence_is_never_untouched_or_replayable(self):
        """Developer forensic counters must agree with the real robot's no-replay gate."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "instagram-actions-fixture.json"
            no_click = (
                "Instagram session verification failed before the first click. "
                "No action performed."
            )
            saved = {
                "bad_type": 123,
                "nullvalue": None,
                "empty": {},
                "missing_status": {"click_intent": {
                    "phase": "relationship_control", "outcome_recorded": False}},
                "null_click_block": {"status": "blocked", "message": no_click,
                                     "click_intent": None},
                "null_click_review": {"status": "review",
                                      "issue": "missing_profile_info",
                                      "message": "The profile does not show the state required for this action.",
                                      "click_intent": None},
                "null_click_ok": {"status": "ok", "click_intent": None},
                "unrecognized_phase": {"status": "ok", "click_intent": {
                    "phase": "unexpected_private_action", "outcome_recorded": True}},
                "list_phase": {"status": "ok", "click_intent": {
                    "phase": ["nonhashable"], "outcome_recorded": True}},
                "safe_block": {"status": "blocked", "message": no_click},
                "valid_terminal": {"status": "already_not_following",
                                   "message": "Already not following: exact profile."},
            }
            original.write_text(json.dumps(saved), encoding="utf-8")
            cohorts = root / "instagram-actions-fixture-batch-reviews.json"
            cohorts.write_text(json.dumps([{
                "id": "saved-private-batch",
                "targets": list(saved) + ["genuinely_absent"],
                "approved_at": None,
            }]), encoding="utf-8")
            original_bytes, cohort_bytes = original.read_bytes(), cohorts.read_bytes()

            report = run_audit(root)
            self.assertEqual(report["pending_batch_targets"], 12)
            self.assertEqual(report["pending_batch_untouched"], 1)
            self.assertEqual(report["pending_batch_safe_preclick"], 1)
            self.assertEqual(report["pending_batch_recorded_terminals"], 1)
            self.assertEqual(report["pending_batch_uncertain"], 9)
            findings = {f["code"]: f["count"] for f in report["findings"]}
            self.assertEqual(findings["INVALID_ACTION_RECORD"], 2)
            self.assertEqual(findings["BATCH_UNCERTAIN_ACTIONS"], 1)
            # The null click-intent is NOT a proven zero-click result.
            self.assertEqual(findings["RETRYABLE_ZERO_CLICK"], 1)
            self.assertEqual(original.read_bytes(), original_bytes)
            self.assertEqual(cohorts.read_bytes(), cohort_bytes)
            exported = json.dumps(report) + ai_prompt(report)
            for private in (*saved.keys(), "saved-private-batch"):
                self.assertNotIn(private, exported)

    def test_corrupt_history_is_not_exception(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "instagram-actions-corrupt.json").write_text("{corrupt")
            (root / "instagram-actions-invalid.json").write_text('{"invalid": 123}')
            result = run_audit(root)
            self.assertEqual({v["code"] for v in result["findings"]},
                             {"INVALID_ACTION_RECORD", "JOURNAL_UNREADABLE"})

    def test_symlinked_journals_are_skipped_without_leaking_other_workspace(self):
        with TemporaryDirectory() as folder:
            base = Path(folder)
            workspace = base / "developer"
            workspace.mkdir()
            external = base / "unrelated-private.json"
            secret = "SECRET_OUTSIDE_OWNER_WORKSPACE_793"
            external.write_text(json.dumps({
                secret: {"status": "blocked", "issue": "requires_manual_review",
                         "message": "manual " + secret}
            }), encoding="utf-8")
            actual = workspace / "instagram-actions-local.json"
            actual.write_text(json.dumps({"local_test_profile": {
                "status": "ok", "issue": "requires_manual_review"}}), encoding="utf-8")
            links = (
                workspace / "instagram-actions-leaked.json",
                workspace / "instagram-actions-leaked-batch-reviews.json",
                workspace / "instagram-actions-leaked-historical-rechecks.json",
            )
            try:
                for link in links:
                    link.symlink_to(external)
            except (OSError, NotImplementedError):
                self.skipTest("Creating symlinks needs elevated privileges on this platform")
            before = external.read_bytes()
            report = run_audit(workspace)
            self.assertEqual(report["journals"], 1)
            self.assertEqual(report["profiles"], 1)
            self.assertEqual(report["unapproved_batches"], 0)
            self.assertEqual(report["historical_readonly_observations"], 0)
            counts = {x["code"]: x["count"] for x in report["findings"]}
            self.assertEqual(counts["EXTERNAL_JOURNAL_LINK_SKIPPED"], 3)
            self.assertNotIn(secret, json.dumps(report))
            self.assertNotIn(secret, ai_prompt(report))
            self.assertEqual(external.read_bytes(), before)

    def test_auditor_refuses_symlink_root_without_reading_external_history(self):
        with TemporaryDirectory() as folder:
            base = Path(folder)
            external = base / "private-backups"
            external.mkdir()
            secret = "PRIVATE_ROOT_ACCOUNT_614"
            (external / "instagram-actions-x.json").write_text(json.dumps({
                secret: {"status": "blocked", "issue": "requires_manual_review"}
            }), encoding="utf-8")
            link = base / "developer"
            try:
                link.symlink_to(external, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("Directory symlinks unavailable")
            result = run_audit(link)
            self.assertEqual(result["profiles"], 0)
            self.assertEqual(result["journals"], 0)
            self.assertEqual(result["findings"][0]["code"], "AUDIT_ROOT_IS_SYMLINK")
            self.assertIn("AUDIT_ROOT_IS_SYMLINK", ai_prompt(result))
            self.assertNotIn(secret, json.dumps(result))

    def test_ai_export_never_copies_untrusted_diagnostic_strings(self):
        private = "PRIVATE_INSTAGRAM_482"
        compromised = {
            "schema": private, "product": private,
            "generated_at": "now " + private,
            "source_revision": "Bearer=" + private,
            "mode": private, "privacy": private,
            "journals": 2, "profiles": 4,
            "unapproved_batches": True, "historical_readonly_observations": 4,
            "action_status_counts": {"ok": 2, private: 99, 7: 5},
            "issue_code_counts": {"requires_manual_review": 1, private: 98},
            "findings": [
                {"code": "UNCERTAIN_OR_MANUAL", "severity": private,
                 "action": "send cookies " + private, "count": 3},
                {"code": private, "action": private, "count": 700},
            ],
            "limitations": ["https://instagram.com/accounts?token=" + private],
        }
        checks = {"app_revision": "@" + private,
                  "username": private, "uncaught_ui_errors": 2}
        prompt = ai_prompt(compromised, checks)
        self.assertNotIn(private, prompt)
        self.assertNotIn("send cookies", prompt)
        self.assertNotIn("Bearer=", prompt)
        self.assertIn("UNCERTAIN_OR_MANUAL", prompt)
        self.assertIn("uncaught_ui_errors", prompt)
        backend = json.loads(prompt.split("\n\n", 1)[1])["backend"]
        self.assertEqual(backend["source_revision"], "unknown")
        self.assertEqual(backend["unapproved_batches"], 0)
        self.assertEqual(backend["action_status_counts"], {"ok": 2})
        self.assertEqual(backend["issue_code_counts"], {"requires_manual_review": 1})
        self.assertEqual(backend["findings"][0]["count"], 3)
        self.assertEqual(backend["findings"][0]["severity"], "warning")
        with TemporaryDirectory() as folder:
            actual = run_audit(Path(folder), source_revision="token=" + private)
            self.assertEqual(actual["source_revision"], "unknown")
            self.assertNotIn(private, json.dumps(actual))


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
