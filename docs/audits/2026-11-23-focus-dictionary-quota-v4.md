# GRANADA P0 #371 — Focus 30 lossless dictionary quota fallback

Date: 2026-11-23. Source branch `granada/focus-lossless-dictionary-quota-20261123`. Public stable remains v120.80.

## Root condition

Standalone HTML and the integrated Desktop companion share the same synchronous `saveActiveFocusBatch()`. The active, still-unconfirmed Focus 30 selection must be saved before opening tabs. The existing lossless v2 columnar and v3 URL/boolean-packed formats can both hit the browser's remaining localStorage quota when Review and history evidence legitimately occupy space. Previously, the third available choice was to pause Focus; deleting existing reviews would be unsafe.

## Functional source changes

- Introduce storageFormat **4**, a third *lossless* dictionary encoding of the existing v3 unconfirmed cohort. It stores repeated name, relationship and risk-level strings once and repeated risk-reason arrays once. Unique names, noncanonical URLs, null/empty/missing URL distinctions, all booleans, scores, times, row order and current batch identifiers remain intact. No cloud state, history or existing Reviewed/Pending/protected entry is touched.
- Execute only when **both** original v2 and fallback v3 `localStorage.setItem` calls fail with quota errors and the resulting v4 payload is smaller. v2/v3 success paths and legacy read support are preserved.
- Decode v4 through the existing v3 strict per-row validation. Reject invalid dictionary shapes/references rather than guess a username, relationship, decision or URL. Invalid saved entries are not deleted by the read path.
- The redacted storage diagnostic now identifies final failing format v4; no private handles, URLs, stored values or raw provider messages appear in its output. SecurityError is still a hard failure.
- Under actual insufficent quota, the old durable cohort remains intact and Focus still refuses to open or auto-confirm.

## Source validation

- Added `tests/focus-dictionary-quota-recovery.test.cjs` to run the real codec for **both** `index.html` and `desktop/ig_cleaner_pro_v120_27_synced_companion.html`: 30 identities, 789 historical Reviewed entries, pending/protected/history unchanged, v2/v3 quota rejection then v4 success, exactly reconstructed rows, A→B→A isolation, malformed dictionary fail-closed, SecurityError and too-small quota rollback.
- Adjusted the existing quota diagnostic test to expect v4 on final total-quota rejection; unchanged expectation v3 when v3 fits.
- Wired the test into generic CI and the integrated Windows gate, with explicit exit status on Windows.
- Direct pure-JavaScript smoke check against the **actual pushed codec** in both entrypoints returned identical results: v2 4,775 chars / v3 3,045 / v4 2,126, **30.18% below v3**; stored fallback was v4, exact JSON roundtrip true, next total-quota rejection retained prior bytes and the 10k-character Reviewed fixture.

## Acceptance boundaries

Source and synthetic tests are not evidence that the owner's original browser recovers. The underlying quota/error class and physical localStorage usage in that browser have not been observed. Keep issue #371 open until a real Focus 30 can start after safe migration/recovery with prior decisions intact. Keep #360, #377, #164 and #172 open and v120.81 on hold until the owner-facing P0 matrix completes. Overall milestone progress remains **6/12 (50%)**.
