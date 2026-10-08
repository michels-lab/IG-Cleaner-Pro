# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.37 — stable GitHub release (October 8, 2026).** [Get v120.37](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.37).

| Platform | Primary release file | Notes |
| --- | --- | --- |
| Desktop (Windows/macOS/Linux browser) | `IG-Cleaner-Pro-Desktop-v120.37.html` | Open locally in a modern browser; single self-contained offline HTML includes official branding. |
| Android | `IG-Cleaner-Pro-Android-v120.37.apk` | Signed release APK; Android package `com.michelslab.igcleaner`. |
| Desktop optional full bundle | `IG-Cleaner-Pro-Desktop-v120.37.zip` | Includes separate assets; direct HTML is the preferred simple download. |

Desktop and Android belong to the same product and preserve historical review and Focus workflows. Release CI verified Desktop Chromium Home/About rendering, Android-emulator Home/About, artifact integrity and Android signing. **Physical Samsung installation, real Instagram ZIP import, Focus batches and cloud round-trip remain unverified on the user's device**; see [device acceptance #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24).

## Features

- Import Instagram Following, Followers and Pending Requests in supported export ZIP / JSON / HTML formats, with evidence safeguards for ambiguous exports.
- Review Queue, Mutuals, Followers-you-don't-follow and Pending workspaces, with 20/30/40-profile Focus batches.
- Recheck 30, Double Check 30, review/protection history, active batch recovery, filters, live activity and local backup/export.
- Optional authenticated **Supabase sync of supported normalized lists, review/Focus states and audit data** across Desktop and Android.
- Cloud data export and deletion controls, separate from local export files.

## Data boundary

The **original Instagram export is processed locally**, and raw Instagram ZIP/JSON/HTML files are **not uploaded to the sync backend**. If cloud sync is enabled, supported derived list and review records are transmitted to Supabase for cross-device continuity. It is therefore inaccurate to describe the entire product as having no backend. Local operation and import do not require Instagram login. Review state may exist both locally and, if synchronized, in the user's cloud account. See [Privacy](docs/PRIVACY.md) and [Sync notes](README_SYNC.md).

## Run or develop

For Desktop, download the standalone `.html` asset from the latest GitHub release and open it locally. Developers can also use `index.html`; check the distribution manifest for the supported release artifact. For Android, install the signed APK supplied with the release. Keep app signing identity, browser state keys and Focus history compatible across upgrades.

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Do not publish v120.37 without a new explicit release instruction.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
