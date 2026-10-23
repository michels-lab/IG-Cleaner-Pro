# Operación Granada #36 — normal Windows action worker: journal quarantine at admission

Date: 2026-10-23. Scope: **normal InstaCleaner Windows robot**, Unfollow / Cancel Pending (existing source, no Developer changes).

## Root-cause inspection
`start()` validates malformed target journal entries at batch approval. Later, after potentially lengthy manual Instagram sign-in, `ActionRobot._run` loads the journal again but its ten-tab prefetch and subsequent target loop used `previous.get("status") in known terminal states` as the only saved-history guard. A *present* empty/statusless/foreign JSON record could slip through as apparently untouched; a non-dict value could raise a confusing exception. This violated the stricter previously established no-replay policy even though a normal start typically rejects malformed records. The post-login interval and worker paths require an independent fail-closed barrier.

## Change
- Introduced one authoritative `_saved_journal_blocks_action(journal, username)`: absent target record is eligible; an existing record is eligible **only** if `_preclick_no_action` independently proves a safe, pre-click failure. Success, uncertain-click, malformed, empty and unrecognized records are **not** automatically eligible.
- After manual owner login, but **before the first target tab opens**, the worker verifies that all selected saved records are valid. Invalid evidence blocks the task with an explicit, non-destructive diagnostic; there is no Instagram click and no journal rewrite.
- Both complete ten-tab staging and the sequential execution loop use the same guard. The final durable write-ahead barrier independently rejects malformed existing evidence immediately before any relationship click.
- Existing saved cohorts, original 40-person batch, protected account list, session and WAL history are unchanged. No read-only check is misrepresented as a successful mutation.

## Independent test requirements
`tests/test_action_worker_journal_gate.py` runs fake Chrome against the **real** `ActionRobot._run` entrypoint: invalid records injected before worker admission must result in `blocked`, zero created profile tabs, zero action calls and byte-identical saved journals. Pure helper tests distinguish absent entries, known safe pre-click misses, malformed records and completed/uncertain histories. Simulate write-ahead rejection on malformed records. Wire this suite into Profile Counts CI, integrated Windows Setup CI and final stable publisher Windows gate.

These tests do not contact Instagram and cannot replace owner's acceptance of actual Unfollow / Cancel Pending in the installed normal Windows app. **Latest published stable stays v120.56** until a separately validated FINAL-only release. No RC, Developer Edition investment or modifications to other products.
