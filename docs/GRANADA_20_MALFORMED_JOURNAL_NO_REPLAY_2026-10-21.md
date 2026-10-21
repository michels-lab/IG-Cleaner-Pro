# GRANADA P0 — Legacy action journal uncertainty must never become a repeat click

Date: 2026-10-21. Scope: Windows action worker's **read-only snapshot**, cold-start attempted history and **before-start** safety gate. This is independent of existing Automation Center UI PR #184 and publisher PR #186.

## Defect and user consequence

The prior `ActionRobot.attempted_history` counted a present but malformed saved record (e.g. non-object JSON or an incomplete click intent) as reusable, effectively equating "unknown past action" with "provably untouched". The worker could create or try to continue an authorized cohort without first rejecting every malformed target. The status `snapshot` dereferenced click-intent fields as if they were always objects; malformed persisted records could produce an internal exception and hide Issues. This is particularly dangerous for Unfollow / Cancel Pending where **a click may be irreversible and must not be replayed automatically**.

## Implemented

1. **Fail-closed proof rule** `_invalid_saved_action_record`: any *present* journal entry with a non-object body, missing/unknown status or malformed/unknown durable-click phase is uncertain; presence is not zero-click evidence. Historical valid terminal records and documented **strict pre-click** failures remain unchanged.
2. **Cold-start / batch authorization**: unknown entries appear under `attempted_usernames` (not `reusable_usernames`), preventing browser-side stale cache from implicitly restarting them. `ActionRobot.start` checks the **full exact set of owner-approved targets before any new batch row, worker state change, Chrome tab or relationship click**; unknown evidence fails with a fixed error. No modification of original files.
3. **Readable owner status**: `snapshot` transforms invalid persisted entries in memory into `review / invalid_saved_action_evidence`, with a fixed instruction and no private raw click phase or unknown status injected into the owner-facing Issues. Original on-disk JSON stays byte-identical; no account merging.

## Regression matrix

Three new tests in `tests/test_action_click_wal.py` cover (a) multiple malformed/wrong-type records, historical cohorts and attempted-vs-reusable behavior; (b) no worker, no click, no mutation of saved journal or batch when selected malformed targets are submitted; (c) owner-facing status under malformed, unhashable or malicious nested metadata while preserving valid terminal and bona fide pre-click retry semantics. The Windows integrated preview and generic CI suites already run this test file through the governed workflow.

## Truthfulness and release status

This is a source-only improvement, **not** proof that any Instagram Unfollow or Cancel Pending succeeded in a real signed-in owner browser. The known v120.54 zero-confirmed Unfollow issue #172 and old 40-person cohort remain open; never purge historical protected users, approvals or uncertain WAL intents. Source tests/CI, merge, official definitive stable publication and live owner acceptance are distinct. GRANADA may publish a final stable release if every mandatory gate is satisfied; never issue a Release Candidate or bypass real installed Developer/Windows QA.

## Re-entry

Branch `granada/p0-malformed-journal-no-replay-20261021` — merge only after exact-head CI including simulated crash, persisted Windows batch history and rendered UI regressions. If blocked by another PR/claimed area, leave it isolated, move to next independent GRANADA block and retain this handoff.
