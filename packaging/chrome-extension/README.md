# Insta Cleaner Pro — Chrome Companion (read-only v120.47 development)

This is an **unpacked Manifest V3 extension** for your *regular, already signed-in Google Chrome*. It does not open Playwright, create another browser profile, read or transfer cookies, authenticate on your behalf, inject scripts on every Instagram page, bypass CAPTCHA, or use private Instagram APIs. A click on the popup explicitly grants temporary access only to the active tab. There are no background workers or automatic batch actions.

## Install from the official extracted Windows ZIP

1. Extract the **entire official Insta Cleaner Pro Windows ZIP** to a stable folder. Keep the included `chrome-extension` directory together; do not run an HTML file from inside the ZIP.
2. In **normal Chrome**, open `chrome://extensions/`, enable **Developer mode**, choose **Load unpacked**, and select the **chrome-extension** folder. Read its permission list. This is a local developer install; it has not been published to the Chrome Web Store.
3. Open Instagram in your normal, already signed-in Chrome tab. Pin **Insta Cleaner Pro · Chrome Companion** to Chrome's toolbar, and open its popup. Enter your active Instagram `@username` as a **local workspace label**. This label **does not establish or prove Instagram login ownership**.
4. In Insta Cleaner, go to **Automations → Profile Counts → Export robot queue** to get the current Following usernames as CSV. You can export this with the Windows app even if the Playwright robot cannot sign in.
5. Import the queue CSV into the extension; **Open next profile** navigates the currently active normal Chrome tab only when clicked. Once the profile has loaded, click **Capture visible counts**. Repeat by pressing Open next profile; no automated background navigation runs and no mass unfollow/cancel actions are available.
6. Choose **Export results CSV** in the extension, then use Insta Cleaner **Automations → Profile Counts → Import CSV results**. This CSV includes precisely the seven columns the app expects: `username,followers,following,checked_at,source,status,approximate`. Results are restricted to the selected workspace and your imported Following list. An incomplete/missing header counter is not saved.
7. Saved rows survive reopening the Chrome popup. Importing a new queue does not delete previously captured counts. Clearing a workspace requires confirmation, affects only that locally labelled workspace and does not delete Insta Cleaner's imported exports/history.

## Historical measurements and oldest-first second audit

The first pass always prioritizes never-measured imported profiles, then incomplete/unavailable profiles. It skips already measured profiles. Each successful profile capture preserves its **Followers and Following** values, measurement timestamp, precision, and preceding snapshots.

Once the first pass is complete, click **Start oldest-first re-audit**. A dated cycle is created containing all measured profiles, ordered by their **oldest most recent measurement**. Every profile is visited **at most once per cycle**, with navigation and capture only after your clicks. A failed capture never counts as an updated measurement; the profile remains eligible until an accurate reading is saved. Cycle progress persists when reopening the extension. At the end you can start a third (or later) audit sorted by the oldest available last measurement again.

The popup displays the increase/decrease in Followers and Following compared to the previous capture. **Export latest results CSV** gives Insta Cleaner the current values; **Export dated history CSV** includes all prior successful measurements, even profiles no longer in the current Following queue. Starting another cycle and importing a new queue do not erase history. The optional **Clear this workspace** action remains a confirmed destructive deletion.



- Only read-only visible profile header counters are parsed. The extension **cannot** cancel a request, unfollow, follow, like, scrape DMs, or claim Instagram has approved automated browsing. It uses `activeTab` and `scripting` only after your explicit click, plus `storage`, `unlimitedStorage` and `downloads`; **no host permissions, cookies, debugger or network permissions**.
- Chrome normal account login already succeeds for the owner, but this does **not** guarantee that Instagram will always show visible counts on every page or that Chrome will allow every navigation. Never keep retrying Instagram challenges. The extension does not solve CAPTCHA or login issues.
- Approximate `K/M` values are labelled `approximate=true`. No fabricated counts, no silent empty success and no inferred followback from a historical export.
- Large imports are not clipped by an arbitrary follower-count limit; actual available RAM/storage and browser restrictions still apply. Data is stored under `chrome.storage.local` on your computer; there is **no automatic sync** to Android or other computers.
- No account-changing robots have been migrated or tested on normal Chrome. This feature is a functioning human-driven **Profile Counts companion** only. It does not fix automated Cancel Pending or Unfollow. Those remain blocked pending separate user-visible consent and live validation.
- Loading unpacked files requires a trusted folder. Inspect the extension files before installation and leave its extracted directory in place so Chrome can reload it after future updates.
- Automated fixture/JS/packaging tests do **not** validate a real logged-in Instagram account. Physical Chrome installation and actual owner data acceptance remain outstanding.

Current official stable remains **v120.46** until a separately authorized GitHub Release packages this feature. Development source in `main`/PR is not an official owner download.
