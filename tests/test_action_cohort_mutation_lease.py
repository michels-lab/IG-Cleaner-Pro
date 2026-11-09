"""GRANADA: saved cohort resize/archive never races a different Windows app.

The production methods must acquire the same OS-level action lease used for
actual relationship clicks. This fixture has no Chrome or Instagram network.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector
from robot_interlock import ActionLease, ScopedActionLease, ActionSessionBusy

OWNER = "u_owner_42"
A = "ig_account_123456"
B = "ig_account_789012"
TARGETS = ["done.one", "uncertain.two", "protected.three",
           "fresh.four", "fresh.five"]


class CohortMutationLeaseTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "data", self.root / "chrome")
        self.robot = ActionRobot(self.collector, self.collector.data_dir,
                                 self.collector.session_dir)

    def seed(self, account=A, task="unfollow", batch="wave-40"):
        batches = self.robot._review_batches_file_for(OWNER, account, task)
        journal = self.robot._base_for(OWNER, account, task)
        protected = self.robot._protection_file_for(OWNER, account)
        _atomic_json(batches, [{
            "id": batch, "targets": list(TARGETS),
            "approved_at": None, "recheck_results": {},
        }])
        _atomic_json(journal, {
            "done.one": {"status": "ok",
                         "click_intent": {"phase": "relationship_control",
                                          "outcome_recorded": True}},
            "uncertain.two": {
                "status": "review", "issue": "interrupted_action_uncertain",
                "click_intent": {"phase": "relationship_control"},
            },
        })
        _atomic_json(protected, ["protected.three"])
        return (batches, journal, protected)

    def req(self, task="unfollow", batch="wave-40", account=A, action="replan"):
        data = {"owner": OWNER, "account": account, "task": task,
                "batch_id": batch}
        if action == "replan":
            data.update(desired_batch_size=1,
                        confirmation="replan-size:" + batch + ":1")
        elif action == "aside":
            data.update(desired_batch_size=40,
                        confirmation="new-batch:" + batch + ":40")
        elif action == "protected":
            data["confirmation"] = "defer-protected:" + batch
        return data

    def assert_busy_preserves_all(self, method, request, scope=A):
        files = self.robot._review_batches_file_for(OWNER, scope, request["task"]), \
                self.robot._base_for(OWNER, scope, request["task"]), \
                self.robot._protection_file_for(OWNER, scope)
        previous = [(p, p.read_bytes()) for p in files]
        # Simulate the other installed Public/Developer or action worker.
        lease = ActionLease(self.collector.data_dir).acquire()
        try:
            with self.assertRaises(ActionSessionBusy):
                method(request)
            for path, blob in previous:
                self.assertEqual(path.read_bytes(), blob,
                    "A concurrent app must not mutate batch, click WAL or protection.")
        finally:
            lease.release()
        return previous

    def test_replan_original_40_to_1_rejects_cross_process_and_keeps_uncertain(self):
        batches, journal, protection = self.seed()
        original_wal = journal.read_bytes()
        params = self.req()
        self.assert_busy_preserves_all(self.robot.replan_incomplete_batch, params)
        result = self.robot.replan_incomplete_batch(params)
        self.assertEqual(result["active_size"], 1)
        self.assertEqual(result["reusable_after_active"], 1)
        batch = self.robot.batch_review(params)["batch"]
        self.assertEqual(batch["targets"], ["fresh.four"])
        self.assertEqual(batch["carryover_targets"], ["fresh.five"])
        self.assertEqual(batch["original_targets"], TARGETS)
        self.assertFalse(batch.get("approved_at"))
        self.assertEqual(journal.read_bytes(), original_wal)
        self.assertEqual(batch["action_results"]["fresh.four"]["status"], "pending")
        # Both malformed and uncertain prior WAL must never enter a new wave.
        self.assertNotIn("uncertain.two", batch["targets"])
        self.assertNotIn("done.one", batch["targets"])
        self.assertNotIn("protected.three", batch["targets"])
        with self.assertRaisesRegex(ValueError, "already matches"):
            self.robot.replan_incomplete_batch(params)
        lease = ActionLease(self.collector.data_dir).acquire()
        lease.release()  # A denied resize cannot leave the OS lock held.

    def test_owner_set_aside_is_blocked_by_other_app_and_preserves_click_wal(self):
        batches, journal, protection = self.seed(task="cancel")
        params = self.req(task="cancel", action="aside")
        wal = journal.read_bytes()
        self.assert_busy_preserves_all(self.robot.set_aside_incomplete_batch, params)
        result = self.robot.set_aside_incomplete_batch(params)
        self.assertEqual(result["status"], "saved_cohort_set_aside_for_new_batch")
        self.assertFalse(result["marked_reviewed"])
        self.assertEqual(journal.read_bytes(), wal)
        old = self.robot._review_batches(OWNER, A, "cancel")[0]
        self.assertEqual(old["targets"], TARGETS)
        self.assertEqual(old["deferred_reason"], "owner_new_batch_explicit")
        self.assertNotIn("uncertain.two", result["reusable_usernames"])
        self.assertIn("fresh.five", result["reusable_usernames"])
        self.assertIsNone(self.robot.batch_review(params)["batch"])

    def test_protected_collision_deferral_is_lease_guarded(self):
        batches, journal, protection = self.seed()
        params = self.req(action="protected")
        wal = journal.read_bytes()
        self.assert_busy_preserves_all(self.robot.defer_protected_batch, params)
        result = self.robot.defer_protected_batch(params)
        self.assertEqual(result["protected_usernames"], ["protected.three"])
        self.assertEqual(result["approved_usernames"], [])
        self.assertEqual(journal.read_bytes(), wal)
        self.assertTrue(self.robot._review_batches(OWNER, A, "unfollow")[0]["deferred_at"])
        # Another process can enter after the method releases the exact lock.
        ScopedActionLease(self.collector.data_dir, OWNER, B).acquire().release()

    def test_invalid_exact_scope_never_corrupts_other_accounts(self):
        a_files = self.seed()
        b_files = self.seed(account=B, batch="other-wave")
        before = [(f, f.read_bytes()) for f in (*a_files, *b_files)]
        for method, payload in (
            (self.robot.replan_incomplete_batch,
             {**self.req(), "confirmation": "replan-size:wrong:1"}),
            (self.robot.set_aside_incomplete_batch,
             {**self.req(action="aside"), "account": "wrong"}),
            (self.robot.defer_protected_batch,
             {**self.req(action="protected"), "batch_id": "other-wave"}),
        ):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                method(payload)
        for file, value in before:
            self.assertEqual(file.read_bytes(), value)
        ActionLease(self.collector.data_dir).acquire().release()


if __name__ == "__main__":
    unittest.main()
