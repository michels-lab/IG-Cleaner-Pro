# IG Cleaner Pro — Desktop + Android + Supabase Sync

Current Android work line: **v120.30 beta**.

## Product model

IG Cleaner is one product with two interaction surfaces:

- **Desktop:** the full single-file IG Cleaner workspace.
- **Android:** the full Desktop workspace packaged inside the app, plus native mobile Focus and Audit surfaces.

Android is not a reduced companion. The Workspace exposes the same list data and modules as Desktop; native screens are kept only where mobile interaction benefits from a different workflow.

## What synchronizes in v120.30

Supabase now stores both workflow state **and normalized list snapshots**:

- device identity / last-seen;
- complete `following`, `followers` and `pending` username lists with the metadata IG Cleaner already uses to reconstruct its rows;
- frozen Focus batches and batch items;
- audit events;
- projected per-profile review state.

This means Android can rebuild Review, Mutuals, Followers and Pending from the data published by Desktop instead of showing only counters or empty tables.

The original Instagram ZIP/JSON/HTML file itself is **not** uploaded as a backup. Desktop publishes a normalized snapshot of the profile-list records needed by IG Cleaner.

## List-source rule

For v120.30, Desktop is the canonical publisher of the complete lists.

1. Import/process the Instagram export on Desktop.
2. Sign in to **Cuenta** and run Sync (automatic sync also runs while the app is open).
3. Desktop publishes Following, Followers and Pending to the private per-user `list_snapshots` rows.
4. Android downloads those snapshots and reconstructs the same people in its Workspace.

Android does not overwrite the canonical Desktop list snapshot merely because a fresh phone starts with empty local lists.

## Authentication and session ownership

Android now has **one native Profile account experience**. Password is the primary sign-in method; email OTP is reserved for first-time password setup and recovery.

The former separate native light-blue login is no longer used by bottom navigation. The Workspace session is bridged into the native Focus/Audit layer so all Android surfaces share the same authenticated account.

Session refresh was hardened for Supabase refresh-token rotation:

- HTTP 401 and 403 can trigger a refresh retry;
- a transient failed refresh no longer immediately erases the remembered native session;
- refreshed Workspace credentials are bridged back into native storage;
- the hidden Workspace is destroyed when entering native Focus/Audit so two independent 15-second refresh loops do not race each other.

End users only enter:
1. email;
2. **Enviar código**;
3. the OTP from email;
4. **Entrar con código**.

Project URL and publishable key remain application configuration. Never ship a service-role key, database password, SMTP credential, refresh token or other privileged secret.

## Shared sync semantics

- Opening a profile and reviewing a profile are separate events.
- Review history is append-only through audit events.
- Current review projection uses the newest review timestamp.
- Every event preserves source device (`desktop` / `android`).
- Audit never rewrites the original review time.
- Focus prepared on Desktop keeps its exact frozen username order on Android.
- Android reviews must appear on Desktop after sync, and vice versa.

## Supabase tables

v120.30 uses:

- `devices`
- `audit_events`
- `focus_batches`
- `focus_batch_items`
- `profile_state`
- `list_snapshots`

All application tables use Row Level Security so authenticated users can access only their own rows.

## Android v120.30

Android includes:

- Workspace — packaged Desktop engine and complete synced lists;
- Focus — one-profile-at-a-time native checklist;
- Audit — cross-device review/open history;
- Cuenta — the Workspace account page, used as Android's single visible login.

Workspace integration also provides:

- Android file chooser for HTML/JSON/ZIP inputs;
- external Instagram-link handling;
- mobile prevention/redirection of Desktop bulk-profile opening;
- generated export saving to Android Downloads;
- shared session/device identity between Workspace and native Focus/Audit.

## Validation — 2026-10-05

- Live Supabase migration `add_full_list_snapshots_v120_30` applied successfully.
- `public.list_snapshots` verified with RLS enabled.
- GitHub Actions run `37391428384` completed **SUCCESS** on `android-full-sync-v120.30`.
- `:app:assembleDebug` completed successfully.
- CI's **Verify embedded Workspace asset** gate also passed.
- The remaining gate is on-device functional validation: publish populated lists from the updated Desktop, sync Android, verify the real usernames appear in Review/Mutuals/Followers/Pending, and verify session persistence after app close/reopen.

Do not merge/release v120.30 until that device round-trip is confirmed.


## v120.32 Android product layer

Android now uses the Desktop design system as its canonical visual language rather than generic Material defaults. The mobile shell uses the Desktop palette, IG monogram, sans/monospace hierarchy and compact surface/border treatment.

Primary Android navigation is Home / Review / Focus / Activity / Profile. Home and Review are native. Advanced Desktop tools remain accessible from the overflow menu.

Home/Review restore the last successful per-account cache first, then refresh list_snapshots, workspace_state and profile_state. This prevents temporary zero-count states while the network refresh is running. Pull-to-refresh is supported.

Password sign-in uses Supabase Auth. On first-time setup or recovery, the user requests an email OTP, verifies it, sets a new password, and future sign-ins use email + password. Already-connected users can set or change their password directly from Profile without signing out.

Security note: client EXECUTE privileges were revoked from public.rls_auto_enable(). Supabase leaked-password protection should also be enabled in the project Auth settings.
