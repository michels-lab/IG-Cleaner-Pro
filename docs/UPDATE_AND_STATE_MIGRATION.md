# IG Cleaner Pro — Update, Distribution & State Migration Contract

This document defines the safe update path for Desktop/local-Web and Android. It is an engineering contract, not a claim that every delivery channel is already production-ready.

## Distribution

### Desktop / local-Web
The canonical v120.34 Desktop artifact is the bundle declared in `release/distribution-manifest.json`: `IG-Cleaner-Pro-Desktop-v120.34.zip`, containing the HTML entrypoint plus the canonical About identity assets. A Desktop update must never require uploading the user's Instagram export or browser state.

Before any update that changes persistent state, the user must be able to export a full backup from Vault. Replacing the HTML file must preserve the browser origin when state continuity is expected; opening the app from a different origin, path, or browser profile can create a separate local-storage context.

### Android
GitHub Releases may distribute validated beta APKs. Production delivery should use Google Play only after target-device validation, production signing, and update-path validation are complete.

Publishing is explicit. CI/build success by itself does not authorize a release.

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
