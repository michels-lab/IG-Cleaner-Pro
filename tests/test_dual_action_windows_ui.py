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
            self.assertEqual(result.count(b"window.__igcDualActionPanelLoaded=true"), 1)
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
        self.assertIn("continueSaved.addEventListener('click'", DUAL_ACTION_PANEL)
        self.assertIn("api('start-one'", DUAL_ACTION_PANEL)
        self.assertIn("record.targets", DUAL_ACTION_PANEL)
        self.assertIn("new Set(targets).size", DUAL_ACTION_PANEL)
        self.assertIn("batch_id:record.id", DUAL_ACTION_PANEL)
        self.assertIn("followers_evidence:task.value==='unfollow'", DUAL_ACTION_PANEL)
        self.assertIn("se conservarán los clics inciertos".lower()[0:7], DUAL_ACTION_PANEL.lower())
        self.assertIn("action-workspace-review:", DUAL_ACTION_PANEL)
        self.assertIn("action-workspace-pause:", DUAL_ACTION_PANEL)
        # Default is serial. Parallel is a separate explicit opt-in, never an
        # implicit consequence of merely linking two Chrome accounts.
        self.assertIn("opt.type='checkbox'", DUAL_ACTION_PANEL)
        self.assertIn("opt.id='igcDawParallelOptIn'", DUAL_ACTION_PANEL)
        self.assertIn("acknowledge_serial_actions:!parallel", DUAL_ACTION_PANEL)
        self.assertIn("acknowledge_parallel_actions:parallel", DUAL_ACTION_PANEL)
        self.assertIn("parallel_actions_consent:parallel", DUAL_ACTION_PANEL)
        self.assertIn("dual-action-workspaces-parallel:", DUAL_ACTION_PANEL)
        self.assertIn("parallel_action_confirmation", DUAL_ACTION_PANEL)
        self.assertIn("parallel-action-workspace-start:", DUAL_ACTION_PANEL)
        self.assertIn("response.parallel_mutations_enabled!==parallel", DUAL_ACTION_PANEL)
        self.assertIn("id='igcDawCompletionModal'", DUAL_ACTION_PANEL)
        self.assertIn("setInterval(pollStatus,4000)", DUAL_ACTION_PANEL)
        self.assertIn("api('review-one'", DUAL_ACTION_PANEL)
        self.assertIn("completionAcknowledged", DUAL_ACTION_PANEL)
        self.assertIn("displayNextCompletion()", DUAL_ACTION_PANEL)
        self.assertIn("No se aprobó ni repitió ningún clic.", DUAL_ACTION_PANEL)
        self.assertIn("read_only_consent:true", DUAL_ACTION_PANEL)
        self.assertIn("IGC_INSTAGRAM_PROFILES", DUAL_ACTION_PANEL)
        self.assertNotIn("eval(", DUAL_ACTION_PANEL)
        self.assertNotIn("localStorage.setItem(", DUAL_ACTION_PANEL)
        self.assertNotIn("window.open(", DUAL_ACTION_PANEL)
        self.assertIn("textContent", DUAL_ACTION_PANEL)
        self.assertIn("max-width:650px", DUAL_ACTION_PANEL)


if __name__ == "__main__":
    unittest.main()
