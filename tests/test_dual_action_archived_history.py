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

    def test_all_47_archived_waves_paginate_without_crossing_accounts(self):
        """Never hide waves 21+ or mutate journals while inspecting an archive."""
        robot = self.manager.workspaces[A]["robot"]
        batches = robot._review_batches_file_for(OWNER, A, "unfollow")
        journal = robot._base_for(OWNER, A, "unfollow")
        rows = [
            {"id": "archived-" + str(n), "targets": ["target." + str(n)],
             "created_at": "2026-11-09T07:00:00Z",
             "deferred_at": "2026-11-09T08:00:00Z",
             "deferred_reason": "owner_cancelled",
             "deferred_action_recorded": 0, "deferred_untouched": 1}
            for n in range(47)
        ]
        _atomic_json(batches, rows)
        _atomic_json(journal, {"target.0": {
            "status": "review", "issue": "interrupted_action_uncertain",
            "click_intent": {"phase": "relationship_control"}}})
        sibling = self.seed(self.manager, B, "cancel", "separate-B")
        snapshots = [(p, p.read_bytes()) for p in (batches, journal, *sibling)]
        found = []
        for page, expected in ((0, 20), (20, 20), (40, 7)):
            result = self.manager.archived_one({**request(), "offset": page})
            self.assertEqual(result["offset"], page)
            self.assertEqual(result["page_size"], 20)
            self.assertEqual(result["total_deferred"], 47)
            self.assertEqual(len(result["recent"]), expected)
            self.assertEqual(result["has_more"], page < 40)
            self.assertEqual(result["next_offset"], page + expected if page < 40 else None)
            found.extend(record["batch_id"] for record in result["recent"])
            self.assertNotIn("target.", str(result),
                             "Archive index must never expose target usernames.")
        self.assertEqual(found, ["archived-" + str(n) for n in reversed(range(47))])
        self.assertEqual(self.manager.archived_one({**request(), "offset": 47})["recent"], [])
        self.assertEqual(self.manager.archived_one(request(B, "cancel"))["recent"][0]["batch_id"],
                         "separate-B")
        self.assertEqual(self.manager.archived_one(request(A, "cancel"))["total_deferred"], 0)
        for bad in (-1, True, False, 1.5, "20", 1_000_001):
            with self.subTest(cursor=bad), self.assertRaises(ValueError):
                self.manager.archived_one({**request(), "offset": bad})
        for path, saved in snapshots:
            self.assertEqual(path.read_bytes(), saved)
        self.assertFalse(self.manager.sessions.root.exists(),
                         "Archive pagination cannot start Chrome.")

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

    def test_archived_details_show_uncertain_first_in_view_and_never_replay(self):
        a_files = self.seed(self.manager, A, "unfollow", "cancelled-A")
        b_files = self.seed(self.manager, B, "cancel", "cancelled-B")
        old = json.loads(a_files[0].read_text("utf-8"))
        old[0]["targets"] = [
            "confirmed.click", "uncertain.click", "untouched.one",
            "forged.ok", "already.resolved"]
        _atomic_json(a_files[0], old)
        _atomic_json(a_files[1], {
            "confirmed.click": {"status": "ok", "click_intent": {
                "phase": "relationship_control", "outcome_recorded": True}},
            "uncertain.click": {"status": "review", "click_intent": {
                "phase": "relationship_control"}},
            "forged.ok": {"status": "ok", "click_intent": {
                "phase": "relationship_control"}},
            "already.resolved": {"status": "already_not_following"},
        })
        before = [(p, p.read_bytes()) for part in (a_files, b_files) for p in part]
        fresh = DualActionWorkspaces(
            DualChromeSessions(self.root / "chrome"),
            self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(fresh.shutdown)
        self.assertTrue(fresh.status(OWNER)["bindings_restored_from_disk"])
        payload = {
            **request(), "batch_id": "cancelled-A",
            "confirmation": ("action-workspace-archive-detail:" + OWNER + ":" +
                             A + ":unfollow:cancelled-A"),
        }
        result = fresh.archived_detail_one(payload)
        self.assertTrue(result["archived"])
        self.assertTrue(result["read_only"])
        self.assertEqual(result["targets"], old[0]["targets"],
                         "The archived original order is immutable on disk.")
        states = result["action_results"]
        self.assertEqual(states["confirmed.click"]["status"], "ok")
        self.assertTrue(states["confirmed.click"]["possible_click"])
        self.assertEqual(states["uncertain.click"]["status"], "review")
        self.assertTrue(states["uncertain.click"]["possible_click"])
        self.assertEqual(states["forged.ok"]["status"], "review",
                         "A forged OK without recorded click outcome stays warning.")
        self.assertEqual(states["untouched.one"]["status"], "pending")
        self.assertFalse(states["untouched.one"]["possible_click"])
        self.assertEqual(states["already.resolved"]["status"],
                         "already_not_following")
        self.assertFalse(states["already.resolved"]["possible_click"])
        self.assertNotIn("click_intent", str(result),
                         "Return a minimal read-only view, not raw WAL internals.")
        for file, blob in before:
            self.assertEqual(file.read_bytes(), blob)
        self.assertFalse(any(x["robot"].worker for x in fresh.workspaces.values()))
        for bad in (
            {**payload, "confirmation": "wrong"},
            {**payload, "batch_id": "cancelled-B"},
            {**payload, "account": B},
            {**payload, "task": "cancel"},
            {**payload, "owner": "u_else_42"},
        ):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                fresh.archived_detail_one(bad)
        # A valid confirmation cannot bypass the exact archived batch scope.
        bad_scope = {
            **request(B, "cancel"), "batch_id": "cancelled-A",
            "confirmation": ("action-workspace-archive-detail:" + OWNER + ":" +
                             B + ":cancel:cancelled-A"),
        }
        with self.assertRaises(ValueError):
            fresh.archived_detail_one(bad_scope)

    def test_archived_detail_route_requires_token_and_exact_cohort(self):
        server = build_server(self.collector, "z"*32, 0)
        self.addCleanup(server.server_close)
        server.dual_action_workspaces.configure(bindings())
        self.seed(server.dual_action_workspaces, A, "unfollow", "cancelled-A")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = "http://127.0.0.1:" + str(server.server_port) + (
            "/api/actions/dual-action-workspaces/archived-detail-one")
        payload = {
            **request(), "batch_id": "cancelled-A",
            "confirmation": ("action-workspace-archive-detail:" + OWNER + ":" +
                             A + ":unfollow:cancelled-A"),
        }

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
            self.assertNotEqual(send(payload, "invalid")[0], 200)
            self.assertEqual(send({**payload, "confirmation": "wrong"})[0], 400)
            self.assertEqual(send({**payload, "batch_id": "not-archived"})[0], 400)
            status, data = send(payload)
            self.assertEqual(status, 200)
            self.assertEqual(data["account"], A)
            self.assertTrue(data["read_only"])
            self.assertEqual(data["targets"], ["possible.click", "not.attempted"])
            self.assertTrue(data["action_results"]["possible.click"]["possible_click"])
            self.assertEqual(data["action_results"]["not.attempted"]["status"], "pending")
        finally:
            server.shutdown()
            thread.join(timeout=4)

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
