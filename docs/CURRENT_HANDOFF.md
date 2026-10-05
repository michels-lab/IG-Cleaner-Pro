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

## Completed after LIMÓN

1. Removed duplicate Workspace packaging at the Gradle source-set level; Desktop is now the single packaged asset source.
2. Verified active Android About/version text already reports v120.29 Beta.
3. Generalized Android CI to `android-*` and added APK-level Workspace verification so duplicate/missing assets fail CI.

## Do next

1. Confirm CI passes for the single-asset hardening commits.
2. Install the newest v120.29 artifact on the target phone.
3. Validate Workspace, file picker/ZIP import, OTP persistence, Focus round-trip, Android→Desktop review sync, Audit origin and export-to-Downloads.
4. If validation passes: merge branch to main and publish pre-release v120.29.
5. If validation fails: fix on the same branch and record evidence in PROJECT_LOG before release.

## Do not regress

- Desktop JSON/import behavior.
- HTML partial-range evidence safeguards.
- Frozen Focus batch determinism.
- Review vs opened event separation.
- Device-origin audit trail.
- Raw Instagram exports remain local; Supabase sync is metadata/state.
