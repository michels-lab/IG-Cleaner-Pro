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
    'api.deleteUnscoped(table + "?user_id=not.is.null")',
    "api.logout()",
):
    assert token in main, f"Android synced-data privacy contract missing: {token}"

for token in ("exportCloudData", "deleteCloudData"):
    assert f'@+id/{token}' in account_layout, f"Android account privacy control missing: {token}"

assert 'public void delete(String tableQuery)' in sync_api
assert '"DELETE"' in sync_api
for token in ("scopeQuery(String query, String profile)", '"instagram_" + table',
              'activeInstagramProfile', 'account_key=eq.', 'setInstagramProfile'):
    assert token in sync_api, f"Android multi-Instagram scoped transport missing: {token}"
for token in ("showInstagramProfileManager", "addInstagramProfile",
              "labelLegacyInstagramProfile", "changeInstagramProfile",
              "api.getUnscoped", "api.deleteUnscoped", "instagram_accounts"):
    assert token in main, f"Android multi-Instagram workspace management missing: {token}"
for token in ("@+id/selectInstagramProfile", "@+id/activeInstagramProfile"):
    assert token in account_layout, f"Android active Instagram selection UI missing: {token}"


# Native About must not regress to a text-only dialog.
about = (ROOT / "android/app/src/main/res/layout/dialog_about.xml").read_text(encoding="utf-8")
for token in (
    "@drawable/ig_official_app_icon",
    "@drawable/ig_about_portrait",
    "@drawable/ig_about_studio",
    "TOOLS WITH IDENTITY.",
    "Michel Armando Duarte Flores",
    "Michel’s Lab",
    "@+id/aboutInstagram",
    "@+id/aboutFacebook",
    "@+id/aboutLinkedin",
    "@+id/aboutGithub",
    "@+id/aboutEmail",
    "@+id/aboutPairRow",
    "@+id/aboutProductImage",
    "@+id/aboutDeveloperInfo",
    "@+id/aboutPortraitSocialRow",
    "@+id/aboutVersion",
):
    assert token in about, f"Native About contract missing: {token}"
for token in ("R.layout.dialog_about", "bindAboutLink(", "Intent.ACTION_VIEW", "getPackageManager().getPackageInfo"):
    assert token in main, f"Native About behavior missing: {token}"
for asset in (
    "android/app/src/main/res/drawable-nodpi/ig_about_portrait.jpg",
    "android/app/src/main/res/drawable-nodpi/ig_about_studio.png",
):
    assert (ROOT / asset).is_file(), f"Missing canonical About asset: {asset}"

# Protect the user's actual layout contract, not the obsolete tiny portrait
# + square studio card from v120.36.
for id in ("aboutPairRow", "aboutProductImage", "aboutStudioImage",
           "aboutDeveloperInfo", "aboutPortraitSocialRow", "aboutPortraitImage", "aboutSocialGrid"):
    assert f'@+id/{id}' in about, f"About composition missing: {id}"
assert 'android:layout_width="132dp" android:layout_height="216dp"' in about
assert 'android:orientation="horizontal"' in about
assert not (ROOT / "android/app/src/main/res/menu/top_app_bar.xml").exists(), "Obsolete overflow menu must be removed"
assert 'R.id.actionTools' not in main, "Removed Advanced tools must not open a generic workspace"
assert 'app:menu="@menu/top_app_bar"' not in layout
assert '@+id/headerAboutButton' in layout and '@+id/headerSyncButton' in layout
assert 'android:text="About"' in layout
assert 'aboutAction.setOnClickListener(view -> showAbout())' in main
assert 'syncAction.setOnClickListener(view -> syncNow())' in main
assert '@+id/appBrandTitle' in layout
assert 'activeAboutDialog' in main
instrumentation = ROOT / "android/app/src/androidTest/java/com/michelslab/igcleaner/AboutRenderTest.java"
assert instrumentation.is_file(), "Must have a runnable About screenshot test"
testcode = instrumentation.read_text(encoding="utf-8")
for token in ("getGlobalVisibleRect", "requireVisibleView(dialog.findViewById(R.id.aboutProductImage)",
              "requireVisibleView(dialog.findViewById(R.id.aboutStudioImage)",
              "requireVisibleView(dialog.findViewById(R.id.aboutPortraitImage)",
              "requireVisibleView(dialog.findViewById(res),id,140,66)",
              "R.id.headerAboutButton",
              "aboutInstagram", "aboutFacebook", "aboutLinkedin", "aboutGithub", "aboutEmail",
              "screenshot(\"about\",\"author\")",
              "screenshot(\"about\",\"studio\")",
              "screenshot(\"about\",\"socials\")"):
    assert token in testcode, f"Missing actual About render test assertion: {token}"

# Native Focus dates, history, Double Check and cycle must be runtime-testable.
insights = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/FocusInsights.java").read_text(encoding="utf-8")
focus_test_file = ROOT / "android/app/src/androidTest/java/com/michelslab/igcleaner/FocusInsightsTest.java"
assert focus_test_file.is_file(), "Focus insight instrumented test absent"
focus_test = focus_test_file.read_text(encoding="utf-8")
for token in ("Lo seguiste:", "Te siguió:", "Solicitud enviada:", "Última revisión:",
              "Historial:", "no verificable", "batchHistory", "NO VERIFICABLE"):
    assert token in insights, f"Missing synchronized Focus field: {token}"
for token in ("createDoubleCheckBatch", "fetchDoubleCheckCycle", "persistDoubleCheckCycle",
              "focus_double_check_cycle", "renderDoubleCheckStats",
              "createFocusHistoryCard", "FocusInsights.detail(this, item",
              "Confirmar Double Check", "setSingleChoiceItems(decisions"):
    assert token in main, f"Native Double Check/last-batch missing: {token}"
for token in ("followingAndFollowerDatesHaveCorrectDirectionAndHistory",
              "oldDesktopBatchDatesSurviveNewSnapshotAndUnknownsStayUnknown",
              "pendingAndLastBatchUseOwnDatesAndSourceDevice"):
    assert token in focus_test, f"Missing runtime Focus insight QA: {token}"
assert "8 tests" in (ROOT / "tools/run_android_about_ui.sh").read_text(encoding="utf-8")
print("Android UX/Focus/privacy/About regression contract passed.")

# Real Home screens must now be checked in the packaged Android runtime.
assert 'realHomeRendersNavigationAndWorkspace' in testcode
assert 'screenshot("home","initial")' in testcode and 'R.id.bottomNav' in testcode
