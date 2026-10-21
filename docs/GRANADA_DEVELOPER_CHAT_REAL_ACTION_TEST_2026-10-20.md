# GRANADA · Developer diagnostic chat + owner-authorized real account action tests

Owner requirements (2026-10-20):
1. Developer chat must be basic: save an instruction, dispatch bounded local audit or real Instagram inspection, compare saved results, and copy a privacy-reviewed AI repair prompt to ChatGPT. No remote autonomous AI is needed.
2. Read-only diagnostics alone cannot prove that a real Unfollow / Cancel Pending button works. Developer needs a **distinct real-action test** on the owner's Instagram, using selected targets, with explicit authorization and a confirmed post-click result.
3. Production action robot execution uses 10-tab waves: open up to ten profiles first, then focus/verify/close each in order, only then open the next ten. Separate source workstream: PR #177.

## Implemented here (source candidate, not yet published)
- Local diagnostic chat in the Developer Edition panel, per account/workspace persistence, verbatim owner instructions, simple deterministic dispatch to journal/DOM audit and read-only real Instagram probe; optional comparison of read-only observations.
- **Copy for ChatGPT** sends the AI repair prompt + scoped notes + diagnostics to the local clipboard; browser clipboard unavailable => TXT file fallback. No auto-upload/remote ChatGPT integration and no actual AI dialogue inside the Developer app. Exact notes are owner-reported and confirmed before export.
- Windows-only separate **LIVE ACTION TEST** with exact **1–10** user-entered targets, task Unfollow or Cancel Pending. A detailed irreversible-action confirmation lists every target. The backend requires independent matching target-specific consent, rejects malformed/duplicate/over-limit targets, and denies mutation via old regular Developer endpoints.
- Backend invokes the existing `ActionRobot.start` against the **canonical owner/account/task action/protection journals** and a separate Developer Chrome profile; actions are actually executed and status, verified successes, pending issues and uncertain-click evidence are persisted. This avoids a second unaccounted Developer test journal causing a later public double click. Original pending/unapproved cohort consent cannot be silently bypassed. Unfollow still requires explicit full Followers evidence.
- Read-only live probes and action tests are mutually exclusive within the Developer process. CAPTCHA, unexpected owner, profile mismatch, protected account, unapproved earlier batch and uncertain post-click status fail closed. The visible button can pause the action test; freeform chat messages **never** trigger account changes.
- AI report includes a **username-free** real-action aggregate summary and the owner's voluntary chat/section annotations. Detailed live target names remain in local on-screen status, not automatically exported.

## Still required
- Reconcile this workstream with latest `main` and PR #177 before integration: this Developer branch was created before merged action fixes #174/#175 and is behind the current source. Never overwrite more recent 40→10/Cancel Pending behavior with older code.
- CI: Developer chat JS harness, Developer read-only and real-action API consent/auth tests, installed Windows Developer Setup and verified Chrome action fixtures; real-owner installed public vs Developer sessions. Action-changing Instagram acceptance must be completed by owner using a real account and a published release, not by CI fixtures.
- Provide separately downloaded signed Developer Windows installer and Android Developer APK in governed stable release; Android action changes remain disabled (this new live test is Windows-only).
- No automatic updates or release publication. Official stable remains v120.54; candidate v120.55 has no owner release permission.
