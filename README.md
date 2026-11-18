# Instagram Cleaner Pro

## Published FINAL stable v120.80 — November 18, 2026 UTC

**Normal FINAL v120.80 is published** with [9 SHA-256-verified assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80). The [governed publisher run #44235048175](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44235048175) finished **4/4 jobs SUCCESS**, exact tagged source `e5396cf2710cbd6d9f9ac7f03e5e6eeef948560b`: installed Windows Setup, signed production Android APK installed and launched, exact-source Desktop/Android Home/About screenshots, checksums and public artifact verification. No RC or Developer Edition.

**Granada corrections shipped in v120.80:** Android and HTML Pending freshness reconciliation (including explicit verified empty), paginated review restoration and unique-user counts; native Focus A→B→A owner/session isolation, WebView-login preservation and bounded Windows Setup QA. Previously shipped v120.79 Focus storage/review protections remain. See [release notes](release/RELEASE_NOTES.md) and [official v120.80 release receipt](docs/GRANADA_V12080_FINAL_RECEIPT_2026-11-17.md).

**Owner acceptance remains open:** real Instagram Focus 30/Chrome storage, two accounts A→B→A, profile counters after reload, live Unfollow/Cancel, and physical cross-device acceptance are not established by CI. Export Vault backup before changing standalone HTML path or browser; never clear browser site data.

**v120.80 authorization consumed. Next reserved v120.81 is not authorized or published.**

## Upcoming Granada — both installed Windows account slots and clearer Automations (unreleased)

After merging [#376](https://github.com/michels-lab/IG-Cleaner-Pro/pull/376), source work now checks that the **installed** Windows app initializes both the original and second account slot without sharing a Chrome profile or HTML file origin. Installer upgrade and uninstall must preserve saved data for both. Automations uses the clearly labeled tabs **Analizar / Acciones / Revisar / Historial**, with arrow-key, Home/End and screen-reader tab controls. See the [implementation and acceptance audit](docs/audits/2026-11-18-two-windows-installer-ux.md) and [owner issue #377](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377). **Not present in published v120.80.** Physical simultaneously open Windows and signed-in Instagram A/B acceptance remain open; no release authorization for v120.81.

## Focus near-quota write fallback (source-only; not in v120.80)

When the normal lossless compact Focus batch cannot fit in browser storage, InstaCleaner now attempts a smaller, lossless representation of the same 30 targets before showing its existing storage warning. It preserves every user/relationship field, historical reviewed and Pending ledgers, custom URLs and old v2-format data; it never claims a review occurred unless the batch was durably saved and the owner confirmed it. In the sample regression: **4,091 to 2,510 characters (−38.6%)**. A completely exhausted browser still fails safely. [Audit and open physical acceptance](docs/audits/2026-11-18-focus-quota-fallback.md) · [owner #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). Next stable release not authorized.

## Post-v120.80 GRANADA source work (not yet released)

The Windows Automations activity panel now has a source-branch **robot-confirmed versus unknown legacy-origin filter**. It applies the same period tiles and journal view while preserving contradictory same-time records as unresolved instead of inventing successes. [Implementation audit](docs/audits/2026-11-18-automations-origin-integrity.md) · [Owner issue #298](https://github.com/michels-lab/IG-Cleaner-Pro/issues/298). **Source only: not in published v120.80, with no new stable release and no real-user Windows proof.** Manual+robot combined totals are not claimed.

## Next-source Granada: independent Windows account windows (not in v120.80)

The owner rejected the duplicated **Cuenta 1/Cuenta 2** in-window panels. In [source PR #376](https://github.com/michels-lab/IG-Cleaner-Pro/pull/376), the Windows launcher asks **Cuenta principal / Segunda cuenta**, retaining the original login/browser/file origin for the first and allocating a separate Chrome profile and UI document for the second. The in-app dual-account sidebar, tab-cloning and huge double-robot panel have been removed at source. Automations is organized as **Analyze / Actions / Review / History**; single-account History shows compact verified counters and details on demand. This code is **NOT** in the official v120.80 binaries. [Owner issue #377](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377) · [root-cause and test boundaries](docs/audits/2026-11-18-automations-origin-integrity.md). Installed two-window physical acceptance is open.

## Pending Android vs HTML (shipped source fix; physical owner verification pending)

Owner report: Android can show a cached/cloud Pending snapshot (e.g., **52**) while a standalone HTML displays **0** locally. Neither surface proves live Instagram status. A source-only fix now retains a newer **verified empty** HTML import instead of restoring an older cloud snapshot, loads **complete paginated Android review history** instead of treating a server-capped page as the full history, and labels Android Pending numbers by cache/cloud provenance and import age. **Shipped in v120.80; physical Instagram data reconciliation still unverified.** No historical data is deleted. [Root cause, negative fixtures and acceptance](docs/audits/2026-11-17-pending-android-html-52-vs-zero.md).

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.80 — official stable GitHub release, published November 18, 2026 (UTC).** [Download 9 verified assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80) · [publisher SUCCESS](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44235048175) · tagged source `e5396cf2710cbd6d9f9ac7f03e5e6eeef948560b`. Installed Windows Setup and production-signed Android APK launch passed automated gates; owner physical Instagram checks remain open.

**New in v120.71:** Windows/Desktop has **two independently pinned InstaCleaner account tabs/windows** (open in tab / detach to window) and can request **two isolated persistent Chrome windows** for manual login to different Instagram accounts. Each owner/account Chrome login uses a different user-data folder, separate from exported robot data. The read-only Followers/Following bulk scanner offers owner-bound Recomendado/Más pausado/Personalizado safety controls and mandatory cooldown. **This is NOT two concurrent automated Unfollow/Cancel robots**: relationship-changing workers remain serial, and complete results with the owner's actual Instagram logins still need physical acceptance.

**Current published stable: v120.80. Next reserved version: v120.81, not published.**

v120.80 is published and its one-time authorization is now consumed. v120.81 is reserved and not authorized. Real Instagram acceptance remains open; no RC, beta or Developer editions.

**Previous official release:** [v120.79](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.79), published November 18, 2026 (UTC), official publisher 44204338029.

**New in v120.70 (Windows):** **Automations → Verify live Followers and Following** reads both lists using bulk same-origin authenticated Instagram JSON pages, **not individual target profile visits**, without a ZIP. Compared account identities use numeric Instagram IDs to handle username renames. Corrects the **real user's v120.69 250-page failure** with up to 200 requested members per JSON page, a 1500-page/100k-member bound, and fail-closed incomplete results. No automatic Unfollow, no cookie export, and no overwriting prior complete historical snapshots.

**Instagram safety controls (conservative app settings, not official Instagram limits):** wait 2.5 s between pages, 12 s after five pages and 90 s after 25; stop immediately upon 429/403/503 or `feedback_required`; honor a longer server `Retry-After` and impose at least 30 minutes of persistent shared-Chrome cooldown, including across workspaces, with 15 minutes between completed scans. Stop interrupts waits. These precautions do **not** guarantee freedom from restrictions.

The Instagram private list endpoint may reject reads; owner signed-in **real Instagram acceptance remains OPEN**. **Publication does not prove live Instagram Unfollow** or Cancel Pending succeeded on the owner's account. [Quickstart](docs/INSTACLEANER_V12070_LIVE_SCAN_QUICKSTART.md) · [v120.70 official receipt](docs/GRANADA_V12070_FINAL_RECEIPT_2026-10-27.md).

### Historical v120.66 publication and source notes

**v120.66 — official stable GitHub release, published October 26, 2026 (local; October 27 UTC).** [Governed FINAL publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40423739934) finished **SUCCESS** on exact tagged commit `af291cc6687f527a36fe1d64f31c08615fe216c0` with 12 SHA-256-verified assets, installed Windows public/Developer, production-signed Android public/Developer co-install, rendered Desktop/Android Home/About and verified official update feed.

[**Download v120.66**](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.66) · Windows Setup `IG-Cleaner-Pro-Windows-Setup-v120.66.exe` · Android `IG-Cleaner-Pro-Android-v120.66.apk` · Desktop `IG-Cleaner-Pro-Desktop-v120.66.html`. Independent Windows/Android Developer editions and ZIPs are included in the same normal stable release.

**What changed:** [source PR #253](https://github.com/michels-lab/IG-Cleaner-Pro/pull/253) provides green confirmed OK, yellow Review and grey untouched profile rows in the end-of-batch dialog; **Open Review profiles · robot checks** safely inspects unresolved/untouched exact saved-cohort targets in read-only Chrome. A separate user-approved `Retry verified no-click` acts only on named accounts with a recent positive Following/Requested observation and *durable evidence of no earlier click*, never a possibly clicked/uncertain WAL result. [Governed release PR #254](https://github.com/michels-lab/IG-Cleaner-Pro/pull/254) passed all seven exact-head checks before merging.

**Publication does not prove live Instagram Unfollow or Cancel Pending succeeded on the owner's account.** Real installed v120.65 Unfollow was reported working, but the owner saw the final target left unchecked when Chrome closed. Owner-installed v120.66 Review recovery and actual Cancel Pending need physical validation; see [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) and [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). No live relationship action or Instagram account login occurred in CI. Windows Setup has SHA-256 integrity but no Authenticode signature.

**Historical status at the time of the v120.66 receipt (superseded by the current release above).**

The next reserved development version **v120.67 is authorized ONLY for normal FINAL publication after exact-source installed Windows, production-signed Android public/Developer, rendered visual, SHA-256 and updater-feed gates pass**; it is NOT published yet. The owner tests only officially published installers; source tests cannot replace actual account acceptance. No RC/beta, silent installation or Google Play deployment.

[Official v120.66 publication receipt](docs/GRANADA_V12066_FINAL_RECEIPT_2026-10-26.md). Historical receipts: [v120.65](docs/GRANADA_V12065_FINAL_RECEIPT_2026-10-26.md), [v120.64](docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md), [v120.59](docs/GRANADA_45_V12059_STABLE_RECEIPT_2026-10-23.md), [v120.60](docs/GRANADA_46_V12060_STABLE_RECEIPT_2026-10-23.md), [v120.62](docs/GRANADA_V12062_FINAL_RECEIPT_2026-10-24.md), [v120.63](docs/GRANADA_V12063_FINAL_RECEIPT_2026-10-26.md).

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
