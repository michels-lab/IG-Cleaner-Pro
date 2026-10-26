# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 327; classified: 323; readable documents: 69; above read cap: 1; findings: 2.

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
| document | 64 |
| index | 5 |
| installer_metadata | 1 |
| source | 42 |
| test | 79 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_NO_REPEAT_NEW_BATCH_2026-10-26.md. Next: Fix link or restore target (ID df925d8ba69bac5a)
- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 4 implementation/config paths changed since this log's last commit; examples: tests/automations-cold-start.test.cjs, tests/automations-execution.test.cjs, tests/test_action_batch_history.py, tests/test_action_click_wal.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 55d5e0941629d229)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
