#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
workflow = (ROOT / ".github/workflows/release-v12034.yml").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8"))
signing = json.loads((ROOT / "release/android-signing.json").read_text(encoding="utf-8"))
# Stable signer certificate is intentionally valid through year 9999 (practical non-expiring maximum).
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
    "tools/extract_apksigner_certificate_sha256.py",
):
    assert token in workflow, f"Stable Android release workflow contract missing: {token}"

assert signing["packageId"] == "com.michelslab.igcleaner"
assert signing["versionCode"] == 12034
assert signing["versionName"] == "120.34"
assert signing["keyAlias"] == "ig-cleaner-pro"
assert signing["certificateSha256"] == "99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33"
assert signing["certificateValidUntil"] == "9999-12-31T04:00:39Z"
assert signing["keystorePolicy"] == "private-backup-only-never-commit"
assert "awk -F': ' '/certificate SHA-256 digest:/{print $2; exit}'" not in workflow

parser_path = ROOT / "tools/extract_apksigner_certificate_sha256.py"
spec = importlib.util.spec_from_file_location("apksigner_cert_parser", parser_path)
parser = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(parser)

expected_lower = signing["certificateSha256"].lower()
colonized = ":".join(expected_lower[i : i + 2] for i in range(0, len(expected_lower), 2))
samples = (
    f"Signer #1 certificate SHA-256 digest: {expected_lower}\n",
    f"V3.0 Signer: certificate SHA-256 digest: {expected_lower}\n",
    f"V3.0 Signer: certificate SHA-256 digest: {colonized}\n"
    f"V3.0 Signer: public key SHA-256 digest: {'0' * 64}\n",
)
for sample in samples:
    assert parser.extract_certificate_sha256(sample) == expected_lower

try:
    parser.extract_certificate_sha256("V3.0 Signer: public key SHA-256 digest: " + ("0" * 64))
except ValueError:
    pass
else:
    raise AssertionError("Parser accepted public-key digest without a certificate digest")

android = manifest["channels"]["android"]
assert android["artifact"] == "IG-Cleaner-Pro-Android-v120.34.apk"
assert android["stableArtifactRequiresPersistentSigning"] is True
assert manifest["releasePolicy"]["stableGithubReleaseIncludesLatestValidatedAndroidApk"] is True

assert "*.jks" in gitignore
assert "*.keystore" in gitignore

print("Android production-signing contract passed.")
