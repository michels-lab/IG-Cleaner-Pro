# GRANADA 2026-11-18 — Keep every cloud review sync on one immutable Instagram generation

## Production root cause (#360, cross-account sync)

The REST transport was already protected from A→B→A during **one** request, but `readCompleteProfileState()` can make 10+ GET requests to download 9,896 saved reviews. Its cross-page guard and four-second cache checked only the signed-in app user and active Instagram account string. If A→B→A occurred **between** two GET calls, a later call could legitimately start under the new generation while the existing scan retained rows fetched before the switch, silently merging generations and publishing/caching a mixed snapshot. The per-request REST epoch check cannot detect a switch that occurred between requests.

`pushProfileState()` has a related multi-POST defect: it captures local review rows and awaits the remote preflight, then submits up to 500 rows per POST. If A→B→A occurs between POSTs, a request-level guard can accept the *next* POST in the new generation but still use the old local rows.

## Fix in product sync source

- Capture owner, Instagram active slot **and generation** at the start of the complete paginated download; after every response require all three to match, including when an empty terminal page triggers cache publication. Cache entries carry and require the original generation even for same owner/account within four seconds.
- Before local review snapshot upload, capture the same three identity fields; verify again after the complete remote preflight, before **each** 500-row POST and after each response. If the generation changed, stop immediately without sending another chunk. Previously durable rows remain intact; no automatic replay, no destructive migration, no other-account writes.
- Error messages are generic and contain no Instagram usernames/tokens or private review content. Existing stable single-account pagination and monotonically newer review merge semantics are preserved.

## Regression with real production functions

Extended CI-wired `tests/cloud-review-scope-cache.test.cjs` executes the actual read/push JS source in a VM:
- Return to account A during delayed **second** GET page; the entire scan must reject and may not publish the earlier page.
- The same account in a later generation must fetch fresh results, while an unchanged generation still uses the scoped cache.
- Upload 501 sample review records in two 500-row POST batches, hold the first response, switch A→B→A and release it. Reject the original upload before a **second** POST; this must not send old A data into a newly selected account generation.
- Existing 9,896-row pagination/capped-server tests, owner/account scope tests, cloud monotonicity tests and storage rollback tests remain wired to CI.

## Verification and release boundary

No actual Instagram API or real owner profiles are accessed; fixtures are synthetic. This is source correctness and a negative multi-request race regression, not physical acceptance of both Windows account windows, Focus opening, or Android/HTML sync with owner data. Issues #360/#371/#377 stay open. Official published stable v120.80 remains immutable. New source must pass exact-head CI; no unapproved v120.81, Developer edition or RC release.
