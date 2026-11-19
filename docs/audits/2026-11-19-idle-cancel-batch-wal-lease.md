# GRANADA P0 — Idle batch cancellation after Windows restart

Date: 2026-11-19. Issue #164 / #377. Branch: `granada/idle-cancel-batch-lease-restart-20261119`.

## Root cause

The standard Windows `/api/actions/cancel-batch` path ran
`ActionRobot.cancel_current_batch`, which required a task owner already
bound to this specific Python process. A fresh Windows restart consequently
rejected an exact saved batch even with its correct owner/account/task/ID.

More importantly, the idle path directly called
`_archive_cancelled_batch_locked` while only holding `self.lock`. That
in-process lock **does not protect** the shared canonical JSON journal
against another Windows app (primary, secondary or Developer) performing an
action. The helper documentation itself required the OS action lease.
The dual-workspace manager already acquired a lease before calling this
method, but the public direct endpoint did not.

## Code-level correction

1. `cancel_saved_batch` now checks exact confirmation and obtains the
   same legacy GLOBAL + owner/account OS lease used by action clicks and
   Reviewed, before rereading or editing saved cohort state.
2. `_cancel_saved_batch_under_lease` contains the **only** idle mutation
   path and is callable internally only when the caller already holds the
   canonical lease. The dual-workspace controller uses this helper under
   its existing serial or explicitly consented parallel cohort lease,
   avoiding a nested deadlock with a running separate lane.
3. `cancel_current_batch` preserves active-worker behavior (signal STOP,
   never archive until its in-flight click has stopped) and routes a
   cold-start/idle exact saved batch through the lease-guarded path instead
   of refusing because the Python object has not been bound yet.
4. Saved uncertain clicks remain Review. Cancellation archives the
   *cohort*, not the click WAL, and never marks profiles Reviewed or OK.
   Wrong account/task/batch ID and occupied cross-process locks fail
   without any disk mutation or positive success message.

## Offline proof and acceptance gates

`tests/test_action_cancel_batch_admission.py` runs the actual
`ActionRobot` with synthetic two-account journals and a loopback HTTP
server. Scenarios: external public/secondary lease held, denied request
with byte-for-byte unchanged WAL/cohorts, cold-start cancel after lease
release, separate B account, wrong IDs, live worker stop without nested
lease and token-gated HTTP endpoint. It never opens Instagram or Chrome.

Run the repository's existing dual-worker, cancellation, batch history and
Windows CI suites on the exact branch head too. Real owner two-window GUI
and actual Instagram actions still require physical acceptance. Source
change alone is not a new release; stable remains v120.80.
