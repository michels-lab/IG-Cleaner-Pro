# InstaCleaner Pro v120.78 — immutable FINAL stable publication receipt (2026-11-17)

- **Official published:** [v120.78](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.78), UTC 2026-11-17T21:06:55Z, draft=false, prerelease=false.
- **Exact tagged source and publisher HEAD:** `1c75831c59b457171c113978a6acb282d915d71c`. The owner-authorized [governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44174641647) **COMPLETED SUCCESS, 4/4 required jobs** (scope authorization, exact-source rendered UI, installed Windows Setup, signed Android production and release verification).
- **Public artifacts:** nine immutable assets, including standalone Desktop HTML, Desktop ZIP, Windows native Setup EXE and portable ZIP, production-signed stable Android APK, logo, privacy notice, Setup SHA256 and SHA256SUMS.txt. No RC, beta, Developer edition or Play Store claim.
- **Functional source:** [Focus cohort root-cause fix #366](https://github.com/michels-lab/IG-Cleaner-Pro/pull/366); [evidence/handoff #367](https://github.com/michels-lab/IG-Cleaner-Pro/pull/367). Focus 30 fails closed if storage cannot save, shows Reviewed and manual Open links before tab requests, and explicit unconfirmed requeue never overwrites confirmed reviews. Pending Double Check backup/no-repeat included in main before tag.
- **Owner testing NOT yet verified:** the exact Chrome error, two real Instagram sessions, live Unfollow/Cancel Pending, physical Android/Windows sync, two concurrent relationship-changing robots and full P0 [#360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360). GitHub CI cannot prove real Instagram behavior. The owner requested the FINAL release to run these physical checks afterward.
- **Version governance:** v120.78 one-time owner release permission **consumed** by this publication. Next reserved v120.79 is **not authorized**; retain release_hold=true, owner_final_acceptance=false and all incomplete acceptance flags. Do not overwrite tag/assets.

## SHA-256 digests from GitHub release API

| Published asset | GitHub SHA-256 |
|---|---|
| IG-Cleaner-Pro-Android-v120.78.apk | `sha256:844b549418e3ea53cf43e7b35fc46ffcaf7a480d559d742a6e56792cdd8a4224` |
| IG-Cleaner-Pro-Automatic-Robot-Windows-v120.78.zip | `sha256:2b12a9673446c41480e05f9fa7ad5c6b52dd062df6dcc6e924bcfdad639d3b75` |
| IG-Cleaner-Pro-Desktop-v120.78.html | `sha256:0a378754f12e3ec0a8ec6711fc1f2b769008a5fceab0227ac9486771f99e8b76` |
| IG-Cleaner-Pro-Desktop-v120.78.zip | `sha256:760a76a7775b44de0048b9415207466d4e56bb40cc7b714447dbbfe6b286bd59` |
| IG-Cleaner-Pro-Windows-Setup-v120.78.exe | `sha256:2245572ce5d60d33032fa2e43515956bfdadb4ae11a48c71be56202808283d6d` |
| IG-Cleaner-Pro-Windows-Setup-v120.78.exe.sha256 | `sha256:06ed822172c3a01e3583cc35bc4fb20f5ef9d531722688319f2cf4eb3c193078` |
| Instagram-Cleaner-Pro-v120.78-logo.png | `sha256:83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| Instagram-Cleaner-Pro-v120.78-PRIVACY.md | `sha256:f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| SHA256SUMS.txt | `sha256:66429ace9a5f0b2eb920bf0a8bd144d3fb3445a72dc2831f09ff4b4f98aaac57` |

The SHA-256 digests verify integrity; they do **not** imply Windows Authenticode signing (not configured). The APK was verified against the existing production Android certificate identity in the governed publisher.

## Owner verification: protect historical reviews

The owner's old local v120.77 standalone HTML may store reviews under its original browser file/path context. **Export full backup from Vault before opening a differently named v120.78 HTML or switching browsers; import the backup where needed and verify counts.** Do not delete Chrome site data or reset Reviewed. Start with a small Focus batch and confirm actual opened tabs, visible Reviewed, persistent decisions after reload, and independent A→B→A Instagram account histories.

