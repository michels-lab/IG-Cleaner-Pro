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

A separate transactional smoke test against the live project created two temporary user-owned device rows, switched authenticated JWT subjects and confirmed the active user saw only its own test row. The transaction was rolled back.

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
