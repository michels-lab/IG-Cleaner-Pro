"""Two-account SUPERVISOR acceptance without any Instagram Playwright body.

The Windows bridge does not pass offline_test_runner, so production is still
serialized. This tests actual DualActionWorkspaces.configure/start_one/pause_one/
status/shutdown with two ActionRobot threads, real kernel WAL locks and two
different ChromeLease directories. It never opens Instagram or clicks Follow.
"""
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dual_action_workspaces import DualActionWorkspaces
from dual_chrome_sessions import DualChromeSessions
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server
from robot_interlock import ActionLease, ActionSessionBusy

OWNER = "u_owner_42"
A, B = "ig_account_123456", "ig_account_789012"


def configuration():
    return {"owner": OWNER,
            "primary": {"account": A, "expected_handle": "alpha.one"},
            "secondary": {"account": B, "expected_handle": "beta.two"},
            "read_only_consent": True, "acknowledge_serial_actions": True,
            "confirmation": "dual-action-workspaces:" + A + ":" + B}


def request(account, handle, target):
    return {"owner": OWNER, "account": account,
            "action": {"owner": OWNER, "account": account, "expected_handle": handle,
                       "task": "cancel", "targets": [target], "batch_size": 1,
                       "protected": [], "gap_seconds": 10, "rest_minutes": 0,
                       "confirmation": "cancel:1"},
            "confirmation": "action-workspace-start:" + OWNER + ":" + account + ":cancel"}


def pause(account):
    return {"owner": OWNER, "account": account,
            "confirmation": "action-workspace-pause:" + OWNER + ":" + account}


class OfflineDualManagerIntegrationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.collector = Collector(root / "counts", root / "chrome-legacy")
        self.legacy = ActionRobot(self.collector, self.collector.data_dir,
                                  self.collector.session_dir)
        self.sessions = DualChromeSessions(root / "dual-chrome")
        self.entered = {A: threading.Event(), B: threading.Event()}
        self.release = {A: threading.Event(), B: threading.Event()}
        self.calls = []

        def offline_runner(account, stop):
            self.calls.append(account)
            self.entered[account].set()
            # Production browser code is never invoked, even when stopping.
            while not self.release[account].is_set() and not stop.is_set():
                stop.wait(0.02)

        self.manager = DualActionWorkspaces(
            self.sessions, self.collector, self.collector.data_dir, self.legacy,
            offline_test_runner=offline_runner)
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        for e in self.release.values():
            e.set()
        self.manager.shutdown()

    def test_manager_admits_two_accounts_but_still_reports_no_parallel_clicks(self):
        self.manager.configure(configuration())
        self.manager.start_one(request(A, "alpha.one", "a.target"))
        self.assertTrue(self.entered[A].wait(5))
        self.manager.start_one(request(B, "beta.two", "b.target"))
        self.assertTrue(self.entered[B].wait(5))
        status = self.manager.status(OWNER)
        self.assertEqual({x["account"] for x in status["lanes"]}, {A, B})
        self.assertEqual(sum(x["running"] for x in status["lanes"]), 2)
        self.assertFalse(status["parallel_mutations_enabled"],
                         "Offline supervisor is NOT a user-visible mutating mode.")
        self.assertIn("offline_two_worker", status["mode"])
        self.assertEqual(self.manager._offline_cohort.status()["active_scopes"], 2)
        self.assertNotEqual(self.manager.workspaces[A]["chrome"],
                            self.manager.workspaces[B]["chrome"])
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()
        self.assertEqual(self.manager.workspaces[A]["robot"]._journal(), {})
        self.assertEqual(self.manager.workspaces[B]["robot"]._journal(), {})
        self.assertEqual(self.calls.count(A), 1)
        self.assertEqual(self.calls.count(B), 1)

    def test_pausing_A_does_not_pause_B_or_release_old_global_mutex(self):
        self.manager.configure(configuration())
        self.manager.start_one(request(A, "alpha.one", "a.target"))
        self.manager.start_one(request(B, "beta.two", "b.target"))
        self.assertTrue(self.entered[A].wait(5))
        self.assertTrue(self.entered[B].wait(5))
        self.manager.pause_one(pause(A))
        self.manager.workspaces[A]["robot"].worker.join(5)
        self.assertFalse(self.manager.workspaces[A]["robot"].worker.is_alive())
        self.assertTrue(self.manager.workspaces[B]["robot"].worker.is_alive())
        self.assertFalse(self.manager.workspaces[B]["robot"].stop_event.is_set())
        self.assertEqual(self.manager._offline_cohort.status()["active_scopes"], 1)
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()
        self.manager.pause_one(pause(B))
        self.manager.workspaces[B]["robot"].worker.join(5)
        self.assertFalse(self.manager.workspaces[B]["robot"].worker.is_alive())
        self.assertEqual(self.manager._offline_cohort.status()["active_scopes"], 0)
        ActionLease(self.collector.data_dir).acquire().release()

    def test_rejects_protected_B_without_stopping_or_rebinding_A(self):
        self.manager.configure(configuration())
        a = self.manager.workspaces[A]["robot"]
        b = self.manager.workspaces[B]["robot"]
        self.manager.start_one(request(A, "alpha.one", "a.target"))
        self.assertTrue(self.entered[A].wait(5))
        guard = b._protection_file_for(OWNER, B)
        _atomic_json(guard, ["protected.name"])
        before = guard.read_bytes()
        with self.assertRaisesRegex(ValueError, "protected"):
            self.manager.start_one(request(B, "beta.two", "protected.name"))
        self.assertEqual(guard.read_bytes(), before)
        self.assertEqual(a.account, A)
        self.assertFalse(b.worker)
        self.assertTrue(a.worker.is_alive())
        self.assertEqual(self.manager._offline_cohort.status()["active_scopes"], 1)
        with self.assertRaises(ActionSessionBusy):
            ActionLease(self.collector.data_dir).acquire()

    def test_bad_owner_and_duplicate_A_do_not_disrupt_existing_job(self):
        self.manager.configure(configuration())
        self.manager.start_one(request(A, "alpha.one", "a.target"))
        self.assertTrue(self.entered[A].wait(5))
        with self.assertRaises(ValueError):
            self.manager.start_one({**request(B, "beta.two", "b.target"),
                                   "owner": "u_different_99"})
        with self.assertRaisesRegex(ValueError, "already (active|running)"):
            self.manager.start_one(request(A, "alpha.one", "a.target"))
        with self.assertRaisesRegex(ValueError, "Stop all active"):
            self.manager.configure(configuration())
        self.assertEqual(self.manager._offline_cohort.status()["active_scopes"], 1)
        self.assertEqual(self.calls, [A])

    def test_production_server_never_injects_offline_coordinator(self):
        # This test explicitly verifies the native bridge does not use the
        # injection-only constructor; running Windows still serializes.
        server = build_server(self.collector, "x" * 32)
        try:
            prod = server.dual_action_workspaces
            self.assertIsNotNone(prod)
            self.assertIsNone(prod._offline_test_runner)
            self.assertIsNone(prod._offline_cohort)
            self.assertFalse(prod.status(OWNER)["parallel_mutations_enabled"])
            self.assertEqual(prod.status(OWNER)["mode"],
                             "independent_chrome_sessions_serialized_actions")
        finally:
            server.server_close()

    def test_invalid_offline_test_runner_fails_closed(self):
        with self.assertRaises(TypeError):
            DualActionWorkspaces(self.sessions, self.collector,
                                 self.collector.data_dir, self.legacy,
                                 offline_test_runner="run Instagram in Chrome")


if __name__ == "__main__":
    unittest.main()
