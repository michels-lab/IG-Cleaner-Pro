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

# Static HTML body copy must be English; do not scan JS payloads that preserve
# Instagram's Spanish selectors or historical serialized review identifiers.
import re
static_ui = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", ui, flags=re.I)
static_ui = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", "", static_ui, flags=re.I)
visible_nodes = [m.group(1).strip() for m in re.finditer(r">([^<>]+)<", static_ui)]
accented = [node for node in visible_nodes if re.search(r"[áéíóúñ¿¡ÁÉÍÓÚÑ]", node)]
assert not accented, f"Untranslated static UI text nodes: {accented[:8]}"

collector = (ROOT / "tools/profile_counts_robot.py").read_text(encoding="utf-8")
for token in ("Sign in to Instagram in this window if needed.",
              "The CSV is empty.", "The file contains no valid usernames.",
              "Minimum delay between profile visits"):
    assert token in collector, f"English collector CLI text missing: {token}"
# Locale recognition is intentionally bilingual / multilingual, even if app is English.
for token in ('seguidores?', 'abonnés', 'esta página no está disponible'):
    assert token in collector, f"Existing Instagram locale recognizer removed: {token}"

# Runtime-generated owner dialogs and exported portable reports are part of the UI.
# This regression set intentionally avoids immutable legacy IDs and Instagram DOM
# recognition strings, which must continue accepting Spanish.
for message in (
    "Opened a batch of", "No new profiles remain for Double Check",
    "No results match this filter", "BATCH PREVIEW",
    "Some profiles are UNVERIFIABLE", "BULK CONFIRMATION",
    "This will delete ALL synced cloud data",
    "Relationship and review status", "Unable to load the complete profile list",
    "Syncing lists, reviews and Focus",
):
    assert message in ui, f"Missing English generated UI message: {message}"
for obsolete in (
    "Se abrió una tanda", "Ya no quedan perfiles nuevos",
    "No hay resultados con el filtro actual", "CONFIRMACIÓN MASIVA",
    "¿Seguro que SÍ pudiste revisar", "¿Reiniciar ciclo",
    "Esto borrará TODOS", "Estado de relaciones y revisión",
    "No se pudo cargar toda la lista", "¿Importar ",
    "Sincronizando listas, revisiones y Focus",
):
    assert obsolete not in ui, f"Untranslated owner-visible dynamic copy: {obsolete}"

# High-traffic Pending, Mutuals and non-mutual Followers static controls:
# keep user-visible text English while retaining locale-independent option values
# (medio/alto, legacy Spanish review codes and Instagram DOM recognition).
for new_label in (
    ">Paused</button>", ">Expired pauses</button>", ">Medium/high</option>",
    ">Any date</option>", ">Any age</option>", ">Username</th>",
    ">Reasons</th>", ">Requested on</th>", ">Current cross-check</th>",
    "Go to Mutuals</b>", ">Possibly accepted</button>",
    ">Refresh</button>", ">Import pending_follow_requests.json to begin.</td>",
):
    assert new_label in ui, f"Missing translated Pending/Mutuals label: {new_label}"
static_workspaces = ui.split('id="page-followersMutual"', 1)[-1].split('id="page-automations"', 1)[0]
for outdated in (
    ">Pausados activos</button>", ">Pausas vencidas</button>",
    ">Cualquier edad</option>", ">Cualquier fecha</option>",
    ">Usuario</th>", ">Razones</th>", ">Fecha solicitud</th>",
    ">Cruce actual</th>", ">Actualizar</button>",
    "Pending follow requests — tab especial",
):
    assert outdated not in static_workspaces, f"Untranslated static workspace copy: {outdated}"

print("English UI, cloud-delete guard and legacy review compatibility passed.")
