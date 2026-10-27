# GRANADA — live Instagram Followers + Following independently of ZIP (2026-10-27)

## Owner requirement and gap

The owner explicitly requests a **manual real-time verification** of who follows them and whom they follow, from the owner-supplied same-origin Instagram friendships reference, while retaining Instagram ZIP import as a separate alternative. Previously `profile_lists_live.py` existed but only inside `ActionRobot` Followback Audit for **pre-imported candidate targets**, so it did not retrieve or display the full current relationship set independently. This is the distinct missing capability, not the same as performing Unfollow or calculating numeric Profile Counts.

## Implemented: isolated v120.69+ candidate, NO release yet

- New native local Windows `LiveRelationships` worker, launched by **Verificar seguidores y seguidos ahora** in Automations, with an owner-confirmed read-only request. It uses the exact selected Instagram @handle, current authenticated persistent robot Chrome, same-origin GET list pagination, cross-process ActionLease, single-worker admission, manual login verification, fail-closed owner/challenge checks, and a stop option.
- Live results have four user-selectable complete sets: Followers; Following; Following minus Followers (`not_following_back`); Followers minus Following (`fans`). Each is paginated at 100 usernames per local request, not truncated to a batch of 30/40, and displays independent verified counts.
- A complete pair of lists is saved atomically, per app login + Instagram workspace hash, with a capture timestamp. A partial/blocked/rate-limited/malformed/paused run **never replaces** the prior proven-complete evidence and never asserts a fresh negative relationship. Prior saved data is clearly labeled historical after restart/failure. UI rejects snapshots whose verified handle differs from the currently selected account.
- The collector reads only selected Instagram relationship lists; it does not log/extract cookies, session tokens or private API response bodies, and it never posts mutation requests, revisits target profiles, alters saved ZIP imports, protects, click write-ahead journal, or action-batch history.
- Strict terminal paging was strengthened: Instagram must say `has_more=false` on the last cursor page; absent or contradictory `has_more` is *incomplete*, not proof that profiles do not follow back. Login owner and security challenges are reevaluated during paging.
- Existing per-candidate Followback Audit source remains available unchanged, while the new full snapshot requires **no preloaded targets or ZIP**. No silent automatic periodic requests: each fresh scan is separately confirmed. 'Real-time' means *on-demand currently queried snapshot*, not uninterrupted subscription to Instagram.

## Reproducible QA and release gates

- `tests/test_live_relationship_snapshot.py` (owner isolation, last snapshot paging, fail-closed partial page, no journal replay, explicit consent, active worker denial), `tests/test_live_relationship_bridge.py` (real loopback token/origin/scope/paths), and existing `tests/test_profile_lists_live.py` terminal cursor negatives.
- `tests/live-relationships-browser.test.cjs` checks the built HTML in real Chromium with fully intercepted local data: one confirmation for live scan, accurate four-set read-only display, no relationship-action POST, correct owner scope, no collision with the existing automation live-status element.
- Workflows: general CI, Profile Counts, Android/Developer, Desktop-rendered and **installed Windows Chromium**. Do NOT merge until all exact-head mandatory checks green, then separate normal FINAL release after current v120.68 publication completes; no RC, prerelease or overwriting signed assets.
- The owner's actual Instagram session may fail to expose the undocumented `ds_user_id`/friendships endpoints or hit a rate limit. CI simulates the endpoint, **not** live Instagram or actual relationship counts. Human Windows/Instagram acceptance is still OPEN. Do not falsely claim that their current following/follower totals were observed by the assistant.

**State:** isolated source and QA submitted for validation, not merged, not released, no live owner login or relationship mutation.