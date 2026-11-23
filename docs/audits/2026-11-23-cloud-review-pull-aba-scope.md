# GRANADA P0 #360 — Reject stale cloud-review downloads after A→B→A

Date: 2026-11-23. Parent merged source: #401 (robot WAL), #402 (Focus v4 quota), #403 (unreadable Focus cohort).

## Root defect

The Desktop browser's `pullProfileState()` awaited `readCompleteProfileState('*',{fresh:true})` and only then called `applyOneState(r)` against whichever account's global `doneSet`, `reviewedMeta`, `pendingReviewedMeta` and `localStorage` were current **after** the await. A slow remote A response could therefore apply and persist original A's reviews under account B after an account switch. A→B→A was also unsafe because matching account names alone don't prove the response belongs to the current browser generation. An owner sign-out/sign-in could produce the same stale completion.

This is a credible source-level cause of confusing Focus counters and account contamination, **not** a claim that it is the sole cause of the owner's 30-review counter rebound.

## Code

- Capture signed-in Supabase owner, active Instagram profile identifier, and profile generation **before** awaiting cloud pages.
- After the entire cloud response resolves, before any `applyOneState`, `localStorage` writes or UI rendering, compare all three against the current context. If any changed, stop with an explicit owner-safe error: no Reviewed, Pending, protected, open attempts or counters are applied, no writes happen, and the caller can run a new pull in the selected account.
- Match the independent owner/profile generation proof already required by `pushProfileState()`. Do not guess profile identity from usernames and do not use a visual counter clamp.
- This change touches only the Desktop cloud pull, not Instagram actions, Chrome login, Supabase RLS policies, signed-in credentials, historical data or Android sync.

## Verification

- New `tests/cloud-review-pull-account-aba.test.cjs` executes the exact `pullProfileState` source with a paused remote response. It simulates A→B, A→B→A (generation changes), Supabase owner switch, then successful fresh B pull. Assert no stale writes or RAM changes and normal fresh state persistence.
- Wired the regression into generic Desktop CI and integrated Windows installer CI.
- Direct V8 source smoke: two stale responses rejected, no stale users applied, final fresh read persisted only the current scoped account's review keys. Existing cloud monotonic/rollback tests remain.
- **Still requires:** exact-head CI, then physical multi-account login and 30 verified Focus approvals/reload, including 918/484 historical context if applicable.

## Status

P0 #360 remains OPEN until the real affected account browser proves 30 new reviews persist without count bounce after refresh/restart, pending isolated from Reviewed, and A→B→A. Physical #371/#377/#164/#172 remain OPEN. Strict official score **6/12 (50%)**, public stable **v120.80**, **v120.81 held**, no real Instagram actions.
