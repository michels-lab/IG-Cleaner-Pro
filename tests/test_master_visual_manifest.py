#!/usr/bin/env python3
"""Unit contract for reuse of existing real runtime screenshot evidence."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from create_master_visual_manifest import create_manifest

COMMIT = "a" * 40


def digest(data):
    return hashlib.sha256(data).hexdigest()


class MasterVisualAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.artifact = self.root / "candidate.bin"
        self.artifact.write_bytes(b"real candidate content for binding test")
        self.hash = digest(self.artifact.read_bytes())

    def fixture(self, platform):
        screenshots = []
        root = self.root / ("android/igc-ui-capture" if platform == "android" else "")
        root.mkdir(parents=True, exist_ok=True)
        for viewport in ("compact", "wide"):
            for surface, section in (("home", "initial"),
                                     ("about", "complete" if platform == "android" else "initial")):
                name = f"{surface}-{viewport}-{section}.png"
                bytes_ = f"real screenshot reference {platform}:{viewport}:{surface}".encode()
                (root / name).write_bytes(bytes_)
                screenshots.append({
                    "platform": platform, "surface": surface,
                    "section": section, "viewport": viewport, "path": name,
                    "width": 720, "height": 1280, "sha256": digest(bytes_),
                    "capture_method": ("installed-android-emulator" if platform == "android" else "running-browser"),
                    "candidate_artifact_sha256": self.hash,
                })
        doc = {
            "schema": "michelslab-rendered-ui-v1" if platform == "android"
                      else "igc-desktop-runtime-visual-v1",
            "source_commit": COMMIT,
            "screenshots": screenshots,
        }
        if platform == "android":
            doc["artifact_sha256"] = {"android": self.hash}
        else:
            doc["html_sha256"] = self.hash
        source = self.root / "manifest.json"
        source.write_text(json.dumps(doc))
        return source, doc

    def test_both_platforms_reuse_existing_images_and_bind_real_artifact(self):
        for platform in ("android", "desktop"):
            with self.subTest(platform=platform):
                source, _ = self.fixture(platform)
                result = create_manifest(platform, source, self.artifact, COMMIT)
                self.assertEqual(result["schema"], "michelslab-rendered-ui-v1")
                self.assertEqual(result["artifact_sha256"][platform], self.hash)
                self.assertEqual(len(result["screenshots"]), 4)
                self.assertEqual({x["surface"] for x in result["screenshots"]}, {"home", "about"})
                self.assertEqual({x["viewport"] for x in result["screenshots"]}, {"compact", "wide"})
                self.assertEqual(result["human_visual_review"]["decision"], "PENDING")

    def test_android_four_frames_have_complete_about_section_only(self):
        source, doc = self.fixture("android")
        result = create_manifest("android", source, self.artifact, COMMIT)
        self.assertEqual({shot["section"] for shot in result["screenshots"] if shot["surface"] == "about"}, {"complete"})
        self.assertEqual(len(result["screenshots"]), 4)

        # Old capture contracts cannot masquerade as real complete About frames.
        doc["screenshots"][1]["section"] = "author"
        source.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Expected one real android/compact/about screenshot"):
            create_manifest("android", source, self.artifact, COMMIT)

    def test_extra_legacy_android_frame_is_rejected(self):
        source, doc = self.fixture("android")
        doc["screenshots"].append(dict(doc["screenshots"][1], section="socials"))
        source.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "exactly four"):
            create_manifest("android", source, self.artifact, COMMIT)

    def test_identical_pixels_under_different_android_names_fail_closed(self):
        source, doc = self.fixture("android")
        original = (self.root / "android/igc-ui-capture/home-compact-initial.png").read_bytes()
        target = self.root / "android/igc-ui-capture/about-compact-complete.png"
        target.write_bytes(original)
        doc["screenshots"][1]["sha256"] = digest(original)
        source.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate actual screenshots"):
            create_manifest("android", source, self.artifact, COMMIT)

    def test_foreign_candidate_artifact_fails_closed(self):
        source, _ = self.fixture("android")
        self.artifact.write_bytes(b"another APK")
        with self.assertRaisesRegex(ValueError, "not bound"):
            create_manifest("android", source, self.artifact, COMMIT)

    def test_tampered_image_fails_closed(self):
        source, _ = self.fixture("desktop")
        (self.root / "home-compact-initial.png").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            create_manifest("desktop", source, self.artifact, COMMIT)

    def test_wrong_commit_fails_closed(self):
        source, _ = self.fixture("desktop")
        with self.assertRaisesRegex(ValueError, "different source commit"):
            create_manifest("desktop", source, self.artifact, "b" * 40)


if __name__ == "__main__":
    unittest.main()
