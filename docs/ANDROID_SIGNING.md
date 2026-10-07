# Android Production Signing — IG Cleaner Pro

Updated: **2026-10-06**

## Stable signing identity

IG Cleaner Pro uses one persistent Android production signing identity for the stable package:

- Package: `com.michelslab.igcleaner`
- Key alias: `ig-cleaner-pro`
- Certificate SHA-256: `6FB7720E669ADFD36159A2E9781E15824526DC263900999A500BAB38A7B67D43`
- Certificate validity: through **2126-10-08** (100-year certificate; effectively permanent for the product lifecycle)
- Metadata authority: `release/android-signing.json`

The private keystore and its passwords are **not stored in Git**.

## Required GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions must contain:

- `IGC_ANDROID_KEYSTORE_B64`
- `IGC_ANDROID_KEYSTORE_PASSWORD`
- `IGC_ANDROID_KEY_ALIAS`
- `IGC_ANDROID_KEY_PASSWORD`

The release workflow restores the keystore only inside the ephemeral GitHub Actions runner.

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

For normal IG Cleaner Pro GitHub releases, include the latest validated Android APK whenever the persistent signing requirements are satisfied. The release artifact name for v120.34 is:

`IG-Cleaner-Pro-Android-v120.34.apk`

Physical-device behavior remains a separate validation claim from build/signature verification.
