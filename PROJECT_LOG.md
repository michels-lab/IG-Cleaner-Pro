# IG Cleaner Pro — Project Log & Functional Contract

_Last updated: 2026-10-07_

This file is the **functional contract** for IG Cleaner Pro. UI redesigns, refactors, performance work, and future releases must preserve the capabilities listed here unless Michel Armando Duarte Flores explicitly requests their removal.

## Stable reference

- **Stable functional baseline:** v119 — HTML comparable-range · JSON intact.
- Experimental v120.x redesign previews are **not** allowed to redefine or silently remove v119 functionality.
- Before merging a redesign into `main`, compare the new build against this contract and the v119 baseline.

---

## Non-negotiable architecture

### Review = Following only

Review is exclusively for accounts **Michel follows**.

It must preserve:
- Following cleanup workflow.
- Foco 20 / 30 / 40.
- Recommended batches.
- Recheck / second-review workflow.
- Double Check workflow.
- Protected / reviewed / snoozed states.
- Current-session counters and active-batch tracking.
- Saved history/activity.
- Filters and direct views for accounts that do not follow back.

**Do not reintroduce a "Clean followers" mode inside Review.** Followers has its own dedicated workspace.

### Followers = people who follow the account

Followers must preserve its own dedicated workspace and must not be reduced to a passive table.

It must include:
- Its **own focus controls**.
- Its **own batch/session bar**, equivalent in usefulness to Review.
- Saved history/activity visible inside Followers.
- Search, filters, relation status, risk, review state, protection, and profile actions.
- A Mutuals subview for followers Michel also follows.

### Mutuals

Mutuals is a sub-workflow inside Followers.

It must preserve:
- Foco 20 / 30 / 40.
- Recommended batch.
- Risk batch.
- Review state and protection.
- Its own session/progress tracking.
- Relationship context and review history.

### Pending

Pending is exclusively for pending follow requests.

It must preserve:
- Pending-specific focus/recommended/risk workflows.
- Pending session tracking.
- Pending review/decision state.
- Cross-check logic against Following/Followers.
- No Review or Followers focus may appear here by accident.

---

## Review — mandatory second-review system

The following controls and their behavior are **mandatory** and must not disappear during UI redesign:

### Revisar de nuevo 30
- Reopens accounts that **currently do not follow back**, even if they were already reviewed.
- Must allow already-reviewed rows to be checked again.
- Must show a confirmation popup after opening.
- Must update the review state when confirmed.
- Uses its own cycle/history state so the workflow can rotate through candidates.

### Double Check 30
- Opens accounts that **currently do not follow back**.
- Rotates through different profiles instead of repeatedly serving the same first 30.
- Maintains a separate seen/cycle state.
- Must show a confirmation popup.
- When all current candidates have passed through the cycle, the user can reset/restart the cycle.

### Ver NO ME SIGUE revisados
- Must remain available.
- Shows accounts that currently do not follow back **including already-reviewed accounts**.
- This view exists specifically so previously reviewed relationships can be validated again.

### Cycle controls
Keep visible controls for:
- Reset Double Check cycle.
- Reset Recheck / Revisar de nuevo cycle.

Do not replace these with a generic focus button.

---

## Focus behavior — mandatory

All Focus-style flows must:
- Open Instagram profiles in tabs.
- Leave a confirmation/review UI open in IG Cleaner.
- Preserve active-batch state until the user resolves or cancels it.
- Avoid mixing candidates from another module.
- Never let a global focus control silently switch between Review, Followers, Mutuals, or Pending.

### Context under each username

Where Focus/Recheck/Double Check shows a username, show useful relationship context directly below it when data is available, for example:

- `Lo sigues desde 2022`
- `Te sigue desde 2021`
- `No te sigue`
- `Revisado hace 18 días`
- `Nunca revisado`
- `Te dejó de seguir`

This is context for the user, not a hidden scoring explanation.

---

## Batch/session tracking — mandatory

Review, Followers, Mutuals, and Pending must retain useful batch/session feedback where applicable, including:
- Batches today.
- Reviewed today.
- Reopened/rechecked.
- Active batch.
- Available/openable candidates.
- Last action.
- Ability to recover/reopen/cancel an active batch when supported.

A one-line "Last action" message **does not replace** the batch/session system.

---

## Saved history/activity — mandatory

The app must preserve the automatic review/activity history.

Followers must have a visible saved-history/activity area comparable to Review, scoped to the relevant Followers/Mutuals workflow.

Do not replace the history table/list with only a "last action" label.

History should preserve useful events such as:
- opened
- reopened
- reviewed
- unconfirmed
- snoozed
- last section
- last decision
- last opened
- last reviewed

Export of automatic history must remain available when supported by the stable baseline.

---

## Relationship evidence rules

- Do not treat missing accounts in a partial HTML export as confirmed non-followers.
- JSON behavior from the stable baseline must not be changed casually.
- Relationship conclusions must respect the comparable-range / evidence safeguards already implemented.
- UI redesigns must never weaken evidence correctness.

---

## UX rules

- Primary visual direction is **dark**, not light.
- Avoid generic admin-dashboard styling.
- Redesigns may change layout and visual hierarchy, but **must not remove functionality**.
- Do not duplicate the same workflow in multiple modules.
- Each module owns its actions:
  - Review → Following
  - Followers → Followers
  - Mutuals → mutual followers
  - Pending → pending requests
- Do not add context-dependent global buttons that can trigger the wrong module.
- Keep Focus and review actions obvious and local to their section.

---

## Regression checklist before merge

Before any future build is merged to `main`, verify at minimum:

- [ ] Review still contains Following Focus.
- [ ] Revisar de nuevo 30 is visible and functional.
- [ ] Double Check 30 is visible and functional.
- [ ] Ver NO ME SIGUE revisados is visible and functional.
- [ ] Double Check and Recheck cycle reset controls exist.
- [ ] Followers has its own Focus workflow.
- [ ] Followers has its batch/session bar.
- [ ] Followers has visible saved history/activity.
- [ ] Mutuals has its own Focus workflow.
- [ ] Pending has only Pending actions.
- [ ] No cross-module Focus button appears in the wrong section.
- [ ] Focus cards show relationship-age/review context when available.
- [ ] Active batch can be recovered/resolved.
- [ ] Protected/reviewed/snoozed states are preserved.
- [ ] Relationship evidence safeguards are preserved.
- [ ] JSON import logic remains intact unless intentionally changed and tested.
- [ ] About / Legal / Version remain available.
- [ ] No duplicate DOM IDs.
- [ ] All scripts pass syntax validation.
- [ ] Existing saved local state remains compatible or migration is provided.

---

## 2026-09-29 — redesign lesson

During the v120.x UI experiments, several regressions were found:
- Followers controls were replaced with generic Focus buttons.
- Followers lost its batch/session presentation.
- Followers lost visible saved history.
- The second-review / Recheck / Double Check controls disappeared from the redesigned Review UI.
- A global/contextual Focus control could show actions from the wrong module.

These are now explicitly documented as **regressions that must not recur**.

The redesign may continue, but functionality must be preserved first and reorganized second.


## 2026-09-29 — mandatory module sidebars

The right-side **live sidebar is part of the functional UX contract**, not an optional decoration.

