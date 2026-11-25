# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 502; classified: 498; readable documents: 148; above read cap: 2; findings: 5.

## File roles

| Role | Count |
|---|---:|
| agent | 9 |
| asset | 20 |
| bitacora | 1 |
| build_script | 6 |
| config | 71 |
| database_migration | 7 |
| database_schema | 1 |
| document | 144 |
| index | 5 |
| installer_metadata | 1 |
| source | 56 |
| test | 156 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/PROJECT_PROGRESS.md: Missing: docs/docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md. Next: Fix link or restore target (ID 43f9e3af91f2b36f)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/PROJECT_PROGRESS.md: Missing: docs/docs/audits/2026-11-24-visible-owner-controls-viewport.md. Next: Fix link or restore target (ID b7b89c0ec3f42069)
- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/UPDATE_AND_STATE_MIGRATION.md: Missing: docs/docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md. Next: Fix link or restore target (ID 1eed8bdccf588c59)
- **CONFIRMED / BROKEN_RELATIVE_LINK** release/RELEASE_NOTES.md: Missing: release/docs/GRANADA_V12082_FINAL_RECEIPT_2026-11-24.md. Next: Fix link or restore target (ID d34dbdedaafa4d6f)
- **CONFIRMED / BROKEN_RELATIVE_LINK** release/RELEASE_NOTES.md: Missing: release/docs/GRANADA_V12070_FINAL_RECEIPT_2026-10-27.md. Next: Fix link or restore target (ID 5c362704fd56e07f)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
