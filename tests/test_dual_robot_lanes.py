"""Two live independent browser workers with exact owner/workspace isolation.

All tests are offline: they do NOT open Instagram or perform any account actions.
"""
import sys
import tempfile
import threading
import time
import unittest
import json
import urllib.error
import urllib.parse
import urllib.request
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

    def test_stop_one_then_restart_one_does_not_interrupt_other_lane(self):
        with tempfile.TemporaryDirectory() as temp:
            times = {}
            second_running = threading.Event()
            def runner(account, handle, folder, stopped):
                times[account] = times.get(account, 0) + 1
                if account == PAIR["secondary"]["account"]:
                    second_running.set()
                stopped.wait(3)
            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            first, second = PAIR["primary"]["account"], PAIR["secondary"]["account"]
            try:
                supervisor.start_pair(dict(PAIR))
                self.assertTrue(second_running.wait(3))
                with self.assertRaisesRegex(ValueError, "Confirm the exact"):
                    supervisor.stop_one({"owner": OWNER, "account": first})
                with self.assertRaisesRegex(ValueError, "another user's"):
                    supervisor.stop_one({"owner": "u_other_42", "account": first,
                                         "confirmation": "dual-robot-stop:u_other_42:" + first})
                supervisor.stop_one({"owner": OWNER, "account": first,
                                     "confirmation": "dual-robot-stop:" + OWNER + ":" + first})
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    lanes = {x["account"]: x for x in supervisor.snapshot(OWNER)["lanes"]}
                    if not lanes[first]["running"]:
                        break
                    time.sleep(0.01)
                self.assertFalse(lanes[first]["running"])
                self.assertTrue(lanes[second]["running"],
                                "Stopping first must not interrupt second.")
                with self.assertRaisesRegex(ValueError, "Confirm the exact"):
                    supervisor.restart_one({"owner": OWNER, "account": first})
                supervisor.restart_one({"owner": OWNER, "account": first,
                                        "confirmation": "dual-robot-restart:" + OWNER + ":" + first})
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline and times.get(first, 0) < 2:
                    time.sleep(0.01)
                self.assertEqual(times.get(first), 2)
                self.assertEqual(times.get(second), 1,
                                 "Never restart or duplicate other-account worker.")
                lanes = {x["account"]: x for x in supervisor.snapshot(OWNER)["lanes"]}
                self.assertTrue(lanes[second]["running"])
                self.assertFalse(supervisor.snapshot(OWNER)["actions_enabled"])
            finally:
                supervisor.shutdown()

    def test_cross_supervisor_same_chrome_profile_is_denied_without_double_start(self):
        # Two independent app controller instances must not attach to one
        # persistent Chrome profile, even in distinct OS worker threads.
        with tempfile.TemporaryDirectory() as temp:
            running = threading.Event()
            active = set()
            lock = threading.Lock()
            entered_second = []
            def first_runner(account, handle, folder, stopped):
                with lock:
                    active.add(account)
                    if len(active) == 2:
                        running.set()
                stopped.wait(3)
            first = DualRobotLanes(DualChromeSessions(Path(temp)), runner=first_runner)
            second = DualRobotLanes(
                DualChromeSessions(Path(temp)),
                runner=lambda *args: entered_second.append(args))
            try:
                first.start_pair(dict(PAIR))
                self.assertTrue(running.wait(3), "First supervisor owns both contexts.")
                second.start_pair(dict(PAIR))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    lanes = second.snapshot(OWNER)["lanes"]
                    if {lane["state"] for lane in lanes} == {"blocked"}:
                        break
                    time.sleep(0.01)
                self.assertEqual({lane["state"] for lane in lanes}, {"blocked"})
                self.assertEqual(entered_second, [], "No second Chrome attach on a busy profile.")
                self.assertTrue(all(not x["verified"] for x in lanes))
                self.assertTrue(all(x["running"] for x in first.snapshot(OWNER)["lanes"]))
            finally:
                second.shutdown()
                first.shutdown()

    def test_lease_released_on_stop_allows_explicit_new_run(self):
        with tempfile.TemporaryDirectory() as temp:
            started = threading.Event()
            first = DualRobotLanes(
                DualChromeSessions(Path(temp)),
                runner=lambda _a, _h, _p, stop: (started.set(), stop.wait(3)))
            second_seen = threading.Event()
            second = DualRobotLanes(
                DualChromeSessions(Path(temp)),
                runner=lambda _a, _h, _p, stop: (second_seen.set(), stop.wait(3)))
            try:
                first.start_pair(dict(PAIR))
                self.assertTrue(started.wait(3))
                first.shutdown()  # Does not delete the persistent login.
                self.assertFalse(any(x["running"] for x in first.snapshot(OWNER)["lanes"]))
                second.start_pair(dict(PAIR))
                self.assertTrue(second_seen.wait(3), "Stopped worker released its Chrome lease.")
                self.assertFalse(second.snapshot(OWNER)["actions_enabled"])
            finally:
                first.shutdown()
                second.shutdown()

    def test_stop_one_revokes_verified_immediately_and_ignores_late_browser_status(self):
        with tempfile.TemporaryDirectory() as temp:
            first_handle = PAIR["primary"]["account"]
            ready, release = threading.Event(), threading.Event()
            def runner(account, handle, folder, stopped):
                if account == first_handle:
                    supervisor._report(account, "verified", "Correct owner", verified=True)
                    ready.set()
                    release.wait(3)  # Emulate a slow browser shutdown callback.
                    supervisor._report(account, "verified", "Late browser result", verified=True)
                else:
                    stopped.wait(3)
            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            try:
                supervisor.start_pair(dict(PAIR))
                self.assertTrue(ready.wait(3))
                supervisor.stop_one({
                    "owner": OWNER, "account": first_handle,
                    "confirmation": "dual-robot-stop:" + OWNER + ":" + first_handle,
                })
                before = {x["account"]: x for x in supervisor.snapshot(OWNER)["lanes"]}
                self.assertEqual(before[first_handle]["state"], "stopping")
                self.assertFalse(before[first_handle]["verified"])
                release.set()
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline and any(
                        x["account"] == first_handle and x["running"]
                        for x in supervisor.snapshot(OWNER)["lanes"]):
                    time.sleep(0.01)
                after = {x["account"]: x for x in supervisor.snapshot(OWNER)["lanes"]}
                self.assertEqual(after[first_handle]["state"], "stopped")
                self.assertFalse(after[first_handle]["verified"])
                self.assertTrue(after[PAIR["secondary"]["account"]]["running"])
            finally:
                release.set()
                supervisor.shutdown()

    def test_playwright_error_details_cannot_leak_session_tokens_to_ui(self):
        with tempfile.TemporaryDirectory() as temp:
            leaked = "private_browser_path_token_sample"
            def runner(*_):
                raise RuntimeError(leaked)
            supervisor = DualRobotLanes(DualChromeSessions(Path(temp)), runner=runner)
            try:
                supervisor.start_pair(dict(PAIR))
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    lanes = supervisor.snapshot(OWNER)["lanes"]
                    if {x["state"] for x in lanes} == {"blocked"}:
                        break
                    time.sleep(0.01)
                self.assertEqual({x["state"] for x in lanes}, {"blocked"})
                self.assertTrue(all(leaked not in x["message"] for x in lanes))
                self.assertTrue(all(not x["verified"] for x in lanes))
            finally:
                supervisor.shutdown()

    def test_local_bridge_routes_exact_token_owner_and_individual_lane_commands(self):
        from profile_counts_bridge import Collector, build_server
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            server = build_server(Collector(base / "data", base / "browser"),
                                  "test-token", 0)
            server.dual_robot_lanes.runner = lambda account, handle, folder, stopped: stopped.wait(3)
            listener = threading.Thread(target=server.serve_forever, daemon=True)
            listener.start()
            origin = "http://127.0.0.1:" + str(server.server_port)
            def call(path, data=None, token="test-token"):
                payload = json.dumps(data).encode("utf-8") if data is not None else None
                req = urllib.request.Request(
                    origin + path, data=payload,
                    headers={"X-IGC-Bridge-Token": token,
                             "Origin": "null", "Content-Type": "application/json"},
                    method="POST" if data is not None else "GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    return json.load(resp)
            try:
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    call("/api/actions/dual-robots/status?owner=" + OWNER, token="wrong")
                self.assertEqual(rejected.exception.code, 403)
                initial = call("/api/actions/dual-robots/start", PAIR)
                self.assertFalse(initial["actions_enabled"])
                self.assertEqual(len(initial["lanes"]), 2)
                lookup = call("/api/actions/dual-robots/status?owner=" + OWNER)
                self.assertEqual(lookup["owner"], OWNER)
                self.assertEqual({x["account"] for x in lookup["lanes"]},
                                 {PAIR["primary"]["account"], PAIR["secondary"]["account"]})
                with self.assertRaises(urllib.error.HTTPError) as foreign:
                    call("/api/actions/dual-robots/status?owner=u_other_42")
                self.assertEqual(foreign.exception.code, 400)
                first = PAIR["primary"]["account"]
                stopped = call("/api/actions/dual-robots/stop-one", {
                    "owner": OWNER, "account": first,
                    "confirmation": "dual-robot-stop:" + OWNER + ":" + first,
                })
                self.assertFalse(stopped["actions_enabled"])
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    status = call("/api/actions/dual-robots/status?owner=" + OWNER)
                    rows = {x["account"]: x for x in status["lanes"]}
                    if not rows[first]["running"]:
                        break
                    time.sleep(0.01)
                self.assertFalse(rows[first]["running"])
                restarted = call("/api/actions/dual-robots/restart-one", {
                    "owner": OWNER, "account": first,
                    "confirmation": "dual-robot-restart:" + OWNER + ":" + first,
                })
                self.assertFalse(restarted["actions_enabled"])
                self.assertTrue(any(x["running"] for x in restarted["lanes"]))
                call("/api/actions/dual-robots/stop", {
                    "owner": OWNER,
                    "confirmation": "dual-robots-stop:" + OWNER,
                })
            finally:
                server.dual_robot_lanes.shutdown()
                server.shutdown()
                server.server_close()
                listener.join(timeout=4)

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
