"""Regression: an identity-blocked dual Chrome lane must never become verified from a late callback.

Offline only: no Instagram access, Chrome, profile cookies or account mutations.
"""
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from dual_chrome_sessions import DualChromeSessions
from dual_robot_lanes import DualRobotLanes

OWNER = "u_owner_42"
LEFT = "ig_first_1234567"
RIGHT = "ig_second_123456"
PAIR = {
    "owner": OWNER,
    "primary": {"account": LEFT, "expected_handle": "first_person"},
    "secondary": {"account": RIGHT, "expected_handle": "second_person"},
    "read_only_consent": True,
    "acknowledge_no_actions": True,
    "confirmation": "dual-robots:" + LEFT + ":" + RIGHT,
}


class DualLaneTerminalStatusTests(unittest.TestCase):
    @staticmethod
    def _wait_state(supervisor, account, expected):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            lanes = {row["account"]: row for row in supervisor.snapshot(OWNER)["lanes"]}
            if lanes[account]["state"] == expected:
                return lanes[account]
            time.sleep(0.01)
        raise AssertionError(f"Chrome lane {account} did not reach {expected}: {lanes[account]}")

    def test_wrong_identity_block_is_terminal_until_explicit_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            wrong_identity_seen = threading.Event()
            allow_late_result = threading.Event()
            late_result_sent = threading.Event()
            stop_left = threading.Event()
            attempts = []

            def runner(account, handle, folder, stopped):
                if account == RIGHT:
                    stopped.wait(4)
                    return
                attempts.append(account)
                if len(attempts) == 1:
                    supervisor._report(account, "blocked",
                                       "Wrong Instagram account detected in this Chrome lane.")
                    wrong_identity_seen.set()
                    self.assertTrue(allow_late_result.wait(3))
                    # This stale report used to overwrite blocked and set verified=True.
                    supervisor._report(account, "verified", "Late success", verified=True)
                    supervisor._report(account, "login", "Late login prompt")
                    late_result_sent.set()
                    return
                supervisor._report(account, "login", "Fresh manual login needed")
                supervisor._report(account, "verified", "Fresh login visibly verified", verified=True)
                stop_left.set()
                stopped.wait(4)

            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            try:
                supervisor.start_pair(dict(PAIR))
                self.assertTrue(wrong_identity_seen.wait(3))
                self.assertEqual(self._wait_state(supervisor, LEFT, "blocked")["verified"], False)
                allow_late_result.set()
                self.assertTrue(late_result_sent.wait(3))
                # The first worker must finish before a deliberate restart is accepted.
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    lanes = {x["account"]: x for x in supervisor.snapshot(OWNER)["lanes"]}
                    if not lanes[LEFT]["running"]:
                        break
                    time.sleep(0.01)
                self.assertFalse(lanes[LEFT]["running"])
                self.assertEqual(lanes[LEFT]["state"], "blocked")
                self.assertFalse(lanes[LEFT]["verified"])
                self.assertFalse(supervisor.snapshot(OWNER)["actions_enabled"])
                self.assertTrue(lanes[RIGHT]["running"],
                                "A blocked lane must not stop the sibling account.")
                supervisor.restart_one({
                    "owner": OWNER, "account": LEFT,
                    "confirmation": "dual-robot-restart:" + OWNER + ":" + LEFT,
                })
                self.assertTrue(stop_left.wait(3))
                fresh = self._wait_state(supervisor, LEFT, "verified")
                self.assertTrue(fresh["verified"],
                                "An explicitly restarted lane may verify its identity.")
                self.assertEqual(len(attempts), 2)
            finally:
                allow_late_result.set()
                supervisor.shutdown()


if __name__ == "__main__":
    unittest.main()
