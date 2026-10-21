# File steward: repository file audit

All tracked files classified; Markdown/text docs inspected with size cap. Binary/research-content validity and untracked files not assessed.
No file is auto-deleted or declared unused.

## Coverage

Tracked: 277; classified: 277; readable documents: 43; above read cap: 1; findings: 24.

## File roles

| Role | Count |
|---|---:|
| agent | 9 |
| asset | 20 |
| bitacora | 1 |
| config | 69 |
| document | 37 |
| index | 6 |
| source | 37 |
| test | 65 |
| unknown | 22 |
| workflow | 11 |

## Findings (human review required)

- **CONFIRMED / BROKEN_RELATIVE_LINK** docs/CURRENT_HANDOFF.md: Missing: docs/docs/PENDING_BLOCK_ROBOT_RECOVERY_DEVELOPER_TWIN_2026-10-19.md. Next: Fix link or restore target (ID cb6e9232d5887dbd)
- **REVIEW / POSSIBLY_REDUNDANT_NAME** android/app/src/main/res/xml/backup_rules.xml: Backup/old/copy/draft name; may be intentional. Next: Check references and history before archiving (ID d1bfe6794078b652)
- **REVIEW / UNKNOWN_PURPOSE** LICENSE.txt: No reliable purpose category from path. Next: Declare role after reviewing usage (ID b1f1bb5a1d0c7fe5)
- **REVIEW / UNKNOWN_PURPOSE** android/app/build.gradle.kts: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 19cd65c90b9e6cfc)
- **REVIEW / UNKNOWN_PURPOSE** android/app/src/main/assets/ig_cleaner_workspace.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 03c3bf6f89398080)
- **REVIEW / UNKNOWN_PURPOSE** android/build.gradle.kts: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 6b94bcefb2676ae0)
- **REVIEW / UNKNOWN_PURPOSE** android/settings.gradle.kts: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 893790451fda3de8)
- **REVIEW / UNKNOWN_PURPOSE** desktop/ig_cleaner_pro_v120_27_synced_companion.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 46cc4e15452a5b6a)
- **REVIEW / UNKNOWN_PURPOSE** index.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID c2a507475709b660)
- **REVIEW / UNKNOWN_PURPOSE** packaging/chrome-extension/popup.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID f613e54200722998)
- **REVIEW / UNKNOWN_PURPOSE** packaging/profile-counts/Start-Insta-Cleaner-Robot.cmd: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 585db8ee0d2682b7)
- **REVIEW / UNKNOWN_PURPOSE** packaging/windows-installer/InstaCleanerPro.iss: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 77ffae88bc4fea3d)
- **REVIEW / UNKNOWN_PURPOSE** packaging/windows-installer/InstaCleanerProDeveloper.iss: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 64b3a56fa7004161)
- **REVIEW / UNKNOWN_PURPOSE** packaging/windows-installer/TaskbarPinning.txt: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 75348e30dd4d8d8b)
- **REVIEW / UNKNOWN_PURPOSE** supabase/email-templates/confirmation.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 06bb17e0763452e5)
- **REVIEW / UNKNOWN_PURPOSE** supabase/email-templates/magic_link.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID b4a48ad93b0fd1d1)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261006_initialize_sync_schema.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID a7e8967bf2ec6bf1)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261007_optimize_rls_policies.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID b23e5621a2a793f3)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261009_multi_instagram_workspaces.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 5d1d9476c55f5021)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261010_delete_instagram_profiles.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 31f8270f8834f5d8)
- **REVIEW / UNKNOWN_PURPOSE** supabase/migrations/20261011_profile_identity_and_summaries.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 75566a574ae94c74)
- **REVIEW / UNKNOWN_PURPOSE** supabase/schema.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 521c56b57127249b)
- **REVIEW / UNKNOWN_PURPOSE** supabase/tests/rls_isolation.sql: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 07ae6e565c212eaf)
- **REVIEW / UNKNOWN_PURPOSE** tests/fixtures/instagram-export-sample/connections/followers_and_following/recent_follow_requests.html: No reliable purpose category from path. Next: Declare role after reviewing usage (ID 110f34300db5ae95)

Complete path → purpose/role/certainty list lives in FILE_GOVERNANCE.json. SUMMARY.json has counts only for master polling.
A dated file, duplicate, or suspicious name is an **investigation candidate**, not unwanted material.
No historical science cases, audit logs or evidence may be deleted automatically.
