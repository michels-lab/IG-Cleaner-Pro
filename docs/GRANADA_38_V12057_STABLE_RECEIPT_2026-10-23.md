# Operación Granada #38 — v120.57 FINAL stable release receipt

Published 2026-10-23T07:02:01Z, official [v120.57](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.57); **12 assets**; GitHub draft=false, prerelease=false.

- [Full official governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39913984383): **completed SUCCESS** for all five jobs including final publish.
- Release source SHA: `2ffea2280bc0438ad18931af655278b16a63edc1`.
- Normal Windows integrated public Setup installed, launched and uninstalled in CI; Desktop/Android actual rendered visual gates and production-signed public+Developer Android coinstallation/foreground proved in device gate; package checksum and official release asset validation succeeded.
- Normal InstaCleaner Windows robot change from [PR #215](https://github.com/michels-lab/IG-Cleaner-Pro/pull/215): saved per-target action history is validated after manual login and before all ten target tabs open, during processing and immediately before a click. Malformed or uncertain click evidence is never replayed as fresh action. Preserves original 40-profile cohort, protected list and journal.
- **Important boundary:** CI, even with real Chromium, does *not* verify an actual Unfollow or Cancel Pending on the owner's live signed-in Instagram account; real-world acceptance [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) remain OPEN.
- Post-publication receipt: `.michelslab/release-request.json` is `authorized:false,status:published`, exact run/commit/URL/time recorded; manifest and README public stable `v120.57`, next reserved `v120.58` (not released). No new release candidate or automatic republishing.
- The separate stale target-header identity safety review [PR #216](https://github.com/michels-lab/IG-Cleaner-Pro/pull/216) was not included in the already-published v120.57 release; integrate only after its exact-head tests pass and release separately if approved.
