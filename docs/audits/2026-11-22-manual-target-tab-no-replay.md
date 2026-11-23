# GRANADA P0 — Closed Chrome target tab must not reopen or become OK

Date: 2026-11-22. Source-only candidate for #164 and #172. No real Instagram credentials, login, account action or Windows installer execution.

## Reproduced logic gap in main before change

`ActionTabPool._prune_manually_closed()` previously dropped a target whose Chrome page had been closed outside the robot. After that, `prepared(user)` returned no page and `stage_next_wave()` could allocate a **new** tab for the *same* authorized username within the same saved batch. Losing a tab is not evidence of a verified relationship outcome. New-cohort visit guards were not a substitute for protecting an exact in-progress batch.

## Source changes proposed

1. Record an unresolved closed-tab tombstone in `ActionTabPool`, separate from normal verified robot closes. Deny further `open(username)` for that exact target within the job even if another tab slot becomes free; retain other open tabs and their truthful states.
2. Before preparing either a sequential or ten-tab wave, and before advancing to another target, check unresolved closures; stop the job in **Review**, never silently recycle or re-click. Do not classify a browser transport exception as a confirmed closed tab.
3. For Unfollow/Cancel only, if there is **no existing possible-click evidence**, persist a conservative `review` record in the original account-scoped journal with no new `click_intent`. Preserve any original proven pre-click history as `attempt_history`; fail the next stage on disk inconsistency. Saved review blocks automatic repeat across restart. If a WAL or ambiguous prior result already exists, preserve it byte-for-byte without inventing a no-click result.
4. Treat this as *unverified target navigation*, not a successful Unfollow/Cancel or a completed review. Existing protected targets, action leases, pacing, prior results and sibling account journals remain unchanged.

## Regression

Ten new offline cases are in the existing CI-wired `tests/test_action_tab_waves.py`: sequential and ten-tab closures, proper robot-confirmed closure, durable Review/no-replay, earlier pre-click evidence retained, no overwrite of WAL/invalid evidence, reload and account A/B isolation, transport error retaining tab, final-prefetch cleanup and worker-stage wiring.

Local tests cannot establish successful Instagram actions, physical Windows window behavior, or installer quality. Keep #164/#172 and physical acceptance OPEN. Latest official stable is v120.80. Do not publish v120.81 until the fixed 12-hit criteria are met.

## Gate before merge

Exact PR-head Python regression + relevant robot test groups; Windows installed QA if CI provides it. Review CI failures, check the tested SHA and merge only when tests are passing. The 50% (6/12) tracker does NOT increase for source-only improvement to the still-open real-robot acceptance milestone.
