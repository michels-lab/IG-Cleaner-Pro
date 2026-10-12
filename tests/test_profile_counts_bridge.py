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
            {"owner":"A","account":"first","usernames":["valid"],"per_hour":61},
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

    def test_start_and_login_ready_without_real_browser(self):
        # No Internet/Instagram visit in an offline CI test.
        self.collector._run=lambda: self.collector._update("complete","Simulated done",0)
        state=self.request("/api/start",body={
            "owner":"owner-A","account":"ig-one","usernames":["@AAA", "aaa", "b.b"],
            "per_hour":50,
        })
        self.collector.worker.join(2)
        self.assertEqual(state["total"],2)
        self.assertEqual(self.request("/api/status")["status"],"complete")
        with self.assertRaises(HTTPError) as e:
            self.request("/api/resume",body={})
        self.assertEqual(e.exception.code,400)


if __name__ == "__main__":
    unittest.main()
