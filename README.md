# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.61 — official stable GitHub release, published October 23, 2026.** The [governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40017257499) completed **SUCCESS** on exact source `148074c870a11068d809e1a12ba0384dbe6e4c3f`, producing 12 assets, including public/Developer Windows and signed Android twins, visual and SHA-256 checks.

[**Download v120.61**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.61) · Windows normal Setup `IG-Cleaner-Pro-Windows-Setup-v120.61.exe` · Android signed `IG-Cleaner-Pro-Android-v120.61.apk` · standalone Desktop `IG-Cleaner-Pro-Desktop-v120.61.html`.

**What changed in v120.61:** clearer selection versus actual Chrome worker in Automation, reduced repeat owner-profile visits in Followback and final-state checks, and an optional read-only exact-owner full Followers/Following list evidence source. These changes preserve the existing Profile Counts numerical scraper, safe Cancel batch, owner-specific action journal, original cohorts and protected profiles.

**v120.62 reserved for development and fully gated publication.** Fixes an owner-reported `SAVED COHORT: 10; NEW SELECTED SIZE: 40` dead end: two explicit, safe options to continue the ten or preserve them in archived local history and prepare a fresh forty. Neither planning nor archiving clicks Instagram or marks old profiles Reviewed. Source is merged and automated Windows/Chrome, Android and desktop QA passed; this is **not yet an official release until the governed publisher passes**.

**Publication does not prove live Instagram Unfollow or Cancel Pending.** The owner tests only officially published installers; no branch preview is real account acceptance. Earlier verified publication receipts remain in [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md) and [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md).\n\n**Live Instagram acceptance remains open:** published executable/Chromium tests do not prove that the owner's real account performed Unfollow or Cancel Pending. See [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172), [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). No beta/RC or Google Play distribution. Windows Setup has checksums, not Authenticode signing.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Current published stable: v120.61. Next reserved version: v120.62, not published.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
