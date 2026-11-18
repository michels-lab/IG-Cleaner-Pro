# Granada v120.80 — verified FINAL stable publication receipt

**Local date:** 2026-11-17 (America/Monterrey); **GitHub publication:** 2026-11-18 04:21:23 UTC.

## Authoritative publication evidence

- Official immutable release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80
- Tagged source commit: `e5396cf2710cbd6d9f9ac7f03e5e6eeef948560b`.
- Governed release workflow: https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44235048175 — **completed, success, all four jobs SUCCESS**: request/authorization gate, exact-commit rendered UI proof, installed Windows Setup and startup acceptance, signed Android and asset publisher.
- GitHub release **draft=false**, **prerelease=false**; tag resolves to the exact commit above.
- Exactly **nine public assets** with GitHub SHA-256 digests and bundled `SHA256SUMS.txt`.
- Windows integrated Setup compiled, installed, launched, upgraded, uninstalled and preserved local state in automated QA. Windows Setup is SHA256 verified; Authenticode signing remains not configured.
- Production Android stable `com.michelslab.igcleaner` APK signed with established production certificate, installed and started in emulator; no Developer Edition APK/installer published.
- Desktop standalone HTML and Android Home/About runtime visual checks passed on matching final source.

## Download artifacts and SHA-256

| Stable artifact | Exact SHA-256 |
| --- | --- |
| `IG-Cleaner-Pro-Android-v120.80.apk` | `3c9e1223bc2f8bdc91dc1ad71851cc049cf27148a40cfb5ce21e4b1dc2a4fd8f` |
| `IG-Cleaner-Pro-Windows-Setup-v120.80.exe` | `59f946792805d0fcab883bf7a9430dd30313cf6ab2781848c36852f39f9b0faa` |
| `IG-Cleaner-Pro-Desktop-v120.80.html` | `9816e6f2e0881d0a6cccc977efcd0bacd489d1112c7480e7f4c7d7fcecc10e40` |

Other assets: Desktop ZIP, Windows robot ZIP, Setup .sha256, official logo PNG, Privacy MD and SHA256SUMS.txt. See the official release for complete artifacts and digests.

## Source scope

- Merged PR #373: Pending imported-zero freshness versus old 52, Android provenance, 1,000-row-provider-cap-resistant complete reviewed metadata and unique native Pending profiles across Home/Requests/Focus. Synthetic fixture verification; no actual user Instagram export examined or rewritten.
- Merged PR #374: ordered native IO/UI account transition barrier and generation-guarded Focus reads/decisions, including A→B→A, sign-out, embedded WebView login, explicitly confirmed profile-delete fallback.
- Merged PR #375: owner-requested single-use stable v120.80, Android/Desktop versioning and manifest/signing metadata, official release authorization and 12/12 candidate checks before merge.
- No RC, beta or publicly distributed Developer Edition; prior stable v120.79 assets immutable.

## Still unverified by the owner

Live signed-in Instagram Focus 30 (including the original zero-tab issue), counters after reload (#360), real Pending request count and A/B state (#24), exact-target Unfollow/Cancel, two concurrent user sessions/actions, and physical phone/Windows cross-device behavior. CI is **not** proof of these facts. Do not close the P0 issues as owner-accepted.

Export a Vault backup before moving/opening the standalone HTML in another path/browser origin. Never clear the browser's localStorage/IndexedDB to diagnose mismatched counts.

## Single-use release control

On success the release request was updated to `authorized=false`, `status=published`, `published_run=44235048175` and the immutable tag source. Readiness retains `release_hold=true`, `owner_final_acceptance.approved=false`, and a consumed v120.80 exact-tag device-review exception. **Next v120.81 is reserved without authorization; no automatic subsequent release.**
