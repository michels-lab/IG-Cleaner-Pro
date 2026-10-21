# Operación Granada P0 — Developer saved-cohort forensics (2026-10-21)

## Scope
Independent, non-mutating Developer Edition diagnostics for owner-reported **Run appears inert / 40-profile saved cohort vs selected size** (issues #172/#176). No action robot clicks, Chrome tab lifecycle, production sessions, protection journal, import, Supabase or release files are changed.

## Previous source state
- Audited action journal rows but could label legacy "No action clicked" text as retryable even when `click_intent` existed. The action-worker itself correctly prohibited replay.
- Counted an entry with `deferred_at` and no `approved_at` as an unapproved active cohort, producing a false approval warning.
- Did not correlate pending `*-batch-reviews.json` and matching action journal, so a Developer export could not distinguish untouched profiles, demonstrably no-click errors, uncertain click records and saved terminal observations.

## This source candidate
1. The Developer-only `_proven_preclick` classifier mirrors the action worker's constrained historical evidence rules: exact owner/session pre-click blocks and exact source-coded missing-control cases. **Any click-intent marker or interruption issue prohibits a retryable classification**, including malformed markers.
2. Pair active, neither approved nor deferred, batch files with the **exact hashed journal basename in memory only**. Count the pending cohort's unique valid targets as: untouched (record exists but no status), safe pre-click error, uncertain/manual, recorded terminal, missing/unreadable journal. The report never exposes usernames, IDs, owner, account, paths, or raw messages.
3. Count read-only recheck observations **separately**: observation never equals click/Reviewed. Flag missing journal and corrupt/duplicate targets without losing source records. Flag action attempts but zero terminal saved results, so Developer can triage the user's "0 confirmed" case without implying Instagram success.
4. Extend `ai_prompt` allowlisted numeric aggregates for AI diagnosis; forged text/secret keys remain stripped. Retain legacy schema name for compatibility with consumers, additive numeric fields only.

## Regression scenarios added
- An old pending cohort with confirmed outcome, proven pre-click failure, interrupted write-ahead click, generic error, intentionally malformed intent and one untouched row. Deferred and approved historical cohorts are excluded from pending counts.
- Matching journal missing, interrupted click carrying a misleading pre-click message, malformed and duplicate cohort targets, private username/batch values absent from audit and AI export.
- Saved local JSON files remain byte-identical after the read-only scan.

## Gates, limits and handoff
- **Code commit is source-only.** Tests added, but not claimed executed before same-SHA GitHub Actions reports results.
- Windows preview workflow already executes `tests/test_developer_audit.py`; CI workflow also includes it. Offline fixtures are not a real owner Instagram Unfollow/Cancel acceptance.
- Diagnostics cannot infer whether Instagram changed a relationship; terminal is a saved journal classification, not live proof.
- P0 action executor and tab wave implementation are **out of scope** and remain untouched. Official v120.54 remains stable; v120.55 not authorized/published. Issues #172 (live owner action acceptance) and #176 (full two-lane Automation Center UI) remain OPEN.
- Next step: inspect exact-head CI, address any failures on this branch, request QA review on PR; no auto merge/release. Other P0 code can proceed separately without modifying these files.
