# GRANADA #2 — Windows update restore-point integrity (2026-10-19)

## Independent ownership / no interference
- **Scope:** `tools/windows_updater.py`, `tests/test_windows_updater.py` and this dedicated block log only.
- **Base:** `main` commit `48d3680d5b904d64546fbbec5b8e6fb78b2407eb`. Branch: `granada/windows-verified-restore-points-20261019`.
- **Do not edit:** Focus preview/PR #137, Instagram action robot/issue #133, Developer Windows/Android/issue #135, public `index.html`, Android sources, `PROJECT_LOG.md` while a parallel Focus PR changes it, and public release manifests/workflows.
- **Historical owner constraint:** tests on owner PC are from an official published release, not an Actions artifact. Stable remains **v120.53**; **v120.54 reserved**. No new release authorized by this block.

## Reproduced source gap and implementation
Windows updater SHA-256-verifies the downloaded official installer, then writes a ZIP snapshot of locally available UI and robot `.csv`, `.json`, `.done` journals; previously it did **not** verify the resulting archive before handing control to the Setup wizard. File system changes or corruption during snapshot creation could therefore leave an incomplete backup despite launching Setup.

Added:
1. `BACKUP-CHECKSUMS.json` manifest with SHA-256 of each **saved ZIP member**, calculated after ZIP is written, with metadata schema 2.
2. `verify_restore_point` validates ZIP readability, unique entries, exact manifest match, safe relative names and every saved member digest (streaming, avoiding large unbounded memory use).
3. Snapshot writes remain atomic; incomplete `.partial` files are deleted, and no final backup is exposed until verified.
4. Immediately before `Popen(Setup)`, the saved backup is reverified. Error stops Setup before launch, preserves existing robot journals and old executable.
5. Ignore symlink entries (including links in parent directories), and avoid persisting browser sessions/cookies or raw exports inside the backup.
6. Offline tests cover successful hash manifest, altered files with valid ZIP CRC, missing/unsafe/duplicate archive members, symlink exclusion, and refused Setup execution if final backup verification fails.

## Safety and acceptance boundaries
- Backup integrity is protection against **accidental corruption**, not cryptographic authentication of an attacker-modified archive (hash manifest is stored inside the same ZIP).
- The snapshot saves the local Desktop HTML and robot result journals. It **does not** snapshot Chrome cookies, Instagram credentials, localStorage, IndexedDB or original raw Instagram exports. Users' actual installed-state preservation across Windows upgrades still requires physical acceptance.
- The tests never execute real Instagram automation. This PR does not fix/close owner-acceptance issues #110, #133 or #135.

## Status
Source and regression tests committed on isolated branch. **Exact-HEAD CI and Windows installed Setup smoke pending** until workflow results are available. No merge, no version increment and no release publication is implied. Update this section after CI and merge review.