- **Review** keeps its existing right-side live panel.
- **Followers** must have its own right-side live panel with Followers/Mutuals-specific data.
- **Pending** must have its own right-side live panel with Pending-specific data.
- These sidebars should contain the module's live/session information such as last action, opened/reviewed counts, pending/resolved state, active batch, reopen counts, module-specific status, saved history/activity, and relevant quick actions.
- When Followers switches between **All Followers** and **Mutuals**, the same Followers sidebar may update its scope, but it must remain visible.
- Do **not** replace these sidebars with session/history cards inserted into the central workspace.
- The central workspace is for the module's focus controls, filters, tables and primary content; live tracking belongs in the right sidebar.
- A redesign that removes either the Followers or Pending sidebar is a regression.


### Recent activity parity across module sidebars

Review, Followers/Mutuals, and Pending must each expose a full **Recent activity** block in their right-side live sidebar.

At minimum, each module must show its own scoped metrics for:
- reviewed in the last 1 h and 3 h;
- opened in the last 1 h and 3 h;
- Focus activity in the last 1 h and 3 h;
- action count in the last 1 h and 3 h;
- reviewed today and in the last 24 h;
- opened today and in the last 24 h;
- batches today and in the last 24 h;
- protected/paused today as appropriate to the module;
- reopened today.

These counters must be **module-scoped**. Followers/Mutuals must not show Review or Pending activity, and Pending must not show Review or Followers activity.

A reduced sidebar that only shows last action + a few totals is a regression.


### Standard activity hierarchy for all three work sidebars

The right-side live panels for **Review**, **Followers/Mutuals**, and **Pending** must use the same primary activity hierarchy.

Required order, from top to bottom:
1. **Last action** — show exactly what was done and when it happened.
2. **Opened this session**.
3. **Opened today**.
4. **Opened in the last 7 rolling days**.
5. **Opened in the last 1 hour**.
6. **Opened in the last 2 hours**.
7. **Opened in the last 3 hours**.
8. **Module-scoped action history**.
9. Secondary module-specific state and controls.

“Opened” means profiles actually opened through logged open/focus/reopen actions; the same definition must be used across all three modules.

Followers may switch scope to Mutuals, but the hierarchy stays identical and only the data scope changes.

Do not replace this structure with different metric sets for each module.

### JSON detection diagnostic rule

The file-detection preview must never label a valid JSON file as invalid because only a truncated header was parsed.

- Full JSON must be read before using JSON.parse for validity.
- Header-only sampling may be used for HTML detection.
- “JSON inválido” is reserved for a full JSON document that actually fails parsing.
- Diagnostic/preview messaging must agree with the importer whenever the importer successfully parses the file.


### Explicit relative time for last action

The top card of the Review, Followers/Mutuals, and Pending sidebars must state the last action in explicit human relative time.

Required pattern:
- `ÚLTIMA ACCIÓN · hace 3 horas`
- `ÚLTIMA ACCIÓN · hace 5 días`
- `ÚLTIMA ACCIÓN · hace 12 minutos`
- `ÚLTIMA ACCIÓN · hace un momento`

Directly below it, show what was done. The exact date/time may remain as secondary text.

Do not show only an absolute timestamp or force the user to calculate how long ago the action happened.


#### Relative-time precision

The last-action relative timestamp must be precise enough to identify when the event happened, while still showing the exact date/time underneath.

Examples:
- `hace 7 min`
- `hace 1 h 23 min`
- `hace 5 h 04 min`
- `hace 2 días 3 h`
- `hace 1 semana 2 días`
- `hace 2 meses 5 días`
- `hace 1 año 2 meses`

For events under 24 hours, preserve minutes rather than rounding down to only whole hours.


## 2026-09-29 — Mutuals and non-followed Followers are separate workspaces

The Followers data must be partitioned into two distinct workspaces in the UI:

### Mutuals
Contains only followers that the user also follows (`iFollow === true`).

It must have its own:
- page/navigation entry;
- Focus 20 / 30 / 40;
- recommended/risk batches;
- filters and table;
- standardized right sidebar;
- last action, opened-session/time-window metrics and action history.

### Followers que no sigo
Contains only followers that follow the user but the user does not follow (`iFollow === false`).

It must have its own:
- page/navigation entry;
- Focus 20 / 30 / 40;
- recommended/risk batches;
- filters and table;
- standardized right sidebar;
- last action, opened-session/time-window metrics and action history.

Do **not** put Mutuals and followers the user does not follow in the same page behind an internal `Todos / Mutuos / No los sigo` selector.

Historical data may come from the same Followers export, but presentation, focus candidates, action history and live session scope must stay separated.

### Layout rule
Mutuals, Followers que no sigo and Pending use exactly one flexible central content column plus one right live sidebar on desktop. Never reserve sidebar width twice through nested padding/fixed-panel rules; doing so crushes the central content and is a regression.


## 2026-09-30 — Complete Instagram ZIP is the primary import workflow

The **primary** way to load Instagram data into IG Cleaner Pro is the complete `.zip` export downloaded from Instagram.

Required behavior:
- The Import page must present **Import complete Instagram export (.zip)** as the recommended/default path.
- The user should not need to unzip the export manually.
- ZIP processing happens locally in the browser; the archive is not uploaded to a server.
- Search recursively through folders inside the archive.
- Automatically identify and group every supported export, including:
  - Following;
  - all `followers_*` files;
  - Pending follow requests;
  - Recent follow requests;
  - Recently unfollowed profiles;
  - Blocked profiles;
  - other export categories explicitly supported by the app in the future.
- Following/Followers/Pending found in the ZIP must be loaded into their normal app workflows automatically.
- Additional supported exports must be analyzed and surfaced automatically rather than requiring the user to select them again.
- The ZIP route must reuse the **same format detection/parsers** as manual import. Do not maintain a second independent interpretation of Instagram data.
- Files may be nested in arbitrary folders; do not depend on one fixed Instagram folder path.
- Multiple Followers files must be combined automatically.
- Manual upload of individual JSON/HTML files remains available as an **advanced/alternative import path**, not the primary UX.
- Invalid/encrypted/unsupported archives must produce an explicit error without destroying the currently stored review state.


### ZIP fixture must be derived from a real export structure

The repository fixture at `tests/fixtures/instagram-export-sample.zip` must remain sanitized but structurally faithful to a real Instagram export.

For the 2026-09-30 reference structure:
- preserve the 13 real archive paths and nested folders;
- preserve JSON root types and key shapes;
- preserve the three `followers_*.json` split;
- preserve the real Pending / Recent / Blocked `label_values` schema;
- preserve ZIP STORE (method 0) when that is what the real export uses;
- include neighboring exports such as `following_hashtags.json` so regression tests prove they are ignored rather than misclassified.

The importer must be tested against both the sanitized fixture and the locally supplied real reference ZIP before a ZIP-import change is considered validated.

A real regression found during this validation: `following_hashtags.json` was initially misclassified as Following because of the filename substring. The ZIP classifier must only treat the actual Following account export as Following.

Validated reference counts on 2026-09-30: **11,785 Following / 21,824 Followers / 418 Pending**.


### ZIP-to-Pending synchronization is mandatory

When `pending_follow_requests` is found inside the primary Instagram ZIP import:

