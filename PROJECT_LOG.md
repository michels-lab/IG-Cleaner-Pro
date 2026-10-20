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

## 2026-10-19 — GRANADA #1: Focus preview underfill, separate PR (#137)

- **Operación GRANADA:** se aparcan #133 (release y prueba Instagram real del robot ya integrado) y #135 (Android Developer autenticación/proveedor/dispositivo), y el issue #57 estaba ya implementado y publicado en v120.40 aunque la aceptación física seguía pendiente. No editar esos componentes ni reinterpretar CI como aceptación del usuario.
- Se eligió #136 en rama `granada/focus-priority-full-batches-20261019`, PR [#137](https://github.com/michels-lab/IG-Cleaner-Pro/pull/137). Falla fuente: el pool principal de Focus devolvía **solo la primera categoría no vacía**: uno o dos `changed` suprimían los demás elegibles en tandas 20/30/40. El editor v125 mantenía la misma selección parcial en otro algoritmo duplicado.
- Corrección candidata: priorizar `changed -> critical -> risk -> demás` dentro del **pool elegible** con deduplicación estable, orden por evidencia/prioridad, y una única fuente utilizada tanto por preview congelada como por el editor. Persistencia de usernames congelados, reimport stale y confirmación explícita conservados. No se toca robot ni Android.
- Prueba nueva `tests/focus-batch-priority.test.cjs` conectada a `.github/workflows/ci.yml`, cubre 1 cambiado + restantes, exactitud de conteo, candidatos filtrados, Pending independiente y reimport que obliga a confirmar.
- **Evidencia:** commit candidato `cf46361ca1e40875cd6d0251f868290b96ba294e`; Desktop contracts, Desktop visual, Profile Counts offline y RLS PASS. En el mismo candidato Developer Android falló por el SDK `unknown archive` al descargar una imagen del emulador, **antes de instalar la app**, sin conexión causal establecida con Focus. Un reintento de **solo ese job** quedó solicitado; no se modificó Android. Un merge/publicación sigue sujeto a CI pertinente y normas de release. Stable pública v120.53 permanece intacta.

## 2026-10-19 — BR-01–BR-07 implementation merged: PR #134, release not authorized

