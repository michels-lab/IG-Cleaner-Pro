# GRANADA 2026-11-18 — Cross-account and cross-device cloud review freshness

## Root cause in production source

The Desktop `readCompleteProfileState()` function cached up to four seconds of cloud history without owner or Instagram account identity in its cache key. More importantly, both `pullProfileState()` and `pushProfileState()` could reuse that stale snapshot while reconciling fresh Reviewed/Pending decisions on another device. This makes the claim "merge newer cloud reviews before publishing" unreliable for the four-second window: an Android review can arrive after cache population, and a Desktop sync could still compare against the older cached page.

The paginated reader also verified its expected row total against the *current* account after each asynchronous REST page, without checking that the account had remained the same since the first page. Browser/reload switching usually interrupts work, but this was not a safe data-integrity guarantee.

## Implemented corrections

- Cache entries are now tagged with the exact signed-in user ID/email and the selected Instagram account slot. Other owner/account reads never reuse those entries.
- Reconciliation always passes `{fresh:true}` to both full download and write-preflight reads. The 4-second cache remains available only for non-reconciliation callers with an exact matching scope.
- Each awaited page rejects a changed account or signed-in owner before accumulating, caching, or applying old rows. No partial history is published as complete.
- Existing timestamp-based monotonic merge and paginated completeness checks remain intact.
- Dedicated `tests/cloud-review-scope-cache.test.cjs`, wired to `ci.yml`, checks scope isolation, fresh bypass, and delayed A-to-B response rejection.

## Additional durability correction

`pullProfileState()` previously applied downloaded Reviewed/Pending entries to in-memory sets/metadata, then wrote five localStorage keys inside `try { ... } catch {}`. A quota or SecurityError could therefore leave *new* counts visible but unpersisted; the next reload restored the older snapshot. If an error occurred halfway through the five writes, disk keys could also be mixed.

The new pull saves snapshots of all five in-memory collections, tracks the exact pre-write contents of all five storage keys and records which writes completed. Any failure restores only keys already changed, restores sets and metadata **in place** (preserving canonical object references), propagates a visible sync failure and skips render/statistics success. Successful reconciliation still merges only timestamp-newer records and renders after durable writes. A failed disk rollback is explicitly identified as requiring backup recovery; no automatic reset or deletion of confirmed user history occurs. `tests/cloud-review-storage-rollback.test.cjs`, wired to CI, tests a simulated failure on the third write plus subsequent success.

## Boundaries

This corrects an identified stale-cache/scope hazard but does not alone prove all issue #360 Focus counters or every write race are fixed. The multi-key localStorage durability and true concurrent multi-device review update path need separately validated handling. Tests use synthetic rows only, not the owner's actual Instagram. No account data, cookie, WAL, protected state or historical decisions were deleted. The official published stable remains v120.80; v120.81 is reserved and not authorized.
