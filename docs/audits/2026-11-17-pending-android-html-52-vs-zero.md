# P0 · Android 52 Pending vs HTML 0 — preserve source truth (2026-11-17)

## User report and evidence boundaries

The owner reports **52 Pending on the mobile Android app** and **none in the standalone HTML**. The owner believes HTML reflects the correct current imported view. This is a **cross-surface inconsistency**, not proof that the mobile 52 are live Instagram requests or that an HTML 0 is an authoritative empty export. We did not access the owner's real Instagram account, ZIP bytes, Android device, Supabase user rows or private credentials.

## Root causes verified in source

1. **Distinct stores.** Android native `MainActivity.loadMobileWorkspace` gets `list_snapshots.pending` from owner/account-scoped Supabase; when offline, it displays locally cached data. The Desktop HTML loads its local Pending list, importing a newer authoritative source separately. Prior Android Home rendered `syncedPending` as ordinary **REQUESTS** with no import date, source distinction or stale-cache disclosure.
2. **Empty snapshot weakness.** Desktop `pullListSnapshots` used `if(current.length && Math.max(localAt,importAt)>remoteAt) continue`. A verified **newer empty Pending import** has `current.length===0`; therefore a read of an older nonempty remote snapshot could restore 52 saved usernames. The existing regression only tested an immediate, successful zero upload followed by pull. A missing Pending file, by contrast, is not evidence of zero and must preserve prior cloud history.

## Patch

- Desktop: respect the explicit `dirtyAt` timestamp for a newer empty imported Pending; remote snapshots may still fill a genuinely missing/unimported Pending list. No automatic deletion or overwrite on read. A later successful scoped upsert with a verified empty list is the only way to publish 0 as the new cloud snapshot.
- Android: fetch `captured_at` with per-account cloud list, show **SAVED REQUESTS / CACHED REQUESTS** instead of unqualified REQUESTS, and show date/provenance in the Requests tab. Label numbers as imported/synced, never live Instagram. Missing Pending snapshot is **unknown (—), not zero**. Persist provenance with the existing owner/account-scoped private cache and clear in-memory indicators on A→B→A/account switch. Focus refresh carries the same source context.
- No change to existing Pending reviewed/opened/protected history, original user ZIP, robot/action WAL, credentials, Instagram API, cloud table schemas or server data.

## Regression / physical acceptance

- `tests/cloud-list-snapshot-freshness.test.cjs`: same-account 52 older cloud vs newer explicit empty HTML, read-only pull preserves HTML 0, successful later publication updates remote to zero; no Pending import must **not** erase cloud 52.
- `tests/test_android_workspace_sync_races.py`: server-sourced/cached Pending provenance, missing snapshot unknown, cache persistence, two-account A→B→A, Focus refresh source, UI label.
- Required exact-head GitHub CI and Android/installed Windows runtime must pass before merge/release. Local source changes alone are not evidence of a user's actual pending records.

### Owner acceptance after a future official stable release

1. In **the same authenticated IG Cleaner account and the exact same @Instagram workspace** on both Desktop and Android, verify the HTML Pending section is **0 imported** rather than only **0 visible because of filters / missing Pending file**. If needed, import the same complete ZIP and ensure `pending_follow_requests.json` explicitly declares `relationships_follow_requests_sent: []`.
2. Perform the Desktop **Sync** action and check for successful completion. Then refresh Android on the same Instagram workspace. Android should show **0 saved requests** with the latest cloud import date, not 52 cached.
3. If Desktop never received a Pending file or cannot authenticate, **do not clear the older 52** or overwrite original data. Reconcile export source and profile identity first.

Stable release at start: [v120.79](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.79). This patch is source-only; **not present in v120.79**. Issue #24 physical two-profile sync acceptance stays open. No new release authorization/claim.
