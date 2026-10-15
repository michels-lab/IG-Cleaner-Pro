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
- Profile Counts results from Windows do **not yet** automatically sync into Android.

## Security and acceptance

- Chrome is required. Do not disable Windows security or antivirus protections to run an unsigned Windows binary.
- Automated tests use offline Instagram fixtures, an installed Windows EXE healthcheck, and Android emulator / Desktop Chromium checks. They do **not** prove successful actions against the owner's real signed-in Instagram or physical devices.
- Begin with a small explicitly approved batch. Monitor account identity, logged outcomes, and any verification challenges.

## Offline executable healthcheck

The Windows CI runner validates `InstaCleanerPro.exe --healthcheck`. This confirms the packaged UI, Playwright driver and local server can initialize without contacting Instagram. It does not validate the live Instagram UI.
