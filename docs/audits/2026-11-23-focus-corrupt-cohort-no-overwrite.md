# GRANADA P0 — Unreadable Focus cohort preservation and explicit recovery

Date: 2026-11-23. Primary issue: #371 (storage failure), related #360 (counter rebounds).
After PR #402 (lossless v4 dictionary) merged as `5db379e9edc5913e6b34bc2a831027abd292aff1`.

## Confirmed source defect

Both HTML loaders previously used `try decode(JSON.parse(localStorage.getItem(...)||'null'))`, catching parse/codec errors and assigning `activeFocusBatch=null`. A later owner Focus attempt then treated the malformed *previously persisted and still unconfirmed* cohort as absent and could replace it. This silently destroyed the only saved selection/attempt evidence, while causing the owner to believe Focus had simply started a new batch.

The standalone HTML forced-clear function was already transactional, but the Desktop HTML cleared RAM **before** `localStorage.removeItem` and ignored the storage exception. Under denied removal, the UI misleadingly claimed cleanup while the corrupt cohort remained on disk and would reappear after refresh.

## Source remediation

1. Both `loadActiveFocusBatch` implementations distinguish a **genuinely missing storage key** from nonempty malformed JSON, unsupported codec payload or denied storage read. In the latter cases, they keep the original bytes untouched and set a per-page fail-closed `igcFocusUnreadableBatch` flag.
2. `saveActiveFocusBatch` and `clearActiveFocusBatch` refuse *any* implicit overwrite/removal while a prior cohort is unreadable. A future valid retry cannot conceal or supersede the unconfirmed previous cohort.
3. `forceClearStuckFocusBatch` is the only explicit destructive override. It requires a human confirmation explaining the loss of still-unconfirmed cohort data and recommends backup first, calls the storage removal, and **only after a successful deletion** clears memory/recovery guard and renders UI. Denied read/removal never changes the original saved entry or in-memory state. Saved Reviewed/Pending/protected/history keys are not touched.
4. A newly selected, independent Instagram account whose active-cohort key is genuinely absent is not blocked. Returning to the damaged account re-reads and retains its separate guard. Successfully decoded legacy v2/v3 and new v4 cohorts retain original functionality.
5. No Instagram relationship click, browser cookie, hosted sync, account migrations, release version or owner decisions are touched.

## Regression and direct source validation

- Added `tests/focus-corrupt-cohort-guard.test.cjs` over **both production HTML files**: invalid persisted JSON; blocked new Focus/write/clear; byte-for-byte evidence preservation; rejected vs consented forced delete; previous 789-review ledger, Pending, Protected and chronology preserved; A→B→A account separation; denied reads; valid cohort and missing-key recovery.
- Wired the regression in generic Desktop CI and integrated Windows Setup CI. A failing test blocks source integration.
- Executed both pushed HTML implementations directly with a synthetic corrupt cohort: `FocusRecoveryRequired` rejected an attempted overwrite, a denied storage delete returned false and preserved original data, a consented successful storage delete returned true and removed only the active cohort, and Reviewed/Pending fixtures remained unchanged.

## Acceptance boundary

This is code plus mocked/local source verification, **not** a physical repair of the owner's affected Chrome. #371 remains OPEN until the owner verifies opening a real 30-person batch without losing past 789/other Reviewed, Pending, protected and chronological states. #360 cross-tab counters and #377 two real Windows windows, #164/#172 Instagram robots also remain open. The official P0 metric remains **6/12 (50%)**. Last stable published release is v120.80 and v120.81 must not be published from source QA alone.
