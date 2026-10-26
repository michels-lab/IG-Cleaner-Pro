# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.63 — official stable GitHub release, published October 26, 2026.** [Governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40394937018) completed **SUCCESS** for exact tagged source `cb47df2eeda2f158df408e7a57dbda84600b622d`, with 12 published checksum-verified assets, installed Windows public/Developer checks, production-signed Android public/Developer co-install, Desktop/Android rendered UI and release-feed verification.

[**Download v120.63**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.63) · Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.63.exe` · Android `IG-Cleaner-Pro-Android-v120.63.apk` · standalone Desktop `IG-Cleaner-Pro-Desktop-v120.63.html`. Optional Windows portable ZIP and separate Developer editions are available from the same release.

**Changes:** [#241](https://github.com/michels-lab/IG-Cleaner-Pro/pull/241) reduced repeated signed-in owner-profile navigation using short-lived, session-bound owner proof; [#242](https://github.com/michels-lab/IG-Cleaner-Pro/pull/242) separated the visible 20-person batch/1-minute rest from the former implicit 20-visits-per-hour limit. An explicit 120-visits/60-minute safety budget and between-profile spacing still apply. The previously shipped [v120.62](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.62) saved-10/new-40 decision, action journal, cancel and end-of-batch review remain available.

**Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.** Independent real-account acceptance remains open in [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172), [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). Windows Setup has SHA-256 integrity but no Authenticode signature. No RC/beta or Play publication.

**Current published stable: v120.63. Next reserved version: v120.64, not published.**

The next version is not authorized; the owner tests only officially published installers. Source changes after this tag, including any fixes under [PR #245](https://github.com/michels-lab/IG-Cleaner-Pro/pull/245), are not part of the v120.63 binary. No source-only test proves real Instagram acceptance.

[Official v120.63 publication receipt](docs/GRANADA_V12063_FINAL_RECEIPT_2026-10-26.md). Historical receipts: [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md), [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md) and [v120.62](docs/GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md).

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
