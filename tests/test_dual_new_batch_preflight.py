"""Owner-scoped new batch local WAL preflight: never contacts Instagram.

A successful preflight reports untouched local history ONLY. ActionRobot.start
still independently checks live login, current relationship, protection and
canonical owner WAL before a click.
"""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dual_chrome_sessions import DualChromeSessions
from dual_action_workspaces import DualActionWorkspaces
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server

OWNER = "u_owner_42"
A = "ig_account_123456"
B = "ig_account_789012"


def configuration():
    return {"owner": OWNER,
            "primary": {"account": A, "expected_handle": "alpha.one"},
            "secondary": {"account": B, "expected_handle": "beta.two"},
            "read_only_consent": True, "acknowledge_serial_actions": True,
            "confirmation": "dual-action-workspaces:" + A + ":" + B}


def selection(account=A, task="unfollow", handle="alpha.one", targets=None):
    if targets is None:
        targets = ["new.one", "new.two"]
    return {"owner": OWNER, "account": account,
            "expected_handle": handle, "task": task, "targets": targets,
            "confirmation": "action-workspace-preflight:" + OWNER + ":" + account +
                            ":" + task}


class DualNewBatchPreflightTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.collector = Collector(self.root / "counts", self.root / "legacy-chrome")
        self.legacy = ActionRobot(self.collector, self.collector.data_dir,
                                  self.collector.session_dir)
        self.sessions = DualChromeSessions(self.root / "new-chrome")
        self.manager = DualActionWorkspaces(self.sessions, self.collector,
                                            self.collector.data_dir, self.legacy)
        self.addCleanup(self.manager.shutdown)
        self.manager.configure(configuration())

    def test_new_cohort_is_read_only_not_live_consent(self):
        before = set(self.collector.data_dir.glob("*"))
        result = self.manager.preflight_new_one(selection())
        self.assertEqual(result["owner"], OWNER)
        self.assertEqual(result["account"], A)
        self.assertEqual(result["expected_handle"], "alpha.one")
        self.assertEqual(result["evidence_counts"]["untouched"], 2)
        self.assertTrue(result["offline_untouched_only"])
        self.assertFalse(result["actions_enabled"])
        self.assertFalse(result["can_launch_parallel_unfollow"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["targets"][0]["offline_evidence"], "untouched")
        self.assertEqual(set(self.collector.data_dir.glob("*")), before)
        self.assertFalse(self.manager.workspaces[A]["robot"].worker)
        self.assertFalse(self.manager.workspaces[B]["robot"].worker)

    def test_protected_visited_and_uncertain_evidence_are_not_eligible(self):
        robot = self.manager.workspaces[A]["robot"]
        _atomic_json(robot._protection_file_for(OWNER, A), ["guarded.user"])
        _atomic_json(robot._target_visits_file_for(OWNER, A, "unfollow"),
                     {"visited.user": {"at": "2026-10-30T10:00:00Z"}})
        _atomic_json(robot._base_for(OWNER, A, "unfollow"),
                     {"uncertain.user": {"status": "review",
                       "issue": "interrupted_action_uncertain",
                       "click_intent": {"phase": "unfollow_menu",
                          "task": "unfollow", "batch_id": "old",
                          "written_at": "2026-10-30T12:00:00Z"}}})
        before = robot._base_for(OWNER, A, "unfollow").read_bytes()
        result = self.manager.preflight_new_one(selection(
            targets=["new.one", "guarded.user", "visited.user", "uncertain.user"]))
        labels = {r["username"]:r["offline_evidence"] for r in result["targets"]}
        self.assertEqual(labels, {
            "new.one": "untouched", "guarded.user": "protected",
            "visited.user": "previously_inspected", "uncertain.user": "uncertain_action"})
        self.assertFalse(result["offline_untouched_only"])
        self.assertEqual(robot._base_for(OWNER, A, "unfollow").read_bytes(), before)

    def test_unresolved_saved_cohort_blocks_even_new_names(self):
        robot = self.manager.workspaces[A]["robot"]
        path = robot._review_batches_file_for(OWNER, A, "cancel")
        _atomic_json(path, [{"id": "wave-old", "targets": ["already.reviewed"],
                             "approved_at": None, "recheck_results": {}}])
        before = path.read_bytes()
        result = self.manager.preflight_new_one(selection(
            task="cancel", targets=["never.opened"]))
        self.assertTrue(result["unresolved_saved_cohort"])
        self.assertEqual(result["saved_cohort_id"], "wave-old")
        self.assertEqual(result["targets"][0]["offline_evidence"], "pending_cohort")
        self.assertFalse(result["offline_untouched_only"])
        self.assertEqual(path.read_bytes(), before)

    def test_second_account_cannot_inherit_first_account_journal(self):
        robot = self.manager.workspaces[A]["robot"]
        _atomic_json(robot._base_for(OWNER, A, "unfollow"),
                     {"scoped.user": {"status": "ok", "at": "2026-10-30T10:00:00Z"}})
        first = self.manager.preflight_new_one(selection(targets=["scoped.user"]))
        second = self.manager.preflight_new_one(selection(
            account=B, handle="beta.two", targets=["scoped.user"]))
        self.assertFalse(first["offline_untouched_only"])
        self.assertTrue(second["offline_untouched_only"])
        self.assertEqual(second["account"], B)
        self.assertFalse(second["actions_enabled"])

    def test_wrong_login_owner_task_confirmation_duplicates_and_malformed_users_fail(self):
        baseline = selection()
        changes = [
            {"owner": "u_other_99"}, {"account": B},
            {"expected_handle": "beta.two"}, {"task": "audit"},
            {"confirmation": "wrong"}, {"targets": []},
            {"targets": ["duplicate.user", "duplicate.user"]},
            {"targets": ["@prefix.user"]}, {"targets": ["BAD.UPPER"]},
            {"targets": ["x" * 50]}, {"targets": [1]},
            {"targets": ["x"] * 1001},
        ]
        for change in changes:
            with self.subTest(change=repr(change)[:65]), self.assertRaises(ValueError):
                self.manager.preflight_new_one({**baseline, **change})
        self.assertIsNone(self.manager.workspaces[A]["robot"].worker)

    def test_active_action_worker_blocks_stale_new_cohort_inspection(self):
        import threading
        robot = self.manager.workspaces[A]["robot"]
        entered = threading.Event()
        finish = threading.Event()
        robot._run = lambda: (entered.set(), finish.wait(6))
        command = {"owner": OWNER, "account": A,
                   "action": {"owner": OWNER, "account": A,
                              "expected_handle": "alpha.one",
                              "task": "cancel", "targets": ["running.user"],
                              "batch_size": 1, "protected": [], "gap_seconds": 10,
                              "rest_minutes": 0, "confirmation": "cancel:1"},
                   "confirmation": "action-workspace-start:" + OWNER + ":" + A + ":cancel"}
        try:
            self.manager.start_one(command)
            self.assertTrue(entered.wait(4))
            with self.assertRaisesRegex(ValueError, "Pause"):
                self.manager.preflight_new_one(selection())
        finally:
            finish.set()
            robot.worker.join(6)

    def test_developer_mode_does_not_expose_mutating_new_batch_preflight(self):
        server = build_server(self.collector, "k" * 32, developer_mode=True)
        try:
            self.assertIsNone(server.dual_action_workspaces)
        finally:
            server.server_close()


if __name__ == "__main__":
    unittest.main()
