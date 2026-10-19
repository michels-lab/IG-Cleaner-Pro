# GRANADA #8 — Installed Android Developer WebView QA reliability (2026-10-19)

**Issue:** [#150](https://github.com/michels-lab/IG-Cleaner-Pro/issues/150). Parent acceptance [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135). Branch `granada/android-developer-test-stability-20261019` based on `main` `ff9ef4706f216d0ade2106520e1bca810988cd7a`.

## Evidence / reproduced CI failure
- Multiple installed emulator runs for unrelated English-only Desktop [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) failed `DeveloperEditionTest.realDeveloperBuildSupportsAccountNotesAndRestart`: Java expected `"true"`, Android WebView `evaluateJavascript()` returned `"null"`, including line 87 of the old test. This is an actual red CI check; the source failures did not prove the full Developer feature was broken.
- The test combined `showPage('automations')`, selecting `igcAutoBatchApproval`, writing and saving notes in **one** JS evaluation, while navigation and state updates may invalidate a callback. It offered no evidence of which step failed.

## Changes (instrumentation only)
- `untilJsTrue` polls actual document state with bounded retries and a last-value failure description, never claiming success based on mere elapsed time.
- Separates checks: loaded DOM + `AndroidBridge.isDeveloperMode()` + real Account route, Automations page, active section picker, selected control id, owner note saved, *new-document* reload, exact locator persisted, native JSON export in Downloads.
- Ignores an ambiguous callback result for a one-time dispatched action only after independently inspecting the resulting UI state. Does not repeat saves/clicks blindly after a `null` return.
- Keeps original Android native cloud-write barriers, real installed WebView checks, scoped note content and native Downloads report assertions. No production SDK mutation, no fallback mock UI, no feature changes or authentication shortcuts.

## Boundaries and pending
- This is a **test reliability repair**, not confirmation of real provider OTP sign-in or physical Samsung behavior. Parent #135 and live-owner Instagram #133 remain open.
- No overlap with Profile Counts PRs #147/#149 or Desktop translation #143. Tests are run by existing `.github/workflows/android-developer-edition.yml`; no release job runs automatically.
- Await exact-commit CI and installed Android Developer emulator acceptance. Official public stable remains v120.53, next candidate v120.54 remains reserved/unpublished. Owner tests official published stable artifacts only.
