# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 320; classified: 316; readable documents: 66; above read cap: 1; findings: 1.

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
| document | 61 |
| index | 5 |
| installer_metadata | 1 |
| source | 42 |
| test | 75 |
| text_metadata | 2 |
| web_ui | 7 |
| workflow | 12 |

## Findings (human review required)

- **REVIEW / POTENTIAL_UNLOGGED_CHANGES** PROJECT_LOG.md: 6 implementation/config paths changed since this log's last commit; examples: .michelslab/release-request.json, android/app/build.gradle.kts, desktop/ig_cleaner_pro_v120_27_synced_companion.html, release/android-signing.json, release/distribution-manifest.json, tests/test_update_docs_contract.py. Next: Inspect diffs and reconcile only meaningful decisions/results in the canonical log (ID 78483f9728cf1c0f)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
