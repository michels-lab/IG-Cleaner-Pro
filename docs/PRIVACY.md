# Instagram Cleaner Pro — Privacy & Data Handling

Last reviewed: **2026-10-07**  
Applies to development candidate: **v120.35**  
Current published stable: **v120.34**

## Short version

Instagram Cleaner Pro is **local-first**.

The original Instagram export (`.zip`, JSON or HTML) is parsed on the device running the app. The app does not upload the raw Instagram export as a cloud backup.

When the user signs in, IG Cleaner can synchronize normalized app state between Desktop and Android. v120.35 adds centralized controls to **export** that synchronized cloud state and to **delete** it.

## Data that stays local

The raw Instagram export remains local:
- the original ZIP archive;
- the original JSON/HTML files;
- unsupported neighboring files in the export;
- local import parsing/intermediate file contents.

Desktop state also uses browser storage:
- `localStorage` for review/protection/snooze/configuration/focus/history metadata;
- IndexedDB database `ig_cleaner_pro_history`, schema version 1, for relationship snapshots.

Independent local backups created through Vault or file export are separate from synchronized cloud rows.

## Data synchronized when signed in

The current Supabase contract can store private per-user normalized state in:
- `list_snapshots` — normalized Following / Followers / Pending usernames and relationship metadata;
- `workspace_state` — complete synchronized workspace review state;
- `profile_state` — per-profile review/protected projections;
- `focus_batches` — synchronized Focus batch headers;
- `focus_batch_items` — synchronized Focus members and decisions;
- `audit_events` — open/review/audit events with timestamps and device origin;
- `devices` — device identity / last-seen metadata.

This is not the same as uploading the original Instagram export.

## Authentication and isolation

Clients may contain only the public Supabase Project URL and publishable key.

Never ship:
- service-role/secret Supabase keys;
- database passwords;
- SMTP secrets;
- private Android signing keys/passwords;
- stored user access/refresh tokens in source control.

All seven synchronized tables have Row Level Security enabled. Their CRUD policies restrict authenticated clients to rows whose `user_id` matches `auth.uid()`.

The repository contains an automated pgTAP cross-user isolation suite at `supabase/tests/rls_isolation.sql`. CI runs it against a local Supabase instance and verifies that two simulated authenticated users cannot read, update or delete each other's rows.

## Export synchronized cloud data

v120.35 implements **Export synchronized cloud data** in both Desktop and Android.

The export:
- requires an authenticated IG Cleaner account;
- reads only rows visible through the current user's RLS session;
- paginates all seven synchronized tables;
- creates a JSON document using schema `ig-cleaner-cloud-export-v1`;
- includes per-table row counts, account/device context and the synchronized rows;
- explicitly does **not** contain the original Instagram ZIP/JSON/HTML export.

Desktop downloads the JSON through the browser. Android writes it to the IG Cleaner downloads folder.

## Delete synchronized cloud data

v120.35 implements **Delete synchronized cloud data** in both Desktop and Android.

Deletion:
- requires an authenticated account;
- requires explicit user confirmation;
- deletes only RLS-visible rows for that authenticated user;
- removes Focus items before Focus batches to respect the foreign key;
- deletes synchronized profile state, audit events, list snapshots, workspace state and device rows;
- does **not** delete the original Instagram export;
- does **not** delete independent Vault/file backups;
- signs the app out after cloud deletion so automatic sync cannot immediately repopulate the cloud from still-existing local state.

Cloud deletion and local deletion are intentionally separate actions. Deleting synchronized cloud rows does not erase independent local copies; clearing local app/browser state does not prove cloud rows were deleted.

## Backup and local-state migration

Before any destructive local-state migration or reset, use the app's **Vault** backup/export flow.

A Desktop update must preserve the browser storage context when state continuity is expected. Opening the app under a different origin/path/browser profile may create a separate local-storage context.

Persistent-state changes must:
1. read the previous schema before deleting anything;
2. preserve/export state before destructive conversion;
3. be idempotent;
4. preserve review/protected/snoozed/history semantics;
5. preserve active Focus recovery where possible;
6. preserve or explicitly migrate IndexedDB snapshots;
7. update `release/distribution-manifest.json`;
8. add CI/regression evidence;
9. document rollback in `PROJECT_LOG.md`.

If a migration cannot be performed safely, stop and require backup/export instead of silently resetting state.

## Validation boundary

Repository tests now verify:
- Desktop cloud-export/cloud-delete controls exist;
- Android native cloud-export/cloud-delete controls exist;
- synchronized-table coverage remains complete;
- the real Supabase schema has RLS enabled;
- a local automated two-user pgTAP suite exercises cross-user isolation;
- release/build/signing contracts remain intact.

Repository tests still do not prove every physical-device interaction. Real-device checks remain required for Android file-download UX, confirmation dialogs, session persistence and Desktop ↔ Android round-trip behavior.
