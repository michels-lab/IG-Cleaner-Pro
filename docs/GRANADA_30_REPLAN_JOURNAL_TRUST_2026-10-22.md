# GRANADA #30 — Trustworthy saved-cohort replan + structured missing-Following triage

Date: 2026-10-22. Product: **IG Cleaner Pro** only. No FoamLens/OpenFOAM code.

## Owner bug, source evidence, and root cause
The owner has reported selecting 10 while an earlier incomplete cohort contains 40 and robots seemingly do not perform an Unfollow. The published v120.55 remains unverified on real Instagram (#172/#164); four offline green workflows are not evidence of live action.

After the read-only audit correction (#208) we found a second, independently reproducible **action-worker source bug** in `ActionRobot.replan_incomplete_batch`: the predicate `not isinstance(journal.get(u), dict) or not journal[u].get("status")` classified existing non-object, empty and statusless journal entries as reusable despite potentially concealing old actions. This contradicted the main `start()` no-replay guard and the Developer auditor. The read-only `batch_review()` also dereferenced malformed `journal[u].get`, causing a crash, and `approve_batch()` could accept a superficially `ok` row with invalid `click_intent`.

## Corrective changes
- Replan only **genuinely absent** journal keys or validated **proven pre-click** outcomes. Missing/statusless/non-object/null-intent/armed click evidence is never eligible for a new 10-person wave. Preserve the original pending cohort, its original list/carryover, saved journal bytes, approvals and protections.
- Report malformed rows as `review` with `invalid_saved_action_evidence` instead of throwing or calling them untouched. Block approval of a batch containing an invalid saved action record, even if its status claims `ok`.
- When Unfollow cannot identify a *unique Following/Siguiendo control* after verified target and owner, re-prove owner then attempt the **same browser-local, GET-only** private following lookup from #207. Distinguish a positive exact-target following entry (`still followed; action control missing`) from refused request (403/429) or unavailable/partial data (unknown). Never infer success from absence and never send an undocumented GraphQL POST. Cancel Pending remains a separate, unchanged action flow.
- Keep existing source-native `_preclick_no_action` semantics: failed pre-click layout observations can enter a **future independently owner-approved** batch, but any saved write-ahead click is not replayable. A failed lookup does not grant follow/unfollow permissions.

## Regressions, acceptance boundary
`tests/test_action_batch_history.py`: synthetic saved 10-target cohort with malformed, null, empty, no status, null intent, uncertain click, provably safe no-click, absent targets; assert exact replan targets and carryover, intact journal bytes, protected non-approval. Test malformed `ok` refusal in batch approval. Mock Playwright and browser-local read-only transport to assert exact-target positive diagnostic, rate-limit stop, Cancel Pending isolation, no `.click()` or durable `on_pre_click`.

Exact-source PR CI includes core robot, offline Chromium public/private, Windows installed Setup, Android, rendered UI and RLS. **No real signed-in Instagram action or API endpoint verified by CI.** Publish a future official stable only after release governance authorizes and mandatory gates pass; no RC, no misleading Unfollow success claim.
