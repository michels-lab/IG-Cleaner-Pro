begin;

create extension if not exists pgtap with schema extensions;
select plan(41);

-- Two deterministic users; rows are rolled back after the suite.
-- No auth.users rows are required because these tables intentionally store the
-- Supabase JWT subject as user_id without a foreign key.
insert into public.devices(user_id,device_id,device_type,label) values
  ('11111111-1111-4111-8111-111111111111','rls-u1-device','desktop','RLS U1'),
  ('22222222-2222-4222-8222-222222222222','rls-u2-device','android','RLS U2');

insert into public.audit_events(user_id,id,event_at,action,device_id,device_type) values
  ('11111111-1111-4111-8111-111111111111','rls-u1-event',now(),'seed','rls-u1-device','desktop'),
  ('22222222-2222-4222-8222-222222222222','rls-u2-event',now(),'seed','rls-u2-device','android');

insert into public.focus_batches(user_id,id,module,target_size) values
  ('11111111-1111-4111-8111-111111111111','rls-u1-batch','main',1),
  ('22222222-2222-4222-8222-222222222222','rls-u2-batch','main',1);

insert into public.focus_batch_items(user_id,batch_id,position,username) values
  ('11111111-1111-4111-8111-111111111111','rls-u1-batch',1,'rls_u1_profile'),
  ('22222222-2222-4222-8222-222222222222','rls-u2-batch',1,'rls_u2_profile');

insert into public.profile_state(user_id,username,module,reviewed_at,reviewed_device) values
  ('11111111-1111-4111-8111-111111111111','rls_u1_profile','main',now(),'desktop'),
  ('22222222-2222-4222-8222-222222222222','rls_u2_profile','main',now(),'android');

insert into public.list_snapshots(user_id,list_name,payload,item_count) values
  ('11111111-1111-4111-8111-111111111111','following','[]'::jsonb,0),
  ('22222222-2222-4222-8222-222222222222','following','[]'::jsonb,0);

insert into public.workspace_state(user_id,state_key,payload) values
  ('11111111-1111-4111-8111-111111111111','primary','{}'::jsonb),
  ('22222222-2222-4222-8222-222222222222','primary','{}'::jsonb);

-- 1–7: every exposed sync table must have RLS enabled.
select ok((select relrowsecurity from pg_class where oid='public.devices'::regclass), 'devices has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.audit_events'::regclass), 'audit_events has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.focus_batches'::regclass), 'focus_batches has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.focus_batch_items'::regclass), 'focus_batch_items has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.profile_state'::regclass), 'profile_state has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.list_snapshots'::regclass), 'list_snapshots has RLS enabled');
select ok((select relrowsecurity from pg_class where oid='public.workspace_state'::regclass), 'workspace_state has RLS enabled');

set local role authenticated;
set local request.jwt.claim.sub = '11111111-1111-4111-8111-111111111111';

-- 8–14: user 1 sees exactly their own seeded row, never user 2.
select results_eq('select count(*) from public.devices',array[1::bigint],'user 1 only sees own devices');
select results_eq('select count(*) from public.audit_events',array[1::bigint],'user 1 only sees own audit events');
select results_eq('select count(*) from public.focus_batches',array[1::bigint],'user 1 only sees own focus batches');
select results_eq('select count(*) from public.focus_batch_items',array[1::bigint],'user 1 only sees own focus items');
select results_eq('select count(*) from public.profile_state',array[1::bigint],'user 1 only sees own profile state');
select results_eq('select count(*) from public.list_snapshots',array[1::bigint],'user 1 only sees own list snapshots');
select results_eq('select count(*) from public.workspace_state',array[1::bigint],'user 1 only sees own workspace state');

set local request.jwt.claim.sub = '22222222-2222-4222-8222-222222222222';

