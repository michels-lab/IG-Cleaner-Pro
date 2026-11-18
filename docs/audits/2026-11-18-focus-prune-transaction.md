# GRANADA — Focus recovered-cohort pruning must be durable
Date: 2026-11-18. Owner symptom: Focus counts can rebound after reload when storage writes fail.

## Confirmed source bug
`pruneResolvedActiveFocusBatch()` previously applied `activeFocusBatch.rows=filtered` **before** `saveActiveFocusBatch()`. If the browser storage operation rejected the update (e.g. quota/security), the UI could keep a shortened transient cohort although the older full cohort remained on disk. If every row was resolved, the function also cleared in-memory state before trying the persisted delete and swallowed that delete error. A subsequent reload could therefore restore the old rows, seemingly "bringing back" profiles.

## Fix
- `clearActiveFocusBatch()` also used to clear RAM before a failed durable remove, and then redundantly attempted the delete a second time. It now performs exactly one persistent deletion first and preserves the original RAM state if the delete fails.
- Filter into a candidate array, without changing the original cohort.
- If rows remain, save the new immutable candidate first; on failure restore the original active and review references and return false.
- If no rows remain, perform the persistent deletion before clearing memory. If delete throws, leave both references unchanged and return false.
- Leave previously reviewed, protected, Pending and historical ledgers untouched; no Instagram actions or browser visits.
- Source regressions added to the existing CI-wired `tests/focus-quota-alternative.test.cjs`, with rejected writes, denied removals, successful partial prune and complete prune, plus failure/success paths for explicit batch clearing.

## Limitations
This eliminates an in-memory/durable divergence in *recovered-cohort pruning*. It does not alone fix every possible Focus counter rebound; asynchronous imported-list or cloud updates (issue #360), entirely exhausted browser quotas (#371) and account A/B live acceptance remain open. No real Instagram session is part of the test. Published v120.80 remains immutable; v120.81 is not authorized.
