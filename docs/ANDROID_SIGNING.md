# Android Production Signing — IG Cleaner Pro

Updated: **2026-10-06**

## Stable signing identity

IG Cleaner Pro uses one persistent Android production signing identity for the stable package:

- Package: `com.michelslab.igcleaner`
- Key alias: `ig-cleaner-pro`
- Certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
- Certificate validity: through **9999-12-31** (practical non-expiring maximum for this signing identity)
- Metadata authority: `release/android-signing.json`

The private keystore and its passwords are **not stored in Git**.

## Required GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions must contain:

- `IGC_ANDROID_KEYSTORE_B64`
- `IGC_ANDROID_KEYSTORE_PASSWORD`
- `IGC_ANDROID_KEY_ALIAS`
- `IGC_ANDROID_KEY_PASSWORD`

The release workflow restores the keystore only inside the ephemeral GitHub Actions runner.

## Operational status

- The four repository secrets are configured.
- Final stable publisher run **37574744462** successfully restored the production keystore, verified the FINAL-9999 fingerprint, built the signed APK, verified package/version, and attached `IG-Cleaner-Pro-Android-v120.34.apk` to the normal v120.34 GitHub release.
- The v120.34 signing path is therefore no longer pending; it is the established production-signing baseline for future Android updates.

## Build behavior

Debug:
- application ID: `com.michelslab.igcleaner.beta`
- version suffix: `-beta`
- remains available for CI/development.

Release:
- application ID: `com.michelslab.igcleaner`
- version: `120.34`
- `assembleRelease` / `bundleRelease` fail immediately if production signing variables are missing.
- release publication verifies package ID, versionCode/versionName and signer certificate fingerprint before attaching the APK.

## Backup rule

The production keystore is an update identity, not a disposable build file. Keep at least two private backups outside Git/GitHub. Losing the keystore or passwords can break direct APK update continuity.

Never commit:
- the keystore;
- its base64 form;
- store/key passwords;
- signing properties containing those values.

## Release policy

For normal IG Cleaner Pro GitHub releases, include the latest validated Android APK whenever the persistent signing requirements are satisfied. v120.34 established this as the production baseline. Its release artifact is:

`IG-Cleaner-Pro-Android-v120.34.apk`

Physical-device behavior remains a separate validation claim from build/signature verification.
