# GRANADA — account chooser availability and owner-switch admission (2026-10-27)

## Reported behavior and actual evidence

- [Issue #264](https://github.com/michels-lab/IG-Cleaner-Pro/issues/264): exact merged SHA `2943e735` failed the first [Desktop Chromium run 40499536904](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40499536904) (`#igcLoginChooser` did not appear within 15 seconds). The second attempt on the SAME SHA passed; no app code change between attempts. This establishes an intermittent failure, not a proven single trigger.
- Code inspection establishes a **source-level vulnerability**: `igcSyncSwitchAccount()` returned early when `S.busy===true`, so a startup sync could prevent even the READ-ONLY chooser from opening. The original Chromium test unconditionally expected a modal immediately after a click without checking the sync/worker readiness. A busy race is a plausible cause, not proven to be what occurred in that first run.
- The safeguard against actual account changes while the worker is running or sync is active MUST remain intact. Pausing/cancelling a robot is not automated; sessions and protected lists are never rewritten by this fix.

## Actual source changes in a separate branch

1. The remembered-accounts chooser may open **read-only during a cloud sync**. The user sees a reason in the modal; no account is selected automatically.
2. Every individual `Switch` / `Add another account` click **rechecks** the current automation and sync guards before closing the chooser. A denied click leaves it open with an explanation, never changes authenticated owner, never schedules a hidden retry and never destroys reviews.
3. Read-only `igcSyncSwitchState()` exposes only a `ready` boolean and reason code (`ready`, `sync_busy`, `automation_active`, `android_account_screen`) to the offline browser fixture. No owner email, cookie, token, password or identity is returned.
4. Regression coverage includes read-only chooser during busy sync, zero account transitions under busy/active robot, owner preserved across a denied click, a later **new explicit click** after safe state, and saved local reviews. Rendered real Chromium waits for safe state before requesting the destructive owner-switch action and explicitly tests a late robot veto.

## Evidence gates and reentry

- Branch is **independent of the in-flight v120.68 publisher** ([run 40499536879](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40499536879)). No merge to `main`, no v120.68 tag/asset overwrite or new release while that publisher runs. Publishing v120.68 and this P1 improvement are separate operations.
- Exact PR-head Node VM, packaged standalone HTML in real Chromium, Desktop rendered UI, Windows installed app, Android isolated authentication/Developer and RLS checks must pass before merge. This file **does not** establish a physical owner Chrome login acceptance; #264 remains open until live confirmation.
- Next Granada should distinguish `source functional`, `CI verified`, `merged`, `published`, and `owner accepted`. Any CI or packaging failure stays BLOCKED; do not mask it with a timeout increase or deleting negative tests.
