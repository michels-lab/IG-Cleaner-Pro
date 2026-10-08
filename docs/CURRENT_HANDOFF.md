# Current Handoff — Instagram Cleaner Pro

Updated: 2026-10-08; trigger: LIMÓN.

## v120.36 — approved logo and visual QA candidate

- User expressly instructed **correct remaining problems and release v120.36**. Preparing from PR #35; do not claim a release until Github Releases contains signed APK + Desktop ZIP and all checks pass.
- PR #29 fixed the Android About zero-width author/studio panel. PR #31 redesigned compact About to keep both identities + five social links completely visible; real emulator screenshot test rejected a 70%-visible Email button and passed after correction.
- PR #32 removed the pre-release human reviewer bottleneck as explicitly requested, retaining fail-closed automatic QA. PR #33 prepared Android/Desktop v120.36 version.
- PR #35 imports the **exact original** 1,559,781-byte first chosen profile-card/cyan-orbit/gold-sparkle PNG into IG Cleaner and adds derived lossless launcher/Desktop/release assets. Same original is activated in the Michel's Lab master manifest through PR #30.
- Android **Home and About** now have actual installed-app compact/wide screenshots with APK and source SHA. Desktop **Home and About** have actual Chromium compact/wide screenshots, native asset checks and exact HTML hash. Governed publisher verifies both on exact release-request source SHA.
- Keep production signing identity FINAL-9999 and stable package `com.michelslab.igcleaner`. Do not silently re-key or change app ID.
- Remaining **physical phone** validation of update-over-old-signed-release, Focus, Instagram export ZIP import and live cloud sync is [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24), distinct from CI.
- Public stable was v120.35 before this release work; next release target is v120.36. After publication reconcile release manifest and consume authorization, then append final job and asset proof. Never infer that GitHub release succeeded just because CI did.
- Permanent source log: `PROJECT_LOG.md`. Last published signed cert SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`.

## Historic handoff archive

# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-08**
Trigger: **LIMÓN**

## v120.36 ready in main — not yet published

- **Current main HEAD:** `b99b2357295d124fa783fa555f9793e87028899a`; Android `versionName=120.36`, `versionCode=12036`; matching Desktop development version and unchanged FINAL-9999 certificate.
- **PR #29 (merged):** fixed zero-width native Android About author/Michel's Lab panels; implemented installed-APK Espresso actual-view and screenshot tests.
- **PR #31 (merged):** redesigned compact About as two side-by-side identity sections and five contact links in two columns. A strict complete-visibility assertion rejected clipped Email (70% visible); after correction, **both compact and wide emulator tests passed**. Actual screenshot archive: [About v120.36 visual QA](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37808417135). All five contact links are visible in the initial compact screenshot.
- **PR #32 (merged):** release publishing requires **automated** exact-commit `rendered-ui-qa` and APK screenshot integrity checks. No manual/protected human-review queue is required, consistent with the user's instruction to inspect the finished release afterward.
- **PR #33 (merged):** Android and Desktop dev version, signing metadata and release notes prepared for v120.36. [Desktop/Android/Supabase CI](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37810464858) and [Android emulator About QA](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/37810464913) are both **SUCCESS**.
- **Current public stable:** v120.35. **Next governed publication candidate:** v120.36, `authorized=false`; no release requested or published as part of these PRs.
- **Remaining:** exact original Option 1 logo PNG not yet uploaded to master; approved 64px preview is not suitable as official production asset ([issue #30](https://github.com/michels-lab/IG-Cleaner-Pro/issues/30)). Real Samsung upgrade/Focus/import/cloud roundtrip acceptance remains [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24); broader Home/Desktop screenshot coverage remains [issue #28](https://github.com/michels-lab/IG-Cleaner-Pro/issues/28).
- Do not claim logo migration, physical-phone validation or GitHub v120.36 release as done until evidence exists.

## Current authoritative release state

- Published stable GitHub Release: **v120.35**, non-prerelease; five assets (signed Android APK, Desktop ZIP, logo, Privacy, SHA256SUMS).
- Publisher run: **37737077156 — SUCCESS** on commit `0e4b0c3d5b803436fd453c23e51dce1505871d8a`.
- FINAL-9999 Android signing continuity verified; package `com.michelslab.igcleaner`, versionCode `12035`, versionName `120.35`.
- Generic publisher: `.github/workflows/release.yml`.
- Release authorization was consumed and closed in governance; next governed release target: **v120.36**, not yet authorized.
- v120.35 implementation merged to `main` via PR #20 and responsive About finalization via PR #23.
- Physical-phone acceptance remains open as [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24). GitHub release is published; this does not constitute Google Play publication or physical-device validation.
- Development and publication state must be independently checked against the manifest, current main SHA, current CI and GitHub Releases.

---

## Historical handoff (2026-10-07; preserved for audit)


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


## Current validation blocker

PR **#20** remains open, mergeable and intentionally Draft.

GitHub Actions run **37702842845** on head `e5a49aa55053599636a7c55d91df7b39df7207b9`, triggered by marking PR #20 Ready for review, created all three jobs and terminated them before any runner step or log existed:
- Desktop local-app contract — pre-run failure;
- Android build + embedded Workspace — pre-run failure;
- Supabase RLS isolation — pre-run failure.

Every failed job reports `steps: []` and no log blob exists, so this is not evidence of an application/test assertion failure. GitHub's public status page reports Actions operational after today's service incidents, but the repository runner-start failure remains unresolved and its exact account/platform cause is not exposed through the available connector APIs. PR #20 was returned to Draft immediately after this probe. Draft PR jobs are now server-side skipped, preventing further runner/minute waste until the gate is intentionally retried.

Direct evidence on the exact current branch:
- Desktop inline JavaScript syntax: **16/16 PASS**;
- duplicate static DOM IDs: **0**;
- v120.35/version/privacy/release/RLS static sweep: **PASS**;
- corrected targeted governance/privacy/RLS sweep: **11/11 PASS**;
- Android Java/Gradle delimiter structure: PASS;
- modified Android XML structure: PASS;
- live Supabase optimized RLS migration: APPLIED;
- live two-user RLS sweep across all seven synchronized tables:
  - each user sees only **1 own row** per seeded table;
  - foreign UPDATE affected **0 rows** on all seven tables;
  - foreign DELETE affected **0 rows** on all seven tables;
  - own authenticated INSERT succeeded;
  - test transaction rolled back;
- Supabase Security Advisor: no RLS exposure finding; one separate Auth warning for leaked-password protection being disabled;
- Supabase Performance Advisor: **0 Auth RLS Initialization Plan warnings**; one informational unused-index notice remains.

These checks do not replace Android `assembleDebug` / embedded Workspace packaging or the full same-SHA CI run. Do not merge PR #20 until executable CI resumes and passes.
