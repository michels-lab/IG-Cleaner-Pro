"""GRANADA P0: separate public/Developer processes cannot race relationship clicks."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from robot_interlock import ActionLease, ActionSessionBusy
from profile_actions import ActionRobot
from profile_counts_bridge import Collector


class JournalInterlockTests(unittest.TestCase):
    def test_cross_process_lock_blocks_then_recovers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "canonical-action-journal"
            python_code = (
                "import sys;from pathlib import Path;"
                "sys.path.insert(0,sys.argv[2]);"
                "from robot_interlock import ActionLease,ActionSessionBusy;"
                "lease=ActionLease(Path(sys.argv[1])).acquire();"
                "print('CHILD_LOCK_ACQUIRED',flush=True);"
                "input();lease.release()"
            )
            tools = str(Path(__file__).resolve().parents[1] / "tools")
            with subprocess.Popen(
                [sys.executable, "-u", "-c", python_code, str(root), tools],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True,
            ) as child:
                self.assertEqual(child.stdout.readline().strip(), "CHILD_LOCK_ACQUIRED")
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(root).acquire()
                child.stdin.write("\n")
                child.stdin.flush()
                self.assertEqual(child.wait(timeout=6), 0, child.stderr.read())
            lease = ActionLease(root).acquire()
            lease.release()

    def test_crashed_or_exited_process_does_not_leave_stale_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            tools = str(Path(__file__).resolve().parents[1] / "tools")
            code = (
                "import sys,os;from pathlib import Path;"
                "sys.path.insert(0,sys.argv[2]);"
                "from robot_interlock import ActionLease;"
                "ActionLease(Path(sys.argv[1])).acquire();"
                "os._exit(0)"
            )
            child = subprocess.run(
                [sys.executable, "-c", code, directory, tools],
                timeout=8, check=False,
            )
            self.assertEqual(child.returncode, 0)
            lease = ActionLease(Path(directory)).acquire()
            lease.release()

    def test_worker_owns_lease_until_entire_job_finishes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            canonical = root / "canonical"
            public = ActionRobot(Collector(root/"public-data", root/"public-chrome"),
                                 canonical, root/"public-chrome")
            developer = ActionRobot(Collector(root/"dev-data", root/"dev-chrome"),
                                    canonical, root/"dev-chrome")
            entered = threading.Event()
            stop = threading.Event()
            def fake_run():
                entered.set()
                self.assertTrue(stop.wait(timeout=5))
            public._run = fake_run
            developer._run = lambda: None
            def payload(target, account="same-account"):
                return {
                    "owner":"same-owner", "account":account,
                    "expected_handle":"real.owner", "task":"cancel",
                    "targets":[target], "batch_size":1,
                    "protected":[], "gap_seconds":10, "rest_minutes":0,
                    "confirmation":"cancel:1",
                }
            try:
                public.start(payload("first.test"))
                self.assertTrue(entered.wait(timeout=3))
                with self.assertRaisesRegex(ActionSessionBusy, "Another public/Developer"):
                    developer.start(payload("second.test", "other-account"))
                self.assertEqual(developer.owner, "", "Denied Developer must not rebind its account")
                self.assertTrue(canonical.joinpath(
                    ".instagram-action-admission.lock").exists(),
                    "The lockfile is retained without resetting the action journal.")
            finally:
                stop.set()
                if public.worker:
                    public.worker.join(timeout=5)
            self.assertFalse(public.worker.is_alive())
            # Different owner scope cannot replace the old canonical batch, but
            # the shared lease must have been released.
            lease = ActionLease(canonical).acquire()
            lease.release()

    def test_rejected_batch_does_not_keep_exclusive_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            collector = Collector(root/"results", root/"chrome")
            robot = ActionRobot(collector, root/"canonical", collector.session_dir)
            with self.assertRaisesRegex(ValueError, "explicitly approved"):
                robot.start({
                    "owner":"owner", "account":"account", "expected_handle":"owner",
                    "task":"cancel", "targets":["candidate"],
                    "batch_size":1, "gap_seconds":10, "rest_minutes":0,
                    "confirmation":"wrong",
                })
            lease = ActionLease(root/"canonical").acquire()
            lease.release()


if __name__ == "__main__":
    unittest.main()
