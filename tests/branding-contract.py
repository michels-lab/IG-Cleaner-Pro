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

# Enforce byte identity of the user-selected FIRST logo option, not the retired SVG.
original = ROOT / "branding/ig-cleaner-pro/approved-option-1-original.png"
assert original.is_file()
assert len(original.read_bytes()) == 1559781
assert hashlib.sha256(original.read_bytes()).hexdigest() == "f913686282731c0a076ec6167989ca05c60c25cea18d51e964343f444284d7a8"
assert original.read_bytes()[:8] == bytes([137,80,78,71,13,10,26,10])
for role in ("official-app-icon.png", "official-mark.png", "official-lockup.png"):
    file = ROOT / "branding/ig-cleaner-pro" / role
    assert file.read_bytes() == original.read_bytes(), f"{role} is not the canonical unmodified original"

assert git_blob_sha("android/app/src/main/res/drawable-nodpi/ig_official_app_icon.png") == "6fdb47fc26ed125ec45439612ea83221965fc5d1"
assert git_blob_sha("desktop/assets/ig-cleaner-pro/official-app-icon.png") == "6fdb47fc26ed125ec45439612ea83221965fc5d1"
assert git_blob_sha("branding/ig-cleaner-pro/official-app-icon-1024.png") == "2ccc11a209cb2168a92649a03f7f159d6eb5bba9"
for density, blob in {
    "mdpi":"780a7342d1757810d1956742a39fa8cb5f325862",
    "hdpi":"ad7a128e2596937e98a76335924c023ebe31258c",
    "xhdpi":"1f4bee4e7fa5abad26eb15d675e52791452137fc",
    "xxhdpi":"1240c1dabb59411f5b7528e2fa0bd5052e6e3057",
    "xxxhdpi":"62c5ff4057b7a0108007e57735d10a598e4cf17d",
}.items():
    assert git_blob_sha(f"android/app/src/main/res/mipmap-{density}/ic_launcher.png") == blob

theme = read("android/app/src/main/res/values/themes.xml")
toolbar = read("android/app/src/main/res/layout/activity_main.xml")
workspace = read("android/app/src/main/res/layout/screen_workspace.xml")
about_android = read("android/app/src/main/res/layout/dialog_about.xml")
splash = read("android/app/src/main/res/drawable/ig_brand_splash.xml")
main = read("android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java")
strings = read("android/app/src/main/res/values/strings.xml")
for p in ("ic_launcher.xml","ic_launcher_round.xml"):
    adaptive=read("android/app/src/main/res/mipmap-anydpi-v26/"+p)
    assert '@drawable/ig_official_app_icon' in adaptive
for layout in (toolbar, workspace, about_android, splash):
    assert '@drawable/ig_official_app_icon' in layout, "Visible Android branding must use user-approved icon"
assert '@drawable/ig_brand_splash' in theme
assert 'android:text="Instagram Cleaner Pro"' in toolbar
assert 'android:id="@+id/workspaceLoadingBrand"' in workspace
assert 'R.id.headerAboutButton' in main and 'R.id.headerSyncButton' in main
assert 'android:text="About"' in toolbar
assert '<string name="app_name">IG Cleaner Pro</string>' in strings

html = read("desktop/ig_cleaner_pro_v120_27_synced_companion.html")
for token in (
    '<link rel="icon" type="image/png" href="assets/ig-cleaner-pro/official-app-icon.png"/>',
    'class="aboutOfficialLockup"',
    '<b>Instagram Cleaner Pro</b>',
    'aria-label="Instagram Cleaner Pro logo"',
    'src="assets/ig-cleaner-pro/official-app-icon.png"',
):
    assert token in html, f"Desktop selected logo token missing: {token}"
assert html.count('src="assets/ig-cleaner-pro/official-app-icon.png"') >= 2
assert 'data:image/svg+xml,' not in html, "Retired product logo embedded in Desktop HTML"
assert '<div class="igc-brand-mark">IG</div>' not in html
assert '<div class="aboutMarkBox"><div class="igcMonogram">' not in html

# About must use immutable canonical assets rather than embedding/recompressing them.
assert git_blob_sha("desktop/assets/michel_duarte_avatar.jpg") == "18fe1a68722850c3d8f918dc0799f46ffeb6dbaf"
assert git_blob_sha("desktop/assets/michels-lab/official-lockup.png") == "7fd48093968b31ddacd3098f5b15d962de580652"
assert 'data:image/jpeg;base64' not in html
assert 'src="assets/michel_duarte_avatar.jpg"' in html
assert 'src="assets/michels-lab/official-lockup.png"' in html
assert 'igc-v12030-supabase-sync-js' in html
assert 'normalizeLegacyReviewState' in html
assert 'pushWorkspaceState' in html
assert 'list_snapshots' in html

# All user-visible development identity must agree with the governed next release.
assert '<title>Instagram Cleaner Pro v120.36</title>' in html
assert 'Engine v119 · UI v120.36' in html
assert 'Instagram Cleaner Pro · UI v120.36' in html
assert 'UI v120.26' not in html
assert 'UI v120.27' not in html

# The master studio slogan and social identities are mandatory in the rendered About markup.
assert 'class="aboutBrandTag">TOOLS WITH IDENTITY.' in html
assert 'Ideas · Apps · Un mejor mañana' not in html
for social in ('ig','fb','in','gh','mail'):
    assert f'class="aboutIcon {social}"><svg' in html, f"Missing recognizable social SVG for {social}"
for link in (
    'https://www.instagram.com/realmichelduarte/',
    'https://www.facebook.com/realmichelduarte',
    'https://www.linkedin.com/in/realmichelduart/',
    'https://github.com/realmichelduarte',
):
    assert f'href="{link}"' in html, f"Noncanonical About social link: {link}"
assert html.index('class="aboutOfficialLockup"') < html.index('class="aboutDeveloperCard"')
assert html.index('class="aboutDeveloperCard"') < html.index('class="aboutSocials"')

print("Official IG Cleaner Pro branding contract passed.")
