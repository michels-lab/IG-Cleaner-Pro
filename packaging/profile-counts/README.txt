# Insta Cleaner Pro — Integrated Windows application

This package contains the Windows application `InstaCleanerPro.exe`, including the Desktop workspace and local Chrome robot controller. Check `BUILD-INFO.txt` for the exact source commit. GitHub Releases is the installation channel; this README alone is not evidence that a candidate has been published.

## First launch

1. Extract the complete ZIP and double-click `InstaCleanerPro.exe`. Do not run a separate HTML file, Python script or legacy CMD launcher.
2. In the app window, sign in to Insta Cleaner and select the correct saved Instagram workspace. Chrome and the workspace remain locally scoped to this application.
3. Open **Automations → Automation Center**. All robots are located here:
   - **Profile Counts:** collects public Followers/Following counts for profiles already in your imported Following list. Uses ordered transfer chunks; the total size of your imported relationship dataset is not limited to 10,000 or 50,000. An optional **Refresh Following from Instagram** action exists, but it is NOT required for Profile Counts.
   - **Cancel Pending Requests** and **Unfollow:** account-changing workflows. Review targets, protected profiles, batch sizes and pacing; explicitly approve a selected batch before any changes are made.
   - **Followback Audit:** optional read-only verification on selected profiles.
4. When a robot needs Instagram, the integrated app opens a separate visible Chrome window. Sign in directly on Instagram if required; never enter an Instagram password in Insta Cleaner.
5. **Pause / Resume** and task progress are controlled inside Automations. Only one robot may navigate the active Instagram Chrome session at a time, so the two browser robots cannot corrupt one another's navigation. Your local analytics and manual review can continue separately.
6. Stay in **Automations → Automation Center** for Profile Counts progress, individual results, filters, pagination and CSV exports. **Insights** contains aggregate account statistics and charts, not the Profile Counts robot or its per-profile results. All counts and exports cover the full imported list. **Mutuals** remains manual Focus only.

## Account data, persistence and protection

- Windows workspace data is stored under `%LOCALAPPDATA%\Michels Lab\Insta Cleaner Pro\`. The Chrome session and Profile Counts results use existing directories beneath `%USERPROFILE%\.ig-cleaner-pro\` to preserve prior records.
- Changing a browser, file origin or login can show a different local workspace. Back up your imported Following/Followers files before making changes. Do not delete an older HTML workspace before confirming any migration.
- No Meta private API or password collection is used. The integrated interface talks only to the local token-protected controller on `127.0.0.1`.
- Relationship analysis has no fixed application-level following/follower-count threshold; transport is chunked. Large histories remain constrained by actual browser memory/storage resources. Profile Counts now stores owner/account-scoped records in IndexedDB and preserves legacy localStorage data during migration. Storage failures must be surfaced, not silently discard history. Never assume stored snapshots prove *current* live followback.
- Action batches have deliberate safety/pacing limits that are unrelated to how many Followers or Following your account can **analyze**.
- Pausing and resuming preserve verified progress and pacing history. Uncertain clicks are not automatically replayed. Instagram can restrict automated browsing even with pauses, and the app does not bypass challenges.
- **Instagram login succeeds in normal Chrome but loops on CAPTCHA in the robot?** This can happen because the robot uses a separate persistent Chrome profile. Stop/pause the robot; do not keep retrying CAPTCHA, transfer cookies, delete your local session, or assume regular-Chrome login proves robot access. The **Automations** screen now exposes manual Pending/Following review and **keeps Profile Counts CSV import/export visible even when the integrated Windows backend is connected**. Manual review does not automatically cancel a request. Do not mark a request canceled until Instagram confirms it.
- The **Start Profile Counts in separate Chrome** button actually starts the collector; it is not a passive sign-in check. During an unverified CAPTCHA, the status offers safe Pause and manual paths. An action robot blocked at CAPTCHA cannot be resumed blindly; obtain a verified session and approve any new action batch explicitly.
- Profile Counts results from Windows do **not yet** automatically sync into Android.

## Chrome Companion — read-only Profile Counts in your NORMAL Chrome session

If Instagram works in your regular Chrome but reCAPTCHA loops in the separate robot browser, the ZIP also includes the `chrome-extension` folder.

1. Extract the complete ZIP to a stable directory. In regular Chrome open `chrome://extensions`, enable **Developer mode**, choose **Load unpacked**, and select that extracted **chrome-extension** folder. The extension is not in Chrome Web Store.
2. In Insta Cleaner open **Automations → Profile Counts** and click **Export Following queue CSV**. In the toolbar extension, enter the current Instagram workspace label and import this CSV.
3. With Instagram already signed in in this same regular Chrome, use **Open next profile**, wait for the visible header to load, and click **Capture visible counts**. Repeat with explicit clicks for each profile.
4. In the extension, **Export results CSV**. Back in **Automations → Profile Counts** select **Import captured results CSV**. Existing imported Following and stored Profile Counts records are preserved; records unrelated to the active Following list are ignored.

After completing all never-measured or incomplete profiles, use **Start oldest-first re-audit** to review the profiles with the **oldest last-count date first**. The extension tracks each re-audit cycle and keeps every previous measurement (followers, following, time, precision); a profile is measured only once in the current cycle. Export the latest values as the normal Insta Cleaner import CSV, and optionally export the complete dated history for change comparisons. Importing a new Following list does not reset old measurements.

The extension uses only temporary `activeTab` permission after a click and local browser storage. It has no Instagram site-wide host permissions and never reads/transfers cookies, collects passwords, solves CAPTCHA, or performs a follow/unfollow/cancel action. Missing profile counters are not marked successful; K/M counts are flagged approximate. All data stays on your PC. Read `chrome-extension/README.md` for exact instructions and limitations. This **does not** provide an autonomous replacement for Cancel Pending or Unfollow. It is a manual read-only recovery path until Instagram permits account interaction through an accepted integration.

## Security and acceptance

- Chrome is required. Do not disable Windows security or antivirus protections to run an unsigned Windows binary.
- Automated tests use simulated offline Instagram fixtures, an installed Windows EXE healthcheck, and Android emulator / Desktop Chromium checks. They do **not** prove successful actions against the owner's real signed-in Instagram or physical devices.
- Begin with a small explicitly approved batch. Monitor account identity, logged outcomes, and any verification challenges.

## Offline executable healthcheck

The Windows CI runner validates `InstaCleanerPro.exe --healthcheck`. This confirms the packaged UI, Playwright driver and local server can initialize without contacting Instagram. It does not validate the live Instagram UI.
