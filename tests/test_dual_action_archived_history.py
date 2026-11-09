"""Read-only archived cohorts for two Instagram workspaces (offline WAL fixture)."""
import json
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dual_action_workspaces import DualActionWorkspaces
from dual_chrome_sessions import DualChromeSessions
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server

OWNER = "u_owner_42"
A, B = "ig_account_123456", "ig_account_789012"


def bindings():
    return {
        "owner": OWNER,
        "primary": {"account": A, "expected_handle": "alpha.one"},
        "secondary": {"account": B, "expected_handle": "beta.two"},
        "read_only_consent": True, "acknowledge_serial_actions": True,
        "confirmation": "dual-action-workspaces:" + A + ":" + B,
    }


def request(account=A, task="unfollow", owner=OWNER):
    return {
        "owner": owner, "account": account, "task": task,
        "confirmation": "action-workspace-archive:" + owner + ":" + account + ":" + task,
    }


class ArchivedHistoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.collector = Collector(self.root / "data", self.root / "legacy")
        self.legacy = ActionRobot(self.collector, self.collector.data_dir,
                                  self.collector.session_dir)
        self.manager = DualActionWorkspaces(
            DualChromeSessions(self.root / "chrome"), self.collector,
            self.collector.data_dir, self.legacy)
        self.addCleanup(self.manager.shutdown)
        self.manager.configure(bindings())

    def seed(self, manager, account, task, batch, *, deferred=True):
        robot = manager.workspaces[account]["robot"]
        cohorts = robot._review_batches_file_for(OWNER, account, task)
        journal = robot._base_for(OWNER, account, task)
        record = {
            "id": batch, "created_at": "2026-11-09T07:00:00Z",
            "targets": ["possible.click", "not.attempted"],
            "deferred_at": "2026-11-09T07:30:00Z" if deferred else None,
            "deferred_reason": "owner_cancelled" if deferred else "",
            "deferred_action_recorded": 1, "deferred_untouched": 1,
            "deferred_protected_usernames": ["protected.target"],
            "approved_at": None, "recheck_results": {},
        }
        _atomic_json(cohorts, [record])
        _atomic_json(journal, {"possible.click": {
            "status": "review", "issue": "interrupted_action_uncertain",
            "click_intent": {"phase": "relationship_control"},
        }})
        return cohorts, journal

    def test_read_only_archives_after_restart_isolate_accounts_and_tasks(self):
        a = self.seed(self.manager, A, "unfollow", "cancelled-A")
        b = self.seed(self.manager, B, "cancel", "cancelled-B")
        fresh = self.seed(self.manager, A, "cancel", "not-archived", deferred=False)
        before = [(file, file.read_bytes()) for pair in (a, b, fresh) for file in pair]
        restarted = DualActionWorkspaces(
            DualChromeSessions(self.root / "chrome"), self.collector,
            self.collector.data_dir, self.legacy)
        self.addCleanup(restarted.shutdown)
        self.assertTrue(restarted.status(OWNER)["bindings_restored_from_disk"])
        output = restarted.archived_one(request())
        self.assertEqual((output["owner"], output["account"], output["task"]),
                         (OWNER, A, "unfollow"))
        self.assertEqual(output["total_deferred"], 1)
        self.assertTrue(output["read_only"])
        row = output["recent"][0]
        self.assertEqual(row["batch_id"], "cancelled-A")
        self.assertEqual(row["reason"], "owner_cancelled")
        self.assertEqual((row["target_count"], row["action_recorded"], row["untouched"]),
                         (2, 1, 1))
        self.assertEqual(row["protected_count"], 1)
        self.assertFalse(row["marked_reviewed"])
        self.assertNotIn("possible.click", str(output),
                         "Never expose target identities from archived batches.")
        self.assertEqual(restarted.archived_one(request(B, "cancel"))["recent"][0]["batch_id"],
                         "cancelled-B")
        self.assertEqual(restarted.archived_one(request(A, "cancel"))["total_deferred"], 0)
        for file, blob in before:
            self.assertEqual(file.read_bytes(), blob,
                             "History read must never change original action WAL.")
        self.assertFalse(any(l["robot"].worker for l in restarted.workspaces.values()))

    def test_invalid_account_task_owner_or_confirmation_denied(self):
        self.seed(self.manager, A, "unfollow", "cancelled-A")
        for bad in (
            {**request(), "confirmation": "bad"},
            request(B, "unfollow", owner="u_other_42"),
            request("ig_outside_1234", "unfollow"),
            request(A, "audit"),
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.manager.archived_one(bad)

    def test_authenticated_local_bridge_matches_exact_account(self):
        server = build_server(self.collector, "z"*32, 0)
        self.addCleanup(server.server_close)
        server.dual_action_workspaces.configure(bindings())
        self.seed(server.dual_action_workspaces, A, "unfollow", "cancelled-A")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:" + str(server.server_port) + (
            "/api/actions/dual-action-workspaces/archived-one")

        def send(body, token="z"*32):
            req = urllib.request.Request(
                url, data=json.dumps(body).encode(), method="POST",
                headers={"X-IGC-Bridge-Token": token, "Origin": "null",
                         "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    return resp.status, json.load(resp)
            except urllib.error.HTTPError as exc:
                return exc.code, json.load(exc)
        try:
            self.assertNotEqual(send(request(), "wrong")[0], 200)
            self.assertEqual(send({**request(), "confirmation": "wrong"})[0], 400)
            status, data = send(request())
            self.assertEqual(status, 200)
            self.assertEqual(data["recent"][0]["batch_id"], "cancelled-A")
            self.assertEqual(data["source"], "local_saved_action_batches")
            self.assertEqual(send(request(B, "unfollow"))[1]["total_deferred"], 0)
        finally:
            server.shutdown()
            thread.join(timeout=4)


if __name__ == "__main__":
    unittest.main()
