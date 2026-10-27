# GRANADA — unavailable Instagram profile is not an Unfollow robot error (2026-10-26)

## Real owner report
The owner supplied a signed-in Windows robot Chrome screenshot at `instagram.com/josefksayer/` showing exactly **«Esta página no está disponible»**. The installed Windows UI was stuck at `ROBOT · UNFOLLOW · REVIEW` with a request to manually inspect open Chrome tabs. The owner requests that a visibly unavailable profile not require per-target manual confirmation or stop a 40-profile cohort.

## Root cause
`_wait_for_target_profile_shell` waited for an exact target profile header or hero. Instagram's unavailable-page template lacks both, so the old code recorded a generic target heading/identity failure or timed out. The batch's issue counter and ten-tab review retention incorrectly treated that read-only outcome as a technical exception.

## New source behavior
- Classify **only a visible, exact Spanish/English Instagram page-unavailable banner** on the precise HTTPS target, confirmed in two reads, with no login/challenge and no valid displayed target header. Do not claim the user closed or deleted their Instagram; an incorrect username, rename, deactivation, block or temporary Instagram condition can also produce the banner.
- Return journal state `profile_unavailable` (no Unfollow/Cancel action), then save dated provenance and close its Chrome tab so sequential/ten-tab waves continue without human per-user Review. No Relationship-changing click, no success signal, and no confirmed cancellation.
- Keep separate *Unavailable* count, labelled muted-blue row in the end-of-batch modal; verified **OK remains green**, uncertain **Review yellow**, untouched grey. Unavailable is not a failure, not an issue, not an Unfollow success and not a verified Follow state.
- The exact saved-batch approval returns `unavailable_usernames` separately from genuinely `approved_usernames` and `unresolved_usernames`. It neither auto-promotes unavailable to user's Reviewed set nor requires manual issue review. A preserved prior possible-click/WAL never becomes a new confirmed success merely because a read-only scan saw unavailable.
- Original visit ledger, no-replay action WAL, saved owner/account scopes, protections, no-change historical audits, app records, Android clients and other automation tasks remain unchanged.

## Negative offline regression
`test_action_batch_history.py::InstagramUnavailableProfileTests`: exact Spanish and English phrases; wrong URL, hidden banner, challenge, loaded hero, blinking transient message false positives; first-pass action no click, targeted read-only recovery no click; close unavailable tab; real scoped snapshot reports distinct count and zero false Unfollow; batch approval retains original uncertain click as unresolved.

`tests/automations-execution.test.cjs`: verified OK green, unavailable a separate muted-blue no-action row, ambiguous click yellow, modal counts and approval not blocked by the unavailable profile.

## Acceptance
Actual owner-installed v120.66 cannot contain this source change. The next version must pass exact-head integrated Windows public/Developer installer, offline Chrome browser, Android, rendered UI, signed release and update-feed gates before **one official FINAL stable release**. Owner live Windows confirmation remains PENDING; do not claim real Instagram account deletion detection.
