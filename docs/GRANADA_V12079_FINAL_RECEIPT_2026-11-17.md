# InstaCleaner Pro v120.79 — immutable FINAL stable publication receipt (2026-11-17 local / 2026-11-18 UTC)

- **Official public release:** https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.79 ; published 2026-11-18T00:10:39Z, draft=false, prerelease=false.
- **Exact tagged source:** `b226cc7dbf4d3013959a303a05847ca03c6cd4e2`. **Governed publisher:** https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44204338029 — **4/4 SUCCESS** (authorization, installed Windows Setup, exact-source rendered Android + Desktop UI, production-signed Android install+launch, artifact integrity).
- **Public payload:** 9 stable-only assets (Desktop standalone HTML primary, Desktop ZIP, Windows Setup EXE + portable robot ZIP, signed Android APK, logo, privacy notice, Setup checksum, SHA256SUMS.txt). No RC/Developer binaries, no Play Store claim, Windows EXE not claimed Authenticode signed.
- **Granada fixes included:** compact Focus batch and history, explicit quota-safe retry, preserved Reviewed/Pending/Done on inconclusive Focus/Double Check/Followers/Mutuals, redacted diagnostics and no phantom decrement, storage corruption guard. All new decisions still require owner confirmation.
- **Publisher recovery:** the first exact-source publisher 44202580405 correctly FAILED due to duplicate Android screenshot artifact names (cancelled 186-byte placeholder plus complete 9.3-MB evidence). Fix in `b226cc7d` selects one complete artifact by ID, rejects ambiguity and forbids failed/cancelled runs to upload fake evidence; checksums + APK/screenshot source validation remain mandatory.
- **Real-user acceptance remains PENDING:** physical Chrome file origin/backup migration, real-account Focus 30 and counter persistence after reload, A→B→A two-account isolation, Unfollow/Cancel actions and Android/Windows cross-device state. [P0 #360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) and [storage #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371) remain open.
- **Version governance:** one-time v120.79 authorization CONSUMED; next v120.80 reserved and NOT authorized. release_hold=true and owner_final_acceptance=false retained. Do not overwrite release tag/assets.

## Published SHA-256 digests (GitHub Releases API)

| Asset | SHA-256 |
|---|---|
| IG-Cleaner-Pro-Android-v120.79.apk | `fcaa7ba6a8b686ae34e595c34b02b37eb627e8877d36d6da6bcabc2e9cfe7895` |
| IG-Cleaner-Pro-Automatic-Robot-Windows-v120.79.zip | `395b5bdc3ebca3817a459d74deee84a6151ce0dc8aa952409d03d1cdfa085a60` |
| IG-Cleaner-Pro-Desktop-v120.79.html | `8d464e50655fbc5109b1e709e6a9f48ebcb7e8cc1211c395423ba0b133dac136` |
| IG-Cleaner-Pro-Desktop-v120.79.zip | `4924f06fc20230b8959b7a424a31d05de22683e43209c371a5c0699515c30bc2` |
| IG-Cleaner-Pro-Windows-Setup-v120.79.exe | `a934044500259866b0221f4107c4e797c50af8d28e08bd19bc3367e0f6d67401` |
| IG-Cleaner-Pro-Windows-Setup-v120.79.exe.sha256 | `31b4b5cc5c2421ebe77f8619cfe7bf9db5030e8f4d04a6b3c920a6afad0b980e` |
| Instagram-Cleaner-Pro-v120.79-logo.png | `83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| Instagram-Cleaner-Pro-v120.79-PRIVACY.md | `f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| SHA256SUMS.txt | `2fa697395bb355f5b102dc19d78e23853f53283fd8763b85b7bbe75e86dbfd6d` |

**Owner verification:** back up Vault data before moving from another standalone HTML path/browser. Install/update normally on Windows; verify one small Focus batch and real opened tabs, save only actually reviewed decisions, refresh and compare count, repeat A→B→A without clearing local storage.
