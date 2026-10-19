# Instagram Cleaner Pro

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.53 — official hotfix candidate**, pending independent current-commit packaging/signing/visual QA and final stable GitHub publication. The latest verified published version remains [v120.52](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.52) until publication completes.

| Platform | Planned official v120.53 file |
| --- | --- |
| Windows installed application + automation robot | `IG-Cleaner-Pro-Windows-Setup-v120.53.exe` |
| Android (original production-signed package) | `IG-Cleaner-Pro-Android-v120.53.apk` |
| Desktop offline standalone | `IG-Cleaner-Pro-Desktop-v120.53.html` |
| Optional Windows robot ZIP | `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.53.zip` |
| Optional Desktop ZIP | `IG-Cleaner-Pro-Desktop-v120.53.zip` |

**Critical fix:** Run no longer quietly enters read-only verification for a saved batch still awaiting the owner's approval. It now explicitly resumes **real actions** for untouched or provably zero-click profiles in the *same exact batch*; uncertain previous clicks are never repeated. "Verify previous actions (read-only)" stays separate, approval is disabled until all targets have an outcome, and the issue-profile opener does not open all untouched profiles. Known no-click timeouts do not unnecessarily halt later eligible profiles. Persistent owner/account task journal and imported files are preserved.

**Acceptance:** The owner tests only the **official published stable release** on the real Instagram account; never require a temporary Actions artifact or preview ZIP. Automated Windows/Chromium/Android/Desktop checks are release prerequisites but cannot guarantee that Instagram's real controls work. On challenge or ambiguous action, the robot fails closed. There is no CAPTCHA bypass or Windows Authenticode signature; use published SHA-256 hashes.

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

Before changing product behavior, read [PROJECT_LOG.md](PROJECT_LOG.md), [Current Handoff](docs/CURRENT_HANDOFF.md), and [AGENTS.md](AGENTS.md). Preserve independent workspaces, Focus 20/30/40, Recheck/Double Check, history, protection, backup and user data. **Current published stable remains v120.52 until v120.53 is verified on GitHub. No future version is automatically authorized.**

## Identity and licensing

Created by **Michel Armando Duarte Flores** · **Michel's Lab** · **TOOLS WITH IDENTITY.**  
[Developer GitHub](https://github.com/realmichelduarte) · [Michel's Lab repositories](https://github.com/michels-lab)

This project is **source-available, not open source**. All rights reserved; see [LICENSE.txt](LICENSE.txt). Independent product, not affiliated with or endorsed by Instagram or Meta Platforms, Inc.
