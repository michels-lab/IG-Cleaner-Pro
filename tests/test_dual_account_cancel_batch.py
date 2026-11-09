"""Granada: exact-account cancellation of saved and running dual-action batches.

Synthetic journals, real OS leases and actual ActionRobot start code; fake worker
bodies replace Instagram navigation. No website or relationship action.
"""
import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from dual_action_workspaces import DualActionWorkspaces
from dual_chrome_sessions import DualChromeSessions
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector
from robot_interlock import ActionLease, ActionSessionBusy

OWNER = "u_owner_42"
A, B = "ig_alpha_12345678", "ig_beta_12345678"


def pair(parallel=False):
    return {
        "owner": OWNER,
        "primary": {"account": A, "expected_handle": "alpha.one"},
        "secondary": {"account": B, "expected_handle": "beta.two"},
        "read_only_consent": True,
        "parallel_actions_consent": parallel,
        "acknowledge_parallel_actions": parallel,
        "acknowledge_serial_actions": not parallel,
        "confirmation": ("dual-action-workspaces-parallel:" if parallel
                         else "dual-action-workspaces:") + A + ":" + B,
    }


def cancel(account=A, task="unfollow", batch_id="saved-A"):
    return {
        "owner": OWNER, "account": account, "task": task,
        "batch_id": batch_id,
        "confirmation": "action-workspace-cancel:" + OWNER + ":" + account +
                        ":" + task + ":" + batch_id,
    }


def command(account, handle, task, target):
    action = {
        "owner": OWNER, "account": account, "expected_handle": handle,
        "task": task, "targets": [target], "batch_size": 1, "protected": [],
        "gap_seconds": 15, "rest_minutes": 0, "confirmation": task + ":1",
    }
    if task == "unfollow":
        action["followers_evidence"] = True
    return {
        "owner": OWNER, "account": account, "action": action,
        "confirmation": "action-workspace-start:" + OWNER + ":" + account + ":" + task,
        "parallel_action_confirmation":
            "parallel-action-workspace-start:" + OWNER + ":" + account + ":" + task,
    }


class DualBatchCancelTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "data", self.root / "legacy-browser")
        self.sessions = DualChromeSessions(self.root / "browser")
        self.legacy = ActionRobot(
            self.collector, self.collector.data_dir, self.collector.session_dir)
        self.manager = DualActionWorkspaces(
            self.sessions, self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(self.manager.shutdown)

    def seed(self, account, task, batch_id, records, targets):
        robot = self.manager.workspaces[account]["robot"]
        batchfile = robot._review_batches_file_for(OWNER, account, task)
        journal = robot._base_for(OWNER, account, task)
        _atomic_json(batchfile, [{"id": batch_id, "targets": list(targets),
                                 "approved_at": None, "recheck_results": {}}])
        _atomic_json(journal, records)
        return batchfile, journal

    def test_cancel_idle_saved_cohort_after_restart_never_erases_original_wal(self):
        self.manager.configure(pair())
        before_records = {
            "confirmed.user": {"status": "ok", "at": "2026-11-09T01:00:00Z"},
            "uncertain.user": {
                "status": "review", "issue": "interrupted_action_uncertain",
                "click_intent": {
                    "batch_id": "saved-A", "task": "unfollow",
                    "phase": "relationship_control",
                    "requires_manual_review": True,
                },
            },
        }
        batch_a, journal_a = self.seed(
            A, "unfollow", "saved-A", before_records,
            ["confirmed.user", "uncertain.user", "untouched.user"])
        batch_b, journal_b = self.seed(
            B, "cancel", "saved-B",
            {"other.user": {"status": "review", "at": "2026-11-09T01:00:00Z"}},
            ["other.user", "another.user"])
        saved_a = journal_a.read_bytes()
        saved_b = batch_b.read_bytes(), journal_b.read_bytes()

        restarted = DualActionWorkspaces(
            DualChromeSessions(self.root / "browser"),
            self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(restarted.shutdown)
        restored = restarted.status(OWNER)
        self.assertTrue(restored["bindings_restored_from_disk"])
        self.assertFalse(restored["parallel_mutations_enabled"])
        self.assertEqual(restarted.workspaces[A]["robot"].owner, "",
                         "No Instagram worker should bind or start on reload.")
        result = restarted.cancel_batch_one(cancel())
        self.assertEqual(result["status"], "cancelled")
        self.assertEqual((result["recorded"], result["untouched"]), (2, 1))
        self.assertEqual((result["owner"], result["account"], result["task"]),
                         (OWNER, A, "unfollow"))
        batch = json.loads(batch_a.read_text("utf-8"))[0]
        self.assertEqual(batch["deferred_reason"], "owner_cancelled")
        self.assertFalse(batch["marked_reviewed"])
        self.assertTrue(batch["cancelled_by_owner_at"])
        self.assertIsNone(restarted.workspaces[A]["robot"].worker)
        self.assertEqual(journal_a.read_bytes(), saved_a,
                         "Cancelled cohort must never delete possible clicks.")
        self.assertEqual((batch_b.read_bytes(), journal_b.read_bytes()), saved_b,
                         "Cancelling A must not edit any data for B.")
        with self.assertRaisesRegex(ValueError, "changed"):
            restarted.cancel_batch_one(cancel())

    def test_wrong_account_task_batch_or_confirmation_mutates_nothing(self):
        self.manager.configure(pair())
        batch, journal = self.seed(
            A, "unfollow", "saved-A", {}, ["untouched.user"])
        original = batch.read_bytes(), journal.read_bytes()
        requests = [
            {**cancel(), "confirmation": "wrong"},
            {**cancel(), "batch_id": "wrong"},
            cancel(account=B),
            cancel(task="cancel"),
            cancel(account="ig_unknown_12345678"),
            {**cancel(), "owner": "u_someone_42"},
        ]
        for data in requests:
            with self.subTest(data=data), self.assertRaises(ValueError):
                self.manager.cancel_batch_one(data)
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), original)
        self.assertFalse(any(lane["robot"].worker
                             for lane in self.manager.workspaces.values()))

    def test_external_legacy_action_lease_blocks_idle_cancel_without_partial_archive(self):
        self.manager.configure(pair())
        batch, journal = self.seed(A, "unfollow", "saved-A", {}, ["untouched.user"])
        snapshot = batch.read_bytes()
        with ActionLease(self.collector.data_dir):
            with self.assertRaises(ActionSessionBusy):
                self.manager.cancel_batch_one(cancel())
        self.assertEqual(batch.read_bytes(), snapshot)
        self.assertEqual(journal.read_bytes(), b"{}")

    def test_parallel_running_a_cancel_does_not_stop_b_or_release_global_lease(self):
        self.manager.configure(pair(parallel=True))
        robot_a = self.manager.workspaces[A]["robot"]
        robot_b = self.manager.workspaces[B]["robot"]
        entered_a, entered_b, finish_b = (threading.Event() for _ in range(3))

        def run_a():
            entered_a.set()
            self.assertTrue(robot_a.stop_event.wait(5),
                            "Exact owner cancel should signal A to stop.")
            with robot_a.lock:
                robot_a._finish_owner_cancel_locked()

        def run_b():
            entered_b.set()
            finish_b.wait(5)

        robot_a._run = run_a
        robot_b._run = run_b
        try:
            self.manager.start_one(command(A, "alpha.one", "unfollow", "pending.a"))
            self.manager.start_one(command(B, "beta.two", "cancel", "pending.b"))
            self.assertTrue(entered_a.wait(5))
            self.assertTrue(entered_b.wait(5))
            batch_id = robot_a.active_batch_id
            with self.assertRaisesRegex(ValueError, "different task"):
                self.manager.cancel_batch_one(cancel(A, "cancel", batch_id))
            answer = self.manager.cancel_batch_one(cancel(A, "unfollow", batch_id))
            self.assertEqual(answer["status"], "cancelling")
            robot_a.worker.join(5)
            self.assertFalse(robot_a.worker.is_alive())
            self.assertTrue(robot_b.worker.is_alive(),
                            "The other Instagram action robot must continue.")
            self.assertFalse(robot_b.stop_event.is_set())
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.collector.data_dir).acquire()
            a_batch = robot_a._review_batches_file_for(
                OWNER, A, "unfollow")
            self.assertEqual(json.loads(a_batch.read_text("utf-8"))[0][
                "deferred_reason"], "owner_cancelled")
            self.assertEqual(robot_a.status, "cancelled")
            self.assertEqual(robot_b.status in ("starting", "running"), True)
        finally:
            finish_b.set()
            if robot_b.worker:
                robot_b.worker.join(5)
        ActionLease(self.collector.data_dir).acquire().release()


if __name__ == "__main__":
    unittest.main()
