# GRANADA — Windows Automations History A→B→A scope epoch — 23-Nov-2026

## Source root cause / owner impact
The installed Windows History panel `tools/automation_activity_ui.py` fetched two canonical action journals asynchronously, then checked only owner and currently selected Instagram account by equality after `await`. With A→B→A before an old A response, owner/account are the same again and a stale prior request could be displayed as current. The same source used a mutable global `owner` in per-task response validation. This affects **read-only history and counters**; it is separate from Desktop Supabase pull fixed in merged PR #404.

## Changes
1. Track monotonic `scopeEpoch` when the authenticated owner, workspace registry, active Instagram account, or hidden statistics account selection is changed. Capture at request start and discard stale success/errors/late batch refresh when the generation has advanced, even if final account again equals A.
2. Bind expected owner to each history request before awaiting HTTP; validate response against captured owner, task and account, not a mutable global.
3. Preserve read-only actions, journal data, warning events, period windows and one-account-per-native-window presentation.

## Regression / CI
- `tests/automation-activity-aba-browser.test.cjs` injects the **actual Windows History JavaScript** into Chromium with mocked token-protected loopback history. It holds A/unfollow + A/cancel, switches A→B→A, resolves obsolete A first, asserts no misleading count, then confirms fresh A, fresh B, and authenticated owner switch.
- Windows integrated CI path filters and installed-HTML Chromium stage explicitly require this regression.
- Test fixtures never visit Instagram, access credentials or perform real Unfollow/Cancel.

## Gates and scope
- Source/test on PR branch only until exact-head CI completes. No installed Windows screenshot or physical owner actions tested by this audit. Keep #298/#360/#377/#371/#164/#172 open.
- The fixed 12 milestone path is **6/12 = 50%** pending owner physical acceptance and official v120.81 release; latest stable v120.80.
