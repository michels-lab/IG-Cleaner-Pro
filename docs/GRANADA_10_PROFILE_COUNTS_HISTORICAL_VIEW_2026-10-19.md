# GRANADA #10 — Legacy Profile Counts dated-history evidence display (2026-10-19)

**Issue:** [#154](https://github.com/michels-lab/IG-Cleaner-Pro/issues/154). **Branch:** `granada/dated-counts-invalid-evidence-view-20261019`, base `main` `8697c9f412ca68ec9e62d2dd293d1b58261ba05e`. **Status:** isolated PR awaiting exact-HEAD CI, not released.

## Gap and scope
- GRANADA #7 prevents new invalid `status=ok` measurements entering the append-only dated history. However, *old* `.dated.csv` rows created before verification can still contain invalid counts, missing or future timestamps, or injected-looking CSV-formula content, and `read_dated_page` previously presented every historical `ok` as a verified measurement.
- A read-only view must not silently purge user evidence to repair the display. Modify only the paginated history response: when an old row is `ok` but fails the existing central `_valid_reading` predicate, show `status=invalid_evidence` and a warning that the measurement needs recheck.
- Keep the original bytes, ordering, page sizes and next offsets exactly intact; valid zero and approximate integer counts are still valid, and explicitly failed/unavailable rows retain their original statuses.
- Tests seed a genuine historic CSV containing both valid and invalid rows; assert correct statuses, warning, future/unsafe count handling, original byte-for-byte persistence, no accidental loss in pagination and correct measured zeros. Existing `tests/test_profile_counts_audit.py` is already invoked by normal Linux CI and installed Windows Setup CI; avoid new shared CI edits.

## Parallel work / release boundary
- Independent of [GRANADA #9 PR #153](https://github.com/michels-lab/IG-Cleaner-Pro/pull/153), which addresses the separate robot/bridge resumption of invalid earlier `ok` records. The two fixes affect disjoint implementation/test files and must be evaluated on exact HEAD before merge.
- English Desktop [PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143) and Android Developer acceptance [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135) remain separate.
- No Instagram relationship mutation, credential use, live cloud changes, production release or version bump. Public stable **v120.53** remains, next **v120.54** reserved/unpublished. Owner tests only official released assets.

## Acceptance
- Await exact-HEAD CI; source assertions do not prove real Instagram Profile Counts accuracy or owner physical Windows acceptance (#107/#77).
