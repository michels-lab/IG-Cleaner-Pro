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
    'SHA256SUMS.txt',
    'tools/build_standalone_desktop_html.py',
    'desktop_html_artifact',
    'gh release view "$TAG"',
    'tests/standalone-desktop-contract.py',
):
    assert token in workflow, f"Generic release publisher token missing: {token}"

# Negative regression for repeated FINAL publication: older workflow edited
# existing GitHub release tags and overwrote all assets with --clobber.
# A successful rerun or stale request must never mutate official downloads.
publish_section=workflow.split("      - name: Publish normal GitHub release",1)[1].split(
    "      - name: Verify published release",1)[0]
assert 'if gh release view "$TAG" >/dev/null 2>&1; then' in publish_section
assert "Refusing to edit or overwrite published assets." in publish_section
assert "exit 1" in publish_section
assert 'gh release create "$TAG" dist/*' in publish_section
assert "gh release edit" not in publish_section
assert "gh release upload" not in publish_section
assert all("--clobber" not in line for line in publish_section.splitlines() if not line.lstrip().startswith("#"))

# GitHub must not publish a visually changed app on mere source/build success.
for token in (
    'rendered-ui-qa:',
    'needs: [release-request-gate, rendered-ui-qa, windows-robot, android-developer-qa]',
    'windows-robot:',
    'ig-cleaner-stable-windows-robot-',
    'IG-Cleaner-Pro-Automatic-Robot-Windows-v',
    'needs.windows-robot.result',
    "needs.rendered-ui-qa.result == 'success'",
    "android-developer-qa:",
    "needs.android-developer-qa.result == 'success'",
    "bash tools/run_android_developer_ui.sh",
    "ig-cleaner-final-stable-developer-android-",
    'tools/verify_android_visual_release_evidence.py',
    'tools/resolve_desktop_visual_artifact_dir.py',
    'EVIDENCE_DIR="$(python3 tools/resolve_desktop_visual_artifact_dir.py --artifact desktop-visual-evidence)"',
    '--artifact "$EVIDENCE_DIR"',
    '--html "$EVIDENCE_DIR/IG-Cleaner-Pro-standalone-rebuilt.html"',
    '--manifest "$EVIDENCE_DIR/michelslab-manifest.json"',
    'gh run download',
    '--commit "$GITHUB_SHA"',
):
    assert token in workflow, f"Release P0 missing protected visual approval: {token}"


# A real production-signed Android coexistence test is a hard publish gate.
# The emulator action invokes its `script` using /bin/sh, so strict bash
# syntax must be executed explicitly through bash (never inline sh + pipefail).
coinstall = (ROOT/"tools/verify_production_android_coinstall.sh").read_text(encoding="utf-8")
assert "script: bash tools/verify_production_android_coinstall.sh" in workflow
assert workflow.count("Prove both production-signed Android packages install side by side") == 1
for token in (
    "#!/usr/bin/env bash", "set -euo pipefail",
    "app-release.apk", "app-developer.apk",
    'adb install -r "$PUBLIC_APK"',
    'adb install -r "$DEVELOPER_APK"',
    'PUBLIC_PKG="com.michelslab.igcleaner"',
    'DEVELOPER_PKG="com.michelslab.igcleaner.developer"',
    'grep -Fxq "package:$PUBLIC_PKG"',
    'grep -Fxq "package:$DEVELOPER_PKG"',
    'adb shell am start -n "$component"',
    'adb shell dumpsys activity activities',
    'adb shell pidof "$package"',
    "topResumedActivity",
    "mResumedActivity",
    "stable >= 2",
    'grep -Fq "$package/"',
    'adb shell pm path "$PUBLIC_PKG"',
    'adb shell pm path "$DEVELOPER_PKG"',
):
    assert token in coinstall, "Signed Android device gate missing: "+token

