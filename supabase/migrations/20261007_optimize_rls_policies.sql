-- v120.35: preserve the same per-user RLS semantics while avoiding
-- per-row auth.uid() re-evaluation and explicitly scoping policies to authenticated.

do $$
declare t text;
begin
  foreach t in array array['devices','audit_events','focus_batches','focus_batch_items','profile_state','list_snapshots','workspace_state'] loop
    execute format('drop policy if exists igc_select_own on public.%I',t);
    execute format('drop policy if exists igc_insert_own on public.%I',t);
    execute format('drop policy if exists igc_update_own on public.%I',t);
    execute format('drop policy if exists igc_delete_own on public.%I',t);

    execute format('create policy igc_select_own on public.%I for select to authenticated using ((select auth.uid()) = user_id)',t);
    execute format('create policy igc_insert_own on public.%I for insert to authenticated with check ((select auth.uid()) = user_id)',t);
    execute format('create policy igc_update_own on public.%I for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id)',t);
    execute format('create policy igc_delete_own on public.%I for delete to authenticated using ((select auth.uid()) = user_id)',t);
  end loop;
end $$;
