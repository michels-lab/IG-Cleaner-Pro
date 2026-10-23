# Operación Granada #33 — Normal InstaCleaner robot: verified durable outcome, not optimistic UI

Date: 2026-10-22. Scope: **normal Windows InstaCleaner**, both Unfollow and Cancel Pending. No Developer Edition investment.

## Reproducible source weakness
In `tools/profile_actions.py:perform_visible_action`, several Unfollow and Cancel Pending branches called `_verify_final_state` on the **same JavaScript-rendered page immediately after the click**. If a frontend optimistically switched the target's button to `Follow`, the worker returned `ok` without making an independent read-only round trip. Instagram can visually change before its backend commits a request. An unchanged relationship on a subsequent page load could therefore be falsely counted as a confirmed mutation.

## Source repair
- After a real, owner-approved Unfollow's menu or private-confirmation click, treat immediate UI as **provisional**; only return `ok` after the existing `_verify_unfollow_after_readonly_refresh` performs one new profile navigation and observes the same exact owner and target with a stable Follow / Follow Back state.
- Apply the same requirement after Cancel Pending (Requested → Follow). The existing `_verify_cancel_after_readonly_refresh` must positively confirm Follow/Follow Back after one read-only reload; otherwise return `review` even if the first page optimistically flipped to Follow.
- Never repeat a relationship-changing click when rechecking: saved write-ahead click-intent remains the authority. If a profile redirects, owner identity changes, a security challenge appears or the server still says Following/Requested, **preserve `review`/`blocked` and retain original journal**. No GraphQL POST and no new private Instagram endpoint.
- Existing no-action terminal observations (`already_not_following`, `already_not_requested`) are separate and unchanged. Account protection, 10-tab batch waves, saved 40→10 cohorts and explicit owner approval remain intact.

## Acceptance matrix
Real Playwright + offline Instagram-like server fixtures must simulate:
1. Follow button appears immediately after Unfollow but **reload returns Following** → `review`, no second click.
2. Follow appears immediately after Cancel Pending but **reload returns Requested** → `review`, no second click.
3. Server actually persists Follow / Follow Back on reload → `ok`, exactly one read-only refresh and one set of consented relationship clicks.
4. Outdated Pending, wrong owner, locked/private dialog, language and unchanged status never generate false `ok`.

CI/Windows installed tests are simulated and do **not** prove real Instagram mutation acceptance. P0 issues #172/#164 stay open pending evidence from the normal owner-installed app. No RC, no auto-release based merely on green mocks.
