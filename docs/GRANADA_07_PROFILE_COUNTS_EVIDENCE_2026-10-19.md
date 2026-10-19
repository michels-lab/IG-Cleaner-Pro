# GRANADA #7 — Validate Profile Counts dated measurement evidence (2026-10-19)

**Issue:** [#148](https://github.com/michels-lab/IG-Cleaner-Pro/issues/148). **Branch:** `granada/profile-counts-evidence-validation-20261019` created from `main` at `2ac6692733b4702973b8fe2cfe7942b04bcb4cd4`. Public release unchanged at **v120.53**; v120.54 reserved and unpublished.

## Source-level gap
- `append_dated_reading` and `seed_latest_readings` previously allowed rows tagged `status=ok` with malformed count fields, dates, usernames or untrusted CSV formula-like text to enter the append-only timeline.
- `ordered_audit_targets` treated any status `ok` as a prior valid measurement even without a verifiable numeric follower/following pair, potentially leaving corrupt rows behind never-measured profiles in the oldest-first queue.

## Isolated correction
- One `_valid_reading` guard checks the exact source username, followers and following as nonnegative ASCII decimal integer strings (0 remains a valid observed count), timezone-aware date <= current time + 60 seconds, and `status=ok`.
- Invalid rows are **not appended** or migrated as successful measurements; no historical file is rewritten, truncated, deleted or converted to fabricated zero.
- When historical latest rows claim `ok` without valid evidence, schedule them as never successfully measured instead of treating them as completed. Visible Instagram read-only collection and original owner/account scope remain unchanged.
- `tests/test_profile_counts_audit.py` exercises malformed numeric strings, CSV-formula-like values, future/naive dates, unsafe usernames, preservation of an earlier valid snapshot, zero count + approximation compatibility, and accurate re-audit order.
- This PR modifies only the audit helper and existing audit tests; dedicated Profile Counts CI already discovers this suite. It does not edit the same files or CI workflows as separate GRANADA #6 [PR #147](https://github.com/michels-lab/IG-Cleaner-Pro/pull/147).

## QA / pending
- Await exact-head Profile Counts, Windows installed Setup, Desktop, Android and RLS checks before integration. No live owner Instagram acceptance, SMTP, Supabase production mutation or release publication claimed.
- The old historical CSV itself is left intact for recovery, even if it already contains earlier invalid rows. Existing read/history display does not yet retroactively filter old invalid archived rows; this step prevents new append or migration of such rows. Preserve that limitation explicitly.
- Owner tests only official published release installers. Issues #107/#77 require genuine live-session acceptance; #133/#135 remain separate. No version bump.