- parsed rows must be assigned to `pendingRequestsRaw`, persisted, and rendered immediately in the Pending workspace;
- the Pending workspace must visibly state that its current source came from the ZIP and show the number of loaded requests;
- the manual Pending file input is an alternative/replacement path only; it must not keep presenting `Sin archivo` as if no Pending source exists after successful ZIP import;
- ZIP import must reset stale Pending search/risk/age/view filters to a visible all-data state so imported records cannot appear missing because of an old filter;
- after global rebuild/filter routines run, Pending must be rendered again so later refreshes cannot leave a stale empty table;
- if Pending data exists but the current filters produce zero rows, the empty-state message must say that no rows match the filters rather than asking the user to upload `pending_follow_requests.json`.

The real 2026-09-30 reference ZIP contains exactly one `connections/followers_and_following/pending_follow_requests.json` file with **418** entries using the `label_values` schema.


## 2026-09-30 — Experience layer: Import Report, Command Center and Focus Session

These features improve execution speed without replacing the v119 engine or the module-specific workflows.

### Import Intelligence Report
After a complete Instagram ZIP is processed, Import must expose an operational report based on the current export.

At minimum show:
- Following;
- Followers;
- Mutuals;
- current accounts that do not follow back, respecting existing evidence safeguards;
- Followers the user does not follow;
- Pending;
- current critical-priority count;
- compatible extra-export records/files when available.

The report must provide direct navigation/actions into Review, Mutuals, Followers, Pending and/or Command Center. It must use the already parsed in-memory data and must not require the internal ZIP files to be uploaded again.

### Command Center live work queue
Home / Command Center must expose work that is actually available now rather than only static navigation cards.

It must include live candidate availability for:
- Review Focus;
- Recheck / Double Check;
- Mutuals;
- Followers the user does not follow;
- Pending.

If an active Focus batch exists, continuing that batch takes precedence over suggesting a new one. Starting a Command Center action must call the existing module-specific workflow; it must not create a second focus engine.

### Focus Session
A Focus batch may use a dedicated one-profile-at-a-time working surface.

Required behavior:
- preserve the existing active batch as the source of truth;
- show `resolved / total` progress and remaining count;
- show username plus relationship/review context already known by the app;
- show saved profile-history context when available;
- allow opening the current profile and reopening unresolved profiles;
- support individual decisions without automatically applying one decision to the entire batch;
- Review / Mutuals / Followers support Reviewed, Protect, Keep/Conserve, Snooze and the existing secondary decision types where applicable;
- Pending supports Still pending, Accepted, Reviewed, Snooze and the existing secondary decision types where applicable;
- “Next without marking” must leave that profile unresolved;
- resolving one profile must prune only that profile from the active batch;
- finishing all profiles must leave the active batch empty and show a session summary;
- closing early must preserve unresolved active-batch state so the session can be recovered;
- the legacy/classic batch confirmation UI remains available as a fallback.

The Focus Session is a new working surface over the existing v119/v120 batch state, not a replacement for module state/history or evidence logic.

### Regression found during v120.19 validation
`autoCleanGarbageStates()` referenced the nonexistent `savePendingSnooze()` helper. The correct persisted-state helper is `savePendingSnoozeMap()`.

### v120.19 real-export validation
Validated locally against the supplied 2026-09-30 Instagram ZIP:
- 11,785 Following;
- 21,824 Followers;
- 418 Pending;
- 11,087 Mutuals;
- 698 current no-follow-back rows under the app's current evidence rules;
- 10,737 Followers the user does not follow;
- 27 critical-priority rows;
- Import Report visible after ZIP processing;
- Command Center work queue populated from live candidate functions;
- Pending remained 418 visible rows after ZIP import;
- Focus Session individual-resolution smoke tests passed for Review, Mutuals, Followers and Pending;
- no page errors or console warnings in the final browser smoke test;
- 0 duplicate DOM IDs;
- all 12 inline scripts pass JavaScript syntax validation.


## 2026-10-03 — v120.20 ZIP HTML/JSON parity

- Source baseline: v120.19 experience upgrade.
- Complete Instagram ZIP remains the primary import workflow.
- ZIP import now activates the HTML relationship-evidence safeguards from the files found inside the ZIP itself, instead of depending on the manual Followers file input.
- JSON import/parsing behavior is intentionally unchanged.
- Manual JSON/HTML uploads remain an advanced alternative path.
- Structural validation: all inline scripts pass syntax validation and no duplicate DOM IDs were found.

## 2026-10-05 — Infrastructure / cloud audit

Added `docs/INFRASTRUCTURE_AUDIT.md`.

The current local-only architecture is an intentional privacy property: Instagram exports stay in the browser and no backend is required. Supabase/Google cloud must therefore remain optional future architecture, not a default dependency. Near-term infrastructure gaps are CI, update/distribution design, centralized privacy documentation and browser-storage migration/versioning.

## 2026-10-05 — Michel's Lab parent/child governance contract

Added the repository-level Michel's Lab governance declaration:

- `.michelslab/project.yml` identifies `michels-lab/Michel-Software-Standards` as the shared standards authority.
- `MICHELS_LAB_PROJECT.md` documents the human-readable reporting contract.
- App-specific implementation evidence remains in this repository.
- Reusable/cross-app decisions are promoted to the master standards repository.
- The master repository polls child status centrally; this repository receives no credential that can write to the master.
- Secret values remain prohibited from both repositories.


## 2026-10-05 — Android Companion v120.28 native rebuild

- Replaced the ultra-minimal v120.27 Android prototype after the first distributed APK was only ~25 KB and failed to launch reliably on the target phone.
- v120.28 uses a conventional Android app structure with AppCompat, Material Components, RecyclerView, XML layouts, theme resources, launcher resources and bottom navigation.
- Android UX is intentionally different from Desktop: Focus 20/30/40 is shown as a one-profile-at-a-time checklist instead of opening many browser tabs.
- Opening a profile records an `opened` / `reopened` event; it does not by itself mark the profile reviewed.
- Completing the entire checklist requires explicit confirmation before the batch and profile states become reviewed.
- Review events preserve source device (`android` or `desktop`) and remain distinct from Audit events.
- Audit includes quick access to the latest reviewed/opened profiles by Android or Desktop and records subsequent audit activity separately.
- Supabase URL + publishable key remain app configuration; users only see email OTP login.
- Sync tokens are excluded from Android backup/device-transfer rules.
- Android applicationId for beta debug builds uses `.beta`, allowing the v120.28 beta to coexist with an older installed build during validation.
- GitHub Actions build run 37378481902 completed successfully after the resource-string correction.
- Generated APK size: 5,911,264 bytes; archive contains Material/AndroidX/runtime resources rather than the previous minimal shell.
- APK SHA-256 from the successful build artifact: `30f5a48715279f419ae2610986ef28dbc6ed49bcc6f91bee1abceb513ca4898c`.
- Remaining validation before calling Android production-ready: install/launch on the target phone, OTP login on-device, Focus Desktop → Android round-trip, Android batch completion → Desktop review projection, and Audit origin verification.


## 2026-10-05 — Android v120.29 full Workspace

