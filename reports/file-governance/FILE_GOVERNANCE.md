# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 469; classified: 465; readable documents: 128; above read cap: 2; findings: 2.

## File roles

| Role | Count |
|---|---:|
| agent | 9 |
| asset | 20 |
| bitacora | 1 |
| build_script | 6 |
| config | 70 |
| database_migration | 7 |
| database_schema | 1 |
| document | 124 |
| index | 5 |
| installer_metadata | 1 |
| source | 56 |
| test | 144 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** release/RELEASE_NOTES.md: Missing: release/docs/GRANADA_V12070_FINAL_RECEIPT_2026-10-27.md. Next: Fix link or restore target (ID 5c362704fd56e07f)
- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 5 implementation/config paths changed since this log's last commit; examples: tests/pending-zip-completeness.test.cjs, tests/test_windows_single_window_layout.py, tools/ig_cleaner_desktop.py, tools/profile_counts_bridge.py, tools/windows_workspace_picker.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 35e398a626337fa5)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
