"""Owner-directed release is single-use; source green never authorizes future tags."""
import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from release_readiness_gate import ReleaseBlocked,REQUIRED_ACCEPTANCE,check_readiness

CONFIG=ROOT/"release"/"release-readiness.json"

class OwnerCompletionReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.current=json.loads(CONFIG.read_text(encoding="utf-8"))
        self.valid=deepcopy(self.current)
        self.valid.pop("owner_device_review_release_override",None)
        self.valid["release_hold"]=False
        self.valid["next_version"]="v120.77"
        self.valid["critical_acceptance"]={name:True for name in REQUIRED_ACCEPTANCE}
        self.valid["owner_final_acceptance"]={
          "approved":True,"release_tag":"v120.77",
          "evidence":"owner-provided explicit post-install real-world sign-off"
        }
        self.closed={n:"closed" for n in self.valid["required_closed_issues"]}

    def test_owner_instruction_is_exact_tag_device_review_only(self):
        self.assertTrue(self.current["release_hold"])
        self.assertFalse(self.current["owner_final_acceptance"]["approved"])
        override=self.current["owner_device_review_release_override"]
        self.assertTrue(override["authorized"],"New owner direction applies to v120.77 only")
        self.assertEqual(override["release_tag"],"v120.77")
        self.assertTrue(override["physical_tests_deferred"])
        self.assertTrue(override["automated_publisher_gates_required"])
        self.assertFalse(self.current["owner_device_review_release_override_history"][-1]["authorized"])
        self.assertEqual(self.current["owner_device_review_release_override_history"][-1]["release_tag"],"v120.76")
        check_readiness(self.current,"v120.77",{})
        for tag in ("v120.76","v120.78"):
            with self.subTest(tag=tag),self.assertRaises(ReleaseBlocked):
                check_readiness(self.current,tag,{})
        attempt=deepcopy(self.current)
        attempt["owner_device_review_release_override"]["authorized"]=False
        with self.assertRaises(ReleaseBlocked):
            check_readiness(attempt,"v120.77",{})
        self.assertTrue(any(not value for value in self.current["critical_acceptance"].values()))

    def test_green_ci_does_not_override_owner_hold(self):
        case=deepcopy(self.valid)
        case["release_hold"]=True
        with self.assertRaises(ReleaseBlocked):
            check_readiness(case,"v120.77",self.closed)

    def test_missing_or_partial_owner_acceptance_blocks(self):
        for approval in (None,{},{"approved":False,"release_tag":"v120.77","evidence":"x"*16}):
            case=deepcopy(self.valid);case["owner_final_acceptance"]=approval
            with self.subTest(approval=approval),self.assertRaises(ReleaseBlocked):
                check_readiness(case,"v120.77",self.closed)

    def test_any_unverified_product_critical_acceptance_blocks(self):
        for item in REQUIRED_ACCEPTANCE:
            case=deepcopy(self.valid);case["critical_acceptance"][item]=False
            with self.subTest(item=item),self.assertRaisesRegex(ReleaseBlocked,"acceptance incomplete"):
                check_readiness(case,"v120.77",self.closed)

    def test_open_or_unverified_issue_blocks(self):
        for number in self.valid["required_closed_issues"]:
            for value in ("open",None):
                states=dict(self.closed)
                if value:states[number]=value
                else:states.pop(number)
                with self.subTest(issue=number,value=value),self.assertRaisesRegex(ReleaseBlocked,f"Issue #{number}"):
                    check_readiness(self.valid,"v120.77",states)

    def test_cannot_drop_blocker_from_release_gate(self):
        for n in (164,172,173,176):
            case=deepcopy(self.valid);case["required_closed_issues"].remove(n)
            with self.subTest(issue=n),self.assertRaisesRegex(ReleaseBlocked,"weaker than P0"):
                check_readiness(case,"v120.77",self.closed)

    def test_owner_acceptance_for_wrong_version_never_works(self):
        with self.assertRaisesRegex(ReleaseBlocked,"does not match"):
            check_readiness(self.valid,"v120.76",self.closed)
        case=deepcopy(self.valid)
        case["owner_final_acceptance"]["release_tag"]="v120.76"
        with self.assertRaises(ReleaseBlocked):
            check_readiness(case,"v120.77",self.closed)

    def test_official_publisher_verifies_authorization_twice(self):
        workflow=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
        cmd="tools/release_readiness_gate.py"
        self.assertGreaterEqual(workflow.count(cmd),2)
        self.assertGreater(workflow.rfind(cmd,0,workflow.index('gh release create "$TAG"')),workflow.index("if enabled:"))
        self.assertIn("issues: read",workflow)
        self.assertIn("GH_TOKEN:",workflow)

    def test_finished_app_requires_all_closed_issues_and_authorization(self):
        check_readiness(self.valid,"v120.77",self.closed)

if __name__=="__main__":
    unittest.main()