- Added a fourth Android module: **Workspace**, loaded by default.
- Embedded the complete Desktop workspace HTML inside the APK so Android exposes Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault, Health and About rather than only Focus/Audit/Account.
- Kept Focus, Audit and Account as native Android surfaces optimized for mobile.
- Desktop-style multi-profile Focus actions inside Workspace are redirected to native Mobile Focus so Android continues opening one Instagram profile at a time.
- Added Android WebView file chooser support so ZIP/JSON/HTML imports can be selected from the phone.
- Added Android bridge hooks for Instagram links and portable HTML exports.
- Added session bootstrap so the embedded Workspace can share the authenticated Supabase session/device identity with the native shell.
- Corrected system-bar insets so the toolbar no longer renders under the Android status bar.
- Android version bumped to 120.29.
- GitHub Actions run 37387118838 completed successfully.
- Verified compiled APK: 6,880,075 bytes, 904 entries, embedded `assets/ig_cleaner_workspace.html` = 1,670,732 bytes.
- APK SHA-256 from validated artifact: `ae6a02abd26c3cc09f9b735b162f4008c6e6a56c385d8b7a092312e50f3de30a`.
- Remaining device validation: install/launch on target phone, mobile ZIP import, Workspace navigation, Desktop ↔ Android Focus round-trip and export flow.


## 2026-10-05 — LIMÓN handoff: Android full workspace v120.29

### Estado actual
- Desktop estable/sincronizable: v120.27 con Supabase + OTP, Audit cross-device y Focus congelado/sincronizable.
- Android v120.28 fue una reconstrucción nativa Material que ya abre y compila, pero el usuario la rechazó como producto final porque seguía siendo un companion reducido y no exponía la amplitud funcional de la app Desktop.
- La dirección corregida es **IG Cleaner completo en Android**, no un companion recortado.
- Rama activa: `android-full-workspace-v120.29`.
- v120.29 conserva Focus / Audit / Cuenta como superficies Android nativas y añade **Workspace** como acceso al motor completo de Desktop.
- El Workspace empaqueta el HTML oficial de Desktop desde `desktop/` mediante Android Gradle `sourceSets`, evitando mantener una segunda copia funcional del motor.
- Navegación móvil actual: Workspace / Focus / Audit / Cuenta.
- Workspace carga el motor Desktop dentro de WebView con JavaScript, DOM storage, file access y bridge Android.
- El selector `<input type="file">` del Desktop abre el file picker Android, permitiendo importar ZIP/JSON/HTML desde el teléfono.
- Los enlaces de Instagram se enrutan a la app de Instagram cuando está instalada.
- Aperturas masivas desde el Workspace se redirigen/bloquean en Android a favor del flujo Focus de un perfil por vez.
- El bridge Android ya contempla transferencia de sesión/configuración, exportaciones hacia Descargas e integración con Focus nativo.
- Se corrigió el solapamiento visual con status bar usando WindowInsets.
- Se consolidó una sola implementación de Workspace tras detectar duplicaciones de variables/imports/insets durante el desarrollo.

### Validación
- GitHub Actions run `37388962937`: `gradle :app:assembleDebug` **SUCCESS**.
- El APK generado incluye el HTML Desktop oficial empaquetado como asset.
- Artifact ZIP de Actions: ~6.8 MB; APK inspeccionado previamente: ~7.8 MB.
- El Desktop HTML empaquetado pesa ~1.67 MB.
- El build incluye Material Components, AndroidX, RecyclerView, XML layouts, launcher resources, Workspace WebView, Focus, Audit y Cuenta.

### Release / ramas
- `v120.27`: pre-release publicada; primera sync Desktop ↔ Android.
- `v120.28`: pre-release publicada; app Android nativa abre, pero funcionalmente quedó demasiado reducida respecto a Desktop.
- `v120.29`: **todavía NO publicada ni fusionada a main** al momento de este handoff.
- No llamar v120.29 “lista” hasta instalarla en el teléfono objetivo y comprobar el Workspace real.

### Pendientes inmediatos para el siguiente chat
1. Eliminar/ignorar cualquier asset duplicado/obsoleto de Workspace que no sea el HTML oficial empaquetado desde `desktop/`.
2. Actualizar About/strings Android de v120.28 → v120.29 donde aún quede identidad vieja.
3. Revisar el workflow Android para que no quede acoplado innecesariamente a una sola rama temporal.
4. Instalar el APK v120.29 en el teléfono objetivo y verificar:
   - arranque sin crash;
   - status bar/insets correctos;
   - Workspace visible y navegable;
   - módulos Desktop disponibles: Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault, Health, About;
   - selector de ZIP desde Android;
   - persistencia de datos del Workspace;
   - OTP/sesión Android;
   - Focus Desktop → Android;
   - finalización Android → revisión visible en Desktop;
   - Audit con origen Android/Desktop.
5. Solo después de esa validación: merge a `main` y release formal `v120.29`.

### Decisión de producto
Android debe ofrecer el mismo producto/datos que Desktop, pero no necesariamente la misma interacción. La diferencia intencional principal es Focus: Desktop puede abrir múltiples perfiles; Android usa checklist y apertura uno-a-uno. No volver a reducir Android a una app de solo Focus/Audit/Cuenta.


## 2026-10-05 — LIMÓN handoff — Android full workspace v120.29

### What changed in this work session
- v120.27 established the first Desktop ↔ Android sync architecture with Supabase, email OTP authentication, device-aware review/audit events and frozen Focus batches.
- v120.27 Android was rejected as a real product build after the distributed APK was only ~25 KB and failed to launch reliably on the target phone.
- v120.28 rebuilt Android as a conventional Material/AppCompat application. GitHub Actions compiled successfully and the app launched on-device, but user validation found that it exposed only the companion surfaces and did **not** provide the feature breadth of Desktop.
- v120.29 therefore changes the Android product model from “small companion” to **full Android workspace + native mobile tools**.

### v120.29 current architecture
- Branch: `android-full-workspace-v120.29`.
- Android version metadata: `versionCode 12029`, `versionName 120.29`.
- The official Desktop HTML under `desktop/` is packaged into the Android APK through the Android Gradle main asset source set.
- Android starts on a **Workspace** tab that loads the real Desktop app in a WebView instead of reproducing its modules separately.
- Desktop surfaces available through Workspace include the existing Home/Command Center, Review, Mutuals, Followers, Pending, Import, Insights, Changes, Vault/exports, Health, About and other current Desktop modules.
- The Android bottom navigation also keeps native **Focus**, **Audit** and **Cuenta** surfaces because those workflows benefit from mobile-specific interaction.
- Native Focus opens one Instagram profile at a time and uses a checklist; opening and reviewing remain distinct events.
- Native Audit preserves source-device provenance and does not rewrite the original review timestamp.
- Cuenta uses the same email OTP / Supabase session as Desktop; end users do not enter backend URLs or keys.
- Workspace bootstrapping transfers the Android session/device identity into the embedded Desktop engine.
- Android intercepts Instagram links and routes them to the Instagram app/browser.
- Desktop multi-profile opening is redirected/limited on Android so bulk browser-tab behavior does not become the mobile workflow.
- Android file chooser support allows the embedded Desktop importer to request files from the phone.
- Workspace export bridge can save generated HTML exports into Android Downloads.
- System-bar insets were corrected so app content no longer renders underneath the Android status/navigation bars.

