## 2026-10-26 — GRANADA: prevent already visited profiles in NEW action batches

- **Owner-observed:** Windows InstaCleaner v120.64 now performs actual Unfollow, but a fresh batch reopens profiles from earlier review. Confirmed source cause: `attempted_usernames` intentionally excludes safe no-click rows and the new-batch UI/worker reused those rows from stale imported Following/Pending lists.
- **Code:** new `visited_usernames` response = every owner/account/task journal entry plus write-ahead reserved target navigation. Record each target before opening Chrome URL, independently from any relationship-changing click. Fresh batches exclude ALL visited names and the backend refuses stale direct calls; exact saved cohort Continue and owner-requested read-only recheck remain separate. Invalid evidence blocks, never resets. Protect prior batches, journal, click WAL, account separation and owner data.
- **Regressions:** `tests/test_action_batch_history.py` and `tests/automations-next-batch.test.cjs`; full explanation [here](docs/GRANADA_NO_REPEAT_NEW_BATCH_2026-10-26.md).
- **Status:** isolated source branch; requires exact-head CI and new official FINAL stable installer before owner acceptance. Published v120.64 is unchanged. No real Instagram clicks were initiated from this development environment.

## 2026-10-26 — GRANADA v120.64 FINAL packaging: sequential Chrome target navigation

