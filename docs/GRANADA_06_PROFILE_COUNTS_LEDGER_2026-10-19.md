# GRANADA #6 — Profile Counts pacing-ledger integrity (2026-10-19)

**Issue:** [#146](https://github.com/michels-lab/IG-Cleaner-Pro/issues/146). **Status:** isolated source candidate, tests/CI required, not merged or released. Current published stable v120.53; next reserved v120.54.

## Reproduced source-level gap
- `load_history()` previously required a JSON array but ignored invalid array entries, including booleans, strings, nulls, nonfinite values, zero/negative timestamps and implausibly future timestamps. A parseable but corrupted ledger could silently drop previously counted visits and allow Profile Counts to resume before the user's scheduled rest.
- `load_batch_state()` accepted JSON boolean counters as integers, accepted incomplete/malformed `every` and `minutes` configuration, and could permit invalid persisted batch progress to be reset when resuming.
- This is a durable-account-state/rate-limiter integrity problem, not an Instagram DOM or Chrome login fix. It does not authorize faster automation.

## Implementation
- Fail closed on invalid persisted visit entries, with an explicit message and **no rewrite** of the saved ledger. Genuine valid events older than 24h remain eligible for pruning from the in-memory rolling budget; newly saved files remain compatible.
- Validate persisted batch-rest count, time, interval and disabled-state consistency before resuming. Reject malformed values and preserve the saved file rather than silently resetting.
- Add `tests/test_granada_pacing_integrity.py`: malformed-but-valid JSON records, NaN/Infinity, future times, expired historical events, previously valid rate records and long batch rests, disabled configuration, no alteration of original bytes.
- Route regression tests through isolated `.github/workflows/profile-counts-ci.yml` and `.github/workflows/profile-counts-windows-preview.yml` without editing shared `ci.yml`, owned by active [English PR #143](https://github.com/michels-lab/IG-Cleaner-Pro/pull/143).

## Boundaries
- Does not touch Developer Android issue [#135](https://github.com/michels-lab/IG-Cleaner-Pro/issues/135), Desktop English UI PR #143, Chrome action robot, Instagram credentials, signed APK identity, raw imported ZIP data, rate settings or release manifests.
- Existing owner sessions and errors (#77/#107) still require acceptance on the installed public release; offline fixtures do **not** prove Instagram access.
- No publication, merge, cloud mutation or automated Instagram unfollow is authorized by this issue.

## QA status
Await exact-head CI and Windows install smoke. Merge only after required tests actually pass; record SHA and any known gaps afterward.
