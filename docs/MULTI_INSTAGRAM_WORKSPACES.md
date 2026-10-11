# Multi-Instagram workspaces (published in v120.39 — PRs #50 and #53)

## Public release status — 2026-10-10

Published [stable v120.39](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.39): signed Android APK, self-contained Desktop HTML, optional ZIP and checksums. Governed release run `38112617481` completed successfully against `4170696589c22dc669deac10ca1a0ceddd88bfea` with exact-SHA installed Android emulator, Desktop Chromium, 60 Supabase assertions, production signing and bundle verification. Prior v120.38 remains downloadable; all old `legacy` tables and local review states are preserved. Real Samsung installation, genuine two-profile ZIP imports and authenticated cross-device data roundtrip are still open under issue #24.

The sections below document the pre-publication design/deployment chronology and intentionally retain their historic dates.

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
- **Historical pre-publication status (as of the initial PR merge):** at that moment stable v120.38 did not contain this feature. The v120.39 release has since been published as recorded above. Actual Samsung update, two genuine Instagram ZIP imports and live login roundtrip still require device acceptance.

## Final per-app-login isolation (2026-10-10)

- PR #53 [merged](https://github.com/michels-lab/IG-Cleaner-Pro/pull/53); exact SHA `9793e422a655a958e0f4096e4aa3ddd223551593` CI `38108180395`, native installed Android `38108180430`, Desktop Chromium `38108180542` all PASS.
- Named Instagram workspaces and their selection registry are isolated by **app login owner on the same device** (owner/email fingerprint). The preexisting `legacy` storage keys remain untouched by design for non-destructive v120.38 compatibility, so legacy local data can still exist in a shared browser profile; use separate browser profiles for strong local privacy between people.
- After sign-in or OTP recovery with another IG Cleaner login, Desktop reloads before sync under the new app login scope. The Android Workspace bridge uses the native app login email to scope storage and follows the native per-Instagram account selector.
- Chromium acceptance checked `legacy → A → B → A → legacy` review persistence, account selection, and different app-login registry separation. It also verifies no raw visible text node appears before the shell and that About remains accessible. The source fix removed the prior stray literal `\\n\\n` display.
- Real two-Instagram ZIP imports and cross-device authenticated sync with user's Samsung require physical/manual acceptance. This integrated code is not in the published APK/HTML until an explicitly authorized next version is released.
