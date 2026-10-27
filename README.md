# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.70 — official stable GitHub release, published October 27, 2026 (UTC).** [All 12 verified release assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.70) · [successful governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40555013922) · exact tagged commit `55a9f1d0865c4280d9ef0f9866b51476f8b8c786`. Includes the normal and Developer Windows installers, signed Android public and Developer APKs, and standalone Desktop HTML/ZIP.

**Current published stable: v120.70. Next reserved version: v120.71, not published.**

**New in v120.70 (Windows):** `Automations → Verify live Followers and Following` reads Followers and Following with **read-only, authenticated same-origin JSON list pages**; it does not open each profile individually or run Unfollow. [P0 fix #270](https://github.com/michels-lab/IG-Cleaner-Pro/pull/270) replaces the old 250-page cutoff with a bounded 1500-page/100k-unique-member collector, requests up to 200 accounts per page, checks complete pagination and compares stable numeric Instagram IDs across username changes. [FINAL release #271](https://github.com/michels-lab/IG-Cleaner-Pro/pull/271) adds conservative safety controls: 2.5-second pacing, 12-second breaks every five pages, 90-second breaks every 25, interruptible Stop, no automatic retry after 429/403/503/`feedback_required`, server `Retry-After` with at least 30 minutes of Chrome-wide protective cooldown, and at least 15 minutes before a repeat scan after success. No proxy rotation, challenge bypass or claim of guaranteed account safety.

**Real-account acceptance is still open:** v120.69 failed in the owner's Windows screenshot because the scanner hit the 250 JSON page cap. v120.70 corrects that source limit and passed installed Windows public/Developer, signed Android twin, Chromium and visual release tests. However, Instagram's undocumented private list endpoint may still refuse or limit access; CI did **not** obtain the owner's real Followers/Following or validate actual counts. No incomplete snapshot can become a false negative; the last complete historical snapshot is preserved. **Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.**

[Official v120.70 release receipt](docs/GRANADA_V12070_FINAL_RECEIPT_2026-10-27.md) · [Windows bulk-list quickstart](docs/LIVE_FOLLOWERS_WINDOWS_QUICKSTART.md).

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
