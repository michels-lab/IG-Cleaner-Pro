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
            with patch("profile_actions.shutil.which",return_value=str(chrome)), \
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

    def test_manual_review_navigation_is_durable_no_repeat_without_action_click(self):
        """Manual Chrome-open must not silently become a fresh robot target."""
        from profile_actions import _atomic_json, _read_json
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            collector = Collector(root / "journal", root / "legacy-chrome")
            sessions = ActionChromeProfiles(collector.session_dir)
            robot = ActionRobot(
                collector, collector.data_dir, collector.session_dir,
                session_for_scope=sessions.directory,
                lease_factory=lambda *_args: FakeLease())
            action_wal = robot._base_for(OWNER, A, "cancel")
            _atomic_json(action_wal, {})
            action_before = action_wal.read_bytes()
            manual_a = robot._manual_review_visits_file_for(OWNER, A, "cancel")
            manual_b = robot._manual_review_visits_file_for(OWNER, B, "cancel")
            manual_other_task = robot._manual_review_visits_file_for(OWNER, A, "unfollow")
            self.assertFalse(manual_a.exists())
            chrome = root / "chrome.exe"
            chrome.write_text("mock executable")

            with patch("profile_actions.shutil.which", return_value=str(chrome)):
                with patch("profile_actions.subprocess.Popen") as spawned:
                    opened = robot.open_profile({
                        "owner": OWNER, "account": A,
                        "task": "cancel", "username": "opened.manually"})
                    self.assertFalse(opened["relationship_action"])
                    spawned.assert_called_once()
                    manual = _read_json(manual_a, {})
                    self.assertEqual(set(manual), {"opened.manually"})
                    self.assertEqual(manual["opened.manually"]["source"],
                                     "owner_selected_manual_readonly_review")
                    self.assertEqual(manual["opened.manually"]["state"],
                                     "navigation_requested_not_relationship_action")
                    first_bytes = manual_a.read_bytes()
                    # Explicit reinspection remains allowed but NEVER
                    # duplicates the durable visit record or action history.
                    robot.open_profile({
                        "owner": OWNER, "account": A,
                        "task": "cancel", "username": "opened.manually"})
                    self.assertEqual(manual_a.read_bytes(), first_bytes)
                    self.assertEqual(spawned.call_count, 2)

            self.assertEqual(action_wal.read_bytes(), action_before)
            self.assertFalse(manual_b.exists())
            self.assertFalse(manual_other_task.exists())
            self.assertEqual(
                robot._visited_usernames(OWNER, A, "cancel", {}),
                ["opened.manually"])
            self.assertEqual(robot._visited_usernames(OWNER, B, "cancel", {}), [])
            self.assertEqual(robot._visited_usernames(OWNER, A, "unfollow", {}), [])

            # A cold-start Windows/Developer process must see the same
            # manual navigation and reject the SAME profile in a fresh batch
            # BEFORE any Chrome robot, click or new cohort is launched.
            restarted = ActionRobot(
                collector, collector.data_dir, collector.session_dir,
                session_for_scope=sessions.directory,
                lease_factory=lambda *_args: FakeLease())
            with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
                restarted.start(request(A, "first.person", "opened.manually"))
            self.assertIsNone(restarted.worker)
            self.assertEqual(action_wal.read_bytes(), action_before)
            self.assertFalse(
                restarted._review_batches_file_for(OWNER, A, "cancel").exists())
            # The independent account B can still authorize this exact
            # username: A's manual visit is not B's visit or action evidence.
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                result = restarted.start(request(B, "second.person", "opened.manually"))
                self.assertEqual(result["account"], B)
                worker.return_value.start.assert_called_once()

    def test_malformed_manual_visit_ledger_blocks_new_batch_without_repair(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            collector = Collector(root / "journal", root / "legacy-chrome")
            sessions = ActionChromeProfiles(collector.session_dir)
            robot = ActionRobot(
                collector, collector.data_dir, collector.session_dir,
                session_for_scope=sessions.directory,
                lease_factory=lambda *_args: FakeLease())
            manual = robot._manual_review_visits_file_for(OWNER, A, "cancel")
            _atomic_json(manual, {"opened.manually": "not a visit record"})
            original = manual.read_bytes()
            with self.assertRaisesRegex(ValueError, "Manual Review visits are unreadable"):
                robot.start(request(A, "first.person", "new.target"))
            self.assertEqual(manual.read_bytes(), original)
            self.assertIsNone(robot.worker)
            self.assertFalse(
                robot._review_batches_file_for(OWNER, A, "cancel").exists())

    def test_manual_review_denies_busy_chrome_lane_but_other_account_remains_available(self):
        """An external Windows worker owns A: manual Review cannot attach to A."""
        from chrome_lane_interlock import ChromeLaneLease, ChromeLaneBusy
        from profile_actions import _atomic_json
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            counts = Collector(root / "journal", root / "legacy-chrome")
            sessions = ActionChromeProfiles(counts.session_dir)
            # Fresh instance simulates restarting Public while Developer is
            # actively controlling A's persistent Chrome profile.
            new_app = ActionRobot(counts, counts.data_dir,
                                  counts.session_dir,
                                  session_for_scope=sessions.directory)
            first = sessions.directory(OWNER, A)
            second = sessions.directory(OWNER, B)
            journal_a = new_app._base_for(OWNER, A, "unfollow")
            journal_b = new_app._base_for(OWNER, B, "unfollow")
            _atomic_json(journal_a, {
                "possible.click": {"status": "review", "click_intent": {
                    "phase": "relationship_control"}}})
            _atomic_json(journal_b, {})
            unchanged = journal_a.read_bytes(), journal_b.read_bytes()
            chrome = root / "chrome.exe"
            chrome.write_text("mock executable")
            with patch("profile_actions.shutil.which", return_value=str(chrome)), \
                 patch("profile_actions.subprocess.Popen") as launch:
                with ChromeLaneLease(first):
                    with self.assertRaises(ChromeLaneBusy):
                        new_app.open_profile({
                            "owner": OWNER, "account": A, "task": "unfollow",
                            "username": "possible.click"})
                    launch.assert_not_called()
                    opened = new_app.open_profile({
                        "owner": OWNER, "account": B, "task": "unfollow",
                        "username": "safe.second"})
                    self.assertFalse(opened["relationship_action"])
                    self.assertEqual(launch.call_count, 1)
                    self.assertIn("--user-data-dir=" + str(second),
                                  launch.call_args.args[0])
                    self.assertNotIn("--user-data-dir=" + str(first),
                                     launch.call_args.args[0])
                # Once A worker releases, explicit manual Review is possible
                # in the CORRECT A Chrome without a relationship action.
                reopened = new_app.open_profile({
                    "owner": OWNER, "account": A, "task": "unfollow",
                    "username": "possible.click"})
                self.assertFalse(reopened["relationship_action"])
                self.assertEqual(launch.call_count, 2)
                self.assertIn("--user-data-dir=" + str(first),
                              launch.call_args.args[0])
            self.assertEqual((journal_a.read_bytes(), journal_b.read_bytes()),
                             unchanged,
                             "Manual inspection never edits either account WAL.")

    def test_manual_review_chrome_launch_error_always_releases_lane(self):
        from chrome_lane_interlock import ChromeLaneLease
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            counts=Collector(root/"journal",root/"legacy-chrome")
            sessions=ActionChromeProfiles(counts.session_dir)
            robot=ActionRobot(counts,counts.data_dir,counts.session_dir,
                              session_for_scope=sessions.directory)
            chrome=root/"chrome.exe"
            chrome.write_text("fake executable")
            with patch("profile_actions.shutil.which",return_value=str(chrome)), \
                 patch("profile_actions.subprocess.Popen",
                       side_effect=OSError("Chrome exited")):
                with self.assertRaisesRegex(ValueError,
                    "Unable to reopen robot Chrome"):
                    robot.open_profile({
                        "owner":OWNER,"account":A,"task":"cancel",
                        "username":"some.target"})
            with ChromeLaneLease(sessions.directory(OWNER,A)):
                pass  # Failed Popen did not leak the OS Chrome lane lock.

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
                }), patch("profile_actions.preserve_instagram_auth_page",return_value=True), \
                patch("profile_actions.challenge_detected",return_value=False), \
                patch("profile_actions._find_verified_owner_tab",
                      return_value=(None,"realmichelduarte")), \
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
