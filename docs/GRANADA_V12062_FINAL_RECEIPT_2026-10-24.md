# Operación Granada — official v120.62 FINAL stable release receipt

**Date:** 2026-10-24 (published 2026-10-24T18:44:16Z).  
**Source of truth:** [GitHub stable release v120.62](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.62).  
**Publisher:** [GitHub Actions 40121318686](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40121318686), `completed/success`.  
**Exact tagged source SHA:** `9ad3719aa49378ee38bfb035bc4587ec1af7e7d4` (`main`). Tag ref points to this commit.  
**Release state:** `draft=false`, `prerelease=false`, official FINAL stable, **12 uploaded assets**. No RC, beta or Google Play publication.

## Verified public asset fingerprints

| Published asset | Verified SHA-256 (GitHub release digest) |
| --- | --- |
| `IG-Cleaner-Pro-Windows-Setup-v120.62.exe` | `1b53bd6ef8bc220e727942a567a1fcda3cb1ba245bdc95c7af3b20f5c0549ea0` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.62.exe` | `8b8e3e443ae71f092fda75597167016d8a04ea2274be185d26fb82e3c3998edb` |
| `IG-Cleaner-Pro-Android-v120.62.apk` | `7bcb1b4bb13e7e4ed21ea939df9098b0a5edceea2d820e05750393dfa798f018` |
| `IG-Cleaner-Pro-Android-Developer-v120.62.apk` | `6c949a0925d1af43459d822a7f42a4bda452bc6e6db4e63a5f2fb946f586f84a` |
| `IG-Cleaner-Pro-Desktop-v120.62.html` | `98b66ad5431210fb9f0e89e554a5dce4f802bc3ef76b1f463167f31a16b8fdac` |
| `SHA256SUMS.txt` | `55fcfe3124eeb117bbaf901934ce487b45259f623a32d8ed0e60b96ce5f148d4` |

The other six public release assets are the portable Windows robot ZIP, Desktop ZIP, two Windows per-installer checksum files, product logo PNG and privacy notice. Every published asset is listed on the official release page. Publisher's `Verify published release` step completed **successfully**, as did independent installed Windows, Android production-key public+Developer co-install, rendered Desktop+Android UI and bundle-integrity gates.

## Behavior and safety provenance

- [#238](https://github.com/michels-lab/IG-Cleaner-Pro/pull/238) merged safe explicit **Continue saved 10** vs **Plan new 40** for an owner's confirmed action-cohort mismatch. No mutation is performed merely by planning; the former unfinished ten, prior five attempts, uncertainty journal and protected data remain recoverable.
- [#239](https://github.com/michels-lab/IG-Cleaner-Pro/pull/239) merged the fully gated FINAL v120.62 request. The exact-source seven PR workflows passed, including negative Python saved-10/5-attempt/40-planned regressions, Windows installed/Chromium fixture, Desktop/Android UI, Android Developer, Profile Counts and Supabase isolation.
- Also fixed **release provenance drift** before merge: the original v120.62 candidate was naming v120.61 as previous stable while retaining v120.60's old publication run/SHA/time; test `test_published_stable_receipt_consumes_release_authorization` now enforces a complete `previous_publication`↔manifest match for a requested future release.

## Distinct evidence that remains OPEN

**Installed/emulated CI is NOT the owner's authenticated Instagram account.** No real owner-account Unfollow or Cancel Pending was performed or independently persisted by this publication. Keep [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172), [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230) open until actual installed v120.62 account-specific evidence and owner confirmation. No cookies, passwords, live profiles or protected history were transmitted during documentation closeout.

**Governance:** consume the one-time v120.62 release request, set `currentStableRelease=v120.62` and reserve `nextRelease=v120.63` **without authorizing it**. Reconciliation is documentation/state-policy only; it does not alter the tagged v120.62 binaries or grant automatic publication of a later version.
