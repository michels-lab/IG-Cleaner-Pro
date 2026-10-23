# GRANADA P0 — Unfollow based on owner-supplied code (2026-10-23)

## Source & implementation
The owner supplied `Pasted text(3).txt`. Its original compiled JavaScript uses:
- signed-in same-origin Instagram following GET to resolve one numeric ID for an exact username;
- `usePolarisUnfollowMutation` GraphQL POST, document ID `27789106940691111`, `target_user_id` variable, `x-fb-friendly-name`, `fb_dtsg/lsd`, `csrftoken`, `jazoest`, and `X-IG-App-ID`;
- post-mutation friendship check and action-block/rate-limit handling.

Normal Windows Unfollow source now calls `tools/instagram_unfollow_reference.py` instead of relying exclusively on finding a DOM Following button. The target's exact HTTPS profile, visible target header and signed-in owner are verified before read-only ID resolution and immediately before the authenticated mutation. Browser tokens and bodies never reach Python or logs. One `on_pre_click("relationship_control")` durable WAL is persisted **before** any POST. A POST is **never** repeated automatically on a missing/ambiguous response; no DOM fallback second action is permitted. Success requires independent fresh rendered profile verification; a GraphQL HTTP success alone is never counted.

The supplied code's undocumented Instagram operation could be obsolete; when exact ID, session tokens, mutation response or target identity cannot be established the robot must display an actionable failure rather than invent Unfollows. Cancel Pending remains on the previous conservative visible-control path. Owner approvals, saved original 40-person cohort, protected list, accounts and historical no-replay rules are preserved.

## Evidence boundary
Offline mocked Playwright/Python tests cover GET → WAL → exactly one POST, fail closed, safeguards and no false success. **These tests cannot establish actual Instagram Unfollow success**. Real installed Windows owner's actual signed-in consented test and explicit evidence are outstanding in #172/#164. No release, no RC or claim of repair until all exact-source CI and installed gates are passed.
