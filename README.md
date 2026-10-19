# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.52 — official stable GitHub release (published October 19, 2026).** [Download verified v120.52 with all nine assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.52). Tested in automated Windows Setup, Chromium fixture, Desktop and Android build/render/signing gates. Live Instagram owner acceptance remains pending.

| Platform | v120.52 published official asset |
| --- | --- |
| Windows integrated app and Instagram robots | `IG-Cleaner-Pro-Windows-Setup-v120.52.exe` |
| Production-signed Android | `IG-Cleaner-Pro-Android-v120.52.apk` |
| Standalone Desktop HTML | `IG-Cleaner-Pro-Desktop-v120.52.html` |
| Optional Windows portable ZIP | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.52.zip` |
| Optional Desktop bundle | `IG-Cleaner-Pro-Desktop-v120.52.zip` |

**Changes:** actual preparation of up to ten distinct Chrome tabs; safer verified Following/Siguiendo controls and delayed read-only outcome check; automatic whole-batch **Is this batch OK?** confirmation before marking successful profiles Reviewed. Unapproved batches survive restart and rerun automatically in read-only mode; open only issue profiles when needed. Never replay an uncertain relationship-changing click.

**Owner tests the RELEASE:** Michel validates only published stable installers against his real Instagram session, not candidate/preview Actions artifacts. Automated QA still gates publication. No live Instagram action success is claimed before his post-release tests; the robot stops on uncertainty, challenges and identity mismatch. Windows installer SHA-256 integrity checks are supplied, but no Authenticode certificate is configured.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Current stable: v120.52. Next reserved version: v120.53, not authorized for publication.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