# The sixth real publisher ran the signed Android emulator without usable
# hardware acceleration. Opt into available KVM before launching BOTH APKs,
# while keeping the actual emulator gate mandatory even on fallback hosts.
publish = workflow.split("\n  publish:\n", 1)[1]
kvm_step = publish.index("Enable Android emulator hardware acceleration for signed coexistence")
device_step = publish.index("Prove both production-signed Android packages install side by side")
assert kvm_step < device_step
assert "sudo chmod 666 /dev/kvm" in publish[kvm_step:device_step]
assert "test -r /dev/kvm && test -w /dev/kvm" in publish[kvm_step:device_step]
assert "script: bash tools/verify_production_android_coinstall.sh" in publish[device_step:]

# The owner-provided GraphQL Unfollow must be tested in the ACTUAL final
# Windows publisher, not merely in advisory CI or candidate preview.
# Fail closed if an agent drops any of these exact tests from release.yml.
owner_suite=workflow.index("Offline owner-reference Unfollow, durable WAL and real Chromium acceptance")
legacy_suite=workflow.index("Offline public/private Instagram action flows in real Chromium")
packaging_step=workflow.index("Build Windows executable with embedded Playwright driver")
assert owner_suite < legacy_suite < packaging_step
for required_test in (
    "test_instagram_unfollow_reference.py",
    "test_instagram_unfollow_chromium_e2e.py",
    "tests/owner-unfollow-transport.test.cjs",
    "Owner reference Unfollow and no-replay tests failed; refuse FINAL release.",
    "One-POST exact-target real Chromium Unfollow regression failed; refuse FINAL release.",
    "Supplied-JavaScript Unfollow transport contract failed; refuse FINAL release.",
):
    assert required_test in workflow[owner_suite:legacy_suite], (
        "Final Windows publisher omitted the owner-Unfollow safety gate: "+required_test
    )

# Changes to the FINAL publishing logic must run the real Windows preview
# (which already exercises owner-supplied Unfollow in actual Chromium).
preview=(ROOT/".github/workflows/profile-counts-windows-preview.yml").read_text(encoding="utf-8")
for event in ("push:", "pull_request:"):
    fragment=preview.split("\n  "+event+"\n", 1)[1]
    fragment=fragment.split("\n  pull_request:\n",1)[0] if event=="push:" else fragment.split("\npermissions:",1)[0]
    for tracked in (".github/workflows/release.yml", "tests/release-publisher-contract.py"):
        assert tracked in fragment, "FINAL publisher edits bypass integrated Windows QA: "+tracked

# The stable Windows publisher must match the exact tested integrated app,
# never silently regress to the removed legacy CMD + standalone collector.
for token in (
    'pyinstaller --clean --noconfirm --onefile --windowed',
    '--name InstaCleanerPro tools/ig_cleaner_desktop.py',
    'test_profile_actions_chromium.py',
    'test_native_desktop.py',
    'InstaCleanerPro.exe',
    'EXECUTABLE-SHA256.txt',
    'required = {"InstaCleanerPro.exe", "BUILD-INFO.txt", "EXECUTABLE-SHA256.txt", "README.txt",',
    'chrome-extension/manifest.json',
    'chrome-extension/collector.js',
):
    assert token in workflow, f"Integrated Windows release contract missing: {token}"
assert 'Copy-Item packaging/profile-counts/Start-Insta-Cleaner-Robot.cmd' not in workflow
assert 'pyinstaller --clean --noconfirm --onefile --collect-all playwright --name IGCleanerProfileCounts' not in workflow
assert manifest["channels"]["windowsRobot"]["installation"] == "inno-setup-per-user"
assert manifest["channels"]["windowsRobot"]["execution"].startswith("install Setup.exe")
assert manifest["channels"]["windowsRobot"]["artifactTemplate"] == "IG-Cleaner-Pro-Windows-Setup-v{version}.exe"
assert "tools/build_windows_installer.ps1" in workflow
assert "tools/test_windows_installer.ps1" in workflow
assert 'gh release view "$TAG" --json assets' in workflow
assert "IG-Cleaner-Pro-Windows-Setup-v" in workflow

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
