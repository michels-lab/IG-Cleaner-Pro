#!/usr/bin/env python3
"""Offline source gate for the governed Windows installer. No Instagram access."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / "packaging/windows-installer/InstaCleanerPro.iss"
installer = script.read_text(encoding="utf-8")
license_text = (ROOT / "LICENSE.txt").read_text(encoding="utf-8")
guide = (ROOT / "packaging/windows-installer/TaskbarPinning.txt").read_text(encoding="utf-8")
manifest = json.loads((ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8"))
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
assert win["artifact"] == f"IG-Cleaner-Pro-Windows-Setup-{manifest['releasePolicy']['nextRelease']}.exe"
assert win["portableLegacyZipTemplate"] == "IG-Cleaner-Pro-Automatic-Robot-Windows-v{version}.zip"
assert win["installation"] == "inno-setup-per-user"
assert win["authenticode"].startswith("not-configured")
assert win["autoUpdater"].startswith("not-implemented")
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
assert "gh release upload" in release
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
print("Windows installer source, branding, license, persistence and release routing: PASS")
