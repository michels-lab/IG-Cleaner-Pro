"""GRANADA: cross-process WAL protection while approving saved action batches.

No network, Chrome or live Instagram actions. The same on-disk owner/task
journal is exercised through the production ActionRobot and dual controller.
"""
import json
import sys
import tempfile
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
A = "ig_account_123456"
B = "ig_account_789012"


class BatchApprovalLeaseTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.collector = Collector(self.root / "data", self.root / "browser")
        self.robot = ActionRobot(self.collector, self.collector.data_dir,
                                 self.collector.session_dir)

    def seed(self, *, account=A, task="unfollow", batch_id="saved-wave",
             status="already_not_following", uncertain=False):
        journal = self.robot._base_for(OWNER, account, task)
        batch = self.robot._review_batches_file_for(OWNER, account, task)
        target = "review.target"
        entry = {"status": status, "at": "2026-11-09T13:00:00Z",
                 "message": "Current state verified without another click"}
        if uncertain:
            entry = {"status": "review", "issue": "interrupted_action_uncertain",
                     "at": "2026-11-09T13:00:00Z",
                     "click_intent": {"phase": "relationship_control"}}
        _atomic_json(journal, {target: entry})
        _atomic_json(batch, [{"id": batch_id, "targets": [target],
                              "approved_at": None, "recheck_results": {}}])
        return batch, journal

    def request(self, account=A, task="unfollow", batch_id="saved-wave"):
        return {"owner": OWNER, "account": account, "task": task,
                "batch_id": batch_id, "confirmation": "reviewed:" + batch_id}

    def test_other_public_or_developer_process_holds_global_lease(self):
        batch, journal = self.seed()
        saved = batch.read_bytes(), journal.read_bytes()
        legacy = ActionLease(self.collector.data_dir).acquire()
        try:
            with self.assertRaises(ActionSessionBusy):
                self.robot.approve_batch(self.request())
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), saved,
                             "A blocked batch approval must not modify ANY saved evidence.")
        finally:
            legacy.release()
        response = self.robot.approve_batch(self.request())
        self.assertEqual(response["approved_usernames"], ["review.target"])
        self.assertEqual(response["unresolved_usernames"], [])
        stored = json.loads(batch.read_text("utf-8"))[0]
        self.assertTrue(stored["approved_at"])
        self.assertEqual(stored["approved_usernames"], ["review.target"])
        self.assertEqual(journal.read_bytes(), saved[1])
        with self.assertRaisesRegex(ValueError, "changed"):
            self.robot.approve_batch(self.request())

    def test_owner_and_task_isolation_wrong_scope_never_approves(self):
        batch, journal = self.seed()
        saved = batch.read_bytes(), journal.read_bytes()
        for payload in [
            {**self.request(), "owner": "u_other_42"},
            self.request(account=B),
            self.request(task="cancel"),
            {**self.request(), "confirmation": "not-approved"},
            self.request(batch_id="wrong-wave"),
        ]:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                self.robot.approve_batch(payload)
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), saved)

    def test_possible_click_remains_unresolved_and_wal_is_immutable(self):
        batch, journal = self.seed(uncertain=True)
        old_journal = journal.read_bytes()
        answer = self.robot.approve_batch(self.request())
        self.assertEqual(answer["approved_usernames"], [])
        self.assertEqual(answer["unresolved_usernames"], ["review.target"])
        self.assertEqual(journal.read_bytes(), old_journal)
        self.assertTrue(json.loads(batch.read_text("utf-8"))[0]["approved_at"],
                        "Completing a review must not relabel uncertain as success.")

    def test_two_account_panel_cannot_approve_under_other_app_lease(self):
        sessions = DualChromeSessions(self.root / "action-browser")
        manager = DualActionWorkspaces(sessions, self.collector,
                                       self.collector.data_dir, self.robot)
        self.addCleanup(manager.shutdown)
        manager.configure({
            "owner": OWNER,
            "primary": {"account": A, "expected_handle": "first.person"},
            "secondary": {"account": B, "expected_handle": "second.person"},
            "read_only_consent": True,
            "acknowledge_serial_actions": True,
            "confirmation": "dual-action-workspaces:" + A + ":" + B,
        })
        batch, journal = self.seed()
        original = batch.read_bytes(), journal.read_bytes()
        command = {"owner": OWNER, "account": A, "task": "unfollow",
                   "batch_id": "saved-wave",
                   "confirmation": "action-workspace-approve:" + OWNER + ":" +
                                   A + ":unfollow:saved-wave"}
        other_process = ActionLease(self.collector.data_dir).acquire()
        try:
            with self.assertRaises(ActionSessionBusy):
                manager.approve_one(command)
            self.assertEqual((batch.read_bytes(), journal.read_bytes()), original)
        finally:
            other_process.release()
        result = manager.approve_one(command)
        self.assertEqual(result["owner"], OWNER)
        self.assertEqual(result["account"], A)
        self.assertEqual(result["approved_usernames"], ["review.target"])
        self.assertEqual(journal.read_bytes(), original[1])


if __name__ == "__main__":
    unittest.main()
