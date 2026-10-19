# GRANADA #5 — Release-manager authority, not stale versions (2026-10-19)

**Issue:** [#144](https://github.com/michels-lab/IG-Cleaner-Pro/issues/144). **Base:** `main` commit `6675122fa0d2d3396ff1ba40a15851babb646f8e`.

## Recorded bug
Both active agent sources `.github/agents/release-manager.agent.md` and `.github/copilot-instructions.md` hard-coded **v120.35 stable / v120.36 next**, even though the latest official GitHub stable release and distribution manifest list v120.53 stable, v120.54 reserved. An agent using the former instructions could infer wrong release numbers and attempt an unauthorized publication.

## Implemented
- Eliminated the old static version claims from active agent instructions. The release manager now requires the *current* `release/distribution-manifest.json` values `releasePolicy.currentStableRelease` and `releasePolicy.nextRelease` plus verification of actual GitHub Releases before decisions.
- Retained explicit authorization, CI exact commit, installed Windows, signed Android and visual acceptance gates. Merges, version bumps, CI builds and past authorizations **do not imply permission to publish**.
- Converted a dated `v120.36` Android About heading into a permanent release gate.
- Added `tests/test_release_agent_contract.py` and registered it in normal CI so active release instructions do not revert to stale versions.

## Isolation and acceptance
- Independent from English Desktop runtime [#143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), integrated Focus and updater, Windows robot/live Instagram [#133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133), Developer Android [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135).
- Does **not** alter manifests, tags, release assets, public code, auth, credentials, user data, Instagram actions or Android publishing.
- **Exact-head CI pending** until checks complete. No release is requested. Stable v120.53 remains published, v120.54 reserved. Owner tests only official published release, not PR/Actions candidates.
