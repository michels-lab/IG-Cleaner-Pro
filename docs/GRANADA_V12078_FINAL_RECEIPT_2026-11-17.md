# InstaCleaner Pro v120.78 — official FINAL stable publication receipt

- **Official publication:** 2026-11-17T21:06:55Z; [GitHub release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.78), `draft=false`, `prerelease=false`.
- **Exact tagged source:** `1c75831c59b457171c113978a6acb282d915d71c`. Production [publisher run #44174641647](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44174641647) **4/4 jobs SUCCESS**: release-request authorization, rendered Home/About UI, installed Windows Setup/Chromium QA, and production-signed stable Android with SHA-256 verification.
- **9 uploaded files:** one standalone Desktop HTML, Desktop ZIP, integrated Windows installer and legacy robot ZIP, signed stable Android APK, logo, privacy, installer checksum and SHA256SUMS. No RC, beta, prerelease or Developer Edition assets.
- **Source PRs:** Focus 30/cohort recovery [#366](https://github.com/michels-lab/IG-Cleaner-Pro/pull/366), handoff/incident audit [#367](https://github.com/michels-lab/IG-Cleaner-Pro/pull/367), exact-version/publisher [#368](https://github.com/michels-lab/IG-Cleaner-Pro/pull/368). Source PR #368 CI 10/10 PASS before merge.

## Official SHA-256 values

| Asset | GitHub SHA-256 |
| --- | --- |
| `IG-Cleaner-Pro-Android-v120.78.apk` | `844b549418e3ea53cf43e7b35fc46ffcaf7a480d559d742a6e56792cdd8a4224` |
| `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.78.zip` | `2b12a9673446c41480e05f9fa7ad5c6b52dd062df6dcc6e924bcfdad639d3b75` |
| `IG-Cleaner-Pro-Desktop-v120.78.html` | `0a378754f12e3ec0a8ec6711fc1f2b769008a5fceab0227ac9486771f99e8b76` |
| `IG-Cleaner-Pro-Desktop-v120.78.zip` | `760a76a7775b44de0048b9415207466d4e56bb40cc7b714447dbbfe6b286bd59` |
| `IG-Cleaner-Pro-Windows-Setup-v120.78.exe` | `2245572ce5d60d33032fa2e43515956bfdadb4ae11a48c71be56202808283d6d` |
| `IG-Cleaner-Pro-Windows-Setup-v120.78.exe.sha256` | `06ed822172c3a01e3583cc35bc4fb20f5ef9d531722688319f2cf4eb3c193078` |
| `Instagram-Cleaner-Pro-v120.78-logo.png` | `83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| `Instagram-Cleaner-Pro-v120.78-PRIVACY.md` | `f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| `SHA256SUMS.txt` | `66429ace9a5f0b2eb920bf0a8bd144d3fb3445a72dc2831f09ff4b4f98aaac57` |

## Functional contents and exact limits

- **Focus 30 bug fix:** reserve batch durably before writing secondary history; rollback failed writes; prevent temporary decrease in available count without saved cohort. Render Reviewed/recovery and direct per-profile Open links even if browser blocks tab requests. The owner explicitly decides review outcomes; no silent OK.
- **Recheck, Double Check and Pending:** fail closed if active cohort cannot persist, do not advance no-repeat cycles on a rejected batch. Explicit Couldn't review releases only genuinely unconfirmed attempts, with rollback if that write fails. Pending Double Check backup remains account-scoped and preserves prior confirmed reviews.
- **Desktop/local Chrome localStorage continuity:** existing v120.77 browser history is not migrated/deleted by the app's source change. Back up via Vault before changing HTML paths/origins/browser profiles; `file://` origin and browser boundaries can affect where local data appears.
- **Owner acceptance NOT verified:** the signed-in browser that failed Focus 30 on v120.77, the two real Instagram accounts, live Unfollow/Cancel Pending and physical Windows↔Android synchronization were not used in CI. [P0 #360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) remains open for additional count rebound/cross-account conditions; publication is for the owner to perform installed physical testing.
- **Authority consumed:** new exact-tag one-time owner-directed stable release permission ('op granada y release') was used by #44174641647. Metadata follow-up records `authorized=false`, current stable **v120.78**, next reserved **v120.79 not authorized**, while `release_hold=true` and `owner_final_acceptance.approved=false` remain unchanged.

## Download

Official release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.78
Official publisher: https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44174641647
