# IG Cleaner Pro v120.27 — Desktop + Android Companion + Supabase Sync

This bundle contains the first complete cross-device architecture for IG Cleaner Pro.

## Included

- `desktop/ig_cleaner_pro_v120_27_synced_companion.html` — the existing desktop app plus a Sync Center.
- `android/` — native Android companion project. Focus is a checklist: tap one profile, Instagram opens, that row is marked opened, and the batch is only marked reviewed when you confirm the completed checklist.
- `supabase/schema.sql` — private per-user sync tables with Row Level Security.

## Sync semantics

- Review and audit are separate events.
- Every event records device (`desktop` / `android`), device id, timestamp, module and batch.
- A Focus prepared on Desktop is uploaded with its exact frozen username order.
- Android updates `focus_batch_items` one profile at a time and completes the batch only after explicit confirmation.
- `profile_state` is the current review projection. The newest `reviewed_at` wins; the event log is never overwritten.
- Desktop pulls remote `profile_state`, so Android-reviewed profiles become reviewed on Desktop.
- Audit events do not alter the original review timestamp.

## One-time Supabase setup

1. Create/open a Supabase project.
2. Run `supabase/schema.sql` in SQL Editor.
3. In Desktop → **Sync**, enter Project URL + anon/publishable key + email/password.
4. Use the same Project URL/key/email/password in Android → **Sync**.
5. Prepare a Foco 20/30/40 on Desktop and press Sync. It appears in Android.

The anon/publishable key is safe to ship in a client only because RLS is enabled. Never use a service-role key in Desktop or Android.

## Android build

The project has no third-party runtime SDK. It calls Supabase Auth/PostgREST with Android's built-in HTTP stack. A GitHub Actions workflow is included under `android/.github/workflows/android-companion.yml`; if you copy it to repository root `.github/workflows/`, it builds `app-debug.apk` as an artifact.