### Backend/privacy boundary
- Supabase is now an implemented backend for **sync metadata/state**: devices, Focus batches/items, audit events and projected profile review state.
- Authentication is email OTP.
- Row Level Security is enabled by the app schema; clients use only the publishable key.
- Raw Instagram ZIP/JSON/HTML export contents remain local to the client workflow and are not intentionally uploaded as part of the sync contract.
- Review metadata may sync across Desktop and Android; raw export backup is a separate future decision and is not implied by current sync.

### Validation at chat close
- GitHub Actions run `37388962937` on `android-full-workspace-v120.29` completed **SUCCESS**.
- The final successful build occurred after consolidating duplicate Workspace implementations, restoring the loading indicator and fixing root window insets.
- The Android build artifact `ig-cleaner-companion-debug` was produced by that run.
- The full Workspace uses the official Desktop file `desktop/ig_cleaner_pro_v120_27_synced_companion.html` as the packaged engine.
- No v120.29 GitHub Release has been published yet.

### Known pending work / next-chat starting point
1. Remove the obsolete duplicate `android/app/src/main/assets/ig_cleaner_workspace.html` file if still present; Gradle now packages the official `desktop/` asset directly.
2. Update About/product text that still identifies Android as v120.28 where applicable.
3. Make the Android companion CI trigger reusable/generic instead of branch-specific to v120.29.
4. Update `README_SYNC.md` fully for the current OTP + full-workspace architecture.
5. Install the final v120.29 artifact on the target phone and validate:
   - cold launch;
   - Workspace renders Desktop modules;
   - status-bar inset;
   - Android ZIP/file chooser import;
   - OTP/session persistence;
   - Desktop → Android Focus round-trip;
   - Android completion → Desktop reviewed state;
   - Audit device provenance;
   - Workspace HTML export to Downloads.
6. Only after those checks, merge `android-full-workspace-v120.29` to `main` and publish GitHub pre-release `v120.29`.
7. Do not modify the stable Desktop import/JSON parsing semantics while finishing Android parity.

### Handoff rule
The next chat should continue from this section instead of reconstructing the Android work from screenshots or older v120.27/v120.28 assumptions.

## 2026-10-05 — Android v120.29 single Workspace asset hardening

- Resumed from handoff trigger **LIMÓN** on `android-full-workspace-v120.29`.
- Inspected validated CI artifact from run `37388962937` and found two embedded Workspace assets:
  - `assets/ig_cleaner_pro_v120_27_synced_companion.html`
  - `assets/ig_cleaner_workspace.html`
- Both files were byte-identical: 1,670,732 bytes each, SHA-256 `cc9d3cbe83a453d20e7bd525af2a22f80e8be826d61d468df053b68efb320862`.
- Root cause: Android's default asset source remained active while `../../desktop` was added with `assets.srcDir(...)`, so Gradle packaged both the Android copy and the Desktop copy.
- Changed the Android source set to `assets.setSrcDirs(listOf("../../desktop"))` so the packaged Workspace has one source of truth: the official Desktop HTML.
- Confirmed Android user-facing version/About strings already report **v120.29 Beta**; no remaining v120.28 product text was found in the active Android files checked.
- Confirmed Android CI branch matching is generalized to `android-*`.
- Hardened Android CI to inspect the built APK and fail unless:
  - the official Desktop Workspace asset is present;
  - its packaged size is greater than 1.5 MB;
  - the obsolete duplicate `assets/ig_cleaner_workspace.html` is absent.
- CI workflow now also triggers when its own workflow file changes.
- Desktop parsers, JSON import behavior, HTML evidence safeguards, Focus determinism and sync semantics were not modified by this cleanup.

### CI revalidation after single-asset cleanup

- Hardened Android CI run `37390702783` completed **SUCCESS** on commit `8cbd0f048453d87283e03ae7ae67ebb885314421`.
- Workflow artifact: `ig-cleaner-companion-debug` (artifact id `11380688614`).
- Extracted APK size: **6,880,202 bytes**.
- APK SHA-256: `bc706c76857a18a5fdfce3ffafa9a3edfe01188c952edc4c57667a86529397d9`.
- APK inspection confirms exactly one IG Cleaner Workspace asset:
  - `assets/ig_cleaner_pro_v120_27_synced_companion.html` — 1,670,732 bytes.
- Obsolete duplicate `assets/ig_cleaner_workspace.html` is no longer packaged.
- Current release gate: device validation remains required before merging to `main` and publishing v120.29 pre-release.

## 2026-10-06 — GitHub Copilot agent delegation

Added repository-level Copilot instructions and custom App Maintainer, QA Regression and Release Manager agents. The contracts preserve the canonical Desktop engine/workflows, Android parity requirements, local raw-export privacy boundary, Supabase workflow-metadata/RLS model, Focus/opened/reviewed semantics and device provenance.

Purpose: delegate bounded implementation, regression checks and release preparation to repository agents so cross-project ChatGPT work can focus on product decisions and coordination.

No product behavior, schema, version or release artifact changed in this infrastructure-only update.

## 2026-10-06 — ChatGPT-ready task intake

Added `.github/ISSUE_TEMPLATE/chatgpt-task.yml` so new implementation/audit tasks can capture the desired outcome, evidence, scope, acceptance criteria, required validation and release permission up front.

Purpose: reduce repeated context reconstruction in future ChatGPT sessions and make repository work resumable from a bounded GitHub Issue without changing product behavior.
\n

## 2026-10-06 — CI and distribution hardening

Added a unified repository CI gate for the real Desktop/local-Web and Android product paths.

Desktop CI now checks:
- full-document JSON parsing contract;
- local HTML/raw import pipeline;
- Review / Followers / Mutuals / Pending workflow presence;
- stable localStorage and IndexedDB identifiers;
- full-backup controls;
- duplicate static DOM IDs;
- inline JavaScript syntax;
- sanitized Instagram ZIP fixture structure.

Android CI builds the real debug app and verifies exactly one packaged Workspace asset.

Added `release/distribution-manifest.json` and `docs/UPDATE_AND_STATE_MIGRATION.md` to define the browser-state schema, migration rules, checksum requirements and safe Desktop/Android distribution policy.

Legacy version-specific release workflows no longer publish from a qualifying push to `main`. v120.29 additionally requires explicit manual `publish=true`. Release publication remains separate from CI/build success and real-device gates.

### Validation evidence

Pull-request CI run `37507759707` completed **SUCCESS** on branch HEAD `86e9e01038e779f9b3520efbb565924c5e75c854`.

Validated:
- Desktop local-app contract;
- full-document JSON parsing and local import surface;
- persistent localStorage / IndexedDB compatibility markers;
- required Review / Followers / Mutuals / Pending workflows;
- inline JavaScript syntax and static DOM ID uniqueness;
- repaired auditable sanitized Instagram export fixture;
- Android debug build;
- exactly one embedded Workspace asset.

No release publication was authorized or performed.

## 2026-10-06 — Official IG Cleaner Pro product identity adoption

Implemented the Michel's Lab canonical **Option 3 — stacked layers + sparkle** identity from `michels-lab/Michel-Software-Standards/shared-assets/product-logos/ig-cleaner-pro`.

