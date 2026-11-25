## Granada 25-nov-2026 — v120.83 FINAL publicada: reparación de arranque

[Release oficial](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.83), exact tagged source `23a4759b0aae444e876f54017050f59a252720e3`, [publicador #45568444602](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45568444602) **4/4 SUCCESS**, nueve activos SHA-256. Instalador Windows y selector nativo instalado (dos botones y Cancel), actualización y conservación de datos, render visual y Android firmado en emulador aprobados. [Recibo](docs/GRANADA_V12083_FINAL_RECEIPT_2026-11-25.md). #416 aceptación física pendiente; #413 desarrollo independiente excluido. Ruta P0 **58% (7/12)**; v120.84 reservada sin autorización. No RC/beta.

---

## Granada v120.82 FINAL publicada — 24-nov-2026

[Release oficial](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.82), exact tagged source `84b84e7a5dec057a869b72fe149dfde3f037cf00`, [publicador #45358286199](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/45358286199) **4/4 SUCCESS**, 9 activos con SHA-256, Windows Setup instalado/iniciado/desinstalado, Android firmado instalado/iniciado en emulador y capturas Home/About verificadas. [Recibo](docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md). #409/#410/#411 incluidos. #413 y #414 son desarrollo posterior independiente; no incluidos. Avance **58% (7/12)**, aceptación física sigue pendiente #371/#377/#360/#164/#172. Autorización única consumida; v120.83 reservada no autorizada. No RC ni beta.

---

## v120.82 — FINAL release requested (24-Nov-2026)

Owner explicitly authorized official stable distribution for subsequent physical testing. Source #409, #410 and #411 integrated; #411 6/6 exact-head SUCCESS. Latest published remains v120.81 until governed publisher succeeds. All exact-source installer, signed APK, rendered UI and checksum gates remain mandatory. P0 58% (7/12), five real-account/device milestones pending. No RC, beta or Developer publication.

- [#409](https://github.com/michels-lab/IG-Cleaner-Pro/pull/409): account-bound cloud DELETE and export, preserve local history on registry refresh.
- [#410](https://github.com/michels-lab/IG-Cleaner-Pro/pull/410): reject hidden/offscreen/transparent identity controls.
- [#411](https://github.com/michels-lab/IG-Cleaner-Pro/pull/411): independent Automations batch status and 8-second local journal deadline, partial/unknown counts and retry.

---

# IG Cleaner Pro — Update, Distribution & State Migration Contract

**Published stable: [v120.83](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.83). Next reserved version: v120.84 (not published).** The built-in Windows updater checks the published GitHub stable channel without installing anything automatically; downloading and launching the verified Setup both require explicit owner action. This document reports the published channel, not the candidate asset names in the distribution manifest.

This document defines the safe update path for Desktop/local-Web and Android. It is an engineering contract, not a claim that every delivery channel is already production-ready.

## Distribution

### Desktop / local-Web
The **primary Desktop release artifact is the standalone HTML** declared in `release/distribution-manifest.json`: `IG-Cleaner-Pro-Desktop-v{version}.html` (currently v120.83 in official published releases; next v120.84 reserved but NOT authorized). Download and open it directly: the original application icon, author portrait and Michel's Lab logo are embedded as data URIs, so no extraction or additional assets folder is needed. The ZIP (`IG-Cleaner-Pro-Desktop-v{version}.zip`) remains an **optional full package** containing the HTML entrypoint and original independent assets. Both belong on the same GitHub release beside the signed Android APK and must be listed in `SHA256SUMS.txt`. A Desktop update must never require uploading the user's Instagram export or browser state.

Before any update that changes persistent state, the user must be able to export a full backup from Vault. Replacing the HTML file must preserve the browser origin when state continuity is expected; opening the app from a different origin, path, or browser profile can create a separate local-storage context.

### Android
GitHub Releases distribute the signed stable Android APK directly; read the current stable version from `release/distribution-manifest.json` (currently v120.83 in official published releases; next v120.84 reserved but NOT authorized). Google Play distribution is separate and requires target-device/update-path validation; publication on GitHub is not Google Play publication.

Publishing is explicit. CI/build success by itself does not authorize a release. Michel validates the official installed published release rather than branch or Actions preview artifacts. A branch merge alone is not a publication.

## Browser state schema

Current state schema: 1.

The current app persists state in two places:
- localStorage for review/protection/configuration/focus/history metadata;
- IndexedDB database ig_cleaner_pro_history, version 1, for relationship snapshots.

Existing localStorage keys are treated as stable public storage identifiers. Renaming or deleting a key is a schema migration and requires a migration function plus regression evidence.

## Migration rules

A future schema change must:
1. read the previous schema without deleting it first;
2. create a backup/export-compatible representation before destructive conversion;
3. migrate idempotently — rerunning migration must not duplicate or erase data;
4. preserve review/protected/snoozed/history semantics;
5. preserve active Focus batch recovery when possible;
6. preserve IndexedDB snapshots or explicitly convert them;
7. record the new schema number in release/distribution-manifest.json;
8. add or extend CI checks and fixture evidence;
9. document rollback behavior in PROJECT_LOG.md.

If migration cannot be performed safely, the update must stop and instruct the user to export/import a full backup rather than silently resetting local state.

## CI gate

Repository CI validates:
- Desktop HTML JavaScript syntax;
- required Review / Followers / Mutuals / Pending workflows;
- full-document JSON parsing contract;
- stable browser-state identifiers and backup controls;
- absence of duplicate static DOM IDs;
- sanitized ZIP fixture structure;
- Android debug compilation and embedded Workspace packaging;
- distribution manifest/release policy.

Device-only behavior (OTP persistence, Android to Desktop round trip, Downloads export, production signing and Play updates) remains a separate real-device gate.


## Privacy reference

See `docs/PRIVACY.md` for the current local-first boundary, synchronized-data scope, retention/deletion limitations and backup expectations.
