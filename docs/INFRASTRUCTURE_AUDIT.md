## 2026-10-20 — Local Windows robot archive protocol for protected cohorts

[PR #170](https://github.com/michels-lab/IG-Cleaner-Pro/pull/170) merges local-only `/api/actions/defer-protected-batch` (explicit owner task ID + confirmation) and `/api/actions/deferred-batches` read-only scoped summaries. Saved account/task review cohorts are marked `deferred_at`, never as `approved_at`. The original journal, protected guard, Chrome session, pacing and privacy boundaries remain unchanged. No external provider, Meta API, credentials, new secrets, production migration, remote database writes or release version changes. Exact candidate-head integrated Windows installer + offline action fixture, Desktop and Android CI passed; real Instagram owner acceptance remains unverified, stable public v120.53 unaffected.

## 2026-10-20 — Windows loopback protected-batch rejection and no auto-retry

The installed Windows local-only robot HTTP bridge now uses a scoped HTTP 409 `stale_protected_batch` response, with normalized usernames/count/task, when a proposed owner-confirmed Unfollow/Cancel cohort collides with saved or UI-staged protected profiles. Browser UI mirrors only positive protections for the matching account and requires a completely new foreground approval; no automatic relationship actions, new service, cloud/provider access, cookie export, credentials, bypass or remote write were introduced. Back-end validation occurs under the existing per-robot and shared Chrome-admission locks before creating a durable review cohort or changing active worker identity. [PR #168](https://github.com/michels-lab/IG-Cleaner-Pro/pull/168) merged as `c9edb195562b1a98a6f4a865635b548a0f08b940`; five exact-head active CI workflows passed including integrated Windows Setup/installed launch; current user-installed Instagram session acceptance remains open. Stable GitHub release v120.53 is unchanged.

## 2026-10-19 — Developer twin isolation boundaries (source merged)

Windows and Android Developer Editions ship separate data/browser/storage identity rather than sharing public local sessions. Developer UI/native gates deny cloud writes while preserving real authentication, annotations remain local and owner-exported diagnostics redact credentials. Validated by PR #134 CI installed Windows/Android emulator and offline tests; live provider auth, physical phone, official signed Developer APK distribution and owner acceptance remain unverified. Stable public v120.53 unchanged.

## 2026-10-15 — Opt-in verified native Windows Setup updater

- The native updater uses GitHub public stable release metadata at a product-specific URL and checks official release SHA256SUMS. No new API tokens/secrets, Instagram access, cloud services, Supabase data mutations, update signing keys or remote privileged system changes. GET availability checks are automatic but optional downloads and Setup launch require foreground owner actions and session-only localhost capability.
- Installer checksum is checked while streaming and immediately before invocation. App UI and robot CSV/JSON/done journal snapshots are archived locally before launch; Chromium browser workspace, original Instagram ZIP, cookies and passwords are **not** included in the backup. Native Inno Setup is already designed to preserve old user data and can be cancelled. The updater reports `installer_started` rather than falsely claiming update success.
- Authenticode certificate/signature are **not configured** and the updater does not promise Windows publisher signature; SHA-256 guards integrity relative to official GitHub publication but is not a signature substitute. Owner real-machine update and physical Instagram sessions remain unvalidated.
- Work is source-level v120.47 development, no GitHub release was published.

## 2026-10-15 — Windows robot distribution: installable Setup candidate

- Declared per-user Inno Setup as the primary Windows robot distribution (existing Chrome/Playwright integrated EXE remains private installer payload, portable ZIP optional); no MS Store packaging, new external service, provider permissions or new signing secrets.
- Installer uses official product icon, complete `LICENSE.txt` (acceptance gate), user-controlled desktop shortcut, final taskbar pin guidance, Start menu/uninstaller. Persistent user workspaces under `%LOCALAPPDATA%\Michels Lab\Insta Cleaner Pro\` and original `%USERPROFILE%\.ig-cleaner-pro\` remain untouched on uninstall/upgrade.
- CI candidates perform static contract and actual signed-in-free silent installation, launch installed binary via `--healthcheck` and `--smoke-startup`, then uninstall and confirm persistent sentinel; separate rendered wizard testing, Authenticode, auto-updater and live Instagram remain **pending**. No release authorized.
- Future official Windows asset name `IG-Cleaner-Pro-Windows-Setup-v{version}.exe` must exist on same unified product release as Desktop HTML and Android APK; legacy ZIP is secondary. Update Michel's Lab master installer/distribution registries.

## 2026-10-11 — Auth email template/SMTP configuration gap (production blocker)

- Owner-reported Gmail **Confirm your email address** with link instead of expected OTP: redirect `localhost:3000` refused and `otp_expired`; Brevo fallback sender `realmichelduarte@12366255.brevosend.com` landed in Spam. Repo native/Desktop code calls `/auth/v1/otp` and expects six-digit `/verify` token, so hosted email templates must switch `{{ .ConfirmationURL }}` to `{{ .Token }}` for BOTH signup and magic-link flows.
- Prepared reproducible canonical templates, guarded management API helper (requires private token and exact project confirmation), offline CI contract and dashboard implementation guide. Sender branding **requires validated sender account/domain**; do not claim `@michelslab.dev` unless actual DNS/domain ownership and SPF/DKIM/DMARC exist.
- **Current provider status:** Supabase project `ilmztedebwdzgnlrvwxy` healthy; Auth template/SMTP settings NOT changed by our currently connected tools; no production user/data mutation. Manual provider settings or secure Management API access remains necessary, followed by two-account email OTP and deliverability acceptance. Existing release v120.41 remains published, no v120.42 authorization.

## 2026-10-11 — RLS runner setup failure and deterministic CLI pin

- Documentation/manifest closeout PR #71 encountered an upstream GitHub API rate-limit error in `supabase/setup-cli@v1` while resolving `version: latest` before database initialization or tests. To avoid the unversioned endpoint, pin to verified official stable CLI `2.120.0` (released 2026-10-06). No production Supabase auth, RLS data or schema changed. Full PR validation must rerun on updated commit before merge.

## 2026-10-11 — v120.41 stable publishing evidence

- Release `v120.41` published as a normal stable GitHub release at `1f711badcbc902e61beb7e382a49fe55f87fe9a1` via workflow 38125964658 (SUCCESS). Existing owner/RLS and export privacy boundaries unchanged; no live database migrations or user-data transformations. Signed Android APK verified with original long-lived certificate; self-contained Desktop HTML and optional ZIP uploaded alongside SHA256 checksums. Main-commit Android emulator and Chromium screenshot evidence verified by shared gate; physical Samsung/real credentials not tested.
- Consumed authorization and advanced manifest current stable v120.41 / next v120.42. This is release governance reconciliation, not an additional publication.

## 2026-10-11 — Candidate upgrade of cross-app UI evidence gate

- Public stable is v120.40; no new release is authorized by this QA work. The platform-specific emulator/Chromium Home+About evidence is retained and is now additionally checked by Michel's Lab's canonical `visual_release_gate.py` using source/real artifact SHA-256 and two viewports.
- Desktop screenshots will be taken from the self-contained distributable HTML (not the unbundled source). Android emulator screenshots remain bound to its installed debug APK; production signed APK, real Samsung and post-release owner review are distinct evidence levels.
- This is implementation in a branch pending exact-head CI; new tests and release workflow checks are designed to fail closed without image/manifest evidence.

## Updated production state — v120.39 (2026-10-10 Mexico)

- Current published stable: **v120.39**, signed Android APK and Desktop standalone HTML + ZIP. Next authorized target in the governed manifest: **v120.40** (not authorized yet).
- Existing source v120.38 data remains at `legacy` (unchanged tables); the additive seven-table owner+Instagram scoped RLS migration is live in project `ig-cleaner-sync`. Exact-candidate CI passed **60** behavioral RLS tests, and governed release run `38112617481` verified the real production signing certificate and normal stable assets. Original export ZIP/JSON/HTML stays local.
- Release request consumed after verified publication, with no manual prepublication approval gate; user's actual Samsung and two-account authenticated cloud roundtrip are tracked separately in issue #24. The below audit captures historical 2026-10-07 and prepublication findings (including old version labels) and is retained for evidence.

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
