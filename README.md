# Instagram Cleaner Pro

## Release freeze — owner directive (2026-10-27)

**NO NEW OFFICIAL RELEASES while InstaCleaner remains unfinished, even when CI turns green.** The owner explicitly rejected the premature v120.71 FINAL release with unresolved real-account and dual-worker requirements. The existing v120.71 downloadable assets are historical; **v120.72 is reserved, NOT authorized**. Do not reinterpret the standing "Operación Granada" as permission to publish. Keep developing, testing and reviewing code, but **do not create a release, tag, RC, beta, or app update** before the owner confirms the complete product and explicitly authorizes a new release.

A fail-closed two-stage publisher gate now reads `release/release-readiness.json` and refuses publication unless the hold is explicitly lifted, the mandatory real-world acceptance checks are completed, all listed GitHub blocking issues are CLOSED and can be verified live, and an explicit owner release-tag-specific approval and evidence are recorded. Enforced in `.github/workflows/release.yml` before build and before `gh release create`. See `tests/test_release_readiness_gate.py`.

Open P0 work includes #164 (real Windows Unfollow/Cancel and owner Instagram acceptance), #172 (stale batches, Cancel/Unfollow regressions), #176 (genuine independently operated dual robot lanes) and #173 (Developer twins / owner validation), plus the named non-P0 acceptance issues listed in the gate. Do not mark these complete solely on mocked CI results.


## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.71 — official stable GitHub release, published October 28, 2026 (UTC).** [Download official v120.71 and 12 SHA-256-tracked assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.71) · [successful FINAL publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40608318126) · exact tagged commit `74a91104dd2f2f29c88b8abadbff76a6f3bfd466`. Installed Windows public/Developer Setups and production-signed Android public/Developer APKs passed required official release gates.

**New in v120.71:** Windows/Desktop has **two independently pinned InstaCleaner account tabs/windows** (open in tab / detach to window) and can request **two isolated persistent Chrome windows** for manual login to different Instagram accounts. Each owner/account Chrome login uses a different user-data folder, separate from exported robot data. The read-only Followers/Following bulk scanner offers owner-bound Recomendado/Más pausado/Personalizado safety controls and mandatory cooldown. **This is NOT two concurrent automated Unfollow/Cancel robots**: relationship-changing workers remain serial, and complete results with the owner's actual Instagram logins still need physical acceptance.

**Current published stable: v120.71. Next reserved version: v120.72, not published.**

v120.72 is **not authorized** for publication. Only a newly gated normal FINAL may be released after exact-source Windows/Android install, production signing, visual, SHA-256 and updater checks. No RC or beta.

**Previous official release:** [v120.70](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.70), published October 27, 2026 (UTC), official publisher 40555013922.

**New in v120.70 (Windows):** **Automations → Verify live Followers and Following** reads both lists using bulk same-origin authenticated Instagram JSON pages, **not individual target profile visits**, without a ZIP. Compared account identities use numeric Instagram IDs to handle username renames. Corrects the **real user's v120.69 250-page failure** with up to 200 requested members per JSON page, a 1500-page/100k-member bound, and fail-closed incomplete results. No automatic Unfollow, no cookie export, and no overwriting prior complete historical snapshots.

**Instagram safety controls (conservative app settings, not official Instagram limits):** wait 2.5 s between pages, 12 s after five pages and 90 s after 25; stop immediately upon 429/403/503 or `feedback_required`; honor a longer server `Retry-After` and impose at least 30 minutes of persistent shared-Chrome cooldown, including across workspaces, with 15 minutes between completed scans. Stop interrupts waits. These precautions do **not** guarantee freedom from restrictions.

The Instagram private list endpoint may reject reads; owner signed-in **real Instagram acceptance remains OPEN**. **Publication does not prove live Instagram Unfollow** or Cancel Pending succeeded on the owner's account. [Quickstart](docs/INSTACLEANER_V12070_LIVE_SCAN_QUICKSTART.md) · [v120.70 official receipt](docs/GRANADA_V12070_FINAL_RECEIPT_2026-10-27.md).

### Historical v120.66 publication and source notes

