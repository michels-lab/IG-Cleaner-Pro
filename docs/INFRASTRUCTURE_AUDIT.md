# IG Cleaner Pro — Infrastructure & Privacy Audit

Last reviewed: **2026-10-07**

## Current architecture

- Local-first Instagram export processing.
- Optional authenticated Supabase synchronization for normalized app state.
- Desktop + Android share the same synchronized relationship/review domain.
- Stable v120.34 is published with persistent Android production signing.
- v120.35 is the active development target.

The original Instagram ZIP/JSON/HTML export is not uploaded as a cloud backup.

## Synchronized Supabase domain

Project: `ig-cleaner-sync`

Tables:
- `devices`
- `audit_events`
- `focus_batches`
- `focus_batch_items`
- `profile_state`
- `list_snapshots`
- `workspace_state`

All seven public tables have Row Level Security enabled.

The live policies constrain CRUD operations to the authenticated owner with `(select auth.uid()) = user_id`. Policies are explicitly scoped `TO authenticated`. The repository schema remains the declarative source used by local CI.

## Automated RLS evidence

v120.35 adds:
- `supabase/tests/rls_isolation.sql`
- `tests/rls-contract.py`
- CI job **Supabase RLS isolation**

The pgTAP suite contains 35 behavioral assertions across all seven tables:
- RLS enabled;
- cross-user SELECT isolation;
- cross-user UPDATE denial;
- cross-user DELETE denial;
- own-user INSERT allowed.

CI boots a local Supabase stack, applies `supabase/schema.sql`, then runs the suite with `supabase test db`.

A separate rollback-only transactional test against the live project seeded two users across all seven synchronized tables. Under user 2's authenticated JWT subject, each seeded table exposed only user 2's row; attempts to UPDATE or DELETE user 1's rows affected 0 rows on all seven tables; an own-user INSERT succeeded. The entire test transaction was rolled back.

Current Supabase advisor state on 2026-10-07:
- no RLS exposure finding was returned;
- the prior **28 Auth RLS Initialization Plan** performance warnings were eliminated by the v120.35 policy migration;
- one informational unused-index notice remains for `audit_events_user_device_idx`;
- one unrelated security warning remains: **Leaked Password Protection Disabled** in Supabase Auth. This is an Auth-hardening setting, not an RLS failure.

## Privacy controls

v120.35 adds centralized synchronized-data controls to both clients.

Desktop:
- Exportar datos de nube
- Borrar datos de nube

Android:
- Export synchronized cloud data
- Delete synchronized cloud data

Export reads all RLS-visible rows from the seven synchronized tables and writes `ig-cleaner-cloud-export-v1` JSON.

Delete removes the current authenticated user's synchronized rows in foreign-key-safe order and then signs out. It does not remove the original Instagram export or independent local Vault/file backups.

## Android production signing

Stable package:
- `com.michelslab.igcleaner`

Persistent signer:
- alias `ig-cleaner-pro`
- SHA-256 `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
- valid through 9999-12-31

Private keystore/password material is never committed. GitHub Actions secrets supply signing material to ephemeral release runners.

v120.35 Android identity:
- versionCode 12035
- versionName 120.35

## Release infrastructure

Current published stable: **v120.34**  
Next target: **v120.35**

v120.34's version-specific publisher is a retired non-publishing stub.

Future stable releases use:
- `.github/workflows/release.yml`
- dynamic version/tag authorization from `.michelslab/release-request.json`
- artifact templates from `release/distribution-manifest.json`
- the same persistent Android signing identity.

The generic publisher still requires explicit release authorization and never treats a normal merge to `main` as permission to publish.

## Remaining evidence / work

Repository-side items from the prior audit are implemented in the v120.35 candidate:
- generic stable publisher — implemented;
- automated cross-user RLS tests — implemented;
- centralized cloud export/delete controls — implemented.

Still outstanding:
1. Full CI must pass on the v120.35 PR before merge.
2. Real-device validation of the new Android privacy controls and normal v120.35 app behavior.
3. The Supabase Auth warning for leaked-password protection may be hardened separately if desired.
4. v120.35 must not be published until explicit user release authorization.

Canonical privacy reference: `docs/PRIVACY.md`.

## 2026-10-09 — Planned multi-Instagram data isolation (PR #50, unreleased)

The former synced dataset is keyed only to IG Cleaner Auth user, so multiple Instagram exports could overwrite `list_snapshots(user_id,list_name)`, `profile_state(user_id,username,module)` and Focus/audit histories. An **additive** schema defines a registry `instagram_accounts(user_id,account_key,username)` plus separately keyed scoped tables for six user-data domains. Original seven tables remain fully intact and accessible to stable v120.38. `legacy` maps to that previous dataset without copying it. New profile rows have unique `(user_id,account_key,...)` keys, registered-owner FK and RLS. All-account privacy export/delete must include the new tables.

Implementation is in PR #50 and `supabase/migrations/20261009_multi_instagram_workspaces.sql`; tests define 60 pgTAP behavioral assertions plus Desktop and Android namespace checks. **This is not evidence of production deploy, user ZIP or real account synchronization.** Do not apply to live Supabase or publish until the candidate passes all tests. Detailed migration contract: [MULTI_INSTAGRAM_WORKSPACES.md](MULTI_INSTAGRAM_WORKSPACES.md).

## 2026-10-10 — Production multi-Instagram migration applied, legacy rows preserved

- Migration `supabase/migrations/20261009_multi_instagram_workspaces.sql` deployed to project `ig-cleaner-sync` as `multi_instagram_workspace_isolation_v1` after green exact-head CI (60 pgTAP assertions), Android emulator and Desktop browser tests.
- Live post-deployment read-only verification: `public.list_snapshots` still has **3 rows** (3 before), `instagram_accounts` and new scoped `instagram_list_snapshots` empty until user adds profiles, all **7 new tables** RLS enabled and **7 composite primary keys** exist.
- Database changes additive only; no legacy table mutation. Application code merged via PR #50; not yet delivered in a stable release. Preserve currently installed v120.38 behavior and user data; next release requires explicit consent.
