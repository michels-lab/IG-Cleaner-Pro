#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

html = (ROOT / "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
privacy = (ROOT / "docs/PRIVACY.md").read_text(encoding="utf-8")
migration = (ROOT / "docs/UPDATE_AND_STATE_MIGRATION.md").read_text(encoding="utf-8")
import json
manifest_text = (ROOT / "release/distribution-manifest.json").read_text(encoding="utf-8")
manifest = json.loads(manifest_text)

for token in (
    'id="aboutPrivacyBtn"',
    'id="privacyOverlay"',
    'id="privacyClose"',
    'id="privacyExportCloud"',
    'id="privacyDeleteCloud"',
    'window.igcPrivacyExportCloudData',
    'window.igcPrivacyDeleteCloudData',
    "IGC_SYNC_TABLES",
    "BORRAR NUBE",
    "user_id=not.is.null",
    "S.session=null",
    "ig-cleaner-cloud-export-v1",
    'El export original de Instagram (ZIP/JSON/HTML) se procesa localmente',
    'localStorage y IndexedDB',
):
    assert token in html, f"Privacy surface token missing: {token}"

for token in (
    "The original Instagram export",
    "list_snapshots",
    "workspace_state",
    "profile_state",
    "Export synchronized cloud data",
    "Delete synchronized cloud data",
    "signs the app out",
    "Vault",
):
    assert token in privacy, f"Privacy documentation token missing: {token}"

stable_desktop = manifest["channels"]["desktop"]["artifact"]
assert stable_desktop in migration
assert stable_desktop.startswith("IG-Cleaner-Pro-Desktop-v") and stable_desktop.endswith(".zip")
assert manifest["channels"]["desktop"]["artifactTemplate"] == "IG-Cleaner-Pro-Desktop-v{version}.zip"

print("Privacy/data-handling contract passed.")
