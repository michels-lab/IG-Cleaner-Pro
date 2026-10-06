# Current Handoff — IG Cleaner Pro

Updated: **2026-10-05**
Trigger: **LIMÓN**

## Resume here

Active work is **Android v120.29 full workspace**, branch:

`android-full-workspace-v120.29`

Latest validated CI:
- GitHub Actions run `37390702783` — **SUCCESS**.
- APK: 6,880,202 bytes.
- APK SHA-256: `bc706c76857a18a5fdfce3ffafa9a3edfe01188c952edc4c57667a86529397d9`.
- APK contains exactly one embedded Workspace asset.

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

1. Install the validated v120.29 APK from run `37390702783` on the target phone.
2. Validate Workspace, file picker/ZIP import, OTP persistence, Focus round-trip, Android→Desktop review sync, Audit origin and export-to-Downloads.
3. If validation passes: merge branch to main and publish pre-release v120.29.
4. If validation fails: fix on the same branch and record evidence in PROJECT_LOG before release.

## Do not regress

- Desktop JSON/import behavior.
- HTML partial-range evidence safeguards.
- Frozen Focus batch determinism.
- Review vs opened event separation.
- Device-origin audit trail.
- Raw Instagram exports remain local; Supabase sync is metadata/state.