Adopted surfaces:
- vendored canonical app-icon, mark and lockup SVGs under `branding/ig-cleaner-pro/`;
- Desktop/local-Web favicon/shortcut identity using the official app icon;
- Desktop startup splash using the official app icon;
- Desktop rail/in-app branding using the official transparent mark;
- Desktop About using the official lockup;
- Android adaptive launcher using the official mark over the canonical dark-blue background;
- Android startup/window splash;
- Android toolbar mark;
- Android Workspace loading surface;
- Android About dialog mark;
- Android product display name aligned to **IG Cleaner Pro**.

The Desktop artifact remains self-contained: runtime surfaces embed the canonical SVGs as local data URIs and do not hotlink the standards repository.

Added `tests/branding-contract.py` and wired it into unified CI to guard canonical asset presence, launcher/splash/About references and removal of the obsolete IG/check-style active branding.

**Validation status:** implementation complete; PR Desktop + Android CI must pass before Issue #6 is closed.

### Branding validation complete

Pull-request CI run `37512776514` completed **SUCCESS** on functional/test commit `da3021660ea83614c50f7adf7584b3f12b1fba48`.

Validated:
- Desktop local-app regression contract;
- official branding contract for vendored canonical SVGs and active Desktop/Android references;
- Desktop inline JavaScript syntax after splash integration;
- sanitized Instagram fixture contract;
- Android debug build with the official adaptive launcher/startup resources;
- exactly one embedded Workspace asset.

The only later branch change is this documentation entry. No sync/auth/review data model change and no release publication occurred.

## 2026-10-06 — Stable GitHub release v120.29 published

Published/refreshed **v120.29** as a normal GitHub Release (not a prerelease) after official branding adoption and hardened CI passed.

Release validation workflow: `37516998786` — **SUCCESS**.

Published assets:
- `IG-Cleaner-Pro-v120.29-Desktop.html` — self-contained Desktop/local-Web app;
- `IG-Cleaner-Pro-v120.29-Android-beta.apk` — Android beta companion;
- `IG-Cleaner-Pro-logo.svg` — official product icon source;
- `SHA256SUMS.txt` — integrity hashes for all distributed assets.

The release is stable for the Desktop/local-Web product. Android remains explicitly beta pending target-device and production-store validation. No claim of Google Play/production-device validation was made.

## 2026-10-06 — Intelligent Michel's Lab brand-adoption guidance

Repository instructions now explicitly route logo, launcher, splash/startup and About work through the Michel-Software-Standards Product Identity Standard and Brand Adoption Playbook.

The required interpretation is structural integration rather than sticker placement: replace active legacy identity, adapt canonical geometry to the existing product design language, preserve unrelated behavior, validate the build, and keep release publication separate unless explicitly authorized.



## 2026-10-06 — v120.34 canonical candidate consolidation

### Release/version reconciliation
- Consolidated active work onto `release/v120.34`; this branch is based on current `main` and is the authoritative v120.34 candidate.
- Next release target is exactly `v120.34`; GitHub prerelease must be false.
- No v120.34 release has been published from this work.
- Publication remains explicitly gated; validation workflows do not publish.

### Canonical identity / About
- Confirmed the master identity is stacked layers + upper-right sparkle; the old rounded-square IG monogram is legacy/rejected.
- Child SVG identity copies match the master canonical assets.
- Vendored the canonical Michel Duarte portrait byte-for-byte at `desktop/assets/michel_duarte_avatar.jpg` (git blob SHA `18fe1a68722850c3d8f918dc0799f46ffeb6dbaf`).
- Vendored the finalized Michel's Lab About lockup byte-for-byte at `desktop/assets/michels-lab/official-lockup.png` (git blob SHA `7fd48093968b31ddacd3098f5b15d962de580652`).
- Removed the embedded base64 portrait from Desktop About and linked the canonical assets instead.
- Unified visible Desktop release identity from stale UI 120.26/120.27 labels to UI v120.34.
- Desktop distribution is now a ZIP/bundle so the external canonical About assets are never omitted.

### Android repair and Focus autonomy
- Restored missing Android resource/dependency parity required by the current native shell.
- Android build again compiles with Home / Review / Focus / Activity / Profile resources.
- Restored native Android Focus creation for Review, Mutuals, Followers-you-don't-follow and Pending Requests.
- Android supports Focus 20 / 30 / 40, freezes the selected usernames in shared Supabase batch tables and refuses unsafe creation when historical review state has not synchronized.

### CI evidence
- Run `37561825709`: Desktop contract **SUCCESS** and Android build + embedded Workspace **SUCCESS**.
- Run `37559946743`: Android companion **SUCCESS**.
- Validation after the Android Focus-autonomy restoration is required before this candidate is handed off as final.
- Physical-device/round-trip testing is still a manual gate and is not claimed as completed.

### Release safety
- The historical v120.34 publisher from the divergent `release-v120.34` branch builds a debug/`.beta` APK while labeling the GitHub release stable; that workflow is not acceptable as the final stable publisher.
- A stable Android v120.34 publication requires a real release artifact with signing continuity; otherwise Android stable publication remains blocked.


## 2026-10-06 — v120.34 final candidate validation

- Reconciled the candidate onto `release/v120.34`; the divergent `release-v120.34` line is marked superseded and must not publish.
- Restored Android native Focus creation for Review, Mutuals, Followers-you-don't-follow and Pending in sizes 20/30/40.
- Restored the v120.30 Desktop sync bridge, including legacy-review normalization, list snapshots and complete workspace review-state publishing. This directly protects already-reviewed profiles from reappearing as unresolved merely because Android has only raw relationship lists.
- Preserved the Android system-bar inset hotfix so Samsung gesture/3-button navigation does not clip the bottom navigation.
- Replaced the embedded About portrait with the exact canonical Michel Duarte asset and added the finalized Michel's Lab production lockup.
- Added a centralized local-first privacy surface/documentation and explicit retention/deletion boundary.
- Added CI regression contracts for canonical branding/About assets, full sync bridge, privacy/data handling, Android Focus autonomy and navigation insets.
- Final consolidated CI run `37562844481`: **SUCCESS** across Desktop contract, sanitized fixture, branding, privacy, Android UX/Focus contract, distribution manifest, Android build and embedded Workspace verification.
- Android companion runs after the relevant functional changes also passed, including `37562748629`, `37562402633` and `37562024494`.
- Manual physical-device/Desktop round-trip remains pending and is not represented as completed.
- v120.34 has **not** been published by this work.
- Stable Android publication remains blocked until a real release artifact/signing path is established; do not relabel a debug `.beta` APK as stable.


## 2026-10-06 — Persistent Android production signing

Decision:
- Stable Android releases use one persistent signing identity for `com.michelslab.igcleaner`.
- Debug builds remain isolated as `com.michelslab.igcleaner.beta`.
- Normal IG Cleaner Pro GitHub releases must include the latest validated signed Android APK once signing requirements are configured.

Implementation:
- Added environment-backed production signing in `android/app/build.gradle.kts`.
- Release tasks fail before packaging if the four production signing inputs are missing.
- Added `release/android-signing.json` with the public certificate identity/fingerprint.
- Added `docs/ANDROID_SIGNING.md` with backup and GitHub Secrets procedure.
- Added `tests/android-signing-contract.py`.
- CI now smoke-tests `assembleRelease` using an ephemeral disposable CI keystore.
- The v120.34 release workflow now builds, verifies and attaches `IG-Cleaner-Pro-Android-v120.34.apk` after validating package ID, version and signer fingerprint.
- Added `*.jks` / `*.keystore` exclusions so private signing material cannot be accidentally committed through normal workflows.

