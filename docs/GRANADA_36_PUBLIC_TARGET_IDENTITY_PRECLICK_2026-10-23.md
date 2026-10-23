# Operación Granada #36 — normal Windows robot: stale Instagram profile identity hard-stop

Date: 2026-10-23 (America/Monterrey). Repo: michels-lab/IG-Cleaner-Pro.

## Reproduced source defect

In `tools/profile_actions.py`, `_profile_relationship_control()` accepted a matching Following/Requested button from a visible `header` whenever the browser URL matched the selected target. It did **not** require the header to visibly identify that target. Instagram can retain an earlier account's header while its single-page interface navigates/hydrates another target, leaving a stale or unrelated relationship control eligible for a click. This is a **source-level risk**, not evidence of an observed wrong-user Instagram action.

The normal worker also failed to re-prove the rendered target handle immediately before its first Following/Requested click and later Unfollow/Cancel Request confirmation clicks. Earlier URL/owner checks cannot rule out a concurrent interface swap.

## Source repair

- Require the exact **HTTPS Instagram target URL** and a **visible matching profile username in the same header that owns the button** before accepting a header relationship action. A correct username elsewhere in the main hero must never authenticate a stale header button.
- Recheck the same target identity immediately before the first relationship click, menu Unfollow click, private Unfollow confirmation and Cancel Request confirmation. On mismatch, **fail closed for manual review**, with no additional relationship click.
- Preserve existing session-owner verification, owner-approved per-target batch execution, protected handles, original 40-profile cohort, user account scope, fsynced write-ahead journal, uncertain-click no-replay and read-only post-action persistence verification. This patch does not migrate or delete any owner data.
- These checks do not add a new login mechanism, circumvent Instagram rate limits or depend on Developer Edition.

## Negative regression and test gates

Added four synthetic normal-worker regression cases in `tests/test_profile_counts_actions.py`:
1. Wrong header username (even when main already shows the right target) and non-HTTPS target URL cannot supply an actionable Following header control; correct header target can.
2. A stale hero swapped just before the first click produces no relationship click.
3. A swapped target after opening Unfollow menu never gets the final Unfollow click.
4. A swapped target after opening pending dialog never gets Cancel Request confirmation.

**Validation status:** code and tests proposed in a PR; review exact-commit CI before merge. Existing realistic Chromium, integrated Windows Setup/robot, action WAL, profile batches, Android and app checks remain required if the repository reports them for the PR. No real Instagram login or account mutation was executed from this change.

## Release/acceptance

Current official stable: **v120.56** (separate verified release); v120.57 is **reserved**, NOT published. This source fix is **not** a release authorization. Do not release or claim real Unfollow/Cancel Pending success without mandatory exact-head gates; real owner account acceptance remains open in #172 and #164. Do not work on Developer Edition as the current owner priority.

This change belongs only to InstaCleaner. No OpenFOAM or other product files imported.
