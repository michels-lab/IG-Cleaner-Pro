"""Two live independent browser workers with exact owner/workspace isolation.

All tests are offline: they do NOT open Instagram or perform any account actions.
"""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from dual_chrome_sessions import DualChromeSessions
from dual_robot_lanes import DualRobotLanes

OWNER = "u_owner_42"
PAIR = {
    "owner": OWNER,
    "primary": {"account": "ig_first_1234567", "expected_handle": "first_person"},
    "secondary": {"account": "ig_second_123456", "expected_handle": "second_person"},
    "read_only_consent": True,
    "acknowledge_no_actions": True,
    "confirmation": "dual-robots:ig_first_1234567:ig_second_123456",
}


class DualRobotLaneTests(unittest.TestCase):
    def test_both_workers_run_simultaneously_with_different_browser_directories(self):
        with tempfile.TemporaryDirectory() as temp:
            entered = set()
            paths = {}
            mutex = threading.Lock()
            both = threading.Event()

            def runner(account, handle, folder, stopped):
                with mutex:
                    entered.add(account)
                    paths[account] = folder
                    if len(entered) == 2:
                        both.set()
                self.assertTrue(both.wait(3), "The two robots must run at the same time.")
                supervisor._report(account, "verified", "Verified exact owner", verified=True)
                stopped.wait(3)

            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            try:
                result = supervisor.start_pair(dict(PAIR))
                self.assertTrue(result["two_lanes"])
                self.assertFalse(result["actions_enabled"], "No Instagram changes in identity-only mode.")
                self.assertTrue(both.wait(3))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    state = supervisor.snapshot(OWNER)
                    if {x["state"] for x in state["lanes"]} == {"verified"}:
                        break
                    time.sleep(0.01)
                self.assertEqual({x["state"] for x in state["lanes"]}, {"verified"})
                self.assertEqual({x["expected_handle"] for x in state["lanes"]},
                                 {"first_person", "second_person"})
                self.assertEqual(len(set(paths.values())), 2)
                for account, path in paths.items():
                    self.assertEqual(path, supervisor.sessions.directory(OWNER, account))
                with self.assertRaisesRegex(ValueError, "previous supervised"):
                    supervisor.start_pair(dict(PAIR))
                with self.assertRaisesRegex(ValueError, "another app owner's"):
                    supervisor.snapshot("u_other_42")
                with self.assertRaisesRegex(ValueError, "Cannot stop another"):
                    supervisor.stop_pair({
                        "owner": "u_other_42",
                        "confirmation": "dual-robots-stop:u_other_42",
                    })
            finally:
                supervisor.stop_pair({
                    "owner": OWNER,
                    "confirmation": "dual-robots-stop:" + OWNER,
                })
                supervisor.shutdown()
            self.assertEqual({x["state"] for x in supervisor.snapshot(OWNER)["lanes"]},
                             {"stopped"})

    def test_invalid_or_unconfirmed_pair_cannot_launch_any_worker(self):
        with tempfile.TemporaryDirectory() as temp:
            calls = []
            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)),
                                        runner=lambda *args: calls.append(args))
            invalid = [
                {"owner": "other"},
                {"secondary": PAIR["primary"]},
                {"read_only_consent": False},
                {"acknowledge_no_actions": False},
                {"confirmation": ""},
                {"primary": {"account": "../oops", "expected_handle": "first_person"}},
                {"secondary": {"account": "ig_another_1234", "expected_handle": "first_person"}},
            ]
            for changes in invalid:
                with self.subTest(changes=changes), self.assertRaises(ValueError):
                    supervisor.start_pair({**PAIR, **changes})
            self.assertEqual(calls, [])
            self.assertFalse(supervisor.lanes)

    def test_one_worker_failure_does_not_falsely_verify_other(self):
        with tempfile.TemporaryDirectory() as temp:
            ready = threading.Event()

            def runner(account, handle, folder, stopped):
                if account == PAIR["secondary"]["account"]:
                    raise RuntimeError("Chrome profile in use")
                ready.set()
                stopped.wait(3)

            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            try:
                supervisor.start_pair(dict(PAIR))
                self.assertTrue(ready.wait(3))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    state = supervisor.snapshot(OWNER)
                    if any(x["state"] == "blocked" for x in state["lanes"]):
                        break
                    time.sleep(0.01)
                self.assertTrue(any(x["state"] == "blocked" for x in state["lanes"]))
                self.assertFalse(any(x["verified"] for x in state["lanes"]))
                self.assertFalse(state["actions_enabled"])
            finally:
                supervisor.shutdown()

    def test_stop_requires_exact_owner_consent_and_is_independent_of_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)),
                                        runner=lambda a,h,p,stopped: stopped.wait(3))
            with self.assertRaises(ValueError):
                supervisor.stop_pair({"owner": OWNER})
            supervisor.start_pair(dict(PAIR))
            with self.assertRaises(ValueError):
                supervisor.stop_pair({"owner": OWNER, "confirmation": "dual-robots-stop:other"})
            supervisor.stop_pair({"owner": OWNER, "confirmation": "dual-robots-stop:" + OWNER})
            supervisor.shutdown()
            self.assertEqual({x["state"] for x in supervisor.snapshot(OWNER)["lanes"]},
                             {"stopped"})


if __name__ == "__main__":
    unittest.main()
