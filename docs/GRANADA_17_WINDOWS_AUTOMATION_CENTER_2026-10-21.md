# GRANADA P0 — Windows Automation Center: distinct Analysis and Action lanes

Date: 2026-10-21 · Issue #176 · source branch `granada/p0-windows-automation-center-lanes-20261021`

## Owner-facing problem
The previous Automations page started with an extra navigation-only panel, then mixed action controls, large Issue Review, pacing and Profile Counts. The actual state of each lane was not clear until scrolling. Issue #176 requires usable, visually verified, owner-specific robot workflows with no fake concurrency or destructive batch reset.

## Implemented UI candidate
1. **Two permanent lane cards, at the beginning of Automations**: Analysis (Profile Counts and read-only followback inspection) versus Action (Unfollow and Cancel Pending). They reuse existing real robot controls; no second Run implementation, no duplicate storage engine and no extra polling. Each card links to its existing real workspace, preserving all existing IDs.
2. **Live status mirrors**: cards reflect the authoritative existing `igcCountsRobotStatus` and `igcAutoLiveStatus` nodes through DOM observation; no fabricated successes. Batch summary distinguishes **next batch preference** from a separate **saved active cohort**, using the existing pending-batch approval details. Updating the preferred number cannot silently replan a persisted group.
3. **Issue Review is optional, keyboard-accessible**: a native `<details>/<summary>` holds the existing full issue filter/table and on-screen count; the original issue journal, filters and explicit Reviewed operations remain unchanged. It starts closed so it cannot crowd robot controls. Owner can expand at any time. Table scrolls within its own body.
4. **Honest concurrency**: visible fixed rule that browser-driven analysis and relationship-changing action workers still share the current browser admission gate. They must not run simultaneously unless independent session ownership and backend locks are separately implemented and tested; saved/local-only analysis may run without Chrome. No bypass of security checks.
5. **Responsive, scoped design**: two aligned cards on wide Windows, stacked on compact layout; preserves existing approved theme tokens/header About, legacy automation panels and separate Profile Counts dated results.

## Non-destructive boundaries
- Did NOT modify `tools/profile_actions.py`, journal formats, protection/favorites, `tools/profile_counts_bridge.py`, Chrome session directories, pending batches, Supabase sync, JSON imports, localStorage identifiers, release workflows or app version.
- Does NOT claim simultaneous live Analysis + Action browser navigation; needs independent Chrome contexts and an owner/scope-aware concurrency test matrix.
- Does NOT claim real Instagram Unfollow/Cancel success or acceptance from a Chromium fixture.
- Distinct pending code in PR #183 is not merged into this branch; no overwrite. Open English translation PR #143 was inspected; its diff did not modify the Automation Center markup/new runtime block, but future merge still requires conflict check and CI.

## Verifiable QA
- New `tests/automation-center-browser.test.cjs`: launches genuine Chromium against the same candidate standalone HTML, renders 390px and 1280px viewports, verifies both lanes, no duplicate Run controls, source-status updates, preference versus saved-cohort wording, browser-concurrency warning, native disclosure/mouse/keyboard and untouched Issue Review filters. Writes two screenshots.
- `.github/workflows/desktop-rendered-ui.yml`: runs real rendered acceptance after standalone HTML build and stores screenshots with visual evidence artifacts.
- `.github/workflows/profile-counts-windows-preview.yml`: same rendered smoke test on actual packaged HTML before PyInstaller + Inno Setup native Windows build, in addition to existing Chromium robots.
- **QA status is not inferred from committed tests**. Check exact-head workflow conclusions and job logs. Release requires separate explicit owner authorization and actual owner-installed verification.

## Remaining issue #176 scope
- Move the complete existing Action/Analysis sub-workflows into a truly redesigned compact information architecture, including safe pacing/exclusions/rotating target builder and a focused review subview. No large duplicated cards. This PR delivers the main navigation/status/disclosure foundation but is not the full issue's definition of done.
- Implement proven parallel analysis only with per-browser-context ownership and independent navigation locking; otherwise leave the safety gate active.
- Test signed-in physical Windows app and owner Instagram session after **official published stable** only; no owner test of previews. Current official release v120.54; reserved candidate v120.55 not authorized.

## Handoff
Source code: `desktop/ig_cleaner_pro_v120_27_synced_companion.html`. Test: `tests/automation-center-browser.test.cjs`. Workflow integration: rendered Desktop and installed Windows. PR not merged or published. Next action: inspect same-SHA CI, fix test/render failure on this isolated branch without changing the action engine, then review for possible merge. Remaining P0 #172 action failures and #173 official Developer installs remain open.
