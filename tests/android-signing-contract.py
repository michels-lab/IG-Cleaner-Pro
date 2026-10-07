#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/release-v12034.yml").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8"))
signing = json.loads((ROOT / "release/android-signing.json").read_text(encoding="utf-8"))
gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

for token in (
    "IGC_ANDROID_KEYSTORE_PATH",
    "IGC_ANDROID_KEYSTORE_PASSWORD",
    "IGC_ANDROID_KEY_ALIAS",
    "IGC_ANDROID_KEY_PASSWORD",
    'create("release")',
    "releaseTaskRequested",
    'contains("assembleRelease"',
    "Production Android signing is required",
):
    assert token in gradle, f"Release signing Gradle contract missing: {token}"

for token in (
    "secrets.IGC_ANDROID_KEYSTORE_B64",
    "secrets.IGC_ANDROID_KEYSTORE_PASSWORD",
    "secrets.IGC_ANDROID_KEY_ALIAS",
    "secrets.IGC_ANDROID_KEY_PASSWORD",
    ":app:assembleRelease",
    "apksigner",
    "aapt",
    "IG-Cleaner-Pro-Android-v120.34.apk",
):
    assert token in workflow, f"Stable Android release workflow contract missing: {token}"

assert signing["packageId"] == "com.michelslab.igcleaner"
assert signing["versionCode"] == 12034
assert signing["versionName"] == "120.34"
assert signing["keyAlias"] == "ig-cleaner-pro"
assert signing["certificateSha256"] == "2E47E4438DAC3E3ED5CFF36E31689BE21EE27B08CCF2A40E0E7209CC57D72A14"
assert signing["certificateValidUntil"] == "2054-02-22T03:44:28Z"
assert signing["keystorePolicy"] == "private-backup-only-never-commit"

android = manifest["channels"]["android"]
assert android["artifact"] == "IG-Cleaner-Pro-Android-v120.34.apk"
assert android["stableArtifactRequiresPersistentSigning"] is True
assert manifest["releasePolicy"]["stableGithubReleaseIncludesLatestValidatedAndroidApk"] is True

assert "*.jks" in gitignore
assert "*.keystore" in gitignore

print("Android production-signing contract passed.")