-- 15–21: user 2 cannot update user 1.
select is_empty($$update public.devices set label='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 devices');
select is_empty($$update public.audit_events set action='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 audit events');
select is_empty($$update public.focus_batches set label='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 focus batches');
select is_empty($$update public.focus_batch_items set decision='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 focus items');
select is_empty($$update public.profile_state set decision='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 profile state');
select is_empty($$update public.list_snapshots set content_hash='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 list snapshots');
select is_empty($$update public.workspace_state set source_device='hacked' where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot update user 1 workspace state');

-- 22–28: user 2 cannot delete user 1.
select is_empty($$delete from public.focus_batch_items where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 focus items');
select is_empty($$delete from public.devices where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 devices');
select is_empty($$delete from public.audit_events where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 audit events');
select is_empty($$delete from public.focus_batches where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 focus batches');
select is_empty($$delete from public.profile_state where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 profile state');
select is_empty($$delete from public.list_snapshots where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 list snapshots');
select is_empty($$delete from public.workspace_state where user_id='11111111-1111-4111-8111-111111111111' returning 1$$,'user 2 cannot delete user 1 workspace state');

-- 29–35: authenticated user 2 can create rows owned by user 2.
select lives_ok($$insert into public.devices(user_id,device_id,device_type) values ('22222222-2222-4222-8222-222222222222','rls-u2-own-insert','other')$$,'user 2 can insert own device');
select lives_ok($$insert into public.audit_events(user_id,id,event_at,action,device_id,device_type) values ('22222222-2222-4222-8222-222222222222','rls-u2-own-event',now(),'own','rls-u2-device','android')$$,'user 2 can insert own audit event');
select lives_ok($$insert into public.focus_batches(user_id,id,module,target_size) values ('22222222-2222-4222-8222-222222222222','rls-u2-own-batch','main',1)$$,'user 2 can insert own focus batch');
select lives_ok($$insert into public.focus_batch_items(user_id,batch_id,position,username) values ('22222222-2222-4222-8222-222222222222','rls-u2-own-batch',1,'rls_u2_own_item')$$,'user 2 can insert own focus item');
select lives_ok($$insert into public.profile_state(user_id,username,module,reviewed_at,reviewed_device) values ('22222222-2222-4222-8222-222222222222','rls_u2_own_profile','main',now(),'android')$$,'user 2 can insert own profile state');
select lives_ok($$insert into public.list_snapshots(user_id,list_name,payload,item_count) values ('22222222-2222-4222-8222-222222222222','followers','[]'::jsonb,0)$$,'user 2 can insert own list snapshot');
select lives_ok($$insert into public.workspace_state(user_id,state_key,payload) values ('22222222-2222-4222-8222-222222222222','secondary','{}'::jsonb)$$,'user 2 can insert own workspace state');

-- 36–41: simulated same-account Desktop/Android Focus cycle roundtrip.
-- Both devices share one account-scoped key without mutating canonical
-- review history; the other account must never read that key.
set local request.jwt.claim.sub = '11111111-1111-4111-8111-111111111111';
select lives_ok($
  insert into public.workspace_state(user_id,state_key,payload,source_device)
  values ('11111111-1111-4111-8111-111111111111',
          'focus_double_check_cycle',
          '{"epoch":7,"seen":["alice"],"lastBatchId":"desktop-batch"}'::jsonb,
          'desktop')
$, 'Desktop can publish the Double Check cycle in its own separate workspace state');

select is((select payload->>'lastBatchId' from public.workspace_state
  where state_key='focus_double_check_cycle'),
  'desktop-batch', 'Android would read Desktop batch marker through same authenticated account');

select lives_ok($
  insert into public.workspace_state(user_id,state_key,payload,source_device)
  values ('11111111-1111-4111-8111-111111111111',
          'focus_double_check_cycle',
          '{"epoch":7,"seen":["alice","bob"],"lastBatchId":"android-batch"}'::jsonb,
          'android')
  on conflict (user_id,state_key)
  do update set payload=excluded.payload,source_device=excluded.source_device
$, 'Android can update the shared cycle with its own additions');

select is((select payload->'seen'->>1 from public.workspace_state
  where state_key='focus_double_check_cycle'),
  'bob', 'Desktop can read the Android cycle update without a duplicate state key');

select is((select payload::text from public.workspace_state
  where state_key='primary'),
  '{}', 'Double Check updates do not overwrite canonical primary review state');

set local request.jwt.claim.sub = '22222222-2222-4222-8222-222222222222';
select is_empty($
  select state_key from public.workspace_state
  where state_key='focus_double_check_cycle'
$,'An unrelated account cannot access another account Double Check cycle');

select * from finish();
rollback;
