# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.48 — current official stable GitHub release (published October 17, 2026, Mexico time).** [Download v120.48](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.48).

| Platform | Primary release file | Notes |
| --- | --- | --- |
| Windows installed app + robots | `IG-Cleaner-Pro-Windows-Setup-v120.48.exe` | Standard per-user installer with Automations, Profile Counts and opt-in checked updater; preserves account/robot journals on upgrade. |
| Desktop browser | `IG-Cleaner-Pro-Desktop-v120.48.html` | Standalone offline HTML; no native Windows robot within the HTML file. |
| Android | `IG-Cleaner-Pro-Android-v120.48.apk` | Production-signed with the established certificate and app package identity. |
| Windows portable bundle (optional) | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.48.zip` | Legacy portable compatibility package; Setup is preferred. |
| Desktop complete ZIP (optional) | `IG-Cleaner-Pro-Desktop-v120.48.zip` | HTML plus separately bundled original assets. |

**What's new:** safe Pending Requests multi-batch progress after reimports and Windows cold starts; read-only follow-up verification for uncertain cancellation; recoverable Pending Focus previews and individual profile links; targeted English labels for Pending, Mutuals and Followers.

**Known limits:** Instagram may refuse sign-in within the robot's separate browser even if regular Chrome works; no CAPTCHA bypass. Offline QA passed but actual owner account-changing actions, a real Windows self-update and Samsung/Android cross-device state preservation remain to be accepted. The updater requires separate user approval and SHA-256 verification; the Windows executable is not Authenticode-signed.

**Next development version:** v120.49 is reserved; no release is authorized for it.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Published stable: v120.48. Next candidate: v120.49 (not authorized). Releases require separate owner authorization.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
