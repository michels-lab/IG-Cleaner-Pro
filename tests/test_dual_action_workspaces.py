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
        # The two action lanes expose owner-proof navigation separately
        # from relationship results, without leaking browser paths or cookies.
        first["robot"].owner_profile_visits = 4
        first["robot"].owner_sibling_proofs = 2
        second["robot"].owner_profile_visits = 1
        second["robot"].owner_sibling_proofs = 7
        snapshot = self.manager.status(OWNER)
        by_account = {row["account"]: row for row in snapshot["lanes"]}
        self.assertEqual(by_account[A]["owner_profile_visits"], 4)
        self.assertEqual(by_account[A]["owner_sibling_proofs"], 2)
        self.assertEqual(by_account[B]["owner_profile_visits"], 1)
        self.assertEqual(by_account[B]["owner_sibling_proofs"], 7)
        # Read-only per-lane SOURCE results, not fabricated from processed.
        def fake_status(task, total, processed, successful, no_follow, no_request, batch):
            return {"status": "running", "message": "Live exact target", "running": True,
                    "task": task, "current_profile": "", "processed": processed,
                    "pending": total-processed, "issue_count": 1,
                    "owner_profile_visits": 0, "owner_sibling_proofs": 0,
                    "total": total, "successful": successful,
                    "already_not_following": no_follow,
                    "already_not_requested": no_request,
                    "batch_size": 10, "review_batch": {"id": batch}}
        with patch.object(first["robot"], "snapshot", return_value=fake_status(
                "unfollow", 13, 8, 0, 2, 1, "batch-owner-A")), patch.object(
                second["robot"], "snapshot", return_value=fake_status(
                "cancel", 15, 5, 3, 0, 2, "batch-owner-B")):
            evidence = {x["account"]: x for x in self.manager.status(OWNER)["lanes"]}
        self.assertEqual(evidence[A]["successful"], 0)
        self.assertEqual(evidence[A]["already_not_following"], 2)
        self.assertEqual(evidence[A]["already_not_requested"], 1)
        self.assertEqual(evidence[A]["total"], 13)
        self.assertEqual(evidence[A]["batch_id"], "batch-owner-A")
        self.assertEqual(evidence[B]["successful"], 3)
        self.assertEqual(evidence[B]["already_not_requested"], 2)
        self.assertEqual(evidence[B]["total"], 15)
        self.assertEqual(evidence[B]["batch_id"], "batch-owner-B")
        self.assertNotIn("session_dir", str(snapshot))
        self.assertFalse(self.collector.data_dir.exists())
        self.assertFalse(self.sessions.root.exists(),
                         "Configuring workspaces must not open Chrome or create login data.")

    def test_restart_recovers_two_links_without_actions_secrets_or_parallel_consent(self):
        """Real native manager restart loads only identities; never a Chrome job."""
        parallel = {
            **config(), "acknowledge_serial_actions": False,
            "parallel_actions_consent": True, "acknowledge_parallel_actions": True,
            "confirmation": "dual-action-workspaces-parallel:" + A + ":" + B,
        }
        original = self.manager.configure(parallel)
        self.assertTrue(original["parallel_mutations_enabled"])
        links = self.manager._binding_file(OWNER)
        self.assertTrue(links.is_file())
        self.assertFalse(links.is_relative_to(self.collector.data_dir))
        self.assertFalse(links.is_relative_to(self.sessions.root))
        saved = json.loads(links.read_text("utf-8"))
        self.assertEqual(saved, {
            "version": 1, "owner": OWNER,
            "primary": {"account": A, "expected_handle": "first.person"},
            "secondary": {"account": B, "expected_handle": "second.person"},
        })
        for forbidden in ("cookie", "session", "token", "password", "targets",
                          "confirmation", "consent", "parallel", "protected"):
            self.assertNotIn(forbidden, links.read_text("utf-8").lower())
        first_robot = self.manager.workspaces[A]["robot"]
        journal = first_robot._base_for(OWNER, A, "cancel")
        batch = first_robot._review_batches_file_for(OWNER, A, "cancel")
        _atomic_json(journal, {"clicked.uncertain": {
            "status": "review", "issue": "interrupted_action_uncertain",
            "message": "Click outcome not proven",
        }})
        _atomic_json(batch, [{
            "id": "saved-on-previous-run",
            "targets": ["clicked.uncertain"], "approved_at": None,
            "recheck_results": {},
        }])
        original_journal = journal.read_bytes()
        original_batch = batch.read_bytes()

        # New backend instance: no configure, no consent and NO worker or browser.
        restarted = DualActionWorkspaces(
            DualChromeSessions(self.root / "browser"),
            self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(restarted.shutdown)
        result = restarted.status(OWNER)
        self.assertTrue(result["bindings_restored_from_disk"])
        self.assertTrue(result["two_workspaces"])
        self.assertFalse(result["parallel_mutations_enabled"],
                         "Prior parallel consent cannot survive app restart.")
        self.assertEqual(result["mode"], "independent_chrome_sessions_serialized_actions")
        self.assertEqual([r["account"] for r in result["lanes"]], [A, B])
        self.assertEqual([r["expected_handle"] for r in result["lanes"]],
                         ["first.person", "second.person"])
        self.assertTrue(all(not r["running"] for r in result["lanes"]))
        self.assertEqual(restarted.workspaces[A]["chrome"],
                         self.sessions.directory(OWNER, A))
        self.assertEqual(restarted.workspaces[B]["chrome"],
                         self.sessions.directory(OWNER, B))
        self.assertIsNone(restarted.workspaces[A]["robot"].worker)
        self.assertIsNone(restarted.workspaces[B]["robot"].worker)
        self.assertFalse(self.sessions.root.exists(), "Restoring metadata cannot open Chrome.")
        review = restarted.review_one({"owner": OWNER, "account": A, "task": "cancel"})
        self.assertEqual(review["batch"]["id"], "saved-on-previous-run")
        self.assertEqual(review["batch"]["action_results"]["clicked.uncertain"]["status"],
                         "review", "Uncertain click must never be promoted to OK.")
        self.assertEqual(journal.read_bytes(), original_journal)
        self.assertEqual(batch.read_bytes(), original_batch)
        with self.assertRaisesRegex(ValueError, "must match"):
            restarted.start_one({**command(),
                                 "action": {**action(), "expected_handle": "other.person"}})
        self.assertFalse(any(restarted._alive(l["robot"]) for l in restarted.workspaces.values()))

    def test_cold_restart_shows_original_40_vs_replanned_10_and_scoped_warnings(self):
        """After Windows reopens, original 40 must not look like an empty job."""
        self.manager.configure(config())
        robot_a = self.manager.workspaces[A]["robot"]
        robot_b = self.manager.workspaces[B]["robot"]
        original = ["old.wave." + str(i) for i in range(40)]
        chosen = original[:10]
        batch_a = robot_a._review_batches_file_for(OWNER, A, "unfollow")
        journal_a = robot_a._base_for(OWNER, A, "unfollow")
        batch_b = robot_b._review_batches_file_for(OWNER, B, "cancel")
        journal_b = robot_b._base_for(OWNER, B, "cancel")
        _atomic_json(batch_a, [{
            "id": "saved-forty", "targets": chosen, "original_targets": original,
            "approved_at": None, "recheck_results": {},
        }])
        _atomic_json(journal_a, {
            chosen[0]: {"status": "already_not_following"},
            chosen[1]: {"status": "review",
                        "issue": "interrupted_action_uncertain",
                        "click_intent": {"phase": "relationship_control"}},
            chosen[2]: {"status": "ok",
                        # Exact persisted proof of one successful relationship
                        # change must still appear as green after restart.
                        "click_intent": {"phase": "relationship_control",
                                         "outcome_recorded": True}},
        })
        _atomic_json(batch_b, [{
            "id": "saved-second", "targets": ["request.one", "request.two"],
            "approved_at": None, "recheck_results": {},
        }])
        _atomic_json(journal_b, {
            "request.one": {"status": "already_not_requested"},
        })
        saved_bytes = [(p, p.read_bytes()) for p in
                       (batch_a, journal_a, batch_b, journal_b)]
        restarted = DualActionWorkspaces(
            DualChromeSessions(self.root / "browser"),
            self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(restarted.shutdown)
        snapshot = restarted.status(OWNER)
        self.assertTrue(snapshot["bindings_restored_from_disk"])
        lanes = {row["account"]: row for row in snapshot["lanes"]}
        self.assertFalse(lanes[A]["running"])
        self.assertFalse(lanes[B]["running"])
        self.assertEqual(lanes[A]["task"], "",
                         "Saved metadata may not start an action robot.")
        self.assertEqual(lanes[B]["task"], "")
        self.assertEqual(lanes[A]["saved_batches"], [{
            "task": "unfollow", "batch_id": "saved-forty",
            "original_total": 40, "current_total": 10,
            "untouched": 7, "confirmed_clicks": 1,
            "already_resolved_no_click": 1, "warnings": 1,
            "unavailable_no_click": 0, "requires_explicit_resume": True,
            "source": "saved_local_action_journal",
        }])
        self.assertEqual(lanes[B]["saved_batches"][0]["task"], "cancel")
        self.assertEqual(lanes[B]["saved_batches"][0]["current_total"], 2)
        self.assertEqual(lanes[B]["saved_batches"][0]["untouched"], 1)
        self.assertEqual(lanes[B]["saved_batches"][0]["already_resolved_no_click"], 1)
        self.assertNotIn("old.wave.", str(snapshot),
                         "Status summaries must not leak original target usernames.")
        self.assertFalse(self.sessions.root.exists(),
                         "Restart status cannot open Chrome or create browser profiles.")
        for file, original_data in saved_bytes:
            self.assertEqual(file.read_bytes(), original_data,
                             "Hydrating the badge must not mutate canonical action WAL.")

        # A damaged persisted cohort is NOT interpreted as no unfinished job.
        _atomic_json(batch_a, [{
            "id": "saved-forty", "targets": "corrupt",
            "approved_at": None, "recheck_results": {},
        }])
        damaged = restarted.status(OWNER)["lanes"][0]["saved_batches"]
        self.assertTrue(damaged[0]["unverifiable"])
        self.assertTrue(damaged[0]["requires_manual_review"])
        self.assertNotIn("current_total", damaged[0],
                         "Do not invent a zero when original saved wave is corrupt.")

    def test_saved_batch_counts_verified_click_separately_from_ambiguous_intent(self):
        """An outcome-recorded click is confirmed; missing proof is Review."""
        self.manager.configure(config())
        robot = self.manager.workspaces[A]["robot"]
        batch = robot._review_batches_file_for(OWNER, A, "unfollow")
        journal = robot._base_for(OWNER, A, "unfollow")
        _atomic_json(batch, [{
            "id": "signed-evidence", "targets": [
                "confirmed.with.wal", "unconfirmed.with.wal",
                "no.click", "untouched.profile"],
            "approved_at": None, "recheck_results": {},
        }])
        _atomic_json(journal, {
            "confirmed.with.wal": {
                "status": "ok", "click_intent": {
                    "phase": "relationship_control", "outcome_recorded": True},
            },
            "unconfirmed.with.wal": {
                "status": "ok", "click_intent": {
                    "phase": "relationship_control"},
            },
            "no.click": {"status": "already_not_following"},
        })
        saved_batch, saved_journal = batch.read_bytes(), journal.read_bytes()
        restored = DualActionWorkspaces(
            DualChromeSessions(self.root / "browser"),
            self.collector, self.collector.data_dir, self.legacy)
        self.addCleanup(restored.shutdown)
        snapshot = restored.status(OWNER)
        row = next(x for x in snapshot["lanes"] if x["account"] == A)
        results = row["saved_batches"][0]
        self.assertEqual(results["confirmed_clicks"], 1,
                         "Valid terminal OK with recorded click must be counted.")
        self.assertEqual(results["warnings"], 1,
                         "Forged OK without recorded outcome cannot turn green.")
        self.assertEqual(results["already_resolved_no_click"], 1)
        self.assertEqual(results["untouched"], 1)
        self.assertEqual(results["current_total"], 4)
        self.assertEqual(batch.read_bytes(), saved_batch)
        self.assertEqual(journal.read_bytes(), saved_journal)
        self.assertFalse(self.manager.sessions.root.exists(),
                         "Read-only totals must not start a Chrome session.")

    def test_damaged_saved_batch_fails_closed_without_hiding_sibling_lane(self):
        """Native Windows status must show a recoverable warning, not HTTP 500.

        Historically a syntactically valid JSON list containing null/string
        entries threw AttributeError inside _pending_review. A malformed
        active cohort could also throw KeyError/TypeError in batch_review.
        All original files must remain byte-for-byte unchanged.
        """
        self.manager.configure(config())
        first = self.manager.workspaces[A]["robot"]
        second = self.manager.workspaces[B]["robot"]
        bad_file = first._review_batches_file_for(OWNER, A, "unfollow")
        good_file = second._review_batches_file_for(OWNER, B, "cancel")
        good = {"id": "second-saved", "targets": ["second.pending"],
                "approved_at": None, "recheck_results": {}}
        _atomic_json(good_file, [good])
        good_bytes = good_file.read_bytes()
        valid = {"id": "first-saved", "targets": ["first.pending"],
                 "approved_at": None, "recheck_results": {}}
        malformed = (
            [None],                         # valid JSON, invalid batch record
            [valid, "previous-damaged"],    # older/wrongly typed row not skipped
            [{"id": "bad-targets", "targets": "first.pending"}],
            [{"id": "missing-targets", "approved_at": None}],
            [{"id": "duplicates", "targets": ["first.pending", "first.pending"]}],
        )
        for rows in malformed:
            with self.subTest(saved=rows):
                _atomic_json(bad_file, rows)
                original = bad_file.read_bytes()
                snapshot = self.manager.status(OWNER)
                lanes = {row["account"]: row for row in snapshot["lanes"]}
                self.assertEqual(lanes[A]["saved_batches"], [{
                    "task": "unfollow", "unverifiable": True,
                    "requires_manual_review": True,
                    "source": "saved_local_action_journal",
                }])
                self.assertEqual(lanes[B]["saved_batches"][0]["batch_id"],
                                 "second-saved")
                self.assertEqual(lanes[B]["saved_batches"][0]["untouched"], 1)
                self.assertNotIn("first.pending", str(snapshot))
                with self.assertRaises(ValueError):
                    self.manager.review_one(
                        {"owner": OWNER, "account": A, "task": "unfollow"})
                self.assertEqual(bad_file.read_bytes(), original)
                self.assertEqual(good_file.read_bytes(), good_bytes)
                self.assertFalse(self.sessions.root.exists(),
                                 "Recovering status may not start Chrome.")
                self.assertFalse(any(self.manager._alive(lane["robot"])
                                     for lane in self.manager.workspaces.values()))

    def test_restart_rejects_corrupted_or_cross_owner_links_without_starting(self):
        binding = self.manager._binding_file(OWNER)
        valid = {"version": 1, "owner": OWNER,
                 "primary": {"account": A, "expected_handle": "first.person"},
                 "secondary": {"account": B, "expected_handle": "second.person"}}
        reopened = DualActionWorkspaces(
            DualChromeSessions(self.root / "browser"), self.collector,
            self.collector.data_dir, self.legacy)
        self.addCleanup(reopened.shutdown)
        for bad in (
            {**valid, "owner": "u_other_44"},
            {**valid, "secondary": {"account": B, "expected_handle": "first.person"}},
            {**valid, "secondary": {"account": A, "expected_handle": "second.person"}},
            {**valid, "confirmation": "cancel:1"},
            {**valid, "version": 2},
            {**valid, "primary": {"account": "../../evil", "expected_handle": "first.person"}},
        ):
            with self.subTest(saved=bad):
                _atomic_json(binding, bad)
                with self.assertRaises(ValueError):
                    reopened.status(OWNER)
                self.assertIsNone(reopened.owner)
                self.assertEqual(reopened.workspaces, {})
                self.assertFalse(self.collector.data_dir.exists())
                self.assertFalse(self.sessions.root.exists())
        binding.write_text("{broken json", encoding="utf-8")
        with self.assertRaises(ValueError):
            reopened.status(OWNER)
        self.assertIsNone(reopened.owner)
        self.assertFalse(reopened._restored_from_disk)

    def test_binding_write_failure_never_claims_configured_accounts(self):
        with patch("dual_action_workspaces._atomic_json",
                   side_effect=OSError("disk is unavailable")):
            with self.assertRaises(OSError):
                self.manager.configure(config())
        self.assertIsNone(self.manager.owner)
        self.assertEqual(self.manager.workspaces, {})
        self.assertFalse(self.sessions.root.exists())

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

    def test_real_http_bridge_restores_two_identities_after_native_restart(self):
        """New process, new token and server: GET only must rebind both accounts."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def launch(token):
                server = build_server(
                    Collector(root / "data", root / "browser-legacy"), token, 0)
                thread = threading.Thread(target=server.serve_forever, daemon=True)
                thread.start()
                return server, thread
            def query(server, token, url, payload=None):
                req = urllib.request.Request(
                    "http://127.0.0.1:" + str(server.server_port) + url,
                    data=json.dumps(payload).encode() if payload is not None else None,
                    method="POST" if payload is not None else "GET",
                    headers={"X-IGC-Bridge-Token": token, "Origin": "null",
                             "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    return json.load(response)
            first, old_thread = launch("old-process-token")
            try:
                result = query(first, "old-process-token",
                    "/api/actions/dual-action-workspaces/configure", config())
                self.assertTrue(result["two_workspaces"])
            finally:
                first.shutdown()
                first.server_close()
                old_thread.join(5)

            second, new_thread = launch("fresh-process-token")
            try:
                status = query(second, "fresh-process-token",
                               "/api/actions/dual-action-workspaces/status?owner=" + OWNER)
                self.assertEqual(status["owner"], OWNER)
                self.assertTrue(status["bindings_restored_from_disk"])
                self.assertTrue(status["two_workspaces"])
                self.assertEqual([lane["account"] for lane in status["lanes"]], [A, B])
                self.assertFalse(status["parallel_mutations_enabled"])
                self.assertTrue(all(not lane["running"] for lane in status["lanes"]))
                self.assertIsNone(second.dual_action_workspaces.workspaces[A]["robot"].worker)
                self.assertFalse(list((root / "data").glob("instagram-actions-*.json")))
                with self.assertRaises(urllib.error.HTTPError) as forbidden:
                    query(second, "old-process-token",
                          "/api/actions/dual-action-workspaces/status?owner=" + OWNER)
                self.assertEqual(forbidden.exception.code, 403)
                with self.assertRaises(urllib.error.HTTPError) as other:
                    query(second, "fresh-process-token",
                          "/api/actions/dual-action-workspaces/status?owner=u_other_42")
                self.assertEqual(other.exception.code, 400)
            finally:
                second.shutdown()
                second.server_close()
                new_thread.join(5)

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
