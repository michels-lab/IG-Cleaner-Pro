# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-06**
Trigger: **LIMÓN**

## Current release

- GitHub release: **v120.34**
- Channel: normal/stable GitHub release
- GitHub prerelease: **false**
- Desktop bundle is already published.
- Android v120.34 implementation is in `main`; production-signing hardening is being completed on `android-signing/v120.34`.

## Android signing work

Stable package:
- `com.michelslab.igcleaner`
- versionCode: `12034`
- versionName: `120.34`

Debug remains:
- `com.michelslab.igcleaner.beta`
- `120.34-beta`

Persistent signing identity:
- alias: `ig-cleaner-pro`
- certificate SHA-256: `6FB7720E669ADFD36159A2E9781E15824526DC263900999A500BAB38A7B67D43`
- valid until: **2126-10-08**
- public metadata: `release/android-signing.json`

Private keystore/passwords must never be committed. Required GitHub Actions secret names:
- `IGC_ANDROID_KEYSTORE_B64`
- `IGC_ANDROID_KEYSTORE_PASSWORD`
- `IGC_ANDROID_KEY_ALIAS`
- `IGC_ANDROID_KEY_PASSWORD`

Operational guide: `docs/ANDROID_SIGNING.md`.

## Release behavior

Once the four signing secrets are loaded:
1. the governed v120.34 publisher restores the keystore only inside the Actions runner;
2. it builds `:app:assembleRelease`;
3. it verifies package = `com.michelslab.igcleaner`;
4. it verifies versionCode/versionName = `12034 / 120.34`;
5. it verifies the signer certificate fingerprint;
6. it attaches `IG-Cleaner-Pro-Android-v120.34.apk` to the existing v120.34 GitHub release;
7. it regenerates `SHA256SUMS.txt` including the APK.

Normal future IG Cleaner Pro GitHub releases must include the latest validated signed Android APK unless Michel explicitly requests desktop-only distribution.

## Functional v120.34 state preserved

- Android Focus creation from Android itself: Review / Mutuals / Followers-you-don't-follow / Pending.
- Focus sizes: 20 / 30 / 40.
- Full Desktop ↔ Android normalized review/list/workspace synchronization.
- Android system-navigation inset protection.
- Canonical stacked-layers + sparkle product identity.
- Canonical Michel Duarte portrait and Michel's Lab About branding.
- Local-first privacy surface and documented sync boundary.

## Evidence boundary

Repository CI can verify:
- compile/package path;
- signing plumbing;
- package identity/version;
- certificate signer identity;
- embedded Workspace integrity.

Repository CI does **not** prove physical phone behavior. Cold launch, persistence, real-account Focus, state round-trip and file/export behavior remain real-device validation items.

## Verified signing evidence

GitHub Actions run `37568540656` — **SUCCESS**:
- Desktop/state/branding/privacy/signing contracts — PASS.
- Android debug build and embedded Workspace — PASS.
- Production-signing plumbing smoke test using an ephemeral CI key — PASS.
- Signed release APK identity verified as `com.michelslab.igcleaner`, versionCode `12034`, versionName `120.34`.

## Next steps

1. Merge PR #14 into `main`.
2. Add the four production signing values to GitHub Actions Secrets.
3. Trigger the governed v120.34 publisher to attach the signed APK.
4. Install the signed APK on the target phone and record device evidence.
