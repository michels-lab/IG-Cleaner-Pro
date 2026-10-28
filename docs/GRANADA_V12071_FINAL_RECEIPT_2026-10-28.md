# GRANADA — v120.71 FINAL release receipt

**Verified release:** [v120.71](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.71)  
**Publication (UTC):** 2026-10-28T00:32:34Z  
**Tagged exact main commit:** `74a91104dd2f2f29c88b8abadbff76a6f3bfd466`  
**Release type:** official normal stable FINAL (`draft=false`, `prerelease=false`)  
**Publisher:** [GitHub Actions 40608318126](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40608318126) — 5/5 mandatory jobs SUCCESS  
**Assets:** 12 (public+Developer Windows installers, signed public+Developer Android APKs, standalone Desktop HTML/ZIP, Windows executable package, SHA256SUMS, .sha256 and official metadata). Signing uses persistent official certificate verified by the publisher.

## Delivered
- Two owner-bound detachable InstaCleaner account tabs/windows, whose profile selection stays fixed independently across reloads.
- Windows button to open TWO separate Chrome persistent browser windows with distinct per-owner/account user-data directories for manually signing into different Instagram accounts; browser cookies are outside robot-data exports.
- Read-only bulk relationship Followers/Following verification controls with guarded Recommended, Cautious and Custom presets, safety-floor pacing and 429/challenge cooldown.
- Previous reviewed/visited results, protected entries, action journals and ZIP imports remain in canonical storage; **no concurrent relationship-changing Unfollow or Cancel Pending worker is enabled**.

## Evidence and limits
- Candidate PR #279 passed 7/7 workflows (Profile Counts, Desktop real Chromium, Windows installed app + Developer, Android About, Android Developer, general CI, documentation), exact PR head `91990e29dd54d2e894eb4ae24e31560886d7e9fd`.
- Final publisher 40608318126 passed all 5 jobs, including independently installed public+Developer Windows and signed co-installed Android binaries, Desktop/Android screenshot proof, hashes and updater acceptance.
- Real owner Instagram account A/B login correctness, full follower/following private endpoint success, and live Unfollow/Cancel Pending action verification remain **unobserved**. Owner should first open the installed v120.71 Windows app, log into each isolated Chrome profile manually, confirm the handle shown on Instagram for each before any relationship action and test read-only verification. Never treat source CI or manual dual browser launch as real two-worker action acceptance.
- No new publication is authorized for v120.72. Previous one-time v120.71 request consumed.
