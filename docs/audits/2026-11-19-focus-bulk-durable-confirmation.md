# GRANADA #360 / #371 — Focus bulk review crash/storage consistency
Date: 2026-11-19. Source-only; no public release authorization.

## Root cause found

Two shipped HTML entrypoints (`index.html` and `desktop/ig_cleaner_pro_v120_27_synced_companion.html`) contained multiple independent bulk review handlers. `confirmSafeFocusReviewed` and the older `confirmExtraFocusReviewed` mutated `doneSet`, `reviewedMeta`, Pending metadata and the opened ledger **before** writing them to separate localStorage keys. A quota/security exception on any later write meant a partially saved decision, a stale counter/Review UI, or a closed modal with lost context. Separately, the older `markExtraFocusNotReviewed` and `index.html`'s `markSafeFocusNotReviewed` **deleted already confirmed reviews** when a new Recheck/Double Check attempt could not be opened.

## Change

- Both entrypoints now use `igcCommitFocusDecision` for the primary confirmation: prepare immutable next snapshots, read exact account-local backups, commit all necessary keys, restore already-written keys in reverse order if a write fails, and publish in-memory state only if the complete transaction succeeds. No optimistic counter changes or success screen on failed write.
- Pending Double Check archives the previous decision and retains its Reviewed/Open ledger; every current confirmation, including the legacy extra modal, uses this same entrypoint.
- Main/Followers/Mutuals commit Reviewed metadata and Done ledger together. Mutuals/Followers add protected profiles in the same transaction for keep decisions.
- `igcCommitFocusUnconfirmed` and both *Couldn't review yet* handlers no longer delete earlier confirmed Reviewed, Pending or protected decisions. They release only previously unreviewed Pending opened attempts.
- Chronological open/review history remains a separate supplemental ledger. A history quota warning is reported rather than pretending that the primary Reviewed/Pending decision failed.
- Saved focus cohort is cleared only after the authoritative ledger transaction. If cohort deletion is rejected, the UI is not closed or given a fake successful end-of-batch.
- Single queue-sync hook fires **after** the complete transaction, not halfway between two writes. No Google/Instagram session or credentials are read.

## Offline verification

`tests/focus-bulk-durable-confirmation.test.cjs` runs the real production functions in a browser-like VM on both entrypoints, with 30-person batch, 789-existing-review-compatible state, simulated quota failure on 2nd and 3rd storage keys, protected decisions, A→B→A account scopes, pending second-review archival, rejected reads and legacy unconfirmed modal delegation. An occupied / full storage path must retain the exact old bytes and modal without false count changes.

Follow-up remains **physical browser and actual Instagram owner QA** for issue #360, #371 and #377; no CI claim is live Instagram acceptance. Stable stays v120.80 and release_hold stays true.
