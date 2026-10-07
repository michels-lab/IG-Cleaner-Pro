#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

html = (ROOT / "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
privacy = (ROOT / "docs/PRIVACY.md").read_text(encoding="utf-8")
migration = (ROOT / "docs/UPDATE_AND_STATE_MIGRATION.md").read_text(encoding="utf-8")
manifest = (ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8")

for token in (
    'id="aboutPrivacyBtn"',
    'id="privacyOverlay"',
    'id="privacyClose"',
    'El export original de Instagram (ZIP/JSON/HTML) se procesa localmente',
    'localStorage y IndexedDB',
    'todavía no declara implementado un único botón para borrar todos los datos sincronizados',
):
    assert token in html, f"Privacy surface token missing: {token}"

for token in (
    "The original Instagram export",
    "list_snapshots",
    "workspace_state",
    "profile_state",
    "Vault",
    "not yet claimed as implemented",
):
    assert token in privacy, f"Privacy documentation token missing: {token}"

assert "IG-Cleaner-Pro-Desktop-v120.34.zip" in migration
assert "IG-Cleaner-Pro-Desktop-v120.34.zip" in manifest

print("Privacy/data-handling contract passed.")
