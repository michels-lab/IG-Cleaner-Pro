# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 296; classified: 292; readable documents: 50; above read cap: 1; findings: 1.

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
| document | 45 |
| index | 5 |
| installer_metadata | 1 |
| source | 40 |
| test | 69 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 5 implementation/config paths changed since this log's last commit; examples: .github/workflows/ci.yml, tests/test_developer_live_probe.py, tests/test_ig_structured_probe.py, tools/developer_live_probe.py, tools/ig_structured_probe.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 42d58e467f44583f)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
