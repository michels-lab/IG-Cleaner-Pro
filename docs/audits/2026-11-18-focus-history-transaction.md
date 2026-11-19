# GRANADA 2026-11-18 — Atomic Focus bulk history on storage failure

## Root cause (#360/#371)

The production `recordRowsHistory(rows,event,details)` ran `recordProfileHistory` for each profile **before** `saveProfileHistory()`. When localStorage denied a write (QuotaExceededError/SecurityError), the app's per-profile RAM history still contained the failed open/reopen events, although the persistent ledger had not changed. A subsequent unrelated successful history write could accidentally persist those rejected events. Reload would otherwise lose them, making Focus frequency/recheck and counters inconsistent. Unlike `markActiveFocusBatchUnconfirmed`, this bulk writer did not have rollback.

## Owning-source correction

- Before changing RAM, reject an already unreadable history instead of modifying it.
- Snapshot only distinct affected usernames and each original record's fields/reference (including the original events array).
- Execute the unchanged real per-profile recorder and unchanged durable history writer.
- If any mutation or disk write fails, restore existing record fields **in place**, delete only newly created *uncommitted* RAM entries and rethrow; never delete an existing durable history, Reviewed/Pending/protected decision, original batch or WAL record.
- Successful writes keep current per-profile counts, event limits and history serialization. Duplicates in input retain the existing semantics.

## Exact failure regression

Extend already CI-wired `tests/focus-history-compaction.test.cjs` with the actual production `ensureProfileHistory`, `recordProfileHistory`, `recordRowsHistory`, history loader/saver/codec executed in one VM. Simulated QuotaExceededError on a mixed cohort (existing profile twice, new profile once) must restore exact RAM JSON, preserve existing object and event-array identities, delete uncommitted new RAM row, and leave disk unchanged. A successful subsequent retry must persist exactly the intended events through reload. A corrupted/unreadable saved history must refuse mutation before a new row appears.

## Boundaries

Does not claim that a fully exhausted browser quota is fixed, or that two real Instagram Windows sessions and live Unfollow/Cancel are verified. Previous official stable v120.80 remains published and immutable; next v120.81 is reserved but unauthorized. Changes are source only, do not access owner Instagram sessions and require exact-head CI plus physical owner browser acceptance for closing #360/#371.
