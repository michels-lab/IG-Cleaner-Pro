# GRANADA 25 — Production-signed Android coexistence gate ran under the wrong shell

Date: 2026-10-21. Product: InstaCleaner. Official final-only stable v120.55 attempt #4 [run 39655352708](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39655352708) ended **FAILURE**, and v120.54 remains the latest downloadable official stable.

## Actual verified failure

All three pre-publish required jobs passed on the same exact release SHA `c9534b739aaac65cb9069daf07937088ddee0c4a`: `rendered-ui-qa`, installed Android Developer Account/notes/native JSON export, and integrated Windows public/Developer Setup. On the mandatory `publish` job the Android production signer checks and separate APK builds/signature/package metadata checks passed, but the real signed APK side-by-side emulator step failed immediately after boot at:

```
/usr/bin/sh: 1: set: Illegal option -o pipefail
```

GitHub's `reactivecircus/android-emulator-runner@v2` executes its `script:` input through `/usr/bin/sh`, whereas the inline YAML script was written for Bash using `set -euo pipefail`. The two APK install/launch commands were **never reached**, and therefore there is NO evidence of a failed APK installation. Prior run #39629335827 had a separate emulator boot timeout; do not conflate these.

## Isolated fail-closed correction

- Move the same installed, production-signed public+Developer APK coexistence checks to product-owned `tools/verify_production_android_coinstall.sh` with a Bash shebang and strict `set -euo pipefail`.
- Call `script: bash tools/verify_production_android_coinstall.sh` from the existing **mandatory** emulator step. This works even if the action invokes its script via `sh`; it launches Bash explicitly. Neither step/job can be skipped.
- Strict script verifies both real APKs exist, Android boot completed, both `adb install` commands succeeded, BOTH package IDs are present, BOTH real launch commands report `Status: ok`, and both package installation paths still exist after each launch.
- Expand `tests/release-publisher-contract.py` to enforce the Bash call and all original installed package/signing evidence. The earlier pinned production certificate checks remain unchanged.

## Safety and reentry

No release version bump, production key change, user session/data/journal migration, developer chat or Instagram relationship action. No RC/prerelease; never greenwash CI as proof of real owner Instagram Unfollow/Cancel. Keep issue #172 open.

Require exact PR SHA CI before merging. Then reissue the preauthorized **FINAL stable** v120.55 through the entire standard publisher from a fresh main SHA; both production-signed APKs must actually install/launch and all artifact SHA256/published-asset gates must pass. Only then mark v120.55 stable and update manifests and logs with observed GitHub release evidence.
