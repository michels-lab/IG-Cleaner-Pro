#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8"))
signing = json.loads((ROOT / "release/android-signing.json").read_text(encoding="utf-8"))
gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

import re
build_version_match = re.search(r'versionName = "([0-9]+\.[0-9]+)"', gradle)
assert build_version_match, "Android Gradle build version missing"
build_version = build_version_match.group(1)
expected_code=int(build_version.replace(".",""))
policy=manifest["releasePolicy"]
assert "v"+build_version in (policy["currentStableRelease"],policy["nextRelease"]), "Android build version must match current stable or governed next release"
request=json.loads((ROOT / ".michelslab/release-request.json").read_text(encoding="utf-8"))
if request.get("authorized"):
    assert request.get("version") == build_version, "Authorized release request must match signed Android build"

for token in (
    "IGC_ANDROID_KEYSTORE_PATH",
    "IGC_ANDROID_KEYSTORE_PASSWORD",
    "IGC_ANDROID_KEY_ALIAS",
    "IGC_ANDROID_KEY_PASSWORD",
    'create("release")',
    "releaseTaskRequested",
    'contains("assembleRelease"',
    "Production Android signing is required",
    f"versionCode = {expected_code}",
    f'versionName = "{build_version}"',
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
    "android_artifact",
    "artifactTemplate",
    "/certificate SHA-256 digest:/",
    "{print $NF; exit}",
):
    assert token in workflow, f"Stable Android release workflow contract missing: {token}"

assert signing["packageId"] == "com.michelslab.igcleaner"
assert signing["versionCode"] == expected_code
assert signing["versionName"] == build_version
assert signing["keyAlias"] == "ig-cleaner-pro"
assert signing["certificateSha256"] == "99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33"
assert signing["certificateValidUntil"] == "9999-12-31T04:00:39Z"
assert signing["keystorePolicy"] == "private-backup-only-never-commit"

android = manifest["channels"]["android"]
assert android["artifactTemplate"] == "IG-Cleaner-Pro-Android-v{version}.apk"
assert android["stableArtifactRequiresPersistentSigning"] is True
assert manifest["releasePolicy"]["stableGithubReleaseIncludesLatestValidatedAndroidApk"] is True
assert manifest["releasePolicy"]["genericPublisher"] == ".github/workflows/release.yml"

assert "*.jks" in gitignore
assert "*.keystore" in gitignore

print("Android production-signing contract passed.")
