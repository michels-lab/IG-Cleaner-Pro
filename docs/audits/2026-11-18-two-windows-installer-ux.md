# Granada — two Windows account-slot upgrade/uninstall evidence and Automations navigation

Date: 2026-11-18. Source branch: `granada/windows-two-slot-installer-a11y-20261118`. Owner issue: [#377](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377). Parent implementation: [merged #376](https://github.com/michels-lab/IG-Cleaner-Pro/pull/376).

## Gap after #376

The native Windows startup chooser already isolated each application's Chrome `--user-data-dir`, file:// UI entrypoint and named mutex while retaining the first window's existing session. However, the integrated installer test only ran `--smoke-startup` for the **primary** workspace, then upgraded and uninstalled without checking the second window's state. That was insufficient evidence against regression for the user's explicit request for **two actual independent Windows windows**.

Automations already had four exclusive sections, but the tab names/subtitles were in English, the `role="tab"` controls lacked `aria-controls` links, and only the selected tab was keyboard-focusable without arrow-key navigation.

## Implementation

- `tools/test_windows_installer.ps1`: run the **installed binary** again with `--smoke-startup --workspace secondary`. Confirm the original and second UI file:// entrypoints are both present and complete, their deterministic Chrome user-data directories are separate, and the rendered bytes match. Write synthetic CI-only markers into both Chrome profile directories, reinstall the *same* app, verify both markers, both file origins and expected HTML bytes survived, uninstall and verify both profiles/markers remain. Remove **only** synthetic test markers; never wipe any actual Chrome profile, localStorage, actions WAL, protected users or Vault.
- `tests/windows-installer-contract.py`: enforce those checks exist in the release smoke test, so a future regression cannot quietly revert to a one-account installer test.
- `tests/test_native_desktop.py`: canceling the native chooser is asserted to start no Chrome process, localhost controller, folder creation, mutex or UI write.
- `desktop/ig_cleaner_pro_v120_27_synced_companion.html`: explicit Spanish navigation labels for the four areas (Analizar, Acciones, Revisar, Historial) with concise subtitles, `aria-controls`, `role=tabpanel`/labels, roving focus and Arrow/Home/End keyboard support. The single real Unfollow/Cancel worker and saved Review drawer remain untouched.
- `tests/automation-center-browser.test.cjs`: verify all four visible Spanish labels, every tab's exact panel target and keyboard-only navigation without opening profiles or acting on Instagram.

## What the CI proves, and does NOT prove

The integrated Windows test now exercises both workspace *startup paths of the real installed EXE* and the installed/upgrade/uninstall persistence. This is stronger than a pure source-unit test, but does **not** verify that two interactive Chrome GUI windows are simultaneously open or that Instagram accounts actually sign in and work. Those require physical two-window owner acceptance after a governed, published stable build; the user explicitly rejected two account cards inside the same app window. Neither this test nor existing Playwright offline fixtures should be represented as physical acceptance.

Existing cross-process global Instagram action lease stays in place. The second window does not imply two simultaneous relationship-changing workers; no race, bypass, auto-click, active user session migration, or Instagram login is introduced by these changes.

## Release discipline

The official published release remains `v120.80`. The next `v120.81` is reserved but **not authorized** under `release/distribution-manifest.json` and `.michelslab/release-request.json`. Source work can merge after exact-head CI; do not publish any release, create Developer/RC, or overwrite immutable assets. Mark real account/Windows GUI acceptance as **OPEN** until independently verified.
