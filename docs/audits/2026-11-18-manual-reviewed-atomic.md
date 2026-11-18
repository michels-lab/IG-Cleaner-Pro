# 2026-11-18 GRANADA — Manual Reviewed confirmation durability

## Verified source hazard

The user reported that Reviewed/Focus counters decrease, then rebound after reloading. Even after the cloud pull transaction fix in PR #381 and recovered cohort fix #380, every *local manual confirmation* in the source still called `saveReviewedState()` only **after** mutating `doneSet` and `reviewedMeta`. That helper wrote `LS_DONE` and `LS_REVIEW_META` in separate writes. A quota failure on the second key left a partial disk snapshot and an inflated on-screen Reviewed state. The confirmation dialog could remain open but the RAM state was already changed, while other call sites could proceed to increment success counters.

## Actual source changes

- `saveReviewedState(mutate)` now obtains the exact previous contents of both scoped localStorage keys and snapshots the live canonical set/metadata object before running any change.
- The mutation runs within the transaction; metadata and Reviewed set are saved durably before a cloud sync callback is queued.
- On failure, the code restores any key already written, reverts the live set and metadata **in place** (not reassigning their references), tells the user that the save failed, and returns false. If disk rollback itself fails, it warns specifically that backup recovery is needed.
- All six existing Review confirmation paths now use this transactional helper: the opened-batch popup, undo, individual checkbox, manual selection, manual unmark, and post-server automation approval. On failure they do not advance session stats, success journal, popup dismissal, or reported successful batch approval.
- Automation's server-authoritative action history is never reset or replayed; if local persistence is unavailable the approval confirmation UI remains and the user is notified.

## CI regression

`tests/manual-reviewed-atomic-storage.test.cjs`, wired into the general Desktop CI, exercises the real production helper and popup with a 30-person simulated cohort, a forced quota exception on the second write, a successful retry, canonical reference preservation, zero false successes, and read-denied storage refusal.

## Acceptance boundary

This fixes a concrete local multi-key atomicity issue, not a promise that all #360 or #371 storage and cross-device races have been eliminated. The regression uses synthetic accounts only. Physical Instagram owner verification remains open. Official stable stays v120.80 until separate release authorization; no actual user history/credentials/files were deleted.
