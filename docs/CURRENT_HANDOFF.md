# Current Handoff — Instagram Cleaner Pro

Updated: **2026-10-06**
Trigger: **LIMÓN**

## Authoritative candidate

Continue from:

`release/v120.34`

Current validated implementation head before this handoff-only documentation update:

`da08628a068dde4e2716fe622741037ad0d68a02`

The divergent branch `release-v120.34` is historical/superseded and **must not be used for publication**.

## Release authority

- Next release: **v120.34**
- Channel: **stable GitHub release**
- GitHub prerelease: **false**
- Authority: `release/distribution-manifest.json`
- Automatic publication: **disabled**
- Publication from this work: **not authorized / not performed**
- Do not infer another version from old tags, branch names or historical workflows.

A historical publisher on `release-v120.34` is unsafe for stable Android publication because it attaches a debug/`.beta` APK. Do not reuse it unchanged.

## What is now fixed

### Candidate/version consistency
- `release/v120.34` is based on current `main` and is ahead with the v120.34 work.
- Android versionCode/versionName: **12034 / 120.34**.
- Desktop visible title, rail badge, About and Version dialog report **UI v120.34**.
- Old v120.26/v120.27 visible release labels were removed without renaming historical storage/schema identifiers.

### Canonical product identity
- Official product identity: **three stacked layers/diamond planes + restrained upper-right sparkle**.
- Old rounded-square blue/cyan `IG` monogram is legacy/rejected.
- Canonical child SVGs match Michel-Software-Standards.
- Desktop About uses real vendored canonical assets:
  - `desktop/assets/michel_duarte_avatar.jpg`
  - `desktop/assets/michels-lab/official-lockup.png`
- Portrait git blob SHA: `18fe1a68722850c3d8f918dc0799f46ffeb6dbaf`
- Michel's Lab lockup git blob SHA: `7fd48093968b31ddacd3098f5b15d962de580652`
- Embedded base64 portrait was removed.

### Desktop ↔ Android review-state continuity
- Restored the full `igc-v12030-supabase-sync-js` bridge to the Desktop candidate.
- Restored `normalizeLegacyReviewState()`, `pushWorkspaceState()`, `list_snapshots` and `workspace_state` synchronization.
- Historical Desktop-reviewed profiles can be normalized and published instead of being silently treated as unresolved on Android.
- CI now fails if this sync bridge disappears again.

### Android repair
- Restored resource/dependency parity for the current native shell.
- Fixed missing `bg_badge`, Home/Review/Focus/Activity/Profile navigation resources and SwipeRefreshLayout dependency.
- Android compiles again.
- Packaged Workspace includes the external About assets and no duplicate legacy Workspace.

### Android-created Focus
Android can create Focus without Windows/Desktop.

Modules:
- Review / no te siguen
- Mutuals
- Followers que tú no sigues
- Pending Requests

Sizes:
- 20
- 30
- 40

The creator refreshes synchronized relationship/review state, excludes reviewed/protected/active-snooze/already-batched usernames, freezes the selection in Supabase, and refuses unsafe creation if historical review state is unavailable.

### Privacy surface
- Added `docs/PRIVACY.md` as the centralized local-first/data-handling contract.
- Desktop About now exposes a dedicated **Privacidad** dialog.
- The UI explicitly distinguishes raw local Instagram exports from normalized synchronized state and does not falsely claim a one-click cloud-data deletion control.
- Added a CI privacy contract.

### Shared governance
- Michel's Lab shared child-agent contract synced to **2026-10-06.5** in `AGENTS.md` and `.github/copilot-instructions.md`.

## Verified CI evidence

Final repository validation for the consolidated candidate:
- GitHub Actions run `37562844481` — **SUCCESS**
  - Desktop HTML/persistent-state contract — PASS
  - sanitized Instagram fixture — PASS
  - canonical product/About branding — PASS
  - privacy/data-handling contract — PASS
  - Android Focus/inset regression contract — PASS
  - distribution manifest — PASS
  - Android build — PASS
  - embedded Workspace/package verification — PASS
- GitHub Actions run `37562748629` — Android companion with privacy/About changes — **SUCCESS**.
- GitHub Actions run `37562402633` — Android companion with restored full Desktop sync bridge — **SUCCESS**.
- GitHub Actions runs `37562024462` / `37562024494` — full CI + companion after restoring Android-created Focus — **SUCCESS**.

Evidence status: **verified in repository CI**. Physical-device/provider behavior remains a separate manual gate.

## Manual validation still pending

Do not claim these as completed until tested on the real phone/desktop account:
1. cold launch and physical rendering/insets;
2. account/session persistence after close/reopen;
3. real usernames in Review / Mutuals / Followers / Pending;
4. create Focus 20/30/40 directly on Android;
5. reopen/complete Android-created batches;
6. Android review → Desktop state round-trip;
7. audit device provenance;
8. export/file chooser behavior on device.

## Desktop distribution

Desktop About now depends on canonical external assets, so release Desktop as the bundle declared in `release/distribution-manifest.json`:

`IG-Cleaner-Pro-Desktop-v120.34.zip`

with:
- `IG-Cleaner-Pro.html`
- `assets/michel_duarte_avatar.jpg`
- `assets/michels-lab/official-lockup.png`

Do not publish a lone HTML file that drops these assets.

## Next safe work

1. Run the manual phone/desktop round-trip above.
2. Decide/sign the real Android stable release artifact; never present a debug/`.beta` APK as stable.
3. Only after explicit user authorization, implement/use the governed v120.34 publisher.
4. Merge the validated candidate to `main`.
5. Retire the historical `release-v120.34` branch/workflow path after no unique evidence is needed from it.
