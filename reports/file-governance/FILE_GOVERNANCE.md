# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 284; classified: 280; readable documents: 44; above read cap: 1; findings: 9.

## File roles

| Role | Count |
|---|---:|
| agent | 9 |
| asset | 20 |
| bitacora | 1 |
| build_script | 6 |
| config | 69 |
| document | 38 |
| index | 6 |
| license | 1 |
| source | 38 |
| test | 66 |
| unknown | 8 |
| web_ui | 7 |
| workflow | 11 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/PENDING_BLOCK_ROBOT_RECOVERY_DEVELOPER_TWIN_2026-10-19.md. Next: Fix link or restore target (ID cb6e9232d5887dbd)
- **REVIEW / UNKNOWN_PURPOSE** packaging/windows-installer/TaskbarPinning.txt: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 75348e30dd4d8d8b)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261006_initialize_sync_schema.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID a7e8967bf2ec6bf1)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261007_optimize_rls_policies.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID b23e5621a2a793f3)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261009_multi_instagram_workspaces.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 5d1d9476c55f5021)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261010_delete_instagram_profiles.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 31f8270f8834f5d8)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261011_profile_identity_and_summaries.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 75566a574ae94c74)
- **REVIEW / UNKNOWN_PURPOSE** supabase/schema.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 521c56b57127249b)
- **REVIEW / UNKNOWN_PURPOSE** supabase/tests/rls_isolation.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 07ae6e565c212eaf)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
