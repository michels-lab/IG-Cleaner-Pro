#!/usr/bin/env python3
"""Fail-closed verification of real Android screenshot CI artifact before release.

Protected GitHub Environment *human* approval is checked separately by workflow.
This exact-SHA debug-build UI evidence is not the final production-signed APK
digest; do not represent it as signed APK device acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageStat


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root: Path, sha: str):
    f = root / "manifest.json"
    doc = json.loads(f.read_text(encoding="utf-8"))
    assert doc.get("source_commit") == sha, "Rendered visual test is from wrong commit"
    assert doc.get("human_visual_review", {}).get("decision") == "PENDING", (
        "CI must never forge its own human review"
    )
    apk = root / "app-debug.apk"
    assert apk.is_file() and apk.stat().st_size > 500_000, "No candidate APK in screenshot artifact"
    h = digest(apk)
    assert doc.get("artifact_sha256", {}).get("android") == h, "APK differs from captured candidate"
    shots = doc.get("screenshots", [])
    assert len(shots) == 6, "Missing one or more of six About screenshot captures"
    expected = {(v,p) for v in ("compact","wide") for p in ("author","studio","socials")}
    seen = set()
    hashes = {}
    for item in shots:
        key = (item.get("viewport"), item.get("section"))
        assert key in expected and key not in seen, f"Unexpected/duplicate screenshot: {key}"
        seen.add(key)
        assert item.get("capture_method") == "installed-android-emulator"
        assert item.get("candidate_artifact_sha256") == h, "Screenshot not tied to installed APK"
        p = root / "android" / "igc-ui-capture" / item["path"]
        assert p.is_file(), f"Screenshot missing from artifact: {p}"
        assert digest(p) == item.get("sha256"), "Screenshot checksum mismatch"
        with Image.open(p) as im:
            im.verify()
        with Image.open(p) as im:
            dim = (im.width, im.height)
            assert dim == (item.get("width"), item.get("height"))
            assert dim == ((720,1280) if item["viewport"] == "compact" else (1080,1920))
            assert max(ImageStat.Stat(im.convert("RGB").resize((64,64))).stddev) >= 9, "Blank screenshot"
        hsh = item["sha256"]
        assert hsh not in hashes or hashes[hsh] == item["viewport"], "Reused screenshot from another viewport"
        hashes[hsh] = item["viewport"]
    assert seen == expected
    print("PASS: real Android About screenshot coverage from 2 viewports, 3 sections, same SHA/APK")
    print("IMPORTANT: independent human protected environment approval is required in addition.")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--artifact",required=True,type=Path)
    parser.add_argument("--sha",required=True)
    a=parser.parse_args()
    verify(a.artifact,a.sha)
