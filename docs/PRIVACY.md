# Instagram Cleaner Pro — Privacy & Data Handling

Last reviewed: **2026-10-06**
Applies to candidate: **v120.34**

## Short version

Instagram Cleaner Pro is **local-first**.

The original Instagram export (`.zip`, JSON or HTML) is parsed on the device running the app. The app does not upload the raw export as a cloud backup.

When the user signs in and synchronization is enabled, Instagram Cleaner Pro does synchronize the normalized app data needed for Desktop ↔ Android continuity.

## Data that stays local

The raw Instagram export remains local:
- the original ZIP archive;
- the original JSON/HTML files;
- unsupported neighboring files in the export;
- local import parsing/intermediate file contents.

Desktop state also uses browser storage:
- `localStorage` for review/protection/snooze/configuration/focus/history metadata;
- IndexedDB database `ig_cleaner_pro_history`, schema version 1, for relationship snapshots.

Local state remains until the user clears/resets that app/browser storage or a documented migration changes it.

## Data synchronized when signed in

The current Supabase contract can store private per-user normalized state such as:
- normalized Following / Followers / Pending usernames and relationship metadata (`list_snapshots`);
- complete synchronized workspace review state (`workspace_state`);
- newer per-profile review/protected/snooze projections (`profile_state`);
- frozen Focus batches and Focus batch items;
- audit/review/open events and their timestamps/device origin;
- device identity / last-seen metadata.

This is not the same as uploading the original Instagram export.

## Authentication and isolation

Clients may contain only the public Supabase Project URL and publishable key.

Never ship:
- service-role/secret Supabase keys;
- database passwords;
- SMTP secrets;
- private signing keys/passwords;
- stored user access/refresh tokens in source control.

Application tables use Row Level Security so authenticated users are intended to access only their own rows.

## Backup and export

Before any destructive local-state migration or reset, use the app's **Vault** backup/export flow.

A Desktop update must preserve the browser storage context when state continuity is expected. Opening the app under a different origin/path/browser profile may create a separate local-storage context.

The Desktop release bundle includes identity assets next to the HTML; replacing the release bundle does not require uploading Instagram data.

## Retention and deletion

Local browser/app data is retained until the user removes or resets it.

Cloud-synchronized rows remain in the authenticated account until they are deleted from the synchronized store. v120.34 documents this boundary clearly; a single centralized in-product “delete all synchronized cloud data” control is **not yet claimed as implemented** and must not be represented as available until it is actually built and validated.

Deleting local browser data does not automatically prove cloud rows were deleted, and deleting cloud rows does not automatically erase independent local backups.

## Migration rule

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

## Manual validation still required

Repository tests can verify contracts and packaging, but they do not prove live provider isolation or phone behavior. Real-device/provider checks remain required for account/session persistence, Desktop ↔ Android round-trip, and production release/signing.
