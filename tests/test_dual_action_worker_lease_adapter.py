"""GRANADA: real ActionRobot start/stop under shared legacy-safe admission.

Fakes only the Instagram browser worker body. Everything BEFORE that body
runs through actual ActionRobot.start(), exact canonical WAL admission,
ChromeLaneLease, owner scope and kernel OS file locks. No network or clicks.
"""
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from chrome_lane_interlock import ChromeLaneLease
from dual_action_coordinator import SharedGlobalActionCohort
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector
from robot_interlock import ActionLease, ActionSessionBusy, ScopedActionLease

OWNER = "u_owner_42"
LEFT, RIGHT = "ig_account_123456", "ig_account_789012"


def command(account, handle, target, *, owner=OWNER):
    return {"owner": owner, "account": account, "expected_handle": handle,
            "task": "cancel", "targets": [target], "batch_size": 1,
            "protected": [], "gap_seconds": 10, "rest_minutes": 0,
            "confirmation": "cancel:1"}


class DualActionRobotLeaseAdapterTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "counts", self.root / "legacy-chrome")
        self.journal = self.collector.data_dir
        self.cohort = SharedGlobalActionCohort(self.journal)
        self.left = ActionRobot(self.collector, self.journal,
                                self.root / "chrome-left",
                                lease_factory=self.cohort.lease)
        self.right = ActionRobot(self.collector, self.journal,
                                 self.root / "chrome-right",
                                 lease_factory=self.cohort.lease)

    def _wait_workers(self):
        for robot in (self.left, self.right):
            robot.stop_event.set()
            if robot.worker:
                robot.worker.join(10)
                self.assertFalse(robot.worker.is_alive(),
                                 "No kernel lease may remain held after test workers exit.")

    def test_actual_two_ActionRobot_start_are_independent_but_legacy_global_stays_busy(self):
        a_started, b_started = threading.Event(), threading.Event()
        a_done, b_done = threading.Event(), threading.Event()
        self.left._run = lambda: (a_started.set(), a_done.wait(12))
        self.right._run = lambda: (b_started.set(), b_done.wait(12))
        try:
            left_response = self.left.start(command(LEFT, "alpha.one", "first.target"))
            self.assertTrue(a_started.wait(5))
            right_response = self.right.start(command(RIGHT, "beta.two", "second.target"))
            self.assertTrue(b_started.wait(5))
            self.assertEqual(left_response["account"], LEFT)
            self.assertEqual(right_response["account"], RIGHT)
            self.assertEqual(self.cohort.status()["active_scopes"], 2)
            self.assertTrue(self.cohort.status()["legacy_global_lease_held"])
            self.assertFalse(self.cohort.status()["parallel_mutations_enabled"],
                             "Internal tests MUST NOT enable user-facing parallel clicks.")
            self.assertNotEqual(self.left.session_dir.resolve(), self.right.session_dir.resolve())
            self.assertNotEqual(self.left._base(), self.right._base())
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.journal).acquire()
            with self.assertRaises(ActionSessionBusy):
                ScopedActionLease(self.journal, OWNER, "ig_third_12345").acquire()
            # An actual old installed worker (default factory) must also fail
            # before it creates its new job or changes its bound identity.
            legacy = ActionRobot(self.collector, self.journal,
                                 self.root / "legacy-worker")
            with self.assertRaises(ActionSessionBusy):
                legacy.start(command("ig_legacy_12345", "legacy.person", "legacy.target"))
            self.assertFalse(legacy.worker)
            self.assertEqual(legacy.owner, "")
            a_done.set()
            self.left.worker.join(10)
            self.assertFalse(self.left.worker.is_alive())
            self.assertTrue(self.right.worker.is_alive())
            self.assertEqual(self.cohort.status()["active_scopes"], 1)
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.journal).acquire()
            b_done.set()
            self.right.worker.join(10)
            self.assertEqual(self.cohort.status()["active_scopes"], 0)
            ActionLease(self.journal).acquire().release()
            self.assertEqual(self.left._journal(), {})
            self.assertEqual(self.right._journal(), {})
            self.assertEqual(self.left.account, LEFT)
            self.assertEqual(self.right.account, RIGHT)
        finally:
            a_done.set()
            b_done.set()
            self._wait_workers()

    def test_second_owner_denied_without_mutating_sibling_state_or_premature_unlock(self):
        begin, finish = threading.Event(), threading.Event()
        self.left._run = lambda: (begin.set(), finish.wait(12))
        try:
            self.left.start(command(LEFT, "alpha.one", "first.target"))
            self.assertTrue(begin.wait(5))
            before = self.left.snapshot()
            with self.assertRaisesRegex(ActionSessionBusy, "same app owner"):
                self.right.start(command(RIGHT, "beta.two", "other.target",
                                         owner="u_different_99"))
            self.assertFalse(self.right.worker)
            self.assertEqual(self.right.account, "")
            self.assertEqual(self.left.snapshot()["account"], before["account"])
            self.assertEqual(self.cohort.status()["active_scopes"], 1)
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.journal).acquire()
            finish.set()
            self.left.worker.join(10)
            self.assertFalse(self.left.worker.is_alive())
            self.assertEqual(self.cohort.status()["active_scopes"], 0)
        finally:
            finish.set()
            self._wait_workers()

    def test_protected_second_cohort_rejection_cannot_release_live_first(self):
        begin, finish = threading.Event(), threading.Event()
        self.left._run = lambda: (begin.set(), finish.wait(12))
        try:
            self.left.start(command(LEFT, "alpha.one", "first.target"))
            self.assertTrue(begin.wait(5))
            protection = self.right._protection_file_for(OWNER, RIGHT)
            _atomic_json(protection, ["protected.user"])
            original = protection.read_bytes()
            with self.assertRaisesRegex(ValueError, "protected"):
                self.right.start(command(RIGHT, "beta.two", "protected.user"))
            self.assertEqual(protection.read_bytes(), original)
            self.assertFalse(self.right.worker)
            self.assertEqual(self.cohort.status()["active_scopes"], 1)
            with self.assertRaises(ActionSessionBusy):
                ActionLease(self.journal).acquire()
        finally:
            finish.set()
            self._wait_workers()

    def test_busy_second_chrome_fails_before_worker_and_preserves_first(self):
        begin, finish = threading.Event(), threading.Event()
        called = []
        self.left._run = lambda: (begin.set(), finish.wait(12))
        self.right._run = lambda: called.append("RELATIONSHIP CLICK NOT ALLOWED")
        try:
            self.left.start(command(LEFT, "alpha.one", "first.target"))
            self.assertTrue(begin.wait(5))
            with ChromeLaneLease(self.right.session_dir):
                reply = self.right.start(command(RIGHT, "beta.two", "second.target"))
                self.assertEqual(reply["account"], RIGHT)
                self.right.worker.join(10)
                self.assertFalse(self.right.worker.is_alive())
                self.assertEqual(self.right.snapshot()["status"], "blocked")
                self.assertEqual(called, [])
                self.assertEqual(self.cohort.status()["active_scopes"], 1)
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(self.journal).acquire()
            finish.set()
            self.left.worker.join(10)
            self.assertEqual(self.cohort.status()["active_scopes"], 0)
        finally:
            finish.set()
            self._wait_workers()

    def test_default_lease_factory_is_legacy_and_invalid_factory_rejected(self):
        with self.assertRaises(TypeError):
            ActionRobot(self.collector, self.journal, self.root / "invalid",
                        lease_factory="not-a-function")
        standard = ActionRobot(self.collector, self.journal, self.root / "standard")
        first, done = threading.Event(), threading.Event()
        standard._run = lambda: (first.set(), done.wait(10))
        try:
            standard.start(command(LEFT, "alpha.one", "first.target"))
            self.assertTrue(first.wait(5))
            with self.assertRaises(ActionSessionBusy):
                self.right.start(command(RIGHT, "beta.two", "other.target"))
            self.assertEqual(self.cohort.status()["active_scopes"], 0)
        finally:
            done.set()
            if standard.worker:
                standard.worker.join(10)


if __name__ == "__main__":
    unittest.main()
