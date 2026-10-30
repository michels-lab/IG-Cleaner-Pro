"""Granada: cross-process account admission and rejected-start state integrity.

Offline tests never start real Chrome or contact Instagram.
"""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from robot_interlock import ActionLease, ScopedActionLease, ActionSessionBusy
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector


class ScopedAdmissionTests(unittest.TestCase):
    def test_scoped_lock_preserves_legacy_global_barrier(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            lease = ScopedActionLease(path, "owner-one", "ig_alpha").acquire()
            try:
                self.assertTrue((path / ".instagram-action-admission.lock").exists())
                scope_names = [p.name for p in path.iterdir()
                               if p.name.startswith(".instagram-action-")
                               and p.name != ".instagram-action-admission.lock"]
                self.assertEqual(len(scope_names), 1)
                self.assertNotIn("owner-one", scope_names[0])
                self.assertNotIn("ig_alpha", scope_names[0])
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(path).acquire()
                with self.assertRaises(ActionSessionBusy):
                    ScopedActionLease(path, "owner-two", "ig_beta").acquire()
                with self.assertRaises(ActionSessionBusy):
                    lease.acquire()
            finally:
                lease.release()
            with _lease_cm(path, "owner-two", "ig_beta"):
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(path).acquire()

    def test_lock_acquisition_failure_releases_global_even_if_scoped_busy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Explicitly reserve only the hashed named lease to emulate an
            # independent future process already owning that account.
            candidate = ScopedActionLease(root, "owner-one", "account_1")
            named = ActionLease(root, lock_name=candidate.workspace_lease.lock_name).acquire()
            try:
                with self.assertRaises(ActionSessionBusy):
                    candidate.acquire()
                # A failed account-specific admission MUST release legacy
                # global lease so unrelated work is not stuck.
                available = ActionLease(root).acquire()
                available.release()
            finally:
                named.release()

    def test_same_scope_is_stable_and_two_scopes_have_distinct_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            one = ScopedActionLease(temp, "owner", "account_a")
            again = ScopedActionLease(temp, "owner", "account_a")
            other = ScopedActionLease(temp, "owner", "account_b")
            self.assertEqual(one.workspace_lease.lock_name, again.workspace_lease.lock_name)
            self.assertNotEqual(one.workspace_lease.lock_name, other.workspace_lease.lock_name)
            self.assertNotEqual(one.workspace_lease.lock_name, ".instagram-action-admission.lock")
            for invalid in ("", None):
                with self.assertRaises(ValueError):
                    ScopedActionLease(temp, invalid, "account_a")
            for invalid in ("../malicious", "/evil", chr(92) + "bad"):
                with self.assertRaises(ValueError):
                    ActionLease(temp, lock_name=".instagram-action-" + invalid + ".lock")

    def test_crashed_scoped_worker_leaves_no_stale_global_lock(self):
        with tempfile.TemporaryDirectory() as temp:
            tools_dir = str(Path(__file__).resolve().parents[1] / "tools")
            script = (
                "import sys,os;"
                "sys.path.insert(0,sys.argv[2]);"
                "from robot_interlock import ScopedActionLease;"
                "ScopedActionLease(sys.argv[1],'owner','account').acquire();"
                "os._exit(0)"
            )
            child = subprocess.run(
                [sys.executable, "-c", script, temp, tools_dir],
                timeout=8, check=False)
            self.assertEqual(child.returncode, 0)
            lease = ScopedActionLease(temp, "owner", "account").acquire()
            lease.release()


class _lease_cm:
    def __init__(self, root, owner, account):
        self.lease = ScopedActionLease(root, owner, account)
    def __enter__(self):
        return self.lease.acquire()
    def __exit__(self, *args):
        self.lease.release()


class RejectedStartScopeTests(unittest.TestCase):
    def test_denied_replay_does_not_rebind_owner_or_lose_old_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            counts = Collector(root / "counts", root / "chrome")
            robot = ActionRobot(counts, root / "canonical", counts.session_dir)
            robot.owner, robot.account, robot.handle, robot.task = (
                "previous-owner", "previous-account", "previous.handle", "cancel")
            robot.targets = ["old.profile"]
            _atomic_json(robot._base_for("new-owner", "new-account", "unfollow"), {
                "already.done": {"status": "already_not_following", "message": "Observed"}
            })
            payload = {
                "owner": "new-owner", "account": "new-account",
                "expected_handle": "new.owner",
                "task": "unfollow", "targets": ["already.done"],
                "followers_evidence": True, "protected": [],
                "batch_size": 1, "gap_seconds": 10, "rest_minutes": 0,
                "confirmation": "unfollow:1",
            }
            with self.assertRaises(ValueError):
                robot.start(payload)
            self.assertEqual((robot.owner, robot.account, robot.handle, robot.task),
                             ("previous-owner", "previous-account", "previous.handle", "cancel"))
            self.assertEqual(robot.targets, ["old.profile"])
            self.assertFalse((root / "canonical" / "instagram-actions-new-batch.json").exists())
            # Denied start cannot strand the global OS lock.
            available = ActionLease(root / "canonical").acquire()
            available.release()

    def test_protected_mismatch_preserves_active_owner_and_never_changes_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            counts = Collector(root / "counts", root / "chrome")
            robot = ActionRobot(counts, root / "canonical", counts.session_dir)
            robot.owner, robot.account, robot.handle, robot.task = (
                "owner", "first-account", "first.handle", "cancel")
            robot.targets = ["first.target"]
            path = robot._protection_file_for("owner", "second-account")
            _atomic_json(path, ["protected.user"])
            before = path.read_bytes()
            payload = {
                "owner": "owner", "account": "second-account",
                "expected_handle": "second.handle",
                "task": "cancel", "targets": ["protected.user"],
                "protected": [], "batch_size": 1,
                "gap_seconds": 10, "rest_minutes": 0,
                "confirmation": "cancel:1",
            }
            with self.assertRaisesRegex(ValueError, "protected"):
                robot.start(payload)
            self.assertEqual(robot.account, "first-account")
            self.assertEqual(robot.targets, ["first.target"])
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(robot.worker)

    def test_worker_holds_scoped_and_global_locks_until_completed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            counts = Collector(root / "counts", root / "chrome")
            robot = ActionRobot(counts, root / "canonical", counts.session_dir)
            entered, finish = threading.Event(), threading.Event()
            def controlled_worker():
                entered.set()
                self.assertTrue(finish.wait(4))
            robot._run = controlled_worker
            payload = {
                "owner": "test-owner", "account": "ig-one",
                "expected_handle": "owner.name", "task": "cancel",
                "targets": ["new.user"], "protected": [], "batch_size": 1,
                "gap_seconds": 10, "rest_minutes": 0, "confirmation": "cancel:1",
            }
            try:
                result = robot.start(payload)
                self.assertTrue(entered.wait(3))
                self.assertEqual(result["account"], "ig-one")
                with self.assertRaises(ActionSessionBusy):
                    ScopedActionLease(root / "canonical", "test-owner", "ig-one").acquire()
                with self.assertRaises(ActionSessionBusy):
                    ScopedActionLease(root / "canonical", "test-owner", "ig-two").acquire()
            finally:
                finish.set()
                if robot.worker: robot.worker.join(5)
            self.assertFalse(robot.worker.is_alive())
            lease = ScopedActionLease(root / "canonical", "test-owner", "ig-two").acquire()
            lease.release()


if __name__ == "__main__":
    unittest.main()
