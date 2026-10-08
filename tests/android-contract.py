#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

main = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java").read_text(encoding="utf-8")
gradle = (ROOT / "android/app/build.gradle.kts").read_text(encoding="utf-8")
nav = (ROOT / "android/app/src/main/res/menu/bottom_nav.xml").read_text(encoding="utf-8")
layout = (ROOT / "android/app/src/main/res/layout/activity_main.xml").read_text(encoding="utf-8")
account = (ROOT / "android/app/src/main/res/layout/screen_account.xml").read_text(encoding="utf-8")
sync_api = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/SyncApi.java").read_text(encoding="utf-8")
account_layout = (ROOT / "android/app/src/main/res/layout/screen_account.xml").read_text(encoding="utf-8")
sync_api = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/SyncApi.java").read_text(encoding="utf-8")

# The mobile shell must own real system-bar insets so bottom controls are not clipped.
for token in (
    "WindowInsetsCompat.Type.statusBars()",
    "WindowInsetsCompat.Type.navigationBars()",
    "targetHeight = navBaseHeight + navigation.bottom",
    "bottomNav.setPadding(",
):
    assert token in main, f"Android inset protection missing: {token}"

# Native Focus creation must not require Desktop to construct every batch.
for token in (
    "showCreateFocusDialog",
    "showFocusSizeDialog",
    "createFocusBatch",
    'String[] modules = {"main", "mutual", "followers", "pending"}',
    'int[] values = {20, 30, 40}',
    '"focus_batches"',
    '"focus_batch_items"',
    "syncedReviewStateAvailable",
):
    assert token in main, f"Android Focus autonomy contract missing: {token}"

assert 'implementation("androidx.swiperefreshlayout:swiperefreshlayout:1.1.0")' in gradle
for nav_id in ("navHome", "navReview", "navFocus", "navActivity", "navProfile"):
    assert f'@+id/{nav_id}' in nav, f"Bottom navigation entry missing: {nav_id}"

assert 'android:layout_height="80dp"' in layout
assert 'app:menu="@menu/bottom_nav"' in layout

# Native Android must expose the same synchronized-data privacy controls as Desktop.
for token in (
    "SYNC_TABLES",
    "exportSyncedCloudData",
    "confirmDeleteSyncedCloudData",
    "deleteSyncedCloudData",
    "fetchAllCloudRows",
    "saveBytesToDownloads",
    'api.delete(table + "?user_id=not.is.null")',
    "api.logout()",
):
    assert token in main, f"Android synced-data privacy contract missing: {token}"

for token in ("exportCloudData", "deleteCloudData"):
    assert f'@+id/{token}' in account_layout, f"Android account privacy control missing: {token}"

assert 'public void delete(String tableQuery)' in sync_api
assert '"DELETE"' in sync_api

# Native About must not regress to a text-only dialog.
about = (ROOT / "android/app/src/main/res/layout/dialog_about.xml").read_text(encoding="utf-8")
for token in (
    "@drawable/ig_official_mark",
    "@drawable/ig_about_portrait",
    "@drawable/ig_about_studio",
    "TOOLS WITH IDENTITY.",
    "Michel Duarte",
    "Michel’s Lab",
    "@+id/aboutInstagram",
    "@+id/aboutFacebook",
    "@+id/aboutLinkedin",
    "@+id/aboutGithub",
):
    assert token in about, f"Native About contract missing: {token}"
for token in ("R.layout.dialog_about", "bindAboutLink(", "Intent.ACTION_VIEW"):
    assert token in main, f"Native About behavior missing: {token}"
for asset in (
    "android/app/src/main/res/drawable-nodpi/ig_about_portrait.jpg",
    "android/app/src/main/res/drawable-nodpi/ig_about_studio.png",
):
    assert (ROOT / asset).is_file(), f"Missing canonical About asset: {asset}"

print("Android UX/Focus/privacy/About regression contract passed.")
