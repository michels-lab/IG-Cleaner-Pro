# Copilot instructions — IG Cleaner Pro

Read `AGENTS.md`, `PROJECT_LOG.md` and the relevant infrastructure/handoff documentation before editing.

Preserve the canonical Desktop engine and established cleanup workflows. Mobile-specific UX is allowed, but required feature parity must not be removed.

Keep raw Instagram exports local. Supabase is for authenticated workflow metadata/state unless a reviewed architecture change explicitly says otherwise. Never commit privileged keys or user export data.

Use current-commit validation for import, state migration, Focus/review/audit behavior, Android builds and sync changes. Device/provider claims remain unvalidated until actually exercised.

Update `PROJECT_LOG.md` for meaningful work. Do not publish a release unless explicitly assigned.
