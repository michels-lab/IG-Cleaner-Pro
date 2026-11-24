## Granada v120.82 FINAL publicada — 24-nov-2026

[Release oficial](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.82), exact tagged source `84b84e7a5dec057a869b72fe149dfde3f037cf00`, [publicador #45358286199](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45358286199) **4/4 SUCCESS**, 9 activos con SHA-256, Windows Setup instalado/iniciado/desinstalado, Android firmado instalado/iniciado en emulador y capturas Home/About verificadas. [Recibo](docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md). #409/#410/#411 incluidos. #413 y #414 son desarrollo posterior independiente; no incluidos. Avance **58% (7/12)**, aceptación física sigue pendiente #371/#377/#360/#164/#172. Autorización única consumida; v120.83 reservada no autorizada. No RC ni beta.

---

**v120.82 — official stable GitHub release, published November 24, 2026 (UTC).** [Download](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.82) · [Receipt](docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md).

## v120.82 — FINAL release requested (24-Nov-2026)

Owner explicitly authorized official stable distribution for subsequent physical testing. Source #409, #410 and #411 integrated; #411 6/6 exact-head SUCCESS. Latest published remains v120.81 until governed publisher succeeds. All exact-source installer, signed APK, rendered UI and checksum gates remain mandatory. P0 58% (7/12), five real-account/device milestones pending. No RC, beta or Developer publication.

- [#409](https://github.com/michels-lab/IG-Cleaner-Pro/pull/409): account-bound cloud DELETE and export, preserve local history on registry refresh.
- [#410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410): reject hidden/offscreen/transparent identity controls.
- [#411](https://github.com/michels-lab/IG-Cleaner-Pro/pull/411): independent Automations batch status and 8-second local journal deadline, partial/unknown counts and retry.

---

## GRANADA 24-nov-2026 — #410 integrado; #411 Automations responsive

**58% (7/12) → 58% (7/12).** [#410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410) integrado `7e3dd5420362c9e235b9966da5e5bffc8955da5f`, 8/8 SUCCESS exact-head `5e6e84f035974b02b920f39fa344b995b4295065`. [Auditoría](docs/audits/2026-11-24-visible-owner-controls-viewport.md). [#411](https://github.com/michels-lab/IG-Cleaner-Pro/pull/411) abierto HEAD `16f4f7f30a385471ceb0f0ca7fc02b66a4d7a196`: tiempo máximo de lectura local 8 s incluso JSON, estado de tanda independiente del historial, reintento tras fallo, supervisor no verificable no equivale a detenido. Regresión Chromium de timeout parcial, total y recuperación en revisión; CI pendiente. No modificación de datos ni acciones Instagram reales. Cinco hitos físicos #371/#377/#360/#164/#172 pendientes. FINAL v120.81 publicada; #409/#410 no distribuidos y #411 no integrado; v120.82 retenida.

---

# Instagram Cleaner Pro

## GRANADA 24 Nov — owner identity: exclude offscreen/transparent controls (source PR #410; NOT released)

[PR #410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410) adds real-code checks so the Chrome robot does not identify the logged-in owner from offscreen navigation links or an invisible/transparent Edit profile control. Includes [offline Chromium regressions and cause analysis](docs/audits/2026-11-24-visible-owner-controls-viewport.md). **Await exact-head CI/merge; not included in v120.81.** Physical live Instagram owner/navigation acceptance remains open, as do five P0 gates. This work does **not** authorize v120.82 or claim successful Unfollow/Cancel Pending.

## Historical v120.81 stable and P0 acceptance — 23 Nov 2026 Saltillo

[v120.81 FINAL](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.81) has **nine SHA256-verified assets**, signed Android public APK, integrated installed Windows Setup and offline Desktop HTML, with [official 4/4 publisher SUCCESS](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45319438358). This published milestone moves the **12-item P0 owner acceptance path from 6/12 (50%) to 7/12 (58%)**. Live Focus no-counter-rebound, two independent Windows Instagram logins, Unfollow, Cancel Pending, and physical Android/Windows backup upgrade remain owner-pending. Do not claim real account acceptance. **v120.82 is only reserved, not authorized.**

## GRANADA — Atomic Focus history writes (included in v120.81; owner QA pending)

The Focus bulk opening/reopening history writer now restores **all affected in-memory profile counters and events** when the persistent history write is rejected. Failed operations cannot be silently saved later or disappear only upon reload. The production-function quota/retry/reload regression is CI-wired. [Detailed audit](docs/audits/2026-11-18-focus-history-transaction.md) · [Owner counter issue #360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) · [storage #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). This does not increase browser storage limits. Official stable v120.81 is now publicly released (9 SHA256 assets; 4/4 publisher SUCCESS). Owner physical Focus/storage acceptance is still open.

## GRANADA Focus — exact failed-storage diagnostics (included in v120.81; owner QA pending)

When a Focus cohort is refused by browser storage, the recovery panel now identifies whether the actual rejected write was the normal v2 or smaller v3 attempt, the fixed Focus key, the attempted UTF-16 byte estimate and estimated storage usage, without exposing profile names or stored values. A successful retry clears stale warnings. This **does not free an exhausted quota or prove Focus opened on the owner's browser**. [Root cause and regression audit](docs/audits/2026-11-18-focus-write-diagnostics.md) · [open owner #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). Published stable v120.81 includes this source fix; browser quota and Focus real-owner acceptance are still pending.

## GRANADA P0 — prevent stale Instagram cloud responses (shipped v120.81, physical QA pending)

A cloud REST request is tied to its exact app owner, Instagram account and switch generation, so late A→B and A→B→A responses cannot hydrate the wrong workspace or refresh an obsolete request. This source update preserves the already merged atomic Reviewed confirmations ([#383](https://github.com/michels-lab/IG-Cleaner-Pro/pull/383)) and includes negative race regressions. See the [race-condition audit](docs/audits/2026-11-18-inflight-instagram-rest-guard.md). **Now included in official stable v120.81** after 4/4 guarded publisher jobs; real signed-in owner A/B verification remains separate.

## Published FINAL stable v120.80 — November 18, 2026 UTC

**Normal FINAL v120.80 is published** with [9 SHA-256-verified assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80). The [governed publisher run #44235048175](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44235048175) finished **4/4 jobs SUCCESS**, exact tagged source `e5396cf2710cbd6d9f9ac7f03e5e6eeef948560b`: installed Windows Setup, signed production Android APK installed and launched, exact-source Desktop/Android Home/About screenshots, checksums and public artifact verification. No RC or Developer Edition.

**Granada corrections shipped in v120.80:** Android and HTML Pending freshness reconciliation (including explicit verified empty), paginated review restoration and unique-user counts; native Focus A→B→A owner/session isolation, WebView-login preservation and bounded Windows Setup QA. Previously shipped v120.79 Focus storage/review protections remain. See [release notes](release/RELEASE_NOTES.md) and [official v120.80 release receipt](docs/GRANADA_V12080_FINAL_RECEIPT_2026-11-17.md).

**Owner acceptance remains open:** real Instagram Focus 30/Chrome storage, two accounts A→B→A, profile counters after reload, live Unfollow/Cancel, and physical cross-device acceptance are not established by CI. Export Vault backup before changing standalone HTML path or browser; never clear browser site data.

**v120.81 FINAL has published, one-time authorization consumed. Next reserved v120.82 is not authorized.**

## Granada — installed Windows account slots and clearer Automations (source shipped v120.81, owner QA pending)

After merging [#376](https://github.com/michels-lab/IG-Cleaner-Pro/pull/376), source work now checks that the **installed** Windows app initializes both the original and second account slot without sharing a Chrome profile or HTML file origin. Installer upgrade and uninstall must preserve saved data for both. Automations uses the clearly labeled tabs **Analizar / Acciones / Revisar / Historial**, with arrow-key, Home/End and screen-reader tab controls. See the [implementation and acceptance audit](docs/audits/2026-11-18-two-windows-installer-ux.md) and [owner issue #377](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377). **Included in published v120.81.** Physical simultaneously open Windows and signed-in Instagram A/B account acceptance remain open; publication is for owner device review, not owner feature acceptance.

## Focus near-quota write fallback (shipped v120.81, real-browser QA pending)

When the normal lossless compact Focus batch cannot fit in browser storage, InstaCleaner now attempts a smaller, lossless representation of the same 30 targets before showing its existing storage warning. It preserves every user/relationship field, historical reviewed and Pending ledgers, custom URLs and old v2-format data; it never claims a review occurred unless the batch was durably saved and the owner confirmed it. In the sample regression: **4,091 to 2,510 characters (−38.6%)**. A completely exhausted browser still fails safely. [Audit and open physical acceptance](docs/audits/2026-11-18-focus-quota-fallback.md) · [owner #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). Stable v120.81 published after all official publisher checks; next reserved v120.82 unauthorized.

## Post-v120.80 GRANADA work (included in v120.81; physical tests pending)

The Windows Automations activity panel now has a source-branch **robot-confirmed versus unknown legacy-origin filter**. It applies the same period tiles and journal view while preserving contradictory same-time records as unresolved instead of inventing successes. [Implementation audit](docs/audits/2026-11-18-automations-origin-integrity.md) · [Owner issue #298](https://github.com/michels-lab/IG-Cleaner-Pro/issues/298). **Included in official stable v120.81; still no real-owner Windows account proof.** Manual+robot combined totals are not claimed.

## Next-source Granada: independent Windows account windows (not in v120.80)

The owner rejected the duplicated **Cuenta 1/Cuenta 2** in-window panels. In [source PR #376](https://github.com/michels-lab/IG-Cleaner-Pro/pull/376), the Windows launcher asks **Cuenta principal / Segunda cuenta**, retaining the original login/browser/file origin for the first and allocating a separate Chrome profile and UI document for the second. The in-app dual-account sidebar, tab-cloning and huge double-robot panel have been removed at source. Automations is organized as **Analyze / Actions / Review / History**; single-account History shows compact verified counters and details on demand. This code is **NOT** in the official v120.80 binaries. [Owner issue #377](https://github.com/michels-lab/IG-Cleaner-Pro/issues/377) · [root-cause and test boundaries](docs/audits/2026-11-18-automations-origin-integrity.md). Installed two-window physical acceptance is open.

## Pending Android vs HTML (shipped source fix; physical owner verification pending)

Owner report: Android can show a cached/cloud Pending snapshot (e.g., **52**) while a standalone HTML displays **0** locally. Neither surface proves live Instagram status. The shipped v120.81 fix now retains a newer **verified empty** HTML import instead of restoring an older cloud snapshot, loads **complete paginated Android review history** instead of treating a server-capped page as the full history, and labels Android Pending numbers by cache/cloud provenance and import age. **Shipped in v120.80; physical Instagram data reconciliation still unverified.** No historical data is deleted. [Root cause, negative fixtures and acceptance](docs/audits/2026-11-17-pending-android-html-52-vs-zero.md).

## Operación Granada — auditoría de aplicación y plugins (2026-10-21)

[Ver auditoría y bitácora propias de este producto](docs/GRANADA_APP_PLUGIN_AUDIT_2026-10-21.md): evidencia de GitHub Actions, conectores ChatGPT aplicables, servicios existentes, costo cero adicional por defecto, pendientes reales y separación estricta de los demás productos. La documentación no prueba QA físico ni publica una versión.

Local-first Instagram export analyzer by **Michel's Lab**. Review Following/Followers, manage cleanup batches, track decisions, and optionally sync supported workspace state between Desktop and Android. **No Instagram credentials, Instagram API access, or automatic follow/unfollow actions are required.**

## Current release

**v120.81 — official stable GitHub release, published November 24, 2026 (UTC).** [Download 9 verified assets](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.81) · [governed publisher 4/4 SUCCESS](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45319438358) · tagged source `fc1cd03a476dc4c5797e90e89e18d22733c34175`. Windows Setup installation/launch/uninstall and production-signed Android APK emulator installation/launch passed; Home/About screenshot evidence and checksums verified. [Official receipt](docs/GRANADA_V12081_FINAL_RECEIPT_2026-11-23.md). Owner live Instagram/physical Samsung checks remain open.

**New in v120.71:** Windows/Desktop has **two independently pinned InstaCleaner account tabs/windows** (open in tab / detach to window) and can request **two isolated persistent Chrome windows** for manual login to different Instagram accounts. Each owner/account Chrome login uses a different user-data folder, separate from exported robot data. The read-only Followers/Following bulk scanner offers owner-bound Recomendado/Más pausado/Personalizado safety controls and mandatory cooldown. **This is NOT two concurrent automated Unfollow/Cancel robots**: relationship-changing workers remain serial, and complete results with the owner's actual Instagram logins still need physical acceptance.

**Current published stable: v120.82. Next reserved version: v120.83, not published.**

v120.81 is published and its one-time owner authorization is consumed. v120.82 is reserved without authorization. Real Instagram acceptance remains open; no RC, beta or Developer editions.

**Previous official release:** [v120.80](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.80), published November 18, 2026 (UTC), official publisher 44235048175.

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

## GRANADA — Cross-page A→B→A cloud review sync (shipped v120.81; owner QA pending)

The review/pending cloud sync now ties a **complete multi-page download and a multi-POST upload** to one app owner, Instagram slot and slot generation. Switching A→B→A between requests rejects the original operation, rather than combining rows or sending old account records under the new active slot. The four-second cache is generation-scoped too. The CI-wired regression tests actual production read/push JS, including a delayed second GET and a delayed first of two POSTs. [Root cause and test evidence](docs/audits/2026-11-18-cloud-multipage-aba.md) · [owner counter issue #360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360). Physical owner accounts still need validation; official stable v120.81 is now published; owner live Instagram acceptance remains pending.

## GRANADA — Pending Focus two-ledger recovery and Double Check (shipped v120.81; owner QA pending)

Fixed two real Focus partial-write paths: when an active Pending cohort was saved but the separate opened-ledger write failed, RAM counters used to drop although no tabs were requested; that failure now rolls back Pending RAM and leaves the cohort recoverable with a visible warning. Pending Double Check now saves its **second-pass mode in the first cohort write**, persists the attempt ledger before changing selection, shows Reviewed before tab requests, and isolates popup exceptions. Both paths defer `open` history until required ledgers are durable. CI-wired negative tests reproduce quota denial, manual retry, a broken dialog and a thrown popup. [Root-cause audit](docs/audits/2026-11-18-pending-focus-two-ledger-durability.md) · [#360](https://github.com/michels-lab/IG-Cleaner-Pro/issues/360) · [#371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). Owner physical verification remains open; latest published stable is v120.81, owner physical QA still pending.

## GRANADA — Unified Focus reopen (shipped v120.81; owner QA pending)

Both Active Batch Reopen and Reviewed Reopen now use the same recovery-first implementation: already-resolved profiles are excluded, owner Reviewed and direct links appear **before** Chrome requests, one rejected popup does not suppress the remaining profiles, and failed secondary history/audit writes cannot erase a saved cohort. The unused timer-based launcher that incorrectly claimed profiles were opened was removed from source. Production-function negative cases are wired to CI. [Audit](docs/audits/2026-11-19-focus-reopen-single-path.md) · [Owner storage issue #371](https://github.com/michels-lab/IG-Cleaner-Pro/issues/371). Requires real owner-browser acceptance. Published stable is v120.81 after 4/4 governed publisher checks; owner acceptance remains pending.
