"""Offline two-account action workspace and Chrome-exclusivity regressions.

No Instagram login, external requests or relationship clicks.
"""
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from chrome_lane_interlock import ChromeLaneLease
from dual_action_workspaces import DualActionWorkspaces
from dual_chrome_sessions import DualChromeSessions
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server

OWNER = "u_owner_42"
A, B = "ig_account_123456", "ig_account_789012"


def config():
    return {
        "owner": OWNER, "primary": {"account": A, "expected_handle": "first.person"},
        "secondary": {"account": B, "expected_handle": "second.person"},
        "read_only_consent": True, "acknowledge_serial_actions": True,
        "confirmation": "dual-action-workspaces:" + A + ":" + B,
    }


def action(account=A, handle="first.person", target="fresh.account", task="cancel"):
    return {
        "owner": OWNER, "account": account, "expected_handle": handle,
        "task": task, "targets": [target], "batch_size": 1, "protected": [],
        "gap_seconds": 10, "rest_minutes": 0,
        "confirmation": task + ":1",
        **({"followers_evidence": True} if task == "unfollow" else {}),
    }


def command(account=A, handle="first.person", task="cancel", target="fresh.account"):
    return {
        "owner": OWNER, "account": account,
        "action": action(account, handle, target, task),
        "confirmation": "action-workspace-start:" + OWNER + ":" + account + ":" + task,
    }


class IsolatedWorkspaceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "data", self.root / "legacy-chrome")
        self.legacy = ActionRobot(self.collector, self.collector.data_dir,
                                  self.collector.session_dir)
        self.sessions = DualChromeSessions(self.root / "browser")
        self.manager = DualActionWorkspaces(
            self.sessions, self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(self.manager.shutdown)

    def test_two_accounts_have_unique_persistent_chrome_and_mutable_state(self):
        result = self.manager.configure(config())
        self.assertEqual(result["owner"], OWNER)
        self.assertFalse(result["parallel_mutations_enabled"])
        self.assertTrue(result["two_workspaces"])
        self.assertEqual({x["account"] for x in result["lanes"]}, {A, B})
        first = self.manager.workspaces[A]
        second = self.manager.workspaces[B]
        self.assertNotEqual(first["chrome"], second["chrome"])
        self.assertNotEqual(first["robot"], second["robot"])
        self.assertEqual(first["robot"].data_dir, second["robot"].data_dir)
        self.assertEqual(first["robot"].session_dir, self.sessions.directory(OWNER, A))
        self.assertEqual(second["robot"].session_dir, self.sessions.directory(OWNER, B))
        self.assertFalse(self.collector.data_dir.exists())
        self.assertFalse(self.sessions.root.exists(),
                         "Configuring workspaces must not open Chrome or create login data.")

    def test_wrong_owner_handles_accounts_or_consent_can_never_rebind(self):
        c = config()
        wrong = [
            {"owner": "attacker"}, {"confirmation": "not-approved"},
            {"acknowledge_serial_actions": False},
            {"read_only_consent": False},
            {"secondary": {"account": A, "expected_handle": "other"}},
            {"secondary": {"account": B, "expected_handle": "first.person"}},
        ]
        for change in wrong:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.manager.configure({**c, **change})
        self.assertIsNone(self.manager.owner)
        self.manager.configure(c)
        with self.assertRaisesRegex(ValueError, "another owner"):
            self.manager.status("u_other_42")
        with self.assertRaises(ValueError):
            self.manager.configure({**c, "owner": "u_other_42"})
        with self.assertRaisesRegex(ValueError, "exact"):
            self.manager.start_one({**command(), "confirmation": "wrong"})
        with self.assertRaisesRegex(ValueError, "must match"):
            self.manager.start_one({**command(), "action":
                {**action(), "expected_handle": "second.person"}})
        with self.assertRaisesRegex(ValueError, "belongs to another owner"):
            self.manager.start_one(command("ig_not_registered_12", "fake.person"))
        self.assertFalse(any(self.manager._alive(v["robot"]) for v in self.manager.workspaces.values()))

    def test_one_worker_at_a_time_and_distinct_owner_stop(self):
        self.manager.configure(config())
        entered = threading.Event()
        release = threading.Event()
        count = []
        def run_a():
            count.append(A)
            entered.set()
            release.wait(4)
        self.manager.workspaces[A]["robot"]._run = run_a
        self.manager.workspaces[B]["robot"]._run = lambda: count.append(B)
        try:
            response = self.manager.start_one(command())
            self.assertEqual(response["account"], A)
            self.assertTrue(entered.wait(3))
            self.assertEqual(self.manager.status(OWNER)["lanes"][0]["account"], A)
            self.assertTrue(self.manager.status(OWNER)["lanes"][0]["running"])
            with self.assertRaisesRegex(ValueError, "Only one relationship-changing"):
                self.manager.start_one(command(B, "second.person", target="other.target"))
            with self.assertRaisesRegex(ValueError, "Confirm the exact"):
                self.manager.pause_one({"owner": OWNER, "account": A, "confirmation": "wrong"})
            with self.assertRaisesRegex(ValueError, "belongs to another owner"):
                self.manager.pause_one({
                    "owner": OWNER, "account": "ig_other_123456",
                    "confirmation": "action-workspace-pause:" + OWNER + ":ig_other_123456"})
            self.manager.pause_one({
                "owner": OWNER, "account": A,
                "confirmation": "action-workspace-pause:" + OWNER + ":" + A})
            self.assertTrue(self.manager.workspaces[A]["robot"].stop_event.is_set())
            self.assertFalse(self.manager.workspaces[B]["robot"].stop_event.is_set())
        finally:
            release.set()
            self.manager.workspaces[A]["robot"].worker.join(5)
        self.assertEqual(count, [A])
        self.assertFalse(self.manager._alive(self.manager.workspaces[A]["robot"]))
        response = self.manager.start_one(command(B, "second.person", target="other.target"))
        self.assertEqual(response["account"], B)
        self.manager.workspaces[B]["robot"].worker.join(5)
        self.assertEqual(count, [A, B])
        self.assertEqual(self.manager.workspaces[A]["robot"].account, A)
        self.assertEqual(self.manager.workspaces[B]["robot"].account, B)

    def test_chrome_identity_lease_blocks_action_before_any_worker_code(self):
        self.manager.configure(config())
        folder = self.sessions.directory(OWNER, A)
        entered = []
        self.manager.workspaces[A]["robot"]._run = lambda: entered.append("UNSAFE")
        with ChromeLaneLease(folder):
            started = self.manager.start_one(command())
            self.assertEqual(started["account"], A)
            self.manager.workspaces[A]["robot"].worker.join(5)
            state = self.manager.status(OWNER)["lanes"][0]
            self.assertEqual(state["state"], "blocked")
            self.assertIn("already owned", state["message"])
            self.assertFalse(state["running"])
            self.assertEqual(entered, [])
        # A refused browser admission leaves the original exact-scope batch
        # for manual review/continue; it never claims a relationship click.
        journal = self.manager.workspaces[A]["robot"]._journal()
        self.assertEqual(journal, {})
        self.assertFalse(self.manager.workspaces[B]["robot"].worker)

    def test_protected_account_never_starts_and_other_account_unaffected(self):
        self.manager.configure(config())
        first = self.manager.workspaces[A]["robot"]
        second = self.manager.workspaces[B]["robot"]
        path = first._protection_file_for(OWNER, A)
        _atomic_json(path, ["fresh.account"])
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, "protected"):
            self.manager.start_one(command())
        self.assertEqual(first.owner, "")
        self.assertEqual(second.owner, "")
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(first.worker)
        self.assertFalse(second.worker)

    def test_manual_review_opens_only_prior_target_in_exact_account_chrome(self):
        self.manager.configure(config())
        one = self.manager.workspaces[A]["robot"]
        saved = one._base_for(OWNER, A, "unfollow")
        _atomic_json(saved, {"old.target": {"status": "review", "message": "Outcome unverified"}})
        _atomic_json(one._review_batches_file_for(OWNER, A, "unfollow"),
                     [{"id": "saved-wave", "targets": ["old.target"],
                       "approved_at": None, "recheck_results": {}}])
        result = self.manager.review_one(
            {"owner": OWNER, "account": A, "task": "unfollow"})
        self.assertEqual(result["batch"]["id"], "saved-wave")
        with self.assertRaisesRegex(ValueError, "never inspected"):
            self.manager.open_review_one({
                "owner": OWNER, "account": A, "task": "unfollow",
                "username": "fresh.target",
                "confirmation": "action-workspace-review:" + OWNER + ":" + A + ":fresh.target"})
        with self.assertRaisesRegex(ValueError, "never inspected"):
            self.manager.open_review_one({
                "owner": OWNER, "account": B, "task": "unfollow",
                "username": "old.target",
                "confirmation": "action-workspace-review:" + OWNER + ":" + B + ":old.target"})
        with self.assertRaisesRegex(ValueError, "Confirm the exact"):
            self.manager.open_review_one({
                "owner": OWNER, "account": A, "task": "unfollow",
                "username": "old.target", "confirmation": "wrong"})
        with patch("profile_actions.shutil.which", return_value=sys.executable), \
             patch("profile_actions.subprocess.Popen") as opened:
            value = self.manager.open_review_one({
                "owner": OWNER, "account": A, "task": "unfollow",
                "username": "old.target",
                "confirmation": "action-workspace-review:" + OWNER + ":" + A + ":old.target"})
            self.assertEqual(value["relationship_action"], False)
            args = opened.call_args.args[0]
            # Windows can expand an 8.3 temp path (RUNNER~1) when the
            # robot resolves its Chrome directory. Compare canonical paths.
            chosen = next(a.split("=", 1)[1] for a in args
                          if a.startswith("--user-data-dir="))
            self.assertEqual(Path(chosen).resolve(), self.sessions.directory(OWNER, A).resolve())
            self.assertNotEqual(Path(chosen).resolve(), self.sessions.directory(OWNER, B).resolve())
            self.assertIn("https://www.instagram.com/old.target/", args)
            opened.assert_called_once()

    def test_approve_exact_account_archives_only_checked_and_preserves_uncertain(self):
        self.manager.configure(config())
        robot = self.manager.workspaces[A]["robot"]
        entry = {"id": "wave-exact", "targets": ["confirmed.one", "uncertain.two"],
                 "approved_at": None, "recheck_results": {}}
        _atomic_json(robot._review_batches_file_for(OWNER, A, "cancel"), [entry])
        records = {
            "confirmed.one": {"status": "ok", "at": "2026-10-30T14:00:00Z",
                              "message": "Confirmed no active Requested."},
        }
        journal = robot._base_for(OWNER, A, "cancel")
        _atomic_json(journal, records)
        data = {
            "owner": OWNER, "account": A, "task": "cancel",
            "batch_id": "wave-exact",
            "confirmation": "action-workspace-approve:" + OWNER + ":" + A +
                            ":cancel:wave-exact",
        }
        with self.assertRaisesRegex(ValueError, "untouched"):
            self.manager.approve_one(data)
        with self.assertRaisesRegex(ValueError, "Confirm the exact"):
            self.manager.approve_one({**data, "confirmation": "wrong"})
        with self.assertRaisesRegex(ValueError, "pending batch changed"):
            self.manager.approve_one({**data, "account": B,
                "confirmation": "action-workspace-approve:" + OWNER + ":" + B +
                                 ":cancel:wave-exact"})
        self.assertIsNone(robot._pending_review(OWNER, A, "cancel").get("approved_at"))
        records["uncertain.two"] = {
            "status": "review", "issue": "interrupted_action_uncertain",
            "at": "2026-10-30T14:01:00Z", "message": "Click may have occurred",
            "click_intent": {"task": "cancel", "batch_id": "wave-exact",
                             "phase": "cancel_request_confirmation",
                             "written_at": "2026-10-30T14:00:59Z",
                             "requires_manual_review": True},
        }
        _atomic_json(journal, records)
        before = journal.read_bytes()
        outcome = self.manager.approve_one(data)
        self.assertEqual(outcome["approved_usernames"], ["confirmed.one"])
        self.assertEqual(outcome["unresolved_usernames"], ["uncertain.two"])
        self.assertIsNone(robot._pending_review(OWNER, A, "cancel"))
        self.assertEqual(journal.read_bytes(), before,
                         "Review approval must NEVER rewrite or erase action evidence.")
        self.assertIsNone(self.manager.workspaces[B]["robot"].worker)

    def test_review_reports_only_saved_timestamp_without_promoting_uncertain_click(self):
        self.manager.configure(config())
        robot = self.manager.workspaces[A]["robot"]
        _atomic_json(robot._base_for(OWNER, A, "cancel"), {
            "confirmed.profile": {
                "status": "ok", "at": "2026-10-30T10:00:00Z",
                "message": "Confirmed no request"},
            "uncertain.profile": {
                "status": "review", "issue": "interrupted_action_uncertain",
                "at": "2026-10-30T10:01:00Z",
                "message": "Uncertain result", "click_intent": {
                    "batch_id": "wave-review", "task": "cancel",
                    "phase": "cancel_request_confirmation", "written_at": "2026-10-30T10:00:59Z",
                    "requires_manual_review": True},
            },
        })
        _atomic_json(robot._review_batches_file_for(OWNER, A, "cancel"), [{
            "id": "wave-review",
            "targets": ["confirmed.profile", "uncertain.profile", "untouched.profile"],
            "approved_at": None, "recheck_results": {},
        }])
        first = robot._base_for(OWNER, A, "cancel").read_bytes()
        data = self.manager.review_one({"owner": OWNER, "account": A, "task": "cancel"})
        rows = data["batch"]["action_results"]
        self.assertEqual(rows["confirmed.profile"]["status"], "ok")
        self.assertEqual(rows["confirmed.profile"]["at"], "2026-10-30T10:00:00Z")
        self.assertEqual(rows["uncertain.profile"]["status"], "review")
        self.assertEqual(rows["uncertain.profile"]["at"], "2026-10-30T10:01:00Z")
        self.assertTrue(rows["uncertain.profile"]["possible_click"])
        self.assertEqual(rows["untouched.profile"]["status"], "pending")
        self.assertEqual(rows["untouched.profile"]["at"], "")
        self.assertEqual(robot._base_for(OWNER, A, "cancel").read_bytes(), first)
        self.assertIsNone(self.manager.workspaces[B]["robot"].worker)

    def test_continue_saved_cohort_requires_exact_batch_and_preserves_wal(self):
        self.manager.configure(config())
        robot = self.manager.workspaces[A]["robot"]
        original_targets = ["possibly.clicked", "still.untouched"]
        saved = {
            "possibly.clicked": {
                "status": "review", "issue": "interrupted_action_uncertain",
                "message": "Relationship click outcome unknown.",
                "click_intent": {"phase": "cancel_request_confirmation", "batch_id": "saved-wave",
                                 "task": "cancel", "written_at": "2026-10-30T15:00:00Z",
                                 "requires_manual_review": True},
            }
        }
        _atomic_json(robot._base_for(OWNER, A, "cancel"), saved)
        _atomic_json(robot._review_batches_file_for(OWNER, A, "cancel"), [{
            "id": "saved-wave", "targets": original_targets,
            "approved_at": None, "recheck_results": {},
        }])
        before = robot._base_for(OWNER, A, "cancel").read_bytes()
        command_base = command(A, "first.person", task="cancel", target="possibly.clicked")
        cohort = {**command_base["action"], "targets": original_targets,
                  "batch_size": len(original_targets),
                  "confirmation": "cancel:2", "batch_id": "saved-wave"}
        with self.assertRaisesRegex(ValueError, "An unapproved batch exists"):
            self.manager.start_one({**command_base, "action": {
                **cohort, "targets": ["still.untouched"], "batch_size": 1,
                "confirmation": "cancel:1"}})
        with self.assertRaisesRegex(ValueError, "An unapproved batch exists"):
            self.manager.start_one({**command_base, "action": {
                **cohort, "batch_id": "wrong"}})
        self.assertEqual(robot._base_for(OWNER, A, "cancel").read_bytes(), before)
        self.assertFalse(robot.worker)
        called = []
        robot._run = lambda: called.append("would only inspect the saved cohort")
        result = self.manager.start_one({**command_base, "action": cohort})
        self.assertEqual(result["account"], A)
        robot.worker.join(5)
        self.assertEqual(called, ["would only inspect the saved cohort"])
        self.assertEqual(robot.targets, original_targets)
        self.assertEqual(robot.active_batch_id, "saved-wave")
        self.assertEqual(robot._base_for(OWNER, A, "cancel").read_bytes(), before)
        self.assertIsNone(self.manager.workspaces[B]["robot"].worker)

    def test_shutdown_joins_only_actual_action_workers(self):
        self.manager.configure(config())
        entered = threading.Event()
        robot = self.manager.workspaces[A]["robot"]
        def waiter():
            entered.set()
            robot.stop_event.wait(3)
        robot._run = waiter
        self.manager.start_one(command())
        self.assertTrue(entered.wait(3))
        self.manager.shutdown()
        self.assertTrue(robot.stop_event.is_set())
        self.assertFalse(robot.worker.is_alive())


