"""Negative release-contract fixtures for actual Android Home/complete About evidence.

Synthetic PNGs here only exercise the OFFLINE verifier. Official screenshots
must still come from installed native instrumentation on the exact source SHA.
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from collect_android_about_screenshots import EXPECTED, SIZES
from verify_android_visual_release_evidence import verify

SOURCE = "a" * 40


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AndroidReleaseEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.apk = self.root / "app-debug.apk"
        self.apk.write_bytes(b"offline-fixture-apk" * 40000)
        screenshots = self.root / "android" / "igc-ui-capture"
        screenshots.mkdir(parents=True)
        shots = []
        for index, name in enumerate(EXPECTED):
            surface, viewport, section = name[:-4].split("-")
            width, height = SIZES[viewport]
            image = Image.new("RGB", (width, height), (20 + 17*index, 28, 64))
            canvas = ImageDraw.Draw(image)
            for j in range(120):
                x = (j*41 + 13*index) % (width-60)
                y = (j*67 + 17*index) % (height-60)
                canvas.rectangle((x, y, x+55, y+37),
                                 fill=((j*31+index*23)%255, (j*47)%255, (j*59)%255))
            path = screenshots / name
            image.save(path)
            shots.append(dict(
                platform="android", surface=surface, viewport=viewport,
                section=section, path=name, width=width, height=height,
                sha256=sha(path), capture_method="installed-android-emulator",
                candidate_artifact_sha256=sha(self.apk)
            ))
        self.doc = dict(
            schema="michelslab-rendered-ui-v1",
            source_commit=SOURCE, artifact_sha256={"android": sha(self.apk)},
            screenshots=shots, human_visual_review={"decision": "PENDING"},
            device_acceptance="UNVERIFIED"
        )
        self.save()

    def save(self):
        (self.root / "manifest.json").write_text(json.dumps(self.doc), encoding="utf-8")

    def test_four_real_shape_evidence_passes_and_is_order_independent(self):
        verify(self.root, SOURCE)
        self.doc["screenshots"].reverse()
        self.save()
        verify(self.root, SOURCE)

    def test_old_eight_frame_contract_rejected(self):
        self.doc["screenshots"].extend(copy.deepcopy(self.doc["screenshots"]))
        self.save()
        with self.assertRaisesRegex(AssertionError, "four distinct"):
            verify(self.root, SOURCE)

    def test_duplicate_actual_pixels_rejected_even_if_claimed_digests_match(self):
        shots = self.doc["screenshots"]
        dst = self.root / "android/igc-ui-capture" / shots[1]["path"]
        src = self.root / "android/igc-ui-capture" / shots[0]["path"]
        dst.write_bytes(src.read_bytes())
        shots[1]["sha256"] = sha(dst)
        self.save()
        with self.assertRaisesRegex(AssertionError, "Duplicate screenshot bytes"):
            verify(self.root, SOURCE)

    def test_missing_or_unexpected_png_fails_closed(self):
        folder = self.root / "android/igc-ui-capture"
        (folder / EXPECTED[0]).unlink()
        with self.assertRaisesRegex(AssertionError, "Missing or unexpected"):
            verify(self.root, SOURCE)
        (folder / EXPECTED[0]).write_bytes(b"not-a-real-image")
        (folder / "about-compact-author.png").write_bytes(b"obsolete")
        with self.assertRaisesRegex(AssertionError, "Missing or unexpected"):
            verify(self.root, SOURCE)

    def test_wrong_source_apk_or_saved_human_review_is_rejected(self):
        with self.assertRaisesRegex(AssertionError, "wrong commit"):
            verify(self.root, "b" * 40)
        self.apk.write_bytes(b"replaced-apk" * 50000)
        with self.assertRaisesRegex(AssertionError, "APK differs"):
            verify(self.root, SOURCE)
        self.apk.write_bytes(b"offline-fixture-apk" * 40000)
        self.doc["human_visual_review"]["decision"] = "approved"
        self.save()
        with self.assertRaisesRegex(AssertionError, "never forge"):
            verify(self.root, SOURCE)

    def test_legacy_section_or_wrong_platform_rejected(self):
        self.doc["screenshots"][1]["section"] = "author"
        self.save()
        with self.assertRaisesRegex(AssertionError, "Old or mismatched"):
            verify(self.root, SOURCE)
        self.doc["screenshots"][1]["section"] = "complete"
        self.doc["screenshots"][1]["platform"] = "desktop"
        self.save()
        with self.assertRaisesRegex(AssertionError, "platform mismatch"):
            verify(self.root, SOURCE)

    def test_foreign_path_wrong_dimensions_or_bad_capture_origin_rejected(self):
        self.doc["screenshots"][0]["path"] = "../untrusted.png"
        self.save()
        with self.assertRaisesRegex(AssertionError, "path/identity mismatch"):
            verify(self.root, SOURCE)
        self.doc["screenshots"][0]["path"] = EXPECTED[0]
        self.doc["screenshots"][0]["width"] = 7
        self.save()
        with self.assertRaisesRegex(AssertionError, "metadata dimensions mismatch"):
            verify(self.root, SOURCE)
        self.doc["screenshots"][0]["width"] = SIZES["compact"][0]
        self.doc["screenshots"][0]["capture_method"] = "fake-browser-image"
        self.save()
        with self.assertRaisesRegex(AssertionError, "installed emulator"):
            verify(self.root, SOURCE)


if __name__ == "__main__":
    unittest.main()
