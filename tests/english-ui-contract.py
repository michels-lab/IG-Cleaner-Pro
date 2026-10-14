#!/usr/bin/env python3
"""Scoped English UI regression contract: localization must not rewrite user data.

Full dynamic UI and live Instagram owner acceptance are tracked separately.
This test requires the translated high-traffic controls and privacy disclosure,
without mistaking preserved Spanish Instagram export/legacy metadata for UI.
"""
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ui = (ROOT / "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
native = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java").read_text(encoding="utf-8")
strings = ROOT / "android/app/src/main/res/values/strings.xml"
account = ROOT / "android/app/src/main/res/layout/screen_account.xml"

assert '<html lang="en">' in ui
for label in (
    "Review Queue", "Focus 20", "Focus 30", "Focus 40",
    "Mutual followers", "Recheck 30", "View reviewed non-followback accounts",
    "Review date filter", "Import full Instagram export",
    "Audit logical gaps", "Pending requests", "Open these profiles",
    "Switch Instagram profile", "No active batch to recover.",
):
    assert label in ui or label in native, f"English interface label missing: {label}"

for disclosure in (
    "Original Instagram ZIP/JSON/HTML exports are processed locally",
    "IF YOU ENABLE SYNC",
    "The app uses localStorage and IndexedDB",
    "SYNCED DATA MANAGEMENT",
    "The app signs out",
):
    assert disclosure.lower() in ui.lower(), f"Privacy disclosure missing: {disclosure}"

assert "type DELETE CLOUD" in ui
assert "BORRAR NUBE" not in ui
# Preexisting persisted batch values are internal state identifiers, not UI text.
for token in (
    "steps.find(s=>s.status==='pendiente'",
    "status:p.length?'pendiente':'vacío'",
    "i.module==='Seguidores que sigo'",
    "esc(s.status==='pendiente'?'Pending'",
):
    assert token in ui, f"Historical review/audit compatibility lost: {token}"

# Keep bilingual Instagram/profile recognition untouched by app-language choice.
assert 'lower.contains("no me sigue")' in native
assert 'lower.contains("foco")' in native
ET.parse(strings)
ET.parse(account)

print("English UI, cloud-delete guard and legacy review compatibility passed.")
