# GRANADA — Recover last unchecked / Review action profiles and color outcomes (2026-10-26)

## Owner's real-device observation and desired behavior

Installed InstaCleaner Windows **v120.65** can actually Unfollow targets, but Chrome closed after the last target without visibly verifying it. The end-of-batch list needs a prominent **Open Review profiles** option; confirmed OK rows should be **green**, unresolved Review **yellow**, and a never-processed row **neutral grey**. A user should be able to approve a separate repeat Unfollow for a target still visibly followed **only if the durable journal proves no previous click**. Never silently start Instagram relationship-changing work from a read-only review.

## Root cause and previous gap

The old `igcAutoShowBatchReview` displayed all outcomes in identical rows with raw technical status text. `igcAutoOpenBatchIssues` opened selected exception URLs manually but did not launch a targeted automatic check of unresolved and untouched targets. `recheck_batch` walked every selected profile and refused useful read-only Following observations for an untouched or proven pre-click failed target. `start` already supported exact same-cohort recovery of proven no-click targets but did not support a named Review-only, separately authorized subset.

This is a **recovery workflow**, not proof of why the owner's Windows Chrome window closed. Actual browser lifecycle/owner Instagram DOM and live Unfollow must still be tested on installed v120.66 or later. Do not claim a simulated last-row fixture proves a live Instagram click occurred.

## Implementation

1. End-of-batch modal plus Batch results panel get **Open Review profiles · robot checks**. The robot reuses its verified local persistent Chrome profile, rechecks **only unresolved and untouched** targets in the exact saved unapproved cohort, and never clicks a relationship control during that first pass. Green `OK` denotes confirmed saved success or positively verified absence; yellow `Review` denotes unknown/failed status or pure read-only still-Following, grey `Not checked` denotes no result.
2. Read-only relationship observations distinguish `still_following`/`still_requested` from `observed_not_following`. They are stored only as `recheck_results` with `observation_only`, not as a forged original Unfollow/Cancel outcome or an automatic Reviewed decision.
3. A separate **Retry verified no-click profiles** button appears only when there is fresh read-only evidence (maximum 15 minutes) of `still_following` / `still_requested` and the original owner-scoped journal has **no possible click**. It shows the exact named targets and requires the owner's new confirmation. Backend independently checks saved cohort ID, owner, workspace, task, confirmation, current recent scan, protected status, and durable original action journal **before** opening a Chrome page. Worker receives only the eligible subset; original cohort remains intact.
4. A historical click intent, malformed record, ambiguous old error, wrong owner or stale/missing observation blocks the retry. No rechecking of a confirmed OK target from the new button. Keep the existing manual open and complete batch read-only recheck distinct.

## Regression gates

- `tests/test_action_batch_history.py::GranadaReviewRecoveryTests`: last untouched profile included in review scan; prior confirmed target excluded; uncertain click remains blocked even when current Following is observed; owner-approved retry acts only on selected zero-click names and preserves original saved cohort; stale or forged observations block new actions.
- `tests/automations-execution.test.cjs`: concrete modal green/yellow rows, Review button invokes only `recheck-batch` first, no `start` from read-only scan, separate approval constructs only the safe subset and excludes the uncertain target.
- Exact head integrated Windows installed source + offline browser, Android native/Developer builds and rendered Desktop/Android UI must all pass before merge/release.
- Physical owner Windows acceptance is **pending**: see whether end-of-batch final unchecked row is displayed, Review opens and checks it automatically, no extra confirmed profiles are opened, a no-click `Following` result can be explicitly approved once, and any prior possible click stays yellow/non-retryable.

## Data and release rules

Preserve `v120.65` current published FINAL and all immutable receipts, local Instagram Chrome profile/cookies, existing 10/40 cohorts, review and protected sets, account isolation, WAL/no-replay, original saved actions, snapshots, and source of truth. This feature branch changes only Windows action controller, Desktop embedded app, offline regressions and this audit. No owner Instagram navigation or click was initiated through ChatGPT. No unapproved prerelease, RC, no silent Android install.
