# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 313; classified: 309; readable documents: 62; above read cap: 1; findings: 1.

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
| document | 57 |
| index | 5 |
| installer_metadata | 1 |
| source | 41 |
| test | 73 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 5 implementation/config paths changed since this log's last commit; examples: .github/workflows/profile-counts-windows-preview.yml, tests/test_instagram_unfollow_chromium_e2e.py, tests/test_instagram_unfollow_reference.py, tools/instagram_unfollow_reference.py, tools/profile_actions.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID d7fa0ab1c75ea28b)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
