"""End-to-end owner-reference Unfollow against a LOCAL simulated Instagram.

Real Chromium and the normal perform_visible_action entrypoint; all routes
intercepted. No live Instagram account, remote request, or real relationship
change. A durable WAL callback is required before a single mutation POST.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import perform_visible_action

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipIf(sync_playwright is None, "Playwright unavailable")
class OwnerReferenceChromiumE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.ctx = self.browser.new_context()
        self.ctx.add_cookies([
            {"name": "ds_user_id", "value": "9981",
             "domain": "www.instagram.com", "path": "/"},
            {"name": "csrftoken", "value": "fixture-csrf",
             "domain": "www.instagram.com", "path": "/"},
        ])
        self.page = self.ctx.new_page()
        self.steps = []
        self.state = {"unfollowed": False, "post_count": 0, "block_post": False,
                      "lookup_empty": False, "wrong_header": False,
                      "stale_following": False}
        self.ctx.route("https://www.instagram.com/**", self._intercept)
        # Independent owner evidence in authenticated site nav; no patch to
        # production owner verification or exact target identity selectors.
        self.owner = "owner.user"
        self.target = "target.user"

    def tearDown(self):
        self.ctx.close()

    def _html(self):
        heading = "wrong.user" if self.state["wrong_header"] else self.target
        relation = ("Following" if self.state["stale_following"] else
                    ("Follow" if self.state["unfollowed"] else "Following"))
        return ("""<!doctype html><html><body>
          <nav><a href="/owner.user/" aria-label="Profile">Profile</a></nav>
          <header><h1>""" + heading + """</h1>
          <button id="relationship">""" + relation + """</button></header>
          <main><h2>""" + heading + """</h2></main>
          <input name="fb_dtsg" value="testDTSG">
          <input name="lsd" value="testLSD">
          </body></html>""")

    def _intercept(self, route):
        request = route.request
        path = request.url
        if "/api/v1/friendships/" in path and "/following/" in path:
            self.steps.append("lookup")
            users = [] if self.state["lookup_empty"] else [
                {"username": self.target, "pk": "50012", "pk_id": "50012"}]
            route.fulfill(status=200, content_type="application/json",
                          body=__import__("json").dumps({"status": "ok", "users": users}))
        elif path.endswith("/api/graphql"):
            self.steps.append("post")
            self.state["post_count"] += 1
            data = parse_qs(request.post_data or "")
            self.assertEqual(request.method, "POST")
            self.assertEqual(data["doc_id"][0], "27789106940691111")
            self.assertEqual(data["fb_api_req_friendly_name"][0],
                             "usePolarisUnfollowMutation")
            self.assertEqual(data["jazoest"][0], "2"+str(sum(map(ord,"testDTSG"))))
            self.assertEqual(__import__("json").loads(data["variables"][0])
                             ["target_user_id"], "50012")
            if self.state["block_post"]:
                route.fulfill(status=429, content_type="application/json",
                              body='{"errors":[{"message":"feedback_required"}]}')
            else:
                self.state["unfollowed"] = True
                route.fulfill(status=200, content_type="application/json",
                              body='{"data":{"unfollow":{"friendship_status":'
                                   '{"following":false,"outgoing_request":false}}}}')
        elif path.rstrip("/") == "https://www.instagram.com":
            route.fulfill(status=200, content_type="text/html", body=self._html())
        elif path.rstrip("/").endswith("/"+self.owner):
            route.fulfill(status=200, content_type="text/html",
                          body='<html><header><h1>owner.user</h1>'
                               '<button>Edit profile</button></header></html>')
        else:
            self.steps.append("profile")
            route.fulfill(status=200, content_type="text/html", body=self._html())

    def run_robot(self, allowed=True, on_pre_click=None):
        def record(phase):
            self.steps.append("wal")
            self.assertEqual(phase, "relationship_control")
        return perform_visible_action(
            self.page, self.target, "unfollow", self.owner,
            can_act=lambda _:allowed, on_pre_click=on_pre_click or record,
            use_reference_transport=True)

    def test_real_browser_owner_reference_one_mutation_verified(self):
        status, note = self.run_robot()
        self.assertEqual(status, "ok", note)
        self.assertEqual(self.state["post_count"], 1)
        self.assertLess(self.steps.index("lookup"), self.steps.index("wal"))
        self.assertLess(self.steps.index("wal"), self.steps.index("post"))
        self.assertEqual(self.steps.count("post"), 1)
        self.assertGreaterEqual(self.steps.count("profile"), 2,
            "Fresh profile GET must verify final Follow state")

    def test_accepted_post_with_stale_following_is_pending_not_false_ok(self):
        self.state["stale_following"] = True
        status, note = self.run_robot()
        self.assertEqual(status, "review", note)
        self.assertIn("Pending verification:", note)
        self.assertEqual(self.state["post_count"], 1,
            "A pending result must never lead to a second mutation.")
        self.assertEqual(self.steps.count("wal"), 1)
        self.assertLess(self.steps.index("wal"), self.steps.index("post"))

    def test_protected_target_is_never_sent(self):
        status, note = self.run_robot(allowed=False)
        self.assertEqual(status, "skipped", note)
        self.assertEqual(self.state["post_count"], 0)
        self.assertNotIn("wal", self.steps)

    def test_lookup_absence_must_never_unfollow(self):
        self.state["lookup_empty"] = True
        status, note = self.run_robot()
        self.assertEqual(status, "review", note)
        self.assertEqual(self.state["post_count"], 0)
        self.assertNotIn("wal", self.steps)

    def test_wrong_header_is_not_an_authorized_target(self):
        self.state["wrong_header"] = True
        status, note = self.run_robot()
        self.assertIn(status, ("blocked", "review"), note)
        self.assertEqual(self.state["post_count"], 0)
        self.assertNotIn("wal", self.steps)

    def test_action_block_keeps_unknown_click_status(self):
        self.state["block_post"] = True
        status, note = self.run_robot()
        self.assertEqual(status, "blocked", note)
        self.assertEqual(self.state["post_count"], 1)
        self.assertEqual(self.steps.count("wal"), 1)

    def test_wal_write_failure_prevents_post(self):
        def disk_full(_):
            self.steps.append("wal")
            raise OSError("disk full")
        with self.assertRaisesRegex(OSError, "disk full"):
            self.run_robot(on_pre_click=disk_full)
        self.assertEqual(self.state["post_count"], 0)


if __name__ == "__main__":
    unittest.main()
