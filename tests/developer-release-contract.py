#!/usr/bin/env python3
"""GRANADA P0: official Developer twins cannot silently disappear from release.

Source-only contract: does not require signing secrets, Instagram login or APK
builds. The gated release workflow performs real binary/signature validation.
"""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
read = lambda p: (root / p).read_text(encoding="utf-8")
m = json.loads(read("release/distribution-manifest.json"))
policy = m["releasePolicy"]
version = policy["nextRelease"][1:]
win = m["channels"]["windowsDeveloper"]
android = m["channels"]["androidDeveloper"]
workflow = read(".github/workflows/release.yml")
gradle = read("android/app/build.gradle.kts")
installer = read("packaging/windows-installer/InstaCleanerProDeveloper.iss")
win_builder = read("tools/build_windows_developer_installer.ps1")
win_smoke = read("tools/test_windows_developer_installer.ps1")
request = json.loads(read(".michelslab/release-request.json"))

assert policy["automaticPublishFromMain"] is False
assert policy["explicitManualPublishRequired"] is True
assert all(policy[k] is True for k in (
    "requireDeveloperTwinAssets", "requireDeveloperAndroidProductionSigning",
    "requireDeveloperWindowsIndependentInstallTest"
))
assert request.get("authorized") is not True or (
    request.get("version") == version and request.get("tag") == "v" + version
), "Authorized release request must match the governed candidate"

assert win["artifactTemplate"] == "IG-Cleaner-Pro-Windows-Developer-Setup-v{version}.exe"
assert win["artifact"] == win["artifactTemplate"].replace("{version}",version)
assert android["artifactTemplate"] == "IG-Cleaner-Pro-Android-Developer-v{version}.apk"
assert android["artifact"] == android["artifactTemplate"].replace("{version}",version)
assert android["packageId"] == "com.michelslab.igcleaner.developer"
assert android["signRequired"] is True
assert win["installerSource"] == "packaging/windows-installer/InstaCleanerProDeveloper.iss"
assert "AppId={{A8B19C6D-6C31-45B4-92DF-4B4DB20CB7DA}" in installer
assert "Insta Cleaner Pro Developer Edition" in installer
assert 'Parameters: "--developer"' in installer
assert "EXECUTABLE-SHA256.txt" in win_builder and "SHA256" in win_builder
assert "--developer" in win_smoke and "uninstall" in win_smoke.lower()

assert 'applicationIdSuffix = ".developer"' in gradle
assert 'versionNameSuffix = "-developer"' in gradle
assert "IGC_ANDROID_SIGNED_DEVELOPER_REQUIRED" in gradle
assert "signingConfig = signingConfigs.getByName(\"release\")" in gradle
assert "isDebuggable = false" in gradle
assert "(releaseTaskRequested || developerPublicationRequested)" in gradle
assert "initWith(getByName(\"debug\"))" in gradle, "Keep emulator QA available"
assert 'releaseSigningConfigured' in gradle

for phrase in (
    "requireDeveloperTwinAssets", "requireDeveloperAndroidProductionSigning",
    "requireDeveloperWindowsIndependentInstallTest",
    "IGC_ANDROID_SIGNED_DEVELOPER_REQUIRED",
    ":app:assembleRelease :app:assembleDeveloper",
    "com.michelslab.igcleaner.developer",
    "apksigner.txt", "dev-apksigner.txt",
    "DEV_CERT", 'test "$DEV_CERT" = "$ACTUAL"',
    "dev-badging.txt",
    'developerPublicationRequested',
    "android_developer_artifact", "windows_developer_artifact",
    "build_windows_developer_installer.ps1",
    "test_windows_developer_installer.ps1",
    "test_developer_live_probe.py",
    "developer-annotations-contract.test.cjs",
    "sha256sum --check SHA256SUMS.txt",
    "android-developer-qa:",
    "needs.android-developer-qa.result == 'success'",
    "bash tools/run_android_developer_ui.sh",
    "ig-cleaner-final-stable-developer-android-",
    "developer-release-contract.py",
    "IG-Cleaner-Pro-Windows-Developer-Setup-v*.exe.sha256",
    "gh release view",
):
    assert phrase in workflow, f"Stable release missing Developer gate: {phrase}"

for output in ("android_developer_artifact", "windows_developer_artifact"):
    # Assert the official release checks published GitHub assets, not only CI previews.
    assert re.search(
        r"gh release view \"\$TAG\" --json assets --jq.*" + output,
        workflow
    ), f"No final published asset verification for {output}"

# Real-account tests are Windows-only and never silently initiated from free text.
html = read("desktop/ig_cleaner_pro_v120_27_synced_companion.html")
bridge = read("tools/profile_counts_bridge.py")
for phrase in (
    "igcDevChatCopy", "igcDevActionStart", "igcDevActionPause",
    "LIVE_TEST:", "acknowledge_real_changes"
):
    assert phrase in html or phrase in bridge, f"Developer action consent missing {phrase}"
assert "dev_action_tests.start(request)" in bridge
assert "READ_ONLY_REAL_INSTAGRAM" in read("tools/developer_live_probe.py")

print("GRANADA Developer stable publisher, signing, independent install and authorization gates: PASS")
