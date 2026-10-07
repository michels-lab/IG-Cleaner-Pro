# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-07**
Trigger: **LIMÓN**

## Current stable release

- GitHub release: **v120.34**
- Channel: normal/stable GitHub release
- GitHub prerelease: **false**
- Release URL: `https://github.com/realmichelduarte/IG-Cleaner-Pro/releases/tag/v120.34`
- Final publisher run: **37574744462 — SUCCESS**
- Release target commit: `d8cf449ef8c7f3d71d9bac3acaa951b3beaf98ce`

Published artifacts:
- `IG-Cleaner-Pro-Android-v120.34.apk`
- `IG-Cleaner-Pro-Desktop-v120.34.zip`
- `Instagram-Cleaner-Pro-v120.34-logo.svg`
- `Instagram-Cleaner-Pro-v120.34-PRIVACY.md`
- `SHA256SUMS.txt`

## Android stable signing

Stable package:
- `com.michelslab.igcleaner`
- versionCode: `12034`
- versionName: `120.34`

Debug remains isolated as:
- `com.michelslab.igcleaner.beta`
- `120.34-beta`

Persistent production signing identity:
- alias: `ig-cleaner-pro`
- certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
- valid until: **9999-12-31**
- public metadata: `release/android-signing.json`

The four GitHub Actions signing secrets are configured and were successfully used by the final publisher. Private signing material remains outside Git.

Operational guide: `docs/ANDROID_SIGNING.md`.

## Final v120.34 validation evidence

Publisher run **37574744462 — SUCCESS** verified:
- explicit release authorization;
- release regression contracts;
- production keystore restoration;
- production signing identity;
- signed `:app:assembleRelease`;
- stable package `com.michelslab.igcleaner`;
- versionCode/versionName `12034 / 120.34`;
- exact FINAL-9999 signer fingerprint;
- Desktop + Android release bundle contents;
- normal GitHub release publication;
- Android APK presence in the release.

The earlier verifier failures were CI parser compatibility issues with current `apksigner` output, not APK/signature failures. PR #16 and PR #18 fixed the verifier; the final publisher passed.

## Functional v120.34 state preserved

- Android Focus creation from Android itself: Review / Mutuals / Followers-you-don't-follow / Pending.
- Focus sizes: 20 / 30 / 40.
- Full Desktop ↔ Android normalized review/list/workspace synchronization.
- Android system-navigation inset protection.
- Canonical stacked-layers + sparkle product identity.
- Canonical Michel Duarte portrait and Michel's Lab About branding.
- Local-first privacy surface and documented sync boundary.

## Evidence boundary

Repository CI verifies build/package/signature/state contracts, but it does **not** prove physical-device behavior.

Still requiring real-device evidence:
- cold launch;
- session persistence after closing/reopening;
- Android ZIP/file chooser import;
- Focus 20/30/40 with real usernames;
- Android-created batch recovery/completion;
- Android review → Desktop reviewed-state round trip;
- audit device provenance;
- Android export/chooser behavior;
- system-navigation inset behavior on the target phone.

## Post-release backlog

Repository/app work still available:
1. Centralized in-product privacy/delete/export controls for synchronized metadata.
2. Automated Supabase RLS isolation tests proving one authenticated user cannot read another user's rows.
3. Generalize the release publisher for v120.35+ instead of keeping a version-specific v120.34 publisher.

User/device work still required:
1. Install and validate the signed v120.34 APK on the target phone.

## Next release

- Current stable: **v120.34**
- Next development/release target: **v120.35**
- Do not reuse v120.34 release authorization for v120.35.
