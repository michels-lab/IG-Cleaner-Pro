# GRANADA 2026-11-18 — Focus near-quota durable fallback, no destructive cleanup

## Root cause and physical evidence

Owner issue [#371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371): Standalone HTML can display "Focus pausado · almacenamiento", open no profiles, and store no review decisions when near the localStorage quota. The previously shipped compact v2 active Focus batch still may not fit when existing preserved review history fills the quota. The existing code correctly fails closed but leaves an unusable Focus UI.

## Incremental implementation

In `desktop/ig_cleaner_pro_v120_27_synced_companion.html`:
- Preserve the normal, previously shipped v2 lossless serialization first.
- Only if `localStorage.setItem` fails with a quota-related exception, encode the same 30-person unconfirmed cohort with a **lossless v3 alternative**: represent canonical hrefs with a numeric sentinel, store four booleans in a 4-bit mask and retain all other row fields. An absent href, empty href and custom href have distinct representations. Do **not** rewrite confirmed Reviewed, Pending, protected or historical ledgers.
- Attempt the smaller v3 payload only when it is strictly smaller. The v3 read path decodes into the same `safeBatchRow` object shape and validates row lengths/flags; older v2 or plain-object cohorts remain readable.
- If both encodings fail, propagate the write error to the existing visible "Focus pausado" recovery panel. No browser tabs open and no phantom Reviewed status is recorded. SecurityError and malformed storage are not bypassed.

## Verification and scope

`tests/focus-quota-alternative.test.cjs`: near-quota storage with a 30-person cohort, 789-style prior histories simulated by retained large ledger keys, all row flags and dates round-trip, canonical/empty/absent/custom hrefs, quota-too-small preservation, SecurityError hard failure and malformed v3 refusal. Test wired into CI. The production codec was also evaluated directly: 4,091-character v2 -> 2,510-character v3 for 30 sample rows, 38.6% smaller and exact full-field round trip.

This is **not** a guarantee that a fully exhausted browser can open Focus, nor a complete automatic IndexedDB migration. If storage is too full for even v3, user data must remain preserved and the existing backup/retry UI stays necessary. Physical owner browsers, counters reappearing after async sync (#360), account A/B, real Instagram robot actions and physical app windows remain independent acceptance issues. Do not report them as solved.

## Release boundary

New source-only development branch `granada/focus-quota-fallback-20261118`; published stable `v120.80` remains immutable. Reserved `v120.81` is not authorized in the governed manifest. No Developer edition, RC or release from this patch without explicit governance and mandatory exact-source verification.
