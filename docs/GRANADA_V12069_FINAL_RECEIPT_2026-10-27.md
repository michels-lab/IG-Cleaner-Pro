# Operación Granada — v120.69 FINAL official publication receipt (2026-10-27)

## Verified published release

- **Normal GitHub FINAL:** [v120.69](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.69), published `2026-10-27T16:24:10Z`. `draft=false`, `prerelease=false`. The exact `refs/tags/v120.69` points to commit `3808c58fab35768fc769f1afef270897da014276`.
- **Publisher:** [GitHub Actions run 40539017886](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40539017886) with result **SUCCESS**. Required jobs: release-request-gate, rendered-ui-qa, Android Developer installed Account/notes/JSON test, Windows installed public/Developer native Setup, and final artifact publishing/verification all completed successfully. Build/publisher gated SHA-256 checksums and produced 12 assets; we did not independently reinstall on the owner's computer.
- **Windows public:** `IG-Cleaner-Pro-Windows-Setup-v120.69.exe`; **Windows Developer:** `IG-Cleaner-Pro-Windows-Developer-Setup-v120.69.exe`; both have separate `.sha256` assets.
- **Android:** `IG-Cleaner-Pro-Android-v120.69.apk` and `IG-Cleaner-Pro-Android-Developer-v120.69.apk`, with production signing tests and distinct packages.
- **Desktop:** `IG-Cleaner-Pro-Desktop-v120.69.html` and `IG-Cleaner-Pro-Desktop-v120.69.zip`; portable legacy Windows ZIP, logo, privacy notice and `SHA256SUMS.txt` complete the set.
- Previous publisher [40530976884](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40530976884) was canceled at native Setup. It did **not** publish v120.69. [PR #267](https://github.com/michels-lab/IG-Cleaner-Pro/pull/267) fixed unbounded installer QA waits; the successful publisher re-ran the mandatory gates on the exact release commit. Previous v120.68 tag/assets remain unchanged.

## New user-visible Windows feature

In installed Windows: **Automations → Verify live Followers and Following**. Choose the exact signed-in account and explicitly approve a read-only live scan, using the Windows robot's authenticated persistent Chrome. The app attempts to read both complete current lists without importing an Instagram ZIP, calculates Not following me back / Fans, then records a dated, isolated complete snapshot. It never auto-Unfollows. See [Windows quickstart](LIVE_FOLLOWERS_WINDOWS_QUICKSTART.md).

## Honesty and outstanding validation

No test accessed the owner's actual Instagram followers/following, performed real Instagram Unfollow, bypassed Instagram challenges or verified that Instagram's undocumented live friendships endpoint is available on the owner's account. The app deliberately rejects partial lists, security challenges or a mismatched account and preserves prior snapshot provenance; the scan has an initial 25k-per-list ceiling. Physical installed Windows/live Chrome and actual counts require the owner's direct test. Windows Setup is not Authenticode-signed; the assets have SHA-256 checksums. v120.70 is reserved but not authorized for publication, and this receipt is documentation only.
