# Granada 24-nov-2026 — visible owner identity, offscreen/transparent Chromium controls

## Root cause and affected behavior

The Windows action robot reuses the read-only Instagram owner discovery in `tools/profile_counts_instagram.py`. The prior `visible_link_descriptors` viewport test accepted navigation links that retained positive width/height and bottom yet were entirely to the left/right or below the live viewport. The owner-profile fallback also counted `Edit profile` role controls without verifying that the unique control was truly visible within the viewport; transformed/transparent controls could masquerade as authenticated ownership.

These are positive authentication signals, so an offscreen/stale response is a **source defect / regression gap**, not a harmless CSS preference. No owner accounts were accessed during this repair.

## Real code change

- Require ordinary Profile-navigation links to intersect current Chromium viewport in all four directions, with nonzero CSS opacity.
- Require exactly one visible, viewport-intersecting `Edit profile` control and matching heading on the exact expected owner URL. An unreadable candidate is **not** proof.
- Preserve existing read-only current-owner check, sibling Chrome tab checks, session-id binding and fail-closed challenge/password behavior; do not add any owner-profile visit, bypass a gate or perform any Instagram action.

## Negative/positive regressions

`tests/test_profile_counts_home_identity.py` now tests: (a) collapsed/offscreen Profile nav does not identify the owner, while a visible link does; (b) offscreen Edit profile is insufficient; (c) transparent Edit profile is insufficient; (d) exact URL + heading + visible Edit profile is accepted. Uses intercepted offline Chromium and synthetic handles, not the owner's Instagram session.

**Evidence status when authored:** [PR #410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410) OPEN; exact-head GitHub CI must pass before merge claim. The test is intended to fail on the earlier implementation (offscreen link/button accepted). No physical live-owner improvement can be asserted from CI alone.

## Remaining & distribution

- #230 actual self-profile navigation count and physical owner verification **OPEN**.
- Five P0 acceptance gates #371, #377, #360, #164, #172 **OPEN**; progress remains **7/12 = 58%**.
- [v120.81 FINAL](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.81) is still the latest published stable; #409 and this source change are **not** included in it.
- v120.82 is reserved only, `release_hold=true`; no RC, prerelease, automatic publisher, or claim of real Unfollow/Cancel Pending success.
