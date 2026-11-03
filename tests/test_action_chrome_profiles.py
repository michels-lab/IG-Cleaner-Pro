"""GRANADA: legacy single-lane robot must never inherit a prior IG account's Chrome.

Real production build_server/ActionRobot code, mocked only for Chrome startup
and relationship operations. No Instagram network traffic or account clicks.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch
import sys
import threading
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from action_chrome_profiles import ActionChromeProfiles
from profile_actions import ActionRobot
from profile_counts_bridge import Collector, build_server


OWNER = "u_owner_42"
A = "ig_real_1234567"
B = "ig_secondary_1234567"


class FakeLease:
    def acquire(self):
        return self

    def release(self):
        pass


def request(account, handle, target):
    return {
        "owner": OWNER, "account": account,
        "expected_handle": handle, "task": "cancel",
        "targets": [target], "protected": [], "batch_size": 1,
        "gap_seconds": 10, "rest_minutes": 0, "confirmation": "cancel:1",
    }


class ActionChromeAccountIsolationTests(unittest.TestCase):
    def test_directories_are_stable_separate_and_no_legacy_cookie_migration(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / "legacy-instagram-chrome"
            legacy.mkdir()
            (legacy / "old-owner-cookie-sentinel").write_text("KEEP PRIVATE")
            chooser = ActionChromeProfiles(legacy)
            first = chooser.directory(OWNER, A)
            second = chooser.directory(OWNER, B)
            self.assertNotEqual(first, second)
            self.assertNotEqual(first, legacy)
            self.assertNotEqual(second, legacy)
            self.assertEqual(first, ActionChromeProfiles(legacy).directory(OWNER, A))
            self.assertNotEqual(first, chooser.directory("u_different_42", A))
            self.assertFalse(first.exists(), "No automatic login or cookie migration.")
            self.assertFalse(second.exists())
            self.assertEqual((legacy / "old-owner-cookie-sentinel").read_text(),
                             "KEEP PRIVATE")
            self.assertFalse(first.is_relative_to(root / "exportable-data"))
            for invalid in [("", A), (OWNER, ""), ("../owner", "ig\x00malformed"),
                            ("x" * 201, A), (OWNER, "x" * 121)]:
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    chooser.directory(*invalid)

    def test_production_bridge_resolves_per_account_and_keeps_manual_chrome_separate(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            counts = Collector(root / "exportable-counts", root / "legacy-chrome")
            server = build_server(counts, "test-token", 0)
            try:
                robot = server.actions
                folder_a = robot._browser_session_for(OWNER, A)
                folder_b = robot._browser_session_for(OWNER, B)
                self.assertNotEqual(folder_a, folder_b)
                self.assertNotEqual(folder_a, counts.session_dir)
                self.assertNotEqual(folder_b, counts.session_dir)
                self.assertNotEqual(folder_a, server.dual_chrome_sessions.directory(OWNER, A))
                self.assertFalse(folder_a.is_relative_to(counts.data_dir))
                self.assertFalse(folder_b.is_relative_to(counts.data_dir))
                self.assertFalse(folder_a.exists())
                self.assertFalse(folder_b.exists())
                self.assertEqual(robot._base_for(OWNER,A,"cancel").parent,
                                 counts.data_dir)
                self.assertNotEqual(robot._base_for(OWNER,A,"cancel"),
                                    robot._base_for(OWNER,B,"cancel"))
                self.assertNotEqual(folder_a,
                                    server.dual_action_workspaces.sessions.directory(OWNER,A))
            finally:
                server.server_close()

    def test_saved_account_switch_reuses_correct_chrome_without_touching_prior_login(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            counts = Collector(root / "journal", root / "legacy-chrome")
            sessions = ActionChromeProfiles(counts.session_dir)
            robot = ActionRobot(
                counts, counts.data_dir, counts.session_dir,
                session_for_scope=sessions.directory,
                lease_factory=lambda *_args: FakeLease())
            a = request(A, "realmichelduarte", "alpha.target")
            b = request(B, "micheltheog", "beta.target")
            folder_a, folder_b = sessions.directory(OWNER,A), sessions.directory(OWNER,B)
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                robot.start(a)
                self.assertEqual(robot.session_dir,folder_a)
                self.assertEqual(robot.owner,OWNER)
                self.assertEqual(robot.account,A)
                self.assertEqual(robot.handle,"realmichelduarte")
                folder_a.mkdir(parents=True)
                (folder_a / "logged-in-as-A").write_text("A private cookie sentinel")
                robot.start(b)
                self.assertEqual(robot.session_dir,folder_b)
                self.assertEqual(robot.handle,"micheltheog")
                self.assertFalse(folder_b.exists())
                self.assertTrue((folder_a / "logged-in-as-A").exists())
                self.assertNotIn("alpha.target",robot.targets)
                self.assertNotIn("beta.target",robot.attempted_history(a)["visited_usernames"])
                self.assertEqual(len(robot._review_batches(OWNER,A,"cancel")),1)
                self.assertEqual(len(robot._review_batches(OWNER,B,"cancel")),1)
                saved_a=robot._review_batches(OWNER,A,"cancel")[0]
                robot.start({**a,"batch_id":saved_a["id"]})
                self.assertEqual(robot.session_dir,folder_a)
                self.assertTrue((folder_a / "logged-in-as-A").exists())
                self.assertEqual(robot.account,A)
                self.assertEqual(worker.return_value.start.call_count,3)
            restarted = ActionRobot(
                counts, counts.data_dir, counts.session_dir,
                session_for_scope=sessions.directory)
            self.assertEqual(restarted._browser_session_for(OWNER,A),folder_a)
            self.assertEqual(restarted._browser_session_for(OWNER,B),folder_b)
            self.assertEqual(restarted.owner,"")
            self.assertEqual(restarted.session_dir,counts.session_dir)

    def test_readonly_manual_profile_after_app_restart_uses_exact_account_chrome(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            counts=Collector(root/"journal",root/"legacy-chrome")
            sessions=ActionChromeProfiles(counts.session_dir)
            robot=ActionRobot(counts,counts.data_dir,counts.session_dir,
                              session_for_scope=sessions.directory)
            chrome=root/"chrome.exe"
            chrome.write_text("fake executable")
            with patch("profile_actions.shutil.which",return_value=str(chrome)), \\
                 patch("profile_actions.subprocess.Popen") as launch:
                for account in (A,B,A):
                    result=robot.open_profile({"owner":OWNER,"account":account,
                        "task":"cancel","username":"some.target"})
                    self.assertFalse(result["relationship_action"])
                    argv=launch.call_args.args[0]
                    self.assertIn("--user-data-dir="+str(sessions.directory(OWNER,account)),
                                  argv)
                    self.assertNotIn("--user-data-dir="+str(counts.session_dir),argv)
                self.assertEqual(launch.call_count,3)
            robot.owner,robot.account,robot.task=OWNER,A,"cancel"
            robot.worker=MagicMock()
            robot.worker.is_alive.return_value=True
            with self.assertRaisesRegex(ValueError,"Another Instagram account"):
                robot.open_profile({"owner":OWNER,"account":B,
                                    "task":"cancel","username":"some.target"})

    def test_wrong_live_instagram_identity_blocks_before_click_in_scoped_chrome(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            counts=Collector(root/"journal",root/"legacy-chrome")
            sessions=ActionChromeProfiles(counts.session_dir)
            robot=ActionRobot(counts,counts.data_dir,counts.session_dir,
                              session_for_scope=sessions.directory)
            robot.owner,robot.account,robot.handle,robot.task=OWNER,B,"micheltheog","unfollow"
            robot.targets=["target.person"]
            robot.session_dir=robot._browser_session_for(OWNER,B)
            page=MagicMock()
            page.is_closed.return_value=False
            browser=MagicMock()
            browser.pages=[page]
            fake_pw=types.SimpleNamespace(chromium=types.SimpleNamespace(
                launch_persistent_context=MagicMock(return_value=browser)))
            manager=MagicMock()
            manager.__enter__.return_value=fake_pw
            with patch.dict(sys.modules,{
                 "playwright":types.ModuleType("playwright"),
                 "playwright.sync_api":types.SimpleNamespace(sync_playwright=lambda:manager)
                }), patch("profile_actions.preserve_instagram_auth_page",return_value=True), \\
                patch("profile_actions.challenge_detected",return_value=False), \\
                patch("profile_actions._find_verified_owner_tab",
                      return_value=(None,"realmichelduarte")), \\
                patch("profile_actions.perform_visible_action",
                      side_effect=AssertionError("NO relationship click allowed")):
                robot._run()
            self.assertEqual(robot.status,"blocked")
            self.assertIn("expected @micheltheog",robot.message)
            self.assertIn("@realmichelduarte",robot.message)
            call=fake_pw.chromium.launch_persistent_context.call_args
            self.assertEqual(call.kwargs["user_data_dir"],str(sessions.directory(OWNER,B)))
            self.assertEqual(robot.snapshot()["processed"],0)


if __name__=="__main__":
    unittest.main()
