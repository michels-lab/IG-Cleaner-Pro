# GRANADA — Local Reviewed confirmation durability (2026-11-18)

## Observed code risk

`saveReviewedState()` wrote `LS_DONE` with `saveSet()`, immediately enqueuing a cloud sync, **before** writing `LS_REVIEW_META`. Under `QuotaExceededError` or `SecurityError` on the second write, a newly confirmed user could survive in the DONE key without matching relationship and time metadata. The caller would throw, but memory already contained the new decision; reload could show inconsistent Reviewed/Focus counts, and the enqueued cloud sync could publish a half-confirmation.

## Source correction

- Read the two previous durable values before writing.
- Persist `LS_DONE` then `LS_REVIEW_META`, deferring cloud synchronization until **both writes succeed**.
- If writing metadata fails, restore the previous DONE key; restore the canonical in-memory `doneSet` and `reviewedMeta` collections in place from the last persistent values; throw a visible error. Never classify an unsuccessfully saved review as confirmed.
- If storage blocks the rollback itself, report that explicitly and direct the user to export a backup; never delete old histories, attempt unfollow, or silently clear the account.
- New CI-wired test `tests/local-reviewed-atomic.test.cjs` forces quota rejection on the second of two writes, checks on-disk and in-memory rollback, ensures **zero cloud sync callbacks** after failure, then retries successfully and enqueues sync exactly once.

## Limitations

LocalStorage offers no true multi-key transaction, so rollback itself can still fail on a broken browser store. This fix is best-effort fail-closed, not a substitute for an IndexedDB transaction or an end-to-end account verification. Existing issue #371 near-quota Focus opens and #360 owner live count rebound still require physical browser testing. No stored user data is deleted by this change. No public release is authorized by this PR.
