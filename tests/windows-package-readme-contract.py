#!/usr/bin/env python3
"""Keep the Windows owner-facing bundle instructions aligned with distribution."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
readme=(root/"packaging/profile-counts/README.txt").read_text(encoding="utf-8")
workflow=(root/".github/workflows/release.yml").read_text(encoding="utf-8")
preview=(root/".github/workflows/profile-counts-windows-preview.yml").read_text(encoding="utf-8")

for token in (
    "INSTA CLEANER PRO — WINDOWS APPLICATION",
    "InstaCleanerPro.exe",
    "No separate HTML, .cmd launcher",
    "Official download channel",
    "Automations",
    "Profile Counts",
    "Followback Audit is optional",
    "Mutuals is human-review-only",
    "simulated Instagram pages",
    "Vault",
    "Original Instagram export ZIP/JSON/HTML input stays on your device",
    "not a live user-session",
):
    assert token.lower() in readme.lower(), f"Missing owner guidance: {token}"

for obsolete in (
    "Aplicación Windows integrada (Preview)",
    "no es un release estable",
    "Start-Insta-Cleaner-Robot.cmd",
    "v120.42 no contiene",
):
    assert obsolete not in readme, f"Obsolete preview/launcher guidance: {obsolete}"

assert "Copy-Item packaging/profile-counts/README.txt" in workflow
assert "packaging/profile-counts/README.txt" in preview
print("Windows integrated app owner guidance contract passed.")
