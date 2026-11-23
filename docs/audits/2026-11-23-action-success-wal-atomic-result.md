# GRANADA P0 — Exact current-batch click WAL required for any verified action OK

Date: 2026-11-23. Source follow-up after merged [PR #400](https://github.com/michels-lab/IG-Cleaner-Pro/pull/400). Issues #164 / #172. No credentials, private Instagram access, actions on owner's Instagram, or signed installer publication.

## Root cause

The Windows action worker previously accepted `perform_visible_action(...)` returning `("ok", details)` and persisted a green `ok` even if no matching `journal[username].click_intent` had been saved for the owner-approved batch. The actual visible flow is designed to invoke a durable `on_pre_click` callback, but the *outer worker's terminal success path* did not independently assert this invariant. Future transport changes, regressions, or unexpected return paths could therefore create a false verified success.

The terminal journal writer also assigned `journal[username]=...` in RAM *before* the final atomic fsync+rename, so a write rejection could leave a non-durable success in the worker snapshot.

## Source fix

1. For **Unfollow** and **Cancel Pending** only, reject `ok` unless current target has a matching `click_intent` with the exact active batch ID, task, valid phase and `relationship_control` in a valid phase trail; reject previously finalized intents. `already_not_following` and `already_not_requested` remain distinct, verified *no-click* states.
2. If the action transport reports an `ok` without such current durable WAL, record `review` with explicit code `success_without_current_click_intent` and text identifying the unknown outcome. Never claim green success, never automatically repeat a click, never proceed to a second target based on the unsupported result. This is not an assertion that Instagram did or did not process a click.
3. Publish the final outcome to RAM **only after** the entire revised journal is written, fsynced and renamed successfully. Retain original click intent on a disk error. Keep owner-account scope, protected list, previously persisted histories and existing user confirmations.

## Offline regression added (CI wired)

- Actual `ActionRobot._run()` in both Unfollow and Cancel modes, mocked visible action claims `ok` with no `on_pre_click`: first becomes Review, second target untouched, original queue not erased.
- Same worker with real `on_pre_click` persisted WAL: verified Cancel OK still succeeds.
- Exact task, batch and phase trail negative matrix rejects stale, malformed, finalized and missing records.
- Simulated disk failure during result finalization: prior WAL remains byte-for-byte on disk and unchanged in RAM; explicit retry can successfully commit without fabricating a previous OK.

No physical acceptance of Instagram, two Windows instances, Focus quota or 30 reviews is asserted. The P0 tracker remains 6/12 (50%) until owner-facing evidence satisfies a currently open milestone. Final v120.81 stays on release hold.

## Source QA gate

PR exact-head offline contract + Windows integrated installer + Desktop/Android / visual checks when emitted. Do not merge before relevant checks pass; do not publish stable release before physical requirements are satisfied.

## Additional same-run Chrome closure guard

- Even with a correctly armed current-batch WAL, a browser transport may report `ok` after the exact target tab has already closed (e.g., user closes Chrome during verification or a transport misreports a stale success). The worker now checks the live target page **again before final result commit**. A closed/uninspectable tab becomes a durable `review` with `target_tab_closed_before_success_commit`, and the existing click intent remains. It is never counted as verified OK or silently deferred as a harmless per-target warning.
- Real worker integration tests simulate both Unfollow and Cancel: durable click intent, externally closed target tab, stale `ok`, and a second selected user. Assert only the first was visited and no second mutation occurred.
