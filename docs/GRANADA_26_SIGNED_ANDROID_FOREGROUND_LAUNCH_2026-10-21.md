# Operación Granada #26 — signed Android app launch runtime evidence

Date: 2026-10-21. Product: **IG Cleaner Pro only**. No foreign OpenFOAM, FoamLens, Michel's Life or LouderMe source.

## Verified sixth final stable publisher failure

The sixth officially authorized FINAL-only v120.55 publication [run #39669433591](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39669433591) **failed closed**. The three pre-publish gates were all SUCCESS: actual Windows public+Developer Setup and offline Chromium/robot tests; Android Developer installed Account/notes/JSON; screenshot-backed Desktop+Android Home/About.

The `publish` job verified BOTH production-signed Android APK builds, package IDs, versions and identical persistent production certificate. Its API-35 software-emulated Google APIs device finally booted (boot completed after ~475 s). Both APKs **installed successfully**; `pm list packages` displayed both `com.michelslab.igcleaner` and `com.michelslab.igcleaner.developer`.

The first `adb shell am start -W -n com.michelslab.igcleaner/.MainActivity` then returned `Status: timeout`, `LaunchState: UNKNOWN (-1)`, `WaitTime: 30623`. The original mandatory Bash gate correctly refused publication, *before* developer APK launch or postlaunch coexistence proof. This is NOT evidence of an app launch failure or launch success; the emulator's foreground state had not been independently observed. Official stable remains v120.54; NO v120.55 release or owner Instagram live acceptance is claimed.

## Root cause and corrective scope

The publisher used the synchronous ActivityManager `am start -W` result as the sole affirmative launch evidence. Under extreme emulator contention a start may not report a positive result within its 30-second wait, even after both signed APKs are installed. A naive removal of `-W` without runtime verification would be unsafe: `am start -n` can acknowledge an intent without proving a resumed application.

Fix in `tools/verify_production_android_coinstall.sh`:
- Keep the exact original production APK paths, nonempty APK checks, boot-completed condition, both `adb install -r` results and separately exact package-list checks.
- Invoke the *real* app component through nonblocking `adb shell am start -n`; reject missing acknowledgement or ActivityManager error.
- For each product package **individually**, poll the emulator's actual `dumpsys activity activities` resumed/top-resumed MainActivity and matching `pidof` live process; require **two consecutive positive observations**. A no-response, wrong package, stale activity or stopped process fails after a bounded 50 tries. This cannot be satisfied by install/package metadata alone.
- After both foreground launches, check both `pm path` installed identities again. Failed observations prevent the publisher from creating/uploading a release. This changes launch *observation* only, never Android source, signing, secrets or account data.

Offline adversarial fixture `tests/test_android_signed_coinstall_runtime.py` uses fake adb strictly to prove gate behavior: delayed valid foreground success, never resumed, wrong account foreground, missing process, missing boot/package, rejected start/install and missing APK must all have correct outcomes. It does **not** substitute for the real emulator in the governed publisher. `tests/release-publisher-contract.py`, broad CI and the mandatory publisher additionally execute these regressions. The existing mandatory `reactivecircus/android-emulator-runner@v2`, real signed APKs, real-device launch, Android Developer UI, Windows installers, visual QA and SHA256 gates are **not removed**.

## Emulator hardware-acceleration contributing factor

The sixth publisher log explicitly reported that Linux hardware acceleration was unavailable to `reactivecircus/android-emulator-runner@v2`; its software emulator needed roughly eight minutes to finish booting, more than two minutes for both APK installs and still exceeded ActivityManager's 30-second synchronous launch wait. The separate Android Developer and About QA workflows already enable usable `/dev/kvm` when available, whereas the `publish` job had omitted that step.

The actual publisher now attempts to enable `/dev/kvm` **before** the signed coexistence emulator starts and verifies read/write access; on a host without KVM it logs a warning but still requires the exact same real signed device gate (never fake success). This addresses an observed environment/configuration difference and may improve performance, but success and physical acceptance must be measured rather than assumed. The release contract requires this acceleration step to precede the mandatory device execution.

## Acceptance and continuation

1. All exact-branch PR CI must pass (offline failure modes plus existing Android emulator / Windows / Desktop gates). Do not merge red CI.
2. Merge the isolated branch without overriding concurrently completed PR #202 or unrelated app work.
3. Reissue a **new exact-main-SHA** fully governed FINAL-stable v120.55 release request under the user's standing Operación Granada authority; never an RC/beta or `prerelease=true`.
4. Require true installed public and Developer Android foreground proof, postlaunch coexistence, original production signer and every release gate to pass before verifying a public stable GitHub tag, asset list and SHA256SUMS; only then change currentStableRelease and user-facing release guidance.
5. Maintain user issue [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) open until Michel tests real signed-in Unfollow/Cancel Pending after a published Windows Setup. Protect the original saved forty-person batch, journal, no-click vs uncertain-click evidence, per-account protections and Chrome state.
