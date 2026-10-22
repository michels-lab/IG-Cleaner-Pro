# GRANADA #28 — Developer-only forensic classification: presence is not zero-click evidence

Date: 2026-10-21 · Product scope: **IG Cleaner Pro**.

## Root-cause evidence (redacted and synthetic only)

An owner-installed Developer read-only aggregate report raised malformed action-evidence and unreadable-journal findings. This does **not** identify which real action, if any, took place. The installed report did not embed a source SHA (`source_revision=unknown`), so do not claim it exactly matches current source without the installed executable build identity.

Verified current repository source issue: `tools/developer_audit.py` treated an existing owner/account/task journal key with a non-object body, an empty object, or no status as **untouched** in pending-cohort totals; it also treated a **present null** `click_intent` as absence in strict no-click classification and permitted a terminal record with a malformed phase marked `outcome_recorded=true`. This is inconsistent with the main Windows action worker's already fail-closed `_invalid_saved_action_record` logic in `tools/profile_actions.py`.

There is **no verified evidence** that malformed entries were actually retried or that an Instagram relationship changed. However, treating unknown saved evidence as “untouched” in the Developer diagnostic is false assurance and must be corrected before recommending any wave.

## Minimal fix and non-goals

- In the Developer auditor, **only an actually absent journal key** is classified as untouched. Existing non-object, empty, unknown-status, malformed intent, and unknown-phase entries count as uncertain; pending cohorts remain saved.
- In Developer's strictly historical zero-click predicate, any **present** `click_intent` key (even null or empty) blocks zero-click eligibility. An explicit allowed phase and terminal `outcome_recorded is True` is required for an action with saved click metadata to be counted as a *recorded terminal*, **not as confirmed real Instagram success**.
- No original action journal, batch approval, saved 40-person cohort, account ID, Chrome state, protection list, account relationship, client DOM, credential or cloud sync record is changed. Only read-only forensic classification and synthetic tests change. The main action worker already fails closed for malformed records and is not modified.
- `tests/test_developer_audit.py` adds synthetic malformed/non-object, missing-status, null-intent, invalid-phase, safe-preclick, recorded-terminal and truly absent-key cases. It asserts exact scope counts, immutable on-disk source journal and batch bytes, and redacted report/prompt with no synthetic target identifiers.
- Continue to gate real owner Instagram read-only probes on separate account identity; `LOGIN_REQUIRED` and `SECURITY_CHALLENGE` are zero-click stops, **not** Unfollow/Cancel success. No CAPTCHA bypass or auto-replay.

## Acceptance

Merge only after exact PR CI passes (Developer read-only audit, robot history/WAL regression, installed Windows where applicable and rendered UI). No RC or version bump; existing released v120.55 is unchanged. Main pending real signed-in owner Unfollow/Cancel issue remains open until independent post-action verification.
