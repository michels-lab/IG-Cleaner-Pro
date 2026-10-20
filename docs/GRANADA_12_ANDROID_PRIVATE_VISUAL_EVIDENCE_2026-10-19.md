# GRANADA #12 — Deterministic installed Android screenshot evidence (2026-10-19)

**Issue:** [#158](https://github.com/michels-lab/IG-Cleaner-Pro/issues/158). **Base:** `main` commit `1730b1f5fe75c8e050ac01b7eef3969281a88d9a`. **Stage:** integrated in `main` via [PR #159](https://github.com/michels-lab/IG-Cleaner-Pro/pull/159), merge `b86ce64ca03c08520405c1bca78043e4188b601d`, after **6/6 exact-HEAD check families SUCCESS** at candidate head `9b3659fe8f331374d92186f29da276c337ed7602` (installed Android Home/About screenshot evidence, installed Developer APK, Android compile, Desktop rendered/contracts, Supabase RLS). Issue #158 closed. Published stable v120.53 remains unchanged; no new release.

## Concrete failed acceptance and risk
- During GRANADA #11 [PR #157](https://github.com/michels-lab/IG-Cleaner-Pro/pull/157) an Android 35 emulator twice reported `OK (12 tests)` for the installed UI, but the job could not retrieve image bytes with `adb pull /sdcard/Android/data/com.michelslab.igcleaner.beta/files/igc-ui-capture/`.
- A same-source job re-run passed, allowing Granada #11 integration, but the intermittent artifact transfer remains a separate CI reliability/fail-closed risk. CI must neither reject good captures for unreliable external-scoped storage nor accept empty/fabricated images as visual evidence.

## Implementation boundaries
- `AboutRenderTest.java`: record **real screenshots taken by Android UiAutomation** into the installed debug APK's *private* `getFilesDir()/igc-ui-capture` instead of external `Android/data`. Visible-layout assertions, real pixel checks and test screenshot names unchanged.
- `tools/collect_android_about_screenshots.py`: use `adb exec-out run-as com.michelslab.igcleaner.beta cat files/igc-ui-capture/<fixed expected filename>`. Fixed eight compact/wide Home/About filenames; refuse stale outputs; check PNG header + dimensions; atomically publish only after all eight succeed. On any missing/fake/wrong-sized image, return nonzero and clean temporary files.
- `tools/run_android_about_ui.sh`: retain **both** installed 12-test instrumentations and existing downstream screenshot validation, but replace external `adb pull` with the private screenshot-transfer collector. No packaging or installation authentication changes.
- `tests/test_android_visual_transfer.py`: offline test matrix of exact paths, eight-file order, atomic success, permission error, wrong dimensions/fake PNG, stale output no-overwrite. CI runs this before installed emulator capture.
- `.github/workflows/android-about-visual.yml`: explicitly watch collector/runner path changes, gate unit tests and still require the existing binary- and SHA-bound real APK PNG visual manifest. No generic CI/release workflow touched.

## Isolation / owner acceptance
- No changes to runtime Android public or Developer feature, owner authentication, OTP, Chrome automation, Windows action robot, Instagram visit pacing or data, Supabase, release manifests or production certificates.
- Does **not** resolve parked Android Developer real account navigation [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) nor Windows Desktop English [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143). Does not claim user physical device QA.
- Exact-head CI installed Android About **must** pass and evidence manifest must exist before merge. Published stable v120.53, reserved v120.54 not authorized or published; user tests only official releases, never Actions candidates.

## QA
The first offline suite found a missing section loop in the collector, the second found a test-only parent-path parsing bug; both corrected and all exact-HEAD CI checks passed after subsequent commits. Normal/debug APK evidence validates all eight actual screenshots and signed-off CI manifest; no release creation or owner physical-device/provider acceptance claimed.
