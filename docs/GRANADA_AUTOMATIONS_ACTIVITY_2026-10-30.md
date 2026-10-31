# GRANADA · Automations Activity — Windows native sidebar
**Date:** 2026-10-30. **Status:** source integrated in `main`, NOT released, physical UI acceptance pending.

## User request
Automations needs the same practical time-based activity visibility as Manual Actions: hourly, last three hours, today, and the other existing day/week/month views. Keep visible totals and action-specific types, not just how many targets were opened.

## Implementation
- New self-contained native Windows source: `tools/automation_activity_ui.py`. Mounted by `tools/ig_cleaner_desktop.py::prepare_html` beside the Automation Command Center and the existing dual action workspace cards. Standard Windows only at this stage.
- **Read-only local data** through existing token-protected `POST /api/actions/history` for the **exact signed-in owner**, explicitly selected Instagram account, and both `unfollow` and `cancel` tasks. Uses the same canonical per-owner/per-account/per-task journal as the real action robot. This code does not visit Instagram, open tabs, replay actions or save a second counter store.
- Time windows: **Esta sesión** (from native page load), last **1 hour**, last **3 hours**, **Hoy** (local calendar day from midnight), rolling **24 hours**, rolling **7 days**, **Esta semana** (local Monday start), **Este mes** (local calendar first) and **Histórico**. Browser local zone is displayed in the refresh status. Local-day and trailing-24-hours intentionally differ after midnight.
- **Verified action:** only canonical saved status `ok` with a valid UTC `at` timestamp. `already_not_following` and `already_not_requested` are classified as preexisting/no new action. `review/error/blocked` are separate warnings; `profile_unavailable` is separate. A username appears once per task even if a malformed payload duplicates it.
- Sidebar breakdown: verified total, confirmed Unfollow, confirmed Cancel Pending, warnings, already-resolved without an action and unavailable. Selection per account, responsive layout, manual refresh plus read-only refresh every 15 seconds while visible.
- A failed/ambiguous history request produces **—**, never a fabricated zero. On logout/account changes, existing metrics clear before the next account's journal loads. Late in-flight responses cannot cross from one selected account to another.

## Test coverage added
- `tests/test_dual_action_windows_ui.py` (already invoked by CI): native-only injection, Developer source isolation, read-only endpoint, local-day/rolling-day source contract, no relationship-action commands.
- `tests/dual-action-windows-panel-browser.test.cjs` (offline Chromium fixture): two synthetic logged-in accounts and their canonical journal response, exact owner scoping, duplicate/no-op/review classification, midnight local-day versus 24h, per-account isolation.
- Embedded JS parsed using V8 and pure bucket calculations exercised with synthetic events. **No claim that GitHub Actions/installed Windows browser checks have passed** until their runs are verified.

## Outstanding acceptance — issue #298 remains OPEN
1. Read existing Manual Actions time selector and compare all displayed periods, translations, visual styling and edge semantics; the bundled HTML is >1 MB and could not be read through the current connector interface. Do not advertise exact Manual Actions feature parity yet.
2. Run exact-current-HEAD CI, actual Chromium screenshot on Windows (narrow + wide), installed Public build smoke and real user account **read-only** source comparison. Avoid visual overlap with modal/batch controls, check the sidebar while two workers run.
3. Historic journal rows may not have origin metadata. Do **not** claim an accurate manual-vs-automation attribution or merged manual totals until a reliable persisted provenance field is available. No fabricated historical origin.
4. Determine whether Android/Web and Windows Developer also need an equivalent panel with a valid data source. This initial integration is Windows Public, not a published APK.
5. No releases, tags, RCs, or update-feed mutations until explicit owner release approval and gated acceptance.
