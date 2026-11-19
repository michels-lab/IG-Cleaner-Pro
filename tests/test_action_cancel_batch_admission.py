"""GRANADA: idle Cancel Batch is WAL-lease guarded in both Windows windows.

Offline integration through the real loopback controller. Never opens Chrome,
calls Instagram, makes an Unfollow/Cancel Pending click or edits real data.
"""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server
from robot_interlock import ActionLease, ActionSessionBusy

OWNER = "u_owner_42"
A, B = "ig_alpha_12345678", "ig_beta_12345678"


class IdleCancelAdmissionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.collector = Collector(self.root / "data", self.root / "browser")
        self.robot = ActionRobot(self.collector, self.collector.data_dir,
                                 self.collector.session_dir)

    def seed(self, account=A, task="unfollow", batch="saved-40"):
        path = self.robot._review_batches_file_for(OWNER, account, task)
        journal = self.robot._base_for(OWNER, account, task)
        _atomic_json(path, [{"id": batch,
                            "targets": ["previous.ok", "possibly.clicked", "fresh.one"],
                            "approved_at": None, "recheck_results": {}}])
        _atomic_json(journal, {
            "previous.ok": {"status": "ok", "at": "2026-11-10T12:00:00Z"},
            "possibly.clicked": {"status": "review",
                                 "click_intent": {"phase": "relationship_control",
                                                  "requires_manual_review": True}}
        })
        return path, journal

    def command(self, account=A, task="unfollow", batch="saved-40"):
        return {"owner": OWNER, "account": account, "task": task,
                "batch_id": batch, "confirmation": "cancel-batch:" + batch}

    def test_direct_cold_start_is_blocked_by_other_windows_action_worker(self):
        batch, journal = self.seed()
        before = batch.read_bytes(), journal.read_bytes()
        lease = ActionLease(self.collector.data_dir).acquire()
        try:
            with self.assertRaises(ActionSessionBusy):
                self.robot.cancel_current_batch(self.command())
            with self.assertRaises(ActionSessionBusy):
                self.robot.cancel_saved_batch(self.command())
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), before)
            self.assertEqual((self.robot.owner, self.robot.status), ("", "idle"))
            self.assertFalse(self.robot.cancel_requested)
        finally:
            lease.release()
        # Same direct API can recover a named saved batch after app restart.
        result = self.robot.cancel_current_batch(self.command())
        self.assertEqual(result["status"], "cancelled")
        self.assertFalse(result["running"])
        self.assertFalse(result["cancel_requested"])
        self.assertEqual(result["recorded"], 2)
        self.assertEqual(result["untouched"], 1)
        self.assertEqual(journal.read_bytes(), before[1],
                         "Confirmed and possible-click WAL entries are immutable.")
        stored = json.loads(batch.read_text("utf-8"))[0]
        self.assertEqual(stored["deferred_reason"], "owner_cancelled")
        self.assertFalse(stored["marked_reviewed"])
        with self.assertRaisesRegex(ValueError, "changed"):
            self.robot.cancel_current_batch(self.command())

    def test_wrong_batch_or_account_cannot_archive_other_saved_evidence(self):
        a_batch, a_journal = self.seed(A)
        b_batch, b_journal = self.seed(B, task="cancel", batch="pending-B")
        before = [p.read_bytes() for p in (a_batch, a_journal, b_batch, b_journal)]
        wrong = [
            {**self.command(), "confirmation": "cancel-batch:wrong"},
            {**self.command(), "batch_id": "other-batch"},
            self.command(account=B),
            self.command(task="cancel"),
            self.command(account=B, task="cancel", batch="saved-40")
        ]
        for request in wrong:
            with self.subTest(request=request), self.assertRaises(ValueError):
                self.robot.cancel_current_batch(request)
            self.assertEqual([p.read_bytes() for p in
                              (a_batch, a_journal, b_batch, b_journal)], before)
        result = self.robot.cancel_saved_batch(self.command(
            account=B, task="cancel", batch="pending-B"))
        self.assertEqual(result["account"], B)
        self.assertEqual(a_batch.read_bytes(), before[0])
        self.assertEqual(a_journal.read_bytes(), before[1])
        self.assertEqual(b_journal.read_bytes(), before[3])

    def test_live_cancel_signals_without_reacquiring_worker_owned_lease(self):
        self.seed()
        self.robot.owner, self.robot.account, self.robot.task = OWNER, A, "unfollow"
        self.robot.worker = Mock()
        self.robot.worker.is_alive.return_value = True
        self.robot._lease_factory = lambda *_: self.fail(
            "Live cancellation must not reacquire its own OS worker lease")
        result = self.robot.cancel_current_batch(self.command())
        self.assertEqual(result["status"], "cancelling")
        self.assertTrue(result["running"])
        self.assertTrue(self.robot.stop_event.is_set())
        self.assertTrue(self.robot.cancel_requested)
        self.assertIsNotNone(self.robot._pending_review(OWNER, A, "unfollow"),
                             "The live worker owns archival only AFTER its current action ends.")

    def test_real_local_http_cancel_after_relaunch_obeys_kernel_lock(self):
        batch, journal = self.seed()
        before = batch.read_bytes(), journal.read_bytes()
        server = build_server(self.collector, "x" * 32, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:" + str(server.server_port) + "/api/actions/cancel-batch"

        def post(body, token="x" * 32):
            request = urllib.request.Request(
                url, data=json.dumps(body).encode("utf-8"), method="POST",
                headers={"X-IGC-Bridge-Token": token,
                         "Content-Type": "application/json", "Origin": "null"})
            try:
                with urllib.request.urlopen(request, timeout=4) as result:
                    return result.status, json.load(result)
            except urllib.error.HTTPError as error:
                return error.code, json.load(error)

        try:
            self.assertNotEqual(post(self.command(), token="invalid")[0], 200)
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), before)
            lease = ActionLease(self.collector.data_dir).acquire()
            try:
                status, _ = post(self.command())
                self.assertNotEqual(status, 200)
                self.assertEqual((batch.read_bytes(), journal.read_bytes()), before)
            finally:
                lease.release()
            status, response = post(self.command())
            self.assertEqual(status, 200, response)
            self.assertEqual(response["status"], "cancelled")
            self.assertEqual(response["batch_id"], "saved-40")
            self.assertEqual(journal.read_bytes(), before[1])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=4)


if __name__ == "__main__":
    unittest.main()
