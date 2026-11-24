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
        self.valid["next_version"]=self.current["next_version"]
        self.valid["critical_acceptance"]={name:True for name in REQUIRED_ACCEPTANCE}
        self.valid["owner_final_acceptance"]={
          "approved":True,"release_tag":self.current["next_version"],
          "evidence":"owner-provided explicit post-install real-world sign-off"
        }
        self.closed={n:"closed" for n in self.valid["required_closed_issues"]}

    def test_consumed_publication_history_and_explicit_next_release_override(self):
        self.assertTrue(self.current['release_hold'])
        self.assertFalse(self.current['owner_final_acceptance']['approved'])
        next_tag = self.current['next_version']
        override = self.current['owner_device_review_release_override']
        history = self.current['owner_device_review_release_override_history']
        consumed = [item for item in history if item.get('release_tag') == 'v120.79']
        self.assertEqual(len(consumed), 1)
        self.assertTrue(any(x.get('consumed_by_release') == 'v120.80' and x.get('authorized') is False for x in history),
          'The earlier stable review authorization must remain consumed in history')
        self.assertIs(consumed[0]['authorized'], False)
        self.assertEqual(consumed[0]['consumed_by_release'], 'v120.79')
        self.assertEqual(consumed[0]['consumed_run'], 44204338029)
        self.assertTrue(override['physical_tests_deferred'])
        prior = [item for item in history if item.get('release_tag') == 'v120.81']
        self.assertEqual(len(prior), 1)
        self.assertIs(prior[0]['authorized'], False)
        self.assertEqual(prior[0]['consumed_by_release'], 'v120.81')
        self.assertEqual(prior[0]['consumed_run'], 45319438358)
        self.assertTrue(override['automated_publisher_gates_required'])
        self.assertEqual(override['source'], 'explicit-owner-chat-instruction-2026-11-24')
        request = json.loads((ROOT/'.michelslab/release-request.json').read_text(encoding='utf-8'))
        active = request.get('authorized') is True and request.get('status') in ('requested', 'authorized')
        if active:
            self.assertEqual(request['tag'], next_tag)
            self.assertTrue(override['authorized'])
            self.assertEqual(override['release_tag'], next_tag)
            self.assertEqual(override['owner_direct_quote'], 'dale release perra')
            check_readiness(self.current, next_tag, {})
            self.assertEqual(override['release_tag'], 'v120.82')
            forged = deepcopy(self.current)
            forged['owner_device_review_release_override']['release_tag'] = 'v120.77'
            with self.assertRaises(ReleaseBlocked):
                check_readiness(forged, next_tag, {})
        else:
            self.assertFalse(override['authorized'])
            with self.assertRaises(ReleaseBlocked):
                check_readiness(self.current, next_tag, {})
        for old in ('v120.76', 'v120.77', 'v120.78', 'v120.79', 'v120.80', 'v120.81'):
            if old == next_tag:
                continue
            with self.subTest(old_tag=old), self.assertRaises(ReleaseBlocked):
                check_readiness(self.current, old, {})
        self.assertTrue(any(not value for value in self.current['critical_acceptance'].values()))
        if request.get('status') == 'published':
            self.assertEqual(request.get('tag'), 'v120.81')
            self.assertEqual(self.current['next_version'], 'v120.82')
            self.assertEqual(request.get('published_commit'), 'fc1cd03a476dc4c5797e90e89e18d22733c34175')
            self.assertEqual(request.get('published_run'), 45319438358)
            self.assertEqual(override.get('consumed_by_release'), request['tag'])
            self.assertEqual(override.get('consumed_run'), request['published_run'])

    def test_green_ci_does_not_override_owner_hold(self):
        case=deepcopy(self.valid)
        case["release_hold"]=True
        with self.assertRaises(ReleaseBlocked):
            check_readiness(case,self.current["next_version"],self.closed)

    def test_missing_or_partial_owner_acceptance_blocks(self):
        for approval in (None,{},{"approved":False,"release_tag":self.current["next_version"],"evidence":"x"*16}):
            case=deepcopy(self.valid);case["owner_final_acceptance"]=approval
            with self.subTest(approval=approval),self.assertRaises(ReleaseBlocked):
                check_readiness(case,self.current["next_version"],self.closed)

    def test_any_unverified_product_critical_acceptance_blocks(self):
        for item in REQUIRED_ACCEPTANCE:
            case=deepcopy(self.valid);case["critical_acceptance"][item]=False
            with self.subTest(item=item),self.assertRaisesRegex(ReleaseBlocked,"acceptance incomplete"):
                check_readiness(case,self.current["next_version"],self.closed)

    def test_open_or_unverified_issue_blocks(self):
        for number in self.valid["required_closed_issues"]:
            for value in ("open",None):
                states=dict(self.closed)
                if value:states[number]=value
                else:states.pop(number)
                with self.subTest(issue=number,value=value),self.assertRaisesRegex(ReleaseBlocked,f"Issue #{number}"):
                    check_readiness(self.valid,self.current["next_version"],states)

    def test_cannot_drop_blocker_from_release_gate(self):
        for n in (164,172,173,176):
            case=deepcopy(self.valid);case["required_closed_issues"].remove(n)
            with self.subTest(issue=n),self.assertRaisesRegex(ReleaseBlocked,"weaker than P0"):
                check_readiness(case,self.current["next_version"],self.closed)

    def test_owner_acceptance_for_wrong_version_never_works(self):
        with self.assertRaisesRegex(ReleaseBlocked,"does not match"):
            check_readiness(self.valid,"v120.77",self.closed)
        case=deepcopy(self.valid)
        case["owner_final_acceptance"]["release_tag"]="v120.77"
        with self.assertRaises(ReleaseBlocked):
            check_readiness(case,self.current["next_version"],self.closed)

    def test_official_publisher_verifies_authorization_twice(self):
        workflow=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
        cmd="tools/release_readiness_gate.py"
        self.assertGreaterEqual(workflow.count(cmd),2)
        self.assertGreater(workflow.rfind(cmd,0,workflow.index('gh release create "$TAG"')),workflow.index("if enabled:"))
        self.assertIn("issues: read",workflow)
        self.assertIn("GH_TOKEN:",workflow)

    def test_finished_app_requires_all_closed_issues_and_authorization(self):
        check_readiness(self.valid,self.current["next_version"],self.closed)

if __name__=="__main__":
    unittest.main()
