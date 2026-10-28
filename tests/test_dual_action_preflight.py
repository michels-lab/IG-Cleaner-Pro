"""Offline regression for two owner/account-bound action plans without ANY clicks."""
import json
import tempfile
import threading
import urllib.error
import urllib.request
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from dual_action_preflight import DualActionPreflight
from dual_chrome_sessions import DualChromeSessions
from profile_actions import ActionRobot, _atomic_json
from profile_counts_bridge import Collector, build_server

OWNER = "u_owner_42"
FIRST = "ig_first_1234567"
SECOND = "ig_second_123456"


def request():
    return {
        "owner": OWNER, "read_only_consent": True,
        "confirmation": "dual-action-preflight:" + FIRST + ":" + SECOND,
        "primary": {
            "account": FIRST, "expected_handle": "first_person", "task": "unfollow",
            "targets": ["alpha_1", "beta_2"],
        },
        "secondary": {
            "account": SECOND, "expected_handle": "second_person", "task": "cancel",
            "targets": ["alpha_1", "gamma_3"],
        },
    }


class OfflineDualActionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.actions = ActionRobot(None, self.root / "journal", self.root / "legacy-chrome")
        self.preflight = DualActionPreflight(
            DualChromeSessions(self.root / "browser-profiles"), self.actions)

    def test_two_distinct_accounts_have_independent_candidate_counts_and_no_writes(self):
        result = self.preflight.inspect(request())
        self.assertFalse(result["actions_enabled"])
        self.assertFalse(result["can_launch_parallel_unfollow"])
        self.assertEqual(result["status"], "read_only_snapshot")
        self.assertEqual(len(result["lanes"]), 2)
        self.assertEqual({lane["account"] for lane in result["lanes"]}, {FIRST, SECOND})
        for lane in result["lanes"]:
            self.assertEqual(lane["evidence_counts"]["untouched"], 2)
            self.assertTrue(lane["offline_untouched_only"])
            self.assertIn("independent_mutation_WAL_and_cross_process_admission",
                          lane["missing_verification"])
        self.assertFalse((self.root / "journal").exists(),
                         "Offline analysis must not create/approve action journals.")
        self.assertFalse((self.root / "browser-profiles").exists(),
                         "Offline analysis must not initialize/login to Chrome.")

    def test_protected_and_visited_targets_never_reenter_new_cohort(self):
        _atomic_json(self.actions._protection_file_for(OWNER, FIRST), ["alpha_1"])
        _atomic_json(self.actions._target_visits_file_for(OWNER, FIRST, "unfollow"),
                     {"beta_2": {"state": "target_navigation_reserved_not_action_confirmed"}})
        result = self.preflight.inspect(request())
        by_acc = {x["account"]: x for x in result["lanes"]}
        self.assertEqual(by_acc[FIRST]["evidence_counts"]["protected"], 1)
        self.assertEqual(by_acc[FIRST]["evidence_counts"]["previously_inspected"], 1)
        self.assertEqual(by_acc[FIRST]["evidence_counts"]["untouched"], 0)
        self.assertEqual(by_acc[SECOND]["evidence_counts"]["untouched"], 2)
        self.assertEqual([r["offline_evidence"] for r in by_acc[FIRST]["targets"]],
                         ["protected", "previously_inspected"])

    def test_uncertain_click_and_unresolved_cohort_block_automatic_reuse(self):
        _atomic_json(self.actions._base_for(OWNER, FIRST, "unfollow"),
                     {"alpha_1": {"status": "review", "issue": "interrupted_action_uncertain",
                                   "click_intent": {"phase": "relationship_control"}}})
        _atomic_json(self.actions._review_batches_file_for(OWNER, SECOND, "cancel"),
                     [{"id": "saved-cohort-44", "targets": ["older_1"]}])
        result = self.preflight.inspect(request())
        by_acc = {x["account"]: x for x in result["lanes"]}
        self.assertEqual(by_acc[FIRST]["targets"][0]["offline_evidence"], "uncertain_action")
        self.assertEqual(by_acc[FIRST]["targets"][1]["offline_evidence"], "untouched")
        self.assertTrue(by_acc[SECOND]["unresolved_saved_cohort"])
        self.assertEqual(by_acc[SECOND]["evidence_counts"]["pending_cohort"], 2)
        self.assertEqual(by_acc[SECOND]["saved_cohort_id"], "saved-cohort-44")
        self.assertFalse(by_acc[SECOND]["actions_enabled"])

    def test_invalid_history_blocks_both_not_partially_approves(self):
        _atomic_json(self.actions._base_for(OWNER, FIRST, "unfollow"),
                     {"alpha_1": {"status": "ok", "click_intent":
                                  {"phase": "relationship_control"}}})
        with self.assertRaisesRegex(ValueError, "malformed"):
            self.preflight.inspect(request())
        # A malformed unrelated *selected account* must likewise block all.
        _atomic_json(self.actions._base_for(OWNER, FIRST, "unfollow"), {})
        path = self.actions._target_visits_file_for(OWNER, SECOND, "cancel")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{malformed JSON", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Corrupted"):
            self.preflight.inspect(request())

    def test_wrong_owner_same_account_duplicate_invalid_targets_and_consent_denied(self):
        src = request()
        bad = [
            {"owner": "not_a_signed_in_owner"},
            {"read_only_consent": False},
            {"confirmation": "dual-action-preflight:wrong"},
            {"secondary": {**src["secondary"], "account": FIRST}},
            {"secondary": {**src["secondary"], "expected_handle": "first_person"}},
            {"primary": {**src["primary"], "targets": ["alpha_1", "alpha_1"]}},
            {"primary": {**src["primary"], "targets": ["ABC", "alpha_1"]}},
            {"primary": {**src["primary"], "targets": ["alpha_1"], "task": "audit"}},
        ]
        for changes in bad:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.preflight.inspect({**src, **changes})

    def test_owner_approved_action_cannot_be_started_from_preflight_snapshot(self):
        source = request()
        result = self.preflight.inspect(source)
        self.assertFalse(result["actions_enabled"])
        self.assertFalse(result["can_launch_parallel_unfollow"])
        self.assertNotIn("confirmation", result)
        self.assertNotIn("token", json.dumps(result).lower())
        self.assertNotIn("password", json.dumps(result).lower())


class DualActionBridgeContractTests(unittest.TestCase):
    def test_local_api_is_token_bound_read_only_and_inaccessible_in_developer_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            server = build_server(Collector(base / "data", base / "browser"),
                                  "test-token", 0)
            listener = threading.Thread(target=server.serve_forever, daemon=True)
            listener.start()
            url = "http://127.0.0.1:" + str(server.server_port)
            def post(payload, token="test-token", path="/api/actions/dual-robots/preflight"):
                body = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url + path, data=body,
                    headers={"Origin": "null", "Content-Type": "application/json",
                             "X-IGC-Bridge-Token": token},
                    method="POST")
                with urllib.request.urlopen(req, timeout=5) as response:
                    return json.load(response)
            try:
                with self.assertRaises(urllib.error.HTTPError) as err:
                    post(request(), token="wrong")
                self.assertEqual(err.exception.code, 403)
                state = post(request())
                self.assertFalse(state["actions_enabled"])
                self.assertEqual(len(state["lanes"]), 2)
                self.assertFalse(list((base / "data").glob("instagram-actions-*.json")))
                with self.assertRaises(urllib.error.HTTPError) as rejected:
                    post({**request(), "owner": "evil"})
                self.assertEqual(rejected.exception.code, 400)
            finally:
                server.shutdown()
                server.server_close()
                listener.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
