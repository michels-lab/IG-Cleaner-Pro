# GRANADA #13 — Lossless Profile Counts CSV resume (2026-10-19)

**Issue:** [#160](https://github.com/michels-lab/IG-Cleaner-Pro/issues/160). **Branch:** `granada/profile-counts-safe-csv-recovery-20261019`. **Source base:** `main` at `82ece5b5c4ad066696f878aee4e29eee17e0de96`. **Status:** merged [PR #161](https://github.com/michels-lab/IG-Cleaner-Pro/pull/161) into `main` as `ee961dc2fa7e73b973006d7fb955fe4be93dbbfa`; exact PR head `a6f101d4cf6e605175a49135715a165c48a0d557` passed **7/7 CI checks**, including Profile Counts offline, installed Windows Setup, Desktop UI, Android About/build and Supabase RLS. Issue #160 closed; **not published**.

## Concrete source defect
- Prior `read_results` used a dictionary comprehension keyed by raw CSV username. Duplicate records were silently collapsed (last row wins); invalid profile rows could be silently skipped.
- The normal subsequent `save_results` writes exactly the recognized columns and one dict value per username. This can erase historical duplicate evidence and unknown owner-added columns on the next save, without an audit prompt, despite the file containing recoverable original rows.
- This path is used by **both** Windows Profile Counts bridge startup and the standalone read-only collector.

## Source correction and owner protection
- Reader validates an existing CSV before constructing a single resumed result map: strict syntax, unique known column names, required result columns, consistent row lengths, usernames valid under existing Instagram normalization, and duplicates detected across mixed case/`@` aliases.
- Unknown columns fail closed instead of being silently dropped by the next export writer; missing mandatory fields or surplus/truncated rows fail closed with an English diagnostic and line. It does not assume blank count = numeric 0.
- No automatic repair, truncation, deletion, new-backup-in-place or ignored corrupt rows. On invalid evidence the robot does not start visiting Instagram; the source remains byte-identical and must be reviewed by the owner.
- Compatible historical input with a BOM and missing *optional* metadata columns remains readable; valid `unavailable` error rows with blank counts remain readable. New output of normal 7-column writer remains compatible.
- Targeted regression tests `tests/test_granada_csv_recovery.py` check all these cases, plus no unexpected `.tmp` and Windows bridge `load_only=True` fail-closed without spawning Chrome.
- Dedicated Profile Counts Linux/Windows workflows invoke the new suite; no shared Desktop English CI paths modified.

## Isolation / acceptance
- Source only, no public release. No changes to Instagram mutation actions, Chrome sessions, authentication, Android Developer, cloud storage, Android signing, release version or public UI.
- Independent from English PR #143 and live owner acceptance #133/#135. Real Instagram/physical Windows remains pending after source QA.
- **Official stable v120.53** remains last shipped; **v120.54 reserved/unpublished**. User tests only published releases, not Actions artifacts.

## CI verdict
All seven exact-HEAD check families passed and PR #161 was merged. These checks do not validate live Instagram sessions or actual user-installed release. The public stable remains v120.53; v120.54 is reserved, not published.
