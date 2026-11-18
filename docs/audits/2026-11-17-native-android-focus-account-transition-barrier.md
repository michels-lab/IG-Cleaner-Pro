# P0 Granada: native Android Focus account-transition barrier (2026-11-17 Mexico)

## Source risk, not a claimed physical-data incident

Native Android uses one serialized IO executor for Focus and Supabase requests. The previous changeInstagramProfile task merely posted the actual Instagram-account switch to the UI handler. Once that post returned, the IO lane could start the next Focus task before the UI handler applied the switch to B. A task queued for A could therefore run after a delayed account switch.

Native Sign out previously invalidated login state directly on the UI thread, potentially during a Focus read/write. WorkspaceBridge.syncSession also rotated native session state outside the IO lane. These are **source-level races**, not evidence that an actual user's data crossed accounts or a live Instagram action ran.

## Source correction

- postAccountTransitionAndWait posts the account transition to UI and blocks only the IO worker with a CountDownLatch until the UI handoff completes. Failure to post/apply the transition is reported.
- Instagram profile switching, remembered-account selection and adding another account all use this ordering barrier.
- Sign out runs on IO, then resets the UI through the barrier. The owner reset increments workspaceSyncGeneration, invalidating old-owner Home replies; no owner backup is erased.
- WebView-to-native session adoption is serialized through IO.
- All six native Focus operation paths (loadBatches, createFocusBatch, createDoubleCheckBatch, loadBatch, openFocusProfile and finalizeBatch) capture owner email, Instagram account key and generation when queued. If any changes by execution time, the task fails closed. The IO lane and handoff barrier prevent a profile switch from interleaving an already-running Focus task.
- No new Instagram mutation APIs or destructive history clearing added.

## Acceptance and restrictions

tests/test_android_focus_account_transition.py verifies the source contracts, including the UI handoff barrier, scoped Focus entrypoints, A-B-A generation invalidation and serialized sign-out/session bridge. Passing the contract is not equivalent to a physical signed-in device test. Android compilation and installed UI CI must succeed before merge.

Real acceptance remains open for Focus A -> switch B -> switch A during operations, separate reviewed lists, sign-out during in-flight reads, and WebView session handoff. The source-only correction does not authorize v120.80; v120.79 remains the last official stable. Independent Pending issue PR #373 must be integrated safely.
