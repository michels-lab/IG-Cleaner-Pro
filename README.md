# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.60 — official stable GitHub release, published October 23, 2026.** The [governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/39983124380) completed **SUCCESS** on exact source `457506c814c64f4ee31e5cbf0c7fbf6d472fa1f9`, producing 12 official assets with SHA-256 verification. [Full independent release receipt](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md). The [earlier v120.59 receipt](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md) remains historical evidence.

[**Download v120.60**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.60) · Windows normal Setup `IG-Cleaner-Pro-Windows-Setup-v120.60.exe` · Android signed `IG-Cleaner-Pro-Android-v120.60.apk` · Desktop standalone `IG-Cleaner-Pro-Desktop-v120.60.html`. Optional portable Windows ZIP, separate Developer installers, Developer Android APK and checksums are on the same release page.

**What changed in v120.60:** normal Windows robot now offers explicit **Cancel batch** while paused/waiting, stops future target actions after the in-flight operation finishes, releases the job for a different task, shows one prominent actual current-job state/countdown, adds **journal action date/time**, and prompts an end-of-batch **profile-by-profile manual results review**. Unacted members of the saved 40-target cohort remain eligible; protected and uncertain-click records are not erased or automatically retried. v120.59 introduced the owner-supplied exact-ID GraphQL Unfollow transport, retained in v120.60.

**Publication does not prove live Instagram Unfollow or Cancel Pending success.** Installed Windows/Android and offline Chromium tests passed, but **real account Unfollow/Cancel Pending success is not yet verified**. Owner acceptance stays open in issues [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164). Source inspection found avoidable extra own-profile visits; follow-up [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230) tracks deduplication without weakening owner identity security. No RC, beta or Google Play publication; Windows Setup has SHA-256 integrity but not Authenticode signing.

**v120.61 is reserved for development only (not published or authorized).** The owner tests only officially published installers; Windows updater reads official GitHub stable releases and never installs silently.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Current published stable: v120.60. Next reserved version: v120.61, not published.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
