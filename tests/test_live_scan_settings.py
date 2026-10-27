"""Regression: installed UI can configure SAFE bulk read timings, not Unfollow."""
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from live_scan_settings import PRESETS, SCHEMA, validate_settings, effective_settings
from live_relationship_snapshot import LiveRelationships


class BulkSettingsTests(unittest.TestCase):
    def test_recommended_default_matches_live_reader(self):
        s=effective_settings({})
        self.assertEqual(s["schema"],SCHEMA)
        self.assertEqual(s["preset"],"recommended")
        self.assertEqual(s["values"],PRESETS["recommended"])
        self.assertEqual(s["values"]["page_delay_ms"],2500)
        self.assertEqual(s["values"]["short_every"],5)
        self.assertEqual(s["values"]["long_every"],25)

    def test_cautious_is_more_protective(self):
        a=PRESETS["recommended"]
        b=PRESETS["cautious"]
        self.assertLess(b["page_size"],a["page_size"])
        self.assertGreater(b["page_delay_ms"],a["page_delay_ms"])
        self.assertGreaterEqual(b["short_rest_ms"],a["short_rest_ms"])
        self.assertLessEqual(b["long_every"],a["long_every"])
        self.assertGreater(b["repeat_minutes"],a["repeat_minutes"])

    def test_custom_preserves_only_validated_guardrails(self):
        b=dict(PRESETS["recommended"])
        b.update(page_size=80,page_delay_ms=5000,short_every=4,
                 short_rest_ms=15000,long_every=20,long_rest_ms=180000,
                 repeat_minutes=45)
        accepted=validate_settings({"preset":"custom","values":b})
        self.assertEqual(accepted["values"],b)
        self.assertEqual(effective_settings(accepted),accepted)
        bad=[
            {**b,"page_delay_ms":100},
            {**b,"short_rest_ms":1000},
            {**b,"long_rest_ms":500},
            {**b,"repeat_minutes":1},
            {**b,"long_every":35},
            {**b,"page_size":400},
            {**b,"page_size":True},
            {**b,"unknown":5}
        ]
        for entry in bad:
            with self.subTest(entry=entry),self.assertRaises(ValueError):
                validate_settings({"preset":"custom","values":entry})

    def test_preset_values_cannot_be_forged(self):
        with self.assertRaises(ValueError):
            validate_settings({"preset":"recommended","values":{"page_delay_ms":1}})
        with self.assertRaises(ValueError):
            validate_settings({"preset":"unsafe"})
        self.assertEqual(effective_settings({"schema":SCHEMA,"preset":"unsafe"})["preset"],
                         "recommended")

    def test_persistent_owner_isolation_and_edit_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            data=Path(tmp)/"data"
            robot=LiveRelationships(MagicMock(),MagicMock(),data,Path(tmp)/"chrome")
            alice={"owner":"app-user","account":"ig-alice"}
            bob={"owner":"app-user","account":"ig-bob"}
            self.assertEqual(robot.configuration(alice)["settings"]["preset"],"recommended")
            saved=robot.configuration({**alice,"save":True,
                          "settings":{"preset":"cautious"}})
            self.assertEqual(saved["settings"]["preset"],"cautious")
            self.assertEqual(robot.configuration(bob)["settings"]["preset"],"recommended")
            fresh=LiveRelationships(MagicMock(),MagicMock(),data,Path(tmp)/"chrome")
            self.assertEqual(fresh.configuration(alice)["settings"]["preset"],"cautious")
            # No edit may affect a running scan.
            fresh.worker=MagicMock()
            fresh.worker.is_alive.return_value=True
            with self.assertRaisesRegex(ValueError,"Stop the running scan"):
                fresh.configuration({**alice,"save":True,
                              "settings":{"preset":"recommended"}})
            self.assertFalse(fresh.configuration(alice)["editable"])
            self.assertFalse(fresh._cooldown_file(**alice).exists())
            self.assertFalse(fresh._global_cooldown_file().exists())

    def test_saved_custom_is_effective_in_reader_without_proxies(self):
        read=(ROOT/"tools/profile_lists_live.py").read_text(encoding="utf-8")
        self.assertIn('safe = effective_settings(settings)',read)
        self.assertIn('values["page_delay_ms"]',read)
        self.assertIn('values["short_every"]',read)
        self.assertIn('values["long_every"]',read)
        bridge=(ROOT/"tools/profile_counts_bridge.py").read_text(encoding="utf-8")
        self.assertIn('"/api/actions/live-settings"',bridge)
        self.assertIn("live_relationships.configuration(data)",bridge)
        html=(ROOT/"desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
        self.assertIn("igcLiveSafetyPreset",html)
        self.assertIn("igcLiveConfigSave",html)
        self.assertIn('requestAction("live-settings"',html)
        self.assertIn("Recomendado (predeterminado)",html)
        self.assertIn("igcLiveConfigDirty",html)
        # Settings must be discoverable rather than hidden behind a closed
        # disclosure, and the user must never scan with another account's
        # stale visible timing configuration.
        self.assertIn('id="igcLiveSettingsPanel" open',html)
        self.assertIn('id="igcLiveSafetySummary"',html)
        self.assertIn("Recargar ajustes de esta cuenta",html)
        self.assertIn("igcLiveConfigScope!==igcLiveSettingsKey()",html)
        self.assertIn("No se confirmaron los ajustes guardados para esta cuenta",html)
        self.assertIn("Ajustes guardados y vigentes en esta cuenta",html)


if __name__=="__main__":
    unittest.main()
