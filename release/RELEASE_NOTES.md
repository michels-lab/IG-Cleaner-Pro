## v120.45 — Profile Counts from imported Following, improved login detection, English UI

- **No mandatory Following scan:** Insta Cleaner now sends the profiles already imported into the selected Instagram workspace straight to the local Windows Profile Counts robot. Opening the owner's Following list is optional, for an explicit refresh only.
- **11,869-profile support:** the imported queue no longer stops at the former 10,000-profile limit. Owner/account-specific saved counts and pacing are preserved.
- **Login detection:** recognizes the signed-in Instagram account beside the Home **Switch** control; verifies the selected owner before collecting profile counts, with a safe Edit Profile fallback and conflict checks.
- **Recoverable discovery:** optional Following refresh recognizes buttons, links and text in the owner's profile and can wait while Chrome remains open for manual help instead of immediately ending the browser session.
- **English interface:** expanded English labels and status feedback across Desktop, Windows and Android; some legacy dynamic strings may still need localization.
- **Downloads:** the official integrated Windows ZIP with `InstaCleanerPro.exe`, standalone Desktop HTML/optional ZIP, and production-signed Android APK. The Windows Chrome robot does not run on Android.
- **Validation:** offline Chromium, Python, Desktop UI, Android emulator, integrated Windows EXE and exact-commit signing/artifact gates. Real Instagram navigation with the owner's signed-in account, device use and Instagram action outcomes still require supervised acceptance; simulated tests do not guarantee live Instagram compatibility.
- **Safety:** a stored Following export is a historical snapshot, not a live proof of non-followback. No accounts are followed or unfollowed by Profile Counts.

## v120.44 — optional followback audit, Unfollow filter, login resilience

- Unreviewed Unfollow filtering and optional independent read-only followback audit (#85).
- English labels in Automations and Profile Counts; full English-only UI remains tracked in #86 and is not yet complete.
- Improved account/login recognition and owner-scoped guards.
- Real Instagram signed-in browser acceptance remains pending; simulated Chromium tests do not replace live verification.
- Windows integrated EXE, standalone Desktop HTML and production-signed Android are subject to governed publication checks.

## v120.43 — Integrated Windows Insta Cleaner + account switching + safe Profile Counts

- **Windows integrated app:** Download `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.43.zip`, extract, and double-click **InstaCleanerPro.exe**. It includes the Desktop workspace, visible Chrome robot and loopback controller. Requires Google Chrome; no CMD, Python or separate HTML to start the robot. Windows needs manual testing on the owner's machine.
- **Instagram Profile Counts:** discovers Following from visible Instagram, checkpoints per owner and Instagram, reads profile Followers/Following values and shows live progress with pause/resume. Incomplete scans *retain* previously recorded users; only an exact visible Following total allows declaring the list complete. Missing/partial data never becomes proof of no followback.
- **Automatizaciones:** separate opt-in Cancel Sent Requests and Unfollow Non-Followback with per-batch confirmation, protected favorites, omit-current-batch, human-paced browser actions, identity checks, after-click verification, journaling and immediate stop on challenge/ambiguous UI. **Mutuals continues Focus-only, no automatic actions.** Instagram may limit automated browsing.
- **Accounts and session safety:** Windows/Desktop switching between saved IG Cleaner logins (does not sign out), Android encrypted account vault, tests for A → B and history isolation. Each Instagram owner/account remains isolated.
- **Android:** production-signed `IG-Cleaner-Pro-Android-v120.43.apk` with same signing certificate and package ID as v120.42; includes the updated embedded Desktop workspace. The Windows Chrome automation engine does **not** run inside Android, and Profile Counts collected on PC do **not** automatically sync into Android yet.
- **Desktop browser:** standalone offline `IG-Cleaner-Pro-Desktop-v120.43.html` and optional zipped HTML/assets remain available.
- **Validation:** source/behavior tests, mocked Instagram interactions in Chromium, real Desktop rendering, installed Android emulator compact/wide screenshot checks, RLS isolation, Windows bundled EXE healthcheck and persistent Android signing verification. Checksums are bundled.

**User acceptance not yet completed:** The owner's actual Windows/Chrome/Instagram session, private/public follow/unfollow controls, real cancellation outcomes, and cross-device data roundtrips have *not* been exercised. This GitHub release provides a build for supervised testing, not a guarantee of successful Instagram actions. Start with a deliberately selected small batch, inspect per-profile journal and back up existing lists. Stop on login or CAPTCHA challenges; no bypass. This is a GitHub release, not a Google Play publication.
