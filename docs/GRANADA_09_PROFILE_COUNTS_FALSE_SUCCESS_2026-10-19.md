# GRANADA #9 — Safe requeue of corrupted historical Profile Counts successes (2026-10-19)

**Issue:** [#152](https://github.com/michels-lab/IG-Cleaner-Pro/issues/152). **Branch:** `granada/profile-counts-false-success-resume-20261019`, based on `main` `8697c9f412ca68ec9e62d2dd293d1b58261ba05e`. **State:** merged [PR #153](https://github.com/michels-lab/IG-Cleaner-Pro/pull/153) into `main` at `dc229e38fde26dbaac5bf8798aae36bc3f160ef5`, **7/7 exact-HEAD check families SUCCESS**, including Windows installed Setup, Profile Counts offline, Desktop rendered, Android About/build and RLS. Issue #152 closed; **not published**.

## Gap
- Earlier GRANADA #7 enforces valid count and date evidence when appending dated history, but standalone `profile_counts_robot.py` and Windows `profile_counts_bridge.py` were still treating every historical CSV `status=ok` as completed even if its two numeric counts, Instagram username or date were corrupt.
- Such false-success records could suppress the next read-only re-audit indefinitely, or inflate completed/remaining counters, despite no verified evidence. This is especially harmful after recovery from previous crashed/imported sessions.

## Implementation
- Reuse precisely `tools/profile_counts_audit.py::_valid_reading` for verified old successes so CLI, dated-history and Windows bridge all agree on the definition of a successful visible measurement.
- Standalone collector `pending_count_targets` is an isolated pure function: missing profiles and invalid `ok` rows must be queued; explicitly failed non-OK statuses preserve the existing CLI `--retry-unavailable` opt-in policy, and verified `0` still counts as legitimate measured value.
- Windows bridge load/start, first-pass queue, progress, completed and remaining no longer treat malformed `ok` as verified; no cross-owner or cross-Instagram workspace borrowing.
- Windows results JSON maps only malformed old `ok` to `invalid_evidence` with a clear read-only `evidence_warning`. The source CSV remains **byte-identical** until the owner explicitly initiates a subsequent measurement. Previous valid observations are not overwritten by an unsuccessful re-audit.
- Dedicated fixtures `tests/test_granada_false_success_resume.py` cover the CLI policy, bad count/date evidence, zero/approximate values, owner/account scoping, API warning, stable original CSV and dated migration. Add to dedicated Profile Counts CI and installed Windows Setup CI, rather than editing shared main CI used by open Desktop English PR #143.

## Boundaries
- Does not sign into Instagram, navigate to any live profile, bypass challenges, automate unfollows/cancellations or publish a release. No Android production code/Developer code, Supabase data, or Windows updater modification.
- Existing `Profile Counts` live/browser acceptance #107/#77 remains open. Android Developer provider/device acceptance #135 and English Desktop PR #143 remain isolated.
- All owner installation tests must use official published GitHub release, not Actions artifacts. Stable **v120.53** still official, v120.54 reserved/unpublished.
- Merge only if exact-HEAD CI and installed Windows smoke pass; log proof and any unresolved risk.
