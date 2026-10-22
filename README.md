# Instagram Cleaner Pro

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.55 — official stable GitHub release, published October 21, 2026.** [Download the 12 official v120.55 assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.55).

| Platform | Official published asset |
| --- | --- |
| Windows app with integrated action robot | `IG-Cleaner-Pro-Windows-Setup-v120.55.exe` |
| Android with original production signing | `IG-Cleaner-Pro-Android-v120.55.apk` |
| Standalone Desktop HTML | `IG-Cleaner-Pro-Desktop-v120.55.html` |
| Optional Windows portable archive | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.55.zip` |
| Optional Desktop ZIP | `IG-Cleaner-Pro-Desktop-v120.55.zip` |

**Publication does not prove live Instagram Unfollow or Cancel Pending acceptance.** v120.56 is reserved for future development, not yet a published release; the owner tests only officially published installers.

**Fixed:** an unapproved batch could have 38 untouched targets but pressing Run silently entered read-only recheck; v120.53 resumes the exact saved cohort for owner-approved actions on previously untouched or provably no-click targets, never repeating uncertain relationship clicks. **Already not following** is now an explicit terminal no-click result when the exact logged-in target shows Follow/Seguir or Follow Back/Seguir también; the robot records it, closes its safe tab, and advances to the next target without counting a successful Unfollow. Confirmed Unfollows and already-not-followed profiles have separate live totals. Whole-batch Reviewed approval is still a separate owner action.

**Testing contract:** Michel tests against official published stable releases, not temporary previews or Actions artifacts. Automated installed Windows Setup, offline real Chromium action fixtures, Profile Counts, Desktop render, Android render/production signing and SHA256 checksums passed. Those tests do **not** prove a live Instagram Unfollow; only the owner's post-release installed-session test can establish that. Do not bypass challenges, replay uncertain clicks, or erase local journals. The Windows Setup is not Authenticode-signed.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Current published stable: v120.55. Next reserved version: v120.56, not published.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
