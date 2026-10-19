# IG Cleaner Pro — Developer Edition (development candidate)

**Owner requirement (2026-10-19):** a real separate developer twin for IG Cleaner and every current/future Michel's Lab app. Source of truth: [Michel's Lab Developer Twin Audit Standard](https://github.com/michels-lab/Michel-Software-Standards/blob/main/standards/DEVELOPER_TWIN_AUDIT_STANDARD.md).

## How it is intended to work

- Windows installer optionally creates an **Insta Cleaner Pro - Developer Edition** Start menu shortcut, launching the same executable with `--developer`. The regular Windows app and Developer Edition use different single-instance mutexes, persistent Chrome profile directories and HTML origins; the developer version does not overwrite the customer's local import, review and settings files.
- The twin renders the same source UI and its existing **Cuenta / sync** screen. **Sign in / Account** opens that ordinary sign-in flow (real supported email OTP/password, account switching and sign-out); no fake developer credentials, copy of production browser cookies or bypass. Cloud login uses the real configured provider; permissions remain enforced by that provider. Product cloud sync is not a staging sandbox; do not treat developer login as permission to mutate production data.
- The bottom-right **Developer Edition** panel includes **Select section / control**. Click it, then click any real app section/control: that click is intercepted and does not invoke the underlying action. The panel displays a stable screen → section → control locator. Enter a freeform note and **Save section note**. Notes are browser-local, date-stamped, survive restart, and are keyed by the active app login/Instagram workspace. Existing notes can be edited, deleted or located in the current rendered UI. A missing locator is reported, not silently reassigned after an update.
- **Run audit** reads action journals read-only, counts previously saved statuses, issues, unapproved batches, and bounded UI DOM/runtime errors. It does not click Unfollow, Cancel or Follow. Robot/update POST operations are denied in the developer loopback controller. Findings describe what is known, not speculation about real Instagram success.
- **Export AI repair prompt (.txt)** and **Export report + notes (.json)** combine the automatic findings with **owner observations, verbatim comment, screen, section, control, last-seen locator, timestamps and evidence classification**. Notes are owner-reported, not auto-verified. Files are downloaded locally; they are not automatically uploaded. Review your own comments for identifying content before sharing them with an AI.
- Back end never exports raw Instagram usernames, cookies, credentials, auth tokens or raw exported lists. Only the owner's deliberately written notes are included verbatim when they choose Export.

## Known boundary and validation

This is currently source development on `fix/owner-qa-133-automation`; **not published**. Running static or mocked tests does not prove actual Windows Setup Developer shortcut, production login callback, HTML rendered UI, real account switching or Instagram relationship actions. The developer workflow must be smoke-tested as an installed Windows app before release claims. Real email OTP provider validation is separate.

This product currently has Desktop/Windows and Android. The first Developer Edition is a **Windows twin**; a separate Android Developer Edition with real login and section annotations is **not implemented** and must remain an explicit cross-platform backlog item. Do not claim Android parity.

## Mandatory QA

1. Test regular Windows launcher and developer launcher side by side: same app source/version, separate profiles and a working real Account/OTP navigation.
2. Add a note to the Batch size control, restart developer instance, confirm note and its exact locator, edit/delete, switch Instagram workspace and verify isolation; export TXT and JSON with both a known synthetic error and the verbatim note.
3. Confirm developer audit endpoints read journals without modifying the original bytes; relationship-changing POSTs and updating are blocked; app login remains available.
4. Verify no sensitive sessions or raw Instagram content are inserted into the exported file automatically; clearly classify user comments as owner-provided text.
5. Test compact/high-DPI panel overlay and rerender when source IDs change, without resetting saved owner comments.
6. Before an official stable release: validate original Windows Setup, offline Chromium action fixtures, Desktop render, Android signing/build and state migration, then publish only with owner authorization. **Michel tests only published official stable installers.**

## Remaining issue #133

See [issue #133](https://github.com/michels-lab/IG-Cleaner-Pro/issues/133) for unrelated active robot failures: batch size UI reset, no-click failure recovery, same-session manual inspection, journal backfill, progress reconciliations and compact counter wrapping. Code commits are **candidates** until CI and installed/live owner tests establish each result.
