# GRANADA 2026-11-18 — Pending Focus two-ledger commit and Double Check recovery

## Actual source failures (#360/#371)

1. **Normal Pending Focus:** `openConfirmedFocusRows` wrote a durable active cohort, then called `pendingOpenedSet.add` for every target and separately `savePendingOpened()`. If that *second* write failed, the JavaScript caller threw **before showing Reviewed or opening any tabs**, yet RAM still counted the profiles as opened and `setActiveFocusBatch` had already saved their `open` history. A browser reload could restore a different count. No other profile should be automatically marked reviewed, and existing Pending history must survive.
2. **Pending Double Check:** `igcPendingDoubleStart` saved the active cohort first **without** `reviewMode='double'`, then modified RAM and attempted a second save to persist that flag. A denied second write left a first-pass Pending cohort on disk, dangerous when earlier reviews should remain unrelated to a second round. An exception in `igcPendingDoubleSaveSeen` also lost the review panel, and a thrown `window.open` aborted remaining requests after marking targets seen.

## Source corrections

- `setActiveFocusBatch` accepts an optional `reviewMode` and optional `deferHistory`. With Double Check, the **first and only active-cohort write** includes `reviewMode='double'`. Existing call sites preserve original defaults.
- Normal Pending Focus snapshots its existing opened-set reference, writes all opened marks durably and **reverts RAM in place** on failure; no tabs or opening-history entries are requested. The already durable active cohort remains recoverable, and a visible Reviewed recovery dialog + warning explains the partial storage failure. No destructive rollback of earlier decisions or histories.
- Both normal Focus and Pending Double Check defer the `open` history event until **after** all required primary ledgers have committed and the browser tab requests have been attempted; secondary history failure becomes a visible warning while the durable active cohort remains intact.
- Pending Double Check prepares a separate next-cycle set, persists it before changing selection, and catches write failures. The persisted recoverable cohort retains double mode; no browser tabs open on failure. The review modal appears **before** profile tab requests. A thrown popup is isolated per target, so remaining requests are still attempted. `window.open` returning null (normal with noopener) is not treated as evidence of success/failure.
- No extra Developer/RC edition or changes to automation mutating robots, accounts, Reviewed/Pending decisions or original WAL journals.

## CI-wired regressions

- `tests/focus-confirmation-storage-popup-regression.test.cjs` now injects a successful active-cohort write followed by rejected Pending opened ledger; verifies no `window.open`, no opening history, exact original RAM Set identity/values, retained recoverable cohort, visible explanation, and success after explicit cancellation/retry.
- `tests/pending-double-check.test.cjs` executes the actual production Double Check start code with a mock first-write that includes double-mode metadata. It verifies a rejected independent cycle ledger cannot open tabs or change old reviews; first saved cohort is double-mode and needs only one write. A broken modal blocks tabs while retaining recoverable cohort. One popup exception cannot prevent other requested tabs.

## Release / physical owner boundaries

Require all **7 exact-head** GitHub CI workflows and production-source manual review before merge. Browser quota can still exhaust even compact v3; per-profile direct links and real Chrome popup behavior need physical user validation. #360/#371/#377 stay open. Official stable **v120.80** unchanged, next **v120.81** not authorized without release request.
