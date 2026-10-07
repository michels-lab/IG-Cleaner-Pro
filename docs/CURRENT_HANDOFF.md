# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-07**
Trigger: **LIMÓN**

## Current stable release

- Published stable: **v120.34**
- GitHub prerelease: **false**
- Signed Android + Desktop artifacts are attached to the same release.
- Final v120.34 publisher: **37574744462 — SUCCESS**
- Stable production signer: FINAL-9999
  - package: `com.michelslab.igcleaner`
  - alias: `ig-cleaner-pro`
  - SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
  - valid through: **9999-12-31**

v120.34 is closed. Its consumed release authorization must not be reused.

## Active development

Branch: `development/v120.35-infra-privacy`  
Development version: **v120.35**  
Next governed release target: **v120.35**

v120.35 keeps the v120.34 functional baseline and adds infrastructure/privacy hardening without changing the raw Instagram import boundary.

### Generic governed release publisher

New canonical future publisher:
- `.github/workflows/release.yml`

It is version-agnostic and resolves:
- version/tag from `.michelslab/release-request.json`;
- artifact names from `release/distribution-manifest.json` templates;
- Android version from Gradle;
- the persistent FINAL-9999 signing identity from `release/android-signing.json`.

It refuses to publish unless:
- the request is explicitly authorized;
- request status is publishable;
- the requested tag equals `releasePolicy.nextRelease`;
- channel is stable and GitHub prerelease is false;
- Desktop visible version and Android version match the request;
- release regression contracts pass;
- the production signer fingerprint matches;
- the stable APK package/version checks pass.

The old `.github/workflows/release-v12034.yml` is now a harmless retired stub; it cannot publish anything.

### Automated Supabase RLS isolation

New test:
- `supabase/tests/rls_isolation.sql`

Coverage:
- all seven synchronized tables have RLS enabled;
- user 1 can see only user 1 rows;
- user 2 cannot update user 1 rows;
- user 2 cannot delete user 1 rows;
- user 2 can insert rows owned by user 2.

CI job:
- starts a local Supabase stack;
- applies `supabase/schema.sql`;
- executes the pgTAP suite through `supabase test db`;
- uses 35 assertions.

A transactional production smoke check also confirmed the live project isolates temporary rows by authenticated JWT subject. Temporary rows were rolled back.

### RLS policy optimization

The seven live policy sets were migrated from row-by-row `auth.uid()` evaluation to explicit `TO authenticated` policies using `(select auth.uid()) = user_id`. This preserves ownership semantics while avoiding repeated auth-function evaluation. Supabase Performance Advisor dropped from **28 Auth RLS Initialization Plan warnings** to **0** after the migration. The only remaining performance notice is an informational unused-index hint for `audit_events_user_device_idx`.

### Synchronized-data privacy controls

Desktop Privacy now includes:
- **Exportar datos de nube**
- **Borrar datos de nube**

Android Account now includes:
- **Export synchronized cloud data**
- **Delete synchronized cloud data**

Cloud export:
- requires authentication;
- paginates all seven RLS-visible synchronized tables;
- writes schema `ig-cleaner-cloud-export-v1`;
- excludes the original Instagram ZIP/JSON/HTML export.

Cloud delete:
- requires explicit confirmation;
- deletes only RLS-visible synchronized rows;
- deletes Focus items before batches;
- leaves the original Instagram export and independent local backups untouched;
- signs out afterward so automatic sync cannot immediately repopulate the cloud from local state.

## v120.35 version identity

Desktop visible UI: **v120.35**  
Android:
- package: `com.michelslab.igcleaner`
- versionCode: `12035`
- versionName: `120.35`

Debug remains isolated with the `.beta` application ID suffix.

The Desktop filename remains `ig_cleaner_pro_v120_27_synced_companion.html` intentionally because it is a stable packaging/state integration path, not the visible product version.

## Functional baseline preserved

Do not regress:
- Review = Following only;
- separate Mutuals / Followers-you-don't-follow / Pending workspaces;
- Focus 20 / 30 / 40;
- Revisar de nuevo 30;
- Double Check 30;
- Ver NO ME SIGUE revisados;
- cycle-reset controls;
- active batch recovery;
- module-scoped recent activity/sidebars;
- complete ZIP primary import;
- JSON/HTML evidence safeguards;
- Desktop ↔ Android normalized list/workspace/profile sync;
- Android-created Focus;
- Android system-bar inset handling;
- canonical Michel's Lab / IG Cleaner branding.

## Evidence still requiring a physical phone

Repository/CI can prove code, build, package, RLS and signing contracts. It cannot replace these target-phone checks:
- install/update signed v120.35 APK when released;
- cold launch;
- close/reopen session persistence;
- real Instagram ZIP chooser/import;
- Focus 20/30/40 with real usernames;
- batch recovery/completion;
- Android review → Desktop state round trip;
- cloud JSON export appearing in Downloads;
- cloud-delete confirmation UX and post-delete sign-out;
- Samsung system navigation/insets.

## Release rule

Do **not** publish v120.35 until Michel explicitly authorizes a release. Development/merge approval is not release authorization.
