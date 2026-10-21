# GRANADA — Android Developer Account navigation release gate (2026-10-21)

**Owner directive:** GRANADA may include a **final stable official release** if every mandatory release gate passes. No RC or prerelease.

## Reproducible release blocker
The isolated Android Developer runtime workflow for Windows Automation Center PR #184 passed Developer APK signing/configuration, but its real installed emulator test failed **twice** at `DeveloperEditionTest.realDeveloperBuildSupportsAccountNotesAndRestart`. In both attempts the Developer button `Sign in / Account` had been clicked but `#page-sync.active` never became true within the wait window. The independent Developer cloud mutation block test passed. See workflow run `39603960666` first and re-run failed jobs attempts. This is a mandatory gate: **do not publish v120.55** on this evidence.

## Isolated read-only diagnostic
The test now checks the actual real WebView button click, captures **only DOM route names and boolean availability** immediately after the click, and, on a failed navigation, reads a second immutable route snapshot. Error output distinguishes missing button, thrown event, absent sync view, wrong active page and stale navigation. The diagnostics **never read or export account emails, passwords, tokens, cookies, localStorage or personal Instagram data**.

This branch changes **only** Android instrumentation test source plus this handoff. It does not modify the Desktop UI or action robots, sign in silently, bypass Meta checks or call an alternative navigation function that would mask the failed button. The blocked original behavior must either be fixed by its own source change with Android installed proof, or the gate remains red. Do not misreport added instrumentation as bug fixed.

## Ownership and next steps
- Source: `android/app/src/androidTest/java/com/michelslab/igcleaner/DeveloperEditionTest.java`.
- Exact-head Android Developer emulator CI must run and its failure or success be captured. Inspect route diagnostic from the job logs; identify the real root cause before changing product source.
- The Windows UI PR #184 remains separate; do not overwrite its Desktop HTML, project log or handoff.
- Official stable is still v120.54; full final release requires the existing signed public and Developer Android APKs, installed Windows/Developer Setup, Desktop/Android rendered evidence, unchanged state/journals, verified version/checksum and real owner testing as separately documented.

## GRANADA continuity
If this remains blocked by emulator/runtime evidence or another owner, leave this PR/branch here and continue a different non-overlapping P0 workstream. Never force a green result by relaxing the safety/instrumentation assertion.
