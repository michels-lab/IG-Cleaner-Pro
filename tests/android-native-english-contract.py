#!/usr/bin/env python3
"""Guard the native Android English UI without changing Instagram locale detection.

This is intentionally a scoped native-shell check, not a claim that every
Desktop/embedded-WebView string has been translated.
"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java"
STRINGS = ROOT / "android/app/src/main/res/values/strings.xml"
ACCOUNT = ROOT / "android/app/src/main/res/layout/screen_account.xml"

java = JAVA.read_text(encoding="utf-8")
strings = STRINGS.read_text(encoding="utf-8")
account = ACCOUNT.read_text(encoding="utf-8")
ET.parse(STRINGS)
ET.parse(ACCOUNT)

# UI translations must not change relation data, DOM recognition or
# account-scoped backup/review behavior.
for token in ('lower.contains("no me sigue")', 'lower.contains("foco")',
              'exportInstagramProfileBackup', 'deleteInstagramProfile'):
    assert token in java, f"Native behavior boundary removed: {token}"

for token in ("Select Instagram profile", "Add Instagram profile",
              "Save synced backup and continue", "Continue without backup",
              "Permanently delete ", "Signed out", "Synced cycle:",
              "No active batches", "Review synced with Desktop",
              "Audit saved without changing the original review"):
    assert token in java, f"Missing native English status/dialog: {token}"

for token in ('name="nav_account">Account<',
              "Full IG Cleaner for Android"):
    assert token in strings, f"Native Android resource not localized: {token}"
for token in ("Edit Instagram @username", "Export selected Instagram backup",
              "Delete selected Instagram profile", "Legacy data"):
    assert token in account, f"Account control not localized: {token}"

# A narrow native-screen guard: accented Spanish should not leak into
# English UI. Instagram's language-specific browser selectors live elsewhere.
for name, data in (("MainActivity.java", java), ("strings.xml", strings),
                   ("screen_account.xml", account)):
    assert not re.search(r"[áéíóúñ¿¡ÁÉÍÓÚÑ]", data), (
        f"Spanish user-facing text remains in native Android {name}"
    )

print("Android native English UI and behavior-boundary contract passed.")
