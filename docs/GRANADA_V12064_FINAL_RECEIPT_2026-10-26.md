# GRANADA v120.64 — verified official FINAL stable publication

**Date:** 2026-10-26T21:39:35Z (2026-10-26).  
**Official release:** [v120.64](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.64); `draft=false`, `prerelease=false` and **12 assets**.  
**Publisher:** [GitHub Actions 40404587656](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40404587656), `completed/success`.  
**Exact release target/source:** `593f9d4d0598ea6056bca2247c99e899970ffcb1`; [merge PR #247](https://github.com/michels-lab/IG-Cleaner-Pro/pull/247).  
**Prior stable:** [v120.63](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.63), publisher 40394937018, SHA `cb47df2eeda2f158df408e7a57dbda84600b622d`.

## Published assets and SHA-256 fingerprints

GitHub release API returned these twelve assets with matching digest metadata. The governed workflow independently validated local bundle checksums, production-signed Android packages and installer checksums before release.

| Published asset | SHA-256 digest |
| --- | --- |
| `IG-Cleaner-Pro-Android-Developer-v120.64.apk` | `sha256:bf7f84379616325b660131ce72448d7cc9c946d0caa2fcb86c71c06bc7b4639d` |
| `IG-Cleaner-Pro-Android-v120.64.apk` | `sha256:df2b5616524d4537a2dff0bee4b873cde6ba87c040a67d228898248b07720bbd` |
| `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.64.zip` | `sha256:f30abc315cf7857265a97caced1d88a77990e6bf90d9c51780f2560dc1899b47` |
| `IG-Cleaner-Pro-Desktop-v120.64.html` | `sha256:872b71354399c2705b98a4fbbaedd30a1355189fd5f7425f5433c7d8c301c19b` |
| `IG-Cleaner-Pro-Desktop-v120.64.zip` | `sha256:ec5658805d62ae61cc46157a81d5a1ad1323e1666b6b44b4d10def5a9014da88` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.64.exe` | `sha256:20ec67f8a61dc30d8ff018434036d368109cb06c24c8f9f7c13f76633d9e06bb` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.64.exe.sha256` | `sha256:c52ef2c0254664aba538abf92579e1a365b063220ed8743393f3bcda9baf3e24` |
| `IG-Cleaner-Pro-Windows-Setup-v120.64.exe` | `sha256:20c9dc3b796a0eb25bf57cf52f878436abde315b5269e6ca2ca63db9abc19bef` |
| `IG-Cleaner-Pro-Windows-Setup-v120.64.exe.sha256` | `sha256:ebb409f31a8a74d545eeb8fac99f4377759c9343cc83b253f91a5e8bb5a44004` |
| `Instagram-Cleaner-Pro-v120.64-logo.png` | `sha256:83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| `Instagram-Cleaner-Pro-v120.64-PRIVACY.md` | `sha256:f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| `SHA256SUMS.txt` | `sha256:62f9e05a15fe0ed63f6701b745f3d1977ffb30fcb5d647a9afc8e67f8539a10a` |

## Verified publication gates

- New Windows Unfollow/Cancel Chrome target-tab flow defaults to **one profile at a time**; explicit **Prepare 10 tabs (legacy)** remains opt-in per owner workspace/task. Functional code PR [#245](https://github.com/michels-lab/IG-Cleaner-Pro/pull/245) merged before this release; tests cover A → B → A backtracking, historical/WAL no-replay, protected targets and preserved no-click/unknown outcomes.
- Exact-head PR [#247](https://github.com/michels-lab/IG-Cleaner-Pro/pull/247) passed all ten checks after a corrected HTML title and an isolated flaky browser test rerun; initial test failure, successful rerun and safety stop documented on PR. The code was merged only when **10/10 GREEN**.
- The official publisher independently passed `release-request-gate`, `rendered-ui-qa`, Windows Setup public+Developer installed startup/uninstall, native Android Developer, production-key signed public+Developer Android side-by-side installation on emulator, asset integrity, official release feed and **12 uploaded artifacts**.
- Windows Setup is checksum protected; Authenticode is **not** configured. Android production signing is verified against the persistent certificate fingerprint. No Play Store, beta or RC version was published.

## What this release does NOT prove

No signed-in owner Instagram Unfollow or Cancel Pending success has been accepted in the user's actual session. Keep physical owner [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) open; repeated owner navigation [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230) likewise needs owner-device observation. CI Chromium fixtures and emulator results are **not** evidence that Instagram accepted a relationship mutation. No cookies, passwords, original protected lists, local action journals or browser data were modified by this documentation-only reconciliation.

## Post-publication governance

Consume the one-time v120.64 authorization: `authorized=false`, `status=published`, exact tag/run/SHA/date and 12 assets. Set manifest `currentStableRelease=v120.64` and reserve `nextRelease=v120.65` **without authorizing or publishing it**. Update README, sync/update guide and permanent logs. Do **not** overwrite the existing immutable v120.64 tag or republish any binaries.
