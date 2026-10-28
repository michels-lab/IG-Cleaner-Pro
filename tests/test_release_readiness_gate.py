"""No release while real owner features are incomplete, regardless of CI status."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from release_readiness_gate import ReleaseBlocked, REQUIRED_ACCEPTANCE, check_readiness

CONFIG_PATH = ROOT / "release" / "release-readiness.json"


class OwnerCompletionReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.current = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        self.valid = deepcopy(self.current)
        self.valid["release_hold"] = False
        self.valid["next_version"] = "v120.72"
        self.valid["critical_acceptance"] = {name: True for name in REQUIRED_ACCEPTANCE}
        self.valid["owner_final_acceptance"] = {
            "approved": True,
            "release_tag": "v120.72",
            "evidence": "owner-provided explicit post-install real-world sign-off",
        }
        self.closed = {n: "closed" for n in self.valid["required_closed_issues"]}

    def test_current_repo_is_under_hard_release_hold(self):
        self.assertTrue(self.current["release_hold"])
        self.assertIs(self.current["owner_final_acceptance"]["approved"], False)
        with self.assertRaisesRegex(ReleaseBlocked, "RELEASE BLOCKED BY OWNER"):
            check_readiness(self.current, "v120.72", self.closed)

    def test_green_ci_does_not_override_owner_hold(self):
        ready = deepcopy(self.valid)
        ready["release_hold"] = True
        with self.assertRaises(ReleaseBlocked):
            check_readiness(ready, "v120.72", self.closed)

    def test_missing_or_partial_owner_acceptance_blocks(self):
        for approval in (None, {}, {"approved": False, "release_tag": "v120.72", "evidence": "x" * 16}):
            with self.subTest(approval=approval), self.assertRaises(ReleaseBlocked):
                candidate = deepcopy(self.valid)
                candidate["owner_final_acceptance"] = approval
                check_readiness(candidate, "v120.72", self.closed)

    def test_any_unverified_product_critical_acceptance_blocks(self):
        for name in REQUIRED_ACCEPTANCE:
            with self.subTest(check=name), self.assertRaisesRegex(ReleaseBlocked, "acceptance incomplete"):
                candidate = deepcopy(self.valid)
                candidate["critical_acceptance"][name] = False
                check_readiness(candidate, "v120.72", self.closed)

    def test_open_or_unverifiable_issue_blocks_release(self):
        for issue in self.valid["required_closed_issues"]:
            with self.subTest(issue=issue), self.assertRaisesRegex(ReleaseBlocked, f"Issue #{issue}"):
                state = dict(self.closed)
                state[issue] = "open"
                check_readiness(self.valid, "v120.72", state)
            with self.subTest(issue=issue, missing=True), self.assertRaisesRegex(ReleaseBlocked, f"Issue #{issue}"):
                state = dict(self.closed)
                state.pop(issue)
                check_readiness(self.valid, "v120.72", state)

    def test_cannot_drop_p0_issue_from_release_gate(self):
        for issue in (164, 172, 173, 176):
            candidate = deepcopy(self.valid)
            candidate["required_closed_issues"].remove(issue)
            with self.subTest(issue=issue), self.assertRaisesRegex(ReleaseBlocked, "weaker than P0"):
                check_readiness(candidate, "v120.72", self.closed)

    def test_owner_acceptance_for_wrong_version_never_works(self):
        with self.assertRaisesRegex(ReleaseBlocked, "does not match"):
            check_readiness(self.valid, "v120.73", self.closed)
        candidate = deepcopy(self.valid)
        candidate["owner_final_acceptance"]["release_tag"] = "v120.73"
        with self.assertRaises(ReleaseBlocked):
            check_readiness(candidate, "v120.72", self.closed)

    def test_official_publisher_requires_live_completion_twice(self):
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        cmd = "tools/release_readiness_gate.py"
        self.assertGreaterEqual(workflow.count(cmd), 2,
                                "Require owner approval before build AND immediately before gh release create.")
        gate = workflow.index("if enabled:")
        publish = workflow.index('gh release create "$TAG"')
        final_check = workflow.rfind(cmd, 0, publish)
        self.assertGreater(final_check, gate)
        self.assertGreater(publish, final_check)
        self.assertIn("issues: read", workflow)
        self.assertIn("GH_TOKEN:", workflow)

    def test_release_needs_all_three_separate_proofs(self):
        # Positive test is explicitly isolated; never flips real repo hold.
        check_readiness(self.valid, "v120.72", self.closed)


if __name__ == "__main__":
    unittest.main()
