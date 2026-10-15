# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.47 — current official stable GitHub release (published October 15, 2026).** [Download v120.47](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.47).

| Platform | Primary release file | Notes |
| --- | --- | --- |
| Windows installed app + robots | `IG-Cleaner-Pro-Windows-Setup-v120.47.exe` | Standard per-user installer, Start menu, optional shortcut, uninstall, integrated Automation Center and consent-gated updater. |
| Desktop browser (Windows/macOS/Linux) | `IG-Cleaner-Pro-Desktop-v120.47.html` | Standalone local HTML. No Windows-only browser robot in this file. |
| Android | `IG-Cleaner-Pro-Android-v120.47.apk` | Production-signed APK with original package/signing continuity. The Windows robot does not run on Android. |
| Legacy portable Windows robot bundle | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.47.zip` | Optional portable compatibility delivery; the native Setup is preferred. |
| Desktop optional ZIP | `IG-Cleaner-Pro-Desktop-v120.47.zip` | Browser workspace and separate branded assets. |

**Next development candidate: v120.48 (not published).** Its source contains fixes for successive Cancel Pending Requests batches, imports, stuck Focus previews and ambiguous post-click verification. GitHub source changes are **not** automatically installed in the public v120.47 Setup. A separately authorized release and real-owner acceptance are still required.

The v120.47 Windows app contains a checked update feed, explicitly approved SHA-256-verified Setup download, manual installer launch, and restore-point creation before upgrade. It also includes oldest-first repeat Profile Counts audits with append-only per-profile measurements. Instagram may deny sign-in to a separate automation-controlled Chrome profile even when regular Chrome works; no CAPTCHA bypass or live-action compatibility is guaranteed.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Published stable: v120.47. Unpublished development: v120.48. Releases require separate owner authorization.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
