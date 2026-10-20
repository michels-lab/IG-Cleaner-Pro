"""Offline contract for REAL installed Developer Chrome read-only probes.

Live owner account is NEVER accessed by CI; test fixture proves diagnostic
selection, identity fails closed, no profile mutation and report redaction.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from developer_live_probe import (
    DeveloperLiveProbe, select_real_issues, _journal_path,
    inspect_real_profile, LIVE_CODES,
)
from profile_counts_bridge import Collector, build_server


class FakePage:
    url = "https://www.instagram.com/test.target/"
    def locator(self, value):
        class E:
            def count(self): return 0
        return E()
    def wait_for_timeout(self, ms):
        return None


class DeveloperRealDOMTest(unittest.TestCase):
    def test_select_failed_profiles_only_for_exact_account_task(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = _journal_path(root, "owner-one", "ig-one", "unfollow")
            path.write_text(json.dumps({
                "old.good": {"status": "ok", "at": "2026-10-20T09:00:00Z"},
                "test.target": {"status": "review", "at": "2026-10-20T09:02:00Z"},
                "test.second": {"status": "blocked", "at": "2026-10-20T09:03:00Z"},
                "bad target": {"status": "error", "at": "2026-10-20T09:04:00Z"},
            }), encoding="utf-8")
            self.assertEqual(select_real_issues(root, "owner-one", "ig-one", "unfollow", 2),
                             ["test.second", "test.target"])
            for owner, account, task in (
                ("owner-two", "ig-one", "unfollow"),
                ("owner-one", "ig-two", "unfollow"),
                ("owner-one", "ig-one", "cancel"),
            ):
                self.assertEqual(select_real_issues(root, owner, account, task, 3), [])
            self.assertNotIn("old.good",
                             select_real_issues(root, "owner-one", "ig-one", "unfollow", 5))

    def test_no_click_live_dom_classification(self):
        page = FakePage()
        with patch("developer_live_probe.challenge_detected", return_value=False), \
             patch("developer_live_probe._wait_for_target_profile_shell", return_value=True), \
             patch("developer_live_probe._verified_action_owner", return_value=True), \
             patch("developer_live_probe._profile_relationship_control") as controls, \
             patch("developer_live_probe._follow_state") as follow:
            controls.side_effect=lambda page, user, words: (
                "CONTROL" if "Following" in words else None)
            follow.return_value=None
            self.assertEqual(inspect_real_profile(page,"test.target","unfollow","owner"),
                             "FOLLOWING_VISIBLE")
            controls.side_effect=lambda page, user, words: (
                "CONTROL" if "Requested" in words else None)
            self.assertEqual(inspect_real_profile(page,"test.target","cancel","owner"),
                             "REQUESTED_VISIBLE")
            controls.return_value=None
            controls.side_effect=None
            follow.return_value="follow"
            self.assertEqual(inspect_real_profile(page,"test.target","cancel","owner"),
                             "NO_REQUEST_VISIBLE")
            self.assertEqual(inspect_real_profile(page,"test.target","unfollow","owner"),
                             "NOT_FOLLOWING_VISIBLE")
            follow.return_value=None
            self.assertEqual(inspect_real_profile(page,"test.target","cancel","owner"),
                             "RELATIONSHIP_UNKNOWN")
        with patch("developer_live_probe.challenge_detected", return_value=False), \
             patch("developer_live_probe._wait_for_target_profile_shell", return_value=True), \
             patch("developer_live_probe._verified_action_owner", return_value=False):
            self.assertEqual(inspect_real_profile(page,"test.target","unfollow","owner"),
                             "OWNER_IDENTITY_UNVERIFIED")
        # A profile redirect must not lead to any click/scan on unrelated users.
        page.url="https://www.instagram.com/suggested.profile/"
        with patch("developer_live_probe.challenge_detected", return_value=False):
            self.assertEqual(inspect_real_profile(page,"test.target","unfollow","owner"),
                             "PROFILE_REDIRECT")

    def test_probe_fail_closed_and_exports_redacted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source=root/"journal"
            source.mkdir()
            _journal_path(source,"owner","ig","cancel").write_text(json.dumps({
                "confidential.profile":{"status":"review","at":"2026-10-20T10:00:00Z"}
            }),encoding="utf-8")
            probe=DeveloperLiveProbe(source,root/"isolated-developer-chrome")
            with self.assertRaises(ValueError):
                probe.start({"owner":"owner","account":"ig","task":"cancel",
                             "expected_handle":"my.profile","confirmation":"missing"})
            with self.assertRaises(ValueError):
                probe.start({"owner":"owner","account":"ig","task":"cancel",
                             "expected_handle":"my.profile","max_profiles":10,
                             "confirmation":"READ_ONLY_REAL_INSTAGRAM"})
            with patch.object(DeveloperLiveProbe,"_run",lambda self, targets, task, handle:
                              self._add(1,"REQUESTED_VISIBLE")):
                result=probe.start({"owner":"owner","account":"ig","task":"cancel",
                                    "expected_handle":"my.profile",
                                    "confirmation":"READ_ONLY_REAL_INSTAGRAM"})
                probe.worker.join(timeout=3)
            snapshot=probe.snapshot()
            self.assertEqual(snapshot["counts"],{"REQUESTED_VISIBLE":1})
            self.assertTrue(snapshot["events"][0]["meaning"])
            for private in ("confidential.profile","my.profile","owner","ig",
                            "012345678901234567890123456789"):
                self.assertNotIn(private,json.dumps(snapshot))
            self.assertEqual(snapshot["evidence"],"real_visible_dom_no_relationship_click")
            self.assertFalse(snapshot["contains_usernames"])
            self.assertTrue(all(x in LIVE_CODES for x in snapshot["counts"]))
            self.assertFalse((root/"isolated-developer-chrome").exists())

    def test_developer_only_authenticated_loopback_endpoints(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            collector=Collector(root/"scratch",root/"dev-session")
            server=build_server(collector,"123456789012345678901234567890ab",0,
                                developer_mode=True,audit_root=root)
            t=threading.Thread(target=server.serve_forever,daemon=True)
            t.start()
            addr=f"http://127.0.0.1:{server.server_port}"
            headers={"X-IGC-Bridge-Token":"123456789012345678901234567890ab",
                     "Content-Type":"application/json"}
            try:
                result=json.load(urlopen(Request(addr+"/api/developer/live-status",
                                                   headers=headers),timeout=5))
                self.assertEqual(result["state"],"idle")
                action_status=json.load(urlopen(Request(
                    addr+"/api/developer/action-status",headers=headers),timeout=5))
                self.assertEqual(action_status["status"],"idle")
                # Developer mutation is impossible without exact-target consent.
                base={"owner":"owner","account":"ig","task":"cancel",
                      "expected_handle":"my.profile","targets":["test.target"]}
                for payload in (
                    base,
                    {**base,"acknowledge_real_changes":True},
                    {**base,"acknowledge_real_changes":True,
                     "explicit_consent":"LIVE_TEST:unfollow:test.target"},
                    {**base,"acknowledge_real_changes":True,
                     "explicit_consent":"LIVE_TEST:cancel:test.target",
                     "targets":["test.target"]*11},
                    {**base,"acknowledge_real_changes":True,
                     "explicit_consent":"LIVE_TEST:cancel:test.target",
                     "targets":[None]},
                ):
                    with self.assertRaises(HTTPError) as forbidden:
                        urlopen(Request(addr+"/api/developer/action-start",
                           data=json.dumps(payload).encode(),headers=headers,
                           method="POST"),timeout=5)
                    self.assertEqual(forbidden.exception.code,400)
                self.assertFalse(list(root.glob("instagram-actions-*.json")),
                                 "Rejected tests must not create canonical action journals")
                # A *valid* exact-target approval reaches only the explicit
                # Developer test runner; mocked start means zero real clicks.
                from profile_counts_bridge import ActionRobot
                payload={**base,"acknowledge_real_changes":True,
                         "explicit_consent":"LIVE_TEST:cancel:test.target"}
                with patch.object(ActionRobot,"start",return_value={"status":"starting"}) as start:
                    accepted=json.load(urlopen(Request(
                        addr+"/api/developer/action-start",
                        data=json.dumps(payload).encode(),headers=headers,
                        method="POST"),timeout=5))
                    self.assertEqual(accepted["status"],"starting")
                    self.assertEqual(start.call_count,1)
                    forwarded=start.call_args[0][0]
                    self.assertEqual(forwarded["targets"],["test.target"])
                    self.assertEqual(forwarded["batch_size"],1)
                    self.assertEqual(forwarded["confirmation"],"cancel:1")
                    self.assertGreaterEqual(forwarded["gap_seconds"],10)
                # The same real-action route cannot silently Unfollow without
                # independently verified Followers evidence.
                unfollow={**base,"task":"unfollow",
                          "acknowledge_real_changes":True,
                          "explicit_consent":"LIVE_TEST:unfollow:test.target"}
                with self.assertRaises(HTTPError) as unverified:
                    urlopen(Request(addr+"/api/developer/action-start",
                        data=json.dumps(unfollow).encode(),headers=headers,
                        method="POST"),timeout=5)
                self.assertEqual(unverified.exception.code,400)

                with self.assertRaises(HTTPError) as missing:
                    urlopen(Request(addr+"/api/developer/live-status"),timeout=5)
                self.assertEqual(missing.exception.code,403)
                with self.assertRaises(HTTPError) as act:
                    urlopen(Request(addr+"/api/actions/start",data=b"{}",
                                    headers=headers,method="POST"),timeout=5)
                self.assertEqual(act.exception.code,400)
                with self.assertRaises(HTTPError) as empty:
                    urlopen(Request(addr+"/api/developer/live-start",
                                    data=json.dumps({"owner":"x","account":"y","task":"cancel",
                                     "expected_handle":"my.profile",
                                     "confirmation":"READ_ONLY_REAL_INSTAGRAM"}).encode(),
                                    headers=headers,method="POST"),timeout=5)
                self.assertEqual(empty.exception.code,400)
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