class BridgeIsolatedWorkspaceTests(unittest.TestCase):
    def test_token_protected_configure_status_and_reject_mutation_without_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            server = build_server(Collector(root / "data", root / "chrome"), "token-123", 0)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = "http://127.0.0.1:" + str(server.server_port)
            def send(path, value=None, token="token-123"):
                url = base + path
                payload = None if value is None else json.dumps(value).encode("utf8")
                req = urllib.request.Request(url, data=payload, method="GET" if value is None else "POST",
                    headers={"X-IGC-Bridge-Token": token, "Origin": "null",
                             "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    return json.load(response)
            try:
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    send("/api/actions/dual-action-workspaces/configure", config(), token="wrong")
                self.assertEqual(rejected.exception.code, 403)
                x = send("/api/actions/dual-action-workspaces/configure", config())
                self.assertTrue(x["two_workspaces"])
                x = send("/api/actions/dual-action-workspaces/status?owner=" + OWNER)
                self.assertFalse(x["parallel_mutations_enabled"])
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    send("/api/actions/dual-action-workspaces/start-one", {
                        **command(), "confirmation": "wrong"})
                self.assertEqual(rejected.exception.code, 400)
                self.assertFalse(list((root / "data").glob("instagram-actions-*.json")))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(5)

    def test_developer_disallows_workspace_action_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            server = build_server(Collector(root / "developer", root / "chrome"),
                "dev-token", 0, developer_mode=True, audit_root=root / "audit")
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                data = json.dumps(config()).encode()
                req = urllib.request.Request(
                    "http://127.0.0.1:" + str(server.server_port)
                    + "/api/actions/dual-action-workspaces/configure",
                    data=data, method="POST", headers={
                        "Origin": "null", "X-IGC-Bridge-Token": "dev-token",
                        "Content-Type": "application/json"})
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    urllib.request.urlopen(req, timeout=5)
                self.assertEqual(rejected.exception.code, 400)
                self.assertIsNone(server.dual_action_workspaces)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(5)


if __name__ == "__main__":
    unittest.main()
