# IG Cleaner Pro — Infrastructure & Privacy Audit

Last reviewed: **2026-10-06**

## Current architecture
- **Local-first import + opt-in authenticated sync metadata.**
- Instagram export ZIP/JSON/HTML files are parsed locally in Desktop/Android Workspace.
- Raw Instagram export contents are not part of the current Supabase sync contract.
- Supabase is used for cross-device workflow metadata/state.
- Android v120.34 packages the Desktop engine for advanced tools and provides native Home / Review / Focus / Activity / Profile surfaces.

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

Cross-device sync moves normalized list snapshots plus workflow state such as which profile was opened/reviewed, when, from which device, review/protection/snooze state, and which Focus batch it belongs to.

The app must not silently broaden this boundary from review metadata to raw social-export storage.

## Android distribution state
- GitHub release **v120.34** is published as a normal release (`prerelease=false`).
- Final publisher run **37574744462** completed **SUCCESS**.
- The stable Android artifact `IG-Cleaner-Pro-Android-v120.34.apk` is attached to the release.
- The Android implementation is versionCode **12034** / versionName **120.34**.
- Debug builds remain `com.michelslab.igcleaner.beta` / `120.34-beta`.
- Stable builds use `com.michelslab.igcleaner` and the persistent production signing identity recorded in `release/android-signing.json`.
- Production certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`.
- Certificate validity: **9999-12-31**.
- The four Android signing secrets are configured in GitHub Actions and were successfully consumed by the final publisher.
- No private signing material is stored in Git.
- The release workflow verifies package/version/signature before publication.
- Physical-device validation remains a separate evidence gate and must not be inferred from CI.

## Remaining infrastructure work
1. Install/test the signed APK on the target phone and record cold-launch, persistence, Focus and round-trip evidence.
2. Add centralized in-product privacy/delete/export controls for synchronized metadata.
3. Add automated RLS isolation tests proving one authenticated user cannot read another user's rows.
4. Generalize the release publisher for v120.35+ instead of keeping version-specific release automation.
5. Keep sanitized fixtures in Git; never commit real Instagram exports or secrets/signing material.

Canonical privacy reference: `docs/PRIVACY.md`.

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

## 2026-10-06 — CI / update / migration hardening

Implemented the missing deterministic repository gates:
- unified Desktop + Android CI;
- sanitized ZIP fixture validation;
- Desktop syntax/workflow/state compatibility contract;
- distribution manifest with browser-state schema 1;
- explicit migration/rollback rules;
- explicit-release publication policy.

Persistent browser state is now formally treated as a compatibility surface. Existing localStorage keys and IndexedDB `ig_cleaner_pro_history` version 1 may not be renamed/reset without an explicit migration and regression evidence.

Version-specific release workflows were separated from ordinary `main` validation so CI success cannot silently publish a release. Android GitHub distribution is now live with persistent production signing. Google Play publication remains separate and still requires real-device/store validation.

