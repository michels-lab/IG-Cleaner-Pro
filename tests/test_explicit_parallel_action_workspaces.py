"""GRANADA: real production supervisor two-action opt-in, offline-safe contract.

These tests instantiate the actual production DualActionWorkspaces constructor,
NOT the offline_test_runner adapter. Only each Playwright _run method is replaced
by deterministic local events after configuration. Therefore the actual start,
owner consent, WAL, protected records, global+scope kernel admission, ChromeLane
reservation and independently running threads are all executed.
"""
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from chrome_lane_interlock import ChromeLaneLease
from dual_chrome_sessions import DualChromeSessions
from dual_action_workspaces import DualActionWorkspaces
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server
from robot_interlock import ActionLease, ActionSessionBusy

OWNER = "u_owner_42"
A, B = "ig_account_123456", "ig_account_789012"


def config(*, parallel=True):
    return {
        "owner": OWNER,
        "primary": {"account": A, "expected_handle": "alpha.one"},
        "secondary": {"account": B, "expected_handle": "beta.two"},
        "read_only_consent": True,
        "acknowledge_parallel_actions": bool(parallel),
        "acknowledge_serial_actions": not parallel,
        "parallel_actions_consent": bool(parallel),
        "confirmation": ("dual-action-workspaces-parallel:" if parallel
                         else "dual-action-workspaces:") + A + ":" + B,
    }


def command(account, handle, target, *, task="cancel", parallel=True):
    action = {
        "owner": OWNER, "account": account, "expected_handle": handle,
        "task": task, "targets": [target], "batch_size": 1, "protected": [],
        "gap_seconds": 15, "rest_minutes": 0,
        "confirmation": task + ":1",
    }
    if task == "unfollow":
        action["followers_evidence"] = True
    result = {
        "owner": OWNER, "account": account, "action": action,
        "confirmation": "action-workspace-start:" + OWNER + ":" + account + ":" + task,
    }
    if parallel:
        result["parallel_action_confirmation"] = (
            "parallel-action-workspace-start:" + OWNER + ":" + account + ":" + task)
    return result


