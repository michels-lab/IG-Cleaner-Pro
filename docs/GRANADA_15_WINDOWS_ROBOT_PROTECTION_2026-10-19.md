# GRANADA #15 — Windows robot protected-accounts persistence and explicit revocation (2026-10-19)

**Priority:** P0 Windows Desktop robots, epic [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164). **Issue:** [#165](https://github.com/michels-lab/IG-Cleaner-Pro/issues/165). **Base:** `main` at `d4ccebdcd4f1dc5ac4be1dc9d16ca1a3b8c5bea7`. **Branch:** `granada/windows-robots-protected-persistence-20261019`. **State:** isolated source candidate; exact-head CI pending; public v120.53 unchanged.

## Confirmed source-level P0 failure
1. New `ActionRobot.start` batch overwrote `action-protected-<owner-account hash>.json` with the submitted `protected` array rather than unioning already saved permanent protections. Restart/reimport/account switch producing an incomplete array could silently drop prior saved favorite protections and make those profiles eligible for a relationship-changing click.
2. `window.igcAutoProtect` called `requestAction("protect",{protected:[u]})` regardless of whether the owner was *protecting* or *unprotecting*. The local UI toggled optimistically before durable acknowledgement. As a result its displayed protection and Windows action guard could disagree.
3. Before a job starts, `ActionRobot.protect` correctly rejects an unbound owner scope: the loopback token is not enough to authenticate arbitrary account changes. The previous UI reported backend failure but had already flipped local state. The new UI explicitly stages additions locally for the next authorized batch without pretending they are yet persisted to Windows.

## Implementation
- `tools/profile_actions.py`: on every owner-authorized start, union disk-protected handles with the displayed UI handles, not only on resume. Same unchanged SHA256 filename based on NUL-separated `owner/account`, existing data stays in place; failed/unknown local state fails closed.
- `/api/actions/protect` accepts either additive `protected` or **one** `unprotected` with a matching explicit `unprotect:<username>` confirmation. It refuses mixed commands and removal while the worker is alive; a running or paused job from another account still owns its guard. An unbound cold startup rejects direct backend mutations; additions may be staged in the selected UI workspace and are saved by `ActionRobot.start` only after full owner/account/task selection and the usual explicit batch confirmation.
- `desktop/ig_cleaner_pro_v120_27_synced_companion.html`: the visible Protect toggle now asks for explicit removal confirmation and awaits the bridge's successful response before changing locally stored state. Failed removal leaves the profile visually protected and reports a real error. When the installed bridge has no bound owner yet, additions are staged locally for the next approved batch without claiming server persistence. If the bridge is absent, local additions remain possible; revoking durable Windows protections requires the installed bound robot. Any cross-owner API request is rejected.
- Regression tests extend `tests/test_profile_counts_actions.py`: two successive action modes, restart, seeded protected files, empty/stale UI lists, no cross-Instagram leakage, owner confirmation, active worker guard, unchanged historical filename and correct frontend request grammar.
- No Instagram relationship action, login, following import, Chrome session, Supabase table, Developer Android behavior, publishing workflow or production certificate touched.

## Independent PR and QA boundary
- This is intentionally a tiny surgical Desktop Protect-control hunk, distinct from the broader high-traffic English UI translation [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), which remains blocked on Developer Account test #135. Reconcile if future translation merge conflicts; no whitespace-wide reformat.
- Require exact-HEAD CI on real Chromium mock flows and frozen/installed Windows Setup smoke; Android UI/signing and Supabase regression where run. They do not prove real Instagram Following/Cancel request controls.
- The real owner Chrome login/Unfollow/Cancel completion and third+ Pending batch issues remain open [#83](https://github.com/michels-lab/IG-Cleaner-Pro/issues/83), [#114](https://github.com/michels-lab/IG-Cleaner-Pro/issues/114), [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133). No CAPTCHA bypass; no uncertain click replay.
- **Published stable v120.53** remains current, **v120.54 is reserved, not authorized/published**, and user only tests officially published release assets.

## CI and merge result
Await candidate exact-HEAD checks; never mark as integrated/published solely after source edits.
