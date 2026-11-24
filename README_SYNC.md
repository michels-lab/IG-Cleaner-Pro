## v120.82 — FINAL release requested (24-Nov-2026)

Owner explicitly authorized official stable distribution for subsequent physical testing. Source #409, #410 and #411 integrated; #411 6/6 exact-head SUCCESS. Latest published remains v120.81 until governed publisher succeeds. All exact-source installer, signed APK, rendered UI and checksum gates remain mandatory. P0 58% (7/12), five real-account/device milestones pending. No RC, beta or Developer publication.

- [#409](https://github.com/michels-lab/IG-Cleaner-Pro/pull/409): account-bound cloud DELETE and export, preserve local history on registry refresh.
- [#410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410): reject hidden/offscreen/transparent identity controls.
- [#411](https://github.com/michels-lab/IG-Cleaner-Pro/pull/411): independent Automations batch status and 8-second local journal deadline, partial/unknown counts and retry.

---

# Instagram Cleaner Pro — Desktop + Android + Supabase Sync

> **Auth email issue (2026-10-11):** Hosted Supabase Auth/Brevo email templates remain a separate unresolved infrastructure check; successful GitHub release does not certify OTP deliverability.

Current published stable: **v120.81**, [official GitHub release](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.81), [successful exact-commit publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45319438358), **9 SHA-256-tracked stable assets**. Public Windows Setup installed/launched/uninstalled, production-signed Android stable APK installed/launched in emulator, same-source Home/About renders and integrity gates passed. The next reserved development version **v120.82 is not authorized**. One-time v120.81 permission consumed. Release is for owner's post-publication physical review, not proof of live Instagram Unfollow/Cancel/Focus or two-account physical acceptance. Developer Editions remain canceled.

## v120.41 — Safe app-user switch and Desktop Instagram registry refresh

Desktop **Cambiar usuario** and Android **Switch account** are distinct from changing an Instagram workspace; sign-in ownership, historic data and selected Instagram state remain isolated. The Desktop selector displays full Instagram handles and exposes an independent **Actualizar perfiles** action. The stable paired Desktop HTML and signed Android APK passed five exact-source automated checks, production certificate verification and runtime screenshot provenance. Physical Samsung two-login/ZIP tests remain open #24.

## Multiple Instagram profiles under one app login — shipped in v120.39

Since v120.39, **one Supabase Auth login supports several isolated Instagram data workspaces**. Each named @Instagram profile keeps independent Following, Followers, Pending, saved reviews/protection/snooze, Focus/Double Check cycle, batches, audit activity and historical snapshots. Desktop and native Android can select/create profiles, while the pre-existing v120.38 data remains at the special `legacy` identity without moving or deleting previous records. New profiles use composite `(user_id,account_key,...)` keys and owner RLS; the same user being followed by two Instagram profiles does **not** merge their review states.

**Originally published in v120.39:** official GitHub Release includes Desktop standalone HTML, Desktop ZIP and original-production-certificate signed Android APK. PRs #50 and #53 passed Desktop Chromium, installed Android emulator and 60 Supabase RLS tests. The additive migration is already live on production `ig-cleaner-sync`; old `legacy` data stays intact. New profiles keep the selector, reviews and IndexedDB isolated between different IG Cleaner sign-in owners on the same device. Exact-publication run `38112617481` passed signed APK and Desktop evidence gates. Physical Samsung and real two-Instagram ZIP/cloud roundtrip are still pending post-release acceptance; see [Multi-Instagram workspaces](docs/MULTI_INSTAGRAM_WORKSPACES.md) and issue #24.

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

The next reserved release target is **v120.82**, not authorized for publication. The owner-requested [v120.81 FINAL](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.81) was published from exact source `fc1cd03a476dc4c5797e90e89e18d22733c34175` by the [official publisher run #45319438358](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45319438358), with 4/4 jobs SUCCESS and 9 SHA256 assets. Its single-use permission was consumed on 2026-11-24 UTC. Real Instagram and physical device acceptance remains unverified. Every later official release requires a separate explicit approval and same-source installed Windows/Android, signing, UI, integrity, backup/update provenance verification.

Authority: `release/distribution-manifest.json`.

A guarded publication request must carry the owner's explicit scoped authorization (including the standing Operación Granada FINAL-only rule) and still pass every exact-source release gate. A stable Android artifact must not be a debug/`.beta` package presented as stable; it must be a proper release artifact with signing continuity established, or Android publication remains blocked.

The **primary Desktop artifact is a single standalone offline HTML** that embeds the canonical About identity images; an **optional secondary ZIP bundle** includes these original files separately:
- `IG-Cleaner-Pro.html`;
- `assets/michel_duarte_avatar.jpg`;
- `assets/michels-lab/official-lockup.png`.

See `PROJECT_LOG.md`, `docs/CURRENT_HANDOFF.md`, and `release/distribution-manifest.json` for current release evidence.