class ExplicitParallelProductionContract(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "data", self.root / "legacy-chrome")
        self.legacy = ActionRobot(
            self.collector, self.collector.data_dir, self.collector.session_dir)
        self.sessions = DualChromeSessions(self.root / "separate-windows")
        self.manager = DualActionWorkspaces(
            self.sessions, self.collector, self.collector.data_dir, self.legacy)
        self.entered = {A: threading.Event(), B: threading.Event()}
        self.finish = {A: threading.Event(), B: threading.Event()}
        self.addCleanup(self.cleanup_workers)

    def cleanup_workers(self):
        for ev in self.finish.values():
            ev.set()
        self.manager.shutdown()

    def configure_with_fake_chrome_body(self, *, parallel=True):
        result = self.manager.configure(config(parallel=parallel))
        for account in (A, B):
            def worker(name=account):
                self.entered[name].set()
                self.finish[name].wait(10)
            self.manager.workspaces[account]["robot"]._run = worker
        return result

    def test_no_parallel_without_exact_optin_and_secondary_account_consent(self):
        bad = [
            {**config(), "parallel_actions_consent": False},
            {**config(), "parallel_actions_consent": "true"},
            {**config(), "acknowledge_parallel_actions": False},
            {**config(), "acknowledge_serial_actions": True},
            {**config(), "confirmation": "dual-action-workspaces:" + A + ":" + B},
            {**config(), "read_only_consent": False},
            {**config(), "secondary":
                {"account": A, "expected_handle": "beta.two"}},
            {**config(), "secondary":
                {"account": B, "expected_handle": "alpha.one"}},
        ]
        for item in bad:
            with self.subTest(item=repr(item)[:85]), self.assertRaises(ValueError):
                self.manager.configure(item)
        self.assertIsNone(self.manager.owner)
        self.assertFalse(self.manager.status(OWNER)["parallel_mutations_enabled"])
        self.assertFalse(self.collector.data_dir.exists())

    def test_default_serial_remains_serial_after_new_parallel_feature(self):
        config_state = self.configure_with_fake_chrome_body(parallel=False)
        self.assertFalse(config_state["parallel_mutations_enabled"])
        self.assertIn("serialized", config_state["mode"])
        self.manager.start_one(command(A, "alpha.one", "first.person", parallel=False))
        self.assertTrue(self.entered[A].wait(5))
        with self.assertRaisesRegex(ValueError, "Only one relationship-changing"):
            self.manager.start_one(command(B, "beta.two", "second.person", parallel=False))
        self.assertFalse(self.manager.workspaces[B]["robot"].worker)
        self.finish[A].set()
        self.manager.workspaces[A]["robot"].worker.join(5)
        self.assertFalse(self.manager.workspaces[A]["robot"].worker.is_alive())
        self.assertFalse(self.manager.status(OWNER)["parallel_mutations_enabled"])

    def test_two_real_production_workers_execute_under_one_legacy_global_lock(self):
        state = self.configure_with_fake_chrome_body()
        self.assertTrue(state["parallel_mutations_enabled"])
        self.assertIn("explicit_owner_authorized", state["mode"])
        self.assertIsNone(self.manager._offline_cohort,
                          "Only actual production code path may be exercised.")
        self.assertIsNotNone(self.manager._live_cohort)
        left = self.manager.start_one(command(A, "alpha.one", "first.person",
                                              task="unfollow"))
        right = self.manager.start_one(command(B, "beta.two", "second.person",
                                               task="cancel"))
        self.assertTrue(self.entered[A].wait(5))
        self.assertTrue(self.entered[B].wait(5))
        self.assertEqual(left["account"], A)
        self.assertEqual(right["account"], B)
        state = self.manager.status(OWNER)
        self.assertEqual(sum(x["running"] for x in state["lanes"]), 2)
        self.assertTrue(state["parallel_mutations_enabled"])
        self.assertTrue(state["legacy_global_lease_held"])
        self.assertEqual(self.manager._live_cohort.status()["active_scopes"], 2)
        left_robot = self.manager.workspaces[A]["robot"]
        right_robot = self.manager.workspaces[B]["robot"]
        self.assertNotEqual(left_robot.session_dir, right_robot.session_dir)
        self.assertNotEqual(left_robot._base(), right_robot._base())
        self.assertEqual(left_robot._journal(), {})
        self.assertEqual(right_robot._journal(), {})
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()
        # Simulate stopping exactly one user account. The second continues.
        self.manager.pause_one({
            "owner": OWNER, "account": A,
            "confirmation": "action-workspace-pause:" + OWNER + ":" + A})
        self.finish[A].set()
        left_robot.worker.join(5)
        self.assertFalse(left_robot.worker.is_alive())
        self.assertTrue(right_robot.worker.is_alive())
        self.assertFalse(right_robot.stop_event.is_set())
        self.assertEqual(self.manager._live_cohort.status()["active_scopes"], 1)
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()
        self.finish[B].set()
        right_robot.worker.join(5)
        self.assertEqual(self.manager._live_cohort.status()["active_scopes"], 0)
        self.assertFalse(self.manager.status(OWNER)["legacy_global_lease_held"])
        ActionLease(self.collector.data_dir).acquire().release()

    def test_additional_per_task_consent_is_mandatory_even_after_optin(self):
        self.configure_with_fake_chrome_body()
        valid = command(A, "alpha.one", "first.person")
        for value in (None, "", "parallel-action-workspace-start:" + OWNER + ":" + B + ":cancel",
                      "parallel-action-workspace-start:" + OWNER + ":" + A + ":unfollow"):
            bad = dict(valid)
            if value is None:
                bad.pop("parallel_action_confirmation")
            else:
                bad["parallel_action_confirmation"] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "concurrent-action"):
                self.manager.start_one(bad)
        self.assertFalse(self.manager.workspaces[A]["robot"].worker)
        self.assertFalse(self.collector.data_dir.exists())
        reply = self.manager.start_one(valid)
        self.assertEqual(reply["account"], A)
        self.finish[A].set()
        self.manager.workspaces[A]["robot"].worker.join(5)

    def test_second_account_still_needs_fresh_wal_protection_and_correct_handle(self):
        self.configure_with_fake_chrome_body()
        self.manager.start_one(command(A, "alpha.one", "first.person"))
        self.assertTrue(self.entered[A].wait(5))
        right = self.manager.workspaces[B]["robot"]
        protected = right._protection_file_for(OWNER, B)
        _atomic_json(protected, ["guarded.person"])
        before = protected.read_bytes()
        with self.assertRaisesRegex(ValueError, "protected"):
            self.manager.start_one(command(B, "beta.two", "guarded.person"))
        self.assertEqual(protected.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "must match"):
            self.manager.start_one(command(B, "wrong.handle", "another.person"))
        self.assertFalse(right.worker)
        self.assertEqual(right.owner, "")
        self.assertTrue(self.manager.workspaces[A]["robot"].worker.is_alive())
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()
        self.finish[A].set()

    def test_busy_Chrome_profile_B_blocks_only_B_and_preserves_A(self):
        self.configure_with_fake_chrome_body()
        self.manager.start_one(command(A, "alpha.one", "first.person"))
        self.assertTrue(self.entered[A].wait(5))
        folder = self.sessions.directory(OWNER, B)
        with ChromeLaneLease(folder):
            self.manager.start_one(command(B, "beta.two", "second.person"))
            self.manager.workspaces[B]["robot"].worker.join(5)
            self.assertEqual(self.manager.workspaces[B]["robot"].snapshot()["status"], "blocked")
            self.assertFalse(self.entered[B].is_set())
            self.assertTrue(self.manager.workspaces[A]["robot"].worker.is_alive())
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.collector.data_dir).acquire()
        self.finish[A].set()

    def test_preflight_B_can_run_while_A_active_without_touching_A_journal(self):
        self.configure_with_fake_chrome_body()
        self.manager.start_one(command(A, "alpha.one", "first.person"))
        self.assertTrue(self.entered[A].wait(5))
        robot = self.manager.workspaces[A]["robot"]
        before = robot._review_batches_file_for(OWNER, A, "cancel").read_bytes()
        p = self.manager.preflight_new_one({
            "owner": OWNER, "account": B, "expected_handle": "beta.two",
            "task": "cancel", "targets": ["untouched.person"],
            "confirmation": "action-workspace-preflight:" + OWNER + ":" + B + ":cancel",
        })
        self.assertTrue(p["read_only"])
        self.assertTrue(p["offline_untouched_only"])
        self.assertFalse(p["actions_enabled"])
        self.assertEqual(robot._review_batches_file_for(OWNER, A, "cancel").read_bytes(), before)
        with self.assertRaisesRegex(ValueError, "Pause"):
            self.manager.preflight_new_one({
                "owner": OWNER, "account": A, "expected_handle": "alpha.one",
                "task": "cancel", "targets": ["another.person"],
                "confirmation": "action-workspace-preflight:" + OWNER + ":" + A + ":cancel",
            })
        self.finish[A].set()

    def test_reconfiguring_mode_or_swapping_accounts_requires_both_workers_stopped(self):
        self.configure_with_fake_chrome_body()
        self.manager.start_one(command(A, "alpha.one", "first.person"))
        self.assertTrue(self.entered[A].wait(5))
        for changed in (config(parallel=False), config(parallel=True)):
            with self.assertRaisesRegex(ValueError, "Stop all active"):
                self.manager.configure(changed)
        self.finish[A].set()
        self.manager.workspaces[A]["robot"].worker.join(5)
        new = self.manager.configure(config(parallel=False))
        self.assertFalse(new["parallel_mutations_enabled"])
        self.assertIsNone(self.manager._live_cohort)

    def test_native_server_defaults_to_serial_until_exact_owner_optin(self):
        server = build_server(self.collector, "t" * 32)
        try:
            manager = server.dual_action_workspaces
            self.assertFalse(manager._parallel_enabled)
            self.assertIsNone(manager._offline_cohort)
            self.assertIsNone(manager._live_cohort)
            self.assertFalse(manager.status(OWNER)["parallel_mutations_enabled"])
            manager.configure(config(parallel=True))
            self.assertTrue(manager.status(OWNER)["parallel_mutations_enabled"])
            self.assertFalse(manager.status(OWNER)["legacy_global_lease_held"])
        finally:
            server.server_close()


if __name__ == "__main__":
    unittest.main()
