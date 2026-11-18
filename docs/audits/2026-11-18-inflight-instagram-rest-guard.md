# GRANADA 2026-11-18 — In-flight Instagram workspace guard for every cloud REST call

## Confirmed root cause

The shared Desktop/Android HTML Supabase `rest(path,opt)` bridge captured the signed-in application owner before a request, but **not** the active Instagram workspace. `IGC_INSTAGRAM_PROFILES.scopeRest()` chose a per-profile endpoint at request construction time; a delayed result from account A could arrive after the user switched to B. The existing post-response guard only compared `sessionOwner(S.session)`, so both workspaces under the same application owner passed the check.

This could affect list-snapshot pulls, cloud histories, cross-device Reviewed/Pending counts, and other scoped work even where the newer profile-history reader has its own scope guard.

## Source change

- Capture the authenticated owner, active Instagram workspace and a monotonic per-page switch generation immediately after `ensureAuth()` and before `scopeRest()`. The generation increments in the real Instagram selector and rejects A→B→A even when the current key returns to its original value.
- Check both at REST execution and immediately after awaiting the HTTP result.
- On an authorization error, reject a changed scope **before** any token refresh or retry. Retry is allowed only for the same original owner and Instagram workspace.
- Scope checks fail closed; they do not rewrite profile lists, transfer cookies, touch stored Reviewed/Pending, or schedule Instagram actions.
- The existing `tests/auth-session-refresh.test.cjs` CI suite gained a delayed A→B HTTP test that rejects A data and admits a fresh B request, an A→B→A generation race, plus a 401 error after switching that must not refresh/replay under B. The 918/484 Focus A→B→A regression asserts the production switch generation advances through all four switches.

## Acceptance boundary

CI verifies the production REST bridge offline, including account-scope races. It does not certify live simultaneous Instagram sessions or complete issue #360 behavior. Standalone HTML, installed Windows and Android still require exact-head tests and owner physical verification. Stable v120.80 remains immutable; v120.81 remains reserved but not authorized.
