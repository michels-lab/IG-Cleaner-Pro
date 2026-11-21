# GRANADA P0 #371 — standalone Focus full-quota recovery

## Reproduction and source gap

Owner's standalone browser HTML previously could fail the atomic Focus cohort save with `QuotaExceededError`. Source `index.html` returned `false` without displaying a recoverable retry button, while `desktop/ig_cleaner_pro_v120_27_synced_companion.html` already implemented an explicit, owner-triggered retry. The standalone Review UI also said “perfiles abiertos” though a `window.open` request with `noopener` cannot prove Chrome actually opened a tab.

## Source fix

- Add standalone modal `Reintentar guardar y abrir` (matching Desktop), **only visible after failed cohort persistence**.
- Disable Confirm, Reopen, Couldn't Review, Snooze and decision selector for an unsaved cohort. Show the precise redacted storage diagnostic and original 30 attempted handles as **“Sin abrir · guardado fallido”**, never as reviewed or confirmed opened.
- Retain failed attempt as **transient in-memory** rows, tied to the initiating Instagram slot and mode. A reload does not pretend this unsaved preview was durable.
- Retry only on a fresh explicit user click, reject when account/mode differs or another durable cohort is active. Reuse **the exact previously selected row list**; do not refill with ZIP candidates that may have changed between failure and retry. The existing `setActiveFocusBatch` remains the first durable transaction before any popup request.
- Align Review, activity log, and UI status with actual evidence: **tab requests**, not guaranteed visits. Chrome may block all requests; direct manual links remain visible.
- Preserve Reviewed/Pending/protected and chronological history exactly; no storage clear, no auto-confirming reviews, no Instagram clicks. The v3 compact cohort fallback and history migration stay unchanged.

## Test evidence

The already-wired `tests/focus-standalone-cohort-recovery.test.cjs` invokes the **actual** production codec, batch lifecycle and standalone button path under simulated near-quota/full-quota storage. Added DOM-state and acceptance assertions: failed save produces zero tab requests and disables review controls; original storage bytes stay unchanged; wrong account/mode cannot retry; an explicit retry must open exactly the original 30 requests, not refill from changed ZIP; confirm buttons reactivate only after durable save; diagnostics are redacted and open counts are described as requests. Existing both-entrypoint codec tests cover the 789 previous reviews and exact persistence.

## Remaining external verification

CI cannot prove an owner-signed-in Chrome session's popup permissions or local-storage quota. Keep #371, #360, #164, #172, #377 and v120.81 release held until physical acceptance; do not advance 6/12 milestone count solely because tests pass.
