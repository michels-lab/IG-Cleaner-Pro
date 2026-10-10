#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
schema=(ROOT/"supabase/schema.sql").read_text(encoding="utf-8")
suite=(ROOT/"supabase/tests/rls_isolation.sql").read_text(encoding="utf-8")
ci=(ROOT/".github/workflows/ci.yml").read_text(encoding="utf-8")

tables=[
    "devices",
    "audit_events",
    "focus_batches",
    "focus_batch_items",
    "profile_state",
    "list_snapshots",
    "workspace_state",
]

for table in tables:
    assert f"alter table public.{table} enable row level security;" in schema, f"RLS not enabled in schema for {table}"
    assert table in suite, f"RLS isolation suite does not cover {table}"

for token in (
    "to authenticated using ((select auth.uid()) = user_id)",
    "to authenticated with check ((select auth.uid()) = user_id)",
):
    assert token in schema, f"Optimized authenticated-only RLS policy missing: {token}"

for token in (
    "select plan(41)",
    "set local role authenticated",
    "set local request.jwt.claim.sub",
    "cannot update user 1",
    "cannot delete user 1",
    "can insert own",
    "focus_double_check_cycle",
    "Double Check updates do not overwrite canonical primary review state",
):
    assert token in suite, f"RLS behavioral test token missing: {token}"

for token in (
    "Supabase RLS isolation",
    "supabase/setup-cli@v1",
    "supabase start",
    "supabase/schema.sql",
    "supabase test db supabase/tests/rls_isolation.sql",
):
    assert token in ci, f"RLS CI token missing: {token}"

print("Supabase RLS isolation contract passed.")
