"""GRANADA #12: debug-app private Android screenshots, never fake or partial QA."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from collect_android_about_screenshots import collect, EXPECTED, SIZES, PNG_MAGIC


def sample_png(viewport):
    # Transfer fixture only. Real-image pixels are separately checked by
    # android_about_visual_evidence.py against the installed debug APK.
    width, height = SIZES[viewport]
    return PNG_MAGIC + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height) + b"fixture" * 520


class PrivateAndroidEvidenceTests(unittest.TestCase):
    def test_all_eight_private_files_are_required_and_staged_atomically(self):
        requested = []
        def pretend(command, **kwargs):
            requested.append(command)
            name = command[-1].rsplit("/", 1)[-1]
            return SimpleNamespace(returncode=0, stdout=sample_png(name.split("-")[1]), stderr=b"")
        with tempfile.TemporaryDirectory() as root, patch(
            "collect_android_about_screenshots.subprocess.run", side_effect=pretend
        ):
            output = Path(root) / "artifacts" / "igc-ui-capture"
            files = collect("adb", "com.michelslab.igcleaner.beta", output)
            self.assertEqual(len(files), 8)
            self.assertEqual([f.name for f in files], list(EXPECTED))
            self.assertEqual(set(p.name for p in output.iterdir()), set(EXPECTED))
            self.assertFalse(list(output.parent.glob(".android-evidence-*")))
            for cmd in requested:
                self.assertEqual(cmd[:4], ["adb", "exec-out", "run-as",
                                           "com.michelslab.igcleaner.beta"])
                self.assertEqual(cmd[4], "cat")
                self.assertTrue(cmd[5].startswith("files/igc-ui-capture/"))

    def test_missing_private_screenshot_must_not_publish_partial_results(self):
        calls = []
        def pretend(command, **kwargs):
            calls.append(command)
            if len(calls) == 6:
                return SimpleNamespace(returncode=1, stdout=b"", stderr=b"Permission denied")
            return SimpleNamespace(returncode=0, stdout=sample_png(command[-1].split("-")[1]), stderr=b"")
        with tempfile.TemporaryDirectory() as root, patch(
            "collect_android_about_screenshots.subprocess.run", side_effect=pretend
        ):
            output = Path(root) / "igc-ui-capture"
            with self.assertRaisesRegex(RuntimeError, "Permission denied"):
                collect("adb", "com.michelslab.igcleaner.beta", output)
            self.assertFalse(output.exists())
            self.assertFalse(list(Path(root).glob(".android-evidence-*")))

    def test_wrong_viewport_or_placeholder_bytes_are_rejected(self):
        for bad in (b"not a screenshot" * 300, sample_png("wide")):
            with self.subTest(bad=bad[:8]), tempfile.TemporaryDirectory() as root:
                def pretend(command, **kwargs):
                    name = command[-1].rsplit("/", 1)[-1]
                    value = bad if name == EXPECTED[0] else sample_png(name.split("-")[1])
                    return SimpleNamespace(returncode=0, stdout=value, stderr=b"")
                with patch("collect_android_about_screenshots.subprocess.run", side_effect=pretend):
                    out = Path(root) / "igc-ui-capture"
                    with self.assertRaisesRegex(ValueError, "PNG|viewport"):
                        collect("adb", "com.michelslab.igcleaner.beta", out)
                    self.assertFalse(out.exists())

    def test_existing_evidence_is_never_replaced_or_reused(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root) / "igc-ui-capture"
            out.mkdir()
            marker = out / "owner.txt"
            marker.write_text("do not touch", encoding="utf-8")
            with patch("collect_android_about_screenshots.subprocess.run") as run:
                with self.assertRaisesRegex(ValueError, "stale Android screenshot"):
                    collect("adb", "com.michelslab.igcleaner.beta", out)
                run.assert_not_called()
            self.assertEqual(marker.read_text(), "do not touch")


if __name__ == "__main__":
    unittest.main()
