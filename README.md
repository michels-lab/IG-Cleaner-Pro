# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.50 — official stable GitHub release (published October 18, 2026).** [Download all v120.50 assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.50).

| Platform | Primary asset | Notes |
| --- | --- | --- |
| Windows installed application + robots | `IG-Cleaner-Pro-Windows-Setup-v120.50.exe` | Recommended; one-click Setup and robot integrations, preserves previous local activity journal on upgrade. |
| Android | `IG-Cleaner-Pro-Android-v120.50.apk` | Original production package ID and verified persistent Android signing identity. |
| Desktop browser | `IG-Cleaner-Pro-Desktop-v120.50.html` | Standalone local HTML, no Windows-only native robot. |
| Optional Windows portable | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.50.zip` | Optional legacy ZIP; Setup is the normal delivery. |
| Optional Desktop ZIP | `IG-Cleaner-Pro-Desktop-v120.50.zip` | HTML and original assets. |

**v120.50:** fixed another Following/Siguiendo locator assumption found in the owner's actual v120.49 screenshots. The robot now surveys the exact visible target username even if Instagram puts it in a span/div instead of h1/h2/h3, and accepts a single nearby accessible/clickable button, role=button or tabindex=0. Never acts on Following counts, links, suggestions or duplicate controls. Read-only no-click diagnostics report `main`, `exact username` and relevant control counts without capturing page contents; Issue Review now wraps messages. Known no-click records remain safely retryable with a new explicit owner-approved batch; post-click uncertainty is still quarantined.

**Important acceptance limit:** GitHub's Chromium simulation, Windows Setup install/upgrade/uninstall and Android/Desktop visual checks passed, but this does **not** confirm that a real Instagram unfollow succeeded on the owner's session. Test with a small batch and inspect the resulting Follow/Follow Back. If it still reports `missing_profile_info`, capture the new `Profile layout` diagnostic. The separate Chrome may receive Instagram challenges; no CAPTCHA bypass. Windows binaries have SHA-256 release checksums but no Authenticode certificate.

**Next development version:** v120.51, not yet authorized.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Published stable: v120.50. Next candidate: v120.51 (not authorized). Releases require separate owner authorization.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
