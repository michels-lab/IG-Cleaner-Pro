# Operación Granada #32 — normal Windows robot: multi-tab login handoff

Date: 2026-10-22. Product: InstaCleaner public Windows robot only.

## Reproducible source issue
The standard `ActionRobot._run()` launcher may reuse an Instagram Login page from persistent Chrome, then poll **only that original Page object** for the logged-in owner. When a human signs into Instagram in a new browser tab, the original tab can remain on `/accounts/login/`, so `signed_in_handle(page)` never changes. #210 correctly added a 240-second timeout but did not detect the authenticated tab; the app appeared inert and then reported an avoidable login timeout.

## Public-app fix
- `_find_verified_owner_tab` scans **only visible/open HTTPS Instagram pages from the same persistent robot Chrome context** with existing `signed_in_handle` proof (navigation, switcher, or own-header Edit profile). It does not read browser cookies, export a session or trust a URL by itself. No outside tabs or HTTP profiles are accepted.
- If exactly the selected owner is provable, select that tab as the subsequent action page. If **any** tab proves a different Instagram owner, fail closed instead of choosing arbitrarily. A stale Login page does not count as evidence of mismatch or owner.
- Existing no-CAPTCHA, authorization, cohort/protected accounts, write-ahead action-intent, manual owner approval, ten-tab waves and 240-second timeout remain in place. No new Instagram API mutation, no Developer functionality.
- Offline regression fixtures cover Instagram login tab + new signed-in tab, off-origin/insecure/closed tabs ignored, same-owner casefold, conflicting identity blocks, and no unintended navigations/clicks. Existing public robot tests for timeout and wrong account set explicit HTTPS Instagram URLs.

## Validation and status
Source tests and installed-Windows workflow must pass for exact PR head before merge. After merging, **real live Instagram Unfollow and Cancel Pending remain unverified**, requiring owner to open the official Windows app in their own authenticated Chrome. Keep P0 #172/#164 open and preserve old 40/10 saved batches. v120.55 is still official until an authorized governed **FINAL stable** v120.56 publisher completes, without RC.
