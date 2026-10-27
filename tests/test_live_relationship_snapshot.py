"""Complete current Instagram relationship lists, no ZIP and no mutations.

Offline ONLY: simulated pages and local loopback; no live Instagram requests.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch, call
from types import ModuleType

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.live_relationship_snapshot import LiveRelationships
from tools.profile_actions import _atomic_json


class LiveRelationshipSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.collector=MagicMock()
        import threading
        self.collector.browser_admission=threading.RLock()
        self.collector.worker=None
        self.actions=MagicMock()
        self.actions.worker=None
        self.robot=LiveRelationships(self.collector,self.actions,self.root/"data",self.root/"session")
        self.scope={"owner":"app-user","account":"ig-account"}
        self.robot.owner,self.robot.account,self.robot.handle="app-user","ig-account","my.account"

    def tearDown(self):
        self.temp.cleanup()

    def sample(self):
        _atomic_json(self.robot._file_for(**self.scope),{
          "schema":"igc-live-relationships-v1","complete":True,
          "expected_handle":"my.account","captured_at":"2026-10-27T11:00:00Z",
          "read_only":True,"lists":{
            "followers":["a","b","c"],"following":["b","c","d","e"],
            "not_following_back":["d","e"],"fans":["a"]}})

    def test_complete_paginated_and_owner_scoped_without_zip(self):
        self.sample()
        a=self.robot.results({**self.scope,"list":"not_following_back","offset":0,"limit":1})
        self.assertEqual(a["usernames"],["d"])
        self.assertTrue(a["has_next"])
        self.assertEqual(a["totals"]["followers"],3)
        self.assertEqual(a["totals"]["following"],4)
        self.assertFalse(a["complete"]) # historic snapshot is NOT guaranteed current
        self.assertTrue(a["last_verified"])
        b=self.robot.results({**self.scope,"list":"not_following_back","offset":1,"limit":1})
        self.assertEqual(b["usernames"],["e"])
        self.assertFalse(b["has_next"])
        other=self.robot.results({"owner":"another-app-owner","account":"ig-account","list":"followers"})
        self.assertFalse(other["last_verified"])
        self.assertEqual(other["usernames"],[])
        self.assertFalse(other["complete"])

    def test_no_invalid_kind_large_page_or_cross_account_active_scan(self):
        self.sample()
        for change in ({"list":"unfollow"},{"limit":300},{"offset":-1},{"limit":True}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.robot.results({**self.scope,**change})
        self.robot.worker=MagicMock()
        self.robot.worker.is_alive.return_value=True
        with self.assertRaises(ValueError):
            self.robot.results({"owner":"another-app-owner","account":"ig-account"})

    def test_start_requires_owner_consent_and_chrome_exclusivity(self):
        params={**self.scope,"expected_handle":"my.account",
                "read_only_consent":True,"confirmation":"live-relationships:my.account"}
        with self.assertRaises(ValueError):
            self.robot.start({**params,"read_only_consent":False})
        with self.assertRaises(ValueError):
            self.robot.start({**params,"confirmation":"audit:1"})
        with patch("tools.live_relationship_snapshot.ActionLease") as lease:
            lease.return_value.acquire.return_value=MagicMock()
            self.actions.worker=MagicMock()
            self.actions.worker.is_alive.return_value=True
            with self.assertRaises(ValueError):
                self.robot.start(params)
            self.actions.worker=None
            self.collector.worker=MagicMock()
            self.collector.worker.is_alive.return_value=True
            with self.assertRaises(ValueError):
                self.robot.start(params)
            self.collector.worker=None
            with patch("tools.live_relationship_snapshot.threading.Thread") as thread:
                resp=self.robot.start(params)
                self.assertEqual(resp["status"],"starting")
                self.assertFalse(resp["relationship_action"])
                self.assertTrue(thread.return_value.start.called)

    def _run_fake(self,first,second):
        browser=MagicMock()
        tab=MagicMock()
        tab.is_closed.return_value=False
        tab.url="https://www.instagram.com/"
        browser.pages=[tab]
        pw=MagicMock()
        pw.chromium.launch_persistent_context.return_value=browser
        cm=MagicMock()
        cm.__enter__.return_value=pw
        api=ModuleType("playwright.sync_api")
        api.sync_playwright=lambda:cm
        pkg=ModuleType("playwright")
        pkg.sync_api=api
        with patch.dict(sys.modules,{"playwright":pkg,"playwright.sync_api":api}), \\
             patch("tools.live_relationship_snapshot.preserve_instagram_auth_page",return_value=True), \\
             patch("tools.live_relationship_snapshot._find_verified_owner_tab",return_value=(tab,None)), \\
             patch("tools.live_relationship_snapshot.read_live_friendship_list",side_effect=[first,second]) as read:
            self.robot._run()
        return read

    def test_complete_lists_prove_negative_and_preserve_original_action_records(self):
        record=self.root/"data"/"action-journal-existing.json"
        _atomic_json(record,{"x":{"status":"review","click_intent":{"phase":"relationship_control"}}})
        read=self._run_fake(frozenset(("alice","bob","mutual")),
                            frozenset(("bob","mutual","carol")))
        self.assertEqual(read.call_count,2)
        self.assertEqual([x.args[2] for x in read.call_args_list],["followers","following"])
        self.assertEqual(self.robot.status,"complete")
        result=self.robot.results({**self.scope,"list":"not_following_back"})
        self.assertEqual(result["usernames"],["carol"])
        self.assertEqual(self.robot.results({**self.scope,"list":"fans"})["usernames"],["alice"])
        self.assertTrue(result["complete"])
        self.assertEqual(json.loads(record.read_text())["x"]["status"],"review")
        self.assertTrue(json.loads(record.read_text())["x"]["click_intent"])

    def test_failure_in_following_keeps_last_complete_historical_without_false_new_result(self):
        self.sample()
        self._run_fake(frozenset(("a","b")),RuntimeError("429 rate limited"))
        self.assertEqual(self.robot.status,"blocked")
        prior=self.robot.results({**self.scope,"list":"not_following_back"})
        self.assertEqual(prior["usernames"],["d","e"])
        self.assertFalse(prior["complete"])
        self.assertEqual(prior["captured_at"],"2026-10-27T11:00:00Z")
        self.assertIn("historical",self.robot.message.lower())

    def test_owner_pause_preserves_last_complete(self):
        self.sample()
        self.robot.stop_event.set()
        self._run_fake(frozenset(("x",)),frozenset(("x",)))
        self.assertEqual(self.robot.status,"paused")
        self.assertEqual(self.robot.results({**self.scope,"list":"followers"})["usernames"],["a","b","c"])


if __name__=="__main__":
    unittest.main()
