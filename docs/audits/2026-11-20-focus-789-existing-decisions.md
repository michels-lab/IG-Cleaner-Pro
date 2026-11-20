# InstaCleaner P0 #360/#371 — real-volume Focus confirmation regression (2026-11-20)

## Detection gap
The previous Focus bulk confirmation test named 789 prior Reviewed accounts in its explanation but actually initialized only a single prior review. Its quota / second-key rollback and A→B→A checks were valuable but did not establish that a large history survives the same transaction and simulated reload.

## Scope of this continued engineering block
- Seed **789 distinct, previously confirmed Reviewed accounts** with original `reviewedAt` timestamps and matching Done ledger; add **30 distinct new** Focus targets.
- Inject rejection on the second persisted key. Require no changes to original serialized bytes, RAM counters, modal visibility or cloud sync queue.
- Retry exactly the original 30. Require **819** persisted Reviewed metadata and Done entries, and preserved historical timestamps and membership for all 789.
- Reconstruct state from saved bytes (refresh simulation), then switch A→B→A and verify the A ledger remains 819 while B has its own independent decision.
- Retain third-key protected failure, Pending Double Check historical decisions and denied storage read coverage.
- Test invokes the real `igcCommitFocusDecision` production function extracted from **both** the standalone and desktop HTML entrypoints. No copied implementation, no Instagram credentials or live relationship-changing actions.

## Acceptance boundary
This is stronger **offline regression coverage**, not a new app-side storage migration or real-browser acceptance. It does not mean the owner's quota is large enough, that Focus requested/opened 30 Chrome tabs, or that Android/Windows live A/B sync works. Issue #371 (real browser quota) and #360 (real counters) stay open; #377 Windows physical windows and #164/#172 live robot actions remain open. The currently published stable is **v120.80**; **v120.81** stays on hold with no publication authorized by plain "continue".

Progress on the fixed 12-hito roadmap stays **6/12 = 50%**; this test strengthens evidence for an already-counted CI milestone and cannot be counted as one of six physical/release gates.
