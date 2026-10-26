# GRANADA — why a new Unfollow batch reopened already checked profiles

**Date:** 2026-10-26. **Observed by owner:** the published Windows robot actually unfollows, but beginning a NEW batch reopens some earlier inspected profiles. This is a reported physical-device symptom; no owner journal or Chrome session was remotely accessed.

## Root cause confirmed in source

The Windows `attempted_history` response deliberately excluded `_preclick_no_action` outcomes from `attempted_usernames` to allow explicit retries of safe no-click failures. The UI's new-batch chooser filtered only `attempted_usernames`, so a profile already opened and diagnosed without a click could enter the next cohort. The Windows `start` gate similarly tolerated these old outcomes when creating a fresh cohort. Source `inputs()` also draws on potentially stale imported Following/Pending snapshots: they are NOT proof a prior Instagram action failed.

## Functional fix in this branch

1. Server returns **`visited_usernames`**, the owner/account/task-scoped union of every durable action result (including confirmed, uncertain and safe no-click) and a new separate navigation write-ahead ledger. `attempted_usernames` remains unchanged for its original no-replay meaning. Historical data is never discarded.
2. Each action-target navigation is durably reserved **before `page.goto`**. This records only `target_navigation_reserved_not_action_confirmed`, NEVER falsely marking a relationship click or a completed review. On a crash, an opened-but-unrecorded target cannot appear as brand-new in another cohort. Malformed visit history blocks rather than resetting.
3. UI's fresh-cohort selector excludes **all visited profiles** after an authoritative Windows history request (missing visit list fails closed); rendering/cached counters distinguish already visited from merely clicked. The Windows worker independently rejects stale/falsely approved NEW Unfollow/Cancel lists containing earlier visits **before writing a batch or launching Chrome**. Continuing the exact original unfinished cohort may still revisit a demonstrably safe no-click result under the existing explicit owner approval; read-only historical recheck remains separate.
4. Owner/account/task hashes isolate records; prior protected lists, saved 10/40 cohorts, click WAL, timestamps and the released v120.64 installer are never rewritten. Actual Instagram action acceptance remains a physical owner test, not a CI claim.

**Regression coverage:** `tests/test_action_batch_history.py` covers confirmed, uncertain, safe no-click, cold-start, crash-reserved and corrupted journal exclusions. `tests/automations-next-batch.test.cjs` simulates a historical no-click profile that must be skipped before creating the next batch. New code does not ship in v120.64; a future official governed stable release is required after all gates.

**Next:** exact-head unit/Chrome/installed-Windows CI and Android/rendered regressions, then merge only if green. Do not publish a new release without normal FINAL Windows/Android signing, install, integrity, UI and feed validation. Real owner verification: finish 3–5 successful unfollows, close/reopen Windows, start a NEW batch, confirm none of those usernames or earlier inspected no-click profiles are reopened; confirm app does not infer a new completed relationship from merely visiting a URL.
