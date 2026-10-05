-- IG Cleaner Pro v120.27 — Supabase sync schema
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

alter table public.devices enable row level security;
alter table public.audit_events enable row level security;
alter table public.focus_batches enable row level security;
alter table public.focus_batch_items enable row level security;
alter table public.profile_state enable row level security;
alter table public.list_snapshots enable row level security;

do $$
declare t text;
begin
  foreach t in array array['devices','audit_events','focus_batches','focus_batch_items','profile_state','list_snapshots'] loop
    execute format('drop policy if exists igc_select_own on public.%I',t);
    execute format('drop policy if exists igc_insert_own on public.%I',t);
    execute format('drop policy if exists igc_update_own on public.%I',t);
    execute format('drop policy if exists igc_delete_own on public.%I',t);
    execute format('create policy igc_select_own on public.%I for select using (auth.uid() = user_id)',t);
    execute format('create policy igc_insert_own on public.%I for insert with check (auth.uid() = user_id)',t);
    execute format('create policy igc_update_own on public.%I for update using (auth.uid() = user_id) with check (auth.uid() = user_id)',t);
    execute format('create policy igc_delete_own on public.%I for delete using (auth.uid() = user_id)',t);
  end loop;
end $$;

grant usage on schema public to authenticated;
grant select,insert,update,delete on public.devices, public.audit_events, public.focus_batches, public.focus_batch_items, public.profile_state, public.list_snapshots to authenticated;