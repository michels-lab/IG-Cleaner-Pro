-- IG Cleaner Pro v120.35 — Supabase sync schema
-- Run once in Supabase SQL Editor. Tables are private per authenticated user via RLS.

create extension if not exists pgcrypto;

create table if not exists public.devices (
  user_id uuid not null default auth.uid(),
  device_id text not null,
  device_type text not null check (device_type in ('desktop','android','other')),
  label text not null default '',
  last_seen timestamptz not null default now(),
  created_at timestamptz not null default now(),
  primary key (user_id, device_id)
);

create table if not exists public.audit_events (
  user_id uuid not null default auth.uid(),
  id text not null,
  event_at timestamptz not null,
  username text,
  action text not null,
  device_id text not null,
  device_type text not null,
  device_label text not null default '',
  module text not null default 'unknown',
  batch_id text,
  batch_label text not null default '',
  batch_size integer not null default 0,
  decision text not null default '',
  origin_event_id text,
  meta jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  primary key (user_id, id)
);
create index if not exists audit_events_user_time_idx on public.audit_events(user_id,event_at desc);
create index if not exists audit_events_user_device_idx on public.audit_events(user_id,device_type,event_at desc);
create index if not exists audit_events_user_username_idx on public.audit_events(user_id,username,event_at desc);

create table if not exists public.focus_batches (
  user_id uuid not null default auth.uid(),
  id text not null,
  module text not null,
  label text not null default '',
  target_size integer not null,
  status text not null default 'prepared' check (status in ('prepared','active','completed','cancelled')),
  created_device text not null default 'desktop',
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  source_signature text not null default '',
  updated_at timestamptz not null default now(),
  primary key (user_id,id)
);
create index if not exists focus_batches_user_status_idx on public.focus_batches(user_id,status,created_at desc);

create table if not exists public.focus_batch_items (
  user_id uuid not null default auth.uid(),
  batch_id text not null,
  position integer not null,
  username text not null,
  status text not null default 'pending' check (status in ('pending','opened','reviewed','audited','skipped')),
  opened_at timestamptz,
  opened_device text,
  reviewed_at timestamptz,
  reviewed_device text,
  decision text not null default '',
  context jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id,batch_id,username),
  foreign key (user_id,batch_id) references public.focus_batches(user_id,id) on delete cascade
);
create index if not exists focus_batch_items_user_batch_idx on public.focus_batch_items(user_id,batch_id,position);

create table if not exists public.profile_state (
  user_id uuid not null default auth.uid(),
  username text not null,
  module text not null,
  reviewed_at timestamptz not null,
  reviewed_device text not null,
  reviewed_device_id text not null default '',
  decision text not null default '',
  protected boolean not null default false,
  context jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (user_id,username,module)
);
create index if not exists profile_state_user_reviewed_idx on public.profile_state(user_id,reviewed_at desc);

create table if not exists public.list_snapshots (
  user_id uuid not null default auth.uid(),
  list_name text not null check (list_name in ('following','followers','pending')),
  payload jsonb not null default '[]'::jsonb,
  item_count integer not null default 0,
  source_device text not null default 'desktop',
  content_hash text not null default '',
  captured_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (user_id,list_name)
);
create index if not exists list_snapshots_user_updated_idx on public.list_snapshots(user_id,updated_at desc);

create table if not exists public.workspace_state (
  user_id uuid not null default auth.uid(),
  state_key text not null default 'primary',
  payload jsonb not null default '{}'::jsonb,
  source_device text not null default 'desktop',
  updated_at timestamptz not null default now(),
  primary key (user_id,state_key)
);


alter table public.devices enable row level security;
alter table public.audit_events enable row level security;
alter table public.focus_batches enable row level security;
alter table public.focus_batch_items enable row level security;
alter table public.profile_state enable row level security;
alter table public.list_snapshots enable row level security;
alter table public.workspace_state enable row level security;

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

grant usage on schema public to authenticated;
grant select,insert,update,delete on public.devices, public.audit_events, public.focus_batches, public.focus_batch_items, public.profile_state, public.list_snapshots, public.workspace_state to authenticated;

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
