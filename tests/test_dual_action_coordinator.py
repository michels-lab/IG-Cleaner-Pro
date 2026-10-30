"""Offline proof of legacy-safe TWO scoped mutators under one global OS lock.

NO browser launch, profile navigation, Instagram login, or relationship click.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dual_action_coordinator import SharedGlobalActionCohort
from robot_interlock import ActionLease, ActionSessionBusy, ScopedActionLease


class SharedGlobalActionCohortTests(unittest.TestCase):
    def test_two_distinct_scopes_share_global_and_first_release_cannot_unlock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            first = cohort.lease(root, "u_owner_42", "ig_first_12345")
            second = cohort.lease(root, "u_owner_42", "ig_second_12345")
            first.acquire()
            self.assertTrue(cohort.status()["legacy_global_lease_held"])
            with self.assertRaises(ActionSessionBusy):
                ActionLease(root).acquire()
            second.acquire()
            self.assertEqual(cohort.status()["active_scopes"], 2)
            with self.assertRaises(ActionSessionBusy):
                ScopedActionLease(root, "u_other_99", "ig_third_12345").acquire()
            first.release()
            self.assertTrue(cohort.status()["legacy_global_lease_held"])
            self.assertEqual(cohort.status()["active_scopes"], 1)
            with self.assertRaises(ActionSessionBusy):
                ActionLease(root).acquire()
            with self.assertRaises(ActionSessionBusy):
                cohort.close()
            second.release()
            self.assertFalse(cohort.status()["legacy_global_lease_held"])
            cohort.close()
            ActionLease(root).acquire().release()

    def test_duplicate_scope_same_or_other_owner_rejected_without_leak(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            first = cohort.lease(root, "ownerA", "account1").acquire()
            with self.assertRaises(ActionSessionBusy):
                cohort.lease(root, "ownerA", "account1").acquire()
            with self.assertRaises(ActionSessionBusy):
                first.acquire()
            with self.assertRaisesRegex(ActionSessionBusy, "same app owner"):
                cohort.lease(root, "ownerB", "account1").acquire()
            second = cohort.lease(root, "ownerA", "account2").acquire()
            with self.assertRaises(ActionSessionBusy):
                cohort.lease(root, "ownerA", "account3").acquire()
            self.assertEqual(cohort.status()["active_scopes"], 2)
            second.release()
            first.release()
            first.release()
            self.assertEqual(cohort.status()["active_scopes"], 0)
            # A different owner can claim the coordinator AFTER both jobs stop.
            later = cohort.lease(root, "ownerB", "account1").acquire()
            later.release()
            ActionLease(root).acquire().release()

    def test_second_scope_collision_never_releases_first_global_lease(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            first = cohort.lease(root, "ownerA", "first").acquire()
            busy = cohort.lease(root, "ownerA", "second")
            outside = ActionLease(root, lock_name=busy.workspace_lease.lock_name).acquire()
            try:
                with self.assertRaises(ActionSessionBusy):
                    busy.acquire()
                self.assertFalse(busy.acquired)
                self.assertEqual(cohort.status()["active_scopes"], 1)
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(root).acquire()
            finally:
                outside.release()
                first.release()
            ActionLease(root).acquire().release()

    def test_failed_first_scope_collision_rolls_back_global_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            scope = cohort.lease(root, "ownerA", "first")
            outside = ActionLease(root, lock_name=scope.workspace_lease.lock_name).acquire()
            try:
                with self.assertRaises(ActionSessionBusy):
                    scope.acquire()
                self.assertFalse(cohort.status()["legacy_global_lease_held"])
                self.assertEqual(cohort.status()["active_scopes"], 0)
                ActionLease(root).acquire().release()
            finally:
                outside.release()

    def test_wrong_root_and_invalid_configuration_are_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            with self.assertRaises(ValueError):
                cohort.lease(root / "different", "ownerA", "first")
            with self.assertRaises(ValueError):
                cohort.lease(root, "", "first")
            for value in (0, 1, 3, False, None):
                with self.assertRaises(ValueError):
                    SharedGlobalActionCohort(root, maximum_workers=value)
            self.assertFalse(cohort.status()["parallel_mutations_enabled"])

    def test_other_process_cannot_acquire_global_until_last_scope_exits(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cohort = SharedGlobalActionCohort(root)
            one = cohort.lease(root, "u_a_1", "ig_one").acquire()
            two = cohort.lease(root, "u_a_1", "ig_two").acquire()
            script = (
                "import sys;"
                "sys.path.insert(0,sys.argv[2]);"
                "from robot_interlock import ActionLease,ActionSessionBusy;"
                "root=sys.argv[1];"
                "exec('try:\\n ActionLease(root).acquire()\\nexcept ActionSessionBusy:\\n sys.exit(19)\\n')"
            )
            folder = str(Path(__file__).resolve().parents[1] / "tools")
            def probe():
                p = subprocess.run([sys.executable, "-c", script, str(root), folder],
                                   timeout=12, check=False)
                return p.returncode
            try:
                self.assertEqual(probe(), 19)
                one.release()
                self.assertEqual(probe(), 19)
            finally:
                two.release()
                one.release()
            self.assertEqual(probe(), 0)

    def test_crash_releases_cohort_global_and_two_scope_locks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = (
                "import sys,os;"
                "sys.path.insert(0,sys.argv[2]);"
                "from dual_action_coordinator import SharedGlobalActionCohort;"
                "c=SharedGlobalActionCohort(sys.argv[1]);"
                "c.lease(sys.argv[1],'owner','one').acquire();"
                "c.lease(sys.argv[1],'owner','two').acquire();"
                "os._exit(0)"
            )
            child = subprocess.run([sys.executable, "-c", script, str(root),
                str(Path(__file__).resolve().parents[1] / "tools")], timeout=12,
                check=False)
            self.assertEqual(child.returncode, 0)
            c = SharedGlobalActionCohort(root)
            first = c.lease(root, "owner", "one").acquire()
            second = c.lease(root, "owner", "two").acquire()
            second.release()
            first.release()


if __name__ == "__main__":
    unittest.main()