- **Merged product source**: PR [#134](https://github.com/michels-lab/IG-Cleaner-Pro/pull/134) into `main` at `8df8f3b27747b0ba1ccfd896664676223219f4ac`. This replaces the previous document-only candidate status for BR-01..BR-06; the original owner bug #133 is still open for actual release acceptance.
- **Robot**: persistent batch-size UI selection, same persistent robot Chrome session for manual Issue Review, safe no-click retry/advance, distinct terminal `already_not_following`, historical read-only re-audit and journal history retention, clearer counters. New backend guard refuses approval while targets remain *untouched* (but permits explicitly recorded uncertain targets to remain unresolved, never Reviewed).
- **Developer twin**: Windows launcher (`--developer`) with separately isolated workspace/session, same public login workflow, anchored persisted annotations and sanitized JSON/AI prompt audit export; Android separate `.developer` package, installed real WebView/UI tests, annotations and native Downloads export. Production cloud writes are blocked at relevant Developer native/browser boundaries. Source code does **not** prove real OTP provider login or installed physical-device acceptance.
- **Exact PR head CI** `8f725d109170862afc2aefaa8ac42039a6a465ee` all eight checks **SUCCESS**: Desktop local-app, Supabase RLS, Android build, Android About installed emulator, Android Developer installed emulator, Windows integrated Setup install/runtime, Desktop visual, Profile Counts offline contract. During QA corrected two obsolete Android contract assertions and added a backend regression refusing premature batch approval. New `main` merge SHA is separately verified; record post-merge CI separately when available.
- **Still NOT released**: current public stable remains **v120.53**. v120.54 neither authorized nor published. Michel uses official stable releases for testing, not branch builds or Actions artifacts. Live Instagram following/unfollowing, original user session reliability, real OTP/account switching on physical Windows/Android, Samsung acceptance and signed public Developer APK distribution remain external/product release acceptance work. No bypass of Instagram challenges or uncertain clicks.
- **Documents**: detailed [BR-01–BR-07](docs/PENDING_BLOCK_ROBOT_RECOVERY_DEVELOPER_TWIN_2026-10-19.md) remains historical acceptance spec. Issues #133 and #135 remain open until real installed-release and provider acceptance.

## 2026-10-19 — Gran bloque de recuperación y Developer twin (especificación registrada)

- Nuevo contrato de ingeniería: `docs/PENDING_BLOCK_ROBOT_RECOVERY_DEVELOPER_TWIN_2026-10-19.md` (BR-01–BR-07). Cubre batch size, prefetched huérfanos, sesión única, reauditoría segura de tandas históricas, contadores, gemelo Developer con anotaciones ubicadas y exportación IA, y QA de instaladores.
- **Evidencia:** documento comprometido en `c9ca61063fb73be40e7986ef8cf9cc03e084a551`. Es trabajo documental y diseño de pruebas: **todavía no se reparó el ejecutable, no se corrieron pruebas y no hay nuevo release**.
- Próximo paso de implementación: máquina de estados y contratos de persistencia, después Chrome-context compartido; conservar v120.53 como estable hasta autorización explícita de publicar versión nueva.


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

## 2026-10-18 — Owner requested explicit automatic-batch Reviewed confirmation

- Owner clarified: automatic Unfollow/Cancel/Followback audits must **not** count as manually `Reviewed` merely because Chrome visited a profile or the action returned `ok`. Unlike manual Focus, the automatic robot should do all ordinary work itself and then ask **"Is this batch OK?"** once for the whole batch. Only unusual/uncertain profiles can be opened together for targeted inspection. If not approved, the same batch remains pending and may be rechecked automatically, not one-by-one by the owner.
- Candidate `feat/automation-batch-approval-20261018`: additive owner/account/task-scoped on-disk batch review ledger (separate from immutable action attempts), pending across app restarts, exact-batch ID and explicit approval, rejection of fresh action batches while earlier batch is awaiting approval. The approval confirms only rows backed by successful `ok` evidence; ambiguous/not-loaded profiles remain in Issue Review, never silently marked reviewed.
- Safe `recheck-batch`: same saved cohort loaded in visible Chrome and checked read-only. Does not issue any Unfollow/Cancel Request clicks (even if a previous result was ambiguous) or rewrite the authoritative action journal. The owner can initiate another automatic checking pass; the app can open **only exception accounts**, max 10, if human attention is required. Action-session security and pacing remain.
- UI marks reviewed data for verified results only *after* the backend persists owner approval. Windows bridge endpoints require the existing local session token. Pending approval and confirmed click histories must not be conflated. Existing journals are preserved; historical batches with no saved batch identifier are not retroactively assigned to an invented cohort.
- No version bump/release authorized; stable remains v120.51 pending exact-head CI and real Instagram acceptance.

## 2026-10-18 — Owner live v120.51 failure: three tabs, control missed, ambiguous post-click result

- Screenshot of v120.51 Issue Review: @jdrd.avid has `Final state is ambiguous`, **possibly clicked** and therefore must not be automatically repeated. @isaac_nahuat has `profile_load_timeout` with `main=yes, exact username=yes, named interactive controls=0, eligible controls=0`, **no click**. A third issue row is visible. This is actual owner live evidence, not a mock success.
- Root cause of "10 tabs": v120.51 only kept up to ten *slots* but typically prepared **one** next page. On a review/timeout stop, only 2-3 pages were visited. Corrective branch `fix/ig-robot-ten-prefill-following-20261018` now allocates up to ten real target tabs and navigates each with durable visit journaling and owner-configured pacing **before** attempting relationship changes. Explicit approved batch size, exclusions, existing protected/attempted journal and security checks still apply. Fewer than ten eligible selected targets or security stops can still mean fewer than ten loaded pages.
- Enhanced read-only exact-target Following detection for uniquely located visual `cursor:pointer` controls with exact visible text and target username, excluding Following count links, suggested/sidebar controls and ambiguous duplicates. Never guess a click target without exact evidence.
- On a potentially clicked Unfollow still showing ambiguous relationship state, perform **one read-only target refresh** then verify Follow/Follow Back; never re-click, never infer success without verified final state. Keep uncertain tabs and journals.
- Added offline real-Chromium regression fixtures for cursor-pointer control, counter-link exclusion, ambiguous duplicates and delayed post-click UI refresh. Real owner acceptance still pending.
- This is development work. Official stable remains v120.51. **Do not publish v120.52 without a new explicit owner release instruction** and exact-commit QA.

## 2026-10-18 — Official v120.51 stable release published (real Instagram acceptance still pending)

- User explicitly requested `TERMINA TODO Y DALE RELEASE` in the InstaCleaner continuation. PR [#126](https://github.com/michels-lab/IG-Cleaner-Pro/pull/126) merged after all five exact-head QA families passed. The `main` merge commit `1b566b76dd16e34375bbb265531ee7c4f3fe49f3` also passed Desktop, Android, general CI and the installed Windows/Chromium integration tests.
- Authorizing request SHA `f4218e33cc5562c49227b45da23dca9715582a87`; guarded official workflow [39114910174](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39114910174) **SUCCESS**: automated installed Windows Setup launch/upgrade/uninstall evidence, offline real Chromium action tests, same-SHA Desktop/Android rendered evidence, stable original-production-signer Android APK, checksums and public asset verification.
- Normal GitHub stable [v120.51](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.51) published **2026-10-18T09:25:11Z**, `prerelease=false`; nine assets checked including `IG-Cleaner-Pro-Windows-Setup-v120.51.exe`, `IG-Cleaner-Pro-Android-v120.51.apk`, Desktop standalone HTML/ZIP and `SHA256SUMS.txt`.
- Scope: ten-tab visible Chrome workflow, bounded and live-reported wait for Following/Requested controls, owner-verified sequential Unfollow/Cancel actions with no uncertain replays, and one read-only next-profile warmup *only when visit pacing permits*. A stale same-URL profile is reloaded unless specifically confirmed as preloaded; outcome journal is persisted before closing confirmed tabs.
- Post-release safeguard: release authorization reset to `authorized=false,status=published`; distribution manifest reconciled to stable v120.51 and next reserved v120.52, no automatic follow-up publication.
- **Not physically accepted on owner's machine/Instagram:** no real unfollow, pending cancellation or challenge outcome confirmed by CI. User must install official v120.51 Windows Setup, keep local data intact, run a small explicitly approved test batch and inspect final Follow/Follow Back plus Issue Review. Do not say owner has installed the release. Android Play Store publication and third-party email template configuration remain separate provider tasks.

## 2026-10-18 — Prepare v120.51: paced read-only prefetch with ten-tab workflow

- User explicitly ordered finishing InstaCleaner and publishing the next release. Version source follows distribution manifest `nextRelease=v120.51`; Android versionCode 12051/versionName 120.51 and Desktop UI v120.51 are synchronized, retaining original package and production signing certificate.
- Action robot can **preload one next eligible target in a second Chrome tab while the current target is waiting for its relationship control/menu**, provided the owner-configured visit window/delay and mandatory batch rest permit the read-only navigation. Existing ten-tab cap is preserved. Changing an Instagram relationship still occurs **strictly one at a time**, with separate ownership proof, protected list and post-click Follow verification; no silent skips or replay of uncertain clicks.
- A speculative visit is written to the persistent pacing ledger *before* navigation; finalization can target the correct visit timestamp when another tab was opened concurrently. Preloaded profile is reused, never fetched twice before its turn; any preload/navigation failure is left for normal visible readiness review, not treated as a successful action.
- Added Chromium and Python tests for a preloaded exact profile, ten-tab no-eviction, and indexed visit completions. This is read-only overlapping **where cooldown allows**, not ten simultaneous Instagram page requests. The current visit intervals remain in effect.
- Acceptance still pending: real signed-in owner Chrome test that Following is found and a real Unfollow/Cancel Request has changed to Follow/Follow Back. Automated fixture QA can validate safety but not live Instagram.
- Release publication must use the governed v120.51 workflow and pass exact-head Desktop/Android visuals, installed Windows Setup, original Android signing certificate, hash/assets and release verification. Do not claim installation on owner's PC.

## 2026-10-18 — Development: 10 Chrome tabs and visible Instagram readiness confirmation

- Owner superseded previous 5-tab preference: use **10 Chrome tabs** for Instagram action review, preserving one sequential relationship-changing click at a time and keeping unresolved tabs available for inspection. Updates MAX_ACTION_TABS, UI visible 0/10, and ten-tab safety tests.
- Owner observed that a missing Following button can be a loading race, not proof of absence. The action worker now reports loading_profile or waiting_relationship_control with profile handle plus elapsed/max seconds to the live Automations UI, and waits up to 20 s for visible target layout and the Following/Requested control. Following menu also waits read-only up to 20 s; no repeated clicks.
- After a pre-click rendering/control timeout, mark a distinct profile_load_timeout issue, **stop instead of skipping silently**, keep the tab open and journal that no click occurred. Known no-click timeouts may be reconsidered only in a newly approved batch; potentially clicked outcomes are never auto-retried. No change to user data or export privacy.
- Chromium regressions cover a delayed profile header, a never-loading profile, a never-rendered Following button, wait-stage updates and ten-tab slot protections. Exact-head CI and physical owner Chrome acceptance required. Stable release remains v120.50; no release authorization was granted.

## 2026-10-18 — Development: safe Instagram action readiness and five-tab workflow

- User screenshot of the installed v120.50 robot reports both a post-click owner-session verification failure and a missing Following control (no action clicked). Cause may involve delayed DOM hydration, but a timing problem has not been proven from the screenshot.
- Development branch `fix/instagram-action-readiness-20261018` implements bounded read-only waits for the target relationship control and open menu, and retries *verification reads* after post-click transient owner-state failure. No second relationship-changing click is issued.
- Per user's revised preference, Windows action robot supports up to **five distinct visible target tabs** within the same session, sequential owner-approved relationship actions, per-tab outcome tracking, and closes only confirmed `ok` actions or explicit pre-click skips. Unknown/possibly-clicked records retain a visible tab for manual inspection rather than being reused or auto-retried. When all five tabs are unresolved, stop and prompt review.
- Journal writes happen before closing verified tabs, preserving crash/no-replay semantics. Automations displays open review tabs and warns that Pause closes Chrome. No CAPTCHA bypass, no private Instagram API, no raw export upload, no release/version bump.
- Status: candidate only, exact-head GitHub validation and real Windows/Instagram physical acceptance still required; stable stays v120.50.

## 2026-10-18 — Verified stable v120.50 published (real Instagram acceptance pending)

- Normal public GitHub [v120.50](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.50) published 2026-10-18T07:08:16Z, built from exact SHA `e0a95a8c192642c175a1b080212c7ddd5a4f0655`; governed run [39106161831](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39106161831) **success**. Nine assets confirmed, including Windows Setup, Android production APK, Desktop HTML/ZIP and SHA256SUMS.txt.
- Independent exact-commit release checks passed: token-guarded owner approval, installed Windows Setup validation, real offline Chromium action selector safety, Desktop/Android screenshots, original Android production signing certificate, all asset names and hashes. The real user's Instagram account was **not** touched by CI.
- Scope: bounded non-semantic visible handle + unique Following/Siguiendo control detection in profile main, layout category diagnostics when no click is possible, safe new-batch retry of known zero-click issues, improved wrapping of Issue Review details.
- Post-release administrative safeguard: release request returned to `authorized=false,status=published`; distribution manifest now records stable v120.50, next v120.51; README and handoff updated. No automatic future release authorization.
- Still open: real owner Windows/Chrome test that the correct Following menu opens and account reliably changes to Follow/Follow Back; if it fails the new diagnostic counts must be captured for deeper DOM-specific remediation. No blind clicks, no challenge bypass and no journal reset.

## 2026-10-18 — Prepare v120.50: second physical Following failure and read-only DOM diagnostics

- Screenshots after v120.49 still showed visible Instagram Following controls yet `missing_profile_info` and no clicks. PR #122 implemented a bounded real-Chrome read-only layout probe requiring exact visible target username (including span/div) and one nearby interactive control (button, role=button, tabindex=0), with blockers for suggestions/links/duplicates.
- Issue Review now displays safe control-count diagnostics for future investigation and wraps long messages within the viewport. Known no-click journal entries remain retryable in a new explicitly approved batch; no riskier prior click is replayed.
- PR #122 merged as `62ba64a47954` after **five exact-head passing workflows**, including real offline Chromium locator simulations, Windows Setup installation, Desktop/Android UI and profile-count tests.
- This branch prepares v120.50 (Android versionCode 12050, versionName 120.50, displayed Desktop UI v120.50), retaining the original signing certificate and package identity. No new release may publish until separate owner-authorized governed exact-commit QA passes. Real owner's Instagram unfollow success remains an open acceptance criterion.

## 2026-10-18 — v120.50 dev: actual Following visible, v120.49 still misses Instagram control

- New real owner screenshots from installed v120.49: multiple `missing_profile_info` / "Instagram control not found; no action clicked" after visiting actual profiles which visibly display the Following dropdown. This invalidates the assumption that v120.49's heading-based fallback resolved the real-world UI. No account-changing clicks are confirmed.
- Source root cause: `_profile_relationship_control()` only searches a semantic `<header>` or a `<main>` with a visible exact `h1/h2/h3` username. Instagram can show the exact handle in `span/div`; its relationship action may be a `tabindex=0` clickable div instead of a semantic role/button, or show icons alongside its caption. Those variants are not covered by the v120.49 fixture.
- Added a bounded, **read-only** profile-hero survey on the target page: require exact URL, visible target username in the top profile area (including span/div), one nearby visible clickable `button`/`role=button`/`tabindex=0` matching Following/Siguiendo, and no competing same-name candidates. Never click mere text, a following counter/link, suggestions, hidden/other profile controls or ambiguous duplicates. Owner-identity verification, protected set and actual post-click Follow verification remain in force.
- When no unique safe control exists, Issue Review now includes **non-sensitive category counters** (`main` present, exact username found, named interactive control count). No usernames from nearby suggestions, profile content, cookies, DOM dumps, tokens or screenshots are retained by this diagnostic. The message still states nothing was clicked.
- The explicit `missing_profile_info` journal results with appended safe layout diagnostics remain retryable in a **new owner-approved batch**. Ambiguous post-click outcomes are never automatically repeated; no journal reset.
- Regression tests use real local Chromium for span username / role button / tabindex div / Spanish following / unrelated aside / false links / ambiguous duplicates / non-click diagnosis, and Python journal history compatibility.
- **Development only:** v120.49 remains the published version until required CI and a separately authorized v120.50 stable release. CI mocks cannot confirm Instagram's live DOM and owner acceptance is still required.

## 2026-10-17 — v120.49 published: Unfollow Following detector (no-click retry hotfix)

- GitHub stable [v120.49](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.49) published at 2026-10-18T01:25:15Z (October 17, Saltillo local time), source SHA `a6d4583df3cc75ae814b0619c291eac29ed18bff` and owner-authorized governed workflow [39086045263](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39086045263) **success**. Nine expected assets confirmed: Windows Setup, ZIP, Android production-signed APK, standalone HTML and ZIP, SHA256SUMS and metadata/logo.
- Release gates passed: Android source/signed certificate, rendered actual Android/Desktop screenshots, Windows installed Setup and isolated Chrome DOM safety tests, package checksums and published asset verification. Live Instagram unfollow on the owner's profile **not yet physically accepted**. Do not claim the user's screenshot target was unfollowed.
- Post-publication safeguard: release authorization deactivated (`authorized=false`, `status=published`), stable manifest advanced to `v120.49` and next `v120.50` reserved; no automatic publishing of v120.50 is authorized.
- Owner should install Windows Setup v120.49 using Updates or the official Setup (no prior uninstall or journal reset), then start a **small newly approved Not Following Back batch**. Exact legacy `missing_profile_info` pre-click records are eligible again. Inspect final profile state and Issue Review. Still ambiguous post-click entries remain excluded from automatic repetition.
- Remaining follow-up: actual owner's Chrome/Instagram acceptance, confirm follow menu selector and post-click Follow/Follow Back, observe challenge stop and owner-identity checks, verify update preservation and cross-device data where relevant.

## 2026-10-17 — v120.49 candidate for reported Unfollow bug

- Owner supplied a real v120.48 screenshot where three Not Following Back records incorrectly show `Insufficient profile evidence; nothing clicked`, followed by a browser screenshot of the target profile with **Following** visible. This is an active post-release defect, not a successful unfollow.
- Root-cause and fix developed in PR #120: conservative profile-scoped Following/Siguiendo detection including role=button and dropdown caret, no-click-only legacy journal retry, fresh backend history precedence, and explanatory Issue Review. Preserves no-repeat protections for potentially clicked actions.
- PR #120 exact-head CI: Profile Counts, Desktop rendered UI, Android emulator, general CI and integrated Windows app preview/Setup passed before merge into main `5c12723d`; offline Chromium tests do not prove live Instagram.
- This separate preparation branch advances production Android Gradle metadata, signed version manifest and Desktop visible version from v120.48 to v120.49 without altering the certificate. **Stable remains v120.48 until independent governed publication verifies exact commit QA, Windows installed Setup, signed Android APK and SHA-256.**
- User's earlier continuation instruction included publishing the next working installer; actual owner device and Instagram relationship-changing acceptance remains pending and must be reported separately, never invented.

## 2026-10-17 — v120.49 development: live-owner Unfollow misses visible Instagram Following controls

- User's **actual Windows v120.48 Issue Review screenshot** shows three "Not Following Back" profiles with `missing_profile_info`, message "The profile does not show the state required for this action." and zero relationship-changing clicks. User separately showed the Instagram profile itself visibly has **Following**. This establishes a detection failure, not proof the person was unfollowed or that the Instagram session failed.
- Root-cause source audit: `perform_visible_action()` searched only a semantic `<header>` for an exact accessible `button`; Instagram layouts can put its Following/Siguiendo action as `div[role=button]` in a top-level profile main area or add a decorative caret to its accessible name. New locator first checks the verified target header, then only checks `main` when the exact target username appears as a visible heading. No bare Following text, Following counts/links, foreign profile URLs, or ambiguous duplicate controls are acted on.
- The known `missing_profile_info` result was stored permanently as attempted despite being a proven **pre-click** result. Added `_preclick_no_action()` allowing exact known pre-click journal records from v120.48 (and the new explicit message) to be retried **only in a new owner-approved batch**. Unknown review/error and ambiguous post-click outcomes remain excluded and cannot be replayed; owner/account/task journal separation and no duplicate clicks preserved.
- Desktop `igcAutoStart()` now plans from a mandatory fresh scoped Windows disk-journal history rather than unioning stale browser `actionState` / localStorage entries; Issue Review explains that only no-click outcomes are retryable after an update.
- Offline regression coverage: new role=button Following/Siguiendo caret in main without semantic header, successful confirmed post-click Follow state, count/link and incorrect heading no-click, duplicate controls refuse click, v120.48 legacy journal recovery vs uncertain-action quarantine and stale localStorage exclusion. **These simulate Instagram DOM; owner live Chrome acceptance still required.**
- **Status:** development branch, no new stable release published. Stable GitHub v120.48 remains unchanged; v120.49 candidate will require owner authorization, complete exact-head QA and independent release checks.

## 2026-10-17 — v120.48 officially released and authorization deactivated

- Owner-authorized normal stable [v120.48](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.48) published at 2026-10-18 00:27:53 UTC, 2026-10-17 in Saltillo. GitHub governed run [39082472684](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39082472684) **SUCCESS**; exact publication source SHA `19680119c0e0a1c5d5bdfb954793c355849f0bdb`.
- Full official assets verified: Windows native Setup.exe + checksum, optional integrated Windows robot ZIP, standalone Desktop HTML and ZIP, original logo/privacy files, SHA256SUMS.txt and production-signed Android APK with the original app signing identity.
- Independent release gates passed: authenticated authorization, eight real Desktop screenshot surfaces, installed Android Home/About screenshots, Windows Setup wizard/build/install/start/upgrade/uninstall and release asset/integrity tests. The user's **real Instagram sign-in and action outcomes, actual local Windows update and Samsung cross-account state** remain unverified.
- Release request marked `authorized=false,status=published` with immutable publication run, SHA and timestamp. Distribution manifest now records stable `v120.48` and reserves `v120.49`; no later release authorized.
- Functional changes: sequential Pending/ZIP reimport and cold-start action-journal safety, one read-only pending-cancel verification without duplicate click, recoverable manual Focus previews and targeted English UI strings. Remaining dynamic Spanish text and real-session acceptance are tracked separately.

## 2026-10-17 — Preparing governed v120.48 stable release, explicit owner instruction

- Owner instructed: continue InstaCleaner pending development tasks and **publish a release when the work is finished**. Scope of this candidate: PR #113 (read-only Cancel Pending recheck), sequential Pending/Focus import recovery commit `5c7aed9`, PR #117 cold-start action-journal safety and PR #118 static English UI labels. Do not claim all outstanding physical/browser acceptance issues are complete.
- PR #118 was merged to main as `5e7cedcd` after its five exact-head CI families completed successfully. PR #117 is already merged as `c9ac3ff7`.
- Pre-release branch increments Android Gradle release versionCode/name and `release/android-signing.json` from 12047 to 12048 without changing the certificate fingerprint or keystore location. Desktop-visible UI and <title> now show v120.48, and release notes document fixes and known real-device limitations.
- Governed Windows publishing workflow now explicitly runs the cold-start history guard in addition to Pending second/third batch, reimport and no-repeated-click checks.
- Next: merge only after required CI tests; create a separate **authorized v120.48 stable request** on main and let `.github/workflows/release.yml` independently validate exact-commit screenshots, Windows Setup build/install/start/upgrade/uninstall, production Android signature and published SHA256 checksums. After verified GitHub Release, deactivate authorization and advance manifest stable/next versions. No Instagram CAPTCHA bypass or credentials handled.

## 2026-10-15 — English UI follow-up: Pending, Mutuals and non-mutual Followers static labels (v120.48 development)

- Found owner-visible mixed-language labels in Pending Lab, Mutuals and Followers: paused/expired pause filters, age/risk options, action headers, import prompts, detected approvals, counts, navigation and refresh buttons.
- Replaced 42 static visible labels with English text while preserving their exact `value` codes, JS state names, DOM hooks, imported Instagram data and the accepted layout/assets. No Follow, Unfollow or Cancel behavior changed.
- Extended the existing English UI source contract with assertions for the new labels and a scoped regression list of obsolete static Spanish labels. Broader dynamically generated JS and real native Android UI still require separate acceptance under #86.
- **Status:** development only; exact-head CI/Chromium/Android/Windows gates required before merge. Published v120.47 binaries remain unchanged; no release authorization was requested.

## 2026-10-15 — v120.48 development: cold-start Pending history integrity before next action batch

- Follow-up source audit found a remaining starvation/safety case after the sequential-batch fix: Desktop `igcAutoStart()` called `igcAutoPoll()` first, but that poll can silently skip while busy or catch and swallow a Windows connection error. Also, after a fresh Windows process launch, `ActionRobot.snapshot()` has no current task until an action is started, so it cannot expose persisted attempts for an idle task. Selecting the first N based on this stale/empty state can repeat earlier targets or get rejected only once the backend starts.
- Added `ActionRobot.attempted_history(owner,account,task)`: read-only retrieval of the durable journal for the exact selected account/task even before a worker starts. Unknown or potentially clicked states remain blocked from automatic replay; provable pre-click identity failures remain eligible. No Instagram access or relationship-changing actions occur during the history check.
- Added token-protected local `/api/actions/history` and changed `igcAutoStart()` to **require** a successful scoped history read before selecting or confirming the next action batch. Connection failure, malformed history, wrong owner or task changes stop without sending an action start request; no stale in-memory fallback.
- Regression coverage: cold restart with 60 prior attempts and no local client cache, backend owner/task isolation, no-click retry, malformed/scope-mismatched history and history read failure. CI now includes `tests/automations-cold-start.test.cjs` alongside existing later-batch and offline Python tests.
- Documentation: README and Profile Counts guidance now correctly identify published stable v120.47, native Windows Setup, and unpublished v120.48 changes. No version tags or release authorization changed.
- **Status:** development branch, exact-head CI and owner real Chrome acceptance must be verified separately before merging or publishing. Do not claim live Instagram success from fixtures.

## 2026-10-15 — v120.48 development: Pending Requests second/third batch recovery and unverified cancellation checks

- Owner observed that Pending Requests in Automations stopped opening profiles after the second batch, particularly after importing newer Instagram exports, and Instagram cancellations were recorded as unconfirmed although the profile action appeared to occur.
- Root causes in source: Automations selected the *first* N imported usernames every time, excluding only temporary skips/protections but **not any prior ActionRobot journal**; the backend previously skipped already-processed targets, so later batches could be repeatedly empty. The Automations rows UI rendered only the first 300 profiles without pagination. Separately, frozen Focus previews became stale on new imports and refused to open until manually regenerated. Chrome may also block repeated bulk popup openings without detectable confirmation.
- Backend: ActionRobot snapshot exposes per-owner/account/task *all persisted attempted usernames* (not just most recent batch), preserves replay exceptions for provable no-click identity failures, and rejects entirely previously attempted batches with a clear message. Suspect/ambiguous post-click actions are never automatically retried.
- Frontend: Automations now excludes all previously attempted usernames from subsequent action batches, persists scoped historical exclusions, refreshes the local robot journal before selecting the next batch, adds pagination over the entire imported action queue (100 rows/page, no overall import size cap), provides explicit **Open next Pending review batch** (read-only Focus) and clarifies **Clear skips** does not clear historical records.
- Pending Focus: when a previously frozen preview is stale because an export changed, regenerate an *explicit reviewable preview* from current data instead of trapping the user; user must click **Open these profiles** separately before new usernames open. Added **Recover current batch** in Pending Lab. Focus review modal displays a direct **Open** link for every member in case Chrome blocks automatic tabs, and no longer claims all tabs actually opened or marks rows reviewed based on popup requests.
- Pending cancellation: after an uncertain click, a one-time **read-only profile reload** may verify a visible Follow button. A continued Requested/Following state, account verification interruption or navigation mismatch is explicitly recorded for manual review, never replayed. New anomaly code `pending_cancel_unverified` has clear owner-facing explanation.
- Tests: Chromium mocked DOM checks for delayed confirmation and no duplicate clicks; offline Node VM third-batch, fresh-import and Focus stale preview tests; Python journal tests; the governed Windows Setup release pipeline and normal CI now explicitly gate all new regressions.
- This is unreleased **v120.48 development**. Published stable **v120.47** remains intact; physical owner's Instagram session and browser popup permissions not exercised. Do not publish without separate owner instruction.

## 2026-10-15 — Pending Requests cancellation: delayed Instagram UI verification (v120.48 development)

- User reported Cancel Pending Requests executed the request withdrawal but Insta Cleaner could not confirm it. The existing implementation checked the target header only in the same possibly stale browser page. A `review` result was journaled and already prevented unsafe automatic replay; however it did not use a fresh read-only profile view to resolve delayed UI state.
- Fixed `tools/profile_actions.py`: after a previously clicked Cancel Request yields inconclusive header state, navigate once to the **same exact target profile** using the current verified Chrome session, recheck owner and visible Follow/Follow Back state, and only then record `ok` when explicitly proven. A redirect, Requested/Following button, challenge, wrong owner, missing button or network failure never counts as success and never issues a second relationship-changing click. Stop the batch for owner review if uncertain; preserve journal and retry restrictions.
- Added distinct issue code `pending_cancel_unverified` and an English-only **Cancellation not confirmed** filter in Automations review table, with clear instruction to open the profile and avoid re-running cancellation automatically.
- Added offline real Chromium regression tests: stale Requested changing to Follow after read-only refresh, still Requested, Following not being falsely treated as cancel, redirect to login, and no duplicate action click. No live Instagram session acceptance claimed.
- **Post-v120.47 release CI fix:** Windows PR preview source still carries the current published Android/EXE version `120.47` while the manifest reserves `nextRelease=v120.48`. The preview now opts in to `-AllowCurrentStablePreview` so an unreleased PR can install/test its actual current-version QA binary. The official governed release workflow has **no such switch** and continues to require a strictly authorized `nextRelease`. A source contract enforces that distinction; no version/tag was changed.
- No existing v120.47 release files, Android package, account data or unrelated robots modified. This is source-only v120.48 development, requiring its own explicit future release authorization.

## 2026-10-15 — Stable v120.47 published and release authority deactivated

- **Published:** [Instagram Cleaner Pro v120.47](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.47) at 2026-10-15 22:01:27 UTC, governed Actions run `38813431832`, exact published source commit `9d252f70c40145602bb7ad44ef74ffbf26bc5181`. GitHub confirmed stable release (`draft=false`, `prerelease=false`) with 9 assets including SHA256SUMS.txt.
- **Normal Windows artifact:** `IG-Cleaner-Pro-Windows-Setup-v120.47.exe` (50,664,616 bytes), installer with integrated Desktop/robots, verified native updater, optional shortcuts and complete license; optional legacy portable integrated ZIP retained.
- **Other assets:** standalone `IG-Cleaner-Pro-Desktop-v120.47.html`, companion Desktop ZIP, production-signed `IG-Cleaner-Pro-Android-v120.47.apk`, Setup-specific and general SHA-256 checksums, official logo and privacy notice.
- **Release gates:** exact commit real Android Home/About emulator evidence and Desktop Home/About/Automations screenshots passed, and same-commit Windows Setup build/install/start/upgrade/uninstall passed. Signed Android release keystore continuity and uploaded assets/checksums verified by publishing job. Earlier attempt `38812640714` correctly blocked on stale visual verifier expecting six screenshots; corrected verifier to require all **eight** genuine screenshot surfaces and reran official release with full gates. No safety gate was bypassed.
- **Post-publish safety:** `.michelslab/release-request.json` reset to `authorized=false,status=published` with immutable run/commit evidence; manifest stable advanced to `v120.47`, next candidate reserved `v120.48`. The current developer source Android version remains v120.47 until next-feature work intentionally bumps it. Future releases still need a new explicit owner authorization.
- **Pending acceptance:** owner physical Windows app, updater walkthrough, actual Instagram signed-in behavior, and Android installation/device data checks remain unverified. Authenticode signing is not configured; do not claim Windows certified publisher identity or real live Instagram success.

## 2026-10-15 — Native Windows updater and verified manual Setup candidate (v120.47 development; no release)

- Implemented a Windows-only update manager for installed Insta Cleaner Pro with anonymous stable GitHub Releases metadata and SHA256SUMS verification. Checks availability automatically in the native app and on explicit **Updates → Check for updates**. Download and Setup launch are separately user-approved; no token embedded, no manual cookie transfer, no Instagram automation touched.
- UI: added an Updates action beside the persistent **About** button in fixed Desktop header, shown **only** with the native authenticated local bridge; standalone `file://` HTML and Android never show the Windows feature. Real dialogs show current/latest, availability, progress, release notes as safe text, cancellation and Run Setup confirmation. No auto-install success claim or visual redesign.
- Backend: `tools/windows_updater.py` validates stable version/official URLs, enforces asset size and exact SHA-256, streams with cancellation to a temporary file, atomically commits verified Setup, rehashes before launch and backs up existing app HTML + robot result journals as a local ZIP. Browser profiles and cookies are retained in place, never copied into the restore point; installer continues to preserve data. Publisher Authenticode remains unconfigured, and this channel is explicitly SHA-256 verification, not code signing.
- Runtime: Windows PyInstaller executable bundles its actual `release/android-signing.json` version to avoid release/current drift; native startup checks feed asynchronously without contacting Instagram, and token-protected loopback exposes status, check, download, cancel and explicit confirmed install.
- Validation requirements: `tests/test_windows_updater.py` (offline stable feed/certificate limitations, bad redirect and digest, opt-in check/download, cancellation, backup and auth token), `tests/windows-updater-ui.test.cjs` (buttons, actual JS, no auto-installs and standalone isolation). New gates in Windows preview/CI/governed publisher. Exact candidate Windows install/launch and rendered Desktop/Android remain subject to CI; owner's physical Windows/real update remains pending.
- Do not bump versions or publish v120.47 on a merge; the official stable remains v120.46 until separately authorized. No fixed follower analysis limit, no robots relocated from Automations.

## 2026-10-15 — Windows Profile Counts second audit and durable historical sync (v120.47, development)

- Main already had dated per-profile history, timeline comparisons and CSV exports under Automations; do **not** blindly merge old conflicting PR #106. This change fills the remaining Windows robot gap (#107) instead.
- Added `tools/profile_counts_audit.py`: bounded-per-request but unbounded total workspace queue, never-successful first and oldest successful thereafter, owner/account-scoped persistent `.reaudit.json` cycle with frozen order and attempt-completion journal. A paused or app-restarted unfinished cycle resumes by explicit owner start/resume action; a completed cycle generates a new oldest-first order. Challenge/login blocks stop rather than auto-proceed.
- Windows backend creates an append-only `.dated.csv` per account, seeds pre-upgrade latest measurements idempotently, records every new verified successful count and **never replaces a prior successful latest value with a later unavailable/error**. Each successful observation is fsynced before the cycle completion journal is written. A local capability-token-protected, 2,000-row-max-per-request paginated history endpoint supplies dated rows without imposing an overall analysis threshold.
- In the existing **Automations → Profile Counts** section added explicit **Start oldest-first re-audit** and **Sync Windows dated history**, retaining the installed Chrome Companion's own re-audit history, existing results and optional imports. UI shows per-cycle percentage, not misleading cumulative first-pass completion, checks active owner+Instagram workspace during paginated sync and preserves last valid counts against newer failed imported/robot results. No robot moved into Insights, no Instagram relationship-changing actions added.
- Added offline Python tests for real Collector start/resume/restart, history migration/deduplication, account isolation and pagination, and Node Desktop harness assertions for buttons, status, import/sync. Wired relevant tests into normal CI, Windows Setup preview and governed release CI; exact PR/current main CI results must be verified before integration.
- Owner's regular Chrome may still require explicit user-operated Chrome Companion; separate Playwright Chrome CAPTCHA loops are **not** bypassed. No official v120.47 release requested or published.

## 2026-10-15 — Reconcile new Windows installer against master governance audit

- Exact merged installable Windows Setup candidate passed all four main-commit UI/Windows/Android/CI workflows; the separate Michel's Lab governance run failed its cross-app installer source check.
- Root cause in IG Cleaner: master validator requires canonical product name within full legal license and bilingual taskbar guide, and a `{autodesktop}` shortcut scoped by `Tasks: desktopicon`; the branch's installer used `{userdesktop}` while its manifest registered a longer Windows-specific product alias. Corrected the taskbar guide legal name, Inno icon constant, and local contract. The master registry requires the exact canonical license name `IG Cleaner Pro` (separate PR).
- Unrelated FoamLens taskbar-guide contract also failed in the same audit and remains outside this IG Cleaner change. Verify new merged main and master governance run before closing.

## 2026-10-15 — Real native installer wizard/EULA visual gate added

- Extended the Windows Setup CI with `tools/test_windows_installer_wizard.ps1`: launches the actual interactive Inno wizard in English, navigates to the shipped LICENSE.txt page, requires the **accept / decline** radio controls, captures the real wizard screenshot, proves Next is disabled until acceptance, enabled on accept, disabled on decline, then closes without installing. Screenshot is retained in Windows validation artifacts (separate from published release files).
- Silent INSTALL/installed LAUNCH/in-place UPGRADE/UNINSTALL evidence is a separate test, not a substitute for wizard testing. Whether the latest exact-head CI passed is determined only by its completed GitHub Actions run; on the owner's device, visual acceptance and live Instagram behavior remain separate.

## 2026-10-15 — Native Windows installer for integrated Insta Cleaner robot (v120.47 candidate; NO release)

- Owner asked to replace extracting/running the Windows robot EXE with a normal Windows installer aligned to Michel's Lab bitácora and master standards. Added Inno Setup source at `packaging/windows-installer/InstaCleanerPro.iss` using the **existing official app ICO and full proprietary LICENSE.txt**; native welcome, required acceptance, bilingual installer language, unchecked desktop shortcut, installed Start menu shortcut, optional taskbar pin guide and proper Windows uninstall.
- Primary governed Windows artifact becomes `IG-Cleaner-Pro-Windows-Setup-v{version}.exe`, with portable ZIP retained as secondary compatibility; standalone Desktop HTML and production-signed Android distribution unchanged. Product AppId and per-user installation path remain stable for future manual in-place upgrades; local workspace/browser and legacy robot data live outside install folder and are never listed for removal.
- Installer packages the previously embedded PyInstaller runtime and `chrome-extension` folder without automatically installing/extending Chrome, bypassing Instagram security or enabling robot actions. Added deterministic `--smoke-startup` to test installed UI origin, installed Chrome detection and local loopback controller without logging in to Instagram.
- Windows preview and governed release jobs now compile native Setup with Inno Setup 6, verify payload/checksums, perform silent INSTALL → installed healthcheck + startup → UNINSTALL with a persistence sentinel, and upload/verify the installer in the eventual unified release. Appends static license/identity/payload/release contract tests; no release request or signing secrets modified.
- **Validation:** source modifications only until exact-head Windows CI and real installer wizard/owner Windows acceptance are observed. Silent CI is not a proof of rendered interactive EULA, Chrome login or account-changing actions. Windows Authenticode signing and automatic background updater remain unconfigured; never imply them.
- **Governance:** promote the newly installable Windows channel to Michel-Software-Standards installer and distribution registries, while retaining the separate standalone HTML exemption.

## 2026-10-15 — Persist longitudinal Profile Counts history inside Insta Cleaner (development v120.47)

- After PR #104 introduced the Chrome Companion's first-pass unmeasured priority, explicit oldest-first second audit, and append-only local Chrome history, an integration gap remained: Insta Cleaner Desktop imported only the **single newest** row per username, silently discarding older dated snapshots from the Chrome Companion's full-history CSV. The user needs repeated audits and reliable comparisons over time.
- Implemented per-Instagram-account **append-only IndexedDB measurement history** in Desktop Automations, using a separate `ig_cleaner_profile_counts_history_v1` database with scoped `measurements` and `profile` indexes. Existing `ig_cleaner_profile_counts_v2` latest-record database and previous v120.45/46 localStorage keys remain unchanged. In environments lacking IndexedDB, a separately scoped, explicit-quota-error localStorage fallback is used; no arbitrary record count cutoff and no destructive migrations.
- `igcCountsImportFile` accepts chronological history CSVs containing multiple dates for the same username, archives **every valid successful reading** (even older than current), and updates current latest only for genuinely newer observations. Imported foreign accounts/invalid rows never enter history. Browser robot polling also archives a previous successful observation before updating latest, and awaits storage success.
- Added **Export complete measurement history** and **View dated measurements** in Automations → Profile Counts, displaying the latest ten measurements and change in Followers/Following from preceding displayed reading. Historical profiles that are no longer in Following remain exportable within the *same owner/account* scope. Stored results are not evidence of current followback.
- Expanded `tests/profile-counts-ui.test.cjs` with historical CSV, timeline, older/foreign-account isolation, and browser-robot preservation checks. Expanded real-Chromium IndexedDB acceptance `tests/profile-counts-indexeddb-browser.cjs` with three dated snapshots and reload, historical v120.45 migration, rejected foreign usernames, and per-profile UI comparison. No live Instagram or owner's private Chrome/browser data were accessed.
- Security and release: Read-only Chrome Companion still requires explicit user clicks. Cancel Pending/Unfollow still require verified account identity and separately authorized batch; no CAPTCHA bypass. Official release remains **v120.46**, development target **v120.47** without release permission. No claim of real-owner Chrome acceptance.

## 2026-10-15 — Priority and longitudinal re-audits for Chrome Companion (v120.47 development)

- Owner clarified that Profile Counts must keep prior counts for each profile, **prioritize never-measured**, and then allow a **second audit prioritized by oldest previous review/measurement**.
- Updated Chrome Companion to store each successful Followers and Following snapshot with checked_at, source and precision per username, preserving history even after a queue refresh. The popup first-pass queue sorts never-measured before incomplete and skips complete measurements; a user-initiated oldest-first re-audit snapshots a bounded per-cycle ordered target list and records completed profiles without repeats. Re-audits re-sort by the last saved timestamp on every newly started cycle.
- Exports latest valid Profile Counts rows for existing Automations import and a separate dated CSV of all historical snapshots; displays both numerical deltas after a repeated measurement. Migrates prior single-snapshot extension records into historical timelines without deletion.
- Extended automated VM tests to cover ordering, both re-audit modes, per-cycle persistence, change deltas, and preserving older snapshots. Verification must be judged from the exact GitHub PR head; no real Instagram counts collected and no release authorized.

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

## 2026-10-15 — Live Instagram reCAPTCHA login loop; v120.47 safety and login UX fix (unreleased)

- Owner's **real Windows Chrome screenshot** shows Instagram's `/auth_platform/recaptcha` with an “I'm not a robot” checkbox. Owner reports completing the CAPTCHA returns to Login. This is evidence of a real **authentication/security challenge**, NOT proof that Instagram accepted the session, and NOT a successful robot action.
- Confirmed source defect: `challenge_detected` recognized `/challenge/` and `/checkpoint/` but NOT `/auth_platform/recaptcha`. Profile Counts could wait without recognizing the challenge and, after 15 seconds, attempt an optional own-profile navigation while a person was trying to sign in.
- Fixed challenge recognition by route and visible security copy. A new `safe_to_probe_owner_from_home` guard only permits the one-time read-only own-profile identity probe from actual Instagram Home with no login/password/challenge screen.
- Profile Counts now reports `needs_verification`, holds navigation while Chrome remains open for **human-only CAPTCHA handling**, and resumes ordinary identity checks only after challenge disappearance. If Instagram loops back to Login, no collection or account action is allowed without positive account identity verification. User may Pause; saved queues/history are not destroyed.
- Cancel Pending/Unfollow actions now fail closed on a challenge in any browser tab during login, rather than trying to proceed or automatically solving it. No change to action-confirmation gates, rate limiting, protected accounts, journal integrity or session isolation.
- New offline URL/body/security and login-page probe regression: `tests/test_profile_counts_recaptcha.py`, triggered by Profile Counts CI and Windows EXE workflow. Updated Automations status and `docs/PROFILE_COUNTS_ROBOT.md` recovery advice, including normal-vs-robot Chrome profile distinction and no cookie upload, CAPTCHA bypass or storage deletion.
- No real login was attempted by development. Whether Instagram will accept the separate Playwright/Chrome session remains outside the app's control and must be tested only by the owner. Official stable remains **v120.46**, next v120.47 has **no release authorization**.

## 2026-10-15 — v120.47 Automations Windows English + documentation regression gates (development only)

- Continued from official stable v120.46 and merged PR #99 (v120.47 source). Verified that the source already includes the Python Profile Counts `http`-prefix username fix, independent read-only owner identity proof for account actions, and per-profile results in Automations. These remain **unreleased** and unaccepted on a real Instagram session.
- Updated `tools/profile_actions.py`, `tools/profile_counts_bridge.py`, and `tools/profile_counts_robot.py` so new robot status, CLI and validation errors are in English. Preserved the Spanish labels/phrases used to recognize Instagram's localized DOM and to classify existing journal records.
- Updated integrated Windows package `packaging/profile-counts/README.txt`: all robot controls **and individual Profile Counts results** remain under Automations, Insights is aggregate-only, browser robots cannot navigate Chrome simultaneously, and local IndexedDB migration is implemented (no longer an open #96 task).
- New `tests/windows-automations-owner-contract.py` covers Windows package owner instructions and English error paths; the test is required by general CI and governed release QA. Updated developer `AGENTS.md`, current `README.md` and handoff to prevent old v120.44/v120.45 release guidance from overriding the authoritative manifest.
- Branch: `fix/v12047-english-automation-packaging-20261015`. CI and PR exact-head checks **pending at time of entry**. No release authorized. Physical Windows Chrome/Instagram and actual cancellation acceptance remain explicitly open.

## 2026-10-14 — PR #99 merged after reported Windows v120.46 failures

- Main squash `298bf52e7230fba22501a1ac24852023ec4aafda`; exact PR head `9e8ee7e511e0c7e5f07dbed2a0965add95d806f2`. 5/5 CI passed (counts, Windows integrated executable, Desktop rendered UI, Android emulator, general CI).
- Fixed imported Profile Counts list rejection for `http`-prefix usernames; fixed failing owner session verification on target profiles without Profile nav using a strict separate owner proof tab; moved the whole Profile Counts results experience to Automations.
- Confirmed no pending request was canceled in the owner's reported 1/40 screenshot. Existing safe no-click errors may be retried only in separately authorized future batches; unknown post-click states are not repeated.
- v120.47 remains unreleased. Current official stable v120.46 still has the user-reported bugs. Live Instagram session acceptance is an outstanding physical test.

## 2026-10-14 — v120.47 corrective development after real v120.46 Windows feedback

- Owner screenshots exposed two real failures on Windows stable v120.46: **Cancel Sent Requests** processed 1/40 and blocked because owner identity disappeared on a target profile (no request was canceled); **Profile Counts** failed before launch with “Import contains invalid profile usernames.” Owner again clarified *all of Profile Counts*, including its collected per-person results, belongs in **Automations**, not Insights.
- Fixed Profile Counts username validator mistakenly treating any handle beginning with `http` (e.g. `http.cat`, `httpshop`) as a URL. Only explicit `http://` and `https://` URLs are parsed now. Added end-to-end staged import regression covering `http` handles so a single such profile cannot reject a large queue.
- Cancel/Unfollow action preflight now verifies the expected Instagram account safely in a **separate, read-only tab** of the same persistent Chrome context when the target profile hides the signed-in user's Profile navigation. It requires own-profile username heading and visible Edit profile control, refuses incorrect/ambiguous accounts and does not modify the target page to verify. Rechecks identity before sensitive clicks and after action.
- Previously saved `blocked` results are eligible for retry **only if they explicitly documented zero clicks**. All ambiguous, changed-account, after-click or uncertain results remain protected from automatic retries.
- Relocated all Profile Counts result tables, search, filters, exports and robot controls to **Automations**. Insights now only has aggregate account-level analytical panels. Updated the explicit DOM contract tests accordingly.
- Added offline Chromium tests of Cancel Pending with collapsed navigation, correct owner vs mismatched owner, and no-click recovery. None of these tests claim a real Instagram cancellation succeeded.
- This is v120.47 development. The installed v120.46 is still stable/public, with these bugs. Do not release without exact-head Windows/Android/Desktop/Profile Counts CI and an explicit owner release request. Live account acceptance remains pending.

## 2026-10-14 — v120.46 officially published

- Owner-authorized stable v120.46 published, normal GitHub Release: https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.46 .
- Exact publication source `4550635e7435002915b47472452c4c74aba1bc04`, governed workflow #38658477664 **success** with all four jobs green and all seven assets verified. Signed Android APK, integrated Windows EXE ZIP, Desktop HTML/ZIP, logo, privacy and checksums.
- PR #98 merged as `7939dafc61fa2b578e7b2ae2d433dbb2dae7d500`; issue #96 closed. Updated source baseline to unsigned/unreleased v120.47 with `authorized=false`.
- Remaining external acceptance: user's physical Windows/Instagram session and Android installation; quota depends on available device storage rather than arbitrary application-level follower counts.

## 2026-10-14 — v120.46 development: large historical Profile Counts + cross-device audit migration

- Owner explicitly authorized completion and release of v120.46. Publication is **gated by exact-head CI, Android production signing, Windows EXE and Desktop artifacts**; authorization is not proof that a release succeeded.
- PR #98 implements owner/account-scoped IndexedDB records in the Desktop Profile Counts UI, transactional 500-record chunk writes, idempotent legacy localStorage migration and non-destructive backup retention. Storage/quota errors are shown; data is not silently dropped. Successful imports and robot results now await durable writes.
- CSV results export uses streaming file writes when available, or bounded-content segments before Blob fallback.
- Cross-device audit reconciles legacy fallback events into IndexedDB and removes the 12,000-event cutoff. Explicit errors replace silent fallback quota failures.
- New browser tests cover v120.45 legacy count migration, IndexedDB persistence/reload, account isolation, 50k/100k/250k aggregate/pagination correctness and 12,031 historical audit events. Unit/visual/Windows/Android checks remain required before merge.
- PR #97 already delivered unified Automations, large chunked imported queues and shared Chrome locks. Real Instagram acceptance, physical hardware validation and actual device storage constraints remain separate.
- Latest normal published release remains v120.45 until the governed v120.46 publication is confirmed.

## 2026-10-14 — v120.46 unified Automations implementation merged into main

- **MERGED:** PR #97 (superseding PR #95), squash merge `16c78ba84e6d110c7ef7ba8d6b2498f9078d0286`; changes are now in `main` only, **not yet published as a release**.
- The **exact PR head** `c0c33d9efeb1bd90c836783af8b928bfa6bf5320` passed all five gates: Profile Counts tests (38655858892), Desktop rendered UI (38655858890), integrated Windows EXE (38655858854), Android About emulator UI (38655858876) and IG Cleaner CI (38655858859).
- **Owner requirements implemented:** every robot now starts under Automations → Automation Center; Insights retains analytical results and pagination without reducing counted profiles. Chunked owner-scoped imported lists remove the former 50,000-person queue ceiling. Shared browser-admission locking prevents simultaneous Chrome actions/collection.
- **Still open:** browser localStorage quota can restrict very large historical data retention despite arbitrary list caps being removed. Issue #96 tracks an IndexedDB migration with high-volume synthetic tests and safe legacy history migration. End-to-end real Instagram session acceptance remains pending.
- Published stable release is **v120.45**; next development v120.46 has **no release authorization**.

## 2026-10-14 — v120.46 development: unify Automations, remove relationship dataset ceilings

- Owner reaffirmed two non-negotiable requirements: the number of people following or followed **must not impose an arbitrary dataset-count cap on analyses**; and **all Instagram robots must be accessible in the Automations area**, not split between Insights and Automations.
- Moved the complete Profile Counts Chrome robot (connect, pause, resume, current profile, pacing, optional browser Following refresh and manual CSV robot controls) out of Insights into a dedicated panel in Automations beside Unfollow, Cancel Sent Requests and optional Followback Audit. Kept Insight numerical summaries, profile counts results and exports on the Insights page, with a navigation link to Automations.
- Removed the global 50,000-profile imported queue cap and single huge request dependency. Profile Counts now stages arbitrary-size imported Following lists in owner/account-scoped, ordered 1,000-profile UI chunks (up to 2,000 per transport request), validates receipt and uniqueness atomically, then starts the Chrome collector only after all chunks have arrived. The request-byte cap remains **per HTTP request**, not per dataset.
- Added result-table pagination (250 rows rendered per page) so all matching rows remain accessible while aggregates count the **full** imported list. Pagination is presentation-only and never truncates analytics or exports.
- Added a shared browser admission lock across Profile Counts and the account action robot, preventing simultaneous use of their single persistent Chrome session. Parallel *local* analytics remain possible and should not be confused with parallel Instagram browser robots. Relationship-changing actions still require explicit approval, owner match and rate-control guards.
- Validation additions include 50,003-profile staged queue acceptance, ownership mismatch and duplicate rejection, missed-chunk atomicity, nonconcurrent Chrome robot admission, 50,003-profile Insights aggregate and multi-page result access, Windows Chromium staging and nested local bridge routes.
- This is development v120.46; v120.45 remains the published stable. No new release authorization. Real signed-in Instagram and physical Windows/Android acceptance remain pending.

## 2026-10-14 — Imported Following is authoritative for Profile Counts; no redundant browser discovery

- Owner supplied a real Windows v120.44 screenshot: @realmichelduarte session detection succeeded, but the robot failed because it searched for a visible own-profile Following link, then closed Chrome. The owner confirmed Insta Cleaner already holds **11,869 Following profiles** and wants the robot to visit those accounts directly to read their public Followers and Following counts.
- Corrected development flow: Desktop sends the current selected-workspace imported Following handle list to the local authenticated robot; imported profiles take precedence over a possibly stale browser discovery cache. The robot verifies the logged-in Instagram identity, resumes persisted per-account results, visits each imported profile and never opens the owner's Following dialog in this default mode.
- Raised the bounded imported queue ceiling from 10,000 to 50,000 (existing body-size guard still applies); explicit 11,869-profile test checks there is no silent truncation. Empty imports now show guidance rather than initiating implicit Instagram Following discovery.
- Browser discovery remains an **optional separate user action**, labeled "Refresh Following from Instagram (optional)", with safe owner verification, manual-recovery retry and unchanged protected/private-session boundaries. Imported snapshot completeness must not be misrepresented as a live Instagram-followback audit.
- Added Python import/identity/opt-in/end-to-end tests and file:// Chromium bridge fixture proving the queue comes from imported data without a Following UI scrape; old tests updated to opt into discovery explicitly. All tests are simulated, not acceptance of real 11,869-profile Instagram navigation or the owner's physical Windows installation.
- Applies only to unreleased v120.45 source PR #94. The existing v120.44 release is unchanged; publishing requires a new explicit owner instruction.

## 2026-10-14 — Live owner screenshot: Chrome signed in but Instagram Home account not detected (development fix)

- Owner's Windows v120.44 screenshot shows Instagram Home displaying the signed-in account with **Switch** in the right-hand account row, while Insta Cleaner Insights → Profile Counts remains at zero and reports identity not yet verified. This is live evidence of the symptom, **not** acceptance of a corrected build.
- Root cause in source: `signed_in_handle` relied on a semantic Profile navigation anchor or Edit profile inside a profile header; the Home account/switcher row is not recognized, particularly with collapsed/nonsemantic Instagram navigation.
- Development branch `fix/ig-home-switcher-login-20261014` detects a **visible, compact row** containing one valid Instagram profile link adjacent to a Switch / Cambiar control. Multiple or conflicting candidate handles, hidden controls, login forms, arbitrary suggested accounts and nav-vs-switcher disagreement fail closed. Existing semantic nav recognition remains.
- If Home still has no positive identity after a wait, the collector makes **at most one read-only visit** to the exact selected Instagram profile. Only a matching header and an **Edit profile** control prove ownership; a URL or preselected handle alone is never accepted. This does not trigger follow/unfollow/cancel, bypass a challenge or use private APIs.
- Added offline Chromium Home-account fixtures for positive Switch/Cambiar, collapsed nav, suggested profiles, hidden/login/ambiguous controls, conflict, and strict Edit-profile fallback. GitHub exact-head CI and the user's actual installed Windows session still require validation.
- Preserve existing account scopes/history and mark all real Instagram acceptance as pending. Development v120.45 only; stable v120.44 remains published until a separate explicit release request.

## 2026-10-12 — JWT expired during Desktop profile registry sync (user screenshot; development fix)

- User supplied screenshot of **Cuenta y sincronización** signed in to an IG Cleaner login, but cloud list profile registry failed with **JWT expired**. Source root cause: the shared Web sync client restored tokens as connected, only attempted a refresh after an HTTP 401/403, lacked proactive expiry handling/single-flight rotation and left the sign-in form hidden if rotation failed. Android's native client also refreshed only reactively and could accept an older WebView token after native rotation.
- Development branch `fix/supabase-jwt-refresh-20261012` adds Desktop/embedded-WebView proactive JWT expiry checks (server expires_at or JWT exp), single-flight refresh, automatic bounded retry on 401/JWT-expired 403, owner identity safeguards against pending refresh after account switches, and a visible login form only when refresh is definitively rejected. A temporary connectivity failure never deletes or logs out saved local state.
- Native SyncApi stores and conveys expires_at and refreshes before expiring authenticated requests; it refuses a stale WebView callback from overwriting a newer same-owner native token. Keeps former 401 fallback. Does **not** mutate Supabase/Auth hosted settings, migrate profiles, clear local data, or change release numbering/signing.
- Added full shared-sync JavaScript VM behavior contract and a native source guard, included in standard CI.
- **QA/release:** checks pending on exact PR head; user should reload their current app and, if refresh token is already invalid, sign in again using **Cuenta** (do not delete profiles or clear data). Published v120.42 remains unchanged; v120.43 requires separate explicit release instruction.

## 2026-10-12 — v120.42 stable publication verified (Windows Profile Counts + Android + Desktop)

- User explicitly requested **"dale release para probarla"**. Governed normal release [v120.42](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.42) published at **2026-10-12T07:13:17Z**, release commit `1c806e34e3f3b84c9311f466353a6ad30fe735c2`, GitHub Actions run **38216103775** SUCCESS.
- Seven assets confirmed in live GitHub release, including `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.42.zip` (48,578,715 B), `IG-Cleaner-Pro-Android-v120.42.apk` (7,886,660 B), `IG-Cleaner-Pro-Desktop-v120.42.html` (3,307,218 B), full Desktop ZIP, privacy, logo and SHA256SUMS.
- Windows automation is **PC Chrome + persistent local browser controller only** and attempts to detect the signed-in Instagram account, collect its visible Following list and profile Followers/Following counters without manual CSV imports or exposed pacing controls. **Real Instagram signed-in DOM remains UNTESTED**; this is the first owner-testing release and automation may fail or be restricted. Android is signed with same production certificate, but does **not** host Windows Playwright collection or automatically sync the new counts across devices.
- First governed run 38215091151 failed during post-download archive validation (ZIP basename mismatch), **before publishing**; corrected the Windows ZIP version interpolation and download file normalization, added full Python ZIP-content verification instead of fragile `unzip | grep -q` pipefail, retriggered the owner-authorized request and verified successful publication. First run did validate signed Android package/certificate.
- Reconciled `release/distribution-manifest.json` current stable v120.42 / next target v120.43; consumed release-request authorization (`authorized=false`, `status=published`). Do not re-publish without new explicit instruction. Outstanding: owner Windows Chrome and authentic Instagram acceptance, physical Samsung install, optional Desktop↔Android counts sync, and preserving existing IG Cleaner workspaces.

## 2026-10-11 — Autonomous visible-browser Instagram Following discovery (PREVIEW, NOT RELEASED)

- Owner clarified: **do not show manual batch/cadence settings or require manual CSV queue**. Desired UX: open Insta Cleaner with the local PC launcher, log into Instagram in its browser window, then automatically discover the owner account, enumerate visible Following profiles and collect both visible Followers/Following counters; save progress with internal pacing.
- New `tools/profile_counts_instagram.py` reads labeled Profile navigation links, verifies a single unambiguous Instagram username, opens the normal `/username/` profile, clicks the visible Following control and scrolls the dialog using rendered DOM links (not Meta/private APIs). Persists discovered queue with account-handle provenance to an atomic local cache. Does not ask for passwords, follow/unfollow, or solve challenges. If Following cannot be fully read, it marks discovery incomplete; no invented counts.
- Loopback bridge: new idempotent `POST /api/auto` and `GET /api/following`; existing isolated owner + immutable Instagram account key retained. Automatic worker opens a persistent browser, waits for normal user login by observing the page, validates the detected Instagram username against the active account's known/cached handle, discovers profiles and uses the existing saved pacing/after-N rests before gathering counts. Aborts account mismatches rather than mixing data.
- Desktop Insights: the local launcher auto-initiates; the new browser Following list populates Profile Counts even when `followingRaw` is empty. Internal manual controls, CSV buttons and CLI instructions are hidden while the bridge is connected; progress/measurements remain visible. CSV mode remains available only when disconnected as a fallback. User does not need to configure a quota or press Start/Ya inicié sesión.
- Added simulated browser bridge and account-isolation acceptance in Python and Node, and a real Chromium file:// ↔ loopback test that starts automatically without manual queue or button. **No real Instagram account/DOM test** yet; visibility, interaction, Instagram platform restrictions and mobile runtime are unresolved. Windows remains a PC-local robot (not a standalone Android background collector). Do not merge or publish v120.42 based only on test fixtures.

## 2026-10-11 — User-configurable robot pacing and explicit long rests (UNRELEASED)

- User requested full timing control while reading all Instagram Following profiles: e.g. "200 every 5 minutes" and "wait 5 seconds between profiles." Added independent **maximum visits per rolling window**, **window duration in minutes**, **minimum time after each completed profile**, and optional **rest of configurable minutes after every N profiles**. The example of 200 per 5 min with a 5s gap yields at most about 60 visits per five minutes, not 200; the UI explicitly displays that limit. A separate 5-minute *rest after 200 profiles* may be enabled independently.
- Introduced `tools/profile_counts_pacing.py`: bounded input checks; atomic per-account `.visits.json` records **every attempted profile before navigation** and extends the visit timestamp to completion for the actual gap; preserves cooldown across pause/crash/restart. Added `.batch.json` for optional long-rest counter and `rest_until`, likewise persistent across launches. Scheduler uses the longest wait required by all enabled constraints and allows manual stop during waits. Failed/challenged profiles still consume slots; no bypass, CAPTCHA solving, or access to Instagram private endpoints.
- `tools/profile_counts_bridge.py` accepts `max_per_window`, `window_minutes`, `min_delay_seconds`, `pause_every`, `pause_minutes` on start/load and exposes them in status. CLI `tools/profile_counts_robot.py` accepts `--max-per-window`, `--window-minutes`, `--min-delay-seconds`, `--pause-every`, `--pause-minutes`; retains legacy `--per-hour` behavior if no explicit new count.
- Desktop Insights has five numeric controls, effective-rate explanation, progress/status, and per-owner + immutable Instagram `account_key` localStorage persistence for timing preferences. Separate all new scheduling/visit logs by account; never mix the data of different Instagram profiles.
- Added unit tests for independent pacing, 200/5min/5s, long rest, invalid settings, crash/restart and after-page delays; updated Node UI owner-isolation and real Chromium loopback request tests. Latest exact-head workflow validation must finish before merge. The existing v120.41 public release remains unchanged; no v120.42 publication authorized. Real Instagram authenticated DOM and Windows owner-device acceptance are outstanding.

## 2026-10-11 — Profile Counts direct PC ↔ local robot bridge (candidate, NOT released)

- User asked to avoid Meta API permission and minimize manual exports. Added `tools/profile_counts_bridge.py`, loopback-only `127.0.0.1` HTTP controller; a random per-run token is passed in a local HTML file URL fragment by the launcher. All API routes require its bearer capability in a custom request header and refuse non-local web origins; cookies/password remain in the user-operated local Chromium profile. The browser robot still reads only *rendered profile text*.
- Insights now has direct **Iniciar recopilación / Ya inicié sesión / Pausar robot** controls, 1–60 visits/hour setting, live status, automatic record import and local owner + Instagram `account_key` separation. Original CSV export/import stays as offline/mobile fallback.
- Back-end job persists CSV atomically after every visited profile, resumes `ok` rows, halts on Instagram challenge/login/block, and does not bypass restrictions. PC and launched local bridge process must stay running; Android cannot host desktop Playwright. The launcher must point to the user's exact existing HTML to maintain its existing profile/local storage origin; published v120.41 does not include it.
- New bridge unit tests enforce no unauthorized route reads, invalid input rejection, isolated result paths and local-only simulated start. **Exact PR CI** Profile Counts offline contract passed 11 Python cases plus Node source/owner-isolation case at commit `65474c978e240da1a8b89a69cb24eb8c03d3871c`. Other build/UI jobs must complete on this head; real Instagram login/DOM and file://→loopback browser interaction remain **untested**. Prior Android CI run failed visual screenshot capture after 12 frames (7 of 8 instrumented tests passed), not a confirmed app behavior regression; retest triggered and later superseded by new pushes.
- Next: real Chromium loopback UI acceptance, Android rendering/import compatibility, packaging/installers and manual real Instagram preview, plus documented data/security consent boundaries. **Do not publish** v120.42 or claim production readiness without these checks; v120.41 remains stable.

## 2026-10-11 — Profile Counts (robot navegador, NO API) — candidate branch, unreleased

- User clarified the requirement: **read Followers and Following counts shown on each third-party Instagram profile by visiting ordinary profile pages with a locally operated browser**, not via Meta API/app review. CSV export is optional workflow plumbing, not the purpose of the feature. Target cadence is configurable (e.g., 50 profiles/hour), not a guaranteed successful throughput.
- New **Insights → Profile Counts** surface for the active Instagram workspace: exports username/profile URL queue from already-loaded Following, imports robot CSV incrementally, filters pending/available/failed, renders observed counts/time/approximate status, exports complete results. No guessed data, no change to relationship/risk/review/Focus datasets. Stores new records using an explicit **app login owner + immutable Instagram account_key** key in local device storage; imports reject rows outside current Following and malformed numbers.
- New local visible-browser Playwright robot `tools/profile_counts_robot.py`: operator signs in in persistent local Chromium profile, robot visits profile URLs and reads header/meta description numbers; CSV checkpoints atomically after every visit, skips checked profiles on resume, spaces requests based on `--per-hour`, stops on login/checkpoint/challenge and never bypasses CAPTCHA, private endpoints or throttles. No passwords/API tokens in app/code. `docs/PROFILE_COUNTS_ROBOT.md` documents setup, policy caveats and exact limitations.
- **Evidence:** static source additions with Python unit cases and Node VM source/owner-isolation tests; focused CI workflow added. **Not yet live-verified or merged**. Must check exact-head GitHub workflow, packed Desktop Chromium, packaged Android/WebView file picker, real-session Instagram DOM, and backward compatibility before release. No production Supabase migration/sync of these new counters; device-to-device automatic sync remains an open separate task.
- Meta's Automated Data Collection Terms can prohibit scraping without prior written consent; avoid describing this as approved or guaranteed safe. Users should know account access can be restricted. No release/version bump: published v120.41 unchanged, proposed v120.42 requires explicit authorization. Issue #77.

## 2026-10-11 — Owner verified official Gmail sender and account switching; OTP copy mismatch identified

- New real delivered email screenshot shows **Michel's Lab · IG Cleaner Pro <michelslab.dev@gmail.com>**, not the old Brevo sender; owner reports both sign-up completion and the **Switch account** function working. No OTP value or password is captured in GitHub notes.
- The displayed OTP has **eight numeric digits**, even though both hosted email prose/template source describe a **six-digit** code. The app accepted the user's signup, so this is a **copy inconsistency**, not a broken registration method. Source Confirm sign up and Magic Link email templates now say **verification code** without a length promise; tests assert length-neutral messaging. A hosted Auth email-template update is necessary to reflect the revised source text live; our connected tools cannot save Supabase Auth email templates.
- Authentication RLS/account isolation, multiple real Instagram ZIPs and cross-device account switching with preserved history remain separately tracked in issue #24. Production v120.41 remains official; no v120.42 authorization nor binary release.

## 2026-10-11 — Owner confirmed OTP signup works after provider-side fixes

- **User-reported live acceptance:** owner configured Google Gmail SMTP within Supabase Auth (previous screenshots showed `smtp.gmail.com:465`, `michelslab.dev@gmail.com` username, 60-second interval), saved the settings, installed both `{{ .Token }}` email templates from the repository and then confirmed they **received the six-digit code and successfully registered a new IG Cleaner account**. This resolves the previously demonstrated inability to complete the requested code-based new-user registration *for that tested path*.
- **Evidence boundary:** user performed the provider actions directly. We did not see the final authenticated email headers, read confidential OTP/passwords, run separate email delivery from the plugin, prove Inbox instead of Spam, check an additional device, or verify cross-login isolation/recovery. These stay explicitly open in [issue #73](https://github.com/michels-lab/IG-Cleaner-Pro/issues/73) and #24.
- No new source release or further Supabase API modification is required for the now-functional hosted OTP path. Published stable remains **v120.41**, governed next **v120.42**, unauthorized until a new explicit release request.

## 2026-10-11 — Confirmed official Michel's Lab Gmail identity and practical SMTP route

- User clarified sender identity is **`michelslab.dev@gmail.com`**, a Gmail mailbox; company **does not own `michelslab.dev` domain**. Earlier placeholder `no-reply@michelslab.dev` must not be used without domain ownership and authentication.
- Brevo's official mail sender policy reassigns free Gmail senders to `@brevosend.com` (or transactional equivalents) since Gmail domains cannot be authenticated in Brevo; consequently using Brevo cannot guarantee an actual `@gmail.com` From identity. Setup guide changed from Brevo sender verification to conditional direct Gmail SMTP for small volumes: sender/username `michelslab.dev@gmail.com`, `smtp.gmail.com`, TLS port 465, dedicated Google app password after 2-step verification, sender display Michel's Lab · IG Cleaner Pro.
- **No Google credentials requested or handled. No live SMTP/Supabase Auth configuration applied** (current tools lack the relevant provider settings action); production P0 issue #73 tracks end-to-end acceptance. Verified source OTP templates remain prepared, no APK release or user-data change.

## 2026-10-11 — Signup confirmation mismatch: OTP requested, magic link delivered (source prepared; hosted Auth pending)

- **User evidence:** freshly requested registration email titled “Confirm your email address” contains clickable link and arrives in Spam as `IG Cleaner <realmichelduarte@12366255.brevosend.com>`; opening link attempts `localhost:3000/#error=access_denied&error_code=otp_expired` and gets ERR_CONNECTION_REFUSED. The app's existing native/Desktop `/auth/v1/otp` and `/auth/v1/verify` flows expect an email code.
- **Root cause:** Supabase default confirmation/magic-link HTML uses `{{ .ConfirmationURL }}`; it must contain `{{ .Token }}` to provide an OTP. `localhost:3000` is a hosted Auth development URL, not a running local IG Cleaner callback. The actual SMTP sender is a Brevo provider subdomain, not a verified Michel's Lab mailbox. Merely changing the display name does not authenticate an email domain.
- **Prepared in source:** canonical six-digit Michel's Lab confirmation and magic-link HTML under `supabase/email-templates/`, safe opt-in template-only Supabase Management API sync/verification utility `tools/configure_auth_email_templates.py`, CI offline template contract, and `docs/AUTH_EMAIL_SETUP.md` with precise dashboard steps and real end-to-end test matrix. No production Auth config, SMTP, Site URL, customer accounts, Instagram data, auth providers or database policies changed; no credentials committed.
- **Blocker:** connected Supabase tool has no hosted Auth template/SMTP/redirect write action; connected Brevo sender management is unavailable. A dashboard owner or a privately provided `SUPABASE_ACCESS_TOKEN` on an authorized maintainer machine must apply templates to production; sender/domain verification must occur in provider settings. Distinguish tested source from LIVE provider configuration. **Public v120.41 unchanged; v120.42 not authorized.**

## 2026-10-11 — Closeout QA infrastructure: pinned Supabase CLI

- The post-publication documentation PR #71 RLS job initially failed **before running any database assertions**: `supabase/setup-cli@v1` with `version: latest` returned `Failed to resolve latest Supabase CLI release: rate limit exceeded`. This was a GitHub dependency-resolution failure, not a product security/test regression.
- Replaced the unbounded `latest` lookup with the verified upstream latest stable **Supabase CLI v2.120.0** (GitHub release published 2026-10-06). Existing RLS database test content, schema, owner policies and runtime/release workflow remain unchanged. Re-run exact-head CI required; keep failure transparent until green. Public v120.41 already shipped successfully before this separate docs/CI issue.

## 2026-10-11 — v120.41 stable Desktop + Android published, verified and reconciled

- **Published:** [GitHub normal stable v120.41](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.41), `draft=false`, `prerelease=false`, 2026-10-11 08:50:34 UTC, exact source commit `1f711badcbc902e61beb7e382a49fe55f87fe9a1`. Governed publisher [run 38125964658](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38125964658) completed **SUCCESS**, including real installed-Android/Chromium visual screenshot evidence check tied to this release commit, Android production keystore and APK signer/version checks, independent HTML and ZIP creation and GitHub asset validation. Five exact-head PR #70 checks and all five exact release-source CI checks passed.
- **GitHub assets checked:** `IG-Cleaner-Pro-Android-v120.41.apk` (**7,879,580 bytes**), `IG-Cleaner-Pro-Desktop-v120.41.html` (**3,283,790 bytes**), optional `IG-Cleaner-Pro-Desktop-v120.41.zip` (**1,401,875 bytes**), `SHA256SUMS.txt`, logo and PRIVACY.md. Standard package `com.michelslab.igcleaner`, versionCode **12041**, original persistent signing certificate. This is not Google Play distribution nor physical Samsung validation.
- Release delivers merged PR #67 Desktop complete account names + independent authenticated cloud profile registry refresh and PR #69 separate **Switch account / Cambiar usuario** actions for IG Cleaner login on both platforms, protecting Instagram workspaces. No Supabase production migration, actual user-data mutation, or local data wipe occurred in this release.
- Post-publication governance closes the consumed `authorized=false` request, updates `currentStableRelease=v120.41` and sets `nextRelease=v120.42`. No duplicate release; physical Samsung v120.40→v120.41 upgrade, own-account switching and genuine Instagram ZIP/sync round-trip remain pending issue #24.

## 2026-10-11 — User-authorized coordinated stable v120.41 release candidate

- User explicitly instructed **dale release** following integrated account-switch PR #69 and Desktop profile-selector PR #67. Public current stable is v120.40, latest verified GitHub release target `7ec454cbc5852bb8e96b9bd7ff59830b5872bb5a`; manifest next release is v120.41.
- Prepare identical v120.41 identities for Desktop title/About UI and signed native Android versionCode 12041/versionName 120.41, updating exact-version tests and release notes. Preserve Android package `com.michelslab.igcleaner`, original permanent production certificate, all `legacy` state/storage, Supabase RLS tables and cloud identities.
- Govenered `.michelslab/release-request.json` requests **normal stable v120.41** (`authorized=true`, `prerelease=false`) by this user's fresh request. Do not mark published until the exact main-commit action completes with verified signed APK, standalone Desktop HTML, ZIP, checksum, real emulator/Chromium screenshot proof and GitHub release assets. No pre-publication human review requirement; Samsung acceptance #24 remains post-release.

## 2026-10-11 — IG Cleaner account switch merged; release remains paused

- [PR #69](https://github.com/michels-lab/IG-Cleaner-Pro/pull/69) merged to `main` as `f66f9489fa468c45def86f4ee6845a5df3f84113` after all **five exact PR-head GitHub checks succeeded**: Desktop local contract, actual packaged Desktop Chromium visual, Android build/embedded workspace, installed Android emulator compact/wide About UI, Supabase RLS isolation. Correct distinction between app Auth user switch vs per-login Instagram workspace selector; preserves stored per-user data.
- Published GitHub stable remains **v120.40**; `release-request.json` still has `authorized=false`. User paused **v120.41** release; merging PR #69 did not authorize or publish a new Android/desktop artifact. Main push CI re-runs independently; real Samsung multi-login acceptance remains pending #24.

## 2026-10-11 — Account switching across Desktop and Android (PR candidate; no release)

- Added **Switch account / Cambiar usuario** beside existing Sign out in IG Cleaner Auth account screens. This switches the IG Cleaner *login* (email), not the selected Instagram workspace under that login. Sign out keeps the remembered login email; Switch account explicitly resets email and credentials, then presents a fresh login. No remembered passwords, new Auth service or migration.
- Desktop switch refuses while active sync is running, asks for confirmation, invalidates session/Android bridge explicitly, clears only shared sync metadata and email hint, then reloads into the signed-out owner namespace. Other users' Instagram registry, legacy/local reviews, IndexedDB and cloud data are not deleted.
- Android switch serializes logout behind existing native IO, resets in-memory lists, Focus/audit selections, clears account email and tokens, and returns to native login. Existing owner/profile-scoped persistent caches are preserved (unlike normal existing Sign out). Email identity changes now occur only after successful password Auth responses.
- Embedded Android WebView sanitizes an old different-owner session early, uses the actual native identity (including signed-out) as the local owner, never clears a newer native Auth session from an uninitialized web page, and restores native-authenticated session on bridge bootstrap.
- Added behavioral guard to existing multi-Instagram contract testing Desktop switch, busy/cancel paths, native UI & session isolation. Physical Samsung real two-login/ZIP round-trip acceptance still pending under #24.
- **Status:** branch `feat/switch-ig-cleaner-account-20261011`; source changes, automation validations pending exact PR head. Public stable **v120.40** remains unchanged; **v120.41 is paused** following user's request to wait. No release, version bump, production cloud mutation or destructive cleanup authorized.

# IG Cleaner Pro — Project Log & Functional Contract

## 2026-10-11 — Desktop account list and full @handle display corrected; merged, unreleased

- **Merged:** [PR #67](https://github.com/michels-lab/IG-Cleaner-Pro/pull/67), squash `6a7049702f284c2cae378d7aaecff31f5f3a0a80`, exact tested head `1a476fdbb1b6d85497d332086ae2d7ad2bb00421`. Previous PR #66 superseded because cross-app visual QA was merged concurrently.
- **Root causes:** ① Desktop `select` shared a flex row with four actions and could shrink to “Dat”; responsive @max780 further collapsed the entire Instagram section to zero width. ② Desktop initially showed only cached `legacy` and fetched additional identities via authenticated full sync without a visible explanation of missing account/session or cloud fetch error.
- **Shipped-to-source fix:** long @usernames wrap fully inside dedicated active-account card; full-width dropdown; labeled two-column action grid with manual `Actualizar perfiles`; compact viewport reserves nonzero account-rail width; signed-out/failed cloud request shown explicitly and authenticated refresh displays total available profiles. Named/unnamed workspace storage keys, original legacy lists, Supabase functions, Android native code and signing unchanged.
- **Validation:** all five exact-head GitHub checks passed: Desktop contract/owner isolation, real standalone HTML/Chromium compact+wide account geometry and About, Android embedded build, installed Android API35 UI, and 99 pgTAP owner/RLS tests. Real browser actively asserts complete 30-character handle, second choice visible, no squeeze/overlap, five buttons and login instruction.
- **Publication:** Public stable remains `v120.40`; merged fix is **not yet in a downloadable release**. `v120.41` Desktop+Android coordinated publication requires **explicit fresh user approval**. Real user desktop signed-in cloud result and Samsung⇄PC two-profile acceptance remain unverified pending user use of the next release. Do not claim installed PC is proven signed out based on screenshot alone.


## 2026-10-11 — Desktop switcher: incomplete account list and cropped @handle (candidate)

- User screenshot of v120.40 shows the dropdown limited to the locally cached `Datos anteriores` choice and text reduced to “Dat”; Android appears corrected.
- Diagnosed the HTML rail using a shared flex row for account `select` and 4 actions; cloud registry fetch depended on a valid Desktop sync session and failed without visible recovery guidance.
- Candidate corrective design: full multiline active identity label; 100%-width selector; separate explicitly labeled action grid; manual profile-registry refresh without full state sync; visible cloud count and login/network error status. This does not mutate any saved identities or lists.
- Regression: browser layouts at 390px/1360px check active long handle, second account, button geometry, and signed-out status; Node contract checks exact profile name and refresh path.
- This is **unreleased** source work for next v120.41; previous stable v120.40 remains published. Do not claim the user PC session has been diagnosed as signed out without verifying their local login.



## 2026-10-11 — Integrate Michel's Lab rendered UI evidence gate (candidate)

- The master cross-app QA identified P0 missing `tools/visual_release_gate.py` and CI invocation in IG Cleaner. Existing Android installed-emulator and Desktop Chromium Home/About screenshot suites were already present and must not be duplicated.
- Branch `fix/master-rendered-ui-gate-20261011` vendors the unchanged master validator and introduces a strict format adapter bound to existing real screenshots, two distinct viewports, source SHA and tested artifact digest. Reused screenshot/image/commit tampering fails closed. Original platform-specific evidence and checks remain authoritative.
- Desktop visual smoke now captures the actual packaged standalone HTML instead of unbundled source HTML; release QA rebuilds that distributable from the same commit and verifies its SHA-256. Android proof remains explicitly bound to installed emulator **debug** APK and does not certify the separately signed production APK or physical Samsung.
- Generic `release.yml` independently revalidates master screenshots before any publication; human review remains post-release and no version/release request was modified. Added adapter contract tests and workflow path triggers.
- **State:** implementation submitted for PR and exact-head CI validation; not yet merged or published. Physical phone review and any complete production-signed APK runtime equivalence remain separate work.

## 2026-10-11 — Coordinated IG Cleaner Pro v120.40 published and verified

- User explicitly authorized release of v120.40 for Desktop+Android after merged profile recovery/delete improvements. Release preparation [PR #63](https://github.com/michels-lab/IG-Cleaner-Pro/pull/63) merged to exact publication commit `7ec454cbc5852bb8e96b9bd7ff59830b5872bb5a`.
- **Five PR checks passed:** Desktop local contract and Chromium Home/About, Android Gradle build and installed emulator Home/About in compact and wide view, and 99 Supabase RLS tests. Production release workflow [run 38119945272](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38119945272) **SUCCESS** on exact commit `7ec454cbc5852bb8e96b9bd7ff59830b5872bb5a`; proof tied to exact-release commit was downloaded and verified by the release process.
- GitHub [v120.40](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.40) published as stable (`draft=false`, `prerelease=false`) 2026-10-11 07:06:17 UTC, assets confirmed: `IG-Cleaner-Pro-Android-v120.40.apk` (7,876,223 bytes; SHA-256 `1b107ba0ed05a8b83f54a96c03fcc069c2b243ee4f6a647b0ed7ea867b2744db`) and standalone `IG-Cleaner-Pro-Desktop-v120.40.html` (3,277,081 bytes; SHA-256 `da49a4df6b0e9585ab43cdfe6dbf093a22c4943380c4a82199c44242812004d4`), optional Desktop ZIP and SHA256SUMS.txt. Publisher checks production signer against original certificate and Android versionCode 12040; no beta package.
- Main published features: reliable original Dados anteriores selector; smart legacy assignment and non-destructive duplicate @username resolution; named profile editing, independent metrics and cloud JSON backup; named/unnamed profile confirmed deletion; account scoping and Supabase RLS.
- After publication, release request marked `published`/`authorized=false`, currentStableRelease `v120.40`, nextRelease `v120.41` (requires new permission). No additional publisher invoked.
- **Still requires physical Samsung user acceptance**: upgrade existing v120.39, preservation of genuine locally held Instagram ZIPs, two-account imports and Android↔Desktop auth/state roundtrip, release update and About screenshot. Emulator/CI cannot prove these. [#24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24). Issue [#57](https://github.com/michels-lab/IG-Cleaner-Pro/issues/57) is fixed in production build but user-specific live duplicate recovery acceptance remains unverified.


## 2026-10-11 — Smart Instagram recovery, rename, summaries, individual backup

- Added and merged [PR #61](https://github.com/michels-lab/IG-Cleaner-Pro/pull/61), head `ddbfeda1dfbebdbe6e81349a4b8208e058e3fff9`, main `01235bfbfe1ab2f7f5c582e08571d18c995ba256`.
- Desktop/Android: smart legacy choice instead of surprise new empty workspace, metadata-only conflict reassignment with explicit confirmation, immutable workspace keys, editable handle, accurate server-side per-Instagram list/review counts and last snapshot, owner-filtered JSON backup before optional destructive deletion, safe handling for unassigned accounts.
- PostgreSQL: additive production migration `instagram_profile_identity_recovery_and_summaries_v1`, two invoker-only RPCs, authenticated execute, anonymous denied. All **99** pgTAP assertions, Android build/emulator, Desktop contracts/Chromium passed. No live customer records altered; original cloud lists/reviews retained (33,927 entries/7,764 states).
- **State:** source integrated and tested, next release v120.40 awaiting explicit authorization. Published v120.39 unaffected. Keep issue #57 open until production Android/Desktop release; real Samsung/account ZIP roundtrip issue #24 remains pending.


## 2026-10-10 — Safe Instagram profile deletion verified and merged

PR #59 merged as `428c828a614db6a03901a8b4ba61a7ddf0bc1d8a` after all five exact-head checks passed (Android build, Android installed UI emulator, Desktop source and actual browser UI, Supabase 78 assertions). New production SQL function `igc_delete_instagram_profile` deployed with invoker permissions and owner RLS; anonymous execution denied. Production legacy data remained unchanged (33,927 saved list items; 7,764 review rows), and both user profile records were retained. **No release published**; current public version v120.39, next v120.40 pending explicit instruction. Separate duplicate-handle UX #57 remains open.


## 2026-10-10 — Instagram profile delete controls (candidate)

Desktop and Android gain a confirmed remove-profile action for named Instagram workspaces. The original Datos anteriores workspace stays protected. The new authenticated, owner-scoped database function removes a named profile and its own synchronized rows in one transaction; failures roll back. Client-side safeguards require typed confirmation and restrict local cleanup to the selected profile. Added migration and test coverage. No new release published. See docs/MULTI_INSTAGRAM_WORKSPACES.md and PR #59.


## 2026-10-10 — Android profile selector hides data recovery choice (fix candidate, not released)

- User reported **no “Datos anteriores” entry** in Android profile manager after creating a blank Instagram workspace; attempting to assign the old @handle fails with a database unique-value constraint.
- Root cause in `MainActivity.showInstagramProfileManager()`: the Material alert builder chained `setMessage(...)` with `setItems(labels,...)`, hiding the selectable items list. `legacy` was already explicitly prepended and is untouched.
- Surgical fix: give the picker a direct “Seleccionar Instagram” title and remove its incompatible `setMessage`; preserve `setItems`, the original `legacy` slot, new account slots, Add/Assign/Cancel buttons, and all persistent data.
- Add a regression contract to `tests/multi-instagram-contract.test.cjs` checking the legacy-first choice and absence of the incompatible message.
- Released stable **v120.39 is unchanged** until a separately authorized, synchronized Desktop/Android publication. Physical Android acceptance still required; issue #57 tracks the distinct preexisting duplicate-handle reassignment UX defect.


_Last updated: 2026-10-07_

This file is the **functional contract** for IG Cleaner Pro. UI redesigns, refactors, performance work, and future releases must preserve the capabilities listed here unless Michel Armando Duarte Flores explicitly requests their removal.

## Stable reference

- **Stable functional baseline:** v119 — HTML comparable-range · JSON intact.
- Experimental v120.x redesign previews are **not** allowed to redefine or silently remove v119 functionality.
- Before merging a redesign into `main`, compare the new build against this contract and the v119 baseline.

---

## Non-negotiable architecture

### Review = Following only

Review is exclusively for accounts **Michel follows**.

It must preserve:
- Following cleanup workflow.
- Foco 20 / 30 / 40.
- Recommended batches.
- Recheck / second-review workflow.
- Double Check workflow.
- Protected / reviewed / snoozed states.
- Current-session counters and active-batch tracking.
- Saved history/activity.
- Filters and direct views for accounts that do not follow back.

**Do not reintroduce a "Clean followers" mode inside Review.** Followers has its own dedicated workspace.

### Followers = people who follow the account

Followers must preserve its own dedicated workspace and must not be reduced to a passive table.

It must include:
- Its **own focus controls**.
- Its **own batch/session bar**, equivalent in usefulness to Review.
- Saved history/activity visible inside Followers.
- Search, filters, relation status, risk, review state, protection, and profile actions.
- A Mutuals subview for followers Michel also follows.

### Mutuals

Mutuals is a sub-workflow inside Followers.

It must preserve:
- Foco 20 / 30 / 40.
- Recommended batch.
- Risk batch.
- Review state and protection.
- Its own session/progress tracking.
- Relationship context and review history.

### Pending

Pending is exclusively for pending follow requests.

It must preserve:
- Pending-specific focus/recommended/risk workflows.
- Pending session tracking.
- Pending review/decision state.
- Cross-check logic against Following/Followers.
- No Review or Followers focus may appear here by accident.

---

## Review — mandatory second-review system

The following controls and their behavior are **mandatory** and must not disappear during UI redesign:

### Revisar de nuevo 30
- Reopens accounts that **currently do not follow back**, even if they were already reviewed.
- Must allow already-reviewed rows to be checked again.
- Must show a confirmation popup after opening.
- Must update the review state when confirmed.
- Uses its own cycle/history state so the workflow can rotate through candidates.

### Double Check 30
- Opens accounts that **currently do not follow back**.
- Rotates through different profiles instead of repeatedly serving the same first 30.
- Maintains a separate seen/cycle state.
- Must show a confirmation popup.
- When all current candidates have passed through the cycle, the user can reset/restart the cycle.

### Ver NO ME SIGUE revisados
- Must remain available.
- Shows accounts that currently do not follow back **including already-reviewed accounts**.
- This view exists specifically so previously reviewed relationships can be validated again.

### Cycle controls
Keep visible controls for:
- Reset Double Check cycle.
- Reset Recheck / Revisar de nuevo cycle.

Do not replace these with a generic focus button.

---

## Focus behavior — mandatory

All Focus-style flows must:
- Open Instagram profiles in tabs.
- Leave a confirmation/review UI open in IG Cleaner.
- Preserve active-batch state until the user resolves or cancels it.
- Avoid mixing candidates from another module.
- Never let a global focus control silently switch between Review, Followers, Mutuals, or Pending.

### Context under each username

Where Focus/Recheck/Double Check shows a username, show useful relationship context directly below it when data is available, for example:

- `Lo sigues desde 2022`
- `Te sigue desde 2021`
- `No te sigue`
- `Revisado hace 18 días`
- `Nunca revisado`
- `Te dejó de seguir`

This is context for the user, not a hidden scoring explanation.

---

## Batch/session tracking — mandatory

Review, Followers, Mutuals, and Pending must retain useful batch/session feedback where applicable, including:
- Batches today.
- Reviewed today.
- Reopened/rechecked.
- Active batch.
- Available/openable candidates.
- Last action.
- Ability to recover/reopen/cancel an active batch when supported.

A one-line "Last action" message **does not replace** the batch/session system.

---

## Saved history/activity — mandatory

The app must preserve the automatic review/activity history.

Followers must have a visible saved-history/activity area comparable to Review, scoped to the relevant Followers/Mutuals workflow.

Do not replace the history table/list with only a "last action" label.

History should preserve useful events such as:
- opened
- reopened
- reviewed
- unconfirmed
- snoozed
- last section
- last decision
- last opened
- last reviewed

Export of automatic history must remain available when supported by the stable baseline.

---

## Relationship evidence rules

- Do not treat missing accounts in a partial HTML export as confirmed non-followers.
- JSON behavior from the stable baseline must not be changed casually.
- Relationship conclusions must respect the comparable-range / evidence safeguards already implemented.
- UI redesigns must never weaken evidence correctness.

---

## UX rules

- Primary visual direction is **dark**, not light.
- Avoid generic admin-dashboard styling.
- Redesigns may change layout and visual hierarchy, but **must not remove functionality**.
- Do not duplicate the same workflow in multiple modules.
- Each module owns its actions:
  - Review → Following
  - Followers → Followers
  - Mutuals → mutual followers
  - Pending → pending requests
- Do not add context-dependent global buttons that can trigger the wrong module.
- Keep Focus and review actions obvious and local to their section.

---

## Regression checklist before merge

Before any future build is merged to `main`, verify at minimum:

- [ ] Review still contains Following Focus.
- [ ] Revisar de nuevo 30 is visible and functional.
- [ ] Double Check 30 is visible and functional.
- [ ] Ver NO ME SIGUE revisados is visible and functional.
- [ ] Double Check and Recheck cycle reset controls exist.
- [ ] Followers has its own Focus workflow.
- [ ] Followers has its batch/session bar.
- [ ] Followers has visible saved history/activity.
- [ ] Mutuals has its own Focus workflow.
- [ ] Pending has only Pending actions.
- [ ] No cross-module Focus button appears in the wrong section.
- [ ] Focus cards show relationship-age/review context when available.
- [ ] Active batch can be recovered/resolved.
- [ ] Protected/reviewed/snoozed states are preserved.
- [ ] Relationship evidence safeguards are preserved.
- [ ] JSON import logic remains intact unless intentionally changed and tested.
- [ ] About / Legal / Version remain available.
- [ ] No duplicate DOM IDs.
- [ ] All scripts pass syntax validation.
- [ ] Existing saved local state remains compatible or migration is provided.

---

## 2026-09-29 — redesign lesson

During the v120.x UI experiments, several regressions were found:
- Followers controls were replaced with generic Focus buttons.
- Followers lost its batch/session presentation.
- Followers lost visible saved history.
- The second-review / Recheck / Double Check controls disappeared from the redesigned Review UI.
- A global/contextual Focus control could show actions from the wrong module.

These are now explicitly documented as **regressions that must not recur**.

The redesign may continue, but functionality must be preserved first and reorganized second.


## 2026-09-29 — mandatory module sidebars

The right-side **live sidebar is part of the functional UX contract**, not an optional decoration.

- **Review** keeps its existing right-side live panel.
- **Followers** must have its own right-side live panel with Followers/Mutuals-specific data.
- **Pending** must have its own right-side live panel with Pending-specific data.
- These sidebars should contain the module's live/session information such as last action, opened/reviewed counts, pending/resolved state, active batch, reopen counts, module-specific status, saved history/activity, and relevant quick actions.
- When Followers switches between **All Followers** and **Mutuals**, the same Followers sidebar may update its scope, but it must remain visible.
- Do **not** replace these sidebars with session/history cards inserted into the central workspace.
- The central workspace is for the module's focus controls, filters, tables and primary content; live tracking belongs in the right sidebar.
- A redesign that removes either the Followers or Pending sidebar is a regression.


### Recent activity parity across module sidebars

Review, Followers/Mutuals, and Pending must each expose a full **Recent activity** block in their right-side live sidebar.

At minimum, each module must show its own scoped metrics for:
- reviewed in the last 1 h and 3 h;
- opened in the last 1 h and 3 h;
- Focus activity in the last 1 h and 3 h;
- action count in the last 1 h and 3 h;
- reviewed today and in the last 24 h;
- opened today and in the last 24 h;
- batches today and in the last 24 h;
- protected/paused today as appropriate to the module;
- reopened today.

These counters must be **module-scoped**. Followers/Mutuals must not show Review or Pending activity, and Pending must not show Review or Followers activity.

A reduced sidebar that only shows last action + a few totals is a regression.


### Standard activity hierarchy for all three work sidebars

The right-side live panels for **Review**, **Followers/Mutuals**, and **Pending** must use the same primary activity hierarchy.

Required order, from top to bottom:
1. **Last action** — show exactly what was done and when it happened.
2. **Opened this session**.
3. **Opened today**.
4. **Opened in the last 7 rolling days**.
5. **Opened in the last 1 hour**.
6. **Opened in the last 2 hours**.
7. **Opened in the last 3 hours**.
8. **Module-scoped action history**.
9. Secondary module-specific state and controls.

“Opened” means profiles actually opened through logged open/focus/reopen actions; the same definition must be used across all three modules.

Followers may switch scope to Mutuals, but the hierarchy stays identical and only the data scope changes.

Do not replace this structure with different metric sets for each module.

### JSON detection diagnostic rule

The file-detection preview must never label a valid JSON file as invalid because only a truncated header was parsed.

- Full JSON must be read before using JSON.parse for validity.
- Header-only sampling may be used for HTML detection.
- “JSON inválido” is reserved for a full JSON document that actually fails parsing.
- Diagnostic/preview messaging must agree with the importer whenever the importer successfully parses the file.


### Explicit relative time for last action

The top card of the Review, Followers/Mutuals, and Pending sidebars must state the last action in explicit human relative time.

Required pattern:
- `ÚLTIMA ACCIÓN · hace 3 horas`
- `ÚLTIMA ACCIÓN · hace 5 días`
- `ÚLTIMA ACCIÓN · hace 12 minutos`
- `ÚLTIMA ACCIÓN · hace un momento`

Directly below it, show what was done. The exact date/time may remain as secondary text.

Do not show only an absolute timestamp or force the user to calculate how long ago the action happened.


#### Relative-time precision

The last-action relative timestamp must be precise enough to identify when the event happened, while still showing the exact date/time underneath.

Examples:
- `hace 7 min`
- `hace 1 h 23 min`
- `hace 5 h 04 min`
- `hace 2 días 3 h`
- `hace 1 semana 2 días`
- `hace 2 meses 5 días`
- `hace 1 año 2 meses`

For events under 24 hours, preserve minutes rather than rounding down to only whole hours.


## 2026-09-29 — Mutuals and non-followed Followers are separate workspaces

The Followers data must be partitioned into two distinct workspaces in the UI:

### Mutuals
Contains only followers that the user also follows (`iFollow === true`).

It must have its own:
- page/navigation entry;
- Focus 20 / 30 / 40;
- recommended/risk batches;
- filters and table;
- standardized right sidebar;
- last action, opened-session/time-window metrics and action history.

### Followers que no sigo
Contains only followers that follow the user but the user does not follow (`iFollow === false`).

It must have its own:
- page/navigation entry;
- Focus 20 / 30 / 40;
- recommended/risk batches;
- filters and table;
- standardized right sidebar;
- last action, opened-session/time-window metrics and action history.

Do **not** put Mutuals and followers the user does not follow in the same page behind an internal `Todos / Mutuos / No los sigo` selector.

Historical data may come from the same Followers export, but presentation, focus candidates, action history and live session scope must stay separated.

### Layout rule
Mutuals, Followers que no sigo and Pending use exactly one flexible central content column plus one right live sidebar on desktop. Never reserve sidebar width twice through nested padding/fixed-panel rules; doing so crushes the central content and is a regression.


## 2026-09-30 — Complete Instagram ZIP is the primary import workflow

The **primary** way to load Instagram data into IG Cleaner Pro is the complete `.zip` export downloaded from Instagram.

Required behavior:
- The Import page must present **Import complete Instagram export (.zip)** as the recommended/default path.
- The user should not need to unzip the export manually.
- ZIP processing happens locally in the browser; the archive is not uploaded to a server.
- Search recursively through folders inside the archive.
- Automatically identify and group every supported export, including:
  - Following;
  - all `followers_*` files;
  - Pending follow requests;
  - Recent follow requests;
  - Recently unfollowed profiles;
  - Blocked profiles;
  - other export categories explicitly supported by the app in the future.
- Following/Followers/Pending found in the ZIP must be loaded into their normal app workflows automatically.
- Additional supported exports must be analyzed and surfaced automatically rather than requiring the user to select them again.
- The ZIP route must reuse the **same format detection/parsers** as manual import. Do not maintain a second independent interpretation of Instagram data.
- Files may be nested in arbitrary folders; do not depend on one fixed Instagram folder path.
- Multiple Followers files must be combined automatically.
- Manual upload of individual JSON/HTML files remains available as an **advanced/alternative import path**, not the primary UX.
- Invalid/encrypted/unsupported archives must produce an explicit error without destroying the currently stored review state.


### ZIP fixture must be derived from a real export structure

The repository fixture at `tests/fixtures/instagram-export-sample.zip` must remain sanitized but structurally faithful to a real Instagram export.

For the 2026-09-30 reference structure:
- preserve the 13 real archive paths and nested folders;
- preserve JSON root types and key shapes;
- preserve the three `followers_*.json` split;
- preserve the real Pending / Recent / Blocked `label_values` schema;
- preserve ZIP STORE (method 0) when that is what the real export uses;
- include neighboring exports such as `following_hashtags.json` so regression tests prove they are ignored rather than misclassified.

The importer must be tested against both the sanitized fixture and the locally supplied real reference ZIP before a ZIP-import change is considered validated.

A real regression found during this validation: `following_hashtags.json` was initially misclassified as Following because of the filename substring. The ZIP classifier must only treat the actual Following account export as Following.

Validated reference counts on 2026-09-30: **11,785 Following / 21,824 Followers / 418 Pending**.


### ZIP-to-Pending synchronization is mandatory

When `pending_follow_requests` is found inside the primary Instagram ZIP import:

- parsed rows must be assigned to `pendingRequestsRaw`, persisted, and rendered immediately in the Pending workspace;
- the Pending workspace must visibly state that its current source came from the ZIP and show the number of loaded requests;
- the manual Pending file input is an alternative/replacement path only; it must not keep presenting `Sin archivo` as if no Pending source exists after successful ZIP import;
- ZIP import must reset stale Pending search/risk/age/view filters to a visible all-data state so imported records cannot appear missing because of an old filter;
- after global rebuild/filter routines run, Pending must be rendered again so later refreshes cannot leave a stale empty table;
- if Pending data exists but the current filters produce zero rows, the empty-state message must say that no rows match the filters rather than asking the user to upload `pending_follow_requests.json`.

The real 2026-09-30 reference ZIP contains exactly one `connections/followers_and_following/pending_follow_requests.json` file with **418** entries using the `label_values` schema.


## 2026-09-30 — Experience layer: Import Report, Command Center and Focus Session

These features improve execution speed without replacing the v119 engine or the module-specific workflows.

### Import Intelligence Report
After a complete Instagram ZIP is processed, Import must expose an operational report based on the current export.

At minimum show:
- Following;
- Followers;
- Mutuals;
- current accounts that do not follow back, respecting existing evidence safeguards;
- Followers the user does not follow;
- Pending;
- current critical-priority count;
- compatible extra-export records/files when available.

The report must provide direct navigation/actions into Review, Mutuals, Followers, Pending and/or Command Center. It must use the already parsed in-memory data and must not require the internal ZIP files to be uploaded again.

### Command Center live work queue
Home / Command Center must expose work that is actually available now rather than only static navigation cards.

It must include live candidate availability for:
- Review Focus;
- Recheck / Double Check;
- Mutuals;
- Followers the user does not follow;
- Pending.

If an active Focus batch exists, continuing that batch takes precedence over suggesting a new one. Starting a Command Center action must call the existing module-specific workflow; it must not create a second focus engine.

### Focus Session
A Focus batch may use a dedicated one-profile-at-a-time working surface.

Required behavior:
- preserve the existing active batch as the source of truth;
- show `resolved / total` progress and remaining count;
- show username plus relationship/review context already known by the app;
- show saved profile-history context when available;
- allow opening the current profile and reopening unresolved profiles;
- support individual decisions without automatically applying one decision to the entire batch;
- Review / Mutuals / Followers support Reviewed, Protect, Keep/Conserve, Snooze and the existing secondary decision types where applicable;
- Pending supports Still pending, Accepted, Reviewed, Snooze and the existing secondary decision types where applicable;
- “Next without marking” must leave that profile unresolved;
- resolving one profile must prune only that profile from the active batch;
- finishing all profiles must leave the active batch empty and show a session summary;
- closing early must preserve unresolved active-batch state so the session can be recovered;
- the legacy/classic batch confirmation UI remains available as a fallback.

The Focus Session is a new working surface over the existing v119/v120 batch state, not a replacement for module state/history or evidence logic.

### Regression found during v120.19 validation
`autoCleanGarbageStates()` referenced the nonexistent `savePendingSnooze()` helper. The correct persisted-state helper is `savePendingSnoozeMap()`.

### v120.19 real-export validation
Validated locally against the supplied 2026-09-30 Instagram ZIP:
- 11,785 Following;
- 21,824 Followers;
- 418 Pending;
- 11,087 Mutuals;
- 698 current no-follow-back rows under the app's current evidence rules;
- 10,737 Followers the user does not follow;
- 27 critical-priority rows;
- Import Report visible after ZIP processing;
- Command Center work queue populated from live candidate functions;
- Pending remained 418 visible rows after ZIP import;
- Focus Session individual-resolution smoke tests passed for Review, Mutuals, Followers and Pending;
- no page errors or console warnings in the final browser smoke test;
- 0 duplicate DOM IDs;
- all 12 inline scripts pass JavaScript syntax validation.


## 2026-10-03 — v120.20 ZIP HTML/JSON parity

- Source baseline: v120.19 experience upgrade.
- Complete Instagram ZIP remains the primary import workflow.
- ZIP import now activates the HTML relationship-evidence safeguards from the files found inside the ZIP itself, instead of depending on the manual Followers file input.
- JSON import/parsing behavior is intentionally unchanged.
- Manual JSON/HTML uploads remain an advanced alternative path.
- Structural validation: all inline scripts pass syntax validation and no duplicate DOM IDs were found.

## 2026-10-05 — Infrastructure / cloud audit

Added `docs/INFRASTRUCTURE_AUDIT.md`.

The current local-only architecture is an intentional privacy property: Instagram exports stay in the browser and no backend is required. Supabase/Google cloud must therefore remain optional future architecture, not a default dependency. Near-term infrastructure gaps are CI, update/distribution design, centralized privacy documentation and browser-storage migration/versioning.

## 2026-10-05 — Michel's Lab parent/child governance contract

Added the repository-level Michel's Lab governance declaration:

- `.michelslab/project.yml` identifies `michels-lab/Michel-Software-Standards` as the shared standards authority.
- `MICHELS_LAB_PROJECT.md` documents the human-readable reporting contract.
- App-specific implementation evidence remains in this repository.
- Reusable/cross-app decisions are promoted to the master standards repository.
- The master repository polls child status centrally; this repository receives no credential that can write to the master.
- Secret values remain prohibited from both repositories.


## 2026-10-05 — Android Companion v120.28 native rebuild

- Replaced the ultra-minimal v120.27 Android prototype after the first distributed APK was only ~25 KB and failed to launch reliably on the target phone.
- v120.28 uses a conventional Android app structure with AppCompat, Material Components, RecyclerView, XML layouts, theme resources, launcher resources and bottom navigation.
- Android UX is intentionally different from Desktop: Focus 20/30/40 is shown as a one-profile-at-a-time checklist instead of opening many browser tabs.
- Opening a profile records an `opened` / `reopened` event; it does not by itself mark the profile reviewed.
- Completing the entire checklist requires explicit confirmation before the batch and profile states become reviewed.
- Review events preserve source device (`android` or `desktop`) and remain distinct from Audit events.
- Audit includes quick access to the latest reviewed/opened profiles by Android or Desktop and records subsequent audit activity separately.
- Supabase URL + publishable key remain app configuration; users only see email OTP login.
- Sync tokens are excluded from Android backup/device-transfer rules.
- Android applicationId for beta debug builds uses `.beta`, allowing the v120.28 beta to coexist with an older installed build during validation.
- GitHub Actions build run 37378481902 completed successfully after the resource-string correction.
- Generated APK size: 5,911,264 bytes; archive contains Material/AndroidX/runtime resources rather than the previous minimal shell.
- APK SHA-256 from the successful build artifact: `30f5a48715279f419ae2610986ef28dbc6ed49bcc6f91bee1abceb513ca4898c`.
- Remaining validation before calling Android production-ready: install/launch on the target phone, OTP login on-device, Focus Desktop → Android round-trip, Android batch completion → Desktop review projection, and Audit origin verification.


## 2026-10-05 — Android v120.29 full Workspace

- Added a fourth Android module: **Workspace**, loaded by default.
- Embedded the complete Desktop workspace HTML inside the APK so Android exposes Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault, Health and About rather than only Focus/Audit/Account.
- Kept Focus, Audit and Account as native Android surfaces optimized for mobile.
- Desktop-style multi-profile Focus actions inside Workspace are redirected to native Mobile Focus so Android continues opening one Instagram profile at a time.
- Added Android WebView file chooser support so ZIP/JSON/HTML imports can be selected from the phone.
- Added Android bridge hooks for Instagram links and portable HTML exports.
- Added session bootstrap so the embedded Workspace can share the authenticated Supabase session/device identity with the native shell.
- Corrected system-bar insets so the toolbar no longer renders under the Android status bar.
- Android version bumped to 120.29.
- GitHub Actions run 37387118838 completed successfully.
- Verified compiled APK: 6,880,075 bytes, 904 entries, embedded `assets/ig_cleaner_workspace.html` = 1,670,732 bytes.
- APK SHA-256 from validated artifact: `ae6a02abd26c3cc09f9b735b162f4008c6e6a56c385d8b7a092312e50f3de30a`.
- Remaining device validation: install/launch on target phone, mobile ZIP import, Workspace navigation, Desktop ↔ Android Focus round-trip and export flow.


## 2026-10-05 — LIMÓN handoff: Android full workspace v120.29

### Estado actual
- Desktop estable/sincronizable: v120.27 con Supabase + OTP, Audit cross-device y Focus congelado/sincronizable.
- Android v120.28 fue una reconstrucción nativa Material que ya abre y compila, pero el usuario la rechazó como producto final porque seguía siendo un companion reducido y no exponía la amplitud funcional de la app Desktop.
- La dirección corregida es **IG Cleaner completo en Android**, no un companion recortado.
- Rama activa: `android-full-workspace-v120.29`.
- v120.29 conserva Focus / Audit / Cuenta como superficies Android nativas y añade **Workspace** como acceso al motor completo de Desktop.
- El Workspace empaqueta el HTML oficial de Desktop desde `desktop/` mediante Android Gradle `sourceSets`, evitando mantener una segunda copia funcional del motor.
- Navegación móvil actual: Workspace / Focus / Audit / Cuenta.
- Workspace carga el motor Desktop dentro de WebView con JavaScript, DOM storage, file access y bridge Android.
- El selector `<input type="file">` del Desktop abre el file picker Android, permitiendo importar ZIP/JSON/HTML desde el teléfono.
- Los enlaces de Instagram se enrutan a la app de Instagram cuando está instalada.
- Aperturas masivas desde el Workspace se redirigen/bloquean en Android a favor del flujo Focus de un perfil por vez.
- El bridge Android ya contempla transferencia de sesión/configuración, exportaciones hacia Descargas e integración con Focus nativo.
- Se corrigió el solapamiento visual con status bar usando WindowInsets.
- Se consolidó una sola implementación de Workspace tras detectar duplicaciones de variables/imports/insets durante el desarrollo.

### Validación
- GitHub Actions run `37388962937`: `gradle :app:assembleDebug` **SUCCESS**.
- El APK generado incluye el HTML Desktop oficial empaquetado como asset.
- Artifact ZIP de Actions: ~6.8 MB; APK inspeccionado previamente: ~7.8 MB.
- El Desktop HTML empaquetado pesa ~1.67 MB.
- El build incluye Material Components, AndroidX, RecyclerView, XML layouts, launcher resources, Workspace WebView, Focus, Audit y Cuenta.

### Release / ramas
- `v120.27`: pre-release publicada; primera sync Desktop ↔ Android.
- `v120.28`: pre-release publicada; app Android nativa abre, pero funcionalmente quedó demasiado reducida respecto a Desktop.
- `v120.29`: **todavía NO publicada ni fusionada a main** al momento de este handoff.
- No llamar v120.29 “lista” hasta instalarla en el teléfono objetivo y comprobar el Workspace real.

### Pendientes inmediatos para el siguiente chat
1. Eliminar/ignorar cualquier asset duplicado/obsoleto de Workspace que no sea el HTML oficial empaquetado desde `desktop/`.
2. Actualizar About/strings Android de v120.28 → v120.29 donde aún quede identidad vieja.
3. Revisar el workflow Android para que no quede acoplado innecesariamente a una sola rama temporal.
4. Instalar el APK v120.29 en el teléfono objetivo y verificar:
   - arranque sin crash;
   - status bar/insets correctos;
   - Workspace visible y navegable;
   - módulos Desktop disponibles: Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault, Health, About;
   - selector de ZIP desde Android;
   - persistencia de datos del Workspace;
   - OTP/sesión Android;
   - Focus Desktop → Android;
   - finalización Android → revisión visible en Desktop;
   - Audit con origen Android/Desktop.
5. Solo después de esa validación: merge a `main` y release formal `v120.29`.

### Decisión de producto
Android debe ofrecer el mismo producto/datos que Desktop, pero no necesariamente la misma interacción. La diferencia intencional principal es Focus: Desktop puede abrir múltiples perfiles; Android usa checklist y apertura uno-a-uno. No volver a reducir Android a una app de solo Focus/Audit/Cuenta.


## 2026-10-05 — LIMÓN handoff — Android full workspace v120.29

### What changed in this work session
- v120.27 established the first Desktop ↔ Android sync architecture with Supabase, email OTP authentication, device-aware review/audit events and frozen Focus batches.
- v120.27 Android was rejected as a real product build after the distributed APK was only ~25 KB and failed to launch reliably on the target phone.
- v120.28 rebuilt Android as a conventional Material/AppCompat application. GitHub Actions compiled successfully and the app launched on-device, but user validation found that it exposed only the companion surfaces and did **not** provide the feature breadth of Desktop.
- v120.29 therefore changes the Android product model from “small companion” to **full Android workspace + native mobile tools**.

### v120.29 current architecture
- Branch: `android-full-workspace-v120.29`.
- Android version metadata: `versionCode 12029`, `versionName 120.29`.
- The official Desktop HTML under `desktop/` is packaged into the Android APK through the Android Gradle main asset source set.
- Android starts on a **Workspace** tab that loads the real Desktop app in a WebView instead of reproducing its modules separately.
- Desktop surfaces available through Workspace include the existing Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault/exports, Health, About and other current Desktop modules.
- The Android bottom navigation also keeps native **Focus**, **Audit** and **Cuenta** surfaces because those workflows benefit from mobile-specific interaction.
- Native Focus opens one Instagram profile at a time and uses a checklist; opening and reviewing remain distinct events.
- Native Audit preserves source-device provenance and does not rewrite the original review timestamp.
- Cuenta uses the same email OTP / Supabase session as Desktop; end users do not enter backend URLs or keys.
- Workspace bootstrapping transfers the Android session/device identity into the embedded Desktop engine.
- Android intercepts Instagram links and routes them to the Instagram app/browser.
- Desktop multi-profile opening is redirected/limited on Android so bulk browser-tab behavior does not become the mobile workflow.
- Android file chooser support allows the embedded Desktop importer to request files from the phone.
- Workspace export bridge can save generated HTML exports into Android Downloads.
- System-bar insets were corrected so app content no longer renders underneath the Android status/navigation bars.

### Backend/privacy boundary
- Supabase is now an implemented backend for **sync metadata/state**: devices, Focus batches/items, audit events and projected profile review state.
- Authentication is email OTP.
- Row Level Security is enabled by the app schema; clients use only the publishable key.
- Raw Instagram ZIP/JSON/HTML export contents remain local to the client workflow and are not intentionally uploaded as part of the sync contract.
- Review metadata may sync across Desktop and Android; raw export backup is a separate future decision and is not implied by current sync.

### Validation at chat close
- GitHub Actions run `37388962937` on `android-full-workspace-v120.29` completed **SUCCESS**.
- The final successful build occurred after consolidating duplicate Workspace implementations, restoring the loading indicator and fixing root window insets.
- The Android build artifact `ig-cleaner-companion-debug` was produced by that run.
- The full Workspace uses the official Desktop file `desktop/ig_cleaner_pro_v120_27_synced_companion.html` as the packaged engine.
- No v120.29 GitHub Release has been published yet.

### Known pending work / next-chat starting point
1. Remove the obsolete duplicate `android/app/src/main/assets/ig_cleaner_workspace.html` file if still present; Gradle now packages the official `desktop/` asset directly.
2. Update About/product text that still identifies Android as v120.28 where applicable.
3. Make the Android companion CI trigger reusable/generic instead of branch-specific to v120.29.
4. Update `README_SYNC.md` fully for the current OTP + full-workspace architecture.
5. Install the final v120.29 artifact on the target phone and validate:
   - cold launch;
   - Workspace renders Desktop modules;
   - status-bar inset;
   - Android ZIP/file chooser import;
   - OTP/session persistence;
   - Desktop → Android Focus round-trip;
   - Android completion → Desktop reviewed state;
   - Audit device provenance;
   - Workspace HTML export to Downloads.
6. Only after those checks, merge `android-full-workspace-v120.29` to `main` and publish GitHub pre-release `v120.29`.
7. Do not modify the stable Desktop import/JSON parsing semantics while finishing Android parity.

### Handoff rule
The next chat should continue from this section instead of reconstructing the Android work from screenshots or older v120.27/v120.28 assumptions.

## 2026-10-05 — Android v120.29 single Workspace asset hardening

- Resumed from handoff trigger **LIMÓN** on `android-full-workspace-v120.29`.
- Inspected validated CI artifact from run `37388962937` and found two embedded Workspace assets:
  - `assets/ig_cleaner_pro_v120_27_synced_companion.html`
  - `assets/ig_cleaner_workspace.html`
- Both files were byte-identical: 1,670,732 bytes each, SHA-256 `cc9d3cbe83a453d20e7bd525af2a22f80e8be826d61d468df053b68efb320862`.
- Root cause: Android's default asset source remained active while `../../desktop` was added with `assets.srcDir(...)`, so Gradle packaged both the Android copy and the Desktop copy.
- Changed the Android source set to `assets.setSrcDirs(listOf("../../desktop"))` so the packaged Workspace has one source of truth: the official Desktop HTML.
- Confirmed Android user-facing version/About strings already report **v120.29 Beta**; no remaining v120.28 product text was found in the active Android files checked.
- Confirmed Android CI branch matching is generalized to `android-*`.
- Hardened Android CI to inspect the built APK and fail unless:
  - the official Desktop Workspace asset is present;
  - its packaged size is greater than 1.5 MB;
  - the obsolete duplicate `assets/ig_cleaner_workspace.html` is absent.
- CI workflow now also triggers when its own workflow file changes.
- Desktop parsers, JSON import behavior, HTML evidence safeguards, Focus determinism and sync semantics were not modified by this cleanup.

### CI revalidation after single-asset cleanup

- Hardened Android CI run `37390702783` completed **SUCCESS** on commit `8cbd0f048453d87283e03ae7ae67ebb885314421`.
- Workflow artifact: `ig-cleaner-companion-debug` (artifact id `11380688614`).
- Extracted APK size: **6,880,202 bytes**.
- APK SHA-256: `bc706c76857a18a5fdfce3ffafa9a3edfe01188c952edc4c57667a86529397d9`.
- APK inspection confirms exactly one IG Cleaner Workspace asset:
  - `assets/ig_cleaner_pro_v120_27_synced_companion.html` — 1,670,732 bytes.
- Obsolete duplicate `assets/ig_cleaner_workspace.html` is no longer packaged.
- Current release gate: device validation remains required before merging to `main` and publishing v120.29 pre-release.

## 2026-10-06 — GitHub Copilot agent delegation

Added repository-level Copilot instructions and custom App Maintainer, QA Regression and Release Manager agents. The contracts preserve the canonical Desktop engine/workflows, Android parity requirements, local raw-export privacy boundary, Supabase workflow-metadata/RLS model, Focus/opened/reviewed semantics and device provenance.

Purpose: delegate bounded implementation, regression checks and release preparation to repository agents so cross-project ChatGPT work can focus on product decisions and coordination.

No product behavior, schema, version or release artifact changed in this infrastructure-only update.

## 2026-10-06 — ChatGPT-ready task intake

Added `.github/ISSUE_TEMPLATE/chatgpt-task.yml` so new implementation/audit tasks can capture the desired outcome, evidence, scope, acceptance criteria, required validation and release permission up front.

Purpose: reduce repeated context reconstruction in future ChatGPT sessions and make repository work resumable from a bounded GitHub Issue without changing product behavior.
\n

## 2026-10-06 — CI and distribution hardening

Added a unified repository CI gate for the real Desktop/local-Web and Android product paths.

Desktop CI now checks:
- full-document JSON parsing contract;
- local HTML/raw import pipeline;
- Review / Followers / Mutuals / Pending workflow presence;
- stable localStorage and IndexedDB identifiers;
- full-backup controls;
- duplicate static DOM IDs;
- inline JavaScript syntax;
- sanitized Instagram ZIP fixture structure.

Android CI builds the real debug app and verifies exactly one packaged Workspace asset.

Added `release/distribution-manifest.json` and `docs/UPDATE_AND_STATE_MIGRATION.md` to define the browser-state schema, migration rules, checksum requirements and safe Desktop/Android distribution policy.

Legacy version-specific release workflows no longer publish from a qualifying push to `main`. v120.29 additionally requires explicit manual `publish=true`. Release publication remains separate from CI/build success and real-device gates.

### Validation evidence

Pull-request CI run `37507759707` completed **SUCCESS** on branch HEAD `86e9e01038e779f9b3520efbb565924c5e75c854`.

Validated:
- Desktop local-app contract;
- full-document JSON parsing and local import surface;
- persistent localStorage / IndexedDB compatibility markers;
- required Review / Followers / Mutuals / Pending workflows;
- inline JavaScript syntax and static DOM ID uniqueness;
- repaired auditable sanitized Instagram export fixture;
- Android debug build;
- exactly one embedded Workspace asset.

No release publication was authorized or performed.

## 2026-10-06 — Official IG Cleaner Pro product identity adoption

Implemented the Michel's Lab canonical **Option 3 — stacked layers + sparkle** identity from `michels-lab/Michel-Software-Standards/shared-assets/product-logos/ig-cleaner-pro`.

Adopted surfaces:
- vendored canonical app-icon, mark and lockup SVGs under `branding/ig-cleaner-pro/`;
- Desktop/local-Web favicon/shortcut identity using the official app icon;
- Desktop startup splash using the official app icon;
- Desktop rail/in-app branding using the official transparent mark;
- Desktop About using the official lockup;
- Android adaptive launcher using the official mark over the canonical dark-blue background;
- Android startup/window splash;
- Android toolbar mark;
- Android Workspace loading surface;
- Android About dialog mark;
- Android product display name aligned to **IG Cleaner Pro**.

The Desktop artifact remains self-contained: runtime surfaces embed the canonical SVGs as local data URIs and do not hotlink the standards repository.

Added `tests/branding-contract.py` and wired it into unified CI to guard canonical asset presence, launcher/splash/About references and removal of the obsolete IG/check-style active branding.

**Validation status:** implementation complete; PR Desktop + Android CI must pass before Issue #6 is closed.

### Branding validation complete

Pull-request CI run `37512776514` completed **SUCCESS** on functional/test commit `da3021660ea83614c50f7adf7584b3f12b1fba48`.

Validated:
- Desktop local-app regression contract;
- official branding contract for vendored canonical SVGs and active Desktop/Android references;
- Desktop inline JavaScript syntax after splash integration;
- sanitized Instagram fixture contract;
- Android debug build with the official adaptive launcher/startup resources;
- exactly one embedded Workspace asset.

The only later branch change is this documentation entry. No sync/auth/review data model change and no release publication occurred.

## 2026-10-06 — Stable GitHub release v120.29 published

Published/refreshed **v120.29** as a normal GitHub Release (not a prerelease) after official branding adoption and hardened CI passed.

Release validation workflow: `37516998786` — **SUCCESS**.

Published assets:
- `IG-Cleaner-Pro-v120.29-Desktop.html` — self-contained Desktop/local-Web app;
- `IG-Cleaner-Pro-v120.29-Android-beta.apk` — Android beta companion;
- `IG-Cleaner-Pro-logo.svg` — official product icon source;
- `SHA256SUMS.txt` — integrity hashes for all distributed assets.

The release is stable for the Desktop/local-Web product. Android remains explicitly beta pending target-device and production-store validation. No claim of Google Play/production-device validation was made.

## 2026-10-06 — Intelligent Michel's Lab brand-adoption guidance

Repository instructions now explicitly route logo, launcher, splash/startup and About work through the Michel-Software-Standards Product Identity Standard and Brand Adoption Playbook.

The required interpretation is structural integration rather than sticker placement: replace active legacy identity, adapt canonical geometry to the existing product design language, preserve unrelated behavior, validate the build, and keep release publication separate unless explicitly authorized.



## 2026-10-06 — v120.34 canonical candidate consolidation

### Release/version reconciliation
- Consolidated active work onto `release/v120.34`; this branch is based on current `main` and is the authoritative v120.34 candidate.
- Next release target is exactly `v120.34`; GitHub prerelease must be false.
- No v120.34 release has been published from this work.
- Publication remains explicitly gated; validation workflows do not publish.

### Canonical identity / About
- Confirmed the master identity is stacked layers + upper-right sparkle; the old rounded-square IG monogram is legacy/rejected.
- Child SVG identity copies match the master canonical assets.
- Vendored the canonical Michel Duarte portrait byte-for-byte at `desktop/assets/michel_duarte_avatar.jpg` (git blob SHA `18fe1a68722850c3d8f918dc0799f46ffeb6dbaf`).
- Vendored the finalized Michel's Lab About lockup byte-for-byte at `desktop/assets/michels-lab/official-lockup.png` (git blob SHA `7fd48093968b31ddacd3098f5b15d962de580652`).
- Removed the embedded base64 portrait from Desktop About and linked the canonical assets instead.
- Unified visible Desktop release identity from stale UI 120.26/120.27 labels to UI v120.34.
- Desktop distribution is now a ZIP/bundle so the external canonical About assets are never omitted.

### Android repair and Focus autonomy
- Restored missing Android resource/dependency parity required by the current native shell.
- Android build again compiles with Home / Review / Focus / Activity / Profile resources.
- Restored native Android Focus creation for Review, Mutuals, Followers-you-don't-follow and Pending Requests.
- Android supports Focus 20 / 30 / 40, freezes the selected usernames in shared Supabase batch tables and refuses unsafe creation when historical review state has not synchronized.

### CI evidence
- Run `37561825709`: Desktop contract **SUCCESS** and Android build + embedded Workspace **SUCCESS**.
- Run `37559946743`: Android companion **SUCCESS**.
- Validation after the Android Focus-autonomy restoration is required before this candidate is handed off as final.
- Physical-device/round-trip testing is still a manual gate and is not claimed as completed.

### Release safety
- The historical v120.34 publisher from the divergent `release-v120.34` branch builds a debug/`.beta` APK while labeling the GitHub release stable; that workflow is not acceptable as the final stable publisher.
- A stable Android v120.34 publication requires a real release artifact with signing continuity; otherwise Android stable publication remains blocked.


## 2026-10-06 — v120.34 final candidate validation

- Reconciled the candidate onto `release/v120.34`; the divergent `release-v120.34` line is marked superseded and must not publish.
- Restored Android native Focus creation for Review, Mutuals, Followers-you-don't-follow and Pending in sizes 20/30/40.
- Restored the v120.30 Desktop sync bridge, including legacy-review normalization, list snapshots and complete workspace review-state publishing. This directly protects already-reviewed profiles from reappearing as unresolved merely because Android has only raw relationship lists.
- Preserved the Android system-bar inset hotfix so Samsung gesture/3-button navigation does not clip the bottom navigation.
- Replaced the embedded About portrait with the exact canonical Michel Duarte asset and added the finalized Michel's Lab production lockup.
- Added a centralized local-first privacy surface/documentation and explicit retention/deletion boundary.
- Added CI regression contracts for canonical branding/About assets, full sync bridge, privacy/data handling, Android Focus autonomy and navigation insets.
- Final consolidated CI run `37562844481`: **SUCCESS** across Desktop contract, sanitized fixture, branding, privacy, Android UX/Focus contract, distribution manifest, Android build and embedded Workspace verification.
- Android companion runs after the relevant functional changes also passed, including `37562748629`, `37562402633` and `37562024494`.
- Manual physical-device/Desktop round-trip remains pending and is not represented as completed.
- v120.34 has **not** been published by this work.
- Stable Android publication remains blocked until a real release artifact/signing path is established; do not relabel a debug `.beta` APK as stable.


## 2026-10-06 — Persistent Android production signing

Decision:
- Stable Android releases use one persistent signing identity for `com.michelslab.igcleaner`.
- Debug builds remain isolated as `com.michelslab.igcleaner.beta`.
- Normal IG Cleaner Pro GitHub releases must include the latest validated signed Android APK once signing requirements are configured.

Implementation:
- Added environment-backed production signing in `android/app/build.gradle.kts`.
- Release tasks fail before packaging if the four production signing inputs are missing.
- Added `release/android-signing.json` with the public certificate identity/fingerprint.
- Added `docs/ANDROID_SIGNING.md` with backup and GitHub Secrets procedure.
- Added `tests/android-signing-contract.py`.
- CI now smoke-tests `assembleRelease` using an ephemeral disposable CI keystore.
- The v120.34 release workflow now builds, verifies and attaches `IG-Cleaner-Pro-Android-v120.34.apk` after validating package ID, version and signer fingerprint.
- Added `*.jks` / `*.keystore` exclusions so private signing material cannot be accidentally committed through normal workflows.

Production signing identity:
- alias: `ig-cleaner-pro`
- certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
- valid until: 9999-12-31 (practical non-expiring maximum)

Secret boundary:
- No production keystore bytes or signing passwords are stored in Git.
- Required repository secret names are `IGC_ANDROID_KEYSTORE_B64`, `IGC_ANDROID_KEYSTORE_PASSWORD`, `IGC_ANDROID_KEY_ALIAS`, and `IGC_ANDROID_KEY_PASSWORD`.

Validation status:
- GitHub Actions run `37568540656` — **SUCCESS**.
- Desktop/state/branding/privacy/signing contracts — PASS.
- Android debug build + embedded Workspace verification — PASS.
- Signed `assembleRelease` smoke test with ephemeral CI keystore — PASS.
- Release APK package identity verified as `com.michelslab.igcleaner` / `12034` / `120.34` — PASS.
- Real-phone validation remains separate and must not be claimed from CI.


## 2026-10-07 — v120.34 signed Android release closeout

Release state:
- **v120.34** is published as a normal GitHub release (`prerelease=false`).
- Final publisher run `37574744462` completed **SUCCESS**.
- Stable Android artifact: `IG-Cleaner-Pro-Android-v120.34.apk`.
- Stable Desktop artifact: `IG-Cleaner-Pro-Desktop-v120.34.zip`.
- Checksums, privacy document and official product logo are attached to the same release.

Production signing:
- package: `com.michelslab.igcleaner`;
- versionCode/versionName: `12034 / 120.34`;
- alias: `ig-cleaner-pro`;
- certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`;
- certificate validity: `9999-12-31`;
- GitHub Actions signing secrets configured and successfully consumed;
- private signing material remains outside Git.

Release verification:
- production keystore restoration — PASS;
- signer identity verification — PASS;
- signed `assembleRelease` — PASS;
- stable package/version verification — PASS;
- exact signer fingerprint verification — PASS;
- release bundle verification — PASS;
- GitHub release publication — PASS;
- Android asset presence verification — PASS.

CI note:
- two earlier publisher attempts failed only because the verification script assumed an older `apksigner` output label/field layout.
- PR #16 and PR #18 corrected the verifier.
- the APK and FINAL-9999 signing identity themselves were valid; the final publisher passed end-to-end.

Governance:
- v120.34 is closed as the current stable baseline.
- next development/release target is **v120.35**.
- v120.34 authorization must not be reused for v120.35.
- physical-device validation remains separate from repository/CI evidence.


## 2026-10-07 — v120.35 infrastructure, RLS and synchronized-data privacy

Stable baseline:
- v120.34 remains the current published stable release.
- v120.35 is development only until explicit release authorization is given.
- FINAL-9999 Android signing identity is unchanged.

Generic release publisher:
- Added `.github/workflows/release.yml` as the canonical governed publisher for v120.35+.
- Version/tag come from `.michelslab/release-request.json`.
- Dynamic Desktop/Android artifact names come from manifest templates.
- The publisher validates explicit authorization, next-release target, Desktop/Android version parity, regression contracts, production signer fingerprint, stable package identity and normal/non-prerelease channel.
- Historical `.github/workflows/release-v12034.yml` remains manual/closed.

Supabase RLS:
- Added `supabase/tests/rls_isolation.sql` with 35 pgTAP assertions across all seven sync tables.
- Added `tests/rls-contract.py` and a dedicated CI job that starts local Supabase, applies `supabase/schema.sql`, runs the cross-user RLS suite and stops the stack.
- The live Supabase project was also checked transactionally with two temporary JWT subjects; user 2 saw only its own temporary device row. Transaction rolled back.
- Live policy inventory confirms CRUD policies are constrained by `auth.uid() = user_id`.
- Supabase security advisor returned no RLS exposure finding. A separate Auth warning remains for leaked-password protection being disabled.

Cloud data export/delete:
- Desktop Privacy now exposes **Exportar datos de nube** and **Borrar datos de nube**.
- Android Account now exposes **Export synchronized cloud data** and **Delete synchronized cloud data**.
- Export reads every RLS-visible row from devices, audit_events, focus_batches, focus_batch_items, profile_state, list_snapshots and workspace_state, with pagination, into `ig-cleaner-cloud-export-v1` JSON.
- Delete removes synchronized rows in FK-safe order under the authenticated user's RLS session.
- Cloud deletion does not delete the original Instagram ZIP/JSON/HTML export or independent Vault/file backups.
- Both clients sign out after cloud deletion so automatic sync cannot immediately re-upload remaining local state.

Version identity:
- Desktop visible UI: v120.35.
- Android versionCode/versionName: 12035 / 120.35.
- Android package stays `com.michelslab.igcleaner`; debug stays isolated with `.beta`.
- Desktop legacy filename/localStorage identifiers are preserved because they are compatibility identifiers, not visible release identity.

Validation status:
- Implementation complete on branch `development/v120.35-infra-privacy`.
- Full current-head PR CI is required before merge.
- Physical-device validation of Android privacy/download flows remains separate evidence.


### RLS performance hardening
- Applied Supabase migration `optimize_rls_policies_v12035` to all seven synchronized tables.
- Policies are now explicitly `TO authenticated` and compare ownership using `(select auth.uid()) = user_id`.
- Data semantics did not change; no application rows were deleted or rewritten.
- Supabase Performance Advisor: **28 Auth RLS Initialization Plan warnings → 0**.
- Live transactional smoke after migration: authenticated user 1 saw exactly 1 own temporary row and 0 foreign temporary rows; transaction rolled back.
- Remaining advisor items are unrelated to row isolation: leaked-password protection is disabled in Auth, and one unused-index notice is informational.


### v120.35 current-head validation state
- PR #20 head validation was requested repeatedly on GitHub Actions.
- GitHub Actions did **not** execute any workflow steps on the current head: Desktop, Android and Supabase jobs terminated before runner steps/logs existed. Re-running failed jobs produced the same zero-step result. This is an external runner/Actions blocker, not a passing or failing application test result.
- CI trigger policy was hardened to avoid duplicate `push` + `pull_request` runs on development branches and now uses concurrency cancellation for superseded PR runs.
- Current-head Desktop static validation via repository content: 16 inline scripts parsed successfully, 0 duplicate static DOM IDs, required v120.35/privacy/sync tokens present.
- Current-head Android structural validation: `MainActivity.java`, `SyncApi.java`, Gradle Kotlin and modified XML resources have balanced lexical/tag structure; this is **not** a substitute for `assembleDebug`.
- Live Supabase post-migration cross-user check: user 2 affected 0 user-1 rows across all seven synchronized tables for UPDATE attempts; temporary rows were transactionally rolled back.
- Supabase Performance Advisor after migration: 0 Auth RLS Initialization Plan warnings; one informational unused-index notice remains.
- Merge remains blocked until same-SHA executable CI/build evidence is available.


## 2026-10-07 — v120.35 direct validation while GitHub runners are unavailable

GitHub Actions:
- PR #20 head CI run `37696174790` failed before any runner step executed.
- retry attempt 2 reproduced the same pre-run failure for Desktop, Android and Supabase jobs;
- job payloads contain no steps and job log blobs do not exist;
- therefore this is treated as a runner/platform/account execution blocker, not as a failed product assertion;
- PR #20 remains Draft and must not merge until executable same-SHA CI passes.

Direct exact-branch validation:
- all 16 inline Desktop scripts parse successfully;
- 0 duplicate static DOM IDs;
- v120.35 identity, privacy, generic publisher and RLS contract sweep passes;
- targeted corrected sweep: 11/11 PASS;
- Android Java/Gradle delimiter structure passes;
- modified Android XML structure passes.

Live Supabase RLS behavioral evidence:
- rollback-only transaction seeded user 1 and user 2 data across all seven synchronized tables;
- authenticated user 2 saw exactly one own seeded row in every table;
- UPDATE attempts against user 1 affected 0 rows in all seven tables;
- DELETE attempts against user 1 affected 0 rows in all seven tables;
- authenticated own-row INSERT succeeded;
- transaction rolled back, leaving no test rows behind.

Advisor state after the optimized RLS migration:
- Security Advisor: no RLS exposure finding; one unrelated warning remains for leaked-password protection disabled;
- Performance Advisor: 0 Auth RLS Initialization Plan warnings; only the informational unused `audit_events_user_device_idx` notice remains.


## 2026-10-07 — v120.35 release-contract fix and CI minute protection

Release-contract regression found and fixed:
- the generic publisher itself was version-agnostic, but `tests/release-publisher-contract.py` and the CI manifest check still required the old closed v120.34 request state;
- an explicit v120.35 authorization would therefore have caused validation to fail at release time;
- contracts are now state-aware: they accept either the closed current-stable request or an explicitly authorized request that exactly matches `releasePolicy.nextRelease`;
- Android signing contract now derives the expected candidate version/code from `releasePolicy.nextRelease`;
- privacy contract derives the current stable Desktop artifact from the distribution manifest instead of hardcoding v120.34;
- simulated closed v120.34 request + authorized v120.35 request validation: PASS.

CI usage hardening:
- heavy Desktop / Android / Supabase jobs are skipped while a PR is Draft;
- `ready_for_review` explicitly triggers the full CI gate;
- this prevents long-lived Draft PR edits from repeatedly consuming GitHub-hosted runner minutes.

Final runner probe:
- PR #20 was marked Ready for review on head `e5a49aa55053599636a7c55d91df7b39df7207b9`;
- run `37702842845` created Desktop, Android and Supabase jobs;
- all three terminated before any step started and expose `steps: []`;
- PR #20 was returned to Draft;
- merge remains blocked pending a real same-SHA runner execution.

## 2026-10-07 — Master-first About governance synchronization

- Verified current master `michels-lab/Michel-Software-Standards` `standards/ABOUT_STANDARD.md`, `standards/PRODUCT_IDENTITY_STANDARD.md`, `AGENTS.md` and `brand/developer-profile.json` require exact `TOOLS WITH IDENTITY.` studio slogan and paired author/studio About composition (side by side where width permits; responsive stack on narrow screens).
- Updated local `AGENTS.md` plus app-maintainer, QA-regression and release-manager agent contracts to require fresh master reads before About work and rendered Desktop/Android verification.
- This change is **instructions only**: it does not alter UI assets, About implementation, app versions or published releases. Visible About layout/social icons/Android device acceptance remain unverified and open.

## 2026-10-07 — v120.35 CI and Desktop About closure work

- Verified public `michels-lab/IG-Cleaner-Pro` and restored real development-branch GitHub Actions execution after pre-run runner failures.
- Corrected stale v120.34 branding contract and privacy sign-out wording assertion; current Desktop and Android CI jobs subsequently executed successfully on run 37714614593, while Supabase failed during startup.
- Root cause of Supabase startup failure: the `20261007_optimize_rls_policies.sql` migration referenced public sync tables before a clean local stack created them. Added `supabase/migrations/20261006_initialize_sync_schema.sql` to initialize tables first; same-head successful Supabase CI remains pending.
- Updated Desktop About to display canonical `TOOLS WITH IDENTITY.` studio slogan, recognizable inline SVG icons for all five social controls, and master canonical URLs. Official portrait and Michel's Lab logo file bytes were not changed.
- Added Desktop About branding contract checks for official slogan, canonical social links/icons and hierarchy.
- Native Android `showAbout()` is still a plain message dialog. Full master-compliant native About, on-device visual acceptance, real ZIP import/Focus QA and authenticated Desktop↔Android round trip remain open. No release authorized or published.

## 2026-10-07 — Repository transferred to Michel's Lab organization

**Change:** repository ownership moved from `michels-lab/IG-Cleaner-Pro` to `michels-lab/IG-Cleaner-Pro`.

**Active references updated:** `.michelslab` governance, agent/Copilot authority and the distribution manifest now use the organization-owned repository and `michels-lab/Michel-Software-Standards`.

**Preserved intentionally:** Michel Duarte personal developer/social identity remains under `realmichelduarte`. No release is authorized by this migration change.

**Validation:** branch CI is required before merge.


## 2026-10-07 — Native Android About implemented and PR #20 merged

- Replaced Android's text-only About dialog with a native product-first panel, byte-identical canonical portrait and Michel's Lab studio lockup, visible `TOOLS WITH IDENTITY.` slogan, and Instagram/Facebook/LinkedIn/GitHub/Email icon-plus-name links.
- The new Android native panel stacks its paired author/studio columns on narrow screens, and reads the installed application version rather than hardcoding the release name.
- Desktop About now uses the canonical slogan and recognizable SVG social icons with standard canonical URLs.
- Release workflow retains separate explicit publication authorization; no v120.35 GitHub Release was published by this work.
- PR #20 merged after exact-head Desktop, Android and Supabase CI passed (run 37716560654); main merge commit `fd45720e09d6fe7cb399f0eafe0928d97d40f592`.
- Actual phone UX, live authenticated Desktop↔Android round trip, real ZIP imports, cloud export/download and cloud delete must still be validated on target devices; do not claim those device checks complete.


## 2026-10-08 — v120.35 production GitHub Release published

- Explicit user instruction **“dale release”** authorized v120.35 normal/stable GitHub publication on 2026-10-08.
- Generic publisher GitHub Actions run **37737077156** ended **SUCCESS** on release source commit `0e4b0c3d5b803436fd453c23e51dce1505871d8a`.
- Published normal release `v120.35` (`prerelease=false`) with signed production Android APK, Desktop ZIP, canonical logo SVG, privacy notice and `SHA256SUMS.txt`.
- Production Android certificate identity was verified by the publisher; package `com.michelslab.igcleaner`, version `120.35`, persistent FINAL-9999 signer.
- Release request authorization consumed (`authorized=false`, `status=published`), distribution manifest current stable changed to `v120.35`, next governed candidate advanced to `v120.36`.
- The generic publisher now safely skips already-published/unauthorized request changes to avoid accidental duplicate publication. CI contracts made version-aware instead of relying on former hardcoded v120.34.
- Pending real-phone acceptance is tracked in issue #24, including update-over-v120.34, ZIP import, Focus, sync and cloud controls. Not tested by GitHub CI, and no Google Play release claimed.

## 2026-10-08 — P0 Android About blank-region hotfix in progress (v120.36)

- User provided actual v120.35 Samsung screenshot showing product header and title but a large blank author/studio/social block. Root cause identified in `MainActivity.showAbout()`: at `screenWidthDp < 390`, `aboutPairRow` switches to VERTICAL while its children retained horizontal-only `layout_width=0dp` and `layout_weight=1`; their content was not visible.
- PR #29 repairs layout by assigning both identity panels `MATCH_PARENT` width and `WRAP_CONTENT` height, removing leftover weighted parameters and adding clear spacing. Names stable child IDs. Previous Android XML source-token tests passed despite failure.
- New real Android About UI instrumentation asserts nonzero measured dimensions/image drawables/reachable social button; emulator screenshots capture author/studio/socials at compact and wide resolutions, with screenshot/APK/source digest coverage validator.
- New release approval job depends on exact-source Android render screenshots and a GitHub `visual-release-approval` protected required-human-reviewer environment. A missing protection rule fails closed. Actual GitHub Environment configuration and reviewer approval are external and must be verified; do not claim it is configured.
- Cleared incorrect `AGENTS.md`-local app-maintainer reference to retired `IG` monogram. Selected logo is first proposal (profile cards / cyan orbit / gold sparkle), NOT the second circular filter proposal. Full-resolution original must be imported into master without changes before activating it. Existing app logo intentionally unchanged while source-import is pending.
- No new release was requested or published by this work. v120.35 remains stable; v120.36 is an unapproved candidate. Emulated UI and physical phone review remain distinct requirements, and Focus/ZIP/counters/sync device acceptance is still open in issue #24.

## 2026-10-08 — Release QA automation without manual review bottleneck

The user explicitly prefers to inspect apps **after release** rather than waiting for a manual pre-release reviewer. A dedicated PR replaces the `visual-release-approval` protected environment and required-human review step with an enforced automatic `rendered-ui-qa` dependency on the exact source-commit Android emulator screenshot workflow. Validated screenshots, build digest, source SHA and explicit authorization remain required; no human checkbox is needed to start release. Target-device tests and user visual opinion remain post-release separate evidence and never auto-PASS.

## 2026-10-08 — Compact About validated; v120.36 dev integrated (no release)

- After the first blank-region hotfix (PR #29), inspected real Android emulator screenshots and identified a secondary defect: **all five social links were below the fold on compact Android**, despite source/static CI and a scrolling UI test passing.
- PR #31 reworked Android About to a balanced side-by-side author/Michel's Lab composition with a compact two-column social button grid, preserving the **TOOLS WITH IDENTITY.** slogan. Strict test first failed with Email only **70% visible**; adjusted the layout without relaxing the test. Re-run 37808417135 passed at both compact and wide resolutions. Six source/APK-hash-bound screenshots were captured and opened for pixel-level inspection; all five links now appear on opening. PR #31 merged as `eb2ebca6768fa2dacc8441eaae3236f02030d96e`.
- User's explicit post-release review preference implemented in PR #32: mandatory **automatic exact-commit visual screenshot QA** remains in release dependency, no protected human-review environment. Merged as `5df21185eb89689635d26d7cc38262ef14dae0d4`.
- PR #33 raised Android package and Desktop dev identity to v120.36, retained immutable package `com.michelslab.igcleaner` / FINAL-9999 signing identity, and updated release notes/CI contracts. Desktop/Android/Supabase CI run 37810464858 passed; actual emulator UI run 37810464913 passed; merged as `b99b2357295d124fa783fa555f9793e87028899a`.
- Existing normal GitHub release remains **v120.35**. v120.36 source is ready in `main` but release not requested or authorized. The user-selected first logo remains an exact original binary upload/migration dependency (issue #30); actual Samsung update, Focus, ZIP and cloud tests issue #24; additional Home/Desktop screenshot automation issue #28. Never represent these as completed.

## 2026-10-08 — Instagram Cleaner Pro premium visual coherence pass (PR #37)

- User requested a global quality uplift: make native Android About match the rest of the app, improve overall visual polish with subtle gradients, and retain brand cohesion. This is a **UI-only change**, not a data/state/Focus or release rewrite.
- Work branched from `release/v12036-full-qa-logo` (PR #35) to preserve the user-approved Option 1 logo and pending binary/runtime-visual work. PR #37 targets that branch rather than silently overwriting the candidate.
- Introduced a cohesive semantic Android palette (deep navy, vivid but restrained cyan/blue, soft-gold accents, accessible pale text), four reusable gradient drawables (`bg_premium_panel`, `bg_premium_hero`, `bg_about_canvas`, `bg_about_social`), and updated canvas/header/nav indicator/badge gradients.
- Applied Android palette and gradient hierarchy across Main, Home dashboard, cards/profile rows, About, Activity and Profile. About retains the original portrait and official Michel's Lab lockup alongside the approved app icon; all five social links and their IDs/behavior remain intact. Layout dimensions and Focus/data flows intentionally left unchanged.
- Added late-scoped Desktop CSS `igc-v12036-premium-visual`: consistent navigation/surface hierarchy and softened compact About with product-first hero, paired author/studio identity, visible slogan and social link tiles. Preserves existing functional selectors, IDs and JS.
- Added `tests/premium-visual-contract.py` and wired it into CI. Corrected two inherited QA defects on parent PR #35 without weakening visual assertions: brittle expected Home screenshot test source token and a shell count that filtered About images while expecting eight Home+About screenshots.
- Acceptance remains contingent on actual installed-app screenshot workflows for both Android and Desktop on the final candidate commit. Do not claim visual/device acceptance or publication based only on source tests.
- No version bump, signing changes or new GitHub Release authorized by this PR.

## 2026-10-08 — v120.36 normal stable release published and verified

- User explicitly instructed finishing premium UI improvements, integrating and releasing Instagram Cleaner Pro v120.36. PR #37 (cohesive native Android + Desktop navy/cyan/gold visual system and compact About) was merged into release PR #35, then PR #35 was merged to `main`; approved first-option contact-card logo and exact 1254px PNG are included.
- Final authorized release source commit: `335cc84a3c5a823314f5283d3543a9fdf58174d3`. Automatic release run [37827876157](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37827876157) completed SUCCESS. The release-request gate and actual same-SHA Android/Chromium rendered UI screenshot gates completed SUCCESS. Desktop, Android and Supabase CI run on exact SHA completed SUCCESS.
- Production signing identity was verified (FINAL-9999 certificate) and signed APK and ZIP were generated, bundled and checked. Normal latest non-prerelease [v120.36](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.36) published at 2026-10-08T19:00:43Z. Published artifacts: `IG-Cleaner-Pro-Android-v120.36.apk`, `IG-Cleaner-Pro-Desktop-v120.36.zip`, `Instagram-Cleaner-Pro-v120.36-logo.png`, `Instagram-Cleaner-Pro-v120.36-PRIVACY.md`, `SHA256SUMS.txt`.
- Outcome: **BUILD PASS / EMBEDDED APP PASS / EMULATED ANDROID UI PASS / REAL CHROMIUM DESKTOP UI PASS / SIGNED APK PASS / RELEASE PASS**. Physical Samsung upgrade, production account cloud round-trip, real Instagram export Focus and user aesthetic approval remain separate post-release acceptance checks; these were not run or claimed as passed.
- This follow-up commit records v120.36 as currentStableRelease, resets the release request authorization, and sets nextRelease to v120.37. It MUST NOT publish or silently rebuild v120.36.

## 2026-10-08 — Corrected ZIP-only v120.36 Desktop release contract

- User reported that GitHub release **v120.36** offered Desktop only as a ZIP, whereas **direct `.html` download is the desired product standard**.
- Root cause: generic publisher created `package/IG-Cleaner-Pro.html` and zipped it, but did not create/upload a standalone HTML; manifest `channels.desktop` exposed only ZIP. The source HTML also referenced three relative image assets, so uploading the same bare HTML without images would have produced broken About branding.
- Fix: primary Desktop artifact `IG-Cleaner-Pro-Desktop-v{version}.html`, bundled self-contained from validated HTML + exact official icon/author/lockup bytes as data URIs; retain ZIP as optional, preserve signed Android APK. Add real offline Chromium smoke, source/manifest/publisher CI contract and SHA256 coverage. Update release notes and verify GitHub asset presence.
- Backfill v120.36 using a one-time GitHub workflow that extracts the *already released* validated Desktop ZIP, creates/offline-tests the standalone HTML, attaches only HTML + regenerated checksum manifest, and keeps existing signed APK/ZIP and their bytes unchanged. Do not claim backfill completed until workflow ends successfully and the live GitHub release has the downloadable HTML.
- Release protocol now requires direct HTML for this app and master standard for all local-browser Desktop apps. Historical v120.36 ZIP is intentionally retained for compatibility.

## 2026-10-08 — v120.36 post-release support and issue triage

- Confirmed normal GitHub v120.36 release has signed APK, standalone offline Desktop HTML, optional ZIP, official logo, privacy file and checksums. Direct HTML was backfilled after the earlier ZIP-only release; signing and Android APK were not rebuilt.
- Updated public README's erroneous v120.20 and backend-free claims to the v120.36 source-of-truth: local raw export processing, optional Supabase-derived-data sync, Android signing continuity, release assets and remaining physical-device boundary.
- Resolved historical P1 logo (#30) and cross-platform Home/About runtime visual QA (#28) using the evidence already merged into v120.36; did not claim completion of the physical Samsung acceptance issue (#24).
- Carried forward issue #24 to target v120.36 as **post-release device acceptance**, not a human pre-release blocker. Stable release remains v120.36; v120.37 is not authorized.

## 2026-10-08 — About layout rejection, persistent access and unused Advanced tools removal (unreleased)

- User provided actual About screenshot and rejected the three-card/small-portrait implementation. Explicit design: equal-parent app and Michel's Lab logos side by side at the top, developer identity below, then a large canonical portrait with five social links in one vertical list to the side (below only when necessary). About entry visible in the top bar throughout the app. This overrides the generic master paired *author/studio* layout for IG Cleaner Pro.
- Rebuilt Android `dialog_about.xml` as a single flow and removed the obsolete narrow 0dp column adjustments from `MainActivity`. Removed the nonfunctional `Advanced tools` Android top-menu entry and its generic-workspace event handler; retained real Sync navigation.
- Moved Desktop About from the scrollable left-rail footer to the persistent header (outside runtime-generated context actions). Consolidated About styling into one canonical style component rather than competing late overrides, and redesigned its brand/developer/portrait/social hierarchy.
- Added/updated source and actual runtime UI regression assertions for paired marks, large portrait, stacked social list and permanently reachable About. Changes are **development only**; exact-commit CI/Android emulator/Chromium visual acceptance pending. No GitHub release authorized and no Samsung validation claimed.

## 2026-10-08 — Native Android QA failure caught and stronger actual-view inspection

- First candidate PR #39 CI, Supabase RLS, Desktop Chromium Home/About screenshots: **SUCCESS**. Installed Android emulator run `37833416640` reported **FAIL** after APK and androidTest compiled: API 35 UIAutomator text lookup could not locate either `Michel Armando Duarte Flores` inside About or the pre-existing Home title `Instagram Cleaner Pro`, despite native activity measurements; the test stopped before visual screenshots. Do not claim Android visual acceptance from that run.
- Removed brittle cross-window `UiDevice.By.text` dependency. Native `AboutRenderTest` now inspects the **real displayed window's** `getGlobalVisibleRect` for Home toolbar title, on-screen labeled About action, app and studio logos, developer name, large portrait and all five social buttons. Checks horizontal logo/portrait/contact geometry, all required visible pixel dimensions and actual drawable presence; takes the original 8 screenshot images only after assertions pass.
- The active native About dialog is exposed to same-package instrumentation during its lifetime and cleared on dismiss; no change to the user's saved state, sync/Focus logic or signing. Must rerun exact-head emulator and review screenshots before merge. No new release authorization.

## 2026-10-08 — Native Android About fixed by replacing adaptive menu with permanent header controls

- Exact candidate commit `dc8d3ff2c4e191e7a96fa304406bdd5a0c91ca0b` passed full Desktop QA, Android production-signing build and Supabase RLS CI. Real API-35 Android instrumentation run `37849453228` compiled and **native About structure, logos, developer name, large portrait and social geometry PASSED**. Its separate Home check failed: a labeled About action was missing from visible toolbar, exposing the actual regression that source tests had missed. This was a **real product issue**, not a locator false positive.
- Root cause: MaterialToolbar's `showAsAction=always|withText` did not guarantee that the plain-text About menu item became a visible header control under width pressure.
- Removed obsolete `top_app_bar.xml` adaptive menu and replaced it with a single layout-owned header row: responsive brand title plus explicitly labeled fixed-width **About** and dedicated **Sync now** action, each with direct handler. `Advanced tools` remains fully absent. Mobile title may ellipsize on narrow viewports; global actions may not collapse to three-dot overflow.
- Tightened Android installed-APK test to assert actual non-clipped visible and clickable About + Sync controls, no toolbar menu, and unchanged About dialog content and geometry. Run exact-head Android emulator Home/About screenshots and full Desktop/Android/Supabase CI; only merge once all pass. v120.37 release is authorized by user's October 8 instruction, but publishing waits for these pending fixes and version parity.

## 2026-10-08 — v120.37 preparation after completed About/UI QA

- PR #39 merged on `ab02b0d2db9923ad8cb79bb88e1ce669f34c3050` after Android native emulator Home/About screenshot workflow, Desktop real Chromium screenshots, production-signing build, Desktop contract and Supabase RLS checks passed on exact candidate SHA. The native toolbar is no longer an adaptive overflow menu: About and Sync occupy dedicated visible controls; Advanced tools was removed fully.
- User explicitly instructed `dale release` and then `pero primero termina los pendientes`. Pending UI fixes were finished and CI passed before preparing **v120.37**. Increment both Desktop and Android version, signing/public metadata and release notes together while preserving package ID, FINAL-9999 signer and storage state. Keep the prior normal GitHub v120.36 published until the new publisher confirms real signed APK + offline HTML + ZIP + checksums; no success claim before then.

## 2026-10-08 — v120.37 published, signed, parity checked and authorization consumed

- Following user's explicit `dale release` and `pero primero termina los pendientes`, completed and merged functional/layout PR #39 and versioned PR #40 before sending final `.michelslab/release-request.json` authorization.
- Exact release source `15177fee95358a891619266dc90a523d13b8aaef`; `release.yml` run `37851259478` completed all three jobs **SUCCESS** (release request gate, same-commit Android and Desktop rendered UI proof, signed production publisher).
- The publisher verified unchanged FINAL-9999 certificate digest `99c1dd7b0ed32b758afad253a774d85dc7a4481990342b5d09b54b9dcca84f33`, Android v2/v3 signing, stable package/version, published normal GitHub release `v120.37` (not prerelease) at 2026-10-08T22:12:02Z.
- Live GitHub Release assets confirmed: `IG-Cleaner-Pro-Android-v120.37.apk`, `IG-Cleaner-Pro-Desktop-v120.37.html`, `IG-Cleaner-Pro-Desktop-v120.37.zip`, official logo PNG, privacy notice, `SHA256SUMS.txt`.
- Closed v120.37 release request (published / `authorized=false`), reconciled distribution manifest stable v120.37 and next v120.38, updated user-facing README/handoff. Preserve real-device Instagram ZIP, Focus and cloud roundtrip acceptance in issue #24 as post-release follow-up; not a manually blocking gate.

## 2026-10-09 — Android Focus information parity, Double Check and per-section last-batch history (candidate, unreleased)

- User requested Android Focus to **show the same informative fields as Desktop**, not to copy Desktop visual design: both follow dates ("Lo seguiste" and "Te siguió"), their order, confirmed/missing relationship evidence, last review and decision, per-profile opening/review history, context changes and unknown-date safeguards. Frozen Desktop batch context now supplements the newest list snapshots; null dates remain clearly `Sin fecha` and no follow-back claims are explicitly qualified as **snapshot observations**.
- Native Android now loads newest normalized snapshots + workspace review state during Focus and renders them via dedicated `FocusInsights`; it does not bypass the native checklist, change existing migration/storage or silently mark opened profiles reviewed.
- Added **Double Check 30 for Review / not following back** as native Android Focus: eligible currently followed profiles absent from synced followers, exclude protected/snoozed and accounts already in active batches; cycle avoids repeated usernames; completion offers explicit restart. The cycle lives in a separate Supabase `workspace_state` key `focus_double_check_cycle`, not in `primary`; Desktop's existing Double Check state reads/writes the same epoch+seen set. Android marks profiles reviewed only after explicit batch confirmation; multiple review decisions can be recorded.
- Added a native last-batch summary for Review, Mutuals, Followers, Pending and Double Check with date/count/status/device and completion time; old Desktop Double Check audit events are included even without a `focus_batches` row. Separate cycle progress gives visited/remaining totals.
- Added real Android emulator `FocusInsightsTest` tests for relationship date direction, historical fallback, unknown dates, reviews, request dates and last-batch details, alongside existing Home/About screenshot tests. Exact-commit CI, installed emulator test and cross-device user acceptance are **pending**. No v120.38 release is authorized by this request.

## 2026-10-09 — Android native Focus parity / Double Check PR #42 merged; exact-head QA PASS

- **Merged PR #42** https://github.com/michels-lab/IG-Cleaner-Pro/pull/42 via squash commit `9447ae29bb7fe758f7791c0a7be23ebd9fc28841`. Validated exact PR head `9b3fdbd6647d9635076e3610ccd75de63d84809f` before merge.
- **All required checks SUCCESS:** general CI run `38008299846` (Desktop contract, Android build/signing smoke, Supabase RLS); Desktop real Chromium Home/About visual run `38008299836`; installed Android emulator compact+wide Home/About and **5 instrumentation tests per viewport** run `38008299843` with binary-backed screenshot artifact `11652775546`.
- **41 database assertions** passed: original 35 account-isolation checks plus 6 new same-account Desktop/Android Double Check cycle read/update/primary-state protection/cross-user isolation checks. Uses existing `workspace_state` `state_key=focus_double_check_cycle`, no SQL schema migration, does NOT overwrite `primary`.
- Fixed real Android 1080px emulator screenshot race detected in earlier artifact: a Home frame was actually blank while About rendered. Emulator instrumentation now retries compositor captures until **real app pixels** are visible rather than weakening the strict binary-backed screenshot validator. Latest exact-head screenshot QA is PASS.
- Native Focus now shows exact+relative follows/follower dates, who followed first and difference, review dates/decisions, available profile history and provenance; unknown dates/partial followers HTML never become false proof of no follow-back. User can start Double Check 30 on Android, track eligible cycle allocation across Desktop/Android, confirm review separately from opening, and see latest Review/Mutuals/Followers/Pending/Double Check activity including earlier Desktop audit-only tandas. Native Focus sync button refreshes an open batch, not just an idle list.
- **Publication deliberately NOT performed.** v120.37 remains current stable, v120.38 requires separate explicit authorization; CI validation does not equal real-user acceptance. Physical Samsung upgrade, genuine IG export, live authenticated Desktop↔Android activity/review roundtrip remain pending acceptance (issue #24).

## 2026-10-09 — Explicit user-requested stable v120.38 publication preparation

- User explicitly instructed `dale release`. The current GitHub stable release is v120.37; `release/distribution-manifest.json` authoritatively declares `nextRelease=v120.38`. No v120.38 release previously exists at candidate creation.
- Cut one synchronized Desktop + Android candidate: Desktop HTML/title/About `UI v120.38`, Android production package versionName `120.38`, versionCode `12038`, and `release/android-signing.json` identity version while preserving certified original production alias/certificate and app ID. Exact-version tests updated.
- Release payload focuses on merged PR #42 Android Focus information parity, native Double Check 30, latest history for all modules, partial-HTML evidence safety and coordinated Desktop/Android state; PR #43 documented baseline.
- Governed release publisher remains `.github/workflows/release.yml`; publish only after candidate CI and exact-commit rendered screenshot checks, with explicit fresh one-time release authorization consumed afterward. No human pre-publication visual approval is required; user's visual review is after release.
- **Status at preparation:** candidate only, not yet published. Retain stable v120.37 manifest and download references until GitHub verifies a new stable release. Physical Samsung/real cloud acceptance remains open on issue #24.

## 2026-10-09 — v120.38 officially published, complete release reconciliation

- GitHub normal stable release https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.38 published at **2026-10-10T00:47:55Z** (`prerelease=false`, `draft=false`), exact publication SHA **`589d67230e62a7f1ad2cf21bc75a5348bcf4b93a`**. Publisher GitHub Actions run **`38010213161`** fully **SUCCESS** (authorization, exact-commit rendered Android/Desktop proof, signed APK and two Desktop packages/upload verification).
- Verified six release files uploaded: Android v120.38 APK **7,855,994 B**, primary Desktop standalone HTML **3,254,813 B**, Desktop ZIP **1,393,218 B**, product logo PNG, PRIVACY.md, SHA256SUMS.txt. Production Android package `com.michelslab.igcleaner`, versionCode **12038**, versionName **120.38**, unchanged persistent FINAL-9999 signing certificate.
- Prerequisite main-commit runs: Android installed emulator **`38010213267`** SUCCESS, Desktop Chromium **`38010213135`** SUCCESS, CI Android build + Desktop contracts + 41 Supabase cross-account assertions **`38010213180`** SUCCESS.
- After verified publication, mark release request **consumed** (`authorized=false`, `status=published`), manifest current stable **v120.38**, next governed **v120.39**; README/Handoff/AGENTS/migration docs updated. Do not trigger a second publication. Initial duplicate candidate PR #46 was closed unmerged because release candidate PR #45 and authorization had already landed on main.
- Genuine Android device installation, the user's private Instagram export and real authenticated desktop/mobile acceptance remain **post-release** issue #24; never claim they passed in CI.

## 2026-10-09 — Multi-Instagram per-login workspaces, PR #50 (in development)

- User requirement: one IG Cleaner Pro account controls multiple independent Instagram accounts. Existing Supabase tables were keyed only by `user_id`; an additional Instagram export would replace the previous account's following/followers/pending and merge decisions. Reviewed code/data keys and built **new additive registry+scoped tables** instead of unsafe in-place destructive key changes.
- Desktop: preserved legacy browser storage and IndexedDB, added profile picker and namespaced nonlegacy local data, scoped Supabase API writes/reads, registration/alias of legacy, account-wide privacy export/delete. Full local backup encodes its Instagram account and rejects mismatched restoration; named profile ZIP import requires confirmation.
- Android: same account_key, native Profile manager, per-login selected label and per-Instagram cache, per-IG Supabase REST mapping for lists/reviews/Focus/history/audit, explicit memory reset after selecting another Instagram. The selection is queued behind existing IO writes and stale list loads are discarded. Added runtime scope tests and updated instrumented test count to eight at both viewport sizes.
- Source docs: `docs/MULTI_INSTAGRAM_WORKSPACES.md` and `docs/INFRASTRUCTURE_AUDIT.md`. Cloud migration and 60 pgTAP assertions pending verified CI success; production database has **not** been changed. PR #50 not merged, no release. Stable v120.38 unchanged; v120.39 requires separate explicit authorization.

## 2026-10-10 — Multi-Instagram on Android + literal newline rendering regression

- User confirmed Instagram profile selection must work on Android too, and supplied a browser screenshot showing visible literal `\\n\\n` above Instagram Cleaner Pro's sidebar.
- Root cause verified in actual Desktop HTML source: a stray `\\n` text sequence directly after a CSS `</style>`, and another immediately before the next `<style>`. Chromium's HTML parser renders those as body text instead of whitespace. Removed **both source text nodes**, not covered by CSS or hidden overlays.
- Added Desktop source contract plus **running Chromium body-node/geometry assertion** to reject non-whitespace text before the app shell, at compact and wide viewports; retain About visual tests.
- Android Account/Profile contains native Instagram manager: create account, label immutable legacy dataset, select Instagram; added clickable, accessible **always-visible active profile in the top header** (separate from About) for quick switching from Home, Review, Focus and Activity.
- Fixed native emulator test data to use valid opaque Instagram account keys; the previous `Invalid Instagram profile scope` failure came from test values shorter than the minimum schema length, not production profiles (which use UUID keys).
- PR #50 remains **unmerged and unreleased**; stable v120.38 unchanged. Await green exact-head emulator and browser checks, required live Supabase additive migration rollout, and real two-Instagram/phone roundtrip acceptance. Never migrate/copy a legacy Instagram dataset into another profile automatically.

## 2026-10-10 — Multi-Instagram PR #50 merged; live additive migration verified

- PR #50 https://github.com/michels-lab/IG-Cleaner-Pro/pull/50 merged to main in commit `66f43cb38b3f0a046a819d196b6859dd04a521a1` after **three all-green exact-head checks**: IG Cleaner CI `38105541087`, Android installed-emulator UI `38105541099`, Desktop Chromium rendered UI `38105541095`.
- Supabase production project `ig-cleaner-sync` (`ilmztedebwdzgnlrvwxy`): applied additive migration `multi_instagram_workspace_isolation_v1` successfully. Verified **all 7 new tables have RLS** and **7 separate composite primary keys**; the 3 pre-existing legacy snapshot rows remained 3. The registry and new profile tables were empty immediately after deployment, as expected. No legacy row was deleted, copied or overwritten.
- CI's database suite has **60 pgTAP assertions** (the earlier in-progress status note of 59 was outdated); two profiles can have independent same-named list/review/batch identifiers, and another app login cannot access them. No live user Instagram exports were used for testing.
- Android Profile and always-visible header both switch Instagram without requiring another IG Cleaner login. Desktop escapes `\\n\\n` are removed at their two raw HTML source positions; actual Chromium screenshot workflow validates that no stray body text appears above the sidebar. Native emulated Home/About and scope tests passed after fixing test fixture keys.
- **No app release was published:** current stable `v120.38`, governed next `v120.39` (requires explicit authorization). Physical Samsung, real two-account Instagram ZIP imports and authenticated Desktop↔Android round-trip are still pending user acceptance.

## 2026-10-10 — Multi-Instagram completion: app-login-local isolation and real switch proof

- PR #53 https://github.com/michels-lab/IG-Cleaner-Pro/pull/53 merged into `main` via `83d8273568cc3625766145cfff86e0d171a7025f` after **all-green exact-PR-head** jobs on `9793e422a655a958e0f4096e4aa3ddd223551593`: Desktop Chromium `38108180542`, general CI `38108180395` (including Android build/signing smoke, isolated 60-assertion Supabase RLS, desktop contracts), installed Android emulator `38108180430`.
- First implementation PR #50 and deployed migration remain authoritative; this final follow-up prevents different **IG Cleaner app login emails on one computer** from seeing the same Instagram profile registry, selected profile or newer profiles' localStorage/IndexedDB. Owner-specific fingerprint scopes local new-profile data; legacy v120.38 local keys stay unchanged to preserve all existing reviews/snapshots. Native embedded WebView obtains the current owner email through AndroidBridge. After signing in with another email or verifying a different email, Desktop reloads into the newly selected owner scope **before** syncing.
- Added behavioral Node contract checking local-storage and new-profile IndexedDB keys, scoped Supabase REST payload and isolation of two app-logins; added real Chromium switch `legacy → Instagram A → B → A → legacy` with review persistence and no cross-account registry. Original Home/About/branding checks include a real DOM scan for stray text above app shell (including the user-reported literal backslash-n rendering). All verified green.
- Supabase live `ig-cleaner-sync` already contains 7 additive profile tables with RLS; no second migration was applied. Existing user-owned rows remain untouched; physical Samsung real user imports and authenticated Desktop↔Android two-profile sync still require acceptance.
- **Version state:** merged features not included in published v120.38 binaries. Next governed release v120.39 is not authorized. No release published by PR #53 or this documentation closeout.

## 2026-10-10 — v120.39 synchronized Desktop + Android release candidate

- User responded `pues hazlo` to the proposal to prepare v120.39 with the completed multi-Instagram implementation and proceed through the release checks; this candidate does **not** itself publish or alter v120.38's official stable manifest.
- Main baseline includes merged PR #50 (profile-aware Desktop/Android/Supabase) and #53 (per-app-login isolation), plus merged documentation closeout #54. Production additive RLS migration already deployed; legacy records untouched; latest baseline validation success included 60 pgTAP assertions, Android emulator and real Desktop Chromium.
- Candidate bumps Android `versionName=120.39` / `versionCode=12039`, production-signing metadata and all five Desktop title/UI/About references to `v120.39`; aligns exact-version source regressions and update notes. Stable Android package, FINAL-9999 signing SHA-256, canonical assets and source/workflows stay unchanged.
- No destructive migration, new secret, unsafe credentials or loss of local history. Desktop standalone HTML remains primary; signed APK and ZIP publish together on the governed stable release only after verified exact-SHA CI and UI proof.
- **Status on branch creation: candidate, not yet published.** Manual Samsung/real account ZIP and authenticated cross-device acceptance remain tracked in issue #24; automated screenshots are not equivalent to physical-user approval.

## 2026-10-10 — v120.39 stable release published and reconciled

- User requested proceeding with v120.39. Candidate PR #55 aligned all Desktop and native Android version IDs and tests, signing metadata and release notes; preserved the unchanged FINAL-9999 signer and all v120.38 legacy storage keys/tables. All five exact-candidate checks PASS; PR merged as `ffe09d14d887d501b73cd2f95bed3af7532acd84`.
- One-shot release authorization committed at `4170696589c22dc669deac10ca1a0ceddd88bfea`, consumed only after GitHub published normal stable `v120.39` on 2026-10-11T04:51:14Z. Governed publisher run `38112617481` SUCCESS, including exact-SHA installed-emulator and Chromium proof, production certificate verification, signed APK package/version integrity, standalone HTML and ZIP packaging and asset existence checks.
- Verified latest GitHub Release `draft=false`, `prerelease=false`, tag v120.39, exact release target `4170696589c22dc669deac10ca1a0ceddd88bfea`. Verified uploaded primary `IG-Cleaner-Pro-Desktop-v120.39.html` (3,267,531 bytes), optional ZIP (1,397,171 bytes), signed Android APK (7,863,819 bytes), logo, Privacy and SHA256SUMS.
- Release state reconciled: currentStableRelease `v120.39`, nextRelease `v120.40`, consumed request `authorized=false` / `status=published`; Desktop and Android share the same stable version. Public README/handoff/Supabase multi-Instagram guide and agent version authority updated without touching app behavior.
- Post-release QA still required on user's Samsung: update over original APK, authentic export ZIPs for two Instagram profiles and independent relationship/history decisions, cross-device Supabase syncing, About/native Focus and layout acceptance. This remains issue #24 and is **not** claimed as completed or made a pre-release human approval gate.

## 2026-10-12 — Shared agent contract synchronization

Synchronized only the managed blocks in AGENTS.md and .github/copilot-instructions.md to Michel-Software-Standards child-agent-core 2026-10-12.1. Local product instructions remain byte-for-byte unchanged outside those blocks. Carries current installer EULA/shortcut, standalone HTML (where applicable), and independent work during CI policies; does not modify app code, workflows, versions or releases. Validation: one managed block per target, exact canonical body and preserved local prefix/suffix. Product/runtime acceptance is not inferred from this documentation change.


## 2026-10-12 — Profile Counts visible controls + Automation planner + Mutuals Focus ratio (candidate)

- Owner reported that Windows robot's Instagram connect/login entry, batch size/window, per-profile delays, Pause/Resume, progress and error counts were not findable. Root cause in Desktop source: #igcCountsRobotActions and #igcCountsRobotPaceNote intentionally hidden, and automatic startup on page load; old /api/resume only signaled manual login, not paused work.
- Candidate adds explicit Conectar Instagram/Chrome, visible per-account pacing controls, Save, Pause, Resume and progress (analyzed, success, remaining, errors, unavailable, current username/wait, percentage). A saved pause is reentered only by explicit Resume; local controller requests enforce owner/account and preserve visits/results across sessions. No secrets or Meta API access.
- Separate **Automatizaciones** planning page gives per-list Skip this batch, persistent ★ protected favorites, search and accessible Protected view for cancel-sent-requests and unfollow-not-followback tasks; timing stored by owner/account/task. Browser actions explicitly **disabled** until DOM/owner acceptance; do not misrepresent the queue as an automated execution.
- Mutuals **remains Focus-only**; Following/Followers ratio from valid Profile Counts records ranks review batch candidates, with existing review/history exclusions and protected checks. Ratios are not used to unfollow, and missing numbers provide no ratio priority.
- Added/adjusted controller, UI, Chromium and planner behavioral tests plus `docs/AUTOMATIONS.md`. Await exact-head CI including Android emulator and Windows packaging; keep changes on PR branch until validation. Real Instagram login, action execution and physical Android acceptance not yet verified; no release authorized. Stable remains v120.42.

## 2026-10-12 — Automations Chrome action engine implemented on PR #82 (candidate)

- Follow-up requirement: `Automatizaciones` must **execute** Cancel Sent Requests and Unfollow Non-Followback, rather than show a read-only queue. Keep Mutuals Focus-only.
- Added `tools/profile_actions.py`: per-owner/Instagram/task SHA-256 segregated local journal, guarded visible Playwright browser actions from a user-signed-in Chrome window, verification of signed-in owner before any target visit, strict target URL/header and pre-/post-button verification. Requested→Cancel Request→Follow and Following→Unfollow→Follow in English/Spanish are best-effort DOM selectors; explicit visible "Follows you/Te sigue" blocks unfollow. Challenge, login, identity mismatch, incorrect control or unverified final action stops and records state. No Meta API, login password capture or CAPTCHA evasion.
- `tools/profile_counts_bridge.py` now exposes token-protected loopback `/api/actions/status`, `start`, `pause`, `continue`, `protect`, `skip`, binding action attempts to the IG Cleaner owner/account and expected IG handle; refuses concurrent Profile Counts and action-browser sessions. Rate-window and batch cooldowns remain disk-backed. Resuming skips successful results and ambiguous click results to avoid duplicate side effects; no silent retries.
- Desktop Automations UI now has an explicit **Ejecutar tanda seleccionada** approval dialog with username preview, live action metrics/status/progress, per-profile favorites/skip, pause/resume and timing. Unfollow requires nonempty full Following+Followers evidence and refuses detected partial HTML. The user is shown a message if the Windows loopback runner is not connected.
- Added Python mocked-DOM and owner-scope tests (`tests/test_profile_counts_actions.py`), Desktop bridge integration (`tests/automations-execution.test.cjs`) and CI path coverage; updated Windows preview package instructions and `docs/AUTOMATIONS.md`.
- Validation **not assumed**: review exact final PR #82 head actions and Windows portable preview (GitHub CI) prior to merge. A live owner-signed-in Instagram check, genuine UI selector/confirmation behavior and physical Windows testing are **not yet verified**. The stable public v120.42 is unchanged; no release authorized.

## 2026-10-12 — Corrección de flujo Unfollow público/privado

- Evidencia de usuario: las pantallas reales distinguen el menú de **Siguiendo → Dejar de seguir** del posible diálogo adicional de una cuenta privada. No asumir un único diálogo obligatorio para todas las cuentas.
- Implementación en `tools/profile_actions.py`: encontrar acción en menú visible (`menuitem` o botón), verificar cambio a Seguir inmediatamente después en público, y confirmar modal privado **solo si está visible**; ante ausencia de estado o múltiples botones homónimos marcar revisión sin repetir clic. Comprobación de protección/omisión antes de ambos clics. Mantener verificación de identidad y resultado final.
- Se añadieron fixtures/test de perfiles públicos y privados en español e inglés a `tests/test_profile_counts_actions.py`. Esperar CI de head exacto y aceptación del dueño en Chrome real; sin release.

## 2026-10-12 — Evidencia real de modal de solicitudes pendientes y prueba

- Capturas del propietario: una solicitud no aceptada se muestra como `Requested` en el perfil; al pulsar aparece advertencia de tener que volver a solicitar seguir a @handle si se cambia de opinión, con **Unfollow** rojo y **Cancel** neutro. Importante: Unfollow aquí cancela la *solicitud*, no el seguimiento aprobado.
- `tools/profile_actions.py`: la ruta cancel exige estado previo `Requested/Solicitado`; mantiene compatibilidad con acciones explícitas Cancel Request, pero para el texto Unfollow/Dejar de seguir solo actúa si el diálogo contiene referencia al **@handle exacto** y evidencia de volver a solicitar seguimiento. `Cancel` nunca es una acción de cancelar solicitud. Si el modal es incierto, no se pulsa.
- `tests/test_profile_actions_chromium.py`: añade casos de confirmación pendiente en inglés y español, perfil protegido, aviso impreciso, @handle que no coincide y estado final no confirmado. Validación de navegador real pero HTML local interceptado, sin usar credenciales ni cambiar Instagram. Esperar verde en Windows preview exact-head antes de integrar o publicar.

## 2026-10-12 — Dos videos de flujo real y corrección de estado final

- Se inspeccionaron los dos videos aportados: uno muestra cancelación de solicitud pendiente (`Requested` con diálogo `Unfollow`); el otro muestra menú de `Following → Unfollow` de una persona que sí sigue al propietario, de ahí resultado `Follow Back`. Conservar esa semántica; `Follow Back` no implica que se la siga de vuelta.
- El CI de Windows del commit anterior falló **1 de 15** casos Chromium: el texto español terminaba `@target.user.`, y el matcher interpretaba la puntuación final como extensión del nombre. `tools/profile_actions.py` corrigió el control de límite de username y diferenciación de `Follow` vs `Follow Back` en mensajes de auditoría.
- `tests/test_profile_actions_chromium.py` extendido con pruebas de `Follow Back` EN/ES y de @handle extendido malicioso o incorrecto. Mantener prohibición de unfollow automático a mutuals verificados o protegidos. Pendiente validación exact-head, paquete Windows y aceptación real; no marcar producción como probada.

## 2026-10-12 — Pending desactualizado, mutuals detectados y resumen de excepciones

- Requisito nuevo: tras las acciones del robot, mostrar **lista interactiva** de perfiles anómalos, especialmente si la tanda era `No me siguen` pero el resultado fue `Follow Back`, si faltan datos al abrir el perfil, o si un perfil listado en `Pending` ya muestra `Following/Siguiendo`.
- Motor `tools/profile_actions.py`: prevalidación `Requested` protege contra unfollow accidental cuando la solicitud ya se aceptó. `Pending` → `Following` devuelve revisión sin clic y etiqueta `pending_already_following`; se etiquetan también `unexpected_followback`, `pending_not_requested`, `missing_profile_info`, `mutual_before_action` y resultados ambiguos/bloqueados. Diario JSON del robot ahora guarda `issue` por perfil y API snapshot `issues`, `issue_count`, `processed`, `pending`; los hallazgos previos al clic pueden acumularse en la tanda sin bloquear otras visitas.
- Interfaz `desktop/ig_cleaner_pro_v120_27_synced_companion.html`: panel resumen siempre accesible dentro de Automatizaciones con selector de tarea, filtro, búsqueda, `Abrir perfil`, `Proteger` y `Ya revisé`, guardado de revisión/local cache por cuenta y tarea; nunca deduce que una acción debe repetirse solo porque se marca pendiente.
- `tests/test_profile_counts_actions.py`, `tests/test_profile_actions_chromium.py`, `tests/automations-issues.test.cjs`: casos de protección sin click, estado stale Pending, ausencia de datos, persistencia de incidencias y aislamiento entre cuentas; CI debe pasar en commit exacto. **Sin validación real contra sesión Instagram** y sin release hasta validaciones.

## 2026-10-12 — Integración real Windows: una sola aplicación, sin CMD

- Decisión confirmada por el propietario: el robot de Instagram debe iniciarse **dentro de Insta Cleaner**, sin un lanzador .cmd ni procesos auxiliares que él deba gestionar.
- Causa anterior: el producto usaba un HTML suelto más `IGCleanerProfileCounts.exe` lanzado mediante `Start-Insta-Cleaner-Robot.cmd`; la acción Chrome/Instagram estaba conectada por puerto y token locales, pero no era una aplicación integrada.
- Implementación PR #82: nuevo `tools/ig_cleaner_desktop.py` abre ventana propia de Insta Cleaner en Chrome `--app` con perfil persistente, alberga el servidor tokenizado de forma interna en el mismo EXE y apaga/pausa los jobs al cerrar. `tools/profile_counts_bridge.py` expone referencias locales al controlador para cierre seguro; ningún servicio se publica a Internet. No se automatiza Instagram al abrir la app, solo cuando el usuario autoriza la acción.
- El compilador `.github/workflows/profile-counts-windows-preview.yml` genera `InstaCleanerPro.exe` con `--onefile --windowed`, icono canónico y HTML embedded; ZIP sin .cmd ni HTML independiente. `tests/test_native_desktop.py` comprueba persistencia, rutas, servidor único, shutdown y que un solo EXE lance app mode. README de paquete documenta la ruta estable, migración mediante respaldo y uso.
- Límite: el nuevo perfil de la ventana de aplicación tiene almacenamiento de navegador propio; la importación desde HTML anterior es una migración explícita y no puede afirmarse automática. Chrome/robot siguen requiriendo sesión real; no hay aceptación en la PC del propietario ni release estable. CI Windows exact-head y revisión de regresiones pendientes antes de merge.

## 2026-10-12 — Switch Accounts was Sign Out; fixed account chooser (Android + Desktop)

- User-reported regression: **Switch account** did nothing different from Sign out; both discarded the active session, with no list of previously authenticated users. Exact root cause: Android `MainActivity` called `api.logout()` inside Switch; Desktop `igcSyncSwitchAccount` set `S.session=null` and reloaded.
- Android: added `AccountSessionVault.java` using Android Keystore AES-GCM for **one encrypted access/refresh session per IG Cleaner login**. Existing active login migrates on startup, and tokens rotate in the corresponding slot. Switch chooser lists remembered emails + **Add another account**. Selecting an email restores and verifies that account/session, clears in-memory caches and rebuilds the native UI. **Sign out** forgets only the active saved session. Stale WebView messages from another owner are rejected. Per-user Instagram workspaces and local histories remain untouched.
- Desktop/Windows: `Cambiar cuenta` opens an actual chooser with stored users and **Añadir otra cuenta**, restoring the selected session and reloading the owner-dependent namespace. Refresh updates the relevant saved session. Sign out forgets only the current user; other sessions remain available. No Instagram password is stored. Browser-stored session tokens still have the same inherent risk as the existing single-session storage; never treat a shared Windows profile as a secure multi-user device.
- New tests: `tests/auth-account-switch.test.cjs` (two logins, dialog, reload and owner isolation) and Android `RememberedAccountSwitchTest.java` (AndroidKeyStore encrypted storage, switch/sign-out, mismatched identity). Instrumentation count updated from 8 to 10. Existing CI and Windows integrated preview must complete for this exact commit before merge/release; no stable release approved.

## 2026-10-12 — Real Chromium login-switch acceptance and action-job owner guard

- **Verified:** CI `38241950533` ran `tests/auth-account-switch-browser.test.cjs` against the exact single-file Desktop artifact opened through `file://` in real Chromium; switched from the first fixture app login to a second remembered login, verified the new session, preserved the prior login and review history. No real Instagram or Supabase requests.
- **Safety fix:** an action robot started under IG Cleaner owner/Instagram account must not continue while the user switches the app login or active Instagram profile. New `window.igcAutoSwitchGuard` fails closed when the local robot's state is unknown or its worker is active/starting/pausing. Desktop `IGC_INSTAGRAM_PROFILES.switch`, `igcSyncSwitchAccount`, `activateRemembered`, Add Account and Sign Out refuse identity changes until the backend confirms the action job is paused/stopped. Action pause remains available in Automatizaciones.
- **Regression:** `tests/automations-execution.test.cjs` now checks unknown/running robot blocks identity changes and confirmed paused worker allows them. This avoids changing the UI owner while an already approved batch is still making Instagram changes; without the guard the old worker could continue after interface reload.
- **Packaging/UI:** removed obsolete instruction requiring a separate `.cmd`; the integrated Windows application is `InstaCleanerPro.exe`. No stable release, real-owner account authentication test or actual Instagram action confirmation implied by the offline assertions.


### 2026-10-12 — Integración de PR #80 en candidato PR #82
- **Hallazgo:** una lectura Following incompleta podía sustituir la lista guardada y excluir perfiles previamente descubiertos.
- **Cambio:** reconciliar checkpoints de la misma cuenta, exigir un contador visible exacto para marcar una lectura completa y procesar la cola reconciliada; incluir pruebas de parser y reanudación.
- **Seguridad:** la lectura parcial nunca acredita ausencia de followback ni autoriza automatizar unfollow. Sin publicación ni cambio de versión.
- **Estado:** pendiente CI exact-head y aceptación del navegador de Instagram con sesión real del propietario.


### 2026-10-12 — Instrucciones de lanzamiento de Windows alineadas
- Hallazgo: la interfaz seguía pidiendo el launcher CMD y el README nombraba otro ejecutable para healthcheck.
- Corrección: mensajes de UI y documentación ahora usan únicamente InstaCleanerPro.exe, más test de regresión sobre los artefactos fuente.
- Validación pendiente: CI exact-head y aceptación en equipo Windows con Chrome y sesión real; ningún release público automático.


### 2026-10-12 — Preparing governed v120.43 release (owner explicitly requested)
- Prepared integrated Windows publishing pipeline (single `InstaCleanerPro.exe` without legacy CMD, verified ZIP contents and Chromium/Windows tests), signed Android versionCode 12043, matching HTML UI v120.43 and release notes.
- Pending: exact-head CI on new version, PR merge, separate governed release request on main, exact-publish-commit visual checks and signing, GitHub assets/checksums verification.
- Disclose unverified owner Instagram UI, real action acceptance, and Windows↔Android Profile Counts sync limitations; no automated action performed on the owner's account.


### 2026-10-12 — Official normal v120.43 published
- Owner expressly authorized release. Squash-merged PR #82 then published commit `469189095fa1e2f2308689c59d6e60eddec36868` through governed [run #38270817146](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38270817146), all jobs SUCCESS.
- Seven release assets verified: integrated Windows robot ZIP, production-signed Android APK, standalone Desktop HTML, optional Desktop ZIP, logo, privacy and SHA256SUMS. Exact-commit Android/Desktop visual evidence and frozen Windows EXE QA succeeded.
- Release accepted as GitHub distribution for owner-supervised testing; **not** validated with real Instagram UI/actions or physical Windows/Samsung session. No Google Play publication.
- Request consumed; next release target v120.44, pending new authorization.


## 2026-10-12 — Owner-reported stuck Instagram login + optional independent followback audit (PR #85)

- **User evidence:** integrated Windows v120.43 stayed at `Status: login` and zero processed profiles while the user had Instagram open. Source defect: a narrow sidebar Profile-anchor assumption plus polling only the first browser tab and an unbounded login loop; it never gave actionable timeout diagnostics. Live underlying DOM cause cannot be confirmed without the owner browser.
- **Fix candidate:** detect uniquely labeled sidebar profile links and visible profile avatars, inspect all nonclosed Chrome tabs for a unique signed-in handle; never infer identity from arbitrary target URL or cross account scopes. After 40 seconds with no proof, raise a visible `needs_attention` warning but KEEP Chrome open and automatically continue identity detection after the owner signs in or reloads, without closing Chrome mid-login. Keep challenge/mismatch as hard stops.
- **Unfollow queue:** use current `isDoneValidForMode(row,'following')` and the same non-followback membership as Focus; reviewed-current accounts are excluded by default, stale reviews become eligible again, protected/skipped remain excluded.
- **Optional Followback Audit:** completely separate explicit `audit` job, NEVER a prerequisite for existing Unfollow. Suspected non-followbacks are derived from following minus imported followers and are read-only checked using visible search in the *owner's own Followers list*. Return `follows_you`, `not_following` only if the search explicitly and stably displays no results, or `unverified`; do not treat missing labels or incomplete HTML as negative proof. The job never presses Follow/Unfollow/Cancel Request and saves account-scoped results and pacing.
- **Localization:** action workspace/menu, queue, issues, and the Profile Counts screen/robot progress were translated to English. Older modules have legacy Spanish UI copy remaining, so a separate whole-app language audit is still required before claiming English-only completeness.
- **Tests:** Profile Counts Python + Node, mocked real Chromium read-only audit no relationship clicks, Desktop screenshot, Windows integrated EXE and Android emulator. Initial failures were corrected (fake Playwright Page.is_closed, test English labels, Python Page.add_init_script signature, and counts UI accidental quote removal). Exact-head CI, real Instagram session acceptance and new preview EXE validation still required; **no stable release or automatic account operation performed**.


## 2026-10-12 — PR #85 merged (read-only optional audit / stuck login fixes)
- PR #85 merged to main at `a4f75ea4749399b5eac32004da3238fb32b2eeaf` after the **same exact head `8c87da65074173cdee043c52261b3fa1cb932b85`** passed all five GitHub Actions families: general CI, Profile Counts, real Chromium Desktop rendering, integrated Windows EXE/offline action tests, Android emulator screenshot/visual gate.
- Unfollow queues now exclude reviews still valid under the existing Following review metadata; the separate Followback Audit is **optional**, read-only and never a prerequisite for Unfollow. It checks candidates from imported Following minus Followers against the owner-visible Followers search, classifying explicit matches, stable explicit no-match, or inconclusive evidence without modifying relationships.
- Account recognition improved for labeled navigation avatars and own-profile Edit Profile fallback; login warning no longer silently stalls forever and automatic recognition can recover when the user opens the correct Chrome profile. Multiple/conflicting identities remain fail-closed.
- The affected Automations and Profile Counts UI was converted to English; other historical screens still contain Spanish copy, which requires follow-on English-only audit. The real owner's Instagram DOM and physical Windows/Android acceptance remain **not validated**.
- **Release**: last published stable remains `v120.43`; Windows test preview from run #38292268299 is available but not a release. No new version, APK or destructive Instagram changes published by this merge. Future v120.44 requires version bump, exact-commit QA and explicit authorization.


## 2026-10-14 — Verified v120.44 publication, release authorization consumed

- GitHub release https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.44 is a normal stable publication (not prerelease/draft), 2026-10-14 07:10:05 UTC, exact source `90337e23b8bb91b3b2720f73a958c85cea152f77`. Governed Actions workflow https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/38525933376 finished **SUCCESS**.
- Seven expected files verified: `IG-Cleaner-Pro-Android-v120.44.apk` (7,900,232 bytes), `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.44.zip` (48,711,196 bytes), `IG-Cleaner-Pro-Desktop-v120.44.html` (3,347,216 bytes), optional desktop ZIP (1,419,292 bytes), logo, privacy and SHA256SUMS. Production APK signing identity, exact commit Android/Chromium visual evidence and Windows executable passed the governed gates.
- Separate validated PR #89 fixed release candidate vs published stable artifact assertions. No user data, authentication secrets, Supabase production tables or Instagram follow relationships were changed.
- After confirmed publication, consumed release-request authorization and recorded published run/commit, promoted `currentStableRelease=v120.44`, reserved `nextRelease=v120.45` with `authorized=false`. Desktop/Android development metadata now targets 120.45 only, not distributed as a release.
- Live Instagram signed-in action flows, actual Windows owner machine and Samsung installation, account scoped sync, and full English-only UI remain pending. PR #88 is separate and **not** included in v120.44.

## 2026-10-14 — English UI v120.45 continuation (PR #91; supersedes PR #88)

- Rebased the prior English UI work onto reconciled v120.45 development source without overwriting v120.44 published binary/version history. Android native translations, Desktop Review/Pending/Account, test protections and relevant CI gates are carried forward.
- Additional high-traffic English pass: 169 + 75 static labels, filters, Focus/Review/Pending/Import/Insights/Vault/diagnostics descriptions; over 60 Focus/recheck/session/audit status and confirmation strings; workspace navigation, dynamic toolbar controls, About Legal and Privacy copy. Bilingual Instagram DOM selectors and localized historic user strings are deliberately separate from app UI.
- **Data safety:** Guided Session statuses `pendiente`/`vacío`, legacy audit module `Seguidores que sigo`, review keys and browser state identifiers remain unchanged. English labels are derived at presentation. Native app preserves language-specific recognition tokens. Do not migrate stored keys for cosmetic translation.
- **Destructive action safety:** cloud delete stays opt-in, verifies the exact newly localized phrase `DELETE CLOUD` and signs out after deletion to avoid immediate re-sync. No deletion executed in development.
- Added `tests/android-native-english-contract.py` and `tests/english-ui-contract.py` to both CI and signed-release contracts; updated older Desktop/privacy assertions to match actual English UI without weakening export/deletion checks.
- **Pending acceptance:** system-wide generated JS strings and robot feedback still have legacy Spanish; final rendered wide/narrow Desktop, Android and Windows integrated EXE tests must pass on exact PR head. Live owner-signed-in Instagram confirmation/cancellation and optional audit require supervised acceptance; no Instagram relationship changes were executed. This is **development only**: v120.44 remains the stable official download; no authorization to release v120.45.


## 2026-10-14 — Static UI and collector CLI language audit (PR #92)

- After PR #91 was merged with five successful exact-head checks, continued the remaining static Desktop language audit on unreleased v120.45.
- Translated 42 long static instruction fragments and remaining labels in Review, Focus, Mutuals, Pending, Import, snapshot comparisons, Vault, diagnostics and confirmation dialogs. Audited 1,000+ rendered HTML source text nodes: zero still contain Spanish diacritics/inverted punctuation. This is **not** proof that all JS-generated text is English.
- Translated `tools/profile_counts_robot.py` terminal prompts, CSV errors, progress and argument help. Kept the Spanish/French strings used to recognize Instagram UI and page errors untouched.
- Expanded `tests/english-ui-contract.py` with static-HTML source text scan plus English CLI messages and multilingual parsing guard. CI should verify actual Desktop Chromium and Windows packaging as well as Android emulator before integration.
- Still pending: full audit of JS-generated status/error dialogs and live UI acceptance. Real signed-in owner Chrome, physical Samsung, and full language UI checks are separate. No v120.45 release authorization.

## 2026-10-15 — v120.47 dynamic Desktop English pass (development branch, not published)

- Source audit after PR #99 found many Spanish **rendered runtime strings** in Focus, Review, Mutuals, Pending, snapshots, account recovery, cloud delete confirmations, portable status reports and followback KPIs despite earlier static-only English checks.
- `fix/v12047-dynamic-english-desktop-20261015` translates more than 100 runtime occurrences using text-only substitutions (not changes to review IDs or saved state): active-batch notices, protection/verification prompts, Double Check/Recheck reset requests, filters and export report labels, migration dialogs and destructive-action confirmations.
- Adds positive/negative dynamic-copy assertions to the existing `tests/english-ui-contract.py`; preserved historical `pendiente` and `Seguidores que sigo` keys as well as bilingual Instagram DOM parsing.
- The language pass has NOT been verified on the owner's full real dataset or all reachable UI states. Exact-head Desktop Chromium, Windows EXE, Android emulator and CI must be green before integration. Untranslated secondary runtime messages elsewhere may remain and continue to be tracked under #86.
- Public stable remains **v120.46**, and newer v120.47 development cannot be published without an explicit release instruction.
