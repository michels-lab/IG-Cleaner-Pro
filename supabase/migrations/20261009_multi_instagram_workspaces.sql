-- Additive multi-Instagram per-user storage. Legacy tables and primary keys remain untouched.
begin;
create table if not exists public.instagram_accounts (
 user_id uuid not null default auth.uid(),
 account_key text not null check (account_key = 'legacy' or account_key ~ '^ig_[a-z0-9_-]{8,64}$'),
 username text check (username is null or username ~ '^[a-z0-9._]{1,30}$'),
 label text not null default '',
 created_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),
 primary key (user_id,account_key),
 unique (user_id,username)
);
do $igc$
declare spec record; dest text;
begin
 for spec in select * from (values
  ('audit_events','id'),('focus_batches','id'),
  ('focus_batch_items','batch_id,username'),('profile_state','username,module'),
  ('list_snapshots','list_name'),('workspace_state','state_key')
 ) as specs(original,keys) loop
  dest:='instagram_' || spec.original;
  execute format('create table if not exists public.%I (like public.%I including defaults including constraints)',dest,spec.original);
  execute format('alter table public.%I add column if not exists account_key text',dest);
  execute format('alter table public.%I alter column account_key set not null',dest);
  if not exists(select 1 from pg_constraint where conrelid=format('public.%I',dest)::regclass and contype='p') then
   execute format('alter table public.%I add constraint %I primary key(user_id,account_key,%s)',dest,dest||'_pkey',spec.keys);
  end if;
 end loop;
end
$igc$;
do $igc$
declare t text;
begin
 if not exists(select 1 from pg_constraint where conrelid='public.instagram_focus_batch_items'::regclass and conname='igc_instagram_focus_item_parent') then
  alter table public.instagram_focus_batch_items
   add constraint igc_instagram_focus_item_parent
   foreign key (user_id,account_key,batch_id)
   references public.instagram_focus_batches(user_id,account_key,id) on delete cascade;
 end if;
 foreach t in array array[
  'instagram_audit_events','instagram_focus_batches','instagram_focus_batch_items',
  'instagram_profile_state','instagram_list_snapshots','instagram_workspace_state'
 ] loop
  if not exists(select 1 from pg_constraint where conrelid=format('public.%I',t)::regclass and conname=t||'_owner_fk') then
   execute format('alter table public.%I add constraint %I foreign key(user_id,account_key) references public.instagram_accounts(user_id,account_key) on delete restrict',t,t||'_owner_fk');
  end if;
 end loop;
end
$igc$;
create index if not exists igc_instagram_audit_time on public.instagram_audit_events(user_id,account_key,event_at desc);
create index if not exists igc_instagram_focus_time on public.instagram_focus_batches(user_id,account_key,created_at desc);
create index if not exists igc_instagram_reviews_time on public.instagram_profile_state(user_id,account_key,reviewed_at desc);
create index if not exists igc_instagram_lists_time on public.instagram_list_snapshots(user_id,account_key,updated_at desc);
do $igc$
declare t text;
begin
 foreach t in array array[
  'instagram_accounts','instagram_audit_events','instagram_focus_batches',
  'instagram_focus_batch_items','instagram_profile_state',
  'instagram_list_snapshots','instagram_workspace_state'
 ] loop
  execute format('alter table public.%I enable row level security',t);
  execute format('drop policy if exists igc_select_own on public.%I',t);
  execute format('drop policy if exists igc_insert_own on public.%I',t);
  execute format('drop policy if exists igc_update_own on public.%I',t);
  execute format('drop policy if exists igc_delete_own on public.%I',t);
  execute format('create policy igc_select_own on public.%I for select to authenticated using ((select auth.uid()) = user_id)',t);
  execute format('create policy igc_insert_own on public.%I for insert to authenticated with check ((select auth.uid()) = user_id)',t);
  execute format('create policy igc_update_own on public.%I for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id)',t);
  execute format('create policy igc_delete_own on public.%I for delete to authenticated using ((select auth.uid()) = user_id)',t);
 end loop;
end
$igc$;
grant select,insert,update,delete on public.instagram_accounts,
 public.instagram_audit_events,public.instagram_focus_batches,
 public.instagram_focus_batch_items,public.instagram_profile_state,
 public.instagram_list_snapshots,public.instagram_workspace_state to authenticated;
commit;
