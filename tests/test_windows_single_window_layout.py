"""New native Windows two-window product contract (offline and data preserving)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import ig_cleaner_desktop as app
import windows_workspace_picker as picker


class WindowsIndependentWindowTests(unittest.TestCase):
    def test_first_window_is_the_exact_legacy_browser_location(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "workspace-browser"
            existing.mkdir()
            (existing / "History").write_text("KEEP")
            self.assertEqual(picker.chrome_workspace_path(root, "primary"), existing)
            self.assertEqual(picker.chrome_workspace_path(root, "secondary"),
                             root / "workspace-browser-secondary")
            self.assertNotEqual(picker.chrome_workspace_path(root, "primary"),
                                picker.chrome_workspace_path(root, "secondary"))
            self.assertEqual(picker.ui_document_path(root, "primary"),
                             root / "IG-Cleaner-Pro.html")
            self.assertEqual(picker.ui_document_path(root, "secondary"),
                             root / "second-window" / "IG-Cleaner-Pro.html")
            self.assertNotEqual(picker.ui_document_path(root, "primary"),
                                picker.ui_document_path(root, "secondary"))
            self.assertEqual((existing / "History").read_text(), "KEEP")
            self.assertFalse((root / "workspace-browser-secondary").exists())
            for invalid in ("", "third", "../primary", "PRIMARY"):
                with self.assertRaises(ValueError):
                    picker.chrome_workspace_path(root, invalid)

    def test_two_native_windows_isolate_real_robot_sessions_without_moving_journals(self):
        from action_chrome_profiles import ActionChromeProfiles
        from profile_counts_bridge import build_server

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            home, legacy = root / "InstaCleaner", root / ".ig-cleaner-pro"
            legacy.mkdir()
            original = legacy / "instagram-browser"
            original.mkdir()
            (original / "OriginalOwnerSessionMarker").write_text("KEEP", encoding="utf-8")
            # The existing primary browser folder and canonical WAL are never
            # migrated, renamed, copied or deleted just to open account 2.
            for developer in (False, True):
                with self.subTest(developer=developer):
                    first = app.window_collector(home, legacy, "primary", developer=developer)
                    second = app.window_collector(home, legacy, "secondary", developer=developer)
                    base = home if developer else legacy
                    self.assertEqual(first.session_dir, base / "instagram-browser")
                    self.assertEqual(second.session_dir, base / "instagram-browser-secondary")
                    self.assertNotEqual(first.session_dir, second.session_dir)
                    self.assertEqual(first.data_dir, second.data_dir,
                        "The owner/account-scoped canonical audit/WAL remains common")
                    self.assertNotEqual(
                        ActionChromeProfiles(first.session_dir).directory("owner", "ig_first_12345678"),
                        ActionChromeProfiles(second.session_dir).directory("owner", "ig_first_12345678"))
                    self.assertFalse(second.session_dir.exists(),
                        "Selecting a slot alone must not create or modify Chrome sessions")
                    servers = []
                    try:
                        for collector in (first, second):
                            servers.append(build_server(collector, "offline-test-token", 0,
                                developer_mode=developer, audit_root=legacy / "profile-counts"))
                        self.assertEqual(servers[0].actions.session_dir, first.session_dir)
                        self.assertEqual(servers[1].actions.session_dir, second.session_dir)
                        self.assertNotEqual(servers[0].dual_chrome_sessions.root,
                                            servers[1].dual_chrome_sessions.root)
                        self.assertEqual(servers[0].actions.data_dir,
                                         servers[1].actions.data_dir)
                    finally:
                        for server in servers:
                            server.server_close()
            self.assertEqual((original / "OriginalOwnerSessionMarker").read_text(), "KEEP")
            self.assertFalse((legacy / "instagram-browser-secondary").exists())
            self.assertEqual(
                Path(__file__).resolve().parents[1].joinpath(
                    "tools/ig_cleaner_desktop.py").read_text(encoding="utf-8").count(
                    "collector = window_collector("), 2,
                "Installed Windows smoke and normal launch must share isolation mapping")
            for invalid in ("", "../primary", "PRIMARY", "third"):
                with self.assertRaises(ValueError):
                    app.window_collector(home, legacy, invalid)

    def test_native_choice_maps_available_buttons_and_cancel_without_side_effects(self):
        import ctypes
        from unittest.mock import patch

        cases = [
            ((), 101, "primary"), ((), 102, "secondary"), ((), 2, None),
            (("primary",), 102, "secondary"), (("primary",), 101, None),
            (("secondary",), 101, "primary"), (("secondary",), 2, None),
            (("primary", "secondary"), 2, None),
            (("primary", "secondary"), 101, None),
        ]
        for occupied, selected, expected in cases:
            with self.subTest(occupied=occupied, button=selected):
                free = [slot for slot in picker.WORKSPACES if slot not in occupied]
                expected_ids = [101 if slot == "primary" else 102 for slot in free]

                class TaskDialogStub:
                    def __call__(self, config, output, *_args):
                        cfg = config._obj
                        # The Windows SDK uses byte-packed structures, not ctypes' default padding.
                        self.assertEqual(ctypes.sizeof(cfg), 32 + 16 * ctypes.sizeof(ctypes.c_void_p))
                        self.assertEqual(ctypes.sizeof(cfg.pButtons._type_), 4 + ctypes.sizeof(ctypes.c_void_p))
                        self.assertEqual(type(cfg).hwndParent.offset, 4)
                        self_ids = [cfg.pButtons[i].nButtonID for i in range(cfg.cButtons)]
                        self.assertEqual(self_ids, expected_ids)
                        self.assertEqual(cfg.nDefaultButton, expected_ids[0] if free else 2)
                        self.assertIn("account", cfg.pszMainInstruction.lower())
                        ctypes.cast(output, ctypes.POINTER(ctypes.c_int)).contents.value = selected
                        return 0

                # Stub the native dialog only; the actual layout generation and
                # selection mapping run for every available/busy combination.
                stub = TaskDialogStub()
                stub.assertEqual = self.assertEqual
                stub.assertIn = self.assertIn
                class FakeLibrary:
                    TaskDialogIndirect = stub

                with (patch.object(picker.sys, "platform", "win32"),
                      patch.object(picker, "workspace_is_open",
                                   side_effect=lambda slot, **kw: slot in occupied) as probe,
                      patch.object(ctypes, "WinDLL", return_value=FakeLibrary(), create=True)):
                    self.assertEqual(picker.select_workspace(developer=True), expected)
                    self.assertEqual([call.kwargs for call in probe.call_args_list],
                                     [{"developer": True}, {"developer": True}])

    def test_taskdialog_failure_uses_explicit_fallback_not_startup_error(self):
        import ctypes
        from unittest.mock import patch

        class FailingDialog:
            def __call__(self, *_args):
                return -2147024809  # E_INVALIDARG

        class FailingLibrary:
            TaskDialogIndirect = FailingDialog()

        with (patch.object(picker.sys, "platform", "win32"),
              patch.object(picker, "workspace_is_open", return_value=False),
              patch.object(ctypes, "WinDLL", return_value=FailingLibrary(), create=True),
              patch.object(picker, "fallback_workspace_dialog", return_value="secondary") as fallback):
            self.assertEqual(picker.select_workspace(), "secondary")
            fallback.assert_called_once_with(["primary", "secondary"])

        with (patch.object(picker.sys, "platform", "win32"),
              patch.object(picker, "workspace_is_open", return_value=False),
              patch.object(ctypes, "WinDLL", side_effect=OSError("comctl32 unavailable"), create=True),
              patch.object(picker, "fallback_workspace_dialog", return_value=None) as fallback):
            self.assertIsNone(picker.select_workspace())
            fallback.assert_called_once_with(["primary", "secondary"])

    def test_fallback_dialog_respects_explicit_choices_and_cancel(self):
        import ctypes
        from unittest.mock import patch

        class MessageBoxStub:
            def __init__(self, result):
                self.result = result
            def __call__(self, *_args):
                return self.result

        cases = [
            (["primary", "secondary"], 6, "primary"),
            (["primary", "secondary"], 7, "secondary"),
            (["primary", "secondary"], 2, None),
            (["primary"], 1, "primary"),
            (["secondary"], 1, "secondary"),
            (["secondary"], 2, None),
            ([], 1, None),
        ]
        for free, response, expected in cases:
            with self.subTest(free=free, response=response):
                class FakeLibrary:
                    MessageBoxW = MessageBoxStub(response)
                with patch.object(ctypes, "WinDLL", return_value=FakeLibrary(), create=True):
                    self.assertEqual(picker.fallback_workspace_dialog(free), expected)

    @unittest.skipUnless(sys.platform == "win32", "Windows named mutex runtime")
    def test_picker_probes_existing_slots_without_reserving_or_creating_them(self):
        self.assertFalse(picker.workspace_is_open("primary", developer=True))
        self.assertFalse(picker.workspace_is_open("secondary", developer=True))
        handle = app.acquire_single_instance(workspace="primary", developer=True)
        try:
            self.assertTrue(picker.workspace_is_open("primary", developer=True))
            self.assertFalse(picker.workspace_is_open("secondary", developer=True))
            self.assertFalse(picker.workspace_is_open("primary", developer=False))
        finally:
            app.release_single_instance(handle)
        self.assertFalse(picker.workspace_is_open("primary", developer=True))

    def test_named_mutex_guards_slots_independently(self):
        a = picker.instance_mutex_name("primary")
        b = picker.instance_mutex_name("secondary")
        self.assertEqual(a, "Local\\MichelsLab_InstaCleanerPro_Desktop")
        self.assertNotEqual(a, b)
        self.assertEqual(b, a + "_SecondWindow")
        self.assertNotEqual(picker.instance_mutex_name("primary", developer=True), a)
        self.assertNotEqual(picker.instance_mutex_name("secondary", developer=True), b)

    def test_two_app_windows_have_different_chrome_user_data_dirs(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            app_html = root / "IG-Cleaner-Pro.html"
            chrome = root / "chrome.exe"
            cmds = [app.chrome_app_args(chrome, app_html,
                        picker.chrome_workspace_path(root, scope), 40000 + i,
                        "test-session-token-" + str(i))
                    for i, scope in enumerate(("primary", "secondary"))]
            self.assertNotEqual(cmds[0], cmds[1])
            for cmd in cmds:
                self.assertEqual(len([x for x in cmd if x.startswith("--app=")]), 1)
                self.assertEqual(len([x for x in cmd if x.startswith("--user-data-dir=")]), 1)
                self.assertNotIn("--new-tab", cmd)
            self.assertNotEqual(
                next(x for x in cmds[0] if x.startswith("--user-data-dir=")),
                next(x for x in cmds[1] if x.startswith("--user-data-dir=")),
            )

    def test_shared_legacy_journal_stays_owner_account_scoped_across_two_windows(self):
        # Two app frontends share the legacy canonical action journal deliberately.
        # Isolation comes from the owner+account digest, while the one shared
        # OS lock prevents racing old/new Windows action workers.
        from profile_counts_bridge import Collector
        from profile_actions import ActionRobot
        from robot_interlock import ActionLease, ActionSessionBusy
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            canonical=root / "profile-counts"
            a=Collector(canonical, root / "instagram-browser")
            b=Collector(canonical, root / "instagram-browser")
            a.owner="owner_42";a.account="ig_first_1234567"
            b.owner="owner_42";b.account="ig_second_123456"
            self.assertNotEqual(a.result_path(),b.result_path())
            actions_a=ActionRobot(a,canonical,root / "first-actions")
            actions_b=ActionRobot(b,canonical,root / "second-actions")
            self.assertNotEqual(
                actions_a._base_for(a.owner,a.account,"unfollow"),
                actions_b._base_for(b.owner,b.account,"unfollow"))
            self.assertEqual(
                actions_a._base_for(a.owner,a.account,"unfollow"),
                actions_b._base_for(a.owner,a.account,"unfollow"),
                "Same exact account must read the previous canonical WAL")
            lease=ActionLease(canonical).acquire()
            try:
                with self.assertRaises(ActionSessionBusy):
                    ActionLease(canonical).acquire()
            finally:
                lease.release()
            # No stored data or account journal is erased by this comparison.
            self.assertFalse(a.result_path().exists())
            self.assertFalse(b.result_path().exists())

    def test_native_html_contains_only_one_current_workspace(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.html"
            output = root / "app" / "IG-Cleaner-Pro.html"
            source.write_bytes(b"<html><body>" + b"X" * 101000 + b"</body></html>")
            app.prepare_html(source, output, automation_activity=True)
            native = output.read_text()
            self.assertIn("igcAutomationActivitySection", native)
            self.assertIn("igcActMorePeriods", native)
            self.assertNotIn("igcDualActionWorkspacePanel", native)
            self.assertNotIn("igcDawParallelOptIn", native)
            self.assertEqual(native.count("window.__igcAutomationActivityLoaded=true"), 1)
            original = output.read_bytes()
            app.prepare_html(source, output, automation_activity=True)
            self.assertEqual(original, output.read_bytes())
            app.prepare_html(source, output, automation_activity=False)
            self.assertEqual(output.read_bytes(), source.read_bytes())

    def test_product_exposes_actual_startup_account_choice_not_legacy_double_cards(self):
        chooser = (ROOT / "tools/windows_workspace_picker.py").read_text(encoding="utf-8")
        html = (ROOT / "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
        launcher = (ROOT / "tools/ig_cleaner_desktop.py").read_text(encoding="utf-8")
        self.assertIn("TaskDialogIndirect", chooser)
        self.assertIn("Primary account", chooser)
        self.assertIn("Second account", chooser)
        self.assertIn("select_workspace(developer=args.developer)", launcher)
        self.assertIn("acquire_single_instance(developer=args.developer, workspace=workspace)", launcher)
        for forbidden in ('id="igcDualSecondary"', 'class="igc-dual-workspace"',
                          "openOtherWorkspace(asWindow=false)", "IGC_WINDOW_PROFILE_KEY",
                          "igcDualActionWorkspacePanel"):
            self.assertNotIn(forbidden, html)
        for area in ("Analysis", "Actions", "Review", "History"):
            self.assertIn('id="igcAutomationTab' + area + '"', html)


if __name__ == "__main__":
    unittest.main()
