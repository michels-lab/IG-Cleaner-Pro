#!/usr/bin/env python3
"""Immutable signed stable publisher contract. No Developer Editions per owner."""
import json
from pathlib import Path
from release_artifact_policy import artifact_release_tag

ROOT=Path(__file__).resolve().parents[1]
read=lambda p:(ROOT/p).read_text(encoding="utf-8")
workflow=read(".github/workflows/release.yml")
manifest=json.loads(read("release/distribution-manifest.json"))
request=json.loads(read(".michelslab/release-request.json"))
tag=artifact_release_tag(manifest,request)
policy=manifest["releasePolicy"]
assert policy["currentStableRelease"] != policy["nextRelease"]
assert tag==policy["nextRelease"] if request.get("authorized") else tag==policy["currentStableRelease"]
assert policy["explicitManualPublishRequired"] is True
assert policy["automaticPublishFromMain"] is False
assert policy["githubPrerelease"] is False

for token in (
  '.michelslab/release-request.json',
  'policy["nextRelease"] == tag',
  'request.get("authorized") is True',
  'request.get("status") in ("requested","authorized")',
  'artifactTemplate', 'IGC_ANDROID_KEYSTORE_B64',
  ':app:assembleRelease', 'certificate SHA-256 digest:',
  'gh release create', 'SHA256SUMS.txt',
  'tools/build_standalone_desktop_html.py',
  'desktop_html_artifact', 'gh release view "$TAG"',
  'tests/standalone-desktop-contract.py',
):
    assert token in workflow,"Stable publisher token missing: "+token

# A retry must never overwrite a FINAL release tag, assets, checksums or notes.
pub=workflow.split('      - name: Publish normal GitHub release',1)[1].split(
    '      - name: Verify published release',1)[0]
for token in ('if gh release view "$TAG" >/dev/null 2>&1; then',
              'Refusing to edit or overwrite published assets.','exit 1',
              'gh release create "$TAG" dist/*','tools/release_readiness_gate.py'):
    assert token in pub,"Immutable FINAL publisher contract missing: "+token
for forbidden in ("gh release edit","gh release upload","--clobber"):
    assert forbidden not in pub,"Unexpected mutable FINAL publisher operation: "+forbidden

# Exact source Windows installer, Chromium, independent rendered UI and
# production-signed stable Android must all pass before publishing.
for token in (
    'rendered-ui-qa:', 'windows-robot:',
    'needs: [release-request-gate, rendered-ui-qa, windows-robot]',
    "needs.rendered-ui-qa.result == 'success'",
    "needs.windows-robot.result == 'success'",
    'tools/verify_android_visual_release_evidence.py',
    'tools/resolve_desktop_visual_artifact_dir.py',
    'gh run download',
    '--commit "$GITHUB_SHA"',
    'ig-cleaner-stable-windows-robot-',
    'pyinstaller --clean --noconfirm --onefile --windowed',
    '--name InstaCleanerPro tools/ig_cleaner_desktop.py',
    'tools/build_windows_installer.ps1',
    'tools/test_windows_installer.ps1',
    'test_profile_actions_chromium.py',
    'test_instagram_unfollow_reference.py',
    'test_instagram_unfollow_chromium_e2e.py',
    'tests/owner-unfollow-transport.test.cjs',
    'test_native_desktop.py',
    'EXECUTABLE-SHA256.txt',
    'test_android_signed_coinstall_runtime.py',
    'script: bash tools/verify_production_android_coinstall.sh',
    'sudo chmod 666 /dev/kvm',
    '(cd dist && sha256sum --check SHA256SUMS.txt)',
    'gh release view "$TAG" --json assets',
):
    assert token in workflow, "Production safety or artifact proof missing: "+token

installer_test=workflow.index("Offline owner-reference Unfollow, durable WAL and real Chromium acceptance")
chromium_test=workflow.index("Offline public/private Instagram action flows in real Chromium")
build=workflow.index("Build Windows executable with embedded Playwright driver")
assert installer_test<chromium_test<build

# Owner withdrew all developer binaries; test that no orphan Developer
# build/release job was silently kept as a condition of public release.
for prohibited in (
    "android-developer-qa:", "needs.android-developer-qa",
    "android_developer_artifact", "windows_developer_artifact",
    ":app:assembleDeveloper", "app-developer.apk",
    "build_windows_developer_installer.ps1",
    "test_windows_developer_installer.ps1",
    "Developer Edition — independent Windows installation:"
):
    assert prohibited not in workflow,"Retired Developer product got back into publisher: "+prohibited
for key in ("requireDeveloperTwinAssets",
            "requireDeveloperAndroidProductionSigning",
            "requireDeveloperWindowsIndependentInstallTest"):
    assert policy[key] is False
assert "androidDeveloper" not in manifest["channels"]
assert "windowsDeveloper" not in manifest["channels"]

signed=read("tools/verify_production_android_coinstall.sh")
for token in ("#!/usr/bin/env bash","set -euo pipefail",
              'PUBLIC_APK="android/app/build/outputs/apk/release/app-release.apk"',
              'adb install -r "$PUBLIC_APK"',
              'PUBLIC_PKG="com.michelslab.igcleaner"',
              'adb shell am start -n "$component"',
              'adb shell dumpsys activity activities',
              'adb shell pidof "$package"',
              'stable >= 2',
              'adb shell pm path "$PUBLIC_PKG"'):
    assert token in signed,"Production Android installed launch proof missing: "+token
assert "DEVELOPER_APK" not in signed

# Release payload must match the exact candidate metadata.
desktop=manifest["channels"]["desktop"]
android=manifest["channels"]["android"]
assert desktop["artifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.zip"
assert desktop["primaryArtifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.html"
assert desktop["primaryArtifact"]==f"IG-Cleaner-Pro-Desktop-{tag}.html"
assert desktop["artifact"]==f"IG-Cleaner-Pro-Desktop-{tag}.zip"
assert desktop["standaloneOffline"] is True
assert android["artifact"]==f"IG-Cleaner-Pro-Android-{tag}.apk"
assert android["artifactTemplate"]=="IG-Cleaner-Pro-Android-v{version}.apk"
assert policy["genericPublisher"]==".github/workflows/release.yml"
assert manifest["channels"]["windowsRobot"]["installation"]=="inno-setup-per-user"

# Source changes in FINAL publisher must be tested by Windows preview.
preview=read(".github/workflows/profile-counts-windows-preview.yml")
for key in (".github/workflows/release.yml","tests/release-publisher-contract.py"):
    assert key in preview

print("PASS: stable-only immutable final publisher; exact Windows + signed Android + rendered UI gates")
