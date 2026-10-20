# GRANADA #11 — Profile Counts release-guide drift (2026-10-19)

**Issue:** [#156](https://github.com/michels-lab/IG-Cleaner-Pro/issues/156). **Base:** `main` commit `e8aa22a808e22b4e28b60d55aa9e4bb5d91f6657`. **Status:** integrated in `main` via [PR #157](https://github.com/michels-lab/IG-Cleaner-Pro/pull/157) at `1730b1f5fe75c8e050ac01b7eef3969281a88d9a` after **5/5 exact-HEAD checks SUCCESS**, including same-SHA rerun of installed Android visual screenshot transfer. [Issue #156](https://github.com/michels-lab/IG-Cleaner-Pro/issues/156) closed. **No new public release.**

## Defect and remediation
- The user guide `docs/PROFILE_COUNTS_ROBOT.md` still claimed that **v120.47** was the *current stable* and **v120.48** features were unpublished. In reality official stable is **v120.53** at this audit. A reader could install obsolete official packages or misjudge which features are shipped.
- The guide now avoids moving-current numeric claims. It directs release decisions to `release/distribution-manifest.json` → `releasePolicy.currentStableRelease` verified against actual official GitHub Releases. `releasePolicy.nextRelease` remains a reserved candidate until independently published, never a deployment claim.
- Historical v120.47 context is retained with explicit historical attribution; other instructions on login-isolated Chrome, opt-in rate limits, and no CAPTCHA bypass are unchanged.
- A new method in `tests/test_update_docs_contract.py` checks the guide's live release references and absence of obsolete "v120.48 unpublished" and "v120.47 current stable" claims, with existing normal CI coverage.

## Isolation and acceptance
- No Product/Developer engine, Instagram robot actions, Browser, Supabase cloud, packaging workflow, production credentials, user state or release manifest is modified.
- Independent of open Windows translation [#143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143), Profile Counts false-success requeue [#153](https://github.com/michels-lab/IG-Cleaner-Pro/pull/153), and historical view [#155](https://github.com/michels-lab/IG-Cleaner-Pro/pull/155).
- Check exact-HEAD CI before merging. Owner tests **official published release assets only**. Stable v120.53 remains; next reserved v120.54 not published, no publish authorization.
