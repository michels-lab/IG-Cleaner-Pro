# GRANADA 2026-11-19 — Consolidate safe Focus reopening and remove inactive timer launcher

## Root cause (#360, #371 / unresolved browser popup symptoms)

The app had **two** separate user-facing "Reopen" paths that both called `window.open()` on all rows with no per-profile exception handling. `reopenActiveFocusBatch()` attempted Chrome tabs before logging history and returned an exception if any one tab request failed; `reopenSafeFocusBatch()` called the Reviewed modal **after** all browser requests, so a denied popup could hide recovery. Both could reopen already Reviewed/protected/snoozed rows rather than only unresolved targets. The main HTML still also contained a deprecated, unreferenced `openFocusRows()` implementation using a `setTimeout(80)` popup loop and reporting "perfiles abiertos" as fact without reliable browser evidence. It had no call sites in the complete product HTML and was removed from the actual source.

## Product source correction

- Replace the two reopen flows with one `igcReopenSavedFocusBatch(batch)`, invoked by both `reopenActiveFocusBatch()` and `reopenSafeFocusBatch()`. It reads the saved active or owner review cohort, **filters out already-resolved rows** with the existing module-aware `activeBatchRowResolved` predicate (including Pending Double Check semantics), and leaves all confirmed Reviewed/Pending/protected data untouched.
- Display the *existing durable owner Reviewed panel with direct profile links* before asking Chrome to open any profile. If the dialog throws or fails to persist a restored cohort, stop without requesting any tabs. Never infer popup success/failure from `window.open` returning null with `noopener`.
- Catch exceptions on **each** `window.open` to continue requesting remaining eligible rows and show a visible count of rejected tab requests plus instructions to use direct links. Do not claim Instagram accounts were actually visited.
- Append `reopen` history only **after** requests; the history writer already rolls back RAM upon quota failure (#387). A failed secondary history or action audit warns without losing the saved active cohort or claiming Reviewed. Refresh counters with 'requested', not 'opened'.
- Delete the dead timer-based `openFocusRows()` from the real product source, instead of hiding it.

## Production-function negative tests

New CI-wired `tests/focus-reopen-recovery.test.cjs` extracts the real helper and both reopen entrypoints and simulates: broken Reviewed dialog, a failed modal save, all-resolved cohort, first popup throwing but two later tabs being requested, previously Reviewed target excluded, modal shown before all requests, opening history after requests, null `window.open` return, rejected history/audit writes (no destructive state) and successful safe-button path. Assert the legacy timer function is absent from source. No user Instagram sessions are accessed.

## Acceptance and release

Owner real browser popup and two separate Windows account windows still need physical acceptance. No remote Unfollow / Cancel Pending actions executed. Official stable release remains v120.80; next v120.81 is reserved but not authorized. The PR is **source only** until exact-head CI and a later explicitly authorized stable publication.
