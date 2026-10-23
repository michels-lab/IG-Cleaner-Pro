# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 306; classified: 302; readable documents: 59; above read cap: 1; findings: 1.

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
| document | 54 |
| index | 5 |
| installer_metadata | 1 |
| source | 40 |
| test | 70 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 11 implementation/config paths changed since this log's last commit; examples: .github/workflows/profile-counts-ci.yml, .github/workflows/profile-counts-windows-preview.yml, .github/workflows/release.yml, .michelslab/release-request.json, android/app/build.gradle.kts, desktop/ig_cleaner_pro_v120_27_synced_companion.html. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 82a25cce4bd91ba9)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
