# GRANADA 24 — Never continue a ten-profile action wave after a possible click

Date: 2026-10-21. Windows Unfollow/Cancel P0; isolated from in-progress official v120.55 publisher, Desktop English PR #143, Android Developer and all user-account state.

## Finding and impact
The real Windows `ActionRobot._run` persists a fsynced `click_intent` before each potential Instagram relationship click. If the later DOM outcome returns `review` or another unresolved result, the worker typically stops the wave for manual review. However, an older exception for issue codes `missing_profile_info`, `profile_load_timeout`, `mutual_before_action`, `pending_already_following`, `pending_not_requested` permitted continuing with the NEXT target based solely on an issue *label*. It did not check whether the *current target* had already armed a possible-click write-ahead record.

This is a credible safety gap when Instagram changes its UI between control click and post-click check. Even though the uncertain target's own journal prevented a direct replay, the worker could still proceed to a second, unrelated relationship-changing action before manual review. This is a source-level finding; it is not evidence that it occurred in the owner's live Instagram.

A second gap: an existing saved `{"click_intent": null}` was indistinguishable from an absent field in `_invalid_saved_action_record`, despite the declared rule that malformed *present* click records fail closed.

## Scoped repair
- A familiar recoverable pre-click issue is eligible for automatic continuation **only when** the saved record is well formed and `click_intent` is entirely absent. Otherwise stop the current ten-target wave, preserve uncertain tab/journal and require read-only manual review; no new relationship action.
- Classify a *present but null* `click_intent` as invalid saved evidence. Snapshot shows an anonymized fixed review code; automatic cohort start fails before any Chrome click or new batch creation.
- Keep genuinely proven untouched or no-click profile failures resumable. Do not mark any unacted user Reviewed, do not archive the original 40-profile cohort, and do not reset protected accounts or action histories.
- Tests cover five familiar issue labels with/without durable intent, null intent and the **actual mocked ten-tab worker state machine**. Fake Chrome pages only; never connect to owner Instagram.

## Required validation and integration
- PR exact head: `python -m unittest discover -s tests -p 'test_action_click_wal.py' -v`, `test_action_batch_history.py`, full installed Windows public+Developer Setup + browser fixtures, general CI and rendered Desktop checks as invoked by existing workflows.
- No release request, app version, signer or actual Instagram account changes in this PR. The ongoing official v120.55 attempt #4 is pinned to its prior exact SHA; do not attribute this later source fix to that release unless another fully gated, published commit actually includes it.
- Keep live owner Unfollow/Cancel issue #172/#164 OPEN. If tests fail, diagnose and correct this source branch, never waive no-replay assertions.

