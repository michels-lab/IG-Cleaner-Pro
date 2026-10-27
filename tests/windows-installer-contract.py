#!/usr/bin/env python3
"""Offline source gate for the governed Windows installer. No Instagram access."""
from pathlib import Path
import json
import re
from release_artifact_policy import artifact_release_tag

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "packaging/windows-installer/InstaCleanerPro.iss"
installer = script.read_text(encoding="utf-8")
license_text = (ROOT / "LICENSE.txt").read_text(encoding="utf-8")
guide = (ROOT / "packaging/windows-installer/TaskbarPinning.txt").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8"))
request = json.loads((ROOT / ".michelslab/release-request.json").read_text(encoding="utf-8"))
artifact_tag = artifact_release_tag(manifest, request)
win = manifest["channels"]["windowsRobot"]
assert script.is_file() and (ROOT / "tools/test_windows_installer.ps1").is_file()
assert (ROOT / "tools/test_windows_installer_wizard.ps1").is_file()
assert len(license_text) >= 600 and "Michel Armando Duarte Flores" in license_text
assert "All Rights Reserved" in license_text
for value in (
    "AppName=Insta Cleaner Pro", "AppPublisher=Michel's Lab",
    "AppId={{E4D8F690-4D44-4C9E-8E6B-BCDD2879F08C}",
    "LicenseFile=..\\..\\LICENSE.txt", "DisableWelcomePage=no",
    "SetupIconFile=..\\..\\desktop\\assets\\ig-cleaner-pro\\official-app-icon.ico",
    "WizardStyle=modern", "PrivilegesRequired=lowest",
    "UsePreviousAppDir=yes", "Uninstallable=yes",
    "Flags: unchecked", 'Tasks: desktopicon',
    'skipifsilent unchecked', "TaskbarPinning.txt", '{autodesktop}',
    'chrome-extension\\*', "InstaCleanerPro.exe",
    "VersionInfoCompany=Michel's Lab",
):
    assert value in installer, f"Installer required contract missing: {value}"
assert "UninstallDelete" not in installer
assert re.search(r"^Source:\s+\"{#PayloadDir}\\InstaCleanerPro.exe\"", installer, re.M)
assert 'anclar' in guide.lower() and 'pin' in guide.lower()
assert 'taskbar' in guide.lower()
assert win["artifactTemplate"] == "IG-Cleaner-Pro-Windows-Setup-v{version}.exe"
assert win["artifact"] == f"IG-Cleaner-Pro-Windows-Setup-{artifact_tag}.exe"
assert win["portableLegacyZipTemplate"] == "IG-Cleaner-Pro-Automatic-Robot-Windows-v{version}.zip"
assert win["installation"] == "inno-setup-per-user"
assert win["authenticode"].startswith("not-configured")
assert win["autoUpdater"].startswith("anonymous GitHub stable release check")
assert win["updateFeed"] == "https://api.github.com/repos/michels-lab/IG-Cleaner-Pro/releases/latest"
assert "SHA-256" in win["autoUpdater"] and "user-confirmed" in win["autoUpdater"]
assert (ROOT / "tools/windows_updater.py").is_file()
assert (ROOT / "tests/test_windows_updater.py").is_file()
assert (ROOT / "tests/windows-updater-ui.test.cjs").is_file()
preview_installer = (ROOT / ".github/workflows/profile-counts-windows-preview.yml").read_text(encoding="utf-8")
official_installer = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
builder = (ROOT / "tools/build_windows_installer.ps1").read_text(encoding="utf-8")
assert '[switch]$AllowCurrentStablePreview' in builder
assert '$manifest.releasePolicy.currentStableRelease -ne "v$Version"' in builder
assert '-AllowCurrentStablePreview' in preview_installer
assert '-AllowCurrentStablePreview' not in official_installer, "Stable publisher must not use preview version override"
for path in [
    ".github/workflows/profile-counts-windows-preview.yml",
    ".github/workflows/release.yml",
]:
    w = (ROOT / path).read_text(encoding="utf-8")
    for token in (
        "choco install innosetup", "tools/build_windows_installer.ps1",
        "tools/test_windows_installer.ps1",
        "IG-Cleaner-Pro-Windows-Setup-v",
        "tests/windows-installer-contract.py",
        "tools/test_windows_installer_wizard.ps1",
        "IG-Cleaner-Pro-Installer-EULA.png",
    ):
        assert token in w, f"{path}: missing {token}"
release = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
assert "gh release view" in release and "gh release create" in release
# Never allow a rerun with stale authorization to overwrite FINAL installers.
# This formerly required gh release upload, which enabled asset clobbering.
publish = release.split("      - name: Publish normal GitHub release", 1)[1].split(
    "      - name: Verify published release", 1)[0]
assert "Refusing to edit or overwrite published assets." in publish
assert 'gh release create "$TAG" dist/*' in publish
assert "gh release upload" not in publish
assert "gh release edit" not in publish
assert ".assets[].name" in release and "IG-Cleaner-Pro-Windows-Setup-v" in release
assert 'release-request-gate:' in release and "request.get(\"authorized\") is True" in release
assert "windows-robot" in release
launcher = (ROOT / "tools/ig_cleaner_desktop.py").read_text(encoding="utf-8")
assert "--smoke-startup" in launcher
assert 'home / BUNDLED_HTML' in launcher
assert 'legacy = Path.home() / ".ig-cleaner-pro"' in launcher
smoke = (ROOT / "tools/test_windows_installer.ps1").read_text(encoding="utf-8")
for token in ("--healthcheck", "--smoke-startup", "unins000.exe",
              "installer-test-user-data-do-not-delete.txt", "Start menu",
              "Legacy", "/VERYSILENT"):
    if token == "Legacy":
        assert "$legacy" in smoke
    else:
        assert token in smoke, f"Windows install test missing: {token}"

# Enforce real bounded subprocesses rather than misleading RunBounded -Wait.
guard = (ROOT / "tools/installer_process_guard.ps1").read_text(encoding="utf-8")
guard_tests = (ROOT / "tests/test_installer_process_guard.ps1").read_text(encoding="utf-8")
assert "WaitForExit(" in guard and "Kill($true)" in guard
assert "TimeoutSeconds" in guard and "ExitCode -ne 0" in guard
assert "Start-Sleep -Seconds 25" in guard_tests and "timed out" in guard_tests
for tester in ("tools/test_windows_installer.ps1", "tools/test_windows_developer_installer.ps1"):
    body = (ROOT / tester).read_text(encoding="utf-8")
    assert "installer_process_guard.ps1" in body
    assert "Invoke-IgcBoundedProcess" in body
    assert "Start-Process -FilePath $path -ArgumentList $arguments -Wait -PassThru" not in body
for workflow in (".github/workflows/release.yml", ".github/workflows/profile-counts-windows-preview.yml"):
    body = (ROOT / workflow).read_text(encoding="utf-8")
    assert "tests/test_installer_process_guard.ps1" in body
    assert 'Invoke-IgcBoundedProcess -Path $candidate' in body
    assert "Retain Windows installer diagnostics even on failed QA" in body
    assert '-TimeoutSeconds 100 }' not in body, "Stray PowerShell brace in frozen EXE step"

print("Windows installer source, branding, license, persistence and release routing: PASS")
