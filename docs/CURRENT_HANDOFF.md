# Current Handoff — IG Cleaner Pro

Updated: **2026-10-05**
Trigger: **LIMÓN**

## Resume here

Active work is **Android v120.29 full workspace**, branch:

`android-full-workspace-v120.29`

Latest validated CI:
- GitHub Actions run `37388962937` — **SUCCESS**.

## Product direction

Android must provide the breadth of Desktop, not a reduced companion.

Implementation choice:
- package the official Desktop HTML as the Android **Workspace**;
- keep native **Focus**, **Audit** and **Cuenta** for mobile-specific UX.

## Do next

1. Remove obsolete duplicate Android workspace asset if present.
2. Update remaining v120.28 About/version text to v120.29.
3. Generalize branch-specific Android CI trigger.
4. Install the newest v120.29 artifact on the target phone.
5. Validate Workspace, file picker/ZIP import, OTP persistence, Focus round-trip, Android→Desktop review sync, Audit origin and export-to-Downloads.
6. If validation passes: merge branch to main and publish pre-release v120.29.
7. If validation fails: fix on the same branch and record evidence in PROJECT_LOG before release.

## Do not regress

- Desktop JSON/import behavior.
- HTML partial-range evidence safeguards.
- Frozen Focus batch determinism.
- Review vs opened event separation.
- Device-origin audit trail.
- Raw Instagram exports remain local; Supabase sync is metadata/state.
