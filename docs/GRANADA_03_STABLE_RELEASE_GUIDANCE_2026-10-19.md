# GRANADA #3 — Public stable update-guidance consistency (2026-10-19)

- Independent issue [#140](https://github.com/michels-lab/IG-Cleaner-Pro/issues/140).
- Base `main` `e802e900a7b59d466e02ff183547576dbf766624`. Scope limited to `docs/UPDATE_AND_STATE_MIGRATION.md`, `tests/test_update_docs_contract.py`, `.github/workflows/ci.yml` and this log; no overlap with active Windows snapshot PR #139.
- Verified source documentation drift: guide claimed v120.44 was **currently** shipped for Desktop and Android despite `release/distribution-manifest.json` showing stable v120.53, next reserved v120.54 and published [GitHub release v120.53](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.53).
- Corrected current Desktop/Android claims to published v120.53, linked official release, named v120.54 candidate as **not published**, clarified anonymous Windows release feed and explicit owner's Setup approval.
- Added `unittest` CI contract that compares latest published stable, reserved candidate, README, and every `currently v...` claim in update guidance. Future stable releases must update public guidance as part of publication.
- **Acceptance:** passing exact-head CI; stable release still v120.53. No user-side test of source artifacts, no automatic release. Owner only tests official published installers. Physical Instagram and Developer QA issues #133/#135 remain parked.
