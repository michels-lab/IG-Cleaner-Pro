#!/usr/bin/env python3
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]

def read(path):
    p = ROOT / path
    assert p.exists(), f"Missing branding file: {path}"
    return p.read_text(encoding="utf-8")

def git_blob_sha(path):
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()

icon = read("branding/ig-cleaner-pro/official-app-icon.svg")
mark = read("branding/ig-cleaner-pro/official-mark.svg")
lockup = read("branding/ig-cleaner-pro/official-lockup.svg")

for token in ('viewBox="0 0 1024 1024"', 'M170 650 500 510 842 650 505 815Z', '#15e4f5', '#e3aa3e'):
    assert token.lower() in (icon + mark).lower(), f"Canonical icon/mark token missing: {token}"

assert 'viewBox="0 0 1600 600"' in lockup
assert 'IG Cleaner' in lockup and '>Pro<' in lockup
assert 'SORT • DECLUTTER • FOCUS' in lockup

launcher = read("android/app/src/main/res/drawable/ic_launcher_foreground.xml")
internal = read("android/app/src/main/res/drawable/ig_official_mark.xml")
bg = read("android/app/src/main/res/values/ic_launcher_background.xml")
theme = read("android/app/src/main/res/values/themes.xml")
toolbar = read("android/app/src/main/res/layout/activity_main.xml")
workspace = read("android/app/src/main/res/layout/screen_workspace.xml")
main = read("android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java")
strings = read("android/app/src/main/res/values/strings.xml")
adaptive = read("android/app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml")

for source in (launcher, internal):
    assert 'M170,650 L500,510 L842,650 L505,815 Z' in source
    assert '#15E4F5' in source and '#E3AA3E' in source

assert '#071A30' in bg
assert '@drawable/ic_launcher_foreground' in adaptive
assert '@drawable/ig_brand_splash' in theme
assert 'app:logo="@drawable/ig_official_mark"' in toolbar
assert 'app:title="IG Cleaner Pro"' in toolbar
assert 'android:id="@+id/workspaceLoadingBrand"' in workspace
assert 'android:src="@drawable/ig_official_mark"' in workspace
assert '.setIcon(R.drawable.ig_official_mark)' in main
assert '<string name="app_name">IG Cleaner Pro</string>' in strings

html = read("desktop/ig_cleaner_pro_v120_27_synced_companion.html")
for token in (
    'id="igcOfficialFavicon"',
    'id="igcBrandSplash"',
    'id="igc-official-brand-css"',
    'class="aboutOfficialLockup"',
    '<b>IG Cleaner Pro</b>',
    'data:image/svg+xml,'
):
    assert token in html, f"Desktop official-brand token missing: {token}"

assert '<div class="igc-brand-mark">IG</div>' not in html
assert '<div class="aboutMarkBox"><div class="igcMonogram">' not in html

# About must use immutable canonical assets rather than embedding/recompressing them.
assert git_blob_sha("desktop/assets/michel_duarte_avatar.jpg") == "18fe1a68722850c3d8f918dc0799f46ffeb6dbaf"
assert git_blob_sha("desktop/assets/michels-lab/official-lockup.png") == "7fd48093968b31ddacd3098f5b15d962de580652"
assert 'data:image/jpeg;base64' not in html
assert 'src="assets/michel_duarte_avatar.jpg"' in html
assert 'src="assets/michels-lab/official-lockup.png"' in html

# All user-visible release identity must agree with the governed v120.34 target.
assert '<title>IG Cleaner Pro v120.34 — Synced Companion</title>' in html
assert 'Engine v119 · UI v120.34' in html
assert 'IG Cleaner Pro · UI v120.34' in html
assert 'UI v120.26' not in html
assert 'UI v120.27' not in html

print("Official IG Cleaner Pro branding contract passed.")
