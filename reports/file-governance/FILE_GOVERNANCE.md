# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 332; classified: 328; readable documents: 74; above read cap: 1; findings: 6.

## File roles

| Role | Count |
|---|---:|
| agent | 9 |
| asset | 20 |
| bitacora | 1 |
| build_script | 6 |
| config | 69 |
| database_migration | 5 |
| database_schema | 1 |
| document | 69 |
| index | 5 |
| installer_metadata | 1 |
| source | 42 |
| test | 79 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_V12066_FINAL_RECEIPT_2026-10-26.md. Next: Fix link or restore target (ID 90d3ae715cce769a)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_REVIEW_RECOVERY_AND_COLORS_2026-10-26.md. Next: Fix link or restore target (ID 0e4b57a9618c4cbe)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_V12065_FINAL_RECEIPT_2026-10-26.md. Next: Fix link or restore target (ID 8032832fed0ae6fc)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md. Next: Fix link or restore target (ID d6a887cd4cf4669d)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_NO_REPEAT_NEW_BATCH_2026-10-26.md. Next: Fix link or restore target (ID df925d8ba69bac5a)
- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 5 implementation/config paths changed since this log's last commit; examples: desktop/ig_cleaner_pro_v120_27_synced_companion.html, tests/automations-execution.test.cjs, tests/test_action_batch_history.py, tests/test_historical_recheck.py, tools/profile_actions.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 8a301c1b755796fc)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
