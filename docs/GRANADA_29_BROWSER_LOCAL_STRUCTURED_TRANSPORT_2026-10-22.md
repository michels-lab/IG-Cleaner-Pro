# Operación Granada — browser-local structured Instagram transport study

**Date:** 2026-10-22. **Product:** IG Cleaner Pro only. **Boundary:** experimental **READ-ONLY** diagnostics in the isolated, owner-approved Windows Developer Chrome. This does **not** change the action robots or make an Unfollow/Cancel API request.

## User-supplied source evidence

The provided compiled Instagram Unfollowers JS uses a same-origin browser session and a private `/api/v1/friendships/{numeric-owner-id}/following/` GET with query, plus a separate private GraphQL Unfollow mutation requiring numeric target ID and ephemeral session-specific metadata. This is undocumented platform behavior, and the supplied constants cannot be independently verified as live for this user's account. Knowing previously imported usernames does **not** prove the numeric Instagram ID or grant an authenticated browser context in the GitHub repository / ChatGPT tool process.

## Concrete integration

- New `tools/ig_structured_probe.py` makes exactly **one bounded GET** inside the signed-in Developer Chrome origin; sends the session headers and cookies only within Chrome, with no token or raw response exported. It refuses wrong page, target, owner or HTTP scheme and accepts only one exact username match with a well-formed numeric ID. A 200 response with no matching result **must not** be interpreted as the user no longer follows the target (server pagination, filtering, eventual consistency).
- `tools/developer_live_probe.py` uses this alternative only if it already proved the correct owner and precise target but failed to find a unique relationship control for a saved unresolved **Unfollow** record. The resulting `FOLLOWING_STRUCTURED` code means **backend provided one positive exact match on the owner's following lookup at this instant**, not a click, not an action authorization, not successful Unfollow. Negative, missing-session, challenge or rate-limit results fail closed.
- **Cancel Pending has no equivalent documented/verifiable endpoint in the supplied file**, and is deliberately unchanged. There is no mutation/POST, GraphQL Unfollow, login bypass, private API retry, Chrome credentials export, automatic queue replay or release in this PR.
- User's existing owner/account-scoped saved unresolved journal determines which names Developer probes (maximum five per owner-authorized diagnostic). Existing 40-person cohort, protection list, action WAL, cookies and synced accounts are neither reindexed nor overwritten.

## Validation and next real bottleneck

Synthetic regression `tests/test_ig_structured_probe.py` invokes the JavaScript using a fake HTTP fetch in Node when present, checks positive exact match, absent match, malformed numeric ID, duplicate targets, rate limiting, one GET, same-origin credentials, no mutation and no secret disclosure. Added `tests/test_developer_live_probe.py` integration checks correct owner authorization, no calls for other accounts or pending-task, no new side effects.

**No claim of real Instagram capability until installed vNext Developer, signed into its separate Chrome, proves a positive exact structured lookup and physical owner interaction.** If request is rejected or challenge triggers, stop and report a precise failure. Only after a successful read-only test should an independently scoped opt-in action transport be designed with explicit targets, numeric identity, durable intent and independent confirmation. Do not copy hardcoded ephemeral GraphQL tokens or infer success from absence in a bounded following-query result. No RC/prerelease.
