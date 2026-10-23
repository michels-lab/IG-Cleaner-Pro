# Operación Granada #31 — Public InstaCleaner only: stop Developer investment

Date: 2026-10-22. Product: IG Cleaner Pro. Direction from owner: **Developer Edition was unsuccessful and is no longer a development priority.** Focus engineering on the normal Windows InstaCleaner app, real Unfollow and Cancel Pending, truthful run status and durable batch evidence. This document does NOT delete historical Developer code/artifacts or user data, and does NOT claim live Instagram acceptance. The abandoned, unmerged #31 Developer probe experiment must not be shipped as a reason to ask the owner to test Developer again.

## Source problem and fix in the normal action robot
- `ActionRobot._run` used to wait indefinitely when its Chrome failed to expose a verifiable Instagram signed-in account, with no limit or terminal diagnosis. Unfollow/Cancel appeared inert, although **no relationship-changing click was sent**. Limit the manual-sign-in waiting phase to 240 seconds, then report a clear `blocked` state explaining how to sign in manually in the robot's own Chrome, without erasing the queue, approving a batch or writing false action success. Account challenge stops immediately. Owner can later explicitly restart.
- Username identity comparisons in the normal Chrome login and followback-audit path were case-sensitive even though Instagram usernames are case-insensitive. Normalize comparison using `casefold()`, reject missing/different owners. An exact target URL validation also compared lowered browser path with an unlowered saved username; fix HTTPS and casefold checks.
- The fix changes only the public action worker and its offline tests; no new Developer diagnostics, interface, API mutation, Instagram secrets, CAPTCHA bypass or auto-click replay.

## Evidence and release boundary
- New normal-app tests exercise unverified-owner timeout and wrong-account denial using fake Chrome, proving no new action journal is created. Test helper checks owner capitalization and absent identity.
- Owner-installed live account Unfollow and Cancel Pending remain unverified: GitHub CI, local Chromium fixtures and built Windows Setup cannot prove working authenticated Instagram actions (#172 and #164).
- Reserve v120.56 until exact-head CI including integrated Windows installation passes and governed FINAL stable publisher can validate distributables. Do not create RCs. Do not automatically restart an uncertain past click.
