# GRANADA P0 — isolate InstaCleaner file governance from unrelated engineering repositories

Date: 2026-10-21. Reported by owner with actual GitHub Actions screenshot: Actions for `michels-lab/IG-Cleaner-Pro` repeatedly displayed `fix(file-steward): canonical OpenFOAM case layout regression safety` while running the Windows installer preview.

## Confirmed root cause

- Existing commit [a0b5712](https://github.com/michels-lab/IG-Cleaner-Pro/commit/a0b5712230e4ecc1ac381d40f7162c4974b8130e) really exists **in the InstaCleaner Git history** with unrelated subject and paths. It modified `tools/test_repository_file_auditor.py` to add engineering-simulation examples.
- `tools/repository_file_auditor.py` carried research-case-specific path classes, extensionless field rules and scientific output vocabulary copied into this app's deterministic file taxonomy.
- The Windows preview workflow listened to **every push to main**, including file-governance commits. GitHub Actions reuses the triggering commit's message in *every* workflow row on that SHA; therefore one unrelated commit caused multiple OpenFOAM-titled Windows and File Steward rows.
- Repository tracked-tree inspection found **NO tracked scientific solver cases** or OpenFOAM project paths in the InstaCleaner repository itself. This was a mis-scoped **auditor implementation, test and commit message**, not scientific simulation entering the running InstaCleaner application.

## Implemented correction

1. Keep the File Steward engine and full `git ls-files` inventory, no auto-delete, SHA-based record fingerprints, docs/audits log and human triage; remove research-project-specific vocabulary and hard-coded case directory classification from this app. Unknown path classes remain explicitly `unknown`.
2. Replace unrelated simulation tests with **actual product file classes**: Windows native robot source/installer, Android Manifest, Desktop HTML, Chrome Companion, release manifest, CI workflow, action WAL test and current handoff. Verify unrelated extensionless directories remain `unknown`; do not invent semantics.
3. Scope Windows integrated installer preview **push triggers** to the same explicit 41 owned product source/test/packaging paths plus `.michelslab/release-request.json`. Governance-only report or auditor changes must not trigger expensive installed Windows Setup QA. Existing manual `workflow_dispatch` and product PR triggers remain. Real source/release changes still trigger Windows acceptance.
4. The File Steward self-audit workflow now also runs tests on relevant PRs, but never commits generated reports from PR context; only approved main/scheduled/manual runs write the local audit report. Other agents' OpenFOAM repository remains separately owned.
5. Add a regression test protecting Windows product-only push trigger and explicit app role taxonomy. No production robot, persisted approvals/protection, authentication, release request, signer, or official downloaded installer changed.

## Evidence / constraints

- Historical Git commit messages and completed Actions names are immutable; this PR prevents *new* cross-repository wording and unrelated Windows workflow noise, but should **not** rewrite published history or force-push main.
- New owner-specific file classification is not proof of an app install or live Instagram Unfollow/Cancel. Keep issue #172 open until genuine account acceptance.
- Current stable release verification and any paused v120.55 publication remain independent; no RC and no implicit new release request from this governance fix.
- Use exact-head PR File Steward workflow test outcome and merge check. Recalculate generated summaries only through the audited main workflow; do not wipe the previous evidence.

