# GRANADA — Android screenshot duplicate evidence gate (2026-10-26 local)

## Incident, exact real source, and release status

Functional [PR #256](https://github.com/michels-lab/IG-Cleaner-Pro/pull/256) fixed the owner's actual Spanish Instagram unavailable-page issue. Release packaging [PR #257](https://github.com/michels-lab/IG-Cleaner-Pro/pull/257) passed **seven exact-head premerge checks** and merged as `bed8b620466cae87608775fa09be2a0c75e05782`. Its governed FINAL-only publisher [run 40443259064](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40443259064) approved source/request, installed Windows and signed Android public+Developer gates, but Android Home/About visual evidence was **BLOCKED** by its separate [Android About run 40443259036](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40443259036). The latter failed with the strict screenshot gate: `screenshot[1]: duplicate screenshot bytes; likely reused surface/viewport`.

**v120.67 is NOT published unless the official release API reports normal non-draft, non-prerelease tag, all 12 digest-bearing assets and successful exact-head governed publisher**. Continue to advertise existing official v120.66 and preserve its immutable assets.

## Confirmed root cause and ownership

`android/app/src/androidTest/.../AboutRenderTest.java` checks the author's portrait, both product/studio logos and all five social buttons in one native About dialog, then takes THREE consecutive `UiAutomation.takeScreenshot()` snapshots without scrolling or changing UI: `about-*-author.png`, `about-*-studio.png`, `about-*-socials.png`. They are necessarily liable to be byte-identical because each is the SAME actual full screen. The older `tools/android_about_visual_evidence.py` explicitly allowed duplicates within the same viewport, but the authoritative `tools/visual_release_gate.py` correctly refuses ANY duplicate screenshot bytes, including equal captures of the same viewport. That inconsistent screenshot-source contract caused a real publication failure; **not an Instagram robot failure and not evidence of a broken About layout**.

Earlier branch CI provided independent compact/wide screenshots at other commits; a successful older head cannot certify the exact published main head. The mandatory visual gate must stay strict. Avoid resubmitting false repeated frames under different filenames, synthesizing fake images or removing visual UI assertions.

## Repair and negative regression

- The native instrumentation still asserts exact real rectangles and visibility for app/studio marks side by side, developer name, portrait, all five social links, and fixed About toolbar before taking **one full About screenshot per viewport**. Home gets one actual screenshot. Thus four independent screenshots: compact Home + full About, wide Home + full About.
- `tools/collect_android_about_screenshots.py` transfers exactly these four private-app PNG files via `adb exec-out run-as`, validates expected physical viewport dimensions and refuses missing/partial/stale artifacts.
- `tools/android_about_visual_evidence.py` validates physical dimensions, nonblank app pixels, release APK fingerprint and **unique SHA-256 across all four** (not just cross-viewport); `visual_release_gate.py` is unchanged and still fails duplicates, placeholders, stale SHA, missing surfaces and only one size.
- `tools/run_android_about_ui.sh` now demands exactly four native Home/About PNGs after TWO emulator sizes and all 12 instrumentation tests each size, preserving real emulator + native UI proof.
- `tests/test_android_visual_transfer.py` regression fails on the original three `screenshot("about", ...)` repeated captures, refuses missing/partial output, incorrect physical viewport, placeholder PNG and refuses to touch existing owner files.

## Required exact-source gates

The root-cause repair is NOT done until this fix PR passes the actual Android visual workflow and its exact-commit Android manifest/digest gate, original no-click Android Developer/runtime, installed Windows public/Developer, Desktop UI and general RLS/tests. Only then merge and allow the ONE governed official FINAL v120.67 publisher to rerun independently on the new exact head. The failed original publisher may not be labeled success or bypassed.

User physical validation of InstaCleaner unavailable profile on signed-in Windows and real Cancel Pending remains pending separately. No user Instagram relationship mutation, account state, login, keys or original cohort data were touched.
