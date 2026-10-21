# GRANADA P0 — Real GitHub Desktop screenshot artifact layout blocked official v120.55

Date: 2026-10-21. Source release request commit: `f3894056f22312519d67b79ad2385997107aa040`. Governed workflow: [run #39626248768](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39626248768).

## Real observed failure — no release published

- Owner authorized a final **stable** v120.55 by GRANADA; previously PR #188 integrated after 5/5 exact-head QA, v120.55 source/signing version and publisher Android Developer gate were already integrated.
- The real release's `rendered-ui-qa` verified exact-commit **Android** runtime screenshots and downloaded exact-commit **Desktop** Chromium artifact. But the second Desktop validator failed before inspecting its eight screenshots with `FileNotFoundError: desktop-visual-evidence/manifest.json`.
- Root cause: `desktop-rendered-ui.yml` uploads two sibling directories `artifacts/desktop-visual/` and `artifacts/automation-center/`. A downloaded multi-folder artifact can retain `desktop-visual/manifest.json` beneath the download directory, while `release.yml` assumed that `manifest.json` always sits at its root. It is a **publisher wiring error**, not evidence that the current screenshots are valid; the strict screenshot checks did NOT pass and the old release must remain blocked.

## Targeted fail-closed fix

- New `tools/resolve_desktop_visual_artifact_dir.py` selects precisely one **complete** evidence directory among flat and `desktop-visual/` layouts, requires BOTH `manifest.json` and `michelslab-manifest.json`, rejects symlinks, missing manifests and ambiguous duplicate candidates.
- `.github/workflows/release.yml` rebuilds the exact-source standalone HTML next to that verified directory, then runs the **unchanged** strict screenshot SHA, PNG, viewport, scene, source SHA, HTML digest and visual-release-gate checks. The helper never invents screenshots or accepts a missing manifest.
- Five fixture tests prove flat/nested layouts, missing/partial artifacts, contradictory manifests and symlink exclusion; `.github/workflows/ci.yml` runs them; `tests/release-publisher-contract.py` makes the resolver and dynamic artifact root mandatory for future releases.
- Only release evidence wiring and tests/docs change. No action worker, journal, persistent state, Instagram session, release version/keystore, request authorization or production data change.

## Continuation and exact requirement

1. Pass PR exact-head CI, merge without colliding with active PR #143.
2. Reissue the **same final-stable v120.55** request on a new exact main SHA to force its official publish workflow to rerun all real Android/Windows/Developer and downloaded Desktop evidence checks. The original `f3894056` release attempt with failed `rendered-ui-qa` must never be treated as published, nor promoted by reusing stale screenshots from another SHA.
3. Only after successful publication verify the official GitHub release is neither draft nor prerelease, contains Desktop standalone/ZIP, Windows Setup/Developer Setup, Android stable/Developer APK and SHA256SUMS; then update version policy, request status, README, update guide, logs with actual evidence.
4. Owner physical real Instagram Unfollow/Cancel and saved 40-profile batch acceptance remains open issue #172/#164 and is distinct from the official CI acceptance. No Release Candidates.

