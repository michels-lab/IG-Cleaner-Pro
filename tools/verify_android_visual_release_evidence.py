#!/usr/bin/env python3
"""Fail-closed verification of installed Android visual evidence before FINAL.

Uses the same four-file capture contract as the native extraction stage.
Debug-emulator screenshots are never represented as production-signed device
acceptance. The independent studio visual gate also runs after this check.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat
from collect_android_about_screenshots import EXPECTED, SIZES


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root: Path, sha: str):
    f = root / "manifest.json"
    doc = json.loads(f.read_text(encoding="utf-8"))
    assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha.lower()), (
        "Expected the full exact-source commit SHA"
    )
    assert doc.get("schema") == "michelslab-rendered-ui-v1", "Wrong source evidence schema"
    assert doc.get("source_commit") == sha, "Rendered visual test is from wrong commit"
    assert doc.get("human_visual_review", {}).get("decision") == "PENDING", (
        "CI must never forge its own human review"
    )
    apk = root / "app-debug.apk"
    assert apk.is_file() and apk.stat().st_size > 500_000, "No candidate APK in screenshot artifact"
    apk_hash = digest(apk)
    assert doc.get("artifact_sha256", {}).get("android") == apk_hash, (
        "APK differs from captured candidate"
    )
    assert tuple(EXPECTED) == (
        "home-compact-initial.png", "about-compact-complete.png",
        "home-wide-initial.png", "about-wide-complete.png",
    ), "Installed Android four-frame contract changed without release review"
    shots = doc.get("screenshots", [])
    assert isinstance(shots, list) and len(shots) == len(EXPECTED), (
        "Expected four distinct Home/complete About screenshots, compact and wide"
    )
    screenshot_dir = (root / "android" / "igc-ui-capture").resolve()
    assert screenshot_dir.is_dir(), "Missing native Android screenshot directory"
    assert {p.name for p in screenshot_dir.iterdir()} == set(EXPECTED), (
        "Missing or unexpected screenshot files in native Android evidence"
    )

    seen = set()
    pixel_hashes = set()
    for item in shots:
        assert isinstance(item, dict), "Screenshot entry must be an object"
        viewport = item.get("viewport")
        surface = item.get("surface")
        section = item.get("section")
        assert viewport in SIZES, "Unexpected Android viewport"
        assert (surface, section) in (("home", "initial"), ("about", "complete")), (
            "Old or mismatched Android screenshot section"
        )
        name = f"{surface}-{viewport}-{section}.png"
        assert name in EXPECTED, "Unexpected Android screenshot surface"
        key = (viewport, surface, section)
        assert key not in seen, f"Duplicate Android screenshot metadata: {key}"
        seen.add(key)
        assert item.get("path") == name, "Screenshot path/identity mismatch"
        assert item.get("platform") == "android", "Screenshot platform mismatch"
        assert item.get("capture_method") == "installed-android-emulator", (
            "Screenshot is not captured from running installed emulator app"
        )
        assert item.get("candidate_artifact_sha256") == apk_hash, (
            "Screenshot not tied to installed APK"
        )
        image = (screenshot_dir / name).resolve()
        assert image.is_relative_to(screenshot_dir) and image.is_file(), (
            "Screenshot missing from artifact or escapes native evidence root"
        )
        assert image.stat().st_size > 3000, "Implausibly small Android screenshot"
        image_hash = digest(image)
        assert image_hash == item.get("sha256"), "Screenshot checksum mismatch"
        assert image_hash not in pixel_hashes, "Duplicate screenshot bytes"
        pixel_hashes.add(image_hash)
        with Image.open(image) as im:
            im.verify()
        with Image.open(image) as im:
            dims = (im.width, im.height)
            assert dims == SIZES[viewport], f"Actual Android viewport mismatch: {dims}"
            assert dims == (item.get("width"), item.get("height")), (
                "Screenshot metadata dimensions mismatch"
            )
            assert max(ImageStat.Stat(im.convert("RGB").resize((64, 64))).stddev) >= 9, (
                "Blank or near-uniform screenshot"
            )
    assert seen == {
        ("compact", "home", "initial"), ("compact", "about", "complete"),
        ("wide", "home", "initial"), ("wide", "about", "complete"),
    }, "Missing one of four independent rendered Android surfaces"
    print("PASS: exactly four unique installed Android Home/complete About frames, exact SHA/APK")
    print("User visual review and physical Samsung acceptance remain separate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()
    verify(args.artifact, args.sha)
