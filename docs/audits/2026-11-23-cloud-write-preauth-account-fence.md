# GRANADA 2026-11-23 — Cloud writes pre-auth A→B→A and multi-stage pipeline fence

## Root cause: confirmed in real Desktop source
The canonical Desktop `rest(path,opt)` captured Instagram account + generation **after** `await ensureAuth()`. If a token refresh yielded while the user switched A→B (or A→B→A), the pending A payload could be scoped by `scopeRest` to the current B instead, despite the later post-request guard. Previously merged #404 correctly rejected late *pull responses*, but not this earlier write-side capture gap.

A second source gap existed in multi-stage `syncNow`, `pushEvents`, `pushListSnapshots` and `pushPreparedBatches`: checking identity inside each individual REST request does not prevent A data from entering a B request launched after an intermediate `await`, nor prevent cloud A snapshot metadata from being applied to B's local account.

## Functional changes
1. `igcCaptureSyncScope()` captures signed-in user, selected Instagram account and monotonically changing account generation at function entry. `rest()` now captures **before** awaiting auth refresh; checks again immediately before choosing its scoped REST table and throughout HTTP/retry. No requests or local mutations are allowed after a context change.
2. Full `syncNow` validates one immutable owner/account/generation after **each** await. Cross-scope data cannot produce false `Sync completo` or new local `lastSync`; releases busy lock with visible error.
3. Multi-chunk writes recheck between chunks: `pushEvents` and `pushPreparedBatches` refuse to upload the next stale page. `pushListSnapshots` checks after remote GET and POST and before persisting list metadata.

## New CI regression
- `tests/cloud-write-preauth-aba.test.cjs` loads actual unmodified production function bodies from the **updated HTML** into Node VM, using deferred mock network/auth. Exercises owner change, A→B→A during pending refresh, unchanged-scope token rotation, 501 audit events, 550 Focus batch targets, list metadata, and aborted full synchronization.
- Wired into Desktop source CI `.github/workflows/ci.yml`. No private Instagram ZIP, cookies, Supabase connection or automated relationship clicks. This test is different from browser UI/installed Windows and physical owner acceptance.

## Explicit limitations
This source block targets the canonical **Desktop/Windows HTML sync runtime**. The separate Android embedded HTML has a different legacy transport implementation, and is not claimed to inherit this change. A call already committed before the scope changes cannot be reversed; guarantees apply to any **subsequent** requests and local writes, with fail-closed diagnostics. Source CI and owner physical QA are distinct.

Physical blockers #360/#371/#377/#164/#172 remain, and final v120.81 is on release hold. Fixed P0 milestone score stays **6/12 = 50%**; public stable v120.80. Independently modified branch avoids file collision with native Windows History PR #405.
