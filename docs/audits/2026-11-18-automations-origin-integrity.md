# GRANADA — rejected dual-account interface replaced by independent app windows (2026-11-18)

## Screenshot/user requirement and root cause
The installed Windows v120.80 screenshot shows **two account cards inside Automations**, a huge right-side statistics panel and additional secondary-account controls duplicated in the application sidebar. The owner explicitly rejects that UX: opening InstaCleaner again must create an independent application window with a separate login, not multiply account cards inside one window. On startup the launcher should ask which workspace to open.

Three root causes were verified in owning code:
1. `desktop/ig_cleaner_pro_v120_27_synced_companion.html` contained an unnecessary `igc-dual-workspace` rail, same-browser `sessionStorage` tab pinning and `openOtherWorkspace`/two-robot buttons, added despite a single-window account UX request.
2. `tools/ig_cleaner_desktop.py` injected `DUAL_ACTION_PANEL` and `AUTOMATION_ACTIVITY_PANEL` side-by-side into the same page; `tools/dual_action_windows_ui.py` built enormous Cuenta 1/Cuenta 2 cards. These competed with the **canonical** single-account Action Robot and Analysis sections.
3. The native Windows `acquire_single_instance` mutex forbade a second app process and all app windows used one persistent Chrome `--user-data-dir`.

## Code correction in PR #376, linked issue #377
- Native `windows_workspace_picker.py` uses Windows `TaskDialogIndirect` labeled account slot selection with Cancel. Primary keeps its exact old `workspace-browser`, original file:// UI path and mutex; secondary uses `workspace-browser-secondary`, `second-window/IG-Cleaner-Pro.html` and independent named mutex. Two separate app processes may coexist. The slots are **browser identities**, not trusted Instagram authentication; the user must sign into and verify each account.
- Actual HTML source removes `igc-dual-workspace`, duplicate account selection, old pinning and tab-cloning functions. The separate backend account-specific action journaling, global serial action interlock, approved Chrome action worker and protected/history data remain untouched. Removes retired Windows `DUAL_ACTION_PANEL` source and its UI-specific tests; backend dual-session/interlock safety tests remain.
- Real Automations navigation now consists of **Analyze / Actions / Review / History**. Original single action robot and original Issue Review drawer retain their IDs and data; the drawer is moved to its own Review area, not cloned. History is an independent single-account section, not a third column in every view.
- Activity panel retains exact time windows, separate provenance, uncertainty and current batch. The three primary periods are session/today/7d; the others are behind an explicit disclosure. Same-time contradictory WAL rows are reconciled before filtering.

## Non-negotiable data and safety boundaries
- Never clear/import/erase previous Chrome `User Data`, site data, localStorage, original ZIPs, review histories, protected profiles or click WAL.
- Account login selection is **not** a direct Instagram action or authentication proof, nor permission for parallel Unfollow/Cancellation. Preserve per-owner/workspace journals and existing cross-process robot locks.
- Automated Windows unit tests verify immutable primary paths, second Chrome profile and HTML origin separation, no duplicate injected UI and source command. Chromium rendered tests verify four navigation areas and native History, at 390 and 1280 widths. Current-SHA PR/installed Windows checks must pass.
- Windows TaskDialog **physical** button behavior, two simultaneously running installed app windows and owner account A/B real data remain **PENDING** until installed screenshots and physical user confirmation; no fake pass.
- **Stable v120.80 remains published and unchanged.** This is source-only, no release authorization for v120.81/Developer/RC, and no Instagram account was opened.

---

# GRANADA — Automations action provenance integrity (2026-11-18)

## Owner requirement and bounded implementation

Issue [#298](https://github.com/michels-lab/IG-Cleaner-Pro/issues/298) requests an Automations activity panel matching Manual Actions' time-window statistics, with separate verified robot actions, legacy unknown-origin records and manual actions. The existing Windows panel already exposed the canonical time windows but had **no usable origin filter**. Thus combined historical values were easy to misread as attributable robot actions despite the backend intentionally preserving `origin=unknown` for old WAL rows.

This source-only branch adds an active provenance selector:
- **Robot y registros históricos** (all saved records, still separating verified from unknown).
- **Solo robot verificado** (only explicit `origin=robot` confirmed results and robot warning events).
- **Origen histórico sin comprobar** (unknown-origin legacy outcomes and warnings, never relabeled successful robot operations).

The origin filter applies to the manual-parity period tiles, per-task breakdown, and saved-history view without loading Instagram or writing/replaying actions. It is per currently selected Windows owner/account and keeps the existing 15-second refresh, independent account selection, collapsible responsive panel, and the rest of Automations.

## Safety and exactness

Apply the provenance filter **after** canonical same-target timestamp reconciliation, never before. Two latest rows with equal timestamp but contradictory provenance/status remain unresolved; hiding `unknown` cannot turn the remaining `robot` copy into an invented success. Keep contradictory history visible as Review in filtered views. Count warning events by their own timestamp and recorded origin, not by the later OK's origin.

These are records in the existing token-protected local action journal; the panel does **not** read or assert cross-device manual-action history. Older entries without recorded origin remain unknown rather than being assigned to manual or robot. No changes to Chrome identities, target visits, action workers, click WAL, protected profiles, localStorage, Supabase, credentials or native Android.

## Regression and acceptance

- Extended `tests/automation-warning-events.test.cjs` with same-timestamp conflicting provenance, robot-only vs historical-unknown OK and warning counts, preservation of unknown warning events on later robot OK, plus a live production UI selector contract.
- Execute `node tests/automation-warning-events.test.cjs` on the exact branch commit through GitHub Actions CI; also require the Windows installed/screenshot gates where applicable. **Do not mark these passed until actual current-SHA runs are verified.**
- Physical installed Windows native activity panel and owner Instagram journal reconciliation remain **OPEN**. Manual+robot combined totals need a trustworthy shared origin boundary rather than guessing about old records. Issue #298 remains open.
- Last officially published stable remains **v120.80**. `v120.81` is only reserved, not authorized; no release/tag/RC/Developer edition or version change on this branch.

## Handoff

Source branch: `granada/automations-origin-integrity-20261118`. Relevant files: `tools/automation_activity_ui.py`, `tests/automation-warning-events.test.cjs`. After PR CI, verify installed Windows screenshots and manual-period parity; continue separate #230 self-profile visit acceptance and P0 #360 owner data tests without changing published v120.80 assets.
