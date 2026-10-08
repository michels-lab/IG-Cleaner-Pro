#!/usr/bin/env python3
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
workflow=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
manifest=json.loads((ROOT/"release/distribution-manifest.json").read_text(encoding="utf-8"))
request=json.loads((ROOT/".michelslab/release-request.json").read_text(encoding="utf-8"))

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

# GitHub must not publish a visually changed app on mere source/build success.
for token in (
    'visual-release-approval:',
    'environment: visual-release-approval',
    'required_reviewers',
    'needs: [release-request-gate, visual-release-approval]',
    'tools/verify_android_visual_release_evidence.py',
    '--commit "$GITHUB_SHA"',
):
    assert token in workflow, f"Release P0 missing protected visual approval: {token}"

desktop=manifest["channels"]["desktop"]
android=manifest["channels"]["android"]
policy=manifest["releasePolicy"]

assert desktop["artifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.zip"
assert android["artifactTemplate"]=="IG-Cleaner-Pro-Android-v{version}.apk"
assert policy["genericPublisher"]==".github/workflows/release.yml"
assert policy["explicitManualPublishRequired"] is True
assert policy["automaticPublishFromMain"] is False
assert policy["githubPrerelease"] is False

current=policy["currentStableRelease"]
next_release=policy["nextRelease"]
assert current.startswith("v") and next_release.startswith("v")
assert current != next_release

status=request.get("status")
authorized=request.get("authorized")
tag=str(request.get("tag",""))

if authorized:
    # A live release request must point only at the governed next release.
    assert status in ("requested","authorized")
    assert tag == next_release
    assert request.get("version") == next_release.removeprefix("v")
    assert request.get("requested_channel") == "stable"
    assert request.get("github_prerelease") is False
else:
    # Between releases, the last request is retained as immutable publication evidence.
    assert status == "published"
    assert tag == current
    assert request.get("version") == current.removeprefix("v")
    assert request.get("published_run")
    assert request.get("published_commit")

print("Generic release publisher contract passed.")
