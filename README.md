# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.65 — official stable GitHub release, published October 26, 2026.** The [governed FINAL publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40416690593) finished **SUCCESS** on exact tagged commit `8570e12836afd3fde966eb8c590c7604aaf224a8`, publishing **12 checksum-bearing assets** after installed Windows public/Developer, production-signed Android public/Developer co-install, rendered Desktop/Android Home/About and release-feed integrity checks.

[**Download v120.65**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.65) · Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.65.exe` · Android `IG-Cleaner-Pro-Android-v120.65.apk` · Desktop `IG-Cleaner-Pro-Desktop-v120.65.html`. Independent Windows/Android Developer editions and portable ZIP are included.

**What changed:** [PR #249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249) prevents **new** Unfollow/Cancel batches from reopening profiles already visited, including safe no-click and uncertain outcomes. The target visit ledger is durable before Chrome navigation and independently enforced in UI and worker; it does not forge successful Unfollow results. The prior [v120.64](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.64) sequential one-profile-at-a-time default, explicit ten-tab legacy option, protected profiles, exact saved-cohort Continue, timestamps, Cancel, end-of-batch review and click WAL/no-replay protections remain.

**Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.** Owner reports actual Unfollow success with installed v120.64, but new-batch non-repetition and per-target Cancel Pending acceptance require installed v120.65 observation. Track [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). Windows Setup has SHA-256 integrity but no Authenticode signature.

**Current published stable: v120.65. Next reserved version: v120.66, not published.**

The next reserved development version **v120.66 is not authorized** for publication. The owner tests only officially published installers; new features require exact-source safety and distribution gates plus a separate official FINAL-only request. No RC/beta, silent update, Google Play deployment or owner Instagram action was performed from CI.

[Official v120.65 publication receipt](docs/GRANADA_V12065_FINAL_RECEIPT_2026-10-26.md). Historical receipts: [v120.64](docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md), [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md), [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md), [v120.62](docs/GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md), [v120.63](docs/GRANADA_V12063_FINAL_RECEIPT_2026-10-26.md).

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