**v120.66 — official stable GitHub release, published October 26, 2026 (local; October 27 UTC).** [Governed FINAL publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40423739934) finished **SUCCESS** on exact tagged commit `af291cc6687f527a36fe1d64f31c08615fe216c0` with 12 SHA-256-verified assets, installed Windows public/Developer, production-signed Android public/Developer co-install, rendered Desktop/Android Home/About and verified official update feed.

[**Download v120.66**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.66) · Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.66.exe` · Android `IG-Cleaner-Pro-Android-v120.66.apk` · Desktop `IG-Cleaner-Pro-Desktop-v120.66.html`. Independent Windows/Android Developer editions and ZIPs are included in the same normal stable release.

**What changed:** [source PR #253](https://github.com/michels-lab/IG-Cleaner-Pro/pull/253) provides green confirmed OK, yellow Review and grey untouched profile rows in the end-of-batch dialog; **Open Review profiles · robot checks** safely inspects unresolved/untouched exact saved-cohort targets in read-only Chrome. A separate user-approved `Retry verified no-click` acts only on named accounts with a recent positive Following/Requested observation and *durable evidence of no earlier click*, never a possibly clicked/uncertain WAL result. [Governed release PR #254](https://github.com/michels-lab/IG-Cleaner-Pro/pull/254) passed all seven exact-head checks before merging.

**Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.** Real installed v120.65 Unfollow was reported working, but the owner saw the final target left unchecked when Chrome closed. Owner-installed v120.66 Review recovery and actual Cancel Pending need physical validation; see [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). No live relationship action or Instagram account login occurred in CI. Windows Setup has SHA-256 integrity but no Authenticode signature.

**Historical status at the time of the v120.66 receipt (superseded by the current release above).**

The next reserved development version **v120.67 is authorized ONLY for normal FINAL publication after exact-source installed Windows, production-signed Android public/Developer, rendered visual, SHA-256 and updater-feed gates pass**; it is NOT published yet. The owner tests only officially published installers; source tests cannot replace actual account acceptance. No RC/beta, silent installation or Google Play deployment.

[Official v120.66 publication receipt](docs/GRANADA_V12066_FINAL_RECEIPT_2026-10-26.md). Historical receipts: [v120.65](docs/GRANADA_V12065_FINAL_RECEIPT_2026-10-26.md), [v120.64](docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md), [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md), [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md), [v120.62](docs/GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md), [v120.63](docs/GRANADA_V12063_FINAL_RECEIPT_2026-10-26.md).

## Features

- **Switch IG Cleaner accounts** with a separate Desktop **Cambiar usuario** / Android **Switch account** action beside Sign out; switching app logins does not delete the account's Instagram profiles or local reviews. Desktop also displays full @handles and has **Actualizar perfiles** to refresh the cloud registry.
- Manage **multiple independent Instagram profiles under one IG Cleaner login** on Desktop and Android. Switch between @profiles without mixing Following, Followers, Pending, Focus, Double Check or review history; existing v120.38 data stays in the original `legacy` workspace.

- Import Instagram Following, Followers and Pending Requests in supported export ZIP / JSON / HTML formats, with evidence safeguards for ambiguous exports.
- Review Queue, Mutuals, Followers-you-don't-follow and Pending workspaces, with 20/30/40-profile Focus batches.
- Recheck 30, Double Check 30, review/protection history, active batch recovery, filters, live activity and local backup/export.
- Optional authenticated **Supabase sync of supported normalized lists, review/Focus states and audit data** across Desktop and Android.
- Cloud data export and deletion controls, separate from local export files.

## Data boundary

The **original Instagram export is processed locally**, and raw Instagram ZIP/JSON/HTML files are **not uploaded to the sync backend**. If cloud sync is enabled, supported derived list and review records are transmitted to Supabase for cross-device continuity. It is therefore inaccurate to describe the entire product as having no backend. Local operation and import do not require Instagram login. Review state may exist both locally and, if synchronized, in the user's cloud account. See [Privacy](docs/PRIVACY.md) and [Sync notes](README_SYNC.md).

## Run or develop

For Desktop, download the standalone `.html` asset from the latest GitHub release and open it locally. Developers can also use `index.html`; check the distribution manifest for the supported release artifact. For Android, install the signed APK supplied with the release. Keep app signing identity, browser state keys and Focus history compatible across upgrades.

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. 

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
