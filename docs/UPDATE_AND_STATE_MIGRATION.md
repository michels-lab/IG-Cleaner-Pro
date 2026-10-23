# IG Cleaner Pro — Update, Distribution & State Migration Contract

**Published stable: [v120.58](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.58). Next reserved version: v120.59 (not published).** The built-in Windows updater checks the published GitHub stable channel without installing anything automatically; downloading and launching the verified Setup both require explicit owner action. This document reports the published channel, not the candidate asset names in the distribution manifest.

This document defines the safe update path for Desktop/local-Web and Android. It is an engineering contract, not a claim that every delivery channel is already production-ready.

## Distribution

### Desktop / local-Web
The **primary Desktop release artifact is the standalone HTML** declared in `release/distribution-manifest.json`: `IG-Cleaner-Pro-Desktop-v{version}.html` (currently v120.58). Download and open it directly: the original application icon, author portrait and Michel's Lab logo are embedded as data URIs, so no extraction or additional assets folder is needed. The ZIP (`IG-Cleaner-Pro-Desktop-v{version}.zip`) remains an **optional full package** containing the HTML entrypoint and original independent assets. Both belong on the same GitHub release beside the signed Android APK and must be listed in `SHA256SUMS.txt`. A Desktop update must never require uploading the user's Instagram export or browser state.

Before any update that changes persistent state, the user must be able to export a full backup from Vault. Replacing the HTML file must preserve the browser origin when state continuity is expected; opening the app from a different origin, path, or browser profile can create a separate local-storage context.

### Android
GitHub Releases distribute the signed stable Android APK directly; read the current stable version from `release/distribution-manifest.json` (currently v120.58). Google Play distribution is separate and requires target-device/update-path validation; publication on GitHub is not Google Play publication.

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
