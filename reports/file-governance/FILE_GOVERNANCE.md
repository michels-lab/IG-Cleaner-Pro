# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 285; classified: 281; readable documents: 44; above read cap: 1; findings: 1.

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
| document | 39 |
| index | 5 |
| installer_metadata | 1 |
| source | 38 |
| test | 67 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 11 |

## Findings (human review required)

- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 7 implementation/config paths changed since this log's last commit; examples: .github/workflows/ci.yml, .github/workflows/profile-counts-windows-preview.yml, .github/workflows/release.yml, .michelslab/release-request.json, tests/release-publisher-contract.py, tests/test_desktop_visual_artifact_resolution.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 7a8eca742e89c1f6)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
