"""Loopback live follower snapshot routes: auth, isolation and no hidden mutation.

No Instagram navigation, credentials or relationship modification.
"""
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from profile_counts_bridge import Collector, build_server
from profile_actions import _atomic_json


class LiveBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)
        self.collector=Collector(root/"data",root/"session")
        self.server=build_server(self.collector,"local-test-token")
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
        self.url="http://127.0.0.1:"+str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.temp.cleanup()

    def request(self,route,data=None,token="local-test-token",origin="null"):
        headers={"X-IGC-Bridge-Token":token,"Origin":origin}
        if data is not None:headers["Content-Type"]="application/json"
        req=Request(self.url+route,
                    data=json.dumps(data).encode() if data is not None else None,
                    headers=headers,
                    method="POST" if data is not None else "GET")
        with urlopen(req,timeout=6) as response:
            return json.loads(response.read())

    def test_no_session_token_or_wrong_origin(self):
        params={"owner":"app","account":"instagram","list":"followers"}
        with self.assertRaises(HTTPError) as bad:
            self.request("/api/actions/live-results",params,token="incorrect")
        self.assertEqual(bad.exception.code,403)
        with self.assertRaises(HTTPError) as bad:
            self.request("/api/actions/live-results",params,origin="https://elsewhere.example")
        self.assertEqual(bad.exception.code,403)

    def test_full_scoped_pagination_through_actual_local_api(self):
        robot=self.collector.live_relationships
        _atomic_json(robot._file_for("app","instagram"),{
            "schema":"igc-live-relationships-v1","complete":True,
            "captured_at":"2026-10-27T09:00:00Z","expected_handle":"owner.name",
            "lists":{"followers":["a","b"],"following":["b","c","d"],
                     "not_following_back":["c","d"],"fans":["a"]}})
        params={"owner":"app","account":"instagram","list":"not_following_back","offset":1,"limit":1}
        current=self.request("/api/actions/live-results",params)
        self.assertEqual(current["usernames"],["d"])
        self.assertEqual(current["totals"]["followers"],2)
        self.assertFalse(current["complete"])
        self.assertTrue(current["last_verified"])
        other=self.request("/api/actions/live-results",{**params,"account":"instagram2"})
        self.assertEqual(other["usernames"],[])
        self.assertFalse(other["last_verified"])

    def test_explicit_consent_and_one_job_only(self):
        params={"owner":"app","account":"instagram","expected_handle":"owner.name"}
        with self.assertRaises(HTTPError) as no_consent:
            self.request("/api/actions/live-start",params)
        self.assertEqual(no_consent.exception.code,400)
        with patch("live_relationship_snapshot.ActionLease") as lease, \
             patch.object(self.collector.live_relationships,"_run_with_lease") as run:
            lease.return_value.acquire.return_value=MagicMock()
            yes={**params,"read_only_consent":True,"confirmation":"live-relationships:owner.name"}
            r=self.request("/api/actions/live-start",yes)
            self.assertEqual(r["status"],"starting")
            self.assertFalse(r["relationship_action"])
            self.assertEqual(r["expected_handle"],"owner.name")
            # An already finished fake worker cannot mutate or visit Instagram.
            # The result is a start receipt, not a proof of a completed snapshot.
            self.assertFalse(self.request("/api/actions/live-results",{
                "owner":"app","account":"instagram"})["last_verified"])

if __name__=="__main__":
    unittest.main()
