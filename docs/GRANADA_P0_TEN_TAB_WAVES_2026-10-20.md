# GRANADA — Exact 10-tab waves / sequential verified Instagram actions

Owner instruction, 2026-10-20: open all Instagram target profiles of one 10-profile wave first; focus the first tab, perform its owner-approved action, check the resulting state, close only verified outcomes, focus the next; after the previous wave is fully accounted for, open the next ten. A 40-profile batch therefore yields four 10-profile waves, subject to already-completed/protected exclusions.

## Implemented source behavior
- `ActionRobot._run` stages up to `MAX_ACTION_TABS=10` separate visible Chrome pages per wave and navigates each to DOMContentLoaded before starting any action. Existing visits ledger, pacing and rest are enforced during navigation.
- Each prepared target tab is activated using `bring_to_front()` before invoking the existing verified `perform_visible_action` flow.
- The former rolling one-by-one `paced_prefetch` and mid-action next-user Chrome navigation have been removed. Only when all previous wave tabs are cleared can the next full wave start.
- Confirmed Unfollow/Cancel (`ok`) and confirmed no-click terminal states (`already_not_following`, `already_not_requested`) close their respective tabs. An ambiguous post-click result stays open, immediately blocks the next wave and preserves its original journal without replay. A manually closed uncertain tab is *not* permission to retry the click; the persisted journal still blocks it.
- Protected or skipped targets, even if already staged, are closed without touching the relationship. New wave candidates exclude prior potentially-clicked/verified outcomes and are selected from the remaining original cohort. No silent batch rewrite/archival occurs.
- Opening ten tabs does **not** imply ten rapid website requests: owner-configured visit pace, mandatory rest, login and CAPTCHA checks still apply.
- The finite tab wave is independent of the total approved action batch size. The UI still reports the original approved number of profiles; the 10-tab wave is only a browser execution detail.

## QA and honest limitations
- New `tests/test_action_tab_waves.py` covers ten-tab capacity, sequential verified closure, uncertain-action retention, Cancel no-request outcomes and source contract to prevent return of rolling prefetch.
- Both Profile Counts feature tests and integrated Windows installer/Chromium workflows run this test suite on the exact PR SHA. Existing offline Instagram-like DOM flows remain in the Windows suite.
- No CI fixture proves actual Unfollow/Cancel against the owner's live Instagram. This remains an explicit official-installed Developer/public acceptance requirement.
- Developer Edition's *bounded, owner-authorized real relationship action* test mode is a separate consent/session/journaling task; the existing Developer read-only probe and local diagnostic chat do not yet mutate accounts. Do not call it shipped or release v120.55 without further validation/owner release authorization.
