# GRANADA 2026-11-18 — Exact failed Focus write diagnostics (#371)

## Root cause of missing evidence

When browser `localStorage` rejected an active Focus cohort, the app correctly prevented opening Instagram profiles or claiming Reviewed. However the old `igcFocusStorageDiagnostic` always measured the original v2 encoding, even if `saveActiveFocusBatch()` had actually retried and failed with a smaller, lossless v3 payload. It did not name the rejected storage key or distinguish SecurityError from the second quota attempt. The owner therefore could not tell which write failed. The sample failure's actual quota and physical browser exception remain unknown; this change does not claim to remove all quota pressure.

## Production correction

- Save only the attempted fixed `LS_ACTIVE_FOCUS_BATCH` key, `v2`/`v3` encoding and exact UTF-16 estimated bytes in volatile `window.igcFocusWriteAttempt` before each `localStorage.setItem`. Never persist the diagnostic and never include usernames, URLs, raw storage values, cookies or exception message.
- Failed normal v2 + failed compact v3 correctly reports **v3's attempted bytes**, not the prior v2 estimate. SecurityError reports v2 with no quota bypass.
- `igcFocusStorageDiagnostic` preserves existing legacy text contract, adds key/format/attempt size, and estimates full localStorage usage only when permitted. In blocked storage it fails closed to 'unknown' values. Keep the storage warning, recoverable active batch and all Reviewed/Pending/history intact. A successful retry clears transient stale storage warnings.
- CI-wired **real production function** regression extends `tests/focus-quota-alternative.test.cjs` to assert v3 final failed write, v2 SecurityError, privacy redaction, durable cohort survival and success resets. Existing `tests/focus-storage-diagnostic.test.cjs` enforces legacy report text and privacy boundaries.

## Evidence and limits

No owner Instagram account, cookie or local browser data were accessed. Test mocks cannot prove real Chrome quota or a 30-person Focus launch. Source change is diagnostic/retry-state correctness, **not a complete quota cure** or an IndexedDB migration. #371 remains OPEN until real owner browser corroborates that Focus opens and reviews survive restart. #360 counters, #377 physical two-window, live Unfollow/Cancel and Android cross-device checks remain separate.

Published official stable **v120.80** unchanged. v120.81 reserved without release authorization. This PR is source only, not a release, RC or Developer build.
