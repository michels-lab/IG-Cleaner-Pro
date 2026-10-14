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
    'tools/build_standalone_desktop_html.py',
    'desktop_html_artifact',
    'gh release view "$TAG"',
    'tests/standalone-desktop-contract.py',
):
    assert token in workflow, f"Generic release publisher token missing: {token}"

# GitHub must not publish a visually changed app on mere source/build success.
for token in (
    'rendered-ui-qa:',
    'needs: [release-request-gate, rendered-ui-qa, windows-robot]',
    'windows-robot:',
    'ig-cleaner-stable-windows-robot-',
    'IG-Cleaner-Pro-Automatic-Robot-Windows-v',
    'needs.windows-robot.result',
    "needs.rendered-ui-qa.result == 'success'",
    'tools/verify_android_visual_release_evidence.py',
    'gh run download',
    '--commit "$GITHUB_SHA"',
):
    assert token in workflow, f"Release P0 missing protected visual approval: {token}"


# The stable Windows publisher must match the exact tested integrated app,
# never silently regress to the removed legacy CMD + standalone collector.
for token in (
    'pyinstaller --clean --noconfirm --onefile --windowed',
    '--name InstaCleanerPro tools/ig_cleaner_desktop.py',
    'test_profile_actions_chromium.py',
    'test_native_desktop.py',
    'InstaCleanerPro.exe',
    'EXECUTABLE-SHA256.txt',
    'required = {"InstaCleanerPro.exe", "BUILD-INFO.txt", "EXECUTABLE-SHA256.txt", "README.txt"}',
):
    assert token in workflow, f"Integrated Windows release contract missing: {token}"
assert 'Copy-Item packaging/profile-counts/Start-Insta-Cleaner-Robot.cmd' not in workflow
assert 'pyinstaller --clean --noconfirm --onefile --collect-all playwright --name IGCleanerProfileCounts' not in workflow
assert manifest["channels"]["windowsRobot"]["execution"] == "double-click InstaCleanerPro.exe (bundled UI + local robot)"

desktop=manifest["channels"]["desktop"]
android=manifest["channels"]["android"]
policy=manifest["releasePolicy"]

assert desktop["artifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.zip"
assert desktop["primaryArtifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.html"
assert desktop["primaryFormat"]=="html"
assert desktop["standaloneOffline"] is True
assert desktop["zipSecondary"] is True
assert desktop["primaryArtifact"]==f"IG-Cleaner-Pro-Desktop-{policy['nextRelease']}.html"
assert desktop["artifact"]==f"IG-Cleaner-Pro-Desktop-{policy['nextRelease']}.zip"
assert android["artifact"]==f"IG-Cleaner-Pro-Android-{policy['nextRelease']}.apk"
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
