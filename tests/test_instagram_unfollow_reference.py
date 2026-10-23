"""Offline contract for owner-supplied authenticated Unfollow reference.

No Instagram requests, login tokens or relationship mutation in these tests.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from instagram_unfollow_reference import (
    reference_unfollow,_REFERENCE_EXACT_FOLLOWING,_REFERENCE_UNFOLLOW_MUTATION)
from profile_actions import _action_issue, _preclick_no_action, _saved_journal_blocks_action


class FakePage:
    def __init__(self, lookup=None, mutation=None):
        self.url="https://www.instagram.com/target.user/"
        self.lookup=lookup or {"code":"EXACT_FOLLOWING_ID","id":"12345"}
        self.mutation=mutation or {"code":"MUTATION_ACCEPTED"}
        self.steps=[]
    def evaluate(self, script, params):
        stage=("GET" if script==_REFERENCE_EXACT_FOLLOWING else
               ("READY" if params.get("dryRun") else "POST"))
        self.steps.append((stage,params))
        return (self.lookup if stage=="GET" else
                {"code":"READY_TO_MUTATE"} if stage=="READY" else
                self.mutation)


class ReferenceUnfollowTests(unittest.TestCase):
    def call(self, page, *, consent=None, protect=None, verified=None, fresh=None):
        consent = consent if consent is not None else Mock(
            side_effect=lambda phase: page.steps.append(("WAL",phase)))
        protect=protect or (lambda _:True)
        verified=verified or (lambda *_:True)
        fresh=fresh or (lambda *_:("ok","Verified Follow after fresh navigation"))
        return reference_unfollow(
            page,"target.user","owner.user",can_act=protect,
            on_pre_click=consent,verify_owner=verified,
            verify_target=verified,verify_after=fresh)
    def test_exact_target_and_wal_before_a_single_post(self):
        page=FakePage()
        result=self.call(page)
        self.assertEqual(result[0],"ok")
        self.assertEqual([x[0] for x in page.steps],["GET","READY","WAL","POST"])
        self.assertEqual(page.steps[0][1],{"username":"target.user"})
        self.assertEqual(page.steps[-1][1],{"targetId":"12345","dryRun":False})
    def test_missing_identity_never_even_looks_up(self):
        page=FakePage()
        result=self.call(page,verified=lambda *_:False)
        self.assertEqual(result[0],"blocked")
        self.assertEqual(page.steps,[])
    def test_protected_target_never_looks_up_or_posts(self):
        page=FakePage()
        result=self.call(page,protect=lambda _:False)
        self.assertEqual(result[0],"skipped")
        self.assertEqual(page.steps,[])
    def test_unconfirmed_following_id_never_posts(self):
        for c in ("NO_SESSION","RATE_LIMITED","LOOKUP_UNAVAILABLE",
                  "NO_EXACT_FOLLOWING_ID","AMBIGUOUS_TARGET_ID"):
            with self.subTest(code=c):
                page=FakePage(lookup={"code":c})
                result=self.call(page)
                self.assertIn(result[0],("blocked","review"))
                self.assertEqual([x[0] for x in page.steps],["GET"])
    def test_mutation_must_verify_fresh_follow_and_no_false_success(self):
        page=FakePage()
        result=self.call(page,fresh=lambda *_:("review","Still Following after reload"))
        self.assertEqual(result[0],"review")
        self.assertEqual([x[0] for x in page.steps],["GET","READY","WAL","POST"])
    def test_uncertain_result_never_fallbacks_to_second_click(self):
        for code in ("ACTION_BLOCKED","SESSION_TOKENS_UNAVAILABLE",
                     "MUTATION_UNCERTAIN"):
            with self.subTest(code=code):
                page=FakePage(mutation={"code":code})
                result=self.call(page)
                self.assertIn(result[0],("blocked","review"))
                self.assertEqual([x[0] for x in page.steps],["GET","READY","WAL","POST"])
    def test_failed_wal_never_calls_post(self):
        page=FakePage()
        def bad(_): raise OSError("Disk full")
        with self.assertRaises(OSError):
            self.call(page,consent=bad)
        self.assertEqual([x[0] for x in page.steps],["GET","READY"])
    def test_session_readiness_refusal_keeps_journal_available(self):
        class MissingTokens(FakePage):
            def evaluate(self, script, params):
                if params.get("dryRun"):
                    self.steps.append(("READY", params))
                    return {"code":"SESSION_TOKENS_UNAVAILABLE"}
                return super().evaluate(script, params)
        page=MissingTokens()
        result=self.call(page)
        self.assertEqual(result[0],"review")
        self.assertEqual([x[0] for x in page.steps],["GET","READY"])
    def test_no_post_reference_failure_revisitable_only_on_fresh_owner_consent(self):
        cases=[
            ("review","Reference Unfollow read-only lookup: LOOKUP_UNAVAILABLE. No GraphQL request sent."),
            ("blocked","Reference Unfollow read-only lookup: RATE_LIMITED. No GraphQL request sent."),
            ("review","Reference Unfollow session preparation unavailable. No POST or write-ahead action intent; review Chrome sign-in."),
            ("blocked","Reference Unfollow: exact Instagram target or signed-in owner not verified; no action clicked."),
        ]
        for status,message in cases:
            with self.subTest(message=message):
                issue=_action_issue("unfollow",status,message)
                self.assertEqual(issue,"reference_preclick_unavailable")
                record={"status":status,"issue":issue,"message":message}
                self.assertTrue(_preclick_no_action(record))
                self.assertFalse(_saved_journal_blocks_action({"target.user":record},"target.user"))
                # An orphan intent always makes this outcome uncertain, even
                # if the human-readable message suggests no POST occurred.
                armed={**record,"click_intent":{"phase":"relationship_control",
                    "batch_id":"x","task":"unfollow","phases":["relationship_control"]}}
                self.assertFalse(_preclick_no_action(armed))
                self.assertTrue(_saved_journal_blocks_action({"target.user":armed},"target.user"))
        ambiguous={"status":"review","issue":"requires_manual_review",
                   "message":"Reference Unfollow read-only lookup: LOOKUP_UNAVAILABLE. No GraphQL request sent."}
        self.assertFalse(_preclick_no_action(ambiguous))

    def test_reference_transport_keeps_sessions_in_chrome(self):
        self.assertIn("usePolarisUnfollowMutation",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("27789106940691111",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("target_user_id:targetId",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("fetch('https://www.instagram.com/api/graphql'",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("friendship_status",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("same-origin",_REFERENCE_UNFOLLOW_MUTATION)
        self.assertIn("X-IG-App-ID",_REFERENCE_EXACT_FOLLOWING)
        self.assertNotIn("POST",_REFERENCE_EXACT_FOLLOWING)
        self.assertEqual(_REFERENCE_UNFOLLOW_MUTATION.count("method:'POST'"),1)


if __name__=="__main__":
    unittest.main()
