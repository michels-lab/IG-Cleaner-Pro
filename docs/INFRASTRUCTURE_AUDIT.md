# IG Cleaner Pro — Infrastructure & Privacy Audit

Last reviewed: **2026-10-05**

## Current architecture
- **Local-first import + opt-in authenticated sync metadata.**
- Instagram export ZIP/JSON/HTML files are parsed locally in Desktop/Android Workspace.
- Raw Instagram export contents are not part of the current Supabase sync contract.
- Supabase is used for cross-device workflow metadata/state.
- Android v120.29 packages the official Desktop engine and also provides native Focus/Audit/Account surfaces.

## Supabase implementation
Current synchronized domain:
- devices;
- Focus batches;
- Focus batch items;
- audit/review events;
- projected profile review state.

Authentication:
- email OTP;
- user-facing clients use only the publishable key;
- Row Level Security is required on exposed user tables;
- privileged/service-role/database/SMTP credentials must never be shipped in the clients.

## Privacy boundary
The primary privacy property remains: **the raw Instagram export stays on the user's device unless a separate future upload/backup feature is explicitly designed and enabled.**

Cross-device sync currently moves workflow metadata such as which profile was opened/reviewed, when, from which device, and which Focus batch it belongs to.

The app must not silently broaden this boundary from review metadata to raw social-export storage.

## Android distribution state
- v120.28 is the current published Android beta release.
- v120.29 full-workspace Android is build-valid on branch `android-full-workspace-v120.29`.
- GitHub Actions run `37388962937` passed.
- v120.29 is not considered released/production-ready until target-phone validation completes.

## Remaining infrastructure work
1. Complete v120.29 target-phone validation and publish the release only after the real-device gate passes.
2. Add deterministic Desktop/browser regression CI for ZIP/HTML/JSON import and evidence semantics.
3. Define a durable update path for both Desktop HTML and Android app while preserving local state.
4. Add centralized in-product privacy/delete/export controls for synchronized metadata.
5. Document database schema/version migrations and local browser/Android storage migrations.
6. Add automated RLS isolation tests proving one authenticated user cannot read another user's rows.
7. Reconcile About/version identity across Desktop, Android and GitHub Releases.
8. Keep sanitized fixtures in Git; never commit real Instagram exports or secrets.

## Secret rule
Allowed in shipped clients:
- public Supabase Project URL;
- Supabase publishable key.

Not allowed in shipped clients or Git:
- service-role/secret Supabase keys;
- database password;
- SMTP password/API key;
- refresh/access tokens;
- signing passwords/private signing keys;
- private GitHub credentials.