Production signing identity:
- alias: `ig-cleaner-pro`
- certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`
- valid until: 9999-12-31 (practical non-expiring maximum)

Secret boundary:
- No production keystore bytes or signing passwords are stored in Git.
- Required repository secret names are `IGC_ANDROID_KEYSTORE_B64`, `IGC_ANDROID_KEYSTORE_PASSWORD`, `IGC_ANDROID_KEY_ALIAS`, and `IGC_ANDROID_KEY_PASSWORD`.

Validation status:
- GitHub Actions run `37568540656` — **SUCCESS**.
- Desktop/state/branding/privacy/signing contracts — PASS.
- Android debug build + embedded Workspace verification — PASS.
- Signed `assembleRelease` smoke test with ephemeral CI keystore — PASS.
- Release APK package identity verified as `com.michelslab.igcleaner` / `12034` / `120.34` — PASS.
- Real-phone validation remains separate and must not be claimed from CI.


## 2026-10-07 — v120.34 signed Android release closeout

Release state:
- **v120.34** is published as a normal GitHub release (`prerelease=false`).
- Final publisher run `37574744462` completed **SUCCESS**.
- Stable Android artifact: `IG-Cleaner-Pro-Android-v120.34.apk`.
- Stable Desktop artifact: `IG-Cleaner-Pro-Desktop-v120.34.zip`.
- Checksums, privacy document and official product logo are attached to the same release.

Production signing:
- package: `com.michelslab.igcleaner`;
- versionCode/versionName: `12034 / 120.34`;
- alias: `ig-cleaner-pro`;
- certificate SHA-256: `99C1DD7B0ED32B758AFAD253A774D85DC7A4481990342B5D09B54B9DCCA84F33`;
- certificate validity: `9999-12-31`;
- GitHub Actions signing secrets configured and successfully consumed;
- private signing material remains outside Git.

Release verification:
- production keystore restoration — PASS;
- signer identity verification — PASS;
- signed `assembleRelease` — PASS;
- stable package/version verification — PASS;
- exact signer fingerprint verification — PASS;
- release bundle verification — PASS;
- GitHub release publication — PASS;
- Android asset presence verification — PASS.

CI note:
- two earlier publisher attempts failed only because the verification script assumed an older `apksigner` output label/field layout.
- PR #16 and PR #18 corrected the verifier.
- the APK and FINAL-9999 signing identity themselves were valid; the final publisher passed end-to-end.

Governance:
- v120.34 is closed as the current stable baseline.
- next development/release target is **v120.35**.
- v120.34 authorization must not be reused for v120.35.
- physical-device validation remains separate from repository/CI evidence.


## 2026-10-07 — v120.35 infrastructure, RLS and synchronized-data privacy

Stable baseline:
- v120.34 remains the current published stable release.
- v120.35 is development only until explicit release authorization is given.
- FINAL-9999 Android signing identity is unchanged.

Generic release publisher:
- Added `.github/workflows/release.yml` as the canonical governed publisher for v120.35+.
- Version/tag come from `.michelslab/release-request.json`.
- Dynamic Desktop/Android artifact names come from manifest templates.
- The publisher validates explicit authorization, next-release target, Desktop/Android version parity, regression contracts, production signer fingerprint, stable package identity and normal/non-prerelease channel.
- Historical `.github/workflows/release-v12034.yml` remains manual/closed.

Supabase RLS:
- Added `supabase/tests/rls_isolation.sql` with 35 pgTAP assertions across all seven sync tables.
- Added `tests/rls-contract.py` and a dedicated CI job that starts local Supabase, applies `supabase/schema.sql`, runs the cross-user RLS suite and stops the stack.
- The live Supabase project was also checked transactionally with two temporary JWT subjects; user 2 saw only its own temporary device row. Transaction rolled back.
- Live policy inventory confirms CRUD policies are constrained by `auth.uid() = user_id`.
- Supabase security advisor returned no RLS exposure finding. A separate Auth warning remains for leaked-password protection being disabled.

Cloud data export/delete:
- Desktop Privacy now exposes **Exportar datos de nube** and **Borrar datos de nube**.
- Android Account now exposes **Export synchronized cloud data** and **Delete synchronized cloud data**.
- Export reads every RLS-visible row from devices, audit_events, focus_batches, focus_batch_items, profile_state, list_snapshots and workspace_state, with pagination, into `ig-cleaner-cloud-export-v1` JSON.
- Delete removes synchronized rows in FK-safe order under the authenticated user's RLS session.
- Cloud deletion does not delete the original Instagram ZIP/JSON/HTML export or independent Vault/file backups.
- Both clients sign out after cloud deletion so automatic sync cannot immediately re-upload remaining local state.

Version identity:
- Desktop visible UI: v120.35.
- Android versionCode/versionName: 12035 / 120.35.
- Android package stays `com.michelslab.igcleaner`; debug stays isolated with `.beta`.
- Desktop legacy filename/localStorage identifiers are preserved because they are compatibility identifiers, not visible release identity.

Validation status:
- Implementation complete on branch `development/v120.35-infra-privacy`.
- Full current-head PR CI is required before merge.
- Physical-device validation of Android privacy/download flows remains separate evidence.


### RLS performance hardening
- Applied Supabase migration `optimize_rls_policies_v12035` to all seven synchronized tables.
- Policies are now explicitly `TO authenticated` and compare ownership using `(select auth.uid()) = user_id`.
- Data semantics did not change; no application rows were deleted or rewritten.
- Supabase Performance Advisor: **28 Auth RLS Initialization Plan warnings → 0**.
- Live transactional smoke after migration: authenticated user 1 saw exactly 1 own temporary row and 0 foreign temporary rows; transaction rolled back.
- Remaining advisor items are unrelated to row isolation: leaked-password protection is disabled in Auth, and one unused-index notice is informational.


### v120.35 current-head validation state
- PR #20 head validation was requested repeatedly on GitHub Actions.
- GitHub Actions did **not** execute any workflow steps on the current head: Desktop, Android and Supabase jobs terminated before runner steps/logs existed. Re-running failed jobs produced the same zero-step result. This is an external runner/Actions blocker, not a passing or failing application test result.
- CI trigger policy was hardened to avoid duplicate `push` + `pull_request` runs on development branches and now uses concurrency cancellation for superseded PR runs.
- Current-head Desktop static validation via repository content: 16 inline scripts parsed successfully, 0 duplicate static DOM IDs, required v120.35/privacy/sync tokens present.
- Current-head Android structural validation: `MainActivity.java`, `SyncApi.java`, Gradle Kotlin and modified XML resources have balanced lexical/tag structure; this is **not** a substitute for `assembleDebug`.
- Live Supabase post-migration cross-user check: user 2 affected 0 user-1 rows across all seven synchronized tables for UPDATE attempts; temporary rows were transactionally rolled back.
- Supabase Performance Advisor after migration: 0 Auth RLS Initialization Plan warnings; one informational unused-index notice remains.
- Merge remains blocked until same-SHA executable CI/build evidence is available.


## 2026-10-07 — v120.35 direct validation while GitHub runners are unavailable

GitHub Actions:
- PR #20 head CI run `37696174790` failed before any runner step executed.
- retry attempt 2 reproduced the same pre-run failure for Desktop, Android and Supabase jobs;
- job payloads contain no steps and job log blobs do not exist;
- therefore this is treated as a runner/platform/account execution blocker, not as a failed product assertion;
- PR #20 remains Draft and must not merge until executable same-SHA CI passes.

Direct exact-branch validation:
- all 16 inline Desktop scripts parse successfully;
- 0 duplicate static DOM IDs;
- v120.35 identity, privacy, generic publisher and RLS contract sweep passes;
- targeted corrected sweep: 11/11 PASS;
- Android Java/Gradle delimiter structure passes;
- modified Android XML structure passes.

Live Supabase RLS behavioral evidence:
- rollback-only transaction seeded user 1 and user 2 data across all seven synchronized tables;
- authenticated user 2 saw exactly one own seeded row in every table;
- UPDATE attempts against user 1 affected 0 rows in all seven tables;
- DELETE attempts against user 1 affected 0 rows in all seven tables;
- authenticated own-row INSERT succeeded;
- transaction rolled back, leaving no test rows behind.

Advisor state after the optimized RLS migration:
- Security Advisor: no RLS exposure finding; one unrelated warning remains for leaked-password protection disabled;
- Performance Advisor: 0 Auth RLS Initialization Plan warnings; only the informational unused `audit_events_user_device_idx` notice remains.


## 2026-10-07 — v120.35 release-contract fix and CI minute protection

Release-contract regression found and fixed:
- the generic publisher itself was version-agnostic, but `tests/release-publisher-contract.py` and the CI manifest check still required the old closed v120.34 request state;
- an explicit v120.35 authorization would therefore have caused validation to fail at release time;
- contracts are now state-aware: they accept either the closed current-stable request or an explicitly authorized request that exactly matches `releasePolicy.nextRelease`;
- Android signing contract now derives the expected candidate version/code from `releasePolicy.nextRelease`;
- privacy contract derives the current stable Desktop artifact from the distribution manifest instead of hardcoding v120.34;
- simulated closed v120.34 request + authorized v120.35 request validation: PASS.

CI usage hardening:
- heavy Desktop / Android / Supabase jobs are skipped while a PR is Draft;
- `ready_for_review` explicitly triggers the full CI gate;
- this prevents long-lived Draft PR edits from repeatedly consuming GitHub-hosted runner minutes.

Final runner probe:
- PR #20 was marked Ready for review on head `e5a49aa55053599636a7c55d91df7b39df7207b9`;
- run `37702842845` created Desktop, Android and Supabase jobs;
- all three terminated before any step started and expose `steps: []`;
- PR #20 was returned to Draft;
- merge remains blocked pending a real same-SHA runner execution.

## 2026-10-07 — Master-first About governance synchronization

- Verified current master `michels-lab/Michel-Software-Standards` `standards/ABOUT_STANDARD.md`, `standards/PRODUCT_IDENTITY_STANDARD.md`, `AGENTS.md` and `brand/developer-profile.json` require exact `TOOLS WITH IDENTITY.` studio slogan and paired author/studio About composition (side by side where width permits; responsive stack on narrow screens).
- Updated local `AGENTS.md` plus app-maintainer, QA-regression and release-manager agent contracts to require fresh master reads before About work and rendered Desktop/Android verification.
- This change is **instructions only**: it does not alter UI assets, About implementation, app versions or published releases. Visible About layout/social icons/Android device acceptance remain unverified and open.

## 2026-10-07 — v120.35 CI and Desktop About closure work

- Verified public `michels-lab/IG-Cleaner-Pro` and restored real development-branch GitHub Actions execution after pre-run runner failures.
- Corrected stale v120.34 branding contract and privacy sign-out wording assertion; current Desktop and Android CI jobs subsequently executed successfully on run 37714614593, while Supabase failed during startup.
- Root cause of Supabase startup failure: the `20261007_optimize_rls_policies.sql` migration referenced public sync tables before a clean local stack created them. Added `supabase/migrations/20261006_initialize_sync_schema.sql` to initialize tables first; same-head successful Supabase CI remains pending.
- Updated Desktop About to display canonical `TOOLS WITH IDENTITY.` studio slogan, recognizable inline SVG icons for all five social controls, and master canonical URLs. Official portrait and Michel's Lab logo file bytes were not changed.
- Added Desktop About branding contract checks for official slogan, canonical social links/icons and hierarchy.
- Native Android `showAbout()` is still a plain message dialog. Full master-compliant native About, on-device visual acceptance, real ZIP import/Focus QA and authenticated Desktop↔Android round trip remain open. No release authorized or published.

## 2026-10-07 — Repository transferred to Michel's Lab organization

**Change:** repository ownership moved from `michels-lab/IG-Cleaner-Pro` to `michels-lab/IG-Cleaner-Pro`.

**Active references updated:** `.michelslab` governance, agent/Copilot authority and the distribution manifest now use the organization-owned repository and `michels-lab/Michel-Software-Standards`.

**Preserved intentionally:** Michel Duarte personal developer/social identity remains under `realmichelduarte`. No release is authorized by this migration change.

**Validation:** branch CI is required before merge.


## 2026-10-07 — Native Android About implemented and PR #20 merged

- Replaced Android's text-only About dialog with a native product-first panel, byte-identical canonical portrait and Michel's Lab studio lockup, visible `TOOLS WITH IDENTITY.` slogan, and Instagram/Facebook/LinkedIn/GitHub/Email icon-plus-name links.
- The new Android native panel stacks its paired author/studio columns on narrow screens, and reads the installed application version rather than hardcoding the release name.
- Desktop About now uses the canonical slogan and recognizable SVG social icons with standard canonical URLs.
- Release workflow retains separate explicit publication authorization; no v120.35 GitHub Release was published by this work.
- PR #20 merged after exact-head Desktop, Android and Supabase CI passed (run 37716560654); main merge commit `fd45720e09d6fe7cb399f0eafe0928d97d40f592`.
- Actual phone UX, live authenticated Desktop↔Android round trip, real ZIP imports, cloud export/download and cloud delete must still be validated on target devices; do not claim those device checks complete.


## 2026-10-08 — v120.35 production GitHub Release published

- Explicit user instruction **“dale release”** authorized v120.35 normal/stable GitHub publication on 2026-10-08.
- Generic publisher GitHub Actions run **37737077156** ended **SUCCESS** on release source commit `0e4b0c3d5b803436fd453c23e51dce1505871d8a`.
- Published normal release `v120.35` (`prerelease=false`) with signed production Android APK, Desktop ZIP, canonical logo SVG, privacy notice and `SHA256SUMS.txt`.
- Production Android certificate identity was verified by the publisher; package `com.michelslab.igcleaner`, version `120.35`, persistent FINAL-9999 signer.
- Release request authorization consumed (`authorized=false`, `status=published`), distribution manifest current stable changed to `v120.35`, next governed candidate advanced to `v120.36`.
- The generic publisher now safely skips already-published/unauthorized request changes to avoid accidental duplicate publication. CI contracts made version-aware instead of relying on former hardcoded v120.34.
- Pending real-phone acceptance is tracked in issue #24, including update-over-v120.34, ZIP import, Focus, sync and cloud controls. Not tested by GitHub CI, and no Google Play release claimed.
