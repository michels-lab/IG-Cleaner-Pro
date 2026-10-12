import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_bridge import Collector, build_server


class ProfileCountsBridgeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        path = Path(self.directory.name)
        self.collector = Collector(path/"results",path/"session")
        self.server = build_server(self.collector, "unit-test-secret-token")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.directory.cleanup()

    def request(self, route, *, body=None, token="unit-test-secret-token", origin="null"):
        headers = {"X-IGC-Bridge-Token":token, "Origin":origin}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = Request(self.url+route,
                      data=json.dumps(body).encode() if body is not None else None,
                      headers=headers,
                      method="POST" if body is not None else "GET")
        with urlopen(req, timeout=4) as response:
            return json.loads(response.read().decode())

    def test_no_unauthorized_reads(self):
        with self.assertRaises(HTTPError) as e:
            self.request("/api/status", token="incorrect")
        self.assertEqual(e.exception.code, 403)
        with self.assertRaises(HTTPError) as e:
            self.request("/api/status", origin="https://other-site.example")
        self.assertEqual(e.exception.code, 403)
        self.assertEqual(self.request("/api/status")["status"], "idle")
        with self.assertRaises(HTTPError) as e:
            self.request("/api/anything")
        self.assertEqual(e.exception.code, 404)

    def test_reject_invalid_job(self):
        for body in (
            {"owner":"A","account":"first","usernames":[]},
            {"owner":"A","account":"first","usernames":["valid"],"max_per_window":0},
            {"owner":"A","account":"first","usernames":["valid"],"max_per_window":200,"window_minutes":0},
            {"owner":"A","account":"first","usernames":["valid"],"min_delay_seconds":-2},
            {"owner":"A","account":"","usernames":["valid"]},
            {"owner":"A","account":"first","usernames":["../unsafe"]},
        ):
            with self.assertRaises(HTTPError) as e:
                self.request("/api/start", body=body)
            self.assertEqual(e.exception.code, 400)

    def test_isolation_and_local_results(self):
        p=self.collector
        p.owner,p.account="user-A","ig-one"
        a=p.result_path()
        p.account="ig-two"
        b=p.result_path()
        p.owner="user-B"
        c=p.result_path()
        self.assertEqual(len({a,b,c}),3)
        self.assertNotIn("user-A", str(a))
        self.assertNotIn("ig-one", str(a))
        p.owner,p.account,p.usernames="user-A","ig-one",["some.user"]
        self.assertEqual(self.request("/api/results")["rows"],[])

    def test_load_saved_count_rows_without_starting_instagram(self):
        from profile_counts_robot import save_results
        self.collector.owner = "owner-A"
        self.collector.account = "ig-one"
        save_results(self.collector.result_path(), {
            "public.user": {
                "username":"public.user", "followers":"333", "following":"222",
                "checked_at":"2026-10-12T02:00:00+00:00",
                "source":"instagram_visible_profile_browser", "status":"ok", "approximate":"false"
            }
        })
        state = self.request("/api/load", body={
            "owner":"owner-A","account":"ig-one","usernames":["public.user","second.user"]
        })
        self.assertEqual(state["status"],"idle")
        self.assertEqual(state["progress"],1)
        self.assertEqual(state["total"],2)
        self.assertEqual(state["max_per_window"],50)
        self.assertEqual(state["window_minutes"],60)
        self.assertEqual(state["min_delay_seconds"],72)
        self.assertFalse(state["running"])
        rows = self.request("/api/results")["rows"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["followers"],"333")

    def test_autonomous_start_needs_no_csv_or_click(self):
        # Browser interaction is simulated; user credentials are never supplied.
        self.collector._run=lambda: self.collector._update("complete","Fixture finished",0)
        state=self.request("/api/auto",body={
            "owner":"owner-A","account":"ig-one","expected_handle":"my.instagram"
        })
        self.collector.worker.join(2)
        self.assertTrue(state["autonomous"])
        self.assertEqual(state["total"],0)
        self.assertEqual(self.request("/api/following")["usernames"],[])
        self.assertEqual(self.request("/api/status")["status"],"complete")

    def test_autonomous_full_pipeline_without_csv_or_manual_resume(self):
        import types
        from unittest.mock import patch
        from profile_counts_robot import read_results

        class FakePage:
            def goto(self,*args,**kwargs): pass
        class FakeBrowser:
            pages=[FakePage()]
            def close(self):pass
        class FakeSync:
            def __enter__(self):
                self.chromium=types.SimpleNamespace(
                    launch_persistent_context=lambda **kw:FakeBrowser())
                return self
            def __exit__(self,*exc): pass
        fake_module=types.ModuleType("playwright.sync_api")
        fake_module.sync_playwright=lambda:FakeSync()
        def visible_following(page,handle,on_batch,stop_signal):
            self.assertEqual(handle,"own.profile")
            on_batch(["first.user","second.user"],True)
            return ["first.user","second.user"],True

        self.collector.owner="owner_A"
        self.collector.account="ig_A"
        self.collector.expected_handle="own.profile"
        self.collector.autonomous=True
        self.collector.max_per_window=50
        self.collector.window_minutes=60
        self.collector.min_delay_seconds=0
        self.collector.pause_every=0
        self.collector.pause_minutes=0
        with patch.dict(sys.modules,{"playwright.sync_api":fake_module}), \\
             patch("profile_counts_bridge.challenge_detected",return_value=False), \\
             patch("profile_counts_bridge.signed_in_handle",return_value="own.profile"), \\
             patch("profile_counts_bridge.read_following_visible",side_effect=visible_following), \\
             patch("profile_counts_bridge.collect_visible_counts",return_value=("ok",(123,45,False))):
            self.collector._run()

        state=self.collector.snapshot()
        self.assertEqual(state["status"],"complete")
        self.assertEqual(state["progress"],2)
        self.assertTrue(state["discovery_complete"])
        self.assertEqual(self.collector.following()["usernames"],["first.user","second.user"])
        rows=read_results(self.collector.result_path())
        self.assertEqual(rows["first.user"]["followers"],"123")
        self.assertEqual(rows["second.user"]["following"],"45")

    def test_autonomous_account_identity_mismatch_rejected_before_switch(self):
        import time
        def hold():
            while not self.collector.stop_signal.wait(0.1): pass
        self.collector._run=hold
        try:
            response=self.request("/api/auto",body={
                "owner":"owner-A","account":"ig-one","expected_handle":"my.instagram"
            })
            self.assertEqual(response["account"],"ig-one")
            with self.assertRaises(HTTPError) as exc:
                self.request("/api/auto",body={
                    "owner":"owner-A","account":"ig-two","expected_handle":"another.instagram"
                })
            self.assertEqual(exc.exception.code,400)
            self.assertEqual(self.request("/api/status")["account"],"ig-one")
        finally:
            self.collector.stop()

    def test_start_and_login_ready_without_real_browser(self):
        # No Internet/Instagram visit in an offline CI test.
        self.collector._run=lambda: self.collector._update("complete","Simulated done",0)
        state=self.request("/api/start",body={
            "owner":"owner-A","account":"ig-one","usernames":["@AAA", "aaa", "b.b"],
            "max_per_window":200,"window_minutes":5,"min_delay_seconds":5,
            "pause_every":12,"pause_minutes":5,
        })
        self.collector.worker.join(2)
        self.assertEqual(state["total"],2)
        self.assertEqual(state["max_per_window"],200)
        self.assertEqual(state["window_minutes"],5)
        self.assertEqual(state["min_delay_seconds"],5)
        self.assertEqual(state["pause_every"],12)
        self.assertEqual(state["pause_minutes"],5)
        self.assertEqual(self.request("/api/status")["status"],"complete")
        with self.assertRaises(HTTPError) as e:
            self.request("/api/resume",body={})
        self.assertEqual(e.exception.code,400)


if __name__ == "__main__":
    unittest.main()
