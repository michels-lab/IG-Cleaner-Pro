# GRANADA #41 — Normal Windows robot disk-journal drift gate

Date: 2026-10-23. Scope: **only InstaCleaner normal Windows action worker** (Unfollow and Cancel Pending). This code path does not access Michel's Life, FoamLens, LouderMe or OpenFOAM.

## Code-level failure mode

The worker reads the account/task-scoped action journal once after manual Instagram login. The existing cross-process lease prevents two cooperating InstaCleaner action workers from acting in the same saved folder, but does not prevent external file edits, restores or noncooperating writers. A stale in-memory journal could overwrite a newer completed result or an uncertain click intent during the next write-ahead phase or final result save. **This is a source-level prevention finding, not a claim that it occurred in the owner's account.**

## Intervention

1. Read the authoritative saved journal immediately before each relationship-click phase; fail closed on malformed JSON or any divergence from the worker snapshot. Never silently reset or merge unknown evidence.
2. Repeat the same check before writing a final result, including after a possible relationship click. If external evidence changed, preserve it instead of announcing false success.
3. Regression checks cover completed results, uncertain click intent, unrelated newer target records, corrupt JSON, intermediate confirmation phases, original-file byte preservation and the final-save integration location. No live Instagram target is contacted.

This is a **best-effort noncooperating-writer drift guard**, not a fully atomic cross-process compare-and-swap. The existing InstaCleaner OS worker lease remains the app's concurrency primitive. Real owner's saved original 40-profile cohort, protected targets, state schema, signed sessions and click histories are not altered by source/tests.

## Gates and limitations

Exact-head Python/Chromium, Profile Counts and integrated Windows installer CI must pass before merging. Code and offline tests cannot establish that the owner's actual Unfollow/Cancel Pending now works; issues #172 and #164 stay open. Do not publish a final stable solely because these offline tests pass: preserve mandatory Android production signer/device, Windows installed/Developer, screenshots, SHA-256 and artifact gates. No RC or prerelease.
