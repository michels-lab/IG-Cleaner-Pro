"""Native-only dual-account action panel injection contracts. No network."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ig_cleaner_desktop import prepare_html
from dual_action_windows_ui import DUAL_ACTION_PANEL


class DualActionWindowsPanelTests(unittest.TestCase):
    def test_native_only_overlay_preserves_original_and_repeated_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, native, developer = root / "source.html", root / "Windows.html", root / "Developer.html"
            source.write_bytes(b"<html><body>" + (b"X" * 101000) + b"</body></html>")
            original = source.read_bytes()
            prepare_html(source, native, dual_action_panel=True)
            result = native.read_bytes()
            self.assertIn(b"igcDualActionWorkspacePanel", result)
            self.assertIn(b"igcDawConfigure", result)
            self.assertEqual(result.count(b"igcDualActionWorkspacePanel"), 3)
            self.assertTrue(result.endswith(b"</body></html>"))
            self.assertEqual(source.read_bytes(), original)
            modified = native.stat().st_mtime_ns
            prepare_html(source, native, dual_action_panel=True)
            self.assertEqual(native.stat().st_mtime_ns, modified)
            prepare_html(source, developer)
            self.assertEqual(developer.read_bytes(), original)
            self.assertNotIn(b"igcDualActionWorkspacePanel", developer.read_bytes())

    def test_fail_closed_when_source_missing_closing_html_or_overlay_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            source, target = Path(temp) / "src", Path(temp) / "dest"
            target.write_bytes(b"KEEP")
            source.write_bytes(b"X" * 100001)
            with self.assertRaisesRegex(ValueError, "robots dobles"):
                prepare_html(source, target, dual_action_panel=True)
            self.assertEqual(target.read_bytes(), b"KEEP")
            source.write_bytes(b"<html><body>" + (b"X" * 100001)
                               + b"igcDualActionWorkspacePanel</body></html>")
            with self.assertRaisesRegex(ValueError, "robots dobles"):
                prepare_html(source, target, dual_action_panel=True)
            self.assertEqual(target.read_bytes(), b"KEEP")

    def test_panel_must_never_start_auto_unfollow_or_reuse_wrong_account(self):
        self.assertNotIn("start-one", DUAL_ACTION_PANEL)
        self.assertIn("action-workspace-review:", DUAL_ACTION_PANEL)
        self.assertIn("action-workspace-pause:", DUAL_ACTION_PANEL)
        self.assertIn("acknowledge_serial_actions:true", DUAL_ACTION_PANEL)
        self.assertIn("read_only_consent:true", DUAL_ACTION_PANEL)
        self.assertIn("IGC_INSTAGRAM_PROFILES", DUAL_ACTION_PANEL)
        self.assertNotIn("eval(", DUAL_ACTION_PANEL)
        self.assertNotIn("localStorage.setItem(", DUAL_ACTION_PANEL)
        self.assertNotIn("window.open(", DUAL_ACTION_PANEL)
        self.assertIn("textContent", DUAL_ACTION_PANEL)
        self.assertIn("max-width:650px", DUAL_ACTION_PANEL)


if __name__ == "__main__":
    unittest.main()
