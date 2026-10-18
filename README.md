# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.49 — current official stable GitHub release (published October 17, 2026, Mexico time).** [Download v120.49](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.49).

| Platform | Primary release file | Notes |
| --- | --- | --- |
| Windows installed app and robots | `IG-Cleaner-Pro-Windows-Setup-v120.49.exe` | Recommended upgrade, preserving imported lists, existing Chrome robot history and owner-scoped records. |
| Desktop standalone | `IG-Cleaner-Pro-Desktop-v120.49.html` | Self-contained HTML without the Windows-only browser automation robot. |
| Android | `IG-Cleaner-Pro-Android-v120.49.apk` | Signed using the original stable Android package and signing identity. |
| Windows portable robot (optional) | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.49.zip` | Optional compatibility delivery; Windows Setup is preferred. |
| Desktop ZIP (optional) | `IG-Cleaner-Pro-Desktop-v120.49.zip` | Standalone HTML and original separate assets. |

**v120.49 fix:** The Windows robot recognizes an exact profile's `Following` / `Siguiendo` action as a standard button or a `role=button` control with a dropdown caret, in a verified header or profile main area. When the earlier issue was conclusively `nothing clicked`, that historical record can enter a **new owner-approved** batch after an authoritative scoped journal read; uncertain clicked actions remain protected against automatic replay.

**Acceptance limits:** The owner's screenshot confirms the original v120.48 bug, not a successful unfollow. The published v120.49 binary passed offline Chromium tests and official Windows Setup/Android/Desktop gates, but no real Instagram account-changing action has been verified on the owner's device. Instagram security challenges or further DOM variations can still block the robot. Windows Authenticode signing is not configured; use official release checksums.

**Next development version:** v120.50 reserved, not authorized for release.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Published stable: v120.49. Next candidate: v120.50 (not authorized). Releases require separate owner authorization.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
