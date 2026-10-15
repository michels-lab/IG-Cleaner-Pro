# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.46 — current stable GitHub release (published October 14, 2026, Mexico time).** [Download v120.46](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.46).

| Platform | Primary release file | Notes |
| --- | --- | --- |
| Desktop (Windows/macOS/Linux browser) | `IG-Cleaner-Pro-Desktop-v120.46.html` | Open locally in a modern browser; single self-contained offline HTML includes official branding. |
| Android | `IG-Cleaner-Pro-Android-v120.46.apk` | Signed release APK; Android package `com.michelslab.igcleaner`. |
| Windows automatic Instagram collector | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.46.zip` | Extract the ZIP and launch the integrated `InstaCleanerPro.exe`; no CMD launcher. User-signed-in Chrome is used only for explicitly requested robot jobs, and real Instagram owner-session acceptance remains pending. |
| Windows integrated app + robots | `IG-Cleaner-Pro-Windows-Setup-v120.47.exe` (next candidate, not yet published) | Michel's Lab installer with real EULA, Start menu, optional desktop shortcut and data-safe uninstall. The official v120.46 remains a portable ZIP until release is separately authorized. |
| Desktop optional full bundle | `IG-Cleaner-Pro-Desktop-v120.46.zip` | Includes separate assets; direct HTML is the preferred simple download. |

Desktop and Android belong to the same product and preserve historical review and Focus workflows. Release CI verified Desktop Chromium Home/About rendering, Android-emulator Home/About and Focus data tests, 99 Supabase isolation/roundtrip assertions, artifact integrity and Android signing. **Physical Samsung installation, real Instagram ZIP import, Focus batches and cloud round-trip remain unverified on the user's device**; see [device acceptance #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24).

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Published v120.46 is official; v120.47 adds an unreleased native Windows Setup candidate and remains development-only until the owner explicitly authorizes a new release.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
