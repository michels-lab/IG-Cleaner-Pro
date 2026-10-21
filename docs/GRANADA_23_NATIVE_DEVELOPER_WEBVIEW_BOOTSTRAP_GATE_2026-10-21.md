# GRANADA 23 — Native Developer WebView bootstrap release gate

Date: 2026-10-21. Repository: michels-lab/IG-Cleaner-Pro. App only: Android Developer Edition (not FoamLens, Michel's Life or OpenFOAM).

## Exact release failure and evidence
- Owner-authorized **FINAL stable** v120.55 retry #3, [run 39651351295](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39651351295), failed safely: Android Developer emulator instrumented `realDeveloperBuildSupportsAccountNotesAndRestart` returned `MISSING_BUTTON` for the real `igcDevAccount` UI element. Other release jobs: Windows installed Setup and Developer Setup passed; runtime Desktop/Android rendered screenshot gate passed. The Android Developer gate failed and `publish` was skipped, so **v120.54 remains official**.
- Separate prior run 39629335827 had passed Android Developer, but its **different production-signed APK coexistence emulator timed out during boot**. The two failures are distinct. No evidence proves the APK signatures were wrong, and neither failure may be ignored.
- Inspection of `MainActivity.bootstrapWorkspace()` shows an intentional `sessionStorage.igc_android_bootstrapped` first-visit bootstrap and `location.reload()`, followed on the second document by `documentElement.classList.add('igc-android-host')`. The original `untilDeveloperReady()` only checked that the Developer panel was visible; this can be true on the first document shortly before native reload replaces it. This is a **plausible race cause**, not a claimed definitive root cause until installed exact-head acceptance passes.

## Isolated source correction in this branch
- Only `android/app/src/androidTest/java/com/michelslab/igcleaner/DeveloperEditionTest.java` changes. The readiness gate now requires the actual **second document** (bootstrap flag and native host class), complete readyState, real Developer panel, real mounted `igcDevAccount`, real `page-sync`, showPage and Developer Android bridge before clicking the real button.
- Timeout is bounded to 60 × 400 ms, and a failure reports only safe booleans (document readiness, native host, bootstrap flag, panel/button/page mounted and bridge state); never account identity, credentials, cookies, Supabase tokens or localStorage contents.
- The independent click assertion, real active `#page-sync` assertion, persistent section-note-after-restart assertion and real native JSON export assertion are **unchanged**. The test does **not** synthesize the button, call `showPage('sync')` to make the test pass or relax publication gates.
- This branch does not modify desktop HTML (open PR #143 owns translation) nor Android production app logic, robot actions, existing 40-profile cohort, WAL, user data, production signer or release request.

## Validation and continuation
1. Run full Android Developer emulator exact-head PR workflow plus Android About and general source checks. **Do not merge or mark fixed if red.**
2. If test reports native host false, investigate bootstrap lifecycle and WebView navigation. If button true but click fails, inspect actual production handler/route and fix the product, not the assertion. Use redacted DOM-only diagnostics.
3. After green PR merge, the already-authorized **FINAL stable** v120.55 request may be reissued on a *fresh exact main SHA*, requiring every official publisher gate again, including independent production-signed APK side-by-side installation. Never RC/pre-release.
4. Verify published tag is stable and all official asset SHA256 files match. Then separately request physical owner Windows/Developer real Instagram Unfollow/Cancel acceptance (#172/#173); offline emulators cannot establish it.
