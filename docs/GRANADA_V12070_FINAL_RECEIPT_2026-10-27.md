# GRANADA — v120.70 official normal FINAL publication receipt (2026-10-27)

## Verified provenance

- Official [v120.70](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.70), published **2026-10-27T18:05:15Z**; `draft=false`, `prerelease=false`.
- Immutable `refs/tags/v120.70` and GitHub Release `target_commitish` both reference exact source `55a9f1d0865c4280d9ef0f9866b51476f8b8c786`. Governed [run 40555013922](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40555013922) concluded **SUCCESS**, all five jobs: authorization, installed Windows public/Developer setup and startup, installed Android Developer account/notes/JSON test, rendered Desktop/Android UI approval, and publication/integrity verification.
- Twelve published assets: Windows regular and Developer `.exe`, their two `.sha256` sidecars; Android regular and Developer signed APKs; Windows portable ZIP; Desktop standalone HTML and ZIP; privacy statement; logo; `SHA256SUMS.txt`.
- Regular Windows: [IG-Cleaner-Pro-Windows-Setup-v120.70.exe](https://github.com/michels-lab/IG-Cleaner-Pro/releases/download/v120.70/IG-Cleaner-Pro-Windows-Setup-v120.70.exe). Developer Windows: [IG-Cleaner-Pro-Windows-Developer-Setup-v120.70.exe](https://github.com/michels-lab/IG-Cleaner-Pro/releases/download/v120.70/IG-Cleaner-Pro-Windows-Developer-Setup-v120.70.exe).
- This record **consumes** v120.70's single authorized request and aligns release manifest to `currentStableRelease=v120.70`, `nextRelease=v120.71`. It does not edit the published release, tag, binaries or sign another APK.

## User-required corrections shipped

- The owner's previous v120.69 Windows photo confirmed **"Live list reached its 250-pages safety limit"**. This was an API cursor-page ceiling, not a per-user robot limitation.
- The independently developed [bulk reader PR #270](https://github.com/michels-lab/IG-Cleaner-Pro/pull/270) gathers Followers and Following in pages of Instagram JSON, not individual profile visits, with bounded 1500 pages and 100k unique members per list. Compare numeric stable account IDs across username changes, atomically save only both confirmed complete lists and never invent negative membership from an incomplete scan.
- [Final PR #271](https://github.com/michels-lab/IG-Cleaner-Pro/pull/271) introduced user-demanded preventive controls: serial request pace 2.5 seconds, 12-second break every 5 JSON pages, 90-second break every 25 pages, cancelable rests, immediate stop on HTTP 429/403/503 or `feedback_required`, server `Retry-After`, minimum 30 minutes of locally persisted cooldown across all Instagram workspaces using the robot Chrome, 15-minute repeat spacing after success. No automatic rerun, proxy cycling, bypass of security prompts or Unfollow.
- These are app-defined conservative waits, **not guaranteed safe Instagram rate limits**; Instagram can still restrict the session. The endpoints are private/undocumented.

## Real-world acceptance still OPEN

CI proves implementation and installed QA with fixtures; it **did not read the owner's actual live Instagram membership**, and does not establish that Instagram permits current complete lists. The previous v120.69 error is confirmed; success of v120.70 on the owner's account is not. [P0 tracking issue #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) must stay open until the user verifies both complete lists, date/totals/no-followback and no restrictions on the installed v120.70. A new FAIL or truncated list must not be mislabeled complete. No effect on prior ZIP imports, protected profiles, Unfollow/Cancel Pending click WAL or older complete snapshots. Next version v120.71 is reserved but **unauthorized** until new owner direction.
