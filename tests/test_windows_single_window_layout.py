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

    def test_native_choice_maps_each_button_and_cancel_without_side_effects(self):
        import ctypes
        from unittest.mock import patch

        class TaskDialogStub:
            def __init__(self, selected):
                self.selected = selected
            def __call__(self, config, output, *_args):
                self_config = config._obj
                assert self_config.cButtons == 2
                assert self_config.nDefaultButton == 101
                assert "cuenta" in self_config.pszMainInstruction.lower()
                ctypes.cast(output, ctypes.POINTER(ctypes.c_int)).contents.value = self.selected
                return 0

        class FakeLibrary:
            def __init__(self, selected):
                self.TaskDialogIndirect = TaskDialogStub(selected)

        for selected, expected in ((101, "primary"), (102, "secondary"), (2, None)):
            with self.subTest(button=selected):
                with patch.object(picker.sys, "platform", "win32"), \\
                     patch.object(ctypes, "WinDLL", return_value=FakeLibrary(selected),
                                  create=True):
                    self.assertEqual(picker.select_workspace(), expected)

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
        self.assertIn("Cuenta principal", chooser)
        self.assertIn("Segunda cuenta", chooser)
        self.assertIn("select_workspace()", launcher)
        self.assertIn("acquire_single_instance(developer=args.developer, workspace=workspace)", launcher)
        for forbidden in ('id="igcDualSecondary"', 'class="igc-dual-workspace"',
                          "openOtherWorkspace(asWindow=false)", "IGC_WINDOW_PROFILE_KEY",
                          "igcDualActionWorkspacePanel"):
            self.assertNotIn(forbidden, html)
        for area in ("Analysis", "Actions", "Review", "History"):
            self.assertIn('id="igcAutomationTab' + area + '"', html)


if __name__ == "__main__":
    unittest.main()