- **Published stable:** v120.63, exact tagged source `cb47df2eeda2f158df408e7a57dbda84600b622d`; successful publisher [40394937018](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40394937018) and 12 assets. Release receipt reconciled by [#246](https://github.com/michels-lab/IG-Cleaner-Pro/pull/246).
- **Functional code merged:** [#245](https://github.com/michels-lab/IG-Cleaner-Pro/pull/245) passed ten exact-head jobs. Sequential Chrome target navigation is the default instead of the observed A → B → ... → A foreground backtrack. Original ten-tab opt-in retained per selected account and task; no-click, account protection, WAL no-replay, identity proof and timing histories stay intact.
- **This pass:** candidate versions 120.64 for public/Developer Windows, signed Android, standalone Desktop and UI; create one-time guarded FINAL request. Manifest stable stays v120.63 and next reserved v120.64 until official release completes.
- **Publication remains gated:** exact-source installed Windows public/Developer, Android signed public/Developer co-install, native and rendered UI, SHA-256 and update-feed checks. No RC or beta. Owner's real Instagram Unfollow/Cancel Pending success remains **UNVERIFIED** (#164/#172), with no user data or live relationship mutation in CI.

## 2026-10-26 — GRANADA: v120.63 FINAL candidate; owner-profile and false cooldown fixed

- Source merges [#241](https://github.com/michels-lab/IG-Cleaner-Pro/pull/241) and [#242](https://github.com/michels-lab/IG-Cleaner-Pro/pull/242) both completed six exact-head checks and landed in `main`. Repeated owner profile fallback during every action-stage proof is replaced with short-lived, cookie-bound, same-Chrome positive identity proof that never bypasses visible owner mismatch/challenge or loses WAL/no-replay barriers.
- The owner saw **2,670 s** before next tab despite `Batch size 20`, `Rest 1 min`, `Gap 8 s`. Root cause: the selected batch size was being used as a hidden 60-minute visit limit. Fix separates batch rest from explicit 120-visits/hour visit safety policy, preserves original visit/rest histories and identifies the active pause reason. Original 10/40 saved cohort, protection, review tabs, cancel and pending verification are unchanged.
- Official stable stays **v120.62**, published receipt [here](GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md). Conditional **v120.63 FINAL** release request stages exact public/Developer Windows+Android version increments, UI badge and official source SHA gate. Publication remains blocked until all exact-source installed Windows, Android signed-key co-install/visual, SHA-256 and update feed checks pass. No RC/beta and **no real owner Instagram Unfollow/Cancel success yet verified**.

## 2026-10-24 — GRANADA v120.62 FINAL officially published and reconciled

- [Official v120.62 FINAL stable](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.62), 12 assets, exact tagged commit `9ad3719aa49378ee38bfb035bc4587ec1af7e7d4`; [governed publisher 40121318686](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40121318686) **SUCCESS**, including installed Windows public/Developer, production-signed Android public/Developer co-install, rendered UI, SHA-256 bundle and official GitHub feed.
- [Permanent receipt](GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md) records asset fingerprints, merged #238 safe saved-10/new-40 decision, merged #239 7/7 exact-head checks and v120.60 provenance-drift regression caught before publishing.
- One-time release authorization consumed; authoritative manifest/README/update guide now stable **v120.62**, next **v120.63 reserved and NOT authorized**. This documentation-only closeout does not repackage or republish v120.62.
- **Physical owner Instagram Unfollow/Cancel Pending NOT verified**; keep #172/#164/#230 open, never label an uncertain click as confirmed. No existing action journal, Chrome session, protected account or user data was modified.

## 2026-10-24 — GRANADA v120.62 provenance regression caught before merge

- **Root cause (docs/status drift + test gap):** the candidate correctly named published v120.61 but kept v120.60's `lastPublishedRun`, `lastPublishedCommit` and `lastPublishedAt` in `release/distribution-manifest.json`. The old docs-contract test only checked these values when the request was already marked `published`, not during an authorized *next* release.
- **Fix:** match authoritative v120.61 FINAL tag `148074c870a11068d809e1a12ba0384dbe6e4c3f`, successful publisher run `40017257499`, published `2026-10-23T20:19:53Z`; add a regression that requires the new request's `previous_publication` receipt to match every recorded manifest provenance field. The previous manifest fails this regression. No user state, protected cohorts, Instagram browser session or relationship-click logic changed.
- **Gate:** rerun exact-head CI on this PR before merging. v120.62 remains unpublished until independent installed Windows, signed Android coinstall, visual and release-asset checks finish; real owner's Instagram Unfollow and Cancel Pending success remains **UNVERIFIED**.

## 2026-10-24 — GRANADA owner 10-vs-40 blocker fixed in source, v120.62 FINAL publication gated

- [PR #238](https://github.com/michels-lab/IG-Cleaner-Pro/pull/238) merged after six exact-source checks, including installed Windows public/Developer, Chromium, Android runtime and desktop visual validation. Original old cohort remains protected; choose Continue saved 10 or explicitly save old cohort unchanged in local history and prepare new 40 with fresh Run approval. Five earlier attempts are preserved and cannot be blindly replayed; no action is marked Reviewed by planning. **Source change is not evidence of owner Instagram success**.
- [v120.61 official FINAL release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.61) confirmed 12 assets, run [40017257499](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40017257499) SUCCESS, exact published SHA `148074c870a11068d809e1a12ba0384dbe6e4c3f`, October 23. The consumed v120.61 publication is reconciled to current stable, with **v120.62** reserved and specifically authorized for the full official publisher; no local-installed acceptance is claimed.
- Do not test the owner's real Instagram relationship-changing actions from CI. Preserve the original saved 10/40 histories, the write-ahead click journal, the protected list, no-replay barriers, old Profile Counts and the separate Developer twins.

## 2026-10-23 — GRANADA #46: official FINAL v120.60 published, request consumed

- Verified [official v120.60 stable release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.60), 12 downloadable assets, `draft=false` / `prerelease=false`, exact source `457506c814c64f4ee31e5cbf0c7fbf6d472fa1f9`, publisher [#39983124380](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39983124380) **SUCCESS** on attempt 2. First attempt failed to download Android SDK system image; mandatory emulator/Windows/signing/checksum gates remained intact and passed on retry.
- [Authoritative publication receipt](GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md). Consumed the old requested authorization; stable = v120.60, next development reserved = v120.61 (neither published nor authorized).
- Windows installed v120.60 includes true owner-scoped Cancel during cooldown/pause, current operation clarity, per-profile action timestamps and end-of-batch review dialog. This is code/CI/release evidence, **not** real Instagram action acceptance.
- Remaining: physical owner signed-in Unfollow/Cancel verification [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) / [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), eliminate repeated own-profile probes safely [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). Original 40-target evidence/protected/uncertain WAL untouched.

## 2026-10-23 — GRANADA #45: v120.59 officially published and publication receipt reconciled

- FINAL v120.59 published 2026-10-23T12:53:51Z: [12 official assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.59), exact source `92d612377c2c8a6e56534465f86e3ddcfe86bc23`, [governed publisher #39955452062](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39955452062) SUCCESS across all five mandatory jobs.
- v120.59 request consumed and canonical README/manifest/update and sync docs corrected; v120.60 reserved only (not published). New [v120.59 official receipt](GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md). No duplicate publication.
- Root cause fixed: the old governed publisher could edit an existing published tag and upload assets with `--clobber`. It now refuses existing tags; negative contract requires create-only publication.
- Functional caveat: the new Unfollow engine is included in the official Windows v120.59 release but **real owner Instagram relationship changes are not yet verified** (#172/#164). Original saved cohort, protected profiles, uncertain WAL, owner Chrome sessions unchanged.

## 2026-10-23 — GRANADA #40 official published v120.58 receipt (no republish)

- Verified FINAL stable v120.58 GitHub publication with 12 assets and governed publisher SUCCESS #39917647988 on SHA `401389c67e997c81ee5559d3a08989749adbcd62` at 2026-10-23T07:37:10Z.
- Canonical manifest/README/update guide/release request reconciled to current v120.58, reserved v120.59. Release request marked consumed, preventing accidental second publication. See `docs/GRANADA_40_V12058_STABLE_RECEIPT_2026-10-23.md`.
- Real owner signed-in Unfollow/Cancel acceptance (#172/#164) **not verified**; no new release or user action produced by this documentation change.

## 2026-10-21 — GRANADA #27 official v120.55 FINAL release published; canonical receipt reconciliation

- Official [v120.55 **stable**, not an RC or prerelease](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.55) independently verified on GitHub: 12 assets (public and Developer Windows/Android packages plus SHA256SUMS), `draft=false`, `prerelease=false`, published 2026-10-21 21:32:41 UTC; tag targets exact SHA `10f1e4cb9b3990ea47045ff37aa674ce27c2cebb`.
- Governed [publisher run #39678605509](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39678605509) **SUCCESS**: all five jobs green including release-request gate, installed Android Developer Account/notes/JSON, screenshot-backed Android and Desktop QA, installed Windows public+Developer Setup, real production-signed Android public+Developer co-install and foreground, official release verification. PR #204 signed-Android launch gate and KVM configuration merged and passed exact-source QA.
- Post-release receipt reconciled **without new release**: consume `.michelslab/release-request.json` authorization (`authorized:false,status:published` with run/SHA/date/URL); update `release/distribution-manifest.json` to `currentStableRelease=v120.55`, `nextRelease=v120.56` (reserved, NOT published), and match README/update docs/notes. Runtime Windows updater already reads GitHub `releases/latest`, so it independently sees the published stable; updating the manifest corrects repository governance, not the official release itself.
- Real owner signed-in Instagram Unfollow and Cancel Pending still **UNVERIFIED** (issues #172/#164): no live account interaction, original 40-profile cohort, protected entries, Chrome session, uncertain-click WAL, passwords, tokens or owner database state changed by these release-receipt documentation edits.
- Evidence: [CI/publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39678605509) and public GitHub release tag. New receipt contract prevents an already-published stable from remaining authorized. Future reserved v120.56 source builds require separate explicit staging/signing and validation, with NO automatic release triggered by this reconciliation.

## 2026-10-21 — GRANADA #25 Android FINAL stable release-shell fix MERGED; v120.55 attempt #5 STARTED

- [PR #198](https://github.com/michels-lab/IG-Cleaner-Pro/pull/198) **MERGED** at `49f418919df796f7fc0b5b7e09a922906c3682f8`; 4/4 exact-head CI PASS (Android Developer installed WebView, Android Home/About, general app/Android/RLS, Desktop). Mandatory separate production-signed Android public+Developer co-install now invokes strict `bash tools/verify_production_android_coinstall.sh` rather than invalid dash `set -o pipefail`. Preserves real installs, package IDs, both launches and postlaunch installed paths; no bypass.
- Owner's standing FINAL-only stable v120.55 authorization reissued by `a30df2197c915ae914401b01a0b00e00ab8b3f3d` (attempt 5): [governed publisher #39659943579](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39659943579) **in progress**, all required QA to rerun on exact source SHA. No published v120.55 tag/assets claimed before run success and independent release-asset/hash verification. v120.54 remains last verified GitHub stable at this checkpoint.
- Includes [PR #197](https://github.com/michels-lab/IG-Cleaner-Pro/pull/197) Windows durable possible-click stop/invalid-null journal (5/5 CI PASS). Owner real Instagram Unfollow/Cancel (#172/#164) remains unverified regardless of release outcome. No RC, no production data mutation, protected-target removal, old 40-cohort archive or uncertain-click replay.

## 2026-10-21 — GRANADA #24 merged P0 Windows no-click barrier; #25 Android publisher shell blocker (open PR)

- **P0 source safety MERGED:** [PR #197](https://github.com/michels-lab/IG-Cleaner-Pro/pull/197), squash `12ea8a4815f8601f5b967e35b0506ceabb498282`; all five exact-head workflows PASS (generic CI, Profile Counts, installed Windows public+Developer Setup and real Chromium fixtures, Desktop rendered, Android About). Source prevents a benign-looking Instagram issue label from continuing the next ten-tab action after a durable click intent exists; present-but-null click_intent now invalid/uncertain. Fake-browser unit tests prove first target's WAL is saved and subsequent targets untouched. **No real owner's Instagram relationship click** performed; live issue #172 remains open.
- **v120.55 fourth official FINAL stable attempt #39655352708: FAILED**, NOT published. Same source SHA passed Android Developer Account/notes/JSON, rendered Android+Desktop, installed Windows public+Developer Setup and production signed APK metadata. Its independent Android emulator booted but `/usr/bin/sh: 1: set: Illegal option -o pipefail` stopped the co-install script *before any adb install*, and `publish` failed closed. Official last published remains **v120.54**.
- **Release wiring PR [#198](https://github.com/michels-lab/IG-Cleaner-Pro/pull/198)** isolates strict Bash invocation of the mandatory signed public+Developer Android coexistence test, enforcing both actual installs, actual launches, both installed paths, boot state, and publisher contract. Exact-PR CI/Android installed tests are ongoing at this handoff. Do **not** merge if red, do **not** bypass the required emulator, and never make an RC/prerelease. After exact-head merge reissue full official v120.55 governed publisher at new main SHA; verify tag/asset SHA256/feed before saying published.
- Keep owner original 40-profile action journal, protected list, uncertain WAL and saved credentials intact. Desktop translation #143 remains independent. Details: `docs/GRANADA_24_POSSIBLE_CLICK_NEVER_CONTINUE_FAMILIAR_ISSUE_2026-10-21.md` and proposed `docs/GRANADA_25_PRODUCTION_ANDROID_BASH_DEVICE_GATE_2026-10-21.md`.

## 2026-10-21 — GRANADA #23 Android Developer native bootstrap race fixed in tested source; final v120.55 publisher attempt 4 IN PROGRESS

- Exact final-only v120.55 release run [#39651351295](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39651351295) failed at installed Android Developer WebView `igcDevAccount` = `MISSING_BUTTON`; publisher was skipped. Other gates (Desktop/Android UI evidence and installed Windows public+Developer Setup) passed. No official v120.55; v120.54 still last confirmed stable.
- [PR #196](https://github.com/michels-lab/IG-Cleaner-Pro/pull/196) **MERGED** at `c446e32f3f55ab9e65c98c18633ba56308bda417`. The test now waits for the *native post-reload second WebView document* via actual Android bootstrap flag/native host marker, real mounted Developer Account button and sign-in view, then performs the unchanged real click, note persistence and native JSON download assertions. It makes no production changes to robots, histories, HTML, signer or user accounts. Android Developer runtime (installed emulator + matching-key disposable CI signing) [#39654637579](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39654637579) **SUCCESS**, Android About [#39654637640](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39654637640) **SUCCESS**, general CI [#39654637560](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39654637560) **SUCCESS**.
- Official v120.55 **fourth attempt** [#39655352708](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39655352708) triggered on exact release-request commit `c9534b739aaac65cb9069daf07937088ddee0c4a`. At this handoff it is **in progress, NOT published**. The independent signed public+Developer APK coexistence emulator previously timed out booting in attempt 2; cannot skip its installation/signature test. ALL Windows, Android, visual, Developer, SHA256, asset/feed and signer release gates remain mandatory.
- Keep real owner Instagram Unfollow / Cancel Pending test issue #172 OPEN; CI does not prove live relationship changes. Preserve all original protected profiles, interrupted action journals and saved forty-profile cohort. No RC, prerelease, archived unknown users or invented successful release.
- Detailed isolated investigation: `docs/GRANADA_23_NATIVE_DEVELOPER_WEBVIEW_BOOTSTRAP_GATE_2026-10-21.md`. Next action: inspect run #39655352708 exact final conclusion, inspect publisher job logs if red. Verify official stable GitHub tag/assets after green before updating manifest/current-stable policy.

## 2026-10-21 — GRANADA official v120.55 release gate — source integrated, publication not yet proven

- All independent required source PRs merged: #186 final release Android Developer installed QA gate `eef3f53`, #184 two-lane Windows Automation Center `75b8a13`, #189 v120.55 version/source/notes `3423242`, #188 malformed saved journal no-replay `bc6bd68`. **Original saved batches/uncertain journal/protected profiles preserved.**
- Exact-head PR verification: #186 4/4; #184 6/6; #189 6/6; #188 5/5. Windows integrated installer tests are offline fixture/installed local Setup, not proof of live signed-in Instagram Unfollow or Cancel Pending.
- Current officially published v120.54 until verifiable new GitHub tag/assets. Owner's standing GRANADA instruction permits v120.55 FINAL STABLE (never RC) upon mandatory publisher checks: Desktop/Android screenshot, Windows public+Developer installation, Android Developer real emulator navigation/JSON export, persistent production Android signer, integrity SHA-256/asset/feed verification.
- The release request is `authorized` only when set explicitly in `.michelslab/release-request.json` for v120.55. Do not merge other agent-owned Desktop translation #143 into this release unseen. If publisher fails, retain exact failure and do not claim publication or switch manifest/README currentStableRelease. After publication, record confirmed SHA/run/assets and separate owner real Instagram acceptance #172.

## 2026-10-21 — GRANADA #17 Windows two-lane Automation Center (isolated source candidate)

- Issue [#176](https://github.com/michels-lab/IG-Cleaner-Pro/issues/176), branch `granada/p0-windows-automation-center-lanes-20261021`: refactored the real Automations landing structure into **permanent Analysis / Action lanes** with explicit status mirroring from the current Profile Counts and action robot, scoped responsive card layout, saved-cohort versus preferred next batch information, visible browser-admission warning, and a keyboard-accessible collapsible **Issue Review** containing the ORIGINAL issue filters and results (not a new journal or second action runner).
- Eliminated former duplicate navigation-only Overview card. Existing action controller, owner guards, exact batch replan, saved histories, protection and Chrome session code are unchanged. Fallback UI accurately says browser robots cannot navigate in parallel without separate proven contexts; local saved results remain available.
- New **real Chromium 390/1280px rendered acceptance** `tests/automation-center-browser.test.cjs`, plus Desktop rendered workflow and packaged Windows Setup CI gates. Screenshots written during CI to `artifacts/automation-center/`.
- **Source not merged/published;** screenshots/tests added but exact-head conclusions must be inspected before declaring PASS. No actual owner's Instagram action, machine install or independent concurrent browser session established by source changes. v120.54 stays last official stable; v120.55 unauthorized. Detailed handoff: `docs/GRANADA_17_WINDOWS_AUTOMATION_CENTER_2026-10-21.md`. Separate Developer PR #183 and English PR #143 untouched.
- The complete issue #176 remains open for remaining information-architecture consolidation and proven safe analysis/action concurrency; issue #172 live action reliability remains open.

## 2026-10-21 — GRANADA Developer pending-cohort forensics: separate candidate, no release

- Source branch `granada/p0-developer-cohort-forensics-20261021` isolates diagnostic-only work from recent merged WAL #182 and open Desktop English PR #143. Scope: `tools/developer_audit.py`, Developer regression tests and docs; no production action worker or live account mutation.
- Corrects deferred cohort false pending counts and unsafe diagnostic classification of click-intent records as retriable pre-click failures. Exact matching journal+batch aggregate provides untouched, safe pre-click, uncertain, saved terminal, missing-journal and read-only observation counts without exporting identities. Explicit warning when attempted profiles have zero saved terminals.
- Tests are added, **not yet executed**; inspect PR same-SHA CI before integration. Live owner Instagram remains unverified; official v120.54 stable / v120.55 unauthorized. Detailed gate and reentry: `docs/GRANADA_16_DEVELOPER_COHORT_FORENSICS_2026-10-21.md`.

## 2026-10-21 — GRANADA P0 durable pre-click no-replay WAL MERGED; v120.54 still stable

- [PR #182](https://github.com/michels-lab/IG-Cleaner-Pro/pull/182) **MERGED into main** at `1a7a9301c5fefaa630c48205c70fdb620d621f90` (tested source SHA `6f32854881fb5b1b21857fe2d1bf2177e94d6d26`).
- First target relationship-control click, Unfollow menu, optional private confirmation, and Cancel Request confirmation now each require `_persist_action_click_intent` to atomically fsync and replace a canonical journal entry **before** Playwright sends the click. This preserves owner/account/task/batch, exact phase history and uncertain interruption state. On failed write, do not click. On crash after write, startup excludes that target from automatic replay; do not count it as success. After a saved final result the intent is marked `outcome_recorded=true`.
- The desktop Issue Review has an **Interrupted / possible click** filter, fixed last armed phase and read-only recovery instructions. Developer local-only aggregate audit reports outstanding click intents by bounded phase code to ChatGPT, excluding account names, usernames, batch IDs and secrets.
- Added **8 process-interruption/write-denial/duplicate-phase/worker integration tests**, Developer aggregate privacy test and Issue Review regression test. All relevant **five exact-head PR CI workflows passed**: Profile Counts on Linux, Desktop rendered UI, Android About, Android Developer runtime+CI disposable-key APK signing and **Windows integrated installed public/Developer setups with Chromium flows**. Generic broad CI skipped (not failed).
- This is **not** a real Instagram action acceptance test and simulated crashes do not establish real hardware power-loss durability. No production Instagram relationships were modified by this work; source merged, **v120.55 not authorized/not published**; official latest remains **v120.54**. Existing real-owner Unfollow/Cancel acceptance issues #172 and #173 stay open, old protected 40-target journal preserved.

## 2026-10-21 — GRANADA P0 source: interrupted-click write-ahead safety (PR #182, release NOT authorized)

- [PR #182](https://github.com/michels-lab/IG-Cleaner-Pro/pull/182) implements a **fsynced, atomic write-ahead record BEFORE any Instagram relationship-control click**: first Following/Requested control, Unfollow menu, private confirmation and Cancel Request confirmation. Each stage is bound to owner/account/task, exact approved batch ID and target, with explicit phase history; failures to save the barrier prevent the action click.
- An unexpected exit after preparing/sending a click but before the verified result leaves `status=review`, `issue=interrupted_action_uncertain`, `click_intent.phase` in the canonical journal. On startup, this target is **not** a proven no-click, is excluded from auto-replay and instead available for manual/read-only inspection; no automatic success is counted.
- Final confirmed result retains the intent/phase trail and sets `outcome_recorded=true`. Owner's Issue Review gains a dedicated "Interrupted / possible click" filter, last armed click phase and recovery explanation. Developer's original shared canonical journal and cross-process lock remain authoritative.
- New offline regression suite `tests/test_action_click_wal.py` covers process loss before first click and after Unfollow menu click, actual ActionRobot worker wiring, both task stages, duplicate phase, disk write denial, true no-click and prior-history retention. Linux Profile Counts, installed Windows preview and official manual publisher all require this suite; separate JS Issue Review filtering assertion added.
- **Validation status:** PR checks requested/running; this note records source candidate rather than falsely asserting green before finished. Latest official download is **v120.54**; no v120.55 authorization, asset upload or live Instagram owner action. Power-failure/hardware-storage behavior cannot be proven by simulated CI: claims limited to write ordering and crash restart semantics.

## 2026-10-20 — GRANADA P0: public/Developer cross-process Instagram action interlock MERGED (no release)

- [PR #181](https://github.com/michels-lab/IG-Cleaner-Pro/pull/181) **MERGED main** at `4f8b4b9f17e26c71b32203c301ae404ec655a071`, source head `ec00a2cc302d83ebf8992ade741ac9730a86033b`.
- Public and Developer Windows actions share the **canonical** journal root, so they now acquire the same crash-recoverable operating-system file lock BEFORE creating/reusing a batch and hold the lock until the full action worker and manual uncertain-tab review finish. Windows `msvcrt.locking` and Linux `flock` fail closed on contention and release on actual process termination; a second edition receives HTTP 409 `cross_process_action_busy`, `safe_no_click=true`, and never binds a new owner/batch or changes the relationship. An interrupted batch's journal, protections and old 40-profile evidence remain preserved.
- Closing the native Developer app also requests stop and joins the **Developer real action worker** and **read-only Chrome probe** before bridge shutdown. Prior cleanup only awaited public actions + Profile Counts.
- Added `tests/test_robot_interlock.py`: real second-process lock denial, crashed-process recovery, worker-held admission and rejected-task cleanup. Added Developer authenticated HTTP 409 and Developer app safe-shutdown tests. Protected exact-head checks: **5/5 relevant workflows PASS** (Linux Profile Counts, installed Windows main+Developer installers and offline Chromium, Android Developer emulator after rerun, Android About, Desktop rendering). Android Developer first emulator attempt failed intermittently at Account navigation; targeted retry PASS on same SHA. Generic CI skipped. No owner Instagram was accessed in automated tests.
- Official last-published remains **v120.54**. No v120.55 authorization/publication was made. Still open: owner-installed real Unfollow/Cancel verification; developer action diagnoses based on user's live Chrome state; true two-lane automations UX (#176) and crash-window action-write-ahead protection should be assessed independently before promising no-replay across sudden shutdowns.


## 2026-10-20 — GRANADA Developer distribution ready in main (NOT A RELEASE)

- [PR #180](https://github.com/michels-lab/IG-Cleaner-Pro/pull/180) **MERGED**, main merge `73e91a1d917a70b578d9d2ade4ed39c78627bbd1`. Android Developer signed APK and separate Windows Developer Setup are now **mandatory artifacts in the governed release workflow**, including manifest/checksum/published-assets gates. Official Android publisher verifies the same persistent production signer + distinct `.developer` package and installs/launches both production APKs together before publication. Windows Setup tests independent AppId, data-safe install/startup/uninstall.
- Source-head `2eedad32546f6fa9f8b8127cedc90c7349cfda15` passed five relevant PR workflows (Windows integrated setup, Developer signing-path with disposable CI key, Android Developer emulator, Android About, Desktop UI); generic broad CI skipped. Disposable CI key is not the real prod cert; official approved release must verify production certificate again.
- Official v120.55 **NOT authorized, NOT published**. Latest GitHub release still v120.54; `.michelslab/release-request.json` remains authorized=false. A future authorized v120.55 build needs Gradle/signing/UI versions synchronized, exact-commit release hard gates and real-owner testing. Owner's live Unfollow/Cancel remains unverified. Keep issue #173 and #172 open until actual official installed/live acceptance.


## 2026-10-20 — Additional GRANADA official APK device gate

- Authorized publisher now installs BOTH production-signed Android APKs on the SAME API-35 emulator, launches stable and Developer entry points and verifies both package paths still exist. This is a release hard gate after production certificate/package checks, before publishing. The PR's normal emulator test remains a separate debug/debug Developer coexistence check, not equivalent to production signing.
- Release request remains unauthorized and unchanged; source publication PR #180 is separate from the eventual v120.55 release operation. The owner's real Chrome/Instagram Unfollow and Cancel Pending acceptance remains outstanding.

## 2026-10-20 — GRANADA: governed Developer twins in official release (source, not published)

- Added `androidDeveloper` and `windowsDeveloper` assets to `release/distribution-manifest.json`. Official publisher must build **both** independent Developer outputs, inspect them, include them in SHA256SUMS, upload them and confirm them after publication. Stable original outputs remain mandatory.
- Android `:app:assembleDeveloper`: local emulator checks may continue with debug key. Official release requires `IGC_ANDROID_SIGNED_DEVELOPER_REQUIRED=true` and the same persistent production signing configuration/certificate as the normal `:app:assembleRelease`; signed Developer becomes nondebuggable. Package `com.michelslab.igcleaner.developer`, separate app storage and display identity. Fail if unsigned, wrong package, wrong version or certificate mismatch.
- Windows source builds and smoke-tests its independent Developer Setup in the **official publisher job** (not only its development PR): separate Inno AppId, installation path and forced `--developer` entry point; installed healthcheck/launch/uninstall and production-data sentinel. Official publish job checks both Windows installers' .sha256 hashes and sizes.
- Android Developer emulator also installs public **debug** (.beta) and Developer side by side and checks both package IDs after installation. Signed production APKs are validated separately in guarded publication; emulator debug tests alone are *not* signing proof.
- Added `tests/developer-release-contract.py` and Android Developer CI trigger for manifest, release policy and these gates. Release remains **manual authorization only**. No publication command or release request update made. Original `v120.54` remains last stable and owner real Instagram Unfollow/Cancel verification stays unperformed.
- On authorized v120.55 release only, normal version/build metadata will need synchronized bump and exact-commit visual+Windows+Android gates; no user's real account is used during CI and no future approval is presumed.

## 2026-10-20 — GRANADA P0 Developer mainline MERGED, exact-head CI green (no v120.55 release)

- PR [#179](https://github.com/michels-lab/IG-Cleaner-Pro/pull/179) **MERGED**, merge commit `614071e11c66e6258c88b790ab63bcf186056578`; preserves merged ten-tab-wave PR #177 and batch 40→10 / Cancel Pending source fixes #174/#175. Conflicting older Developer draft #178 CLOSED as superseded.
- Exact source head `526a0481b8606cdfea03216cb4aec8f10e0f34fe` had **5/5 relevant CI SUCCESS** (integrated Windows Setup + independent Developer Windows installer install/smoke/uninstall, Profile Counts, Desktop rendered, Android Developer runtime, Android About). Generic CI SKIPPED. Developer CI initially failed two brittle test assumptions (fixed in final exact-head run).
- Developer has a scoped local diagnostic chat with owner annotations and a manual Copy for ChatGPT handoff. Separate Windows-only opt-in 1–10 exact-target real Unfollow/Cancel Pending test uses explicit consent, existing action robot, canonical journal and isolated Developer Chrome. **No actual owner Instagram relationship was changed/tested by us.** Free-text chat alone cannot execute mutation.
- **Still OPEN:** signed independently downloadable Android `.developer` APK in governed release; official publisher and checksum manifest inclusion of both Developer assets; owner live Instagram installed acceptance of actions; explicit owner v120.55 publication authorization. Windows Developer Setup exists as green CI-built preview but **not** an officially published release asset. Official latest stable remains **v120.54**.

## 2026-10-20 — GRANADA merged ten-tab robot waves + candidate Developer real-action QA

- Source verified merged PR #177 as `0de1ac78d9d09bff3a7c79136ccc498d3ad2ac43`: full 10-tab waves (open all targets, focus first, execute + verify, close confirmed, then next full wave), including 40-profile/four-wave fake-Chrome regression, protected/uncertain/no-replay rules and Windows installed CI. This is **source merged**, NOT officially published v120.55 or live owner Instagram tested.
- Developer mainline candidate PR #179 adds a **simple local diagnostic chat** and manual Copy for ChatGPT privacy-reviewed handoff; separately owner-authorized Windows Developer LIVE ACTION TEST can really Unfollow/Cancel Pending 1–10 exact profiles using mainline action robot and canonical scoped journal. Free-text chat cannot mutate an account. Independent Developer Windows Setup candidate/CI remains subject to exact-head tests and owner installed real account acceptance.
- Official stable v120.54 unchanged. v120.55 reserved and release still requires explicit owner command. Production/live actions cannot be claimed repaired without owner testing. See docs/GRANADA_DEVELOPER_CHAT_REAL_ACTION_TEST_2026-10-20.md and docs/GRANADA_P0_TEN_TAB_WAVES_2026-10-20.md.

## 2026-10-20 — GRANADA ten-tab sequential action waves (CANDIDATE, no release)

- Owner's exact behavior implemented in `tools/profile_actions.py`: stage ten visible target profiles **before clicking any**, sequentially activate/focus and verify each, close confirmed outcomes, then open the *next group of ten* (not rolling next-user prefetch). Saved pacing/rest, protected exclusions and uncertainty no-replay remain mandatory. Tested contract added in `tests/test_action_tab_waves.py` and installed Windows/Profile Counts pipelines; details: `docs/GRANADA_P0_TEN_TAB_WAVES_2026-10-20.md`.
- Scope is source development for Windows production action robot. Developer Edition real-action test is implemented on isolated candidate PR #179 with explicit approval, but is not integrated/released and remains unverified on an owner's installed real Instagram session. No actual Instagram account actions were performed by the developer/CI; v120.54 remains official stable; v120.55 reserved, **no permission to publish**.
- Do not equate offline Chromium proof with the owner's live Unfollow/Cancel results. Keep issue #172 open until official-installed real-account acceptance.

## 2026-10-20 — GRANADA P0 Windows robots: PR #174 and #175 MERGED; exact-head CI validated, live Instagram QA OPEN

- **Integrated source:** PR [#174](https://github.com/michels-lab/IG-Cleaner-Pro/pull/174) merge `3bbb4e22de29dbd5e632b96a4b58429eb813d3a1` and PR [#175](https://github.com/michels-lab/IG-Cleaner-Pro/pull/175) merge `a0518a9af4129dffe2f204f820ef73f888fa73f4` on `main`.
- **Safe cohort replan (#174):** owner-explicit 40→10 in-place preservation of original list/batch ID/uncertain click journal; unacted users reusable later without archive, fake Reviewed or repeated uncertain clicks; read-only live robot status cannot be swallowed silently by queue render.
- **Positive Cancel no-request evidence (#175):** target-specific stable Follow/Follow Back, verified actual Instagram owner, positive delay and additional control rechecks before returning durable terminal `already_not_requested`; no Cancel click or success falsely claimed, excluded on restart/reimports, preserved account/task boundary. Requested and Following, suggestion-only Follow, wrong owner and challenges retain fail-closed behavior. Controller distinguishes actual clicked cancellations vs verified absence of request, presents authoritative state and disables Run during active/challenged jobs; read-only recheck observations separate.
- **Exact PR #175 head QA:** `9ccbe1a5f7a050221cb1336e4cfc51eeebfe1112`: five workflows marked **SUCCESS**: Profile Counts feature tests #39405976882, Desktop rendered #39405976828, installed Windows/real offline Chromium action fixtures #39405976915, Android Developer Edition runtime #39405976981, Android About #39405976748. Generic IG Cleaner Pro CI #39405976683 **SKIPPED**, not passed. PR #174 exact head `54f45ead44157cc9579bc0395f35bff56b9be667` likewise had 5 successful relevant checks.
- **Open limitations:** source + offline Chromium do NOT prove owner's signed-in actual Instagram Unfollow click (official v120.54 owner reports zero confirmations), actual Cancel UI or Chrome session on his Windows machine. Keep [live regression #172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [robots epic #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) OPEN. Developer independent packaged twin [#173](https://github.com/michels-lab/IG-Cleaner-Pro/issues/173) remains separate. New [Automation Center architecture #176](https://github.com/michels-lab/IG-Cleaner-Pro/issues/176) specifies nonduplicated Analysis/Action lanes and safe concurrency but is NOT implemented.
- **Distribution:** official published stable remains **v120.54**, next **v120.55 reserved**, **no new release authorization** from this turn. No public Instagram account, cookies or cloud data modified by these CI tests.

## 2026-10-20 — GRANADA P0 Cancel Pending positive evidence (source candidate)

- **Issue:** #172 and #164. Isolated branch `granada/p0-cancel-positive-evidence-20261020`, based on post-#174 main merge `3bbb4e22`.
- **Root issue:** Cancel Pending treated a positively verified exact-target Follow/Follow Back (no Requested) as `review / pending_not_requested`. The profile could be reopened after reimport or restart despite no relationship click.
- **Behavior:** visible Chrome requires the signed-in owner, exact target username, three positive non-requested observations and at least five seconds of hydration delay; an additional three checks exclude delayed Requested before returning terminal `already_not_requested`. No Cancel was clicked or claimed. If Requested appears, only the normal validated cancellation path may run. Owner mismatch, sidebar suggestion, Following, missing controls or challenge never count as positive no-request evidence.
- **Persistence:** owner+Instagram workspace+task-scoped journal/replay and per-cohort approval now recognize the terminal non-click state. Existing historic `ok`, uncertain click, protect/favorites and original saved batches are unchanged. No automatic Reviewed promotion.
- **Controller:** Windows metrics distinguish actual `Cancellations confirmed` from `Already no pending request`; read-only old failures have separate `observed_not_requested` count.
- **Offline tests:** FakePage unit tests and real Chromium DOM fixtures cover English/Spanish, public/private, delayed Requested, sidebar-only Follow, owner mismatch and restart/scope/counter integrity. URL interception prevents real Instagram use.
- **Status:** candidate only; GitHub exact-HEAD CI and installed physical Windows / user Instagram acceptance are separate gates. No version bump or v120.55 release authorized; stable remains v120.54.

## 2026-10-20 — Owner correction: unfinished 40-person cohorts MUST be reusable at selected size; no archival

- **Explicit owner correction:** “si una tanda no termino puede reutilizar los usuarios para nuevas tandas” and “no es necesario ni recomendable archivar esos usuarios.” Previous proposed 'defer-resized-batch' design was replaced **before any merge**. Changing 40→10 must NOT archive the original cohort or its users. This is distinct from existing intentional protected-collision archival (separate special condition).
- **Implementation:** `ActionRobot.replan_incomplete_batch` accepts exact owner/account/task/batch ID, desired size and human `replan-size:<id>:<size>` approval only when Chrome robots are idle. Keeps the same pending batch ID, full `original_targets`, initial confirmed/uncertain original action journal, active next selected 10 targets, and `carryover_targets` for other untouched/proven-preclick profiles. Excludes protected profiles, confirmed actions and uncertain clicks. No relationship click, no Reviewed mutation, no deferred_at, no deleted original user. Cold restart `attempted_history` returns reusable source profiles scoped to original account/task, separate from never-retry attempts.
- **UI:** Run must refuse to continue the old 40 when 10 is selected, offers `Use 10 from unfinished 40 · keep remaining` after explicit confirmation. It then presents a fresh ten-person active approval, and prioritizes still-eligible previously unfinished users in later batches; never silently starts or ignores the selected size. `igcAutoLiveStatus` restored after rerenders so robot status cannot be hidden under 'Queue prepared'.
- **Tests:** backend old 40→ten in-place, 28 remaining after 2 recorded outcomes (uncertain and confirmed), cold restart/owner/task isolation, evidence preservation, later batch 10, no fake Reviewed or archived entries; UI explicit 40-vs-10 and no automatic action on mismatched size. Submitted to exact-head Windows/Chromium/Python/UI CI; real Instagram acceptance still requires owner's installed official stable test.
- **Separate:** Developer Twin real-account diagnostics plus chat and independent packaging in issue #173 and separate `granada/p0-developer-twins-official-distribution-20261020`; do not collide/merge its HTML concurrently without rebasing. Official stable still v120.54; v120.55 is reserved only, not authorized.

## 2026-10-20 — OWNER-AUTHORIZED GRANADA RELEASE v120.54 — officially PUBLISHED and verified

- **Permission:** explicit owner command “OPERACION GRANADA Y DALE RELEASE” (2026-10-20) covers the official stable publication. [Release PR #171](https://github.com/michels-lab/IG-Cleaner-Pro/pull/171) merged after **five active PR-head success** checks (Profile Counts, integrated Windows Setup/Chromium, Desktop rendered, Android About, Android Developer). The Android Developer emulator had one intermittent Account-navigation failure and passed the subsequent same-HEAD rerun; no test was disabled.
- **Published facts:** [v120.54 official stable](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.54), **2026-10-20 08:40:59 UTC**, latest, not draft/prerelease; target release source merge `4d8962743b83bcad178c3e8cde9c057483361300`. [Governed release workflow run #39394417960](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39394417960) completed **SUCCESS** for authorization gate, same-SHA Desktop+Android visual evidence, Windows Setup install/startup/uninstall, stable production-keystore Android signing+certificate check, release-bundle checksums and final published asset existence.
- **9 uploaded release assets verified:** `IG-Cleaner-Pro-Windows-Setup-v120.54.exe` (50,726,622 bytes; SHA256 `fc416f4afad53deef42b128b86810452943d63dd1979e9082836189f3767aba9`), signed `IG-Cleaner-Pro-Android-v120.54.apk` (7,924,315 bytes), integrated Windows robot ZIP, self-contained Desktop HTML, Desktop ZIP, Windows Setup SHA256 sidecar, image, privacy document, and `SHA256SUMS.txt`. Installer and Android/HTML are user-downloadable official stable artifacts, not CI previews.
- **Functional Granada content:** shipped post-v120.53 owner/account durable Protect/Unprotect, preflight stale protected batch rejection without silently changing authorized targets, safe explicit archive of older blocked review cohorts without Reviewed, original action journal + uncertain-click preservation, cold-start history and owner-scoped on-screen archived summary (PRs #166/#168/#170). Includes other previously merged windows/Developer/read-only diagnostics since v120.53.
- **Governance closed:** `.michelslab/release-request.json` marked `authorized:false, status:published` with run/SHA/url to prevent re-publishing on later changes; `release/distribution-manifest.json` records current stable **v120.54**, next candidate **v120.55 reserved only**, not authorized. No production user data, saved import, robot Chrome cookies or previously viewed relationship actions were modified by ChatGPT.
- **CRITICAL OPEN owner acceptance:** [Windows robots epic #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and #83/#114/#107/#110 remain open for *real owner's installed official Windows Setup* with signed-in Instagram: actual Following→Unfollow, Requested→Cancel, 3+ cohorts after overlapping reimport, correct 10-tab/pause/cold-start, protected exclusions and no ambiguous click replay. CI validates offline and cannot prove live Instagram relationship success; stop on CAPTCHA/security challenge and use manual fallback. Lower-priority English PR #143 remains separate.
- **Next Granada:** prioritize the first reproducible owner v120.54 real-world blockers in P0 Windows robots, or the next large independent non-conflicting code/QA block; continue ambition standard 3–6 substantial workstreams when safe and meaningful. Do not publish v120.55 without fresh owner approval.

## 2026-10-20 — GRANADA #17 P0 ambitious five-deliverable protected-cohort recovery: merged and CI verified

- **Integrated:** [PR #170](https://github.com/michels-lab/IG-Cleaner-Pro/pull/170), merge `7a2fba8d8b483553bbf0920d8c7d9845cc993a8c`, issue [#169](https://github.com/michels-lab/IG-Cleaner-Pro/issues/169). Exact PR-head commit `ecfdf89ff2618da1df943128b3ce3c867f826e0d`; **5/5 active checks SUCCESS**: integrated Windows installer build/install/launch/uninstall + offline Chromium fake Instagram, Python action/Profile Counts tests, Desktop rendered UI, Android About emulator, Android Developer runtime. Generic IG Cleaner Pro CI was **SKIPPED**, not counted as passed.
- **Root cause fixed:** when a currently saved unapproved Unfollow/Cancel cohort acquires a protected profile AFTER batch creation, the #16 preflight refuses starting it (correct), while its untouched targets prevent approval (correct); without recovery the pending cohort permanently blocks newer eligible batches.
- **End-to-end changes:** exact ID and explicit owner confirmation to **defer a protected cohort** only for a real disk-saved protected-target collision, while robots idle and task/account match; `_pending_review` ignores deferred entries but saves original targets, date, reason, original observed/untouched counts and preserved uncertain action journal. No Reviewed promotions, no automatic replay, no Chrome opening, no favorite unprotection. The local loopback adds defer and owner-account-task scoped read-only archived history endpoints. Automations displays a warning, a guarded archive button, fresh server check before consent, and a persistent archived-history status; a subsequent **new Run** still requires new exact-owner approval.
- **Regression coverage:** 30/40 cohorts, successful/uncertain old action history, fake worker and active Profile Counts guard, wrong task/owner/account/batch ID, duplicate approval/defer rejection, no collision rejection, persisted journal/guard byte preservation, correct next cohort, cold process restart and scoped read-only archive summaries. No live Instagram account was accessed or modified during CI.
- **Acceptance and release explicitly OPEN:** [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), #83, #114, #107 and #110 still require owner **real installed official stable** test, complete Chrome identity, 3+ batches/reimport and true relationship action verification. Official GitHub stable **v120.53** remains published; **v120.54 is reserved, not authorized/published**. No source CI = owner real Chrome acceptance, no manual Actions artifact acceptance, no release publication.
- **New cross-app owner directive 2026-10-20:** Granada now targets 3–6 ambitious, meaningful linked deliverables/packages where safely independent. Source of truth [master standard](https://github.com/michels-lab/Michel-Software-Standards/blob/main/standards/OPERACION_GRANADA_STANDARD.md); local `.michelslab/GRANADA.md` and product log updated. Continue next unrelated P0 Windows robot backlog block, excluding active English PR #143 and protected cohort now merged.

## 2026-10-20 — GRANADA #17 large P0 Windows robot recovery block (candidate, not published)

- **Parent P0:** [Windows robots #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164); concrete [#169](https://github.com/michels-lab/IG-Cleaner-Pro/issues/169); branch `granada/windows-robots-defer-protected-cohort-20261020` opened after #16 (PR #168) merged. Current main keeps official stable v120.53, next release merely reserved and unauthorized.
- **Root cause:** an already-saved cohort may become blocked when the owner protects any member after its creation. New protected-cohort gate #16 correctly refuses Chrome action, yet original unapproved cohort remained current forever; untouched profiles also prevented Reviewed approval, stranding legitimate next selections.
- **Five related deliverables in one coherent branch:** (1) backend owner-confirmed `defer_protected_batch` requires actual durable in-cohort protected collision, worker idle and exact pending ID; (2) archives original pending cohort with dated reason, protected intersection and counts, without Reviewed, action journal modifications, replay, removal or browser; (3) atomic local bridge routing for explicit defer and account-scoped read-only deferred history, including after cold restart; (4) Windows Automations button only when durable block detected, recheck before confirmation, explicit warning that no account will become Reviewed and new Run requires fresh approval; (5) UI historical summary plus 30/40-account, invalid confirmation, foreign identity/task, busy robot, no-collision, cold restart and original uncertain-action preservation regressions.
- **Integrity:** original action journal, latest auth, browser session, saved protections, pacing, prior results and account separation stay intact. `_pending_review` ignores archived entries; historical records remain intact with `deferred_at`, not `approved_at`. All operations local; no Instagram login/click, CAPTCHA bypass, Meta API or new cloud writes.
- **Candidate QA:** tests added and CI requested via PR; **no checks claimed complete until exact SHA results are seen**. Owner acceptance still requires published stable Setup on a real Instagram account; this Granada does not authorize a version bump or release. English Desktop PR #143 kept separate; Android Developer and language parity remain open.

## 2026-10-20 — GRANADA #16 P0 Windows action batch protection collision: merged and exact-head CI green

- **Integrated source:** [PR #168](https://github.com/michels-lab/IG-Cleaner-Pro/pull/168), merge commit `c9edb195562b1a98a6f4a865635b548a0f08b940`; [issue #167](https://github.com/michels-lab/IG-Cleaner-Pro/issues/167) closed. Source commit `893a27ce648ec60d57dd66651e51012e97fcb578` achieved **five SUCCESS** PR workflow checks: Windows integrated Setup installer and installed-app smoke; real Chromium offline action fixture; Desktop rendered UI; Profile Counts features; Android About rendered; Android Developer runtime. The generic `IG Cleaner Pro CI` run was **SKIPPED**, not counted as a pass. No live Instagram owner acceptance or physical Windows/Android device test occurred.
- **Behavior now in `main`:** Owner/account-scoped `ActionRobot.start` rejects the exact candidate cohort before persisting any new review batch or opening Chrome whenever its members intersect durable Windows favorites OR UI-staged favorites. A structured local HTTP 409 conflict reports canonical usernames/count. Automations updates positive local protection for both action modes, shows the conflicting profiles, and requires a new owner-approved batch. On collision: no relationship click, new worker, changed owner identity, changed journal/cohort or automatic reapproval. Prior unapproved cohorts and multi-account boundaries retained.
- **Still blocked by real owner validation:** [P0 roadmap #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [live actions #83](https://github.com/michels-lab/IG-Cleaner-Pro/issues/83), [multi-batch/reimport #114](https://github.com/michels-lab/IG-Cleaner-Pro/issues/114), [Chrome/Developer acceptance #133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133). Prove genuine Following → Unfollow, Requested → Cancel Request, 3+ advancing batches, correct persistent Chrome session and never retry uncertain clicks on the owner's officially published Windows version. The backend cannot safely simulate live Instagram or CAPTCHA. Lower priority English PR #143 and Android full parity remain separate, not automatically merged.
- **Publication unchanged:** official stable **v120.53**; v120.54 reserved only. No version bump, GitHub Release, installer publication or owner request to test a CI artifact. Next Granada prioritizes independent P0 Windows robot work and owner-accepted public-release path; do not close #164 on offline success alone.

## 2026-10-20 — GRANADA #16 P0: reject stale protected Windows action batches (PR #168, draft)

- **Scope:** Canonical P0 [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), concrete [#167](https://github.com/michels-lab/IG-Cleaner-Pro/issues/167); branch `granada/windows-robots-reject-stale-protected-20261020`, [draft PR #168](https://github.com/michels-lab/IG-Cleaner-Pro/pull/168). No stable release/version bump.
- **Reproduced source risk:** Desktop could approve 30/40 usernames including two favorites saved **only** in the Windows account-scoped guard. An unapproved review batch was written first, while `_run` skipped those protected users. The owner could then be left with permanently untouched review targets. Scope is Unfollow / Cancel Pending Windows robots, not Android or Instagram scraping.
- **Source fix:** With both browser admission and owner/action lock held, `ActionRobot.start` now compares the original exact approved target list to the union of disk-persisted owner/account protections and UI-staged protections **before** assigning worker identity, writing a review cohort, touching an action journal or launching Chrome. Any collision fails atomically with `ProtectedBatchCollision`, normalized usernames and count; never removes a protected profile or silently trims/reapproves the list. Existing unapproved cohorts survive rejection without replacement, and resume semantics remain unchanged.
- **Desktop behavior:** Loopback replies HTTP 409 with an explicit safe `stale_protected_batch` code and collision list; Automations mirrors **positive** persisted protection into both local Unfollow/Cancel views for the still-selected Instagram workspace, displays exactly which profiles made the selection stale, and requires the owner to choose **Run** and approve a newly proposed batch. Wrong-workspace responses cannot mutate the visible account. No automatic retry or Instagram click.
- **Regression coverage added:** 30- and 40-person cohorts with 2 disk-only protected profiles, correction advancing into untouched queue, UI-only stale protection, account isolation, an existing pending cohort remaining unchanged, no worker/Chrome/session/journal/cohort write on rejection, HTTP and Desktop source contract. Offline simulated worker; no user Instagram or physical installed Windows validation.
- **Validation status at creation:** GitHub PR CI launched for exact branch head; outcomes pending. Do not claim source merged/green until observed. Owner tests only an authorized **official stable release**: published v120.53 unchanged, v120.54 merely reserved.
- **Following work:** Check PR CI Windows Setup, Desktop real Chromium, profile-actions Python, Android/device regressions and Supabase RLS. Resolve failures on this branch. Keep #167 open until exact-head results and integration; real-account Chrome/Instagram acceptance #83/#114/#164 remains separate.

## 2026-10-19 — P0 Windows Desktop robots: GRANADA #15 permanently protected targets FIXED IN MAIN

- **GRANADA #15 implemented, verified, integrated:** [PR #166](https://github.com/michels-lab/IG-Cleaner-Pro/pull/166), merge `da18aa1767eeb5b52baeec66807f9fded99d8478`, [issue #165](https://github.com/michels-lab/IG-Cleaner-Pro/issues/165) closed. Candidate HEAD `5cf121acae8dfab53a557e2bd525a5f6f1037ced` had **8/8 SUCCESS** checks: Windows Setup build/install/installed app launch/uninstall, offline real Chromium action/Automations contracts, Desktop rendered/local app, Android build, Android About installed visual, isolated Android Developer WebView notes, Supabase RLS.
- **Two real P0 source failures fixed:** `ActionRobot.start` on NEW authorized cohorts previously replaced owner/account durable `action-protected-<hash>.json` with a possibly stale/incomplete UI list, silently removing protected accounts. It now merges previously saved favorites on both new start and resume; the historical SHA256 filename (NUL-delimited owner/account) is preserved. Desktop `igcAutoProtect` previously sent a **protect** command even on an **unprotect** click, while optimistically flipping local state. It now sends explicit `unprotected:[u]` with matching owner confirmation and commits UI only after the backend accepts it; failures leave the safety guard displayed. Unprotect while active or from foreign/unbound owner is refused; an unbound Windows browser may only stage positive favorites locally until a new owner-approved batch is authorized. No relationship click, cookie transfer or live Instagram user change performed.
- **CI failures resolved without weakening identity:** intermediate exact SHA detected historical file hash fixture accidentally using literal backslash-zero, corrected to original NUL. Existing Windows contract rejected arbitrary scope updates with no bound owner; the controller identity guard remained strict, and a staged-local UI flow was added instead. The old offline planner expected standalone HTML to revoke durable robot protections; changed to assert it must not fake such a revocation. Later exact-HEAD all checks truly passed.
- **Next independent P0 for desktop robots:** [issue #167](https://github.com/michels-lab/IG-Cleaner-Pro/issues/167): if the UI's selected cohort includes a username protected **only** in the durable Windows file, the worker safely skips it but an untouched target could strand a pending review batch. Validate disk-protection collisions **before writing a new batch**, reject/replan rather than silently changing the approved cohort. Existing P0 live-Instagram requirements in [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), #83, #114, #133 remain open: verified real Following→Unfollow→Follow; third+ Pending batches and overlapping reimport; persistent robot Chrome session, 10-tab recovery, no ambiguous double-click or CAPTCHA bypass.
- **Translation/Developer separate:** English Windows PR #143 remains open with Developer Account navigation failure on its exact old head; #135 still needs physical/provider acceptance. #15 source change is a surgical Protect-control hunk, not full app localization.
- **Release status strictly separate:** official published GitHub stable **v120.53**; reserved v120.54 **not authorized/published**, owner only tests officially released Windows Setup/ZIP/APK. CI source green ≠ owner-installed live Instagram acceptance.

## 2026-10-19 — P0 WINDOWS ROBOTS: GRANADA #15 permanent Protect/Unprotect correction in exact-head CI

- **Owner-prioritized robot block:** [P0 roadmap #164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [issue #165](https://github.com/michels-lab/IG-Cleaner-Pro/issues/165), [PR #166](https://github.com/michels-lab/IG-Cleaner-Pro/pull/166), branch `granada/windows-robots-protected-persistence-20261019`, exact active commit `5cf121acae8dfab53a557e2bd525a5f6f1037ced` (source/CI still in progress at writing, **not merged/published**).
- **Reproduced P0 source defects:** new `ActionRobot.start` replaced the permanent `action-protected-<owner-account>.json` data with potentially incomplete UI favorites, unprotecting historical saved profiles by omission. Desktop's Protect toggle sent `protected:[u]` even when the user toggled OFF and changed its UI before a durable response, so visible and backend protections could diverge. Both impact live Unfollow and Cancel Pending safety.
- **Implementation:** always merge persisted guard with UI additions at authorized job start, retaining the precise old NUL-delimited hash path; explicit one-profile `unprotected:[u]` requires matching owner confirmation, bound owner/account scope and an idle worker. Reject cross-owner or unbound arbitrary protection mutations, following existing Windows security tests. The app may stage new favorites locally **before** binding a robot owner, but must say they will be committed only on the next explicitly approved batch. No offline HTML unprotect claim without the installed robot. UI updates after server success and does not display false success after a rejected unprotect.
- **Tests:** new Python fake-worker/disk migration and original file naming tests; existing Windows owner-scope contract preserved; updated offline Automations planner asserts standalone cannot silently remove a Windows robot protection. Earlier red runs exposed two test/assertion mismatches (backslash-zero vs NUL filename; stale standalone/unbound scope assumptions), corrected without deleting original guards. Exact-head offline action/Automations suite, Desktop rendered and Desktop contract **passed so far**; integrated Windows Setup and remaining Android/RLS/Developer checks still running at this handoff. Do not merge until full same-SHA green.
- **Still P0:** real owner Instagram `Following`→Unfollow→`Follow` confirmation, 3+ Pending cohorts after reimport, persistent Chrome login/10 tabs and unread/ambiguous actions need installed **published release** acceptance (#83/#114/#133). English PR #143 and Android Developer #135 remain parked independently. **Public stable v120.53**, reserved v120.54 unpublished/not authorized. Source CI is not a release or live account proof.

## 2026-10-19 — OWNER PRIORITY OVERRIDE: P0 Windows Desktop Robots (not Android Developer)

**Owner instruction:** "dale prioridad a la version de los robots de escritorio, que le falta". Canonical open acceptance epic [#164 — Windows Desktop robots P0](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164); existing #83, #114, #107, #77, #133, #110 cross-linked in comments. This governs subsequent **Operación Granada** block selection and overrides earlier choices to prioritize Android Developer tests/English UI/cosmetics ahead of unfinished Windows robot operation.

**P0-A Unfollow:** Source implemented, published versions v120.49–v120.53 contain several fixes, but owner v120.48/v120.49 screenshots established `missing_profile_info` even with a visible Following button, and v120.52 showed 2/40 processed, 0 confirmed with 38 untouched. v120.53 now separates action Run from optional read-only recheck and recognizes `already_not_following`; **no verified owner-live Instagram Following→Unfollow→Follow transition exists**. Continue controlled instrumentation of actual DOM/control identity and no-click vs uncertain-click safety without bypassing challenges.

**P0-B Cancel Pending:** Sequential 3+ batches after overlapping Instagram imports, exact next eligible cohort, correct batch-size 20/30/40 preference/active separation, persistent journal, no replay after ambiguous click, no falsely Reviewed completion. Code shipped v120.48+, BR recovery source merged after v120.53; owner-live test of batches/reimports still **pending**.

**P0-C Chrome session/action recovery:** Separate persistent robot Chrome may show `/auth_platform/recaptcha` loop where ordinary Chrome works. Must not bypass CAPTCHA/copy cookies/retry aggressively. Issue Review Open Profile must share robot's Chrome session; ten eligible tabs and proven pre-click continuation/restart/cooldowns/protected states need installed owner acceptance. BR-01..BR-07 [issue #133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133) integrated into `main` **after public v120.53** and require an independently authorized release before owner can validate new behavior.

**P1 Profile Counts:** Read-only Instagram Followers/Following numeric collection, stored timestamp/precision, oldest-first cycle, pacing and full queue have offline/installed CI, but real signed-in Chrome and correct counts + restart remain unaccepted (#77/#107). PC→Android automatic history sync is not implemented and is not a P0 Windows requirement.

**P1 installed release/updater:** official latest GitHub stable **v120.53** (Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.53.exe` and checksums). v120.54 is a **reserved target, not published or authorized**; source merges do not update the installed robot. Setup install/upgrade preserves data in CI, but owner real in-place update, Authenticode signing (not configured) and physical-session QA remain open (#110).

**Lower priority, parked not erased:** [English PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) blocked by real installed Android Developer Account navigation test on that PR; [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) requires genuine provider/device sign-in. Neither is now the next default GRANADA task, except for unavoidable security/dependency blockers. Never claim offline fixtures verified Instagram real actions or ask Michel to test Actions artifact previews.

**Next implementation sequence:** P0-A exact owner-scope action result/real-control instrumentation and safe browser-session response → P0-B durable batch/reimport advancement → P0-C Chrome session/recovery → P1 read-only counts + installed Windows/backup acceptance, each in independent small-risk branches with exact-HEAD Windows integration/Chromium/safety tests. Any blocked owner-real-session step remains open; pursue another non-colliding Windows robot source task without claiming background work or publication.

## 2026-10-19 — GRANADA #14 Developer audit sandbox and AI prompt redaction integrated

- **GRANADA #14 integrated:** [PR #163](https://github.com/michels-lab/IG-Cleaner-Pro/pull/163), merge SHA `c949d5dc5147728739a174bbc54f63dfd8c41c1d`; [issue #162](https://github.com/michels-lab/IG-Cleaner-Pro/issues/162) closed. Exact PR head `d0a61094e02952c90a580823b675160237f6e1cd` passed **6/6 SUCCESS**: installed Windows Setup, Desktop contracts, Desktop rendered, normal Android compile + installed About UI, Supabase RLS. The local Developer auditor now rejects a symlink root, skips linked action/batch/historical journals without reading outside the intended workspace, and exports only canonical fixed diagnostic codes, descriptions and bounded counts rather than trusting arbitrary text in AI repair-prompt input. Added regression tests for real symlink privacy escape, preserving external owner bytes and filtering synthetic injected paths/usernames/tokens.
- The previous [GRANADA #13 PR #161](https://github.com/michels-lab/IG-Cleaner-Pro/pull/161) was merged with 7/7 checks as `ee961dc2fa7e73b973006d7fb955fe4be93dbbfa`; duplicate/corrupt results CSV no longer silently drops historical data on Profile Counts resume. Both #13 and #14 are **integrated source only**, not new published releases.
- **Still parked, never waived:** Windows English PR [#143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) failed Android Developer Account navigation test on that exact PR; parent physical/provider acceptance [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) and live Instagram robot acceptance [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133) remain open. Developer audit security QA does not itself validate owner login or app runtime action outcomes.
- **Published stable** remains `v120.53`; reserved `v120.54` has **not** been published or authorized. Owner tests only official published assets, never branch/Actions previews. No live Instagram user actions, production data changes or new release were performed.

## 2026-10-19 — GRANADA #13 merged; #14 Developer audit privacy candidate in CI

- **GRANADA #13 source integrated:** [PR #161](https://github.com/michels-lab/IG-Cleaner-Pro/pull/161) merged to `main` as `ee961dc2fa7e73b973006d7fb955fe4be93dbbfa`, [issue #160](https://github.com/michels-lab/IG-Cleaner-Pro/issues/160) closed. Exact PR head `a6f101d4cf6e605175a49135715a165c48a0d557` passed **7/7** CI check families (Profile Counts offline, integrated installed Windows Setup, Desktop rendered/contracts, Android rendered About/build, Supabase RLS). Profile Counts results CSV loader now rejects duplicate normalized usernames, invalid/truncated/malformed rows or extra/unknown/duplicate headers before resuming and rewriting, preserving original bytes; existing BOM/optional legacy formats remain compatible. No Instagram actions performed.
- **GRANADA #14 independent Developer privacy QA pending:** [issue #162](https://github.com/michels-lab/IG-Cleaner-Pro/issues/162), [PR #163](https://github.com/michels-lab/IG-Cleaner-Pro/pull/163), exact candidate head `d0a61094e02952c90a580823b675160237f6e1cd`. The developer read-only audit formerly followed symlinks from `data_root` to unrelated local files and trusted free-form report strings when exporting an AI diagnosis. Fix rejects symlink root, skips linked action/batch/historical journals with aggregate finding codes, and sanitizes AI repair prompts to canonical allowlisted diagnostics, bounded counts, safe revision metadata and fixed limitations. Tests exercise symlink privacy and synthetic injected labels/tokens while preserving original journal files. Desktop contract CI passed; installed Windows and other exact-head checks in progress. This branch does not modify Android Developer provider login or account navigation.
- **Still open/parked:** English UI [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), Android Developer real provider/device acceptance [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135), owner Instagram real action/Chrome acceptance [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133). Source regression coverage is not live owner acceptance.
- **Release boundary:** public stable stays **v120.53**; v120.54 reserved/unpublished, no owner approval to publish. User tests only official published GitHub release assets. No release or production cloud mutation from either block.

## 2026-10-19 — GRANADA #13 Profile Counts result-CSV lossless resume candidate

- New independent [issue #160](https://github.com/michels-lab/IG-Cleaner-Pro/issues/160), [PR #161](https://github.com/michels-lab/IG-Cleaner-Pro/pull/161), exact candidate head `a6f101d4cf6e605175a49135715a165c48a0d557`, branch `granada/profile-counts-safe-csv-recovery-20261019`. **NOT merged, not released** while exact-HEAD CI is ongoing.
- Source problem: Profile Counts `read_results()` previously silently collapsed duplicate rows into a dict, discarded invalid usernames and allowed unknown columns that its next `save_results()` would drop. This could destroy recoverable historic CSV evidence after an otherwise normal resume. The fix validates strict parseable CSV, required/unique/known headers, consistent row length and duplicate canonical usernames; refuses to start collector on corrupted owner history and **never rewrites the original CSV automatically**.
- New `tests/test_granada_csv_recovery.py` covers duplicated identical/case-aliased/conflicting usernames, missing/duplicate/unknown columns, truncated/surplus/malformed CSV, BOM and optional legacy metadata compatibility, and Windows Collector load-only failing without Chrome side effects. Explicit CI gates in Profile Counts Linux and Windows installed Setup workflows. Windows English [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), Android Developer owner acceptance [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135), live Instagram [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133) remain separately blocked; this PR does not touch those.
- Published stable remains **v120.53**, v120.54 reserved/unpublished and no owner authorization to publish. User tests only official published releases, never PR artifacts. Source implementation ≠ merged ≠ published ≠ installed-owner acceptance.

## 2026-10-19 — GRANADA #12 private Android UI evidence merged (6/6 exact-HEAD)

- **GRANADA #12 integrated:** [PR #159](https://github.com/michels-lab/IG-Cleaner-Pro/pull/159), merge SHA `b86ce64ca03c08520405c1bca78043e4188b601d`, [issue #158](https://github.com/michels-lab/IG-Cleaner-Pro/issues/158) closed. Exact candidate head `9b3659fe8f331374d92186f29da276c337ed7602` achieved **6/6 SUCCESS**: installed Android Home/About compact/wide PNG capture and binary-hash evidence, installed Android Developer WebView test, normal Android build, Desktop local app contract, Desktop rendered and Supabase RLS.
- Replaced flaky scoped Android external `adb pull /sdcard/Android/data/...` (observed red after all 12 UI tests green in #11) with installed **debug APK private screenshot storage** using `getFilesDir()`, read via `adb exec-out run-as <debug app package> cat files/igc-ui-capture/<fixed filename>`. New collector refuses stale outputs, missing/invalid image headers and mismatched viewport, and stages **all eight** verified PNGs atomically before existing nonblank image and APK source-hash visual provenance gates. Added independent offline tests and Android visual workflow path triggers/gate; public app runtime not changed.
- Initial #12 CI exposed one implementation error in the fixed screenshot filename generator and a test-only wrong viewport parser reading the parent directory. Both corrected and exact-HEAD reruns verified green. No claims of Android Developer provider OTP/physical-Samsung owner acceptance: [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) remains open.
- **Remaining blocked:** Windows English UI [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) had installed Developer Account navigation failure and is not merged. Passing Developer test in #12 branch does not waive that original exact-HEAD red check or prove cross-platform English translation complete. Follow GRANADA noncolliding independent backlog.
- **Official release:** v120.53 remains published; v120.54 is reserved/unpublished and requires fresh owner publication consent. No actual Instagram login, follow/unfollow/cancel, cloud mutations or release publishing were performed by #12. Owner tests only official published GitHub installers/APK/HTML, never workflow artifacts.

## 2026-10-19 — GRANADA #11 merged; #12 private Android screenshot extraction under full emulator QA

- **GRANADA #11 integrated:** [PR #157](https://github.com/michels-lab/IG-Cleaner-Pro/pull/157) merged into `main` as `1730b1f5fe75c8e050ac01b7eef3969281a88d9a`; [issue #156](https://github.com/michels-lab/IG-Cleaner-Pro/issues/156) closed. Exact PR head `602b07b15be26cc2fb1a0e5aa646ebd0a255a1b7` passed **5/5 check families**, including a **same-commit rerun** of the Android installed About visual job that had originally failed to retrieve its screenshot folder after both sets of `OK (12 tests)`. This is fully integrated source documentation, **not** newly published software.
- **GRANADA #12 active independent fix:** [issue #158](https://github.com/michels-lab/IG-Cleaner-Pro/issues/158), [PR #159](https://github.com/michels-lab/IG-Cleaner-Pro/pull/159), branch `granada/android-private-visual-evidence-20261019` at current head `9b3659fe8f331374d92186f29da276c337ed7602`. Source root: intermittent `adb pull` from scoped external `/sdcard/Android/data` while real emulator UI screenshots were captured. The installed test now writes screenshots to app-private `getFilesDir()`; an explicit `adb exec-out run-as <debug-package> cat files/igc-ui-capture/<name>` helper validates 8 expected PNG signatures and viewport sizes and atomically stages all without allowing stale or partial evidence. Existing rendered-pixels+APK-hash manifest remains mandatory.
- The initial isolated test failed because the new collector's filename comprehension omitted `for section in sections`; corrected. The next test failed because a mock-adb fixture interpreted the slash-containing directory `igc-ui-capture` as a viewport; corrected without relaxing actual evidence checks. Exact head `9b3659fe8f331374d92186f29da276c337ed7602`: **offline transfer unit tests now passed**; installed emulator extraction / Android visual manifest still in progress at this handoff. PR not merged, no new release.
- **Open and separate:** Windows English [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) remains blocked by installed Android Developer Account navigation failing at the exact `#page-sync.active` readiness assertion; issue [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) remains open for genuine provider login/owner physical-device tests. #12 is a screenshot evidence reliability fix, **not** a Developer login/OTP fix.
- **Publication:** official GitHub stable remains **v120.53**; `releasePolicy.nextRelease` v120.54 reserved/unpublished. There is no owner authorization to publish a new release. User reviews/tests only official published GitHub packages, never workflow preview artifacts. No actual Instagram session, follow/cancel action, owner data or production cloud mutation by #12.

## 2026-10-19 — GRANADA #11 Android screenshot extraction gate (exact-head rerun)

- Profile Counts release-guide [PR #157](https://github.com/michels-lab/IG-Cleaner-Pro/pull/157), head `602b07b15be26cc2fb1a0e5aa646ebd0a255a1b7`: 4/5 exact-head CI check families SUCCESS (Desktop, Desktop rendered, Android compile, Supabase RLS). **Installed Android About screenshot evidence initially FAILED after compact and wide instrumentations each returned `OK (12 tests)`**: `adb pull /sdcard/Android/data/com.michelslab.igcleaner.beta/files/igc-ui-capture/` exited 1, so visual screenshot provenance is not established. Do not conflate test pass with screenshot acceptance.
- Re-ran only the failed Android visual job via GitHub Actions job rerun against the exact unchanged PR head; re-run is still in progress as recorded. Root cause may be runner/emulator storage path but is **unconfirmed**. The source documentation fix itself remains pending CI merge.
- Public stable still v120.53, v120.54 unpublished; no release authorized. Owner tests only official published releases.

## 2026-10-19 — GRANADA #9/#10 integrated, #11 release-guide QA underway; Developer #4 still parked

- **GRANADA #9 merged:** [PR #153](https://github.com/michels-lab/IG-Cleaner-Pro/pull/153) to `main` SHA `dc229e38fde26dbaac5bf8798aae36bc3f160ef5`, issue [#152](https://github.com/michels-lab/IG-Cleaner-Pro/issues/152) closed. Exact PR head `3d6abfdfde2b61e4fa11215ac1dbacc7611db69f` passed **7/7** CI check families, including Windows integrated Setup installed smoke, Desktop rendered/contracts, Android About/build, Profile Counts offline and Supabase RLS. Old CSV rows claiming `ok` without numeric/date evidence are no longer skipped or counted as verified; Windows API displays `invalid_evidence` without rewriting the source file. CLI opt-in failure retry behavior unchanged.
- **GRANADA #10 merged:** [PR #155](https://github.com/michels-lab/IG-Cleaner-Pro/pull/155) SHA `9159617e1ca716d9c15d650deee33b5956077e10`, issue [#154](https://github.com/michels-lab/IG-Cleaner-Pro/issues/154) closed. Exact PR head `57d084b7089fb9f7510dd2b05eda342804f8b22f` passed **6/6** CI check families, including installed Windows Setup, Android About/build, Desktop UI and RLS. Dated-history API now flags pre-validation invalid successful readings on read without deleting or rewriting archived CSV bytes or changing pagination. Verified numeric zero remains valid.
- **GRANADA #11 implementation/CI in progress:** [issue #156](https://github.com/michels-lab/IG-Cleaner-Pro/issues/156), [PR #157](https://github.com/michels-lab/IG-Cleaner-Pro/pull/157). The guide `docs/PROFILE_COUNTS_ROBOT.md` incorrectly claimed v120.47 was the current stable and v120.48 unpublished. It now directs readers to the distribution manifest's `releasePolicy.currentStableRelease` and actual official GitHub Releases; historical v120.47 remains identified as historical. New CI guard in `tests/test_update_docs_contract.py`. Initial check failed due test expecting unformatted `not` while guide emphasized the word in Markdown; repaired to plain `not` in PR head `602b07b15be26cc2fb1a0e5aa646ebd0a255a1b7`; latest exact-head CI underway, no merge claim until passed.
- **Still parked:** English Desktop [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) failed installed Android Developer Account navigation check despite passing 7/8 other check families; [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) remains open for real provider/device acceptance. Neither robot live Instagram reliability nor Developer installed owner login can be inferred from offline CI.
- **Release boundary:** Published stable remains **v120.53**, `releasePolicy.nextRelease` v120.54 is reserved/unpublished; no new publication authorization. User tests only official published GitHub installer/APK/HTML, not GitHub Actions/PR build artifacts. These GRANADA merges only change source, not installed owner software.

## 2026-10-19 — GRANADA #9/#10 parallel safeguards; #4 Developer acceptance still red

- **GRANADA #4 remains unmerged:** [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) head `6522f5e02d431ae8e87b8fe0021581fac736f65f` completed 7/8 exact-HEAD check families SUCCESS, including installed Windows Setup and real Chromium account switch; **installed Android Developer APK failed** at `DeveloperEditionTest.untilJsTrue`: *Developer Account navigation did not activate the real sign-in screen; last WebView result: false*. This failure persists even after separate source/test QA PR #151 was merged. Issue [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) and [#142](https://github.com/michels-lab/IG-Cleaner-Pro/issues/142) have exact failure notes. Do not mark Developer acceptance green, bypass the gate, or merge the translation PR based on partial CI evidence.
- **GRANADA #9 implemented but pending final check:** [issue #152](https://github.com/michels-lab/IG-Cleaner-Pro/issues/152), [PR #153](https://github.com/michels-lab/IG-Cleaner-Pro/pull/153) head `3d6abfdfde2b61e4fa11215ac1dbacc7611db69f`: standalone CLI and Windows Profile Counts now verify historical `ok` rows with central dated-evidence predicate rather than trusting raw status. Invalid legacy results are re-queued, excluded from progress and returned as read-only `invalid_evidence` warnings; original CSV bytes preserved. Existing opt-in error retry unchanged. Owner/IG account isolation and valid measured zeros covered. Dedicated Linux Profile Counts/normal Desktop/Android/RLS CI green so far, Windows frozen Setup still running at log time; do not claim merged.
- **GRANADA #10 implemented but pending final check:** [issue #154](https://github.com/michels-lab/IG-Cleaner-Pro/issues/154), [PR #155](https://github.com/michels-lab/IG-Cleaner-Pro/pull/155) head `57d084b7089fb9f7510dd2b05eda342804f8b22f`: paginated old dated Profile Counts history flags invalid success evidence only in **returned response**, without rewriting/removing any rows, changing offsets or marking valid zero as invalid. Tests in existing audit suite. Independent of PR #153; CI still running. No change to live Instagram actions.
- **Public stable remains v120.53**; v120.54 reserved, not authorized or published. User tests only official published GitHub installers/APK, never Actions/PR previews. Live Instagram/Profile Counts acceptance, physically installed signed APK/OTP, and Android Developer account behavior remain separate open gates.

## 2026-10-19 — GRANADA #8 installed Developer QA green, integrated; #4 revalidation requested

- **GRANADA #8 merged:** [PR #151](https://github.com/michels-lab/IG-Cleaner-Pro/pull/151) at `bed5e5eb2e54a690e261bd558a09075b24f64413`. Exact PR head `54a7738c7f099ddf6d533193c87d600bbd317a7e` passed **5/5 checks**, including installed Developer APK with real WebView section notes, reload and Downloads report, Android About visual, Android build, Desktop and RLS. [Issue #150](https://github.com/michels-lab/IG-Cleaner-Pro/issues/150) closed. This repairs the unstable compound developer instrumentation, **not** a claim that user/provider login has been validated on physical Android; parent #135 remains open.
- **GRANADA #4 resumed:** branch [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) head `407a948ff64a3f7de55496205a066f7dff72b77e` now requests new exact-head CI with updated Android Developer test merged into latest `main`. Previous 7/8 verdict is obsolete; **do not merge until new full CI is green**. Windows-only 115 high-traffic English UI occurrences plus five launcher messages remain source changes; full Web/Android embedded-English parity is a separate future block.
- **Public stable unchanged:** v120.53; v120.54 remains unpublished/unapproved. Owner tests official published installers only. Live Instagram action confirmation, genuine OTP/provider sign-in, signed phone install/upgrade and cross-device isolation are separate acceptance tasks.

## 2026-10-19 — GRANADA #7 integrated; #8 Developer installed QA pending

- **GRANADA #7 source integrated:** [PR #149](https://github.com/michels-lab/IG-Cleaner-Pro/pull/149) merged into `main` as `679a377b54465193bd841f73e74ce15974eb5397`; [issue #148](https://github.com/michels-lab/IG-Cleaner-Pro/issues/148) closed. Exact PR head `830f2dc747bfd7891f4e6a2dee25cdfc96d6cb80`: **6/6 SUCCESS**, including Desktop/Android/RLS, actual Windows integrated Setup install/uninstall and historical Profile Counts audit regression. Existing valid historical evidence remains byte-preserved. False successful rows with bad number/date/username no longer append to the dated journal or count as successfully measured when prioritizing next read-only re-audit.
- **GRANADA #8 remains separate:** [PR #151](https://github.com/michels-lab/IG-Cleaner-Pro/pull/151), [issue #150](https://github.com/michels-lab/IG-Cleaner-Pro/issues/150). Android Developer installed WebView test was split into observable readiness/navigation, precise section targeting, note persistence, actual reload and native Downloads export with bounded polling. Await the full exact-head emulator verdict; no inference of real OTP/physical Android acceptance. [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) remains parked with red Developer CI until actual independent evidence is reconciled.
- **Still:** published stable v120.53, reserved next v120.54 not published or authorized by GRANADA. Owner tests only official GitHub stable installers/releases. Live Instagram outcome/Owner Windows acceptance and Android Developer provider login still require post-release physical checks.

## 2026-10-19 — GRANADA #6 integrated; #7 evidence QA and #8 Android Developer instrumentation isolated

- **GRANADA #6 merged:** [PR #147](https://github.com/michels-lab/IG-Cleaner-Pro/pull/147) into `main` as `ff9ef4706f216d0ade2106520e1bca810988cd7a`. Exact candidate head `3d42c6c109474ebab07cef3f928d2b8d8c7e851f` had **7/7 SUCCESS** including Profile Counts offline, Windows frozen Setup installed smoke, Desktop render/contracts, Android About/build, and RLS. [Issue #146](https://github.com/michels-lab/IG-Cleaner-Pro/issues/146) closed as source-implemented. Persisted visit/rest JSON with malformed but parseable entries now fails closed without wiping original cooldown journal. Genuine expired visits still prune in memory. No CAPTCHA bypass or Instagram relationship actions.
- **GRANADA #7 pending merge:** [issue #148](https://github.com/michels-lab/IG-Cleaner-Pro/issues/148), [PR #149](https://github.com/michels-lab/IG-Cleaner-Pro/pull/149), head `830f2dc747bfd7891f4e6a2dee25cdfc96d6cb80`. Distinct `tools/profile_counts_audit.py` and `tests/test_profile_counts_audit.py` harden valid measurement evidence (ASCII integer pair, IG username, timezone-aware non-future timestamp) before append-only date migration and treating a row as successfully measured. Tests prevent false `ok`, preserve prior CSV bytes and support verified numeric zero. Desktop/Android/RLS and Profile Counts tests passed; Windows installed Setup exact-head completion pending. Earlier invalid historical rows are NOT destructively rewritten. No release authorized.
- **GRANADA #8 pending installed Android Developer QA:** [issue #150](https://github.com/michels-lab/IG-Cleaner-Pro/issues/150), [PR #151](https://github.com/michels-lab/IG-Cleaner-Pro/pull/151), head `54a7738c7f099ddf6d533193c87d600bbd317a7e`. Replaces ambiguous compound `evaluateJavascript` navigation/pick/save in real Android Developer instrumentation with explicit bounded state assertions; still tests original real WebView, account page, exact locator, saved note across reload, native Downloads export and no cloud mutation. Android Developer emulator full result pending. This does not establish actual provider OTP login or physical owner Samsung acceptance; parent #135 remains open.
- **GRANADA #4 still parked** [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143): 7/8 checks; Android Developer check red, not merged. Treat #8 as a separate diagnostic, never waive the failing check.
- **Release gate:** published stable remains **v120.53**; reserved v120.54 not authorized or published. Michel tests ONLY official published release assets, never GitHub Actions previews. Live Instagram and cross-device provider acceptance (#133/#135/#107/#77) remain distinct open gates.

## 2026-10-19 — GRANADA #5 merged; #4 parked for Android Developer instrumentation

- **GRANADA #5 complete source integration:** [PR #145](https://github.com/michels-lab/IG-Cleaner-Pro/pull/145) merged to `main` at `fe9a32bffa8909109c5d4ae6ecf29c7bdc6123ae`; [issue #144](https://github.com/michels-lab/IG-Cleaner-Pro/issues/144) closed. All five exact-head checks at `4c7adab872f4d00c039c9467cc32ff2348c4f1c7` **SUCCESS**: Desktop app contracts (including new release-agent guard), Supabase RLS, Android build, installed About screenshots and rendered Desktop. Removed stale v120.35/v120.36 as current/next from live release agents; all future publication requires manifest current/next, real GitHub Releases and fresh owner authorization.
- **GRANADA #4 still NOT merged:** [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), head `bbc6456d92671e3765db6a71288961c64b2c9d98`: 7/8 exact-head checks **SUCCESS** (Desktop contract, Chromium/offline, Windows installed Setup, Android build, Android About, Supabase RLS, Desktop rendered); **Android Developer Edition installed WebView instrumentation FAILURE** (`DeveloperEditionTest.realDeveloperBuildSupportsAccountNotesAndRestart`, expected `true`, got `null`; existing issue [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135)). That failure is NOT proof the Windows English patch broke Developer Android: the English PR does not change Android source or embedded workspace. Nonetheless, do **not** treat 7/8 as all-green, do not merge or release the candidate until accepted under proper QA; log and return separately under #135. Windows-specific text and tests corrected historical Spanish assertion expectations without weakening account/instance guards. Other Web/Android full-English parity still remains pending.
- **Release status:** official public stable stays **v120.53**, v120.54 reserved/unpublished. The user validates only official published assets; no Instagram live action, real OTP/login on the owner's device or production upload was performed by these blocks. GRANADA resumes at next independent noncolliding task while #143/#135 remains parked.

## 2026-10-19 — GRANADA #3 integrated; #4/#5 independent branches (QA pending)

- **GRANADA #3 — finished:** [PR #141](https://github.com/michels-lab/IG-Cleaner-Pro/pull/141) merged as `6675122fa0d2d3396ff1ba40a15851babb646f8e` after all 5 exact-head CI check families passed. [Issue #140](https://github.com/michels-lab/IG-Cleaner-Pro/issues/140) closed. `docs/UPDATE_AND_STATE_MIGRATION.md` now correctly identifies the published stable v120.53 and reserved unpublished v120.54, with `tests/test_update_docs_contract.py` guarding against future mismatch.
- **GRANADA #4 — development candidate, NOT merged:** [issue #142](https://github.com/michels-lab/IG-Cleaner-Pro/issues/142), [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143). Scoped English runtime cleanup: 88 selected UI strings / 115 occurrences in Windows/Desktop, five Windows launcher startup/errors. Preserves serialized legacy `pendiente/vacío`, Instagram Spanish relation recognition, app auth and robot action logic. Added translated-label and persistence regression suite. Initial CI found outdated Spanish regex in `tests/multi-instagram-contract.test.cjs` and `tests/test_native_desktop.py`; those assertions were updated to validate the same safety boundaries against English copy. Exact-head recheck remains running, including Windows installed Setup and Android Developer. A prior Android Developer run hit a WebView-instrumentation `expected true, got null` failure in a separately owned area; do not mark accepted or modify Android as part of this English-only PR. **Public Web `index.html` and embedded Android workspace NOT translated in this pass; cross-platform English parity is a separate pending block.** Dedicated log in PR branch `docs/GRANADA_04_DESKTOP_ENGLISH_RUNTIME_2026-10-19.md`.
- **GRANADA #5 — development candidate, NOT merged:** [issue #144](https://github.com/michels-lab/IG-Cleaner-Pro/issues/144), [PR #145](https://github.com/michels-lab/IG-Cleaner-Pro/pull/145). Removed stale v120.35/v120.36 current-publication directives from active GitHub agent/Copilot instructions, binding release decisions to `releasePolicy.currentStableRelease`, `releasePolicy.nextRelease` and verified official GitHub Releases. New CI contract prohibits stale hard-coded agent claims; first candidate failed its new guard due missing explicit generic publisher path, repaired on the isolated branch. Exact-head recheck ongoing. Dedicated log in PR branch `docs/GRANADA_05_RELEASE_AGENT_GOVERNANCE_2026-10-19.md`.
- **Do not conflate:** current released stable remains **v120.53**; v120.54 **not** published or authorized by these blocks. Owner only tests official published assets, never Actions previews. #133 robot live Instagram and #135 Developer physical/provider acceptance remain open. No user data, Instagram actions, release assets or production secrets modified by these branches.

## 2026-10-19 — GRANADA #2 integrated; GRANADA #3 version-guidance PR in independent QA

- **GRANADA #2** [PR #139](https://github.com/michels-lab/IG-Cleaner-Pro/pull/139) merged into `main` as `490313a3b23712ff7e05fbe79a93ac82188bd274` after 6/6 exact-head checks SUCCESS: verified Windows updater offline tests, actual frozen executable, installed Windows Setup smoke, Desktop, Android rendering/build, Supabase RLS. ZIP pre-Setup snapshot includes per-file SHA-256 manifest, rejects missing/duplicate/unsafe/corrupt members, excludes linked files and re-verifies before launching Setup. **No new GitHub release** and no physical-owner Windows upgrade acceptance claimed (#110 stays open).
- **GRANADA #3** [issue #140](https://github.com/michels-lab/IG-Cleaner-Pro/issues/140), [PR #141](https://github.com/michels-lab/IG-Cleaner-Pro/pull/141) isolates stale update guidance (v120.44 mislabeled current despite public v120.53); updates text and adds automatic docs-vs-manifest version contract. CI pending; do not call merged/shipped until verified.
- GRANADA #1 Focus [#137](https://github.com/michels-lab/IG-Cleaner-Pro/pull/137) already integrated as `c44589d6855f0b8bacd07d336edcb8f0d8dbe3a9`. Live Instagram/Android Developer acceptance (#133/#135) remains distinct. Stable **v120.53**, reserved **v120.54**. Owner tests only official published release assets, not branch previews.

## 2026-10-19 — GRANADA #1 Focus priority pool integrated; #2 isolated updater QA in progress

- **GRANADA #1** Focus previews PR [#137](https://github.com/michels-lab/IG-Cleaner-Pro/pull/137) merged into `main` at `c44589d6855f0b8bacd07d336edcb8f0d8dbe3a9`. Exact PR head `ee453fabc11538a8d317e8621dbef317a811f04f` had 8 of 8 GitHub checks SUCCESS, including installed Windows Setup, Profile Counts offline, Desktop, Android About and Developer runtime. A 20/30/40 Focus batch now fills from all eligible priority categories rather than stopping at the first tier. This is **source-integrated, not a new release**; installed owner acceptance is separate.
- **GRANADA #2** independent updater safety task [#138](https://github.com/michels-lab/IG-Cleaner-Pro/issues/138), PR [#139](https://github.com/michels-lab/IG-Cleaner-Pro/pull/139) on `granada/windows-verified-restore-points-20261019`. Validated local robot/UI ZIP snapshots with checksums before launching Windows Setup; separate source and tests, no changes to Focus, Instagram robot or Developer. Exact-head CI **in progress**, do not mark merged or released. Dedicated log: `docs/GRANADA_02_WINDOWS_RESTORE_2026-10-19.md` (in PR branch).
- Stable remains **v120.53**; next v120.54 reserved. Owner tests installed official releases only, **not** Actions previews. Open #133, #135 and real-session issues remain unclosed until release/device acceptance. No GitHub release publication was requested by this GRANADA continuation.

## 2026-10-19 — BR-01–BR-07 implementation merged: PR #134, release not authorized

- **Merged product source**: PR [#134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134) into `main` at `8df8f3b27747b0ba1ccfd896664676223219f4ac`. This replaces the previous document-only candidate status for BR-01..BR-06; the original owner bug #133 is still open for actual release acceptance.
- **Robot**: persistent batch-size UI selection, same persistent robot Chrome session for manual Issue Review, safe no-click retry/advance, distinct terminal `already_not_following`, historical read-only re-audit and journal history retention, clearer counters. New backend guard refuses approval while targets remain *untouched* (but permits explicitly recorded uncertain targets to remain unresolved, never Reviewed).
- **Developer twin**: Windows launcher (`--developer`) with separately isolated workspace/session, same public login workflow, anchored persisted annotations and sanitized JSON/AI prompt audit export; Android separate `.developer` package, installed real WebView/UI tests, annotations and native Downloads export. Production cloud writes are blocked at relevant Developer native/browser boundaries. Source code does **not** prove real OTP provider login or installed physical-device acceptance.
- **Exact PR head CI** `8f725d109170862afc2aefaa8ac42039a6a465ee` all eight checks **SUCCESS**: Desktop local-app, Supabase RLS, Android build, Android About installed emulator, Android Developer installed emulator, Windows integrated Setup install/runtime, Desktop visual, Profile Counts offline contract. During QA corrected two obsolete Android contract assertions and added a backend regression refusing premature batch approval. New `main` merge SHA is separately verified; record post-merge CI separately when available.
- **Still NOT released**: current public stable remains **v120.53**. v120.54 neither authorized nor published. Michel uses official stable releases for testing, not branch builds or Actions artifacts. Live Instagram following/unfollowing, original user session reliability, real OTP/account switching on physical Windows/Android, Samsung acceptance and signed public Developer APK distribution remain external/product release acceptance work. No bypass of Instagram challenges or uncertain clicks.
- **Documents**: detailed [BR-01–BR-07](PENDING_BLOCK_ROBOT_RECOVERY_DEVELOPER_TWIN_2026-10-19.md) remains historical acceptance spec. Issues #133 and #135 remain open until real installed-release and provider acceptance.

## 2026-10-19 — Developer real-login preservation: OTP, device registration and production write barriers

Found a **real user login regression** caused by trying to perform production writes from an otherwise read-only Developer Edition. A valid native Android password or OTP login was followed by `touchDevice()` (Supabase device upsert) and thus could appear failed despite authentication. Both normal-user auth and production safety are now separate:
- Android `MainActivity.touchDevice()` intentionally returns without production upsert only in the standalone `.developer` package. Public app registration remains unchanged.
- Android `SyncApi.verifyOtpAndSetPassword()` still verifies a real OTP and keeps the developer session, but skips the production Auth password update in Developer; ordinary public app still updates the password as before. Visible native success copy explicitly says the password was not modified.
- Desktop/Android shared Web `verifyOtpAndSetPassword()` likewise authenticates with a real OTP but bypasses Auth password PUT in Developer only, and reports that accurately. Read-only cloud RPC boundary restrictions remain intact. An added Node regression test verifies *Developer OTP does not PUT Auth user* while *public OTP does*.
- The first installed Android Developer emulator run reached and **passed native guard tests**, then exposed a test race at line 101 while `location.reload()` was replacing the WebView document (a JavaScript evaluation returned `null`). The UI test now requires actual new-document context and restored notes, instead of treating the outgoing page as ready. **Final Android Developer installed test on the updated head is still pending**; do not claim Android Developer accepted/released.
- Previously verified: Windows installed Setup + Desktop visual + Profile Counts + ordinary Android About tests passed for earlier candidate revision; live owner Instagram, OTP provider physical-device delivery and real UI sign-in remain acceptance gaps.

Implementation remains in draft [PR #134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134), release not published, issue [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) open. No owner-created release request issued this block.

## 2026-10-19 — Historical no-click re-audit scale + Developer Android native guard (large-block continuation)

**Scope:** draft PR [#134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134), not merged/released. Windows user tests must use official stable release only; v120.53 remains the public version, and v120.54 is still a candidate.

- Re-audit historical failures: `recheck_action_readonly(..., allow_unacted_observation=True)` now allows **previously proven pre-click failures** to be inspected, explicitly describing a *current visible relationship state* without claiming an Unfollow/Cancel action succeeded. No relationship-changing button is clicked; original action journal remains intact.
- Scalability: `recheck_history` prioritizes profiles never previously re-audited and rotates older unresolved observations rather than endlessly reopening the first 1,000 records. Already observed not-following profiles are omitted from redundant later historical scans. A new action is never inferred from a later read-only observation. Python fixtures test multi-page rotation, protected users, original-byte preservation, no-click classification and the AI report's redaction.
- Android Developer security: `SyncApi` now enforces production cloud-write denial at the **native HTTP request boundary**, not just JavaScript buttons. Auth password/OTP/session login and read-only queries remain available. Emulator test validates this pre-network guard, plus WebView note retention and downloaded combined JSON report.
- CI evidence: exact branch revision `15f1f7b7` passed Profile Counts, Desktop UI, Android About and installed Windows Setup. Next revision corrected the Android Gradle `testBuildType` selection; source tests then reached an installed Developer APK, and **native cloud-write guard test passed**. The sole Android Developer WebView test failure at `da59613b` was `null` during a page reload race; the instrumentation now explicitly waits for a fresh document before testing note restoration (`44df132d`). Await exact-commit validation; do **not** mark Android Developer ready until full instrumentation passes.
- Developer QA/limitations: real Supabase sign-in provider on physical devices, Chrome account mutation verification, uninstall/update preservation on user's PC, actual Android device and original Instagram pending/follow state remain owner acceptance items. Android audit scans UI only, not Windows journals.

**Open:** issue [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133), Android Developer [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135), broader physical/sync issues #24/#73/#77/#83/#107/#110/#114; no new stable release authorization.

## 2026-10-19 — Historical robot failures: automatic READ-ONLY re-audit (candidate)

- **Source:** draft PR [#134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134). New **Re-audit old failures (read-only)** control in Automations operates on the selected owner + Instagram workspace + task, selecting historical `review/error/blocked` action records automatically. It confirms the operation **once for the whole set**, opens the verified persistent Chrome session, and runs only `recheck_action_readonly` without another relationship click. The original action journal is unchanged. Protected profiles are excluded.
- **No phantom Reviewed or success:** historical observations are saved separately under `instagram-actions-<scope>-historical-rechecks.json`, never as new Unfollow successes or reviewed approvals. An observed `Follow / Follow Back` state records `observed_not_following` at inspection time, NOT proof that a prior Unfollow was clicked. Unverifiable results remain `still_unresolved`. All outcomes keep bounded per-profile timestamps; the summary API returns only counts and the UI clearly labels historical read-only progress separately from the normal action batch.
- **No 10-tab deadlock in read-only:** all genuinely read-only inspection tabs now close safely whether or not an earlier action is ambiguous. Tabs with ambiguous *new* relationship-changing results still remain protected against replay. No CAPTCHA bypass.
- Developer audit excludes historical observation ledgers from action journal counts and reports aggregated historical observations without names or raw account data. New `tests/test_historical_recheck.py` and Automations execution assertions cover owner confirmation, original journal immutability, protection, distinct observation labels, JSON/AI redaction, and no per-profile action approval.
- **Validation pending:** source changes are not an official stable release; offline fixtures and exact-head CI have not yet established live Instagram acceptance. Last stable remains **v120.53**; v120.54 is reserved/unpublished. Keep #133 open until real installed release + owner acceptance.

## 2026-10-19 — Large pending-block continuation: Windows robot + two Developer twins (candidate, no release)

**Authoritative worktree:** draft [PR #134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134), branch `fix/owner-qa-133-automation`. Latest published stable **v120.53**, v120.54 reserved, not authorized for publication. Owner tests only official published stable releases, never PR/Actions artifacts.

**Owner acceptance contract now applies to both Windows and Android Developer Editions:** same actual app UI/engine and ordinary real user login/account switching; independent installed local storage/session; select specific visible UI sections *including controls without IDs* and attach exact user-authored notes (edit, delete, locate, persistent scoped history); export automatic findings plus owner comments and exact section locator in TXT AI-repair prompt or JSON. Explicitly distinguish user-reported observations from automated evidence, and prompt before exporting potentially private comment wording. Cross-app requirement is permanent in `michels-lab/Michel-Software-Standards/standards/DEVELOPER_TWIN_AUDIT_STANDARD.md`.

**Windows changes in this PR:** batch-size edit no longer reset by polling; metrics wrapped; safe no-click retry journals original attempt history; an unvisited prefetched tab is not a completed review or an ambiguous clicked action; manual issue-opening uses the persistent robot Chrome profile after app restart; the Developer shortcut runs `--developer` with separate app-data/browser workspace and read-only diagnostic endpoints. Existing public Account OTP/password flow retained; production cloud mutations blocked while developer audit is active. Regression tests for no-click classification, annotated section persistence/export, read-only cloud gate and installer startup added. **Real Instagram account outcomes and owner Windows live session acceptance are unverified.**

**Android Developer implementation added in this block:** new Gradle `developer` build type with **`com.michelslab.igcleaner.developer`** identifier, separate name and package-local WebView/native session cache; native startup enters the same complete Workspace UI and exposes `AndroidBridge.isDeveloperMode()` only on that distinct APK. Original public native Account/OTP/password UI remains available; shared WebView Developer console activates without requiring a Windows robot capability; local read-only UI/DOM/runtime audit and TXT/JSON exports use the existing Android `AndroidBridge.saveBase64` + MediaStore Downloads. Developer web sync rejects production table writes; native bootstrap auto-sync is disabled in Developer and header Sync is guarded. A separate Android emulator CI workflow is added, with instrumentation to verify real Developer UI, native Account route, section note and restart persistence and actual exported JSON. **Do not describe this as live-device/production-provider verified until exact-SHA instrumentation passes.** Android normal app package, signing and release identities remain unchanged.

**Source regression caveat and repair:** modified section selector initially broke an offline mock expecting a panel ID; updated the mock for the actual selector. The selector now stores a precise CSS structural path for id-less controls under a stable ancestor, instead of silently reducing a comment to the entire page. Missing targets are flagged unresolved after an update. Android public About screenshot suite retains its native UI gate (new Developer-only test is skipped in ordinary debug flavor, test count adjusted).

**Open acceptance work:** exact-head Windows Setup/installed runtime, Desktop visual, Profile Counts, Android About and Android Developer emulator CI, real user account login on both platforms, real Instagram relation changes, production cloud sync isolation, and historical account-scoped batch reconciliation. [Issue #133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133) and [Android Developer #135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) remain open. No source test or simulated browser fixture proves live Instagram Unfollow success. No release publication authorized.

## 2026-10-19 — Developer Edition annotations + normal sign-in (owner requirement; development candidate)

**Request:** all Michel's Lab Developer Editions must include the **same real end-user sign-in/switch-account flow** as the public app, plus an interactive tool to point to **specific screens/sections/controls** and save the owner's exact description. The section/locator and observation must survive restart and be included alongside automatic errors in JSON and AI-ready text exports. This is now a permanent cross-project rule in `michels-lab/Michel-Software-Standards/standards/DEVELOPER_TWIN_AUDIT_STANDARD.md`, reflected in global rules, master log, new-app checklist, and cross-project memory.

**Source implementation:** branch `fix/owner-qa-133-automation`; draft PR [#134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134). The installed Windows app adds an optional Start Menu **Developer Edition** shortcut (`--developer`) using the same app UI engine but separate Chrome workspace/HTML origin, process mutex and local audit scratch. Its **Sign in / Account** control opens the actual existing `page-sync` auth flow (no fake login or automatic cookie transfer). Owner's local annotations store a screen → section → control locator, comment, creation/update timestamps, scope by app login/Instagram workspace and edit/delete/locate functions. Audit includes local action-journal state and client DOM/runtime counts; TXT AI prompt and JSON export include the verbatim owner notes as **user-reported observations**. The developer loopback API blocks Instagram action and updater mutation endpoints; the source-only audit does not claim actual live Instagram outcomes. **Important:** the existing Supabase Account flow authenticates to the real service; it is not a fake sandbox. Production cloud-sync effects require explicit provider testing and further isolation review.

**Other issue #133 candidate changes:** a single scoped timing hydration replaces constant polling overwrites; normalized counters wrap; a proven pre-click error can advance to next target without erasing previous journal entries; issue/profile opening requests the action robot's persistent Chrome user-data-dir rather than the system default; UI distinguishes safe no-click technical recoveries from genuinely uncertain manual cases. Ambiguous potentially clicked actions are never automatically replayed.

**Validation:** tests added `tests/developer-annotations-contract.test.cjs` and `tests/test_developer_audit.py` and wired into CI/Windows workflow. Full exact-head runs, installed Windows developer launcher, real account login, Android developer parity and live Instagram actions are **NOT YET VERIFIED** as of this development log entry; don't claim a release until gates complete. Last published stable remains [v120.53](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.53), current candidate target reserved v120.54. User tests **only official published stable releases**; never request branch/PR/Actions previews.

**Next gates:** inspect exact-head tests and fix failures; verify original normal login/Android unchanged; runtime QA for actual Developer UI/notes/export and isolated user profiles; reconcile old issue #133 unresolved historical runs, stale session/counters, cloud state safety. Do not mark issue #133 closed or create release from this entry.

## 2026-10-19 — PENDIENTES ABIERTOS: QA real de InstaCleaner (sin cambios de código)

**Registro:** [GitHub Issue #133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133). El propietario pidió expresamente **"guarda todo en bitácoras de pendientes y limón"**: archivar los pendientes y **DETENER el desarrollo/release por ahora**. Esta entrada es de seguimiento, NO indica que los errores estén resueltos ni autoriza v120.54. Las capturas fueron suministradas en el chat, no se han publicado ni añadido datos personales/sesiones a GitHub.

**Evidencia reportada tras la publicación de v120.53 (la captura no muestra el número de versión instalado):**
1. **P1 — Batch size**: cambiar el tamaño termina regresando automáticamente a `40` en la UI; investigar persistencia y refrescos de estado, sin modificar en silencio una tanda activa.
2. **P1 — Bloqueo del robot**: estado `review` porque la sesión Instagram no pudo verificarse **antes de hacer clic**; quedan **8/10 pestañas `prefetched`** y el proceso no avanza a los siguientes perfiles. El robot debe registrar y reintentar lo seguro, continuar con otros perfiles elegibles cuando haya certeza de cero clics; suspender únicamente ante challenge, identidad contradictoria o acción de resultado ambiguo. La falla de la verificación automática no debe trasladar trabajo perfil por perfil al usuario.
3. **P1 — Chrome manual ≠ Chrome automático**: `Issue Review → Open profile` abre un navegador sin el login activo de Instagram. Debe enfocar/abrir usando **la misma sesión persistente autenticada** del robot, evitando reingreso y sin compartir secretos.
4. **P1 — Reauditoría automática de fallos anteriores**: en tandas previas aparecen cuentas como `Already attempted · inspect journal` y también estados `Already not following`. El usuario pide **que los fallos técnicos se vuelvan a comprobar automáticamente**, no una revisión manual uno por uno. `Attempted`, `opened`, `prefetched` y `robot error` **no equivalen a `Reviewed` ni a Unfollow confirmado**. Reintentar acciones solo donde el journal pruebe **que jamás hubo clic**; si un clic pudo efectuarse, permitir únicamente revalidación read-only para evitar duplicación. Conservar historial, decisiones, fechas y scope.
5. **P1 — Conteos/paneles inconsistentes o confusos**: `Queue 813, Ready 811, Already attempted 2`; `40 in batch, 0 verified, 2 issues, 38 untouched`; `Issue Review 1 pending reviews · 2 issues` mientras progreso muestra `Processed 0/0`. Distinguir claramente tanda actual vs historial vs aún no intentados; no inflar Reviewed o Confirmed.
6. **P2 — Legibilidad**: counters concatenados sin espacios (`Queue 813Ready 811Protected...`, `Processed 0/0Unfollows confirmed...`). Ajustar separación/responsividad sin rediseñar.

**Reglas que no cambian:** cuando se comprueba `Follow / Seguir / Follow Back / Seguir también` para el perfil exacto, registrar `already_not_following` (SIN clic) y avanzar; no repetir jamás Unfollow/Cancel inciertos; conservar protecciones, historial y exportaciones; la aprobación de `Reviewed` es del usuario y solo sobre evidencias verificadas. Michel **prueba únicamente instaladores del release oficial publicado**, jamás previews de GitHub Actions. **Estado:** pendientes registrados, no implementados, no probados, no publicados. Continuar solo después de nueva instrucción del usuario.

**Próxima tarea cuando se autorice:** revisar las implementaciones de guardado/poll de batch size, apertura de enlaces frente al Chrome persistent context y reconciliación de `action_results`/journal/recheck en cohortes antiguas. Añadir pruebas regresivas de owner/session y recuperación segura antes de empaquetar una versión, sin tocar releases ahora.

## 2026-10-19 — Verified official stable v120.53 published

- Michel tests only official published releases; no previews. After owner screenshot v120.52 (2/40, 0 confirmed), PR #130 corrected Run inadvertently switching to read-only recheck for unfinished batches. PR #131 aligned v120.53 version artifacts and release notes, while PR #132 adds **verified already-not-following automatic advance**: require exact target visible identity, Follow/Seguir or Follow Back/Seguir también, no Unfollow click, close safe tab, advance, distinct terminal journal status and separate progress count. Ambiguous actions are not retried.
- Every PR head passed five families: Windows integrated Setup/real offline Chromium fixtures, Android About rendered emulator UI, Desktop rendered Chromium UI, Profile Counts and general CI. Final governed release run [39299032190](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39299032190) SUCCESS from exact SHA `5dba9f140298a14194baa4f1d031bbb1b3935f7c`, including Windows native installer startup/upgrade/uninstall, signed original-production-identity APK, same-commit render proofs, SHA256SUMS and asset checks.
- **Official published stable** [v120.53](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.53), published 2026-10-19T18:09:22Z with `draft=false,prerelease=false` and nine verified assets, including `IG-Cleaner-Pro-Windows-Setup-v120.53.exe`, `IG-Cleaner-Pro-Android-v120.53.apk` and Desktop standalone HTML.
- Post-publication authorization consumed (`authorized=false,status=published`) and distribution policy updated to stable v120.53 with v120.54 reserved, not auto-authorized. Existing local journal/imported data must be preserved on Setup upgrade. **Actual live Instagram behavior and relationship changes still require Michel's post-release owner testing**; CI's offline Chromium fixtures do not prove actual Instagram Unfollow success. No CAPTCHA bypass or unsafe replay.

## 2026-10-19 — Owner requirement: auto-advance when profile is already not followed

- When the exact Instagram target profile is verifiably showing `Follow / Seguir` or `Follow Back / Seguir también`, it is **already not followed** by the selected signed-in owner. InstaCleaner must **make no Unfollow click, close that successfully classified tab and automatically continue to the next eligible account**. This includes former mutuals whose banner says "Follows you" while the actual relationship control shows Follow Back.
- Do not interpret sidebar recommendations, follower-count links, a blank/loading header, a wrong-account session or mismatched target URL as a known non-follow state. The exact-profile, signed-in-owner and uniquely scoped action control checks still apply. Require repeated visible readings during Instagram hydration; if ambiguous, retain existing fail-closed logic.
- Store distinct terminal outcome `already_not_following` instead of reporting an actual successful Unfollow. Count completed/no-action profiles separately from real Unfollow confirmations, exclude both terminal outcomes from next-batch replay, allow whole-batch explicit owner approval of verified non-follows and do not count them as Issue Review errors. Optional read-only recheck preserves no-click semantics.
- Chromium offline fixtures now cover English and Spanish initial Follow / Follow Back, delayed rendering, unrelated sidebar Follow decoys and the "Follows you" case. Python account-scoped history and Desktop approval-panel contracts validate that these profiles are terminal and their tabs are released without clicks.
- Work is additive to merged v120.53 candidate; **do not claim the successor public stable is published until the official release pipeline has passed and GitHub assets are verified**. Michel tests installed official stable releases only, never previews.

## 2026-10-19 — Prepare official stable v120.53 after post-release v120.52 action-mode regression

- Merged fix [PR #130](https://github.com/michels-lab/IG-Cleaner-Pro/pull/130) at `bc2fa492747c4029525b9cf3dd592eaf6a110779` after **five passing** exact-head workflow families: Windows Setup install/Chromium, Desktop, Android, Profile Counts and general CI.
- Functional source root: Run directed incomplete owner-unapproved batch to the read-only recheck API. Real owner screenshot: 2/40 processed, 0 verified, 2 issues, 38 untouched. Corrected to continue exact persisted batch in action mode for untouched and proven-zero-click targets, with explicit user approval before fresh account changes. Never retry ambiguous/clicked actions, and keep read-only verification opt-in. Source tests cover behavior.
- Candidate release metadata v120.53, original production Android identity, Desktop UI v120.53 and release notes. User tests only **official published GitHub stable release**, not previews or ZIPs. CI alone does not demonstrate Instagram unfollow success; owner will validate on official installer.
- Current official release remains v120.52 until governed v120.53 publishing completes and the full nine public assets/checksums are verified; do not claim premature publication. Distribution manifest nextRelease authority is v120.53.
- The owner's earlier instruction to finish and release, and not require preview testing again, is treated as a standing request for the immediate v120.52-regression hotfix; an independent guarded publication commit still requires exact candidate CI before activating it.

## 2026-10-19 — Owner live v120.52: opened Chrome profiles, zero verified actions (post-release defect)

- Screenshot from official installed v120.52: `Processed 2 / 40`, `Confirmed 0`, `Errors/review 2`, `Remaining 38`, pending **Is this batch OK?**. Owner reported profiles opened with no Unfollow. This screenshot alone does not prove which particular DOM selector failed or whether a relationship click happened; inspect full Issue Review messages for that distinction.
- **Source-confirmed functional bug:** Desktop `igcAutoStart()` treated ANY unapproved batch as a mandatory `igcAutoRecheckBatch()`, which calls `/api/actions/recheck-batch` with `review_only=True`. `recheck_action_readonly()` never clicks Unfollow or Cancel Request, including for the 38 never-attempted targets. This is why pressing Run could repeatedly open profiles without carrying out the remaining actions. The previous PR #128 intentionally enabled safe recheck but incorrectly made it the Run default.
- **Fix candidate:** `Run` uses the same persisted cohort and batch ID, requires an explicit owner action confirmation, and calls the normal relationship-changing action endpoint only for targets with NO earlier attempt. Every already attempted record (including proven no-click issues within this cohort) is kept and skipped during continuation; uncertain post-click records are never replayed. New read-only verification remains opt-in and visibly labeled **Verify previous actions (read-only)**.
- The robot can continue past a **proven no-click** `profile_load_timeout`: close only that safely unclicked tab, persist its issue, and advance to other untouched targets without requiring owner-by-owner profile opening. Ambiguous click tabs remain open and stop the job; challenge, identity mismatch and account safety gates remain fail-closed.
- **UI:** show whether running actual actions vs read-only checking, distinguish never-attempted from issues; disable approval while untouched targets remain; **Open only issue profiles** no longer opens 38 not-yet-checked profiles.
- **Owner acceptance contract:** Michel tests only the subsequently published official release, not an Action preview. Real Instagram relationship changes are NOT proven by synthetic Chromium tests. Do not publish until exact-source Windows Setup/Chromium, Desktop, Android and general CI pass and the owner authorizes the next governed stable release. Keep current stable v120.52 intact until then.

## 2026-10-19 — v120.52 stable officially published and verified

- Owner's explicit release-first acceptance rule remains binding: Michel tests the actual stable release only, never temporary Actions previews. Do not request a preview installation for acceptance.
- Candidate release PR #129 merged from exact head `a641b78f190f9cec47053aeab0d52f518a167dc3`; all five workflow families SUCCESS (Windows installed Setup/Chromium, general CI, Profile Counts, Desktop visual, Android emulator visual).
- Authorized via isolated main commit `4db21aaf634d43062e191ae6b9408d86c690f05e`. Governed publication run [39254170073](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39254170073) SUCCESS: rendered UI evidence, Windows Setup install/launch/uninstall, original stable signing Android APK, integrated package and SHA-256 checksums.
- Official GitHub stable [v120.52](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.52), published `2026-10-19T12:48:35Z`, `draft=false`, `prerelease=false`, **nine real assets**, including `IG-Cleaner-Pro-Windows-Setup-v120.52.exe`, `IG-Cleaner-Pro-Android-v120.52.apk`, Desktop HTML/ZIP, optional portable robot ZIP and SHA256SUMS. Release identity verified from GitHub API.
- Public release includes PR #127 ten actually prepared tabs and safer Following verification, PR #128 explicit owner-approved automatic batch Reviewed state and read-only reruns of unapproved cohorts, with only exception profiles opened as needed. Never replay uncertain relationship-changing clicks or erase old journals.
- Release-request authorization consumed (`authorized=false,status=published`); distribution manifest reconciled to current stable v120.52 and next reserved v120.53. No next release is authorized.
- **Still pending owner testing against live Instagram on official installed v120.52.** Offline Chromium does not prove real-world successful Unfollow/Cancel Request. Keep open owner-reported account/session differences as potential follow-up; stop on challenges. No Authenticode certificate was used for Windows Setup.

## 2026-10-19 — v120.52 release preparation and owner testing contract

- **Permanent owner-acceptance rule:** Michel tests the actual official published stable release, never temporary GitHub Actions previews, candidate ZIPs or unmerged artifacts. Complete automated safety, installed Windows, real offline Chromium, Android/desktop UI, signing and asset-integrity checks before publication, then provide the official stable release. Do not use owner manual preview validation as a release gate or claim real Instagram acceptance before post-release feedback.
- Owner explicitly requested completing current InstaCleaner changes and publishing v120.52. PR #127 (ten prepared Chrome tabs, safe Following detection, read-only refresh) and #128 (persistent whole-batch Reviewed approval, automatic read-only recheck when unapproved, exceptions-only tabs) are already merged on main.
- Retain no-repeat safeguards for potentially clicked actions, exact Instagram workspace scope, protected accounts, original local journal and imported data. Stable v120.51 remains published until v120.52 is verified as a normal stable release with all nine assets.
- Official release requires separately authorized release-request commit, exact-source CI, Windows Setup install/upgrade, signed original-production Android, Desktop/Android visuals and checksums; the owner tests *after* that release.

## 2026-10-18 — Candidate: automatic batch needs human "Reviewed" approval

- User interrupted ten-tab work to clarify: do NOT re-open all ten profiles for manual inspection. Robot does routine checking automatically. On batch completion display **"Is this batch OK?"**; only the user's one-click batch approval marks verified profiles Reviewed. An unapproved batch stays pending and can be rerun in automatic **read-only check** mode for the same cohort; no repeated relationship-changing clicks for prior attempts. Optional "Open only issue profiles" is for exceptions.
- Branch `feat/automation-batch-approval-20261018`: owner/account/task-specific durable `-batch-reviews.json` sidecar storing exact target cohort, creation and explicit approved_at; Windows bridge `review-batch`, `approve-batch`, `recheck-batch` with owner/task/batch id validation; separate UI status and legacy reviewedMeta updates only after confirmation. Uncertain records remain unresolved even if the batch was approved.
- New automatic recheck visits all eligible saved targets with existing Instagram pacing and **no Unfollow/Cancel Request clicks**, persisting read-only outcomes without overwriting original action journals. Explicitly does not send Instagram credentials or browser state anywhere. Historical action records stay, but no legacy batch membership is inferred.
- Test against stale sessions, cross-account isolation, restart, non-approved start blocking, safe recheck, only-issues browser opening, and Windows/Android/Desktop regression workflows. Do not release without explicit owner instruction. v120.51 remains stable.

## 2026-10-18 — Live v120.51 failure, ten-tab staged preloading and Following detector candidate

- User screenshot after installing/testing v120.51: an ambiguous post-click result (@jdrd.avid), a no-click Following timeout (@isaac_nahuat: main=yes, exact username=yes, matching controls=0), and only three loaded profiles despite requesting ten. This is **not** accepted as working real Instagram Unfollow.
- Development branch `fix/ig-robot-ten-prefill-following-20261018`. Prepare up to 10 *actual* profile tabs in the explicitly approved batch before any clicks; pace navigation per visit and store each visit durably; stop for sign-in/challenge and keep tabs available. Follow actions remain one at a time and only verified outcomes close automatically.
- Add strict unique visual pointer-backed relationship control fallback and a single *read-only* target refresh for delayed Follow/Follow Back after the Unfollow click. No blind clicks/duplicate action, no reattempt of owner ambiguous @jdrd.avid.
- Pending: exact-head Windows real Chromium fixtures, integrated Windows Setup, Profile Counts, Desktop/Android visual CI. Even passing fixture CI does not prove actual logged-in Instagram live DOM; user must physically retest. Stable remains v120.51 until separate owner release authorization.

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
