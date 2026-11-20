# GRANADA P0 #371/#360 — Lossless Focus history compaction in BOTH HTML entrypoints

Date: 2026-11-20. Scope: source + offline regressions; latest public stable v120.80 unchanged.

## Root causes verified from source
1. **Standalone HTML was not equivalent to integrated Desktop.** `index.html` saved the full per-profile chronology with raw `JSON.stringify(profileHistory)` and swallowed parse errors by replacing memory with `{}`. The Desktop HTML already had a reversible v2 format and a fail-closed invalid-history flag, but standalone did not. Large repeated 25-event histories filled localStorage, preventing a 30-person Focus cohort from being saved even when its own v3 cohort was small.
2. **Existing v2 histories were never re-compacted.** Desktop's `loadProfileHistory()` tried lossless compression only for legacy plain JSON, excluding `__igcHistoryCompact:2` even if a smaller encoding became available.
3. **Standalone Focus opening-history writes were RAM-first with no rollback.** A quota denial after 30 attempted marks could display phantom opened counts, which later vanished or were written by another action.

These are verified source-path defects and probable contributors, not a claim that the owner's exact Chrome exception is identified.

## Product implementation
- A **v3 shared dictionary** deduplicates repeated `(event, details)` pairs across existing per-profile event arrays, while the exact timestamps, original event metadata, arbitrary custom row fields and unknown event shapes are round-tripped.
- `igcCompactHistoryText` chooses the **smallest** of original JSON, v2 and v3; it never expands the stored representation or deletes entries, and it retains v2 and raw readers.
- On load, a smaller v3 may replace legacy plain or v2 **in the same existing scoped localStorage key**, in one atomic `setItem` attempt. If quota/security refuses, original stored bytes stay unchanged; valid decoded data remains available. Unknown/unreadable formats fail closed instead of replacing historical data with empty objects.
- Standalone `index.html` gains this production codec and the same transactional `recordRowsHistory` open/reopen rollback already used by Desktop.
- No IndexedDB migration is claimed or initiated; Chrome cookies, action robot WAL, protected, Pending and confirmed Reviewed ledgers are untouched. Full quota still requires backup and physical diagnosis; no automatic deletion or success without persistent cohort.

## Mandatory regression
`tests/focus-history-v3-parity.test.cjs` invokes the **real functions** from BOTH source HTMLs in a browser-like Node VM:
- 789 users × 25 timestamped historical events, plus custom/legacy values, exact byte-semantics round-trip and measurable shrinkage versus v2/plain.
- Plain and existing v2 migration; refused migration must preserve previous bytes and RAM.
- 30 new Focus targets with insufficient quota: no phantom opening, exact rollback; then success and reload.
- A→B→A scoped ledger isolation; malformed v3 dictionary index must prevent all subsequent writes, then recover after restoring valid source.

Wired into existing `.github/workflows/ci.yml`. Additional UI, Windows packaging and Android checks remain separate gates.

## Honest acceptance boundary
Source and offline QA ≠ owner's real browser. Issue #371 remains OPEN until Focus 30 runs on the real account without deleting historical Reviews; #360 remains OPEN until count rebound has been physically excluded after refresh and A→B→A. #377 physical two-window, #164 Unfollow and #172 Cancel Pending remain open. The fixed v120.81 progress denominator stays **6/12 = 50%**; publish only after all applicable governance gates pass. No Developer edition, RC or preview release.
