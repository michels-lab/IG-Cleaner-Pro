# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 328; classified: 324; readable documents: 70; above read cap: 1; findings: 3.

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
| document | 65 |
| index | 5 |
| installer_metadata | 1 |
| source | 42 |
| test | 79 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_V12064_FINAL_RECEIPT_2026-10-26.md. Next: Fix link or restore target (ID d6a887cd4cf4669d)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/GRANADA_NO_REPEAT_NEW_BATCH_2026-10-26.md. Next: Fix link or restore target (ID df925d8ba69bac5a)
- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 1 implementation/config paths changed since this log's last commit; examples: release/android-signing.json. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID e4e12e1b3ac88ede)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
