# Instagram Cleaner Pro — Desktop + Android + Supabase Sync

Current published stable: **v120.38**. Historical v120.34 instructions below describe the prior release process.

## Multiple Instagram profiles under one app login — integrated, not yet released

The next development feature supports **one Supabase Auth login with several isolated Instagram data workspaces**. Each named @Instagram profile keeps independent Following, Followers, Pending, saved reviews/protection/snooze, Focus/Double Check cycle, batches, audit activity and historical snapshots. Desktop and native Android can select/create profiles, while the pre-existing v120.38 data remains at the special `legacy` identity without moving or deleting previous records. New profiles use composite `(user_id,account_key,...)` keys and owner RLS; the same user being followed by two Instagram profiles does **not** merge their review states.

**Code integrated; app binaries not yet released.** PRs #50 and #53 passed Desktop Chromium, installed Android emulator and 60 Supabase RLS tests. The additive migration has already been applied to production `ig-cleaner-sync`, with existing legacy data preserved. New profiles also keep their local selector, reviews and IndexedDB separate between different IG Cleaner login emails on the same device. Full acceptance and post-deployment limitations are documented in [Multi-Instagram workspaces](docs/MULTI_INSTAGRAM_WORKSPACES.md). Stable downloadable version remains **v120.38**; v120.39 is not authorized.

## Product model

Instagram Cleaner Pro is one product with two interaction surfaces:

- **Desktop:** the full IG Cleaner workspace.
- **Android:** native Home / Review / Focus / Activity / Profile plus the packaged Desktop engine for advanced tools and shared account/session behavior.

Android is not a reduced companion. It consumes the same synchronized people lists and review state and can now create Focus batches independently.

## What synchronizes

Supabase stores private per-user workflow state and normalized list snapshots:

- device identity / last-seen;
- complete `following`, `followers` and `pending` normalized list snapshots;
- frozen Focus batches and batch items;
- audit events;
- projected per-profile review/protected/snooze state;
- workspace state needed to preserve historical review decisions.

The original Instagram ZIP/JSON/HTML export is not uploaded as a backup. Import parsing remains local; only normalized app state needed for cross-device operation is synchronized.

## Released v120.38 — Focus information and Double Check parity

Android Focus now has native access to both follow dates, relationship direction, last review and decision, profile history and source context. Double Check 30 can be created natively for Review / no-follow-back, with a shared `workspace_state` cycle key (`focus_double_check_cycle`) containing an epoch and frozen seen-usernames; it does not overwrite `primary` review data. A native per-module summary shows the latest Review, Mutuals, Followers, Pending or Double Check batch time, size, status and originating device; previous Desktop Double Check audit events are also recognized. The feature is included in the published stable v120.38; exact-commit Android emulator and Desktop Chromium UI QA, Android signing and Supabase RLS passed. Actual Samsung/real Instagram ZIP and live authenticated Desktop↔Android account acceptance remain separate.

## Android Focus autonomy

Android v120.34 can create Focus batches without opening Windows/Desktop first.

Supported modules:
- Review / no te siguen;
- Mutuals;
- Followers que tú no sigues;
- Pending Requests.

Supported sizes:
- Focus 20;
- Focus 30;
- Focus 40.

Creation refreshes list snapshots and review state, excludes reviewed/protected/actively-snoozed profiles and usernames already in an active/prepared batch, then freezes the selected usernames in `focus_batches` + `focus_batch_items`.

If historical review state has not reached the cloud, Android refuses to create a misleading batch instead of treating every raw relationship as unresolved.

## Authentication / session ownership

Android uses one account/session model shared with the embedded Workspace. Password is the primary sign-in method; OTP remains for first-time setup or recovery. Refreshed Workspace credentials bridge back into native storage so native Focus/Audit and Workspace do not fight over separate sessions.

Never ship a service-role key, database password, SMTP credential, refresh token or other privileged secret.

## Canonical product identity

The official Instagram Cleaner Pro identity is the **three stacked layer/diamond planes with the restrained upper-right sparkle** from Michel's Lab standards.

The former rounded-square blue/cyan `IG` monogram is legacy/rejected and must not become an active identity source again.

Canonical child assets live under:
- `branding/ig-cleaner-pro/official-app-icon.svg`;
- `branding/ig-cleaner-pro/official-mark.svg`;
- `branding/ig-cleaner-pro/official-lockup.svg`.

About uses the canonical Michel Duarte portrait and Michel's Lab production lockup as real vendored assets rather than an embedded/recompressed portrait.

## Current v120.34 validation

Final consolidated repository validation:
- GitHub Actions run `37562844481`: **SUCCESS**.
- Desktop contract, fixture parsing, canonical branding, privacy contract, Android Focus/inset regression contract and distribution manifest: **PASS**.
- Android build + packaged Workspace: **PASS**.
- Android companion run `37562748629`: **SUCCESS** after the current About/privacy changes.
- The Desktop candidate contains the v120.30 full-state sync bridge, including legacy review normalization, `list_snapshots`, `workspace_state` and per-profile state merging.

Manual/device validation is still required before calling the Android stable artifact production-ready:
- cold launch;
- sign-in/session persistence;
- real synced usernames in Review / Mutuals / Followers / Pending;
- create Focus 20/30/40 on Android;
- complete/reopen a Focus batch;
- Android → Desktop review round-trip;
- audit device origin;
- physical rendering/insets.

## Release rule

The next governed release target is **v120.39** and GitHub `prerelease` must be **false**; the build version must advance and be validated before authorization.

Authority: `release/distribution-manifest.json`.

Publication is never automatic and requires explicit user authorization. A stable Android artifact must not be a debug/`.beta` package presented as stable; it must be a proper release artifact with signing continuity established, or Android publication remains blocked.

The **primary Desktop artifact is a single standalone offline HTML** that embeds the canonical About identity images; an **optional secondary ZIP bundle** includes these original files separately:
- `IG-Cleaner-Pro.html`;
- `assets/michel_duarte_avatar.jpg`;
- `assets/michels-lab/official-lockup.png`.

See `PROJECT_LOG.md`, `docs/CURRENT_HANDOFF.md`, and `release/distribution-manifest.json` for current release evidence.
