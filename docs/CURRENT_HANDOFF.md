## 2026-10-18 — Official v120.51 stable release published (real Instagram acceptance still pending)

- User explicitly requested `TERMINA TODO Y DALE RELEASE` in the InstaCleaner continuation. PR [#126](https://github.com/michels-lab/IG-Cleaner-Pro/pull/126) merged after all five exact-head QA families passed. The `main` merge commit `1b566b76dd16e34375bbb265531ee7c4f3fe49f3` also passed Desktop, Android, general CI and the installed Windows/Chromium integration tests.
- Authorizing request SHA `f4218e33cc5562c49227b45da23dca9715582a87`; guarded official workflow [39114910174](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39114910174) **SUCCESS**: automated installed Windows Setup launch/upgrade/uninstall evidence, offline real Chromium action tests, same-SHA Desktop/Android rendered evidence, stable original-production-signer Android APK, checksums and public asset verification.
- Normal GitHub stable [v120.51](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.51) published **2026-10-18T09:25:11Z**, `prerelease=false`; nine assets checked including `IG-Cleaner-Pro-Windows-Setup-v120.51.exe`, `IG-Cleaner-Pro-Android-v120.51.apk`, Desktop standalone HTML/ZIP and `SHA256SUMS.txt`.
- Scope: ten-tab visible Chrome workflow, bounded and live-reported wait for Following/Requested controls, owner-verified sequential Unfollow/Cancel actions with no uncertain replays, and one read-only next-profile warmup *only when visit pacing permits*. A stale same-URL profile is reloaded unless specifically confirmed as preloaded; outcome journal is persisted before closing confirmed tabs.
- Post-release safeguard: release authorization reset to `authorized=false,status=published`; distribution manifest reconciled to stable v120.51 and next reserved v120.52, no automatic follow-up publication.
- **Not physically accepted on owner's machine/Instagram:** no real unfollow, pending cancellation or challenge outcome confirmed by CI. User must install official v120.51 Windows Setup, keep local data intact, run a small explicitly approved test batch and inspect final Follow/Follow Back plus Issue Review. Do not say owner has installed the release. Android Play Store publication and third-party email template configuration remain separate provider tasks.

## 2026-10-18 — v120.51 release candidate: paced tab prefetch and official Setup

- User ordered next official release; version authority: `release/distribution-manifest.json` `nextRelease=v120.51`. Work on `feat/v12051-robot-prefetch-release-20261018`. Preparing production signed Android, Desktop HTML and Windows Setup v120.51 identities.
- Existing ten tabs, bounded visible Following/Requested wait, retained uncertain tabs, owner-verified sequential relationship actions are preserved. New read-only speculative next-profile navigation occurs *only when current-profile readiness is pending AND configured visit pacing/rest allows it*. One prepared next profile at a time (not a ten-profile burst); it is reused in its normal queue slot. Journal is persisted before navigation and no ambiguous post-click outcome is replayed.
- New regression checks: preloaded tab reuse, prefetch-target navigation exactly once in offline Chromium, and precise durable visit finish timestamps for overlapping navigation.
- Real owner Instagram browser acceptance remains unverified and must be disclosed even after release; no CAPTCHA bypass/private Instagram API. Stable publication requires exact-source CI/install/render/signing and checksums. Do not claim a release until GitHub confirms published assets.

## 2026-10-18 — Owner revision: 10 tabs, explicit live wait/status when Instagram has not rendered (development only)

- Work branch: feat/action-tabs-ten-20261018; latest owner preference is **10** Chrome tabs rather than 5.
- Important additional acceptance condition: do not interpret an unrendered Following/Requested button as absent immediately. Wait for the real profile/header, then for the exact relationship control, and visibly report the current @profile, stage and elapsed/max time in Automations. A 20-second read-only timeout leaves the uncertain tab open for manual review and stops the queue, not a silent skip. The UI distinguishes profile loading from waiting for Following/Requested and reports profile_load_timeout separately.
- Preserve signed-in owner confirmation before every relationship-changing click, no parallel unfollows, no action replay after uncertainty, existing account-scoped journals and challenge stops. Original 5-tab integration is in main; this ten-tab + wait status change must pass fresh exact-head Windows Chromium/installer, Profile Counts, Desktop, CI and Android UI checks before merging.
- No version bump, no publication. v120.50 official stable is unchanged. Real Instagram/device proof pending.

## 2026-10-18 — Candidate: five Chrome action tabs and DOM-readiness waits (NOT released)

- User now prefers **5 tabs** (not 3) and requires each action's tab to remain visible until outcome is confirmed; prior screenshot showed `Could not verify ... session after the action` and `Instagram control not found; no action clicked`.
- Branch: `fix/instagram-action-readiness-20261018`. Adds up to five per-target browser tabs for local owner-controlled action visits, read-only bounded waits for Following/Requested and menu UI, repeated read-only post-click ownership proof, durable action journal before confirmed-close, and UI visibility/warning for retained tabs. Relationship-changing clicks remain sequential, not five simultaneous clicks. *The five-tab pool is a review/working capacity; it is not a claim of concurrent browser automation or live success.*
- Five unresolved tabs halt further processing rather than silently closing or replaying ambiguous actions. Explicit Pause is allowed to close the Chrome session after a confirmation warning. Manual tab closure must never mark an action `ok`.
- Pending: exact-head CI, installed Windows Setup/Chromium regression, physical Chrome owner's session acceptance. Do not release without a new explicit owner request. v120.50 remains the official stable.

## 2026-10-18 — Verified stable v120.50 published (real Instagram acceptance pending)

- Normal public GitHub [v120.50](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.50) published 2026-10-18T07:08:16Z, built from exact SHA `e0a95a8c192642c175a1b080212c7ddd5a4f0655`; governed run [39106161831](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39106161831) **success**. Nine assets confirmed, including Windows Setup, Android production APK, Desktop HTML/ZIP and SHA256SUMS.txt.
- Independent exact-commit release checks passed: token-guarded owner approval, installed Windows Setup validation, real offline Chromium action selector safety, Desktop/Android screenshots, original Android production signing certificate, all asset names and hashes. The real user's Instagram account was **not** touched by CI.
- Scope: bounded non-semantic visible handle + unique Following/Siguiendo control detection in profile main, layout category diagnostics when no click is possible, safe new-batch retry of known zero-click issues, improved wrapping of Issue Review details.
- Post-release administrative safeguard: release request returned to `authorized=false,status=published`; distribution manifest now records stable v120.50, next v120.51; README and handoff updated. No automatic future release authorization.
- Still open: real owner Windows/Chrome test that the correct Following menu opens and account reliably changes to Follow/Follow Back; if it fails the new diagnostic counts must be captured for deeper DOM-specific remediation. No blind clicks, no challenge bypass and no journal reset.

## 2026-10-18 — v120.50 release preparation: Instagram Following diagnostic

- Owner's actual v120.49 issue screenshot reports no click while the page visibly displays Following. PR #122 implements a read-only bounded `main` profile hero survey handling usernames in span/div and unique nearby following controls (role=button, button, tabindex=0), with explicit safety rejection of counts/links, suggestions and duplicates.
- The issue message includes *category counts only* of the robot-controlled Chrome DOM: `main`, `exact username`, `named interactive controls`, `eligible controls`; no sensitive content is recorded. Known no-click issues remain safely retryable with a fresh owner-approved batch.
- PR #122 passed 5/5 exact-head workflows and merged. Prepare v120.50 signed Android metadata and visible UI. Must still pass governed release exact-commit screenshots, setup install/uninstall/upgrade, production signer and checksum/publication checks.
- User must test installed Windows with a small approved batch; do not claim a working live Instagram unfollow from mock Chromium fixtures. Stable v120.49 stays public until v120.50 independently verified.

## 2026-10-18 — Unfollow still misses Following after v120.49

- Owner v120.49 screenshots show Following visibly present in Instagram but Issue Review still records `missing_profile_info`, no action click.
- Investigation confirms `h1/h2/h3`-only username gating in v120.49; Instagram's username can be visible in span/div with its clickable Following control nested outside a semantic header. New code checks an exact visible handle and an eligible nearby `button` / `role=button` / `tabindex=0` within profile main, plus target URL and session owner checks.
- Unknown controls remain no-click manual review; a category-only read-only diagnostic is attached to no-click Issue Review messages to stop guessing why detection failed. History protects clicked/uncertain outcomes; new diagnostics remain safely retryable if owner approves another batch.
- QA to run: exact PR-head Profile Counts, real local Chromium action fixtures, Windows Setup install/uninstall, Desktop and Android render, general CI; then real owner's installed Windows Instagram test. No live success claimed.

## 2026-10-17 — v120.49 published: Unfollow Following detector (no-click retry hotfix)

- GitHub stable [v120.49](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.49) published at 2026-10-18T01:25:15Z (October 17, Saltillo local time), source SHA `a6d4583df3cc75ae814b0619c291eac29ed18bff` and owner-authorized governed workflow [39086045263](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39086045263) **success**. Nine expected assets confirmed: Windows Setup, ZIP, Android production-signed APK, standalone HTML and ZIP, SHA256SUMS and metadata/logo.
- Release gates passed: Android source/signed certificate, rendered actual Android/Desktop screenshots, Windows installed Setup and isolated Chrome DOM safety tests, package checksums and published asset verification. Live Instagram unfollow on the owner's profile **not yet physically accepted**. Do not claim the user's screenshot target was unfollowed.
- Post-publication safeguard: release authorization deactivated (`authorized=false`, `status=published`), stable manifest advanced to `v120.49` and next `v120.50` reserved; no automatic publishing of v120.50 is authorized.
- Owner should install Windows Setup v120.49 using Updates or the official Setup (no prior uninstall or journal reset), then start a **small newly approved Not Following Back batch**. Exact legacy `missing_profile_info` pre-click records are eligible again. Inspect final profile state and Issue Review. Still ambiguous post-click entries remain excluded from automatic repetition.
- Remaining follow-up: actual owner's Chrome/Instagram acceptance, confirm follow menu selector and post-click Follow/Follow Back, observe challenge stop and owner-identity checks, verify update preservation and cross-device data where relevant.

## 2026-10-17 — v120.49 owner-reported Unfollow hotfix candidate

- PR #120 merged after 5/5 GitHub QA families. The owner screenshot shows the Instagram profile displaying Following while the v120.48 action robot reported nothing clicked. The fix recognizes safely scoped profile Following/Siguiendo buttons in header/main, exact target heading and caret, while refusing unrelated links or duplicate controls.
- Previously quarantined `missing_profile_info` results with exact pre-click messages become eligible for a new explicit batch after reading the latest Windows journal. Potentially clicked uncertain results remain excluded; do not reset/delete local history.
- Release preparation updates v120.49 signed metadata and Desktop version. Publish only via the owner's governed stable request after exact-head CI. Do not claim successful unfollow on live Instagram before owner tries installed Setup.
- Previous stable v120.48 remains the only published release until v120.49 publication and asset integrity are verified.

## 2026-10-17 — Unfollow visible Following control not detected (v120.49 development)

- Actual user's v120.48 Windows Issue Review lists three `missing_profile_info` in "Not Following Back". In the next screenshot the Instagram profile visibly has the Following button; the robot made **zero clicks** on the three affected users.
- Fix candidate `fix/unfollow-following-control-20261017`: detects Following/Siguiendo accessible button (including role=button div and caret label) in verified target header or main-profile hero with exact visible @handle heading. Never turn a Following count/link or ambiguous duplicate into a click.
- Exact legacy `missing_profile_info` no-click records are eligible for a new explicitly approved batch; uncertain previous clicks remain quarantined. Client action planning trusts read-only disk history over stale browser cache. Do not delete local action journals or ask user to reset profile data.
- Regression tests in `tests/test_profile_actions_chromium.py`, `tests/test_action_batch_history.py` and `tests/automations-cold-start.test.cjs`. Run exact-head CI, Desktop/Android rendering and Windows installed Setup preview before merge. Real signed-in Instagram acceptance cannot be claimed from offline DOM tests.
- Published stable stays v120.48; do not silently republish or disable active user state to work around Instagram.

## 2026-10-17 — v120.48 officially released and authorization deactivated

- Owner-authorized normal stable [v120.48](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.48) published at 2026-10-18 00:27:53 UTC, 2026-10-17 in Saltillo. GitHub governed run [39082472684](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39082472684) **SUCCESS**; exact publication source SHA `19680119c0e0a1c5d5bdfb954793c355849f0bdb`.
- Full official assets verified: Windows native Setup.exe + checksum, optional integrated Windows robot ZIP, standalone Desktop HTML and ZIP, original logo/privacy files, SHA256SUMS.txt and production-signed Android APK with the original app signing identity.
- Independent release gates passed: authenticated authorization, eight real Desktop screenshot surfaces, installed Android Home/About screenshots, Windows Setup wizard/build/install/start/upgrade/uninstall and release asset/integrity tests. The user's **real Instagram sign-in and action outcomes, actual local Windows update and Samsung cross-account state** remain unverified.
- Release request marked `authorized=false,status=published` with immutable publication run, SHA and timestamp. Distribution manifest now records stable `v120.48` and reserves `v120.49`; no later release authorized.
- Functional changes: sequential Pending/ZIP reimport and cold-start action-journal safety, one read-only pending-cancel verification without duplicate click, recoverable manual Focus previews and targeted English UI strings. Remaining dynamic Spanish text and real-session acceptance are tracked separately.

## 2026-10-17 — v120.48 stable release candidate, explicitly requested by owner

- Scope: Pending Requests replay-safe history across multi-batch imports and Windows cold startup, read-only revalidation of uncertain cancellation, Focus preview recovery and targeted English UI changes.
- Publishing must use governed v120.48 request only after exact-head CI. Android signing and Gradle version updated together; Windows release-gate includes `tests/automations-cold-start.test.cjs`.
- Do not conflate a passing Playwright DOM fixture with real Instagram access. Owner's actual Windows Chrome, installed-updater flow, physical Samsung and cross-device data acceptance remain open.
- Stable public version remains v120.47 until the exact v120.48 GitHub Release is independently verified. No forced release if any signing, rendered UI or Windows Setup gate fails.

## 2026-10-15 — v120.48 Pending batch and cancellation work (development only)

- Candidate branch `fix/pending-request-readonly-recheck-20261015`: fix last-batch replay after the second batch by exposing the persisted per-account/action ActionRobot attempted journal and excluding all prior attempted rows from new selections, then fetching the latest journal before new batch authorization. A signed-in Chrome robot still only performs actions after explicit user confirmation; uncertain click outcomes remain excluded rather than silently retried.
- Imported Pending list is no longer UI-truncated at 300 rows: Automations displays 100-row pages and supports all imported entries; **Open next Pending review batch** opens read-only Pending Focus with visible confirmation (independent of the cancellation robot). Frozen Focus previews after a new ZIP or JSON import regenerate into a *new visible preview* requiring another click, avoiding both a permanent stale lock and silent substitutions. **Recover current batch** opens prior unconfirmed review; individual profile links survive Chrome popup blocking.
- Uncertain cancellation gets one safe read-only post-click profile reload, confirms only a visible Follow / Follow Back state and matching owner, reports otherwise as `pending_cancel_unverified` for manual review. No auto-Cancel retry or CAPTCHA bypass.
- Required tests: `tests/test_action_batch_history.py`, `tests/automations-next-batch.test.cjs`, `tests/pending-focus-reimport.test.cjs`, `tests/test_profile_actions_chromium.py` plus Windows installer and Desktop/Android CI.
- Current public release stays v120.47. Actual owner Chrome popup settings, current export and live Instagram session are unknown; offline tests cannot certify those.

## 2026-10-15 — Pending Requests uncertain cancellation safe refresh (v120.48 development)

- Existing v120.47 Pending Requests robot may click and then fail to confirm because Instagram's current page has stale Requested UI. Historical `review/error/blocked` journal entries are not replayed; manually inspect any reported username under Automations → Issues, Open profile, without running a second cancellation.
- New branch `fix/pending-request-readonly-recheck-20261015`: **one** read-only target-profile refresh after a cancellation click whose state remains unverified; require a correct Instagram target URL, verified owner, and Follow/Follow Back state to mark confirmed. Other states—including Following/Requested, redirects, challenge/login and errors—stop safely without re-clicking. UI exposes `pending_cancel_unverified` clearly in English with manual review link.
- **Windows preview after stable publication:** `tools/build_windows_installer.ps1` supports an explicit `-AllowCurrentStablePreview` only in the unreleased preview workflow, when the packaged Android metadata remains the current stable v120.47 and nextRelease is reserved for v120.48. Governed stable release publication never passes the override and remains version-locked.
- Chromium regression coverage asserts a delayed successful change can be recognized without a second Instagram action. No real owner session tested. Published v120.47 is unchanged; release needs explicit authorization for later versions.

## 2026-10-15 — Official stable v120.47 RELEASED, future version unrequested

- GitHub release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.47 (2026-10-15 22:01:27 UTC). Verified exact commit `9d252f70c40145602bb7ad44ef74ffbf26bc5181`; governed publisher run `38813431832` completed successfully. Required Windows Setup EXE, Android production-signed APK, Desktop single HTML/ZIP, portable compatibility ZIP, checksum files, logo and privacy notice all exist as public release assets.
- First release attempt was correctly blocked due to old six-screenshot assertion while real Desktop automation now captures eight. Visual verifier was updated to require all eight real Home/About/Automations screenshot files across both viewport classes. Rerun passed exact-commit visual QA and Windows installed Setup acceptance; real signed stable Android APK and checksums passed publishing.
- Owner's request has been marked `authorized=false,status=published` to prevent unintentional re-publication. Distribution manifest now sets `currentStableRelease=v120.47`, `nextRelease=v120.48` (reserved only; not an owner release request). The tested v120.47 source is immutable under tag; do not retroactively rewrite published binaries.
- Remaining acceptance: owner physical Windows/Chrome login and Instagram robots, updater on a real Windows installation, Android physical-device installation, and Windows Authenticode. No CAPTCHA bypass or claims of live user account proof.
- Next work should begin on a new branch/version and only release after explicit owner instruction.

## 2026-10-15 — Windows checked updater (v120.47 candidate, NOT published)

- Branch `feat/windows-verified-updater-20261015` implements installed Windows-only Updates action in the fixed header; visibility strictly gated on native loopback session fragment (no Windows installer in Android/standalone browser). About remains visible and independent.
- `tools/windows_updater.py` checks GitHub's anonymous official stable feed on launch/manual request. Download requires user click, validates exact SHA-256 + declared asset size and hostname; Setup launch requires another explicit confirmation and local app/robot backup first. Chrome cookies/profiles are not copied into backup. No automatic install, no claim that launching Setup proves installation; no Authenticode signer yet.
- Embedded real package version via `--add-data release/android-signing.json;metadata`; native backend exposes authenticated update endpoints. Tests: Python `tests/test_windows_updater.py`, Node `tests/windows-updater-ui.test.cjs`, Windows Setup install/launch smoke and Desktop/Android rendered CI. Live owner Windows acceptance remains separate.
- Existing second-audit Profile Counts PR #111 merged in main `9ab8a399`; outdated conflicting PR #106 closed without merge. Official stable remains v120.46. No release authorization.

## 2026-10-15 — Windows Profile Counts oldest-first re-audit (v120.47 development)

- Existing `main` already has independent IndexedDB history under `ig_cleaner_profile_counts_history_v1`, a per-profile viewer/deltas and CSV export; do not merge conflicting old PR #106 over it.
- Candidate branch `feat/profile-counts-windows-reaudit-20261015` implements an explicit oldest-first second audit using the imported Following queue, with never-successful users prioritized, frozen crash-resumable cycle state and full per-account dated Windows CSV. Previous successful latest measurements are not overwritten on failed rechecks; pre-upgrade latest values are archived non-destructively.
- Automations retains all robots and offers re-audit and safe paginated Windows-history synchronization. Neither accounts nor total Following sizes are arbitrarily capped; request batching is capped at 2,000 rows. Live Instagram challenges still require manual human verification; no CAPTCHA bypass.
- Test gates: `tests/test_profile_counts_audit.py`, `tests/profile-counts-ui.test.cjs`, Windows native/Chromium suite and setup INSTALL/LAUNCH/UPGRADE/UNINSTALL; exact-head evidence before merge. Published stable remains v120.46 until explicit separate release authorization.

## 2026-10-15 — Cross-app Windows installer source validator follow-up

- Windows Setup candidate on `main` passed same-commit Windows INSTALL/LAUNCH/UPGRADE/UNINSTALL, Desktop Chromium, Android emulator and CI; public release remains v120.46, no v120.47 authorization.
- Governance checker rejected mismatched product alias and `{userdesktop}` token despite per-user shortcut semantics. Fix in IG Cleaner branch: canonical `IG Cleaner Pro` label in bilingual guide + use `{autodesktop}` for optional icon. Complementary master registry PR changes product key to canonical license identity. No robot behavior changed. Master audit still has unrelated FoamLens failure, to be tracked separately.

## 2026-10-15 — Interactive Windows Setup contract evidence

- Added exact-candidate interactive UIAutomation script and captured PNG proving EULA acceptance/decline is enforced, rather than only static licence-source assertions. Runs before the silent install/upgrade/runtime/uninstall test in Windows preview and governed release CI.
- Evidence must be checked against the latest PR head before calling wizard validation complete. No official release, Authenticode signature or automatic updater authorization.

## 2026-10-15 — Native Windows Setup integration (v120.47 development)

- User requested a proper installer instead of having to extract and run `InstaCleanerPro.exe`. New `packaging/windows-installer/InstaCleanerPro.iss` follows the Michel's Lab master Windows installer experience standard: branded native wizard, real proprietary license, optional shortcuts, start menu, taskbar guide and uninstaller.
- Builds still bundle the same integrated PyInstaller application + Chrome Companion, but the versioned **Setup.exe** is now the primary Windows artifact. Prior ZIP is optional secondary compatibility only. App/robot data outside the installation directory persists across manual upgrades and uninstalls. No automatic background updater, Authenticode signature or real Chrome-session acceptance is claimed.
- Source of truth: `release/distribution-manifest.json`; CI uses `tools/build_windows_installer.ps1`, `tools/test_windows_installer.ps1` and `tests/windows-installer-contract.py`; published v120.46 remains unchanged and v120.47 has no release authorization.
- Require exact PR SHA BUILD/INSTALL/installed LAUNCH and real interactive wizard evidence, then governed stable publication only on explicit owner request.

## 2026-10-15 — Persist longitudinal Profile Counts history inside Insta Cleaner (development v120.47)

- After PR #104 introduced the Chrome Companion's first-pass unmeasured priority, explicit oldest-first second audit, and append-only local Chrome history, an integration gap remained: Insta Cleaner Desktop imported only the **single newest** row per username, silently discarding older dated snapshots from the Chrome Companion's full-history CSV. The user needs repeated audits and reliable comparisons over time.
- Implemented per-Instagram-account **append-only IndexedDB measurement history** in Desktop Automations, using a separate `ig_cleaner_profile_counts_history_v1` database with scoped `measurements` and `profile` indexes. Existing `ig_cleaner_profile_counts_v2` latest-record database and previous v120.45/46 localStorage keys remain unchanged. In environments lacking IndexedDB, a separately scoped, explicit-quota-error localStorage fallback is used; no arbitrary record count cutoff and no destructive migrations.
- `igcCountsImportFile` accepts chronological history CSVs containing multiple dates for the same username, archives **every valid successful reading** (even older than current), and updates current latest only for genuinely newer observations. Imported foreign accounts/invalid rows never enter history. Browser robot polling also archives a previous successful observation before updating latest, and awaits storage success.
- Added **Export complete measurement history** and **View dated measurements** in Automations → Profile Counts, displaying the latest ten measurements and change in Followers/Following from preceding displayed reading. Historical profiles that are no longer in Following remain exportable within the *same owner/account* scope. Stored results are not evidence of current followback.
- Expanded `tests/profile-counts-ui.test.cjs` with historical CSV, timeline, older/foreign-account isolation, and browser-robot preservation checks. Expanded real-Chromium IndexedDB acceptance `tests/profile-counts-indexeddb-browser.cjs` with three dated snapshots and reload, historical v120.45 migration, rejected foreign usernames, and per-profile UI comparison. No live Instagram or owner's private Chrome/browser data were accessed.
- Security and release: Read-only Chrome Companion still requires explicit user clicks. Cancel Pending/Unfollow still require verified account identity and separately authorized batch; no CAPTCHA bypass. Official release remains **v120.46**, development target **v120.47** without release permission. No claim of real-owner Chrome acceptance.

## 2026-10-15 — Owner follow-up: persistent counts and oldest-first re-audit

- Each username's Followers and Following readings are saved with timestamp and precision, not overwritten on a new audit.
- The first pass queues never-measured accounts ahead of incomplete accounts and skips already measured ones.
- Once the first pass is complete, owner can begin a second and later audit with profiles ordered by oldest last review and no duplicate profile within a cycle. Cycle position and full dated counts history are stored locally per workspace.
- Separate latest-count and full-history exports exist; repeated measurements show per-metric deltas. Offline tests pending exact head; do not claim real live Instagram acceptance.

## 2026-10-15 — Regular Chrome Companion for Profile Counts (v120.47 development, no release)

- Owner explicitly instructed to **build**, not just propose, a way for Insta Cleaner to work with Instagram in their regular Chrome. Prior owner evidence: Instagram already works in regular Chrome and the official mobile app, while the separate Playwright-driven robot Chrome loops through /auth_platform/recaptcha. PRs #102/#103 previously integrated safe challenge detection and manual CSV fallback; neither made the separate automated browser trusted.
- Implemented installable Chrome MV3 extension in `packaging/chrome-extension/` (manifest, independent read-only visible-profile parser, popup, setup/readme). Uses user-initiated `activeTab` injection on currently visible Instagram profile only; opens next selected Following profile **on explicit click**, never background scraping; no cookies, password collection, broad host permissions, network scraping, native messaging, devtools debugging, CAPTCHA circumvention or relationship-changing actions.
- Loads and deduplicates exported Following CSV; owner-supplied local workspace label scopes `chrome.storage.local` (no assumption of verified account ownership). Captures only visible Followers/Following counters when both are readable, flags K/M as approximate, preserves old records on queue replacement, and exports the exact seven columns accepted by **Automations → Profile Counts → Import CSV results**. Capturing a different profile than the current queue or an Instagram auth page fails safely.
- Added a Chrome Companion panel entirely in **Automations**, and `tests/chrome-companion.test.cjs` for count parsing, CSV compatibility, scope, explicit navigation/capture, errors and extension privileges. Plumbed test into Profile Counts and general CI. Windows preview and governed release workflows now bundle and verify the extracted `chrome-extension` folder in the official Windows ZIP, with guidance in both READMEs. Release manifest documents new read-only capability without changing stable/next version numbers.
- Critical scope boundary: This is a **real, manually operated read-only Profile Counts companion**, not a new autonomous Cancel Pending, Unfollow, or bulk counting robot. All Instagram account-changing robots remain on their own separate implementation and require verified identity plus fresh explicit batch approval. Regular Chrome signed-in behavior can be verified only on the owner's device. No extension was installed on their machine or tested against real Instagram during development. No version v120.47 GitHub Release authorized. Official stable remains v120.46.
- Validation **pending until exact PR head GitHub checks are observed**. Do not claim Chrome Web Store listing or a ZIP download until officially published and confirmed.

## 2026-10-15 — Windows CAPTCHA-safe manual fallback (v120.47 development only)

- Owner confirmed Instagram login works in regular desktop Chrome and mobile Instagram but loops on reCAPTCHA only in the separate Playwright-controlled Chrome profile opened by Insta Cleaner. PR #102 fixed safe waiting/navigation and was merged to main with 7/7 exact-head QA; live Instagram login in the robot remains **unverified**, and Instagram determines whether to accept that browser session.
- Found a separate functional regression: the connected Windows UI unconditionally hid `#igcCountsManualCSV` and `#igcCountsManualHelp` merely because a robot token existed. That deprived the owner of CSV import/export and an offline/manual continuation path precisely during login failures.
- On `fix/windows-captcha-manual-fallback-20261015`, restored manual Profile Counts queue/results CSV controls even when the local Windows backend is connected. Added explicit, English-only `needs_verification` / `needs_attention` guidance with buttons for **Pending manual review**, **Following manual review**, and **Pause robot**. The action robot blocked on CAPTCHA now shows the same human-only review paths and disables blind Resume (other paused/error recovery stays available).
- Renamed the Profile Counts launch control **Start Profile Counts in separate Chrome**, correcting its former misleading `Connect Instagram / Open Chrome` wording, and translated manually surfaced CSV errors.
- Expanded offline JS VM tests for local-backend visibility and CAPTCHA/manual workflow transitions in `tests/profile-counts-ui.test.cjs` and `tests/automations-execution.test.cjs`; maintained RLS/workspace isolation and action batch confirmation. The manual routes call existing `showPage('pendingRequests')`/`showPage('list')` only: they NEVER silently mark reviewed, unfollow, cancel, or bypass Instagram verification.
- Windows package guidance updated. Official latest released artifact remains **v120.46**, and this is unreleased v120.47 development. Real Chrome/Instagram account acceptance and physical device testing remain open. No new release was requested.

**Follow-up root cause found during implementation (2026-10-15):** both Profile Counts and ActionRobot called `page.goto("https://www.instagram.com/")` unconditionally when opening persistent Chrome. This could overwrite a restored `/auth_platform/recaptcha` or Login page BEFORE challenge detection. Added `preserve_instagram_auth_page` and prioritize an existing authentication tab so launch never navigates it away; offline tests cover restored CAPTCHA/Login tabs and ordinary profile pages. This does not authenticate the user or bypass Instagram's security controls. Release remains unauthorised.

## Handoff: 2026-10-15 — Live Instagram reCAPTCHA login loop; v120.47 safety and login UX fix (unreleased)

- Owner's **real Windows Chrome screenshot** shows Instagram's `/auth_platform/recaptcha` with an “I'm not a robot” checkbox. Owner reports completing the CAPTCHA returns to Login. This is evidence of a real **authentication/security challenge**, NOT proof that Instagram accepted the session, and NOT a successful robot action.
- Confirmed source defect: `challenge_detected` recognized `/challenge/` and `/checkpoint/` but NOT `/auth_platform/recaptcha`. Profile Counts could wait without recognizing the challenge and, after 15 seconds, attempt an optional own-profile navigation while a person was trying to sign in.
- Fixed challenge recognition by route and visible security copy. A new `safe_to_probe_owner_from_home` guard only permits the one-time read-only own-profile identity probe from actual Instagram Home with no login/password/challenge screen.
- Profile Counts now reports `needs_verification`, holds navigation while Chrome remains open for **human-only CAPTCHA handling**, and resumes ordinary identity checks only after challenge disappearance. If Instagram loops back to Login, no collection or account action is allowed without positive account identity verification. User may Pause; saved queues/history are not destroyed.
- Cancel Pending/Unfollow actions now fail closed on a challenge in any browser tab during login, rather than trying to proceed or automatically solving it. No change to action-confirmation gates, rate limiting, protected accounts, journal integrity or session isolation.
- New offline URL/body/security and login-page probe regression: `tests/test_profile_counts_recaptcha.py`, triggered by Profile Counts CI and Windows EXE workflow. Updated Automations status and `docs/PROFILE_COUNTS_ROBOT.md` recovery advice, including normal-vs-robot Chrome profile distinction and no cookie upload, CAPTCHA bypass or storage deletion.
- No real login was attempted by development. Whether Instagram will accept the separate Playwright/Chrome session remains outside the app's control and must be tested only by the owner. Official stable remains **v120.46**, next v120.47 has **no release authorization**.

## v120.47 follow-up: English Windows controller and authoritative Automations guidance — 2026-10-15

- Development branch `fix/v12047-english-automation-packaging-20261015` follows merged PR #99. The latest official public/stable download is **v120.46**, whose reported Windows Profile Counts/Pending failures are not fixed in the published binaries. No v120.47 release authorization was given in this continuation.
- Corrected user-facing action-controller, Profile Counts bridge and robot messages to English while preserving Spanish Instagram button/DOM recognition and legacy journal matching. No Instagram action algorithm, quotas, state schema, or session permission was deliberately changed.
- The Windows ZIP README now states that **all robots and the per-profile Profile Counts results/filter/export workspace are in Automations**. Insights contains account-level aggregates only. Updated the README's IndexedDB persistence description and removed the obsolete issue #96 pending-migration claim.
- Added `tests/windows-automations-owner-contract.py` to CI and the governed release contract; it checks the package guide, strict account errors, missing-file errors and compatibility vocabulary.
- **Validation not yet complete at this point:** require exact branch/PR head CI, Windows EXE, Desktop rendered UI and Android emulator before merge. Real signed-in Instagram action/collection on the owner's Windows PC is still unverified, and no account request has been canceled during this work.

## v120.47 Windows corrective fixes merged — 2026-10-14

- PR #99 merged into main, commit `298bf52e7230fba22501a1ac24852023ec4aafda`. Exact PR head `9e8ee7e511e0c7e5f07dbed2a0965add95d806f2` passed all five required GitHub checks: Profile Counts #38662603218, Windows #38662603179, Desktop #38662603260 (successful rerun for unrelated Switch Accounts intermittence), Android #38662603207, and full CI #38662603208.
- Bug A: Python profile-count validator rejected ordinary `http`-prefix usernames as URLs; corrected and covered by staged-import regression. No data cap or truncation introduced.
- Bug B: Cancel Sent Requests lost owner identity when Instagram hid target-page Profile navigation; uses a separate, read-only same-context owner tab with **Edit profile** proof, never clicks when wrong owner. Only definitely no-click blocked historical entries may be retried on another owner-approved batch.
- Product location: complete Profile Counts robot and *individual result table* (filters, export, pagination) now under Automations. Insights retains account-wide analysis.
- **NOT PUBLISHED**: stable GitHub Release remains v120.46; fixes are in main for next v120.47 release. Require separate explicit owner release authorization and governed publisher validation before download. User's real Chrome/Instagram session and actual cancellation acceptance remain unverified.

## v120.47 development — fixes for owner screenshots (not yet released)

- Live owner screenshot: Actions → Sent Requests blocked at first profile because the target profile hid the account identity navigation. Reported 1/40 processed, 0 confirmed. Never interpret this as a cancellation; no action performed. Fix is strict same-context own-profile Edit-profile proof in a separate read-only Chrome tab, with fail-closed wrong-account checks.
- Live owner screenshot: Profile Counts rejected imported usernames before Chrome started. Root cause: Python `valid_username` erroneously parsed legitimate `http`-prefix usernames as URLs. Corrected URL recognition and tests.
- All Profile Counts, including the per-profile results table and exports, is now in Automations. Insights is strictly aggregate analysis.
- Account-changing actions retain explicit batch approval, per-click identity protection, and no replay of uncertain operations. Safe no-click historical session failures can be reattempted on owner-authorized new batch.
- Stable v120.46 does not include fixes. v120.47 not yet published. No real Instagram acceptance, only offline synthetic DOM tests.

## Published stable v120.46 — October 14, 2026 (Mexico) / October 15 UTC

- Official verified normal GitHub Release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.46, exact source SHA `4550635e7435002915b47472452c4c74aba1bc04`, successful governed workflow https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38658477664 .
- All four release jobs succeeded: release authorization, exact-commit Desktop/Android visual proof, Windows integrated executable, and production-signed Android plus release artifact publication. Seven stable assets exist: Windows integrated ZIP, production-signed Android APK, standalone Desktop HTML, Desktop ZIP, logo, privacy notice, SHA256SUMS.
- Unified Automations robots and Insights analytics (#97), chunked imported queues and shared Chrome locking. Profile Counts now uses IndexedDB with non-destructive v120.45 legacy localStorage migration, bounded transactions, scalable CSV and audit legacy fallbacks (#98, issue #96 completed).
- Tests passed 50k/100k/250k synthetic relationship lists and 12,031 migrated audit history records in offline Chromium. These **are not** proof of live Instagram actions on the owner's actual PC; real signed-in Chrome and physical Android acceptance remain pending.
- Current stable `v120.46`; next development `v120.47` is **not authorized** for release. No automatic publishing, keep persistent Android keystore and historical backups intact.

## v120.46 development merged — 2026-10-14 (NOT PUBLISHED)

- PR #97 merged into main, squash commit `16c78ba84e6d110c7ef7ba8d6b2498f9078d0286`. Owner demanded all robots in **Automations**, Profile Counts analysis and results under **Insights**, and no dataset-size cap based on Following/Followers totals.
- Implemented Automation Center links to Profile Counts, Cancel Pending Requests, Unfollow and optional Followback Audit. Profile Counts control panel and Chrome robot moved from Insights to Automations; Insights now contains only results, aggregates, paginated 250-row presentation, charts and CSV exports.
- Large imported lists are transmitted in staged, account-scoped, atomic requests (1,000 per browser request / 2,000 server maximum). No global 50,000-profile imported queue cap; full imported list contributes to analytics. Action batch/rate limits remain independent of dataset cardinality. A shared Chrome admission lock prevents concurrent robots on the same session.
- Exact-head gates: Profile Counts #38655858892 PASS, Desktop #38655858890 PASS, Windows #38655858854 PASS, Android About #38655858876 PASS, CI #38655858859 PASS.
- Large historical Profile Counts persistence still uses localStorage; do not assert infinite storage. IndexedDB migration tracked in #96. Live account acceptance and physical device checks remain open.
- Official stable **v120.45** remains published; **v120.46 not authorized** for release. Publish only on a separate explicit owner instruction through the exact-commit gated pipeline.

## v120.45 stable published — October 14, 2026

- Official normal release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.45 ; exact release source `5c58aa5e836da014a86e1bdecad9a30e97013d8f`; successful governed publication https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38648558721 .
- Verified seven assets: integrated Windows `InstaCleanerPro.exe` ZIP, production-signed Android v120.45 APK, standalone Desktop HTML, secondary Desktop ZIP, product logo, privacy notice and SHA256SUMS. Exact-commit Windows EXE healthcheck, Desktop Chromium screenshots, Android emulator screenshots and release gates all passed.
- Owner's specific instruction "dale release" was consumed after confirmed publication; current stable v120.45. Next development version v120.46 has **no release authorization**.
- Windows Profile Counts now uses imported Following profiles by default, supports more than 11k profiles and makes Instagram Following discovery optional. Login identity detector recognizes Home Switch row. The owner's actual Chrome/Instagram end-to-end acceptance remains **unverified**; do not claim real Instagram actions or physical Android acceptance passed.
- Do not present GitHub PR artifacts as releases; always use official GitHub Releases for installation.

## v120.44 stable published, reconciled — October 14, 2026

- Official stable GitHub release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.44 ; exact source `90337e23b8bb91b3b2720f73a958c85cea152f77`; successful governed workflow https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38525933376 .
- Verified seven published files: production-signed Android v120.44 APK, Windows integrated `InstaCleanerPro.exe` ZIP, standalone Desktop HTML, optional Desktop ZIP, logo, privacy and SHA256SUMS. Exact-commit Android emulator/Chromium rendering, integrated Windows, CI and artifact validation passed.
- Owner's prior explicit authorization for v120.44 has been consumed (`authorized=false`, `status=published`). Current stable `v120.44`; development target `v120.45` is **not authorized for release**.
- English-only UI remains work in progress on PR #88, excluded from the v120.44 published binaries. Preserve legacy persisted Focus and audit identifiers during localization. Source-only tests must not be interpreted as physical Windows/Samsung/real signed-in Instagram acceptance.

## Release and delivery rule — owner clarification 2026-10-12

- Development proceeds on branches and PRs with automated tests and integration after validation, but **publishing a new GitHub Release requires an explicit instruction from the owner** (for example, "dale release"). Do not interpret "continúa" or "termina pendientes" as permission to publish.
- **Never present a PR build, GitHub Actions artifact, or temporary preview ZIP as the owner's normal download/install method.** When the owner authorizes a release, publish through the governed signed Windows/Desktop/Android GitHub Releases pipeline, verify the release exists and assets are complete, then share links to the actual release assets.
- The owner says **no one else has the app yet**. Do not assume a public user base until the owner explicitly says others have obtained it. Maintain compatibility and data protections nevertheless.
- Without a release instruction, report implementation/QA status and treat v120.44 as the currently published version. No pending or automatic release authorization should be created by this policy documentation change.

## v120.43 published — 2026-10-12

- Official normal release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.43
- Governed publication workflow https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38270817146 completed SUCCESS against exact source `469189095fa1e2f2308689c59d6e60eddec36868`; all seven files uploaded including Windows `InstaCleanerPro.exe` integrated ZIP, signed production Android APK, Desktop standalone HTML and checksums.
- v120.43 request consumed and next governed version reserved as v120.44; do not re-publish without separate explicit authorization.
- **Owner acceptance still open:** actual Instagram signed-in DOM, public/private action outcomes, Windows/Samsung session and local-vs-cloud transfer. No automatic Windows robot execution in Android; Profile Counts read on PC do not synchronize to Android automatically.
- Maintainer note: Windows robot is bundled in `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.43.zip`; do **not** tell users to open old `.cmd`.

## v120.43 release candidate — explicit owner authorization 2026-10-12

- Owner requested "Dales release" after integrated Windows/Android/Desktop automated QA. Prepare v120.43 only with the integrated Windows EXE and synchronized Desktop/Android version. A release commit must run exact-commit screenshot and signed APK checks; do not publish a mismatched old CMD robot ZIP.
- PR #82 on `feat/profile-counts-visible-controls-20261012`; Profile Counts partial Following fix and integrated Windows launch verified in CI. **Live Instagram owner/Windows/Samsung acceptance is still pending** and must be disclosed. Android does not run Playwright locally or auto-sync Windows counts.
- Release authorization is activated in a separate main-branch request after merging validated source and version metadata; do not mistake the branch preparation itself for a published release.

## v120.42 published — owner testing of automatic Instagram profile counts (2026-10-12)

- Stable [v120.42](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.42) is **published**, not queued; verified normal release run [38216103775](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38216103775) SUCCESS, commit `1c806e34e3f3b84c9311f466353a6ad30fe735c2`, all seven assets uploaded.
- **Windows robot ZIP** `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.42.zip`: extract, double-click `Start-Insta-Cleaner-Robot.cmd`, log in to Instagram in visible Chrome; automatic Following lookup/counter collection is implemented but **not tested with a real signed-in Instagram session**. Stop on session mismatch or challenge; collection may be partial.
- **Android signed APK** v120.42 retains production package/signature, and Desktop HTML v120.42 is included. Android does not run a local Playwright robot or automatically receive the new Windows counts. The owner's device/data acceptance is open; preserve history and per-owner/account separation.
- v120.42 release authorization consumed; next v120.43 is unapproved. The initial 38215091151 publish failed before uploading because of Windows artifact naming; subsequent release passed verified archive ZIP checks.

## Owner-verified sender + Switch account, eight-digit OTP copy correction — 2026-10-11

- Owner's Gmail screenshot visibly confirms sender **`Michel's Lab · IG Cleaner Pro <michelslab.dev@gmail.com>`**, no Brevo fallback. User reports successful numeric-code signup and working **Switch account**. OTP length in actual email is **eight digits** while template text says six, so avoid describing this as a six-digit production OTP. Do not commit or echo the pictured temporary code.
- Source templates for both Confirm sign up and Magic Link use length-agnostic **verification code** wording and CI verifies they cannot promise an unsupported code length. Live Supabase Auth templates must be re-saved with corresponding revised wording; source-only docs/test changes cannot modify hosted Auth SMTP/config. No new app release needed.
- Retain separate issue #73 for copy deployment, remaining recovery/expiry test; issue #24 for full multi-login workspace/data isolation and Android/Desktop sync. Stable release remains v120.41.

## Live OTP signup working after user-applied hosted configuration — 2026-10-11

- After saving Gmail SMTP in Supabase Auth and replacing Confirm sign up/Magic Link with code-only `{{ .Token }}` templates, user confirmed they **received the numeric OTP and successfully created a new IG Cleaner account**. Treat as real owner-reported live signup PASS for that attempt, rather than merely source-level testing.
- User actions were in provider dashboard; connector did not change/read sensitive SMTP settings or account data. Actual delivered `From` address, Inbox/Spam status, first-time flow on the second platform, recovery/resend/expiry and cross-user profile isolation still need acceptance; leave [issue #73](https://github.com/michels-lab/IG-Cleaner-Pro/issues/73) open for those checks.
- Installed app stable **v120.41** unchanged; no new APK, Desktop release or v120.42 authorization requested.

## Confirmed Michel's Lab sender identity — 2026-10-11

- User confirmed **`michelslab.dev@gmail.com`** is the ONLY current official Gmail mailbox. **No registered `michelslab.dev` domain.** Do not configure non-existent `no-reply@michelslab.dev`, and do not leave a personal `realmichelduarte` sender as the product's mail identity.
- Verified Brevo's official policy: free Gmail sender domains cannot be authenticated in Brevo, so Brevo rewrites the sender to a `@brevosend.com` / transactional provider domain; a branded display label cannot change this. If the actual From must remain `michelslab.dev@gmail.com`, a conditional low-volume option is Supabase's custom **Gmail SMTP** (`smtp.gmail.com:465`, exact sender+username Gmail, Google's dedicated app password after 2FA). App password entered by owner into Supabase UI only, never supplied to this chat or committed. Google warns against app passwords when OAuth is feasible, and personal Gmail is not a scalable transactional sender.
- See [docs/AUTH_EMAIL_SETUP.md](AUTH_EMAIL_SETUP.md). **No production SMTP or hosted OTP template has been edited**; owner must enable 2FA, create app password (if eligible), configure SMTP and paste two previously committed OTP templates. Keep issue #73 open until an actual end-to-end new-user delivery confirms six digits, branded *real* Gmail From, and no localhost redirect. v120.41 remains published; no v120.42 release instruction.

## Pending live Supabase Auth/Brevo mail configuration — 2026-10-11

- Screenshot confirms **user-visible signup P0**: IG Cleaner prompts for a numeric verification code, but default Supabase **Confirm sign up** sends a confirmation link redirected to `localhost:3000`; mail sender shows an unbranded Brevo fallback and Spam. Front-end code expects `/auth/v1/verify` `type=email`. Production email deliverability/confirmation is therefore not yet end-to-end verified.
- Working branch `fix/auth-email-six-digit-otp-branding-20261011`: versioned `supabase/email-templates/confirmation.html` and `magic_link.html` with `{{ .Token }}`, guarded CLI helper `tools/configure_auth_email_templates.py`, offline CI assertions and [operational setup guide](../docs/AUTH_EMAIL_SETUP.md). Do not claim this applies the templates to hosted Supabase.
- **Operational blocker:** connected Supabase API exposes DB/edge/project but no Auth config SMTP/template update; no Brevo integration available. Auth dashboard owner must paste both templates, verify remote config via management-token helper if available, choose real verified sender, and check Site URL; code-only OTP does not need localhost redirect. No backend user records should be migrated/deleted.
- Release: stable remains v120.41; source/docs update alone must not authorize or publish v120.42. Track real new-user email+password and sender tests before closeout.

## Official v120.41 stable release complete — 2026-10-11

- [GitHub v120.41](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.41) is published normal stable with all six expected assets; exact `main` publication SHA `1f711badcbc902e61beb7e382a49fe55f87fe9a1`, governed [workflow 38125964658](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38125964658) SUCCESS. Desktop standalone HTML (3,283,790 B), optional ZIP (1,401,875 B), and signed Android APK (7,879,580 B) carry matching v120.41 identity and persistent production certificate.
- Features: Desktop full Instagram names + independent cloud registry refresh (#67), Desktop/Android **Switch account** for the IG Cleaner login (#69); per-Instagram profiles and existing data remain scoped. Five exact release-commit CI checks green, embedded Android emulator + Desktop browser visual evidence verified; real Samsung and private-data two-login roundtrip still unverified #24.
- Release request consumed `authorized=false`, current stable v120.41, next target v120.42; no further release authorized without new user instruction. Do not mistake GitHub APK publication for Google Play.

## Account switch integrated on main — 2026-10-11

- [PR #69](https://github.com/michels-lab/IG-Cleaner-Pro/pull/69) merged at `f66f9489fa468c45def86f4ee6845a5df3f84113`. Desktop **Cambiar usuario** and Android **Switch account** appear beside Sign out and require a fresh login; original per-owner persisted Instagram workspaces/history kept. Desktop signed-out owner reload, serialized Android native logout/clear in-memory state, safe identity commit after successful Android password auth, stale WebView session isolation implemented.
- All five exact-head checks passed before merge, including Chromium real UI, emulator installed UI, Android build, Desktop behavioral contracts and RLS. Real owner/device switch remains to be exercised by Michel on his Samsung; do not describe CI as private-user acceptance.
- Release **paused** at existing v120.40. Next policy target v120.41 requires a fresh user release instruction; no current authorization.

## Account switching feature candidate (2026-10-11)

- Development branch `feat/switch-ig-cleaner-account-20261011` adds distinct **Switch account / Cambiar usuario** actions to Desktop and Android Account pages, independent from Instagram workspace selection. Switch invalidates credentials, clears only transient owner state, requests another IG Cleaner email/password, and preserves per-owner persisted data. Existing Sign out retained.
- Security hardening: native Auth owner changes only after a successful sign-in; Android embedded WebView must not reuse another owner's token or overwrite a new native login with a stale signed-out HTML initialization. Owner fingerprints follow native authority even when native email is empty.
- Testing: new Desktop VM behavioral/Android source contract in existing `tests/multi-instagram-contract.test.cjs`; exact-head CI and real Chromium/emulator must be checked for PR before merge. Live cross-device user acceptance still #24.
- **Publishing is explicitly paused:** v120.40 stable public; v120.41 governed next version has **no new authorization**. Do not publish or change version metadata without a fresh user request.

## Desktop profile list/full-name correction complete in source (2026-10-11)

- [PR #67](https://github.com/michels-lab/IG-Cleaner-Pro/pull/67) merged at `6a7049702f284c2cae378d7aaecff31f5f3a0a80`; **all five exact-head checks passed** on `1a476fdbb1b6d85497d332086ae2d7ad2bb00421`, including actual compact/wide Chromium screenshots and native Android emulator.
- New full-wrap active Instagram identity, reserved full-width select, separated text-labeled actions, independent **Actualizar perfiles**, explicit auth/cloud-error warnings and count. Responsive compact horizontal rail no longer shrinks to zero. Fixes user screenshot of truncated “Dat” and provides diagnosis when only cached Datos anteriores appears.
- **Not released:** v120.40 APK/HTML remains stable and unchanged. The source fix is included in the next v120.41 candidate and requires explicit synchronized Desktop+Android release authorization. No real profile data modified. User should use the same IG Cleaner account email on both devices when loading the cloud registry; real signed-in Desktop results are still to be checked.

## Desktop profile switcher audit (2026-10-11) — correction in progress, not yet shipped

- **User evidence:** screenshot of Desktop v120.40 shows only “Datos anteriores” and severely truncated selector text (“Dat”) in the left rail; user reports Android seems correct. Production cloud previously showed a legacy identity plus an unassigned second named workspace, with original list/review history intact.
- **Root cause verified in source:** the Desktop picker initially renders only the locally cached registry (`legacy` fallback). The full cloud registry is fetched solely as a phase of the optional/session-dependent full sync; when the browser is signed out or the query fails, the rail quietly remains a one-profile list. Existing styling puts the `select` in the same flex row as four action buttons, squeezing it to a couple of letters.
- **Source candidate:** display the **entire selected @handle** in a dedicated, wrap-safe “PERFIL ACTIVO” block, reserve a 100%-width row for the `select`, move clear-text Add/Edit/Backup/Delete buttons to a separate two-column grid, and provide independent `⟳ Actualizar perfiles`. Initial signed-out/failed cloud states are explicit next to the picker with a prompt to log in under **Cuenta**, not silently represented as a complete profile list. Refresh queries `instagram_accounts` and owner-filtered summary through the current authenticated IG Cleaner session and displays the resulting profile count.
- **Safety:** no changes to cloud identities, Supabase tables, local state keys, Android Java, or signing. Existing account scoping, historical legacy and Android session handling remain untouched. Regression tests assert non-truncation with long usernames, compact and wide browser geometry, and visible session status; source contracts guard remote refresh and cache isolation. UI tests use isolated fixtures (no real user account).
- **Pending:** exact-head GitHub CI (Desktop contract/Chromium and Android embedded assets), merge after all required checks; synchronized Desktop/Android v120.41 release **requires new explicit authorization**, since current stable v120.40 was already published. Post-release physical PC sign-in with same email as Android and two-account proof are still needed.

## Published release — v120.40 (2026-10-11)

- **Status: shipped** as the stable [GitHub release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.40); workflow [38119945272](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38119945272) SUCCESS, exact published source `7ec454cbc5852bb8e96b9bd7ff59830b5872bb5a`, signed normal Android package and standalone Desktop HTML with identical version plus ZIP and checksums; no prerelease.
- Android APK SHA-256 `1b107ba0ed05a8b83f54a96c03fcc069c2b243ee4f6a647b0ed7ea867b2744db`; standalone HTML SHA-256 `da49a4df6b0e9585ab43cdfe6dbf093a22c4943380c4a82199c44242812004d4`. Certificate continuity verified in governed publisher; exact-commit emulator and Chromium screenshots verified.
- Contains #58 selector fix, #59 confirmed removal, #61 metadata-only duplicate handle recovery, smart account addition, editable Instagram names, owner-scoped counts and single-profile JSON backups. Live Supabase RPCs already deployed. **No user cloud data changed by release.**
- **Open:** Samsung real-install/session and genuine two ZIPs plus sync acceptance [#24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24); user-instance recovery scenario [#57](https://github.com/michels-lab/IG-Cleaner-Pro/issues/57). Auth sync backup JSON is not a native one-click restore file. Next stable v120.41 requires new user authorization.

## 2026-10-11 — Profile management complete in main; v120.40 app release still pending

- [PR #61](https://github.com/michels-lab/IG-Cleaner-Pro/pull/61) merged to `main` at `01235bfbfe1ab2f7f5c582e08571d18c995ba256` after **five exact-head CI checks succeeded** on `ddbfeda1dfbebdbe6e81349a4b8208e058e3fff9`: Desktop source contract, rendered Chromium, Android build, installed Android emulator compact/wide rendering, and **99 PostgreSQL RLS/behavior assertions**.
- **Desktop + Android:** smart add asks whether to use original **Datos anteriores** or a genuinely new empty profile; change a profile's @username; explicitly transfer a conflicting @username back to `legacy` without moving/deleting either profile's histories, lists or keys. Conflicting named profile stays accessible with "Sin asignar" label. Stale competing changes are rejected. Named and legacy snapshots/report counts (Following, Followers, Pending, reviews, last snapshot) load using one owner-scoped database summary function. Standalone cloud JSON backup for the selected profile, offered ahead of deletion, including orphaned/unnamed profiles.
- **Live Supabase:** migration `instagram_profile_identity_recovery_and_summaries_v1` successfully applied. `igc_set_instagram_username` and `igc_instagram_profile_summaries` are both **SECURITY INVOKER**, execute only for `authenticated` (not `anon`). Production legacy cloud records did not change: 3 original list snapshots containing 33,927 list items, 7,764 historical review-state rows, two account registry rows. No real account rename, reassignment, deletion or import executed.
- **App publication:** Published release is **v120.39**. `v120.40` is still unpublished and must ship signed Android and standalone HTML together after explicit user release instruction. Real Samsung + authentic ZIP multi-account and sync acceptance remains open [#24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24). The reported duplicate-value bug is **fixed in merged source** but not in installed v120.39; retain [#57](https://github.com/michels-lab/IG-Cleaner-Pro/issues/57) open until release/acceptance verifies the recovery UI. Exports include synchronized cloud records only; local unsynced data and original Instagram ZIP must be backed up independently. Export is not yet a one-click restore format.

## Profile deletion integrated, SQL live — 2026-10-10 Mexico (unreleased app UI)

- [PR #59](https://github.com/michels-lab/IG-Cleaner-Pro/pull/59) merged at `428c828a614db6a03901a8b4ba61a7ddf0bc1d8a`. Desktop offers × next to INSTAGRAM, Android Profile offers “Eliminar Instagram seleccionado” for named workspaces; original legacy remains protected. Requires typed confirmation.
- **All exact-head gates passed:** Desktop local contract; 78 Supabase pgTAP RLS assertions; Android Gradle build; real Desktop Chromium visual Home/About; installed Android API35 compact/wide instrumented visual test. Source QA commit `fd656bc87149e0be37a8f471827d6e477ac5dd0b`.
- **Production migration successfully deployed** in `ig-cleaner-sync`: `atomic_named_instagram_profile_deletion_v1`, `public.igc_delete_instagram_profile(text,text)`. Verified `security_definer=false`, authenticated EXECUTE=true, anon EXECUTE=false. Legacy cloud snapshots unchanged: 3 rows / 33,927 list items; 7,764 review-state rows, 2 existing Instagram workspace registry rows and 0 new-profile list rows — no user data deleted during deployment.
- **Published stable remains v120.39**. App UI/source fix and delete feature are staged for **v120.40**, requiring explicit release authorization for synchronized signed Android APK + standalone Desktop HTML. No release requested or published in this closeout. Actual user's phone and real multi-ZIP acceptance remain open in #24. The duplicate @username registration UX still requires direct correction (#57); deletion of a mistaken empty profile is manual, never automatic.
- Unrelated Supabase Auth advisory: Leaked Password Protection remains disabled ([security setup](https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection)); no change to Auth settings in this feature.

## Candidate — Remove named Instagram profile safely (2026-10-10; not yet released)

- User requested ability to delete extra Instagram profiles after accidentally registering original @handle as a blank new workspace. Add an explicit destructive control in Desktop INSTAGRAM and Android Profile while making **Datos anteriores (legacy)** non-deletable.
- New additive SQL migration `supabase/migrations/20261010_delete_instagram_profiles.sql` defines a transactional, caller-RLS-scoped RPC requiring exact owner+profile key+current handle; child Focus/history/list/review rows removed first, then account registry. Cannot change original v120.38 tables. Both clients require typed confirmation and switch to legacy on successful deletion. Local namespaced state purged only for deleted key, including remote deletion reconciliation in Desktop/WebView.
- `supabase/schema.sql` updated for fresh installs, and pgTAP/Node tests extended. CI and visual/Android emulator evidence required before merge. Production additive function deployment must be verified before authorizing v120.40 Desktop+Android publication.
- Previously merged [PR #58](https://github.com/michels-lab/IG-Cleaner-Pro/pull/58) fixes Android picker showing only button labels; user data was verified present in legacy Supabase records. Existing published **v120.39 lacks both fixes**.
- Preserve source-label collision in [issue #57](https://github.com/michels-lab/IG-Cleaner-Pro/issues/57) until it has a distinct non-destructive identity reassignment UX; deleting an empty mistakenly created profile is an opt-in workaround, never automatic.

## Candidate fix — Android selector did not display legacy row (2026-10-10, unreleased)

- User confirmed that the native “Perfiles de Instagram” dialog shows “Asignar datos anteriores” but **not** the “Datos anteriores (sin asignar)” row. `MainActivity.showInstagramProfileManager()` combined Material `setMessage` and `setItems`; the message suppresses the list.
- Source-only correction on a branch removes `setMessage`, leaves `legacy` first and both profile identities intact, and adds a test regression to the existing multi-profile suite. No data is migrated, deleted, renamed, or automatically merged.
- Remains **unpublished** until automated Android installed/emulator acceptance and a separate user release instruction. In released v120.39, Desktop INSTAGRAM selector still permits switching to legacy, provided the saved data is in that installation or synced to the same account.
- Distinct @username collision bug tracked in issue #57. Do not delete either account and do not clear Android app storage during recovery.

## Current release — v120.39 stable published and verified (2026-10-10 Mexico / 2026-10-11 UTC)

- **Published GitHub stable** [v120.39](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.39) on 2026-10-11T04:51:14Z; `draft=false`, `prerelease=false`, `latest=v120.39`. Exact publication commit `4170696589c22dc669deac10ca1a0ceddd88bfea` and governed publisher run [38112617481](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38112617481) **SUCCESS**, including verified release assets.
- **Downloads:** `IG-Cleaner-Pro-Android-v120.39.apk` (7,863,819 bytes; normal package `com.michelslab.igcleaner`, versionCode 12039, original FINAL-9999 signing certificate); `IG-Cleaner-Pro-Desktop-v120.39.html` (3,267,531 bytes, standalone offline); optional `IG-Cleaner-Pro-Desktop-v120.39.zip` (1,397,171 bytes), logo, Privacy and SHA256SUMS.
- **Delivery content:** PRs #50/#53/#54 multi-Instagram workspaces, owner+profile isolation and Desktop text bug fix alongside prior released native Focus/Double Check. PR #55 merged as `ffe09d14d887d501b73cd2f95bed3af7532acd84` after exact-head five checks PASS (Desktop contract, Supabase RLS, Android build, actual Android emulator, real Desktop Chromium). Release publisher then passed the exact-publication-commit visual, signing and artifact gates. Production additive migration was already deployed with legacy data unchanged.
- **Governance:** publication authorization consumed after verifying the release, manifest stable moved to v120.39 and next governed target v120.40. Next publication requires new explicit user instruction; no republish of v120.39 from post-release documentation changes.
- **Still open, not a publication gate:** user Samsung over-the-top update, authentic Instagram ZIP import for multiple profiles, Focus/review and authenticated Android↔Desktop cloud roundtrip, user post-release visual review. Track issue #24. The prior candidate and v120.38 records below are historical, not current status.

## v120.39 release candidate — multiple Instagram workspaces (2026-10-10)

- User asked to proceed after the v120.39 release proposal. Candidate branch `release/ig-cleaner-v120.39-multiinstagram-20261010` aligns Desktop UI/About v120.39 and Android native 120.39 (versionCode 12039) with the unchanged stable production certificate. No destructive storage changes; published v120.38 remains the current public download until verification.
- Included already-merged PRs #50/#53/#54: owner+Instagram profile isolation, real Desktop Chromium switch regression, Android Profile/header switcher, additive deployed Supabase RLS schema, legacy compatibility and literal visible `\\n\\n` fix. Preserves native Focus/Double Check released in v120.38.
- Required gates: candidate exact-SHA general CI, Android installed emulator and Desktop Chromium; after successful merge, one-shot authorized `.michelslab/release-request.json` change on main triggers the existing governed publisher, which itself requires new exact-SHA visual proof and verifies signed APK. Do not treat candidate as released.
- Physical Samsung APK upgrade, authentic two Instagram ZIPs, actual live desktop↔Android sync and final user visual acceptance still pending in issue #24; review is post-publication.

## Latest: multiple Instagram profiles complete in main (2026-10-10)

- Main code: first implementation [PR #50](https://github.com/michels-lab/IG-Cleaner-Pro/pull/50) and final per-login isolation [PR #53](https://github.com/michels-lab/IG-Cleaner-Pro/pull/53), merged at `83d8273568cc3625766145cfff86e0d171a7025f`.
- All exact-head checks PASS: CI `38108180395` (including 60 Supabase pgTAP assertions), Android installed emulator `38108180430`, Desktop real Chromium `38108180542`. Chromium tested switching between two named Instagram workspaces, restoring original review state, and hiding another app login's account registry. Verified no visible `\\n\\n` text above Desktop shell.
- Production Supabase `ig-cleaner-sync` already has the additive migration, all 7 new tables RLS-protected; legacy data unchanged. **No release published**: v120.38 remains the latest downloadable; new code awaits explicit authorization of v120.39. Physical Samsung, authentic ZIP from both Instagram profiles and authenticated Desktop↔Android cross-device data roundtrip remain pending.

## Multi-Instagram data workspaces integrated (PR #50, 2026-10-10)

- **In main, but not in a published APK/HTML yet.** PR #50 merged as `66f43cb38b3f0a046a819d196b6859dd04a521a1`. Live Supabase `ig-cleaner-sync` additive migration `multi_instagram_workspace_isolation_v1` applied; 7 new RLS-protected tables, 7 composite primary keys and original 3 list-snapshot rows preserved.
- Exact-head QA PASS: CI `38105541087` (60 pgTAP assertions), Android emulator `38105541099`, Desktop Chromium `38105541095`. Android has Profile and persistent header Instagram switcher; Desktop stray literal `\\n\\n` rendered above the sidebar fixed at source, with real Chromium regression assertion.
- **Stable download remains v120.38**, next permitted version v120.39 only on explicit user request. Physical device/account ZIP and authenticated two-Instagram Desktop↔Android acceptance remain open.

## Historical multi-Instagram development candidate (PR #50)

- **Status: code candidate; not merged, not released, not yet deployed to production Supabase.** https://github.com/michels-lab/IG-Cleaner-Pro/pull/50
- Additive `instagram_accounts` registry + six per-IG tables with composite PK/RLS; old stable v120.38 tables and keys preserved as `legacy`. Desktop localStorage and IndexedDB namespace nonlegacy profiles; native Android picker scopes queries and cache. Normal one-account Auth credentials remain shared.
- New user export and review data must never silently overwrite another Instagram. Full local backup now records account_key and rejects mismatched import; ZIP import confirms target profile. Account-wide cloud export and deletion include old and new profile tables.
- QA required before merge: 60 Supabase RLS assertions and additive migration test, Desktop source+real Chromium and Android build+8 emulator instrumentation tests at compact/wide. No live-user Supabase migration yet; evaluate after candidate is valid.
- Original v120.38 release remains untouched; any v120.39 release requires explicit user authorization. Product contract: [docs/MULTI_INSTAGRAM_WORKSPACES.md](MULTI_INSTAGRAM_WORKSPACES.md).

## Current shipped version — v120.38 (published, verified; 2026-10-09)

- **Stable GitHub Release:** https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.38 — published 2026-10-10T00:47:55Z, `draft=false`, `prerelease=false`. Exact release commit `589d67230e62a7f1ad2cf21bc75a5348bcf4b93a`; publisher run https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38010213161 finished **SUCCESS**.
- **Published assets verified uploaded:** signed production `IG-Cleaner-Pro-Android-v120.38.apk` (7,855,994 bytes); primary offline `IG-Cleaner-Pro-Desktop-v120.38.html` (3,254,813 bytes); optional `IG-Cleaner-Pro-Desktop-v120.38.zip` (1,393,218 bytes); logo PNG, PRIVACY.md, and SHA256SUMS.txt.
- **Exact-commit required evidence PASSED:** Android real installed API35 emulator compact/wide Home/About `38010213267`, Desktop Chromium real compact/wide Home/About `38010213135`, full CI `38010213180` including Android build and 41 Supabase RLS tests, publisher real production keystore/signing and asset checks `38010213161`. Package `com.michelslab.igcleaner` `versionCode=12038` `versionName=120.38`, unchanged FINAL-9999 certificate SHA-256.
- Feature content: native Android Focus shows full relationship dates/history; Double Check 30 uses Desktop/Android shared cycle; latest activity per section; HTML partial-coverage safety and refreshed active batches. Desktop stays on the same v120.38.
- Manifest and consumed release-request closeout target **v120.39** next. No v120.39 authorization. **Do not republish v120.38** from a docs-only closeout change; governed release gate remains disabled.
- **Post-release physical acceptance** issue #24: Samsung installed/update identity, user's real Instagram export/Focus and authenticated Desktop ↔ Android roundtrip still unverified by automation. No Google Play publishing implied.

# Current Handoff — Instagram Cleaner Pro

## Archived v120.38 publication candidate — 2026-10-09 (superseded by published release above)

- User explicitly requested release. `release/ig-cleaner-v120.38-candidate-20261009` aligns native Android + Desktop runtime version 120.38 and original production signing metadata; release notes and version contracts updated.
- The manifest still records v120.37 as current until **actual GitHub v120.38 publication verification**; its nextRelease is v120.38. The publication authorization is staged separately after merging tested candidate, to trigger exact-commit Android and Desktop visual runners plus the generic governed publisher. Do not bypass release CI.
- Required deliverables: stable signed `IG-Cleaner-Pro-Android-v120.38.apk`, primary offline `IG-Cleaner-Pro-Desktop-v120.38.html`, optional `IG-Cleaner-Pro-Desktop-v120.38.zip`, privacy/logo/checksums. Keep production cert identical to v120.37. No Google Play publishing implied.
- Pending: exact release-candidate CI, publication and post-publication metadata closeout. User's real Samsung and genuine sync/ZIP acceptance remains separately open in #24.


## Archived pre-release Android Focus parity — 2026-10-09

- **PR #42 merged** at `9447ae29bb7fe758f7791c0a7be23ebd9fc28841` after exact-head all-green CI `38008299846`, Desktop real Chromium `38008299836`, Android installed emulator `38008299843` (5 tests at compact+wide; nonblank APK-bound screenshots, artifact `11652775546`). PostgreSQL RLS suite passed **41** assertions, including Desktop/Android account-scoped Double Check read/write and isolation.
- Status: code in `main`, **not shipped**. Stable v120.37 unchanged; v120.38 is **not authorized**. Do not claim genuine Instagram ZIP or live Samsung cloud sync tested until user acceptance.
- On Android, Focus shows follow/follower exact+relative dates, sequence, last review/decision/history; Double Check 30 rotates usernames across PC/phone with explicit confirmation separate from open; last section batches include Desktop audit-only history; partial-HTML uncertainty is enforced across platforms; Sync refreshes active Focus details.

## Historical development handoff — 2026-10-09

- Integrated branch `feat/android-focus-rich-context-double-check-history-20261009` adds full synced follow dates/review history to native Focus, Double Check 30 without repeating profiles across Desktop/Android, last batch by module including Desktop audit-only legacy Double Check events, and per-cycle progress.
- Reuses existing Supabase `workspace_state` table with independent state_key `focus_double_check_cycle`; no SQL schema changes, no destructive state changes, no automatic release. Test instrumented phone dimensions and real cloud roundtrip after source QA. Existing v120.37 remains stable.
- Desktop sync's Double Check epoch and seen-set must stay interoperable; native opened is not reviewed until explicit batch finish. Preserve original exported follow dates, report missing as unknown.

## Historical shipped version — v120.37 (superseded; not current stable)

- **Normal GitHub stable release:** https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.37 — published 2026-10-08T22:12:02Z; `draft=false` and `prerelease=false`.
- **Matched releases:** signed production Android `IG-Cleaner-Pro-Android-v120.37.apk`, offline standalone Desktop `IG-Cleaner-Pro-Desktop-v120.37.html`, optional full Desktop `IG-Cleaner-Pro-Desktop-v120.37.zip`, product logo, privacy notice and `SHA256SUMS.txt`.
- **Production signing:** original FINAL-9999 cert SHA-256 `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33` verified with Android v2/v3 signatures; unchanged stable package `com.michelslab.igcleaner`.
- **Released exact commit:** `15177fee95358a891619266dc90a523d13b8aaef`; publisher run https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37851259478 — all gates `release-request-gate`, `rendered-ui-qa`, `publish` **SUCCESS**.
- **Accepted corrected About code:** PR #39 and version candidate PR #40 merged before publication. App/Michel's Lab logos side by side at top, developer info below, large portrait + vertical social links; Android native persistent About and Sync, no unused Advanced tools; Desktop permanent About in top command bar.
- **Automated verification:** actual installed Android emulator compact/wide Home/About; Desktop Chromium Home/About; product branding, signed Android package, standalone HTML, Supabase CI. **Samsung physical update, genuine Instagram ZIP and live authenticated Desktop↔Android sync are still pending post-release acceptance** in issue #24, not claimed as passed.
- **Next governed candidate:** v120.38, **not authorized**. Do not publish or rebuild v120.37 from a new commit. Earlier handoff content is historical and must not override this heading.


## v120.37 release candidate — user authorized after fixes

- User requested v120.37 release after finishing pending UI bugs. PR #39 is merged into main (commit `ab02b0d2db9923ad8cb79bb88e1ce669f34c3050`) following actual native Android UI and Desktop Chromium screenshot proof. New candidate bumps Android/Desktop 120.37 and signing metadata but does not change state schema. Run same-SHA QA again on main; only then authorize/publish normal signed APK and primary standalone HTML. Keep v120.36 as current stable until GitHub confirms v120.37.



## Current shipped version — v120.36 (released)

- **Latest PR #39 unresolved test corrected in candidate:** Android `37849453228` proved actual About content layout passes but showed *About is not visible in Home toolbar*. Removed entire adaptive menu; explicit fixed header About and Sync buttons wired directly. Must rerun installed-app visual QA on latest SHA before merge. User authorized v120.37 **after finishing pending fixes**, not as permission to bypass UI gates.

- **QA finding for unreleased About correction:** candidate's first Android UI runner `37833416640` failed on API-35 UIAutomator window text lookup (both About full name AND Home app title missing to the accessibility locator). Main CI and Desktop Chromium passed. Candidate test now uses native dialog + actual on-screen geometry/drawables; rerun required. No merge/release claim until exact latest SHA's screenshots succeed.

- **UI correction in development (unreleased):** user's October 8 screenshot rejected the v120.36 About hierarchy. Requirements: official app and studio logos paired at top, developer information below, large canonical portrait with one vertical list of five icons+names beside it, visible About in permanent top bar, and removal of useless Android Advanced tools menu/handler. Candidate branch `docs/v12036-post-release-triage-20261008`, not a release. Do not report candidate fixed until real Android/Chromium UI tests pass; no v120.37 authorization.

- **Published normal GitHub release:** https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.36 (2026-10-08T19:00:43Z).
- **Signed Android:** `IG-Cleaner-Pro-Android-v120.36.apk`; **Desktop:** `IG-Cleaner-Pro-Desktop-v120.36.zip`; original chosen app logo, release artwork and SHA256SUMS included.
- **Published commit:** `335cc84a3c5a823314f5283d3543a9fdf58174d3`; publish run: https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37827876157 — SUCCESS. Real Android Home+About and Desktop Chromium Home+About screenshot quality gates PASS, Android signing certificate identity PASS and release asset checks PASS. Premium native + Desktop navy/cyan/gold design and About improvements integrated.

- **Post-release support / exact download:** GitHub v120.36 now includes the primary standalone `IG-Cleaner-Pro-Desktop-v120.36.html` in addition to ZIP; this was backfilled without rebuilding or re-signing the Android APK. The public README and live issue queue have been reconciled with this shipped state.
- **P1 historical QA and logo items:** #28 and #30 are now satisfied by merged v120.36 exact-original-logo assets and enforced Android/Chromium Home+About screenshot gates. Close with implementation evidence rather than treating stale original checkboxes as incomplete. The historical instruction for protected human review has been superseded by the user's explicit post-release review policy.
- **Outstanding non-automated acceptance:** issue #24 is re-targeted to v120.36; install/update on actual Samsung, genuine Instagram ZIP and Focus behavior, and real Supabase account Desktop↔Android sync remain outstanding. Do not mistake this for a pre-publication gate; GitHub release already exists. No v120.37 authorization.

- **Next version:** v120.37 is NOT authorized. User review of the actual release on their Samsung and actual Instagram ZIP/Focus/cloud cross-device roundtrip are still outstanding, not represented as PASS.
- Historical handoff notes below may describe v120.35 or pre-release stages; the shipped-state facts in this heading take precedence.

Updated: 2026-10-08; trigger: LIMÓN.

## v120.36 — approved logo and visual QA candidate

- User expressly instructed **correct remaining problems and release v120.36**. Preparing from PR #35; do not claim a release until Github Releases contains signed APK + Desktop ZIP and all checks pass.
- PR #29 fixed the Android About zero-width author/studio panel. PR #31 redesigned compact About to keep both identities + five social links completely visible; real emulator screenshot test rejected a 70%-visible Email button and passed after correction.
- PR #32 removed the pre-release human reviewer bottleneck as explicitly requested, retaining fail-closed automatic QA. PR #33 prepared Android/Desktop v120.36 version.
- PR #35 imports the **exact original** 1,559,781-byte first chosen profile-card/cyan-orbit/gold-sparkle PNG into IG Cleaner and adds derived lossless launcher/Desktop/release assets. Same original is activated in the Michel's Lab master manifest through PR #30.
- Android **Home and About** now have actual installed-app compact/wide screenshots with APK and source SHA. Desktop **Home and About** have actual Chromium compact/wide screenshots, native asset checks and exact HTML hash. Governed publisher verifies both on exact release-request source SHA.
- Keep production signing identity FINAL-9999 and stable package `com.michelslab.igcleaner`. Do not silently re-key or change app ID.
- Remaining **physical phone** validation of update-over-old-signed-release, Focus, Instagram export ZIP import and live cloud sync is [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24), distinct from CI.
- Public stable was v120.35 before this release work; next release target is v120.36. After publication reconcile release manifest and consume authorization, then append final job and asset proof. Never infer that GitHub release succeeded just because CI did.
- Permanent source log: `PROJECT_LOG.md`. Last published signed cert SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`.

## Historic handoff archive

# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-08**
Trigger: **LIMÓN**

## v120.36 ready in main — not yet published

- **Current main HEAD:** `b99b2357295d124fa783fa555f9793e87028899a`; Android `versionName=120.36`, `versionCode=12036`; matching Desktop development version and unchanged FINAL-9999 certificate.
- **PR #29 (merged):** fixed zero-width native Android About author/Michel's Lab panels; implemented installed-APK Espresso actual-view and screenshot tests.
- **PR #31 (merged):** redesigned compact About as two side-by-side identity sections and five contact links in two columns. A strict complete-visibility assertion rejected clipped Email (70% visible); after correction, **both compact and wide emulator tests passed**. Actual screenshot archive: [About v120.36 visual QA](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37808417135). All five contact links are visible in the initial compact screenshot.
- **PR #32 (merged):** release publishing requires **automated** exact-commit `rendered-ui-qa` and APK screenshot integrity checks. No manual/protected human-review queue is required, consistent with the user's instruction to inspect the finished release afterward.
- **PR #33 (merged):** Android and Desktop dev version, signing metadata and release notes prepared for v120.36. [Desktop/Android/Supabase CI](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37810464858) and [Android emulator About QA](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37810464913) are both **SUCCESS**.
- **Current public stable:** v120.35. **Next governed publication candidate:** v120.36, `authorized=false`; no release requested or published as part of these PRs.
- **Remaining:** exact original Option 1 logo PNG not yet uploaded to master; approved 64px preview is not suitable as official production asset ([issue #30](https://github.com/michels-lab/IG-Cleaner-Pro/issues/30)). Real Samsung upgrade/Focus/import/cloud roundtrip acceptance remains [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24); broader Home/Desktop screenshot coverage remains [issue #28](https://github.com/michels-lab/IG-Cleaner-Pro/issues/28).
- Do not claim logo migration, physical-phone validation or GitHub v120.36 release as done until evidence exists.

## Current authoritative release state

- Published stable GitHub Release: **v120.35**, non-prerelease; five assets (signed Android APK, Desktop ZIP, logo, Privacy, SHA256SUMS).
- Publisher run: **37737077156 — SUCCESS** on commit `0e4b0c3d5b803436fd453c23e51dce1505871d8a`.
- FINAL-9999 Android signing continuity verified; package `com.michelslab.igcleaner`, versionCode `12035`, versionName `120.35`.
- Generic publisher: `.github/workflows/release.yml`.
- Release authorization was consumed and closed in governance; next governed release target: **v120.36**, not yet authorized.
- v120.35 implementation merged to `main` via PR #20 and responsive About finalization via PR #23.
- Physical-phone acceptance remains open as [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24). GitHub release is published; this does not constitute Google Play publication or physical-device validation.
- Development and publication state must be independently checked against the manifest, current main SHA, current CI and GitHub Releases.

---

## Historical handoff (2026-10-07; preserved for audit)


Updated: **2026-10-07**
Trigger: **LIMÓN**

## Current stable release

- Published stable: **v120.34**
- GitHub prerelease: **false**
- Signed Android + Desktop artifacts are attached to the same release.
- Final v120.34 publisher: **37574744462 — SUCCESS**
- Stable production signer: FINAL-9999
  - package: `com.michelslab.igcleaner`
  - alias: `ig-cleaner-pro`
  - SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
  - valid through: **9999-12-31**

v120.34 is closed. Its consumed release authorization must not be reused.

## Active development

Branch: `development/v120.35-infra-privacy`  
Development version: **v120.35**  
Next governed release target: **v120.35**

v120.35 keeps the v120.34 functional baseline and adds infrastructure/privacy hardening without changing the raw Instagram import boundary.

### Generic governed release publisher

New canonical future publisher:
- `.github/workflows/release.yml`

It is version-agnostic and resolves:
- version/tag from `.michelslab/release-request.json`;
- artifact names from `release/distribution-manifest.json` templates;
- Android version from Gradle;
- the persistent FINAL-9999 signing identity from `release/android-signing.json`.

It refuses to publish unless:
- the request is explicitly authorized;
- request status is publishable;
- the requested tag equals `releasePolicy.nextRelease`;
- channel is stable and GitHub prerelease is false;
- Desktop visible version and Android version match the request;
- release regression contracts pass;
- the production signer fingerprint matches;
- the stable APK package/version checks pass.

The old `.github/workflows/release-v12034.yml` is now a harmless retired stub; it cannot publish anything.

### Automated Supabase RLS isolation

New test:
- `supabase/tests/rls_isolation.sql`

Coverage:
- all seven synchronized tables have RLS enabled;
- user 1 can see only user 1 rows;
- user 2 cannot update user 1 rows;
- user 2 cannot delete user 1 rows;
- user 2 can insert rows owned by user 2.

CI job:
- starts a local Supabase stack;
- applies `supabase/schema.sql`;
- executes the pgTAP suite through `supabase test db`;
- uses 35 assertions.

A transactional production smoke check also confirmed the live project isolates temporary rows by authenticated JWT subject. Temporary rows were rolled back.

### RLS policy optimization

The seven live policy sets were migrated from row-by-row `auth.uid()` evaluation to explicit `TO authenticated` policies using `(select auth.uid()) = user_id`. This preserves ownership semantics while avoiding repeated auth-function evaluation. Supabase Performance Advisor dropped from **28 Auth RLS Initialization Plan warnings** to **0** after the migration. The only remaining performance notice is an informational unused-index hint for `audit_events_user_device_idx`.

### Synchronized-data privacy controls

Desktop Privacy now includes:
- **Exportar datos de nube**
- **Borrar datos de nube**

Android Account now includes:
- **Export synchronized cloud data**
- **Delete synchronized cloud data**

Cloud export:
- requires authentication;
- paginates all seven RLS-visible synchronized tables;
- writes schema `ig-cleaner-cloud-export-v1`;
- excludes the original Instagram ZIP/JSON/HTML export.

Cloud delete:
- requires explicit confirmation;
- deletes only RLS-visible synchronized rows;
- deletes Focus items before batches;
- leaves the original Instagram export and independent local backups untouched;
- signs out afterward so automatic sync cannot immediately repopulate the cloud from local state.

## v120.35 version identity

Desktop visible UI: **v120.35**  
Android:
- package: `com.michelslab.igcleaner`
- versionCode: `12035`
- versionName: `120.35`

Debug remains isolated with the `.beta` application ID suffix.

The Desktop filename remains `ig_cleaner_pro_v120_27_synced_companion.html` intentionally because it is a stable packaging/state integration path, not the visible product version.

## Functional baseline preserved

Do not regress:
- Review = Following only;
- separate Mutuals / Followers-you-don't-follow / Pending workspaces;
- Focus 20 / 30 / 40;
- Revisar de nuevo 30;
- Double Check 30;
- Ver NO ME SIGUE revisados;
- cycle-reset controls;
- active batch recovery;
- module-scoped recent activity/sidebars;
- complete ZIP primary import;
- JSON/HTML evidence safeguards;
- Desktop ↔ Android normalized list/workspace/profile sync;
- Android-created Focus;
- Android system-bar inset handling;
- canonical Michel's Lab / IG Cleaner branding.

## Evidence still requiring a physical phone

Repository/CI can prove code, build, package, RLS and signing contracts. It cannot replace these target-phone checks:
- install/update signed v120.35 APK when released;
- cold launch;
- close/reopen session persistence;
- real Instagram ZIP chooser/import;
- Focus 20/30/40 with real usernames;
- batch recovery/completion;
- Android review → Desktop state round trip;
- cloud JSON export appearing in Downloads;
- cloud-delete confirmation UX and post-delete sign-out;
- Samsung system navigation/insets.

## Release rule

Do **not** publish v120.35 until Michel explicitly authorizes a release. Development/merge approval is not release authorization.


## Current validation blocker

PR **#20** remains open, mergeable and intentionally Draft.

GitHub Actions run **37702842845** on head `e5a49aa55053599636a7c55d91df7b39df7207b9`, triggered by marking PR #20 Ready for review, created all three jobs and terminated them before any runner step or log existed:
- Desktop local-app contract — pre-run failure;
- Android build + embedded Workspace — pre-run failure;
- Supabase RLS isolation — pre-run failure.

Every failed job reports `steps: []` and no log blob exists, so this is not evidence of an application/test assertion failure. GitHub's public status page reports Actions operational after today's service incidents, but the repository runner-start failure remains unresolved and its exact account/platform cause is not exposed through the available connector APIs. PR #20 was returned to Draft immediately after this probe. Draft PR jobs are now server-side skipped, preventing further runner/minute waste until the gate is intentionally retried.

Direct evidence on the exact current branch:
- Desktop inline JavaScript syntax: **16/16 PASS**;
- duplicate static DOM IDs: **0**;
- v120.35/version/privacy/release/RLS static sweep: **PASS**;
- corrected targeted governance/privacy/RLS sweep: **11/11 PASS**;
- Android Java/Gradle delimiter structure: PASS;
- modified Android XML structure: PASS;
- live Supabase optimized RLS migration: APPLIED;
- live two-user RLS sweep across all seven synchronized tables:
  - each user sees only **1 own row** per seeded table;
  - foreign UPDATE affected **0 rows** on all seven tables;
  - foreign DELETE affected **0 rows** on all seven tables;
  - own authenticated INSERT succeeded;
  - test transaction rolled back;
- Supabase Security Advisor: no RLS exposure finding; one separate Auth warning for leaked-password protection being disabled;
- Supabase Performance Advisor: **0 Auth RLS Initialization Plan warnings**; one informational unused-index notice remains.

These checks do not replace Android `assembleDebug` / embedded Workspace packaging or the full same-SHA CI run. Do not merge PR #20 until executable CI resumes and passes.

## 2026-10-12 — Real Switch Account behavior, not Sign Out

The owner clarified that Switch Accounts must **choose between remembered app login sessions** rather than open Sign In. Implemented in PR #82 (not in stable v120.42): native Android chooser with AndroidKeyStore AES-GCM encrypted session slots and Desktop account selection preserving each login's refresh token; Sign Out removes only the selected saved login. Add another account preserves previous sessions. Login selection rebuilds per-owner data scope and never deletes Followings, Focus, reviews or cloud backups. New Desktop and Android emulator tests added. A real Android phone and Windows owner acceptance are pending.
