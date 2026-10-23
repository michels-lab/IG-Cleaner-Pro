# GRANADA #39 — Normal Windows InstaCleaner target identity fail-closed

Date: 2026-10-23. Only the normal Windows Instagram action worker is changed; no Developer Edition features, other app repositories, or direct live account actions.

## Observed source risk
Instagram may asynchronously update its main profile hero while a semantic `<header>` still belongs to a different profile. Before this block, a URL matching the selected target and a visible Following/Requested action button in the header were enough; later post-menu checks could also accept a correct main hero while the actionable header remained stale. This is a **source-level risk**, not evidence of an actual wrong-account click.

## Fix
- Require the exact Instagram HTTPS target route and exact visible account name **within the header that owns the button** before selecting header-based action controls.
- Before the first relationship click, before the Unfollow menu/private confirmation, and before Cancel Request confirmation, reject a stale or unproven visible semantic header **even if main still names the intended user**.
- Only when there is *no visible semantic header* may a verified exact main-profile hero establish target identity. No click is sent when evidence conflicts.
- Existing approved action batches, owner identity verification, owner-protected profiles, durable write-ahead intent, retry limits, no-replay policy and account-isolated saved journals are unchanged.
- Regression fixtures cover wrong target, non-HTTPS route, stale header before action, stale identity after opening Unfollow/Cancel, *correct main hero plus conflicting actionable header*, and main-only valid layout.

## Validation and release boundary
- Original PR [#216](https://github.com/michels-lab/IG-Cleaner-Pro/pull/216) developed the check on a stale base. This clean current-main port preserves merged saved-journal quarantine from [#215](https://github.com/michels-lab/IG-Cleaner-Pro/pull/215); no whole-file overwrite of previous fixes.
- Do not merge until exact-head Windows installed integration, Chromium fixtures, Profile Counts, general CI, and required visuals pass. Offline fixtures are **not** proof of success/failure in owner's real Instagram.
- Official published stable at start is v120.57; this improvement is not in that release. Reserve v120.58 for an independently governed **FINAL** stable when validated (never RC). Keep actual owner Unfollow/Cancel Pending acceptance issues #172 and #164 OPEN.
