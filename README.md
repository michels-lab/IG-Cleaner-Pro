# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.65 — official stable GitHub release, published October 26, 2026.** [Governed FINAL publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40416690593) finished **SUCCESS** for exact tagged source `8570e12836afd3fde966eb8c590c7604aaf224a8`, with 12 published SHA-256-verified assets, installed Windows public/Developer, production-signed Android public/Developer emulator co-install, Desktop/Android Home/About screenshots and official updater-feed validation.

[**Download v120.65**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.65) · Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.65.exe` · Android `IG-Cleaner-Pro-Android-v120.65.apk` · standalone Desktop `IG-Cleaner-Pro-Desktop-v120.65.html`. Independent Windows/Android Developer editions and Windows portable ZIP are on the same official release.

**New batch fix:** [merged PR #249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249) prevents reopening already checked profiles when starting a NEW Unfollow or Cancel Pending batch. The new owner/account/task-scoped visit ledger durably reserves a profile before navigation, preserves original no-replay click evidence and excludes previously visited profiles (even safe no-click reviews). Continue an old explicitly saved incomplete cohort remains a separate owner choice; no old protected profiles, click WAL or review history is deleted.

**Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.** The owner reported real Unfollow working on v120.64 but still experienced repeat visits between cohorts; the **new v120.65 behavior has not yet been accepted on the owner's physical Windows session**. Real account follow-up remains open [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172), [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). Windows Setup has verified SHA-256 integrity, not Authenticode signing. No RC/beta or Play release.

**Current published stable: v120.65. Next reserved version: v120.66, not published.**

The next reserved development version **v120.66 is not authorized** and has not been published. The owner tests only officially published installers. Do not treat source tests, signed APK emulators or read-only status as proof Instagram accepted relationship changes; no automated CI login or relationship click was attempted.

[Official v120.65 publication receipt](docs/GRANADA_V12065_FINAL_RECEIPT_2026-10-26.md). Historical receipts: [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md), [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md), [v120.62](docs/GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md), [v120.63](docs/GRANADA_V12063_FINAL_RECEIPT_2026-10-26.md), [v120.64](docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md).

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
