#!/usr/bin/env python3
"""Non-regression contract for Michel's Lab premium visual system.

Source assertions supplement but NEVER replace real Android/desktop screenshots.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / "android/app/src/main/res"
DESKTOP = ROOT / "desktop/ig_cleaner_pro_v120_27_synced_companion.html"

def read(relative):
    return (ANDROID / relative).read_text(encoding="utf-8")

palette = read("values/colors.xml")
for name in ("ig_bg","ig_surface","ig_surface_2","ig_text","ig_blue","ig_cyan","ig_gold","ig_border"):
    assert f'name="{name}"' in palette, f"Missing semantic palette {name}"

for name in ("bg_app","bg_header","bg_nav_indicator","bg_premium_panel","bg_premium_hero","bg_about_canvas"):
    text = read(f"drawable/{name}.xml")
    assert "<gradient " in text, f"Missing actual Android gradient on {name}"

about = read("layout/dialog_about.xml")
assert 'android:background="@drawable/bg_about_canvas"' in about
assert 'android:background="@drawable/bg_premium_hero"' in about
assert 'android:background="@drawable/bg_premium_panel"' in about
for resource in ("ig_about_portrait","ig_about_studio","ig_official_app_icon"):
    assert f'@drawable/{resource}' in about, f"Missing canonical real About asset: {resource}"
assert "TOOLS WITH IDENTITY." in about
for social in ("Instagram","Facebook","Linkedin","Github","Email"):
    assert f'@+id/about{social}' in about, f"Social control missing: {social}"

main = read("layout/activity_main.xml")
assert 'android:background="@drawable/bg_header"' in main
assert 'android:background="@drawable/bg_app"' in main
home = read("layout/screen_mobile_workspace.xml")
assert 'android:background="@drawable/bg_premium_hero"' in home

desktop = DESKTOP.read_text(encoding="utf-8")
assert '<style id="igc-v12036-premium-visual">' in desktop
assert "TOOLS WITH IDENTITY." in desktop
for selector in (".aboutShell", ".aboutDeveloperCard", ".aboutBrandMini", ".aboutSocial",
                 ".igc-commandbar", ".igc-rail", ".panel"):
    assert selector in desktop, f"Missing cohesive desktop design selector: {selector}"

instrumentation = ROOT / "android/app/src/androidTest/java/com/michelslab/igcleaner/AboutRenderTest.java"
test = instrumentation.read_text(encoding="utf-8")
assert 'requireResource(link, 140, 66)' in test and '"aboutEmail"' in test
print("PASS: premium visual source contract; real rendered Android/Desktop UI gate is separate.")
