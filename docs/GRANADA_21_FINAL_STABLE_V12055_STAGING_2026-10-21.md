# GRANADA — Official final-stable v120.55 staging (no RC, no publish request yet)

**Date:** 2026-10-21. **Owner standing authorization:** a GRANADA execution may publish the **final stable official release** only when all product gates succeed, without another redundant instruction; release is not obligatory on every GRANADA.

## Actual implemented preparation

1. Desktop distributable source, About display, version dialog, sidebar and HTML document title consistently identify candidate **v120.55**; the existing underlying Engine v119 does not change.
2. Android `app/build.gradle.kts` and pinned production signer manifest `release/android-signing.json` now use `versionCode 12055 / versionName 120.55`; **certificateSHA256 and keystore alias are unchanged** for in-place APK updates. No new signing key is generated, committed or shared.
3. `release/RELEASE_NOTES.md` adds truthful final-release notes for new Desktop lane UX, unfinished 40-cohort handling, verified no-click outcomes, Developer/Windows diagnostics, and remaining real Instagram acceptance. README continues to identify v120.54 as **latest published stable**, not a fabricated 120.55 release.
4. The distribution manifest already advertises `nextRelease: v120.55` while retaining `currentStableRelease: v120.54`. The prior `.michelslab/release-request.json` remains `status: published, authorized:false, tag:v120.54`. **This branch is source staging only**; merging it cannot trigger the official publisher.

## Release gate before changing request

- Validate exact HEAD with Desktop/Android/Windows UI + installer; verify Developer emulator actual Sign in / Account navigation, notes and Android Downloads JSON export. The new mandatory publisher gate from PR #186 must be in main.
- Include only merged, green P0 action-safety changes, including PR #188 if validated. PR #143 English translation is separately occupied and not silently merged.
- Final authorized release request must be a distinct `main` change after full CI with exact source version. It will trigger `.github/workflows/release.yml`, which must verify real rendered UI, integrated Windows Setup **install/launch/uninstall**, independent Windows Developer Setup, production owner signing for public + Developer Android, signed APK version/package/certificate, SHA256SUMS/asset audit, and official latest-release feed.
- User's live signed-in Instagram Unfollow / Cancel acceptance for issue #172 cannot be inferred from Chromium fixtures or CI. Such testing occurs on the official published Setup per owner's explicit preference and must remain an open issue until actually observed.
- When official GitHub publication is proven, update docs/manifest/release evidence to `currentStableRelease=v120.55`, lastPublished SHA/run/checksums and the README link; never claim success before the artifacts exist. No RC, public preview, pre-release or permanent download link to an Actions artifact.

## Non-destructive boundary

No journal, workspace, protected profile, batch, cloud account, keystore, private password, browser cookie or state schema was modified. Staging modifies only release-bearing source/metadata/notes + this document. The last official published stable remains [v120.54](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.54) until the governed final release completes.
