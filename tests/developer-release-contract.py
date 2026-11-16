#!/usr/bin/env python3
"""Owner-requested retirement contract: never ship standalone Developer binaries.

The historical Developer source may remain for archive/migration, but release
tasks cannot resurrect it or silently weaken stable production validation.
"""
import json
from pathlib import Path
from release_artifact_policy import artifact_release_tag

root=Path(__file__).resolve().parents[1]
read=lambda p:(root/p).read_text(encoding="utf-8")
manifest=json.loads(read("release/distribution-manifest.json"))
request=json.loads(read(".michelslab/release-request.json"))
tag=artifact_release_tag(manifest,request)
assert tag.startswith("v120.")
policy=manifest["releasePolicy"]
assert policy["requireDeveloperTwinAssets"] is False
assert policy["requireDeveloperAndroidProductionSigning"] is False
assert policy["requireDeveloperWindowsIndependentInstallTest"] is False
assert "androidDeveloper" not in manifest["channels"]
assert "windowsDeveloper" not in manifest["channels"]
workflow=read(".github/workflows/release.yml")
for prohibited in (
    "android-developer-qa:", "assembleDeveloper",
    "windows_developer_artifact", "android_developer_artifact",
    "build_windows_developer_installer.ps1", "test_windows_developer_installer.ps1",
    "IG-Cleaner-Pro-Windows-Developer-Setup-v*.exe",
    "IGC_ANDROID_SIGNED_DEVELOPER_REQUIRED: \"true\"",
    "app-developer.apk"
):
    assert prohibited not in workflow, "Cancelled Developer publication resurfaced: "+prohibited
assert "needs: [release-request-gate, rendered-ui-qa, windows-robot]" in workflow
assert "gradle -p android :app:assembleRelease" in workflow
assert "tools/verify_production_android_coinstall.sh" in workflow
assert "gh release create" in workflow
print("PASS: stable-only Windows/Android publisher retains release safety checks, no Developer twins")
