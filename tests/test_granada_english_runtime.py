"""GRANADA: English runtime messages without breaking legacy app data / IG locale selectors."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DESKTOP = ROOT / "desktop" / "ig_cleaner_pro_v120_27_synced_companion.html"
LAUNCHER = ROOT / "tools" / "ig_cleaner_desktop.py"


class GranadaRuntimeLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ui = DESKTOP.read_text(encoding="utf-8")
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")

    def test_visible_dashboard_and_recent_activity_use_english(self):
        for phrase in (
            "reviewed this session", "protected this session", "resolved this session",
            "relationship changed", "opened this session", "opened in last 7 days",
            "PRIORITY ACTIVITY", "LAST ACTION", "No saved actions in this section.",
            "High pace: consider pausing", "Not enough activity to estimate.",
            "All clear", "No significant inconsistencies were found",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, self.ui)
        for obsolete in (
            "<span>verificados sesión</span>", "<span>protegidos sesión</span>",
            "ACTIVIDAD PRIORITARIA", "ÚLTIMA ACCIÓN", "Sin acciones guardadas en esta sección.",
            "Ritmo alto: mejor haz pausa", "<b>Sin huecos obvios.</b>",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, self.ui)

    def test_batch_confirmation_and_evidence_labels_are_translated(self):
        for phrase in (
            "Opened ${rows.length} profiles.", "<b>Batch quality:</b>",
            "<b>Why opened:</b>", "<h4>Evidence precision audit</h4>",
            "<strong>Critical priority</strong>",
            "<strong>Previously reviewed</strong>",
            "<strong>No critical priority</strong>",
            "Pending requests review", "Mutual followers review", "Non-followback review",
        ):
            self.assertIn(phrase, self.ui)
        for obsolete in ("<b>Calidad de la tanda:</b>", "<b>Por qué abrió:</b>",
                         "<strong>Prioridad crítica real</strong>",
                         "Revisión de pending requests"):
            self.assertNotIn(obsolete, self.ui)

    def test_legacy_storage_identifiers_and_instagram_locale_recognition_remain(self):
        # Existing snapshots have stored these exact historical names; do not translate them.
        for token in (
            "steps.find(s=>s.status==='pendiente'",
            "status:p.length?'pendiente':'vacío'",
            "i.module==='Seguidores que sigo'",
            "esc(s.status==='pendiente'?'Pending'",
        ):
            self.assertIn(token, self.ui)
        self.assertIn("Instagram", self.ui)
        self.assertIn("pendingRequestsRaw", self.ui)
        self.assertIn("reviewedMeta", self.ui)
        self.assertIn("protectedSet", self.ui)

    def test_windows_launcher_errors_are_english(self):
        for phrase in (
            "The bundled interface is incomplete.",
            "The installed executable is missing the Insta Cleaner interface.",
            "Insta Cleaner Pro is already running. Use the existing window.",
            "The Chrome controller was not packaged with this app.",
        ):
            self.assertIn(phrase, self.launcher)
        for obsolete in (
            "La interfaz incluida está incompleta.", "Insta Cleaner Pro ya está abierto.",
            "No se empaquetó el controlador de Chrome.",
        ):
            self.assertNotIn(obsolete, self.launcher)


if __name__ == "__main__":
    unittest.main()
