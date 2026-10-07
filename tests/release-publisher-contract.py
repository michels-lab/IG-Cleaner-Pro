#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
workflow=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
manifest=json.loads((ROOT/"release/distribution-manifest.json").read_text(encoding="utf-8"))

assert "v120.34" not in workflow, "Generic publisher must not be tied to v120.34"
for token in (
    '.michelslab/release-request.json',
    'policy["nextRelease"] == tag',
    'request.get("authorized") is True',
    'request.get("status") in ("requested","authorized")',
    'artifactTemplate',
    'IGC_ANDROID_KEYSTORE_B64',
    ':app:assembleRelease',
    'certificate SHA-256 digest:',
    'gh release create',
    'gh release upload',
    'SHA256SUMS.txt',
):
    assert token in workflow, f"Generic release publisher token missing: {token}"

assert manifest["channels"]["desktop"]["artifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.zip"
assert manifest["channels"]["android"]["artifactTemplate"]=="IG-Cleaner-Pro-Android-v{version}.apk"
assert manifest["releasePolicy"]["genericPublisher"]==".github/workflows/release.yml"

print("Generic release publisher contract passed.")
