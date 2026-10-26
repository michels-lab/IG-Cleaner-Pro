# Operación Granada — v120.63 FINAL stable: verified GitHub publication

**Publication:** 2026-10-26T20:32:03Z; [official stable release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.63); `draft=false`, `prerelease=false`, **12 assets**.  
**Publisher:** [GitHub Actions 40394937018](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40394937018), `completed/success`.  
**Exact tag source:** `cb47df2eeda2f158df408e7a57dbda84600b622d` for `refs/tags/v120.63` and publisher `head_sha`.  
**Channel:** regular FINAL stable, no RC, beta or Google Play claim.

## Public artifact SHA-256 digests

The GitHub release API reports these exact digest values:

| Asset | GitHub-reported SHA-256 |
| --- | --- |
| `IG-Cleaner-Pro-Android-Developer-v120.63.apk` | `32e955a6c3cce6cb1ca26d71a2ec94845298085dfe36775fad85f15da6c9919b` |
| `IG-Cleaner-Pro-Android-v120.63.apk` | `56944baac17eb047587b8901ab6306935ae2f50b7fae3fba1d7f2fc0974a6c8d` |
| `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.63.zip` | `208f98534b3de5b1e64a00a4c8f213413e64c179b13e0ee75adf5ac1ae8e7109` |
| `IG-Cleaner-Pro-Desktop-v120.63.html` | `49f3530e7d50fb1d33651b8ecaefe25c4774450d12b61cc8420b8a56ea8fa265` |
| `IG-Cleaner-Pro-Desktop-v120.63.zip` | `08a2b20f824d51913eaf7277c26e2220a7c6d4dc8612853981f95bfbbbb4951e` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.63.exe` | `f4c19083498fa7a594b22c870a1ea77d5eab42b76c7ca541c57d0eaa5777f785` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.63.exe.sha256` | `e874f7c75f8eb320bd9f5d315c14da09180de17e127527fc8b1823a62d1b2753` |
| `IG-Cleaner-Pro-Windows-Setup-v120.63.exe` | `d2221aad8da4d248b1bb5e18215647c115c011d415f9181cd529985620e3b045` |
| `IG-Cleaner-Pro-Windows-Setup-v120.63.exe.sha256` | `95e9a90c5af1c7a3f6d796b0e9d2f02ae5598c18b93645e43934a52f0241ff42` |
| `Instagram-Cleaner-Pro-v120.63-logo.png` | `83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| `Instagram-Cleaner-Pro-v120.63-PRIVACY.md` | `f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| `SHA256SUMS.txt` | `04925f3afa353dfc310b1c80e41f8c4260b3fef0ff2f573d58f3f2efe461d7a7` |

The official publishing workflow completed its required installed Windows/Developer, signed Android production-key public/Developer co-install, rendered Desktop/Android UI, checksum and release feed gates. Release evidence is not owner-account Instagram acceptance.

## Source scope and safety boundary

- [#241](https://github.com/michels-lab/IG-Cleaner-Pro/pull/241): owner-session-bound proof reuse to reduce unnecessary navigation to the owner's own Instagram profile, without bypassing mismatched owner or login challenge.
- [#242](https://github.com/michels-lab/IG-Cleaner-Pro/pull/242): decouple visible batch size/rest from independent 120-visits-per-hour safety pacing; explain waits without resetting visit/rest history.
- [#238](https://github.com/michels-lab/IG-Cleaner-Pro/pull/238) and [#239](https://github.com/michels-lab/IG-Cleaner-Pro/pull/239): preserve explicit saved-ten/new-forty decision and the existing no-replay action journal from v120.62.
- **Not in the published v120.63 binary:** ongoing post-release [#245](https://github.com/michels-lab/IG-Cleaner-Pro/pull/245) sequential-vs-ten-tab profile navigation changes. They require separate gated source integration and publication.

**Still unverified:** no evidence of real-account Instagram Unfollow or Cancel Pending success. [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230) remain physical owner acceptance gates. No protected accounts, cookies, browser journals or personal relationship data were edited by this release-metadata reconciliation.

## Post-publication governance

- Consume the one-time `v120.63` request (`authorized=false`, `status=published`) and associate exact tag/run/time, after independently reading GitHub release and publisher.
- `currentStableRelease=v120.63`; `nextRelease=v120.64` is **reserved only** and not authorized or published.
- Update README, sync guidance, migration/update guide and historical release note to distinguish published stable from later source PRs.
- **Do not republish v120.63.** This receipt is a metadata correction only, not a new release, binary update, real Instagram operation or physical user acceptance.
