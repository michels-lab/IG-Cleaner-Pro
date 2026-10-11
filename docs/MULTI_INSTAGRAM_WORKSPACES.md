# Multi-Instagram workspaces (merged, unreleased — PR #50)

## Product and identity boundaries
One IG Cleaner Pro login (Supabase Auth email/password) owns zero or more **Instagram data workspaces**. An Instagram workspace is **not** a separate Instagram login and does not need Instagram credentials or the Instagram API.

- `legacy` is the original v120.38 dataset. Its browser storage keys, IndexedDB names, Supabase tables and existing reviews remain untouched and fully readable by published v120.38.
- Every new Instagram username belongs to an opaque `ig_<UUID>` key under the same IG Cleaner owner; human-readable @username is metadata and can change, the data key must **never** be derived from the username.
- Desktop and Android use the same owner+account_key; selection must not promote an opened profile into reviewed, combine two profiles' follow dates, merge Focus cycles, leak protected users or overwrite another profile's list.
- Each Instagram has its own following, followers, pending, protected/reviewed/snoozed state, audits, batches, Double Check epochs and snapshot history. Device identity, IG Cleaner sign-in and account-wide privacy export/delete remain shared.
- Original user export ZIP/JSON/HTML stays local; normalized sync rows are scoped.

## Non-destructive migration and deploy order
1. Keep shipped v120.38 intact. Validate migration and 60 behavioral RLS tests in ephemeral Supabase, native APK emulator (8 tests per viewport) and Desktop Chromium/VM tests on the same commit.
2. Apply `supabase/migrations/20261009_multi_instagram_workspaces.sql` to the existing `ig-cleaner-sync` Supabase project **before** enabling new profile creation. This adds `instagram_accounts` and six scoped tables with composite owner+profile keys, FKs and RLS. It does **not** delete/rename/copy the legacy tables or rows. `supabase/schema.sql` contains the equivalent fresh-install schema.
3. Deploy a compatible Desktop and Android release together only when separately authorized. No release is authorized by merging PR #50.
4. Existing data remains under `legacy`. Users can assign its true @username as label, no export/import or identity guess required. New profiles begin empty and never automatically inherit legacy lists. ZIP import in a named new profile asks for target confirmation. Every full backup encodes its owner Instagram key; cross-profile restore is blocked.
5. User acceptance: sign in once on Android/Desktop, create @A and @B, import separate real ZIPs, review identical username under each independently, create Double Check 30, verify corresponding Android ↔ Desktop selection and correct lists, retry after sign-out, confirm backups, export all-cloud data, update existing signed APK.

## Authorization and safety
- Existing RLS `auth.uid()=user_id` is retained on all new tables. Each new table's PK includes `user_id,account_key`, preventing same-login overwrites; account registry/FKs prevent orphan profile references.
- All-account cloud export and deletion enumerate old and new scoped tables. Deletion removes child tables before account registry. The local browser backup/import remains per selected Instagram, not an entire multi-profile cloud archive.
- A missing migration on Desktop legacy fails soft; new profiles fail closed. Any account mismatch, missing registration or unconfirmed legacy backup must not silently populate a different Instagram profile.
- Never upload the production signing key, Auth service role credentials or private Instagram export for testing. Real user data and phone hardware are not exercised by CI.

## UI parity and text rendering QA

- Desktop: a profile picker appears alongside the workspace identity; `\\n\\n` previously displayed above the product sidebar because malformed literal escape text separated two `<style>` blocks, now removed from HTML source and covered by real Chromium assertions.
- Android: the native Profile screen manages Instagram identities; the current identity in the always-visible top toolbar is tappable for quick switching in **every section**. The About button is not replaced or moved. Active Focus and list caches are invalidated when changing identities; each account retains its own cloud and local scope.
- An Android instrumentation regression previously failed because the fixtures `ig_one_123`/`ig_two_456` did not satisfy the actual account_key minimum length. Updated to valid opaque-format fixture keys; all runtime checks must be rerun on the resulting commit.

## Status — 2026-10-10

- **Merged into main:** PR #50, squash `66f43cb38b3f0a046a819d196b6859dd04a521a1`.
- **Automated tests passed:** general CI `38105541087` (including **60** per-user and per-Instagram pgTAP assertions), native emulator `38105541099` and Desktop Chromium `38105541095`. Android Profile and header switcher present; real Chromium guard against visible literal `\\n\\n` passed.
- **Production Supabase additive migration applied:** `multi_instagram_workspace_isolation_v1`. Seven new RLS-protected, composite-keyed tables created. The three legacy `list_snapshots` rows remained unchanged (three before and three after); new account registry and list snapshots initially empty.
- **Still unreleased:** stable GitHub download remains v120.38 and does not contain this change. v120.39 needs a new explicit user request. Actual Samsung update, two genuine Instagram ZIP imports and live login roundtrip need device acceptance; do not claim they passed.
