-- Additive profile management: no changes to the original v120.38 tables or data.
-- These operations run with the caller's RLS role, not elevated privileges.
create or replace function public.igc_set_instagram_username(
 p_account_key text, p_new_username text,
 p_expected_username text default null,
 p_transfer_from_key text default null
) returns boolean
language plpgsql security invoker set search_path = ''
as $igc_identity$
declare
 v_owner uuid := (select auth.uid());
 v_old text;
 v_conflict text;
begin
 if v_owner is null then raise exception 'Inicia sesión para cambiar Instagram'; end if;
 if p_account_key is null or p_account_key !~ '^(legacy|ig_[a-z0-9_-]{8,64})$' then
   raise exception 'Perfil de Instagram inválido';
 end if;
 if p_new_username is null or p_new_username !~ '^[a-z0-9._]{1,30}$' then
   raise exception 'El @usuario de Instagram es inválido';
 end if;
 -- Lock all registry rows for this owner in deterministic order to serialize
 -- competing changes across Android/Desktop (the username unique index is final defense).
 perform 1 from public.instagram_accounts
 where user_id=v_owner order by account_key for update;
 select username into v_old from public.instagram_accounts
 where user_id=v_owner and account_key=p_account_key;
 if not found then raise exception 'El perfil ya no existe. Actualiza la lista'; end if;
 if v_old is distinct from p_expected_username then
   raise exception 'El @usuario cambió en otro dispositivo. Actualiza e inténtalo de nuevo';
 end if;
 select account_key into v_conflict from public.instagram_accounts
 where user_id=v_owner and username=p_new_username and account_key<>p_account_key;
 if v_conflict is not null then
   if p_account_key<>'legacy' or p_transfer_from_key is distinct from v_conflict then
     raise exception 'Ese @usuario ya está asociado al perfil %. No se modificaron datos',v_conflict;
   end if;
   -- Disassociate only the human-readable handle, NEVER rows or immutable keys.
   -- The prior named workspace remains accessible, with all of its own data.
   update public.instagram_accounts set username=null,
    label='Sin asignar (antes @'||p_new_username||')',updated_at=now()
   where user_id=v_owner and account_key=v_conflict;
 elsif p_transfer_from_key is not null then
   raise exception 'El conflicto cambió. Actualiza antes de reasignar el @usuario';
 end if;
 update public.instagram_accounts
 set username=p_new_username,label='@'||p_new_username,updated_at=now()
 where user_id=v_owner and account_key=p_account_key;
 if not found then raise exception 'No fue posible actualizar este perfil'; end if;
 return true;
end;
$igc_identity$;
revoke all on function public.igc_set_instagram_username(text,text,text,text) from public, anon;
grant execute on function public.igc_set_instagram_username(text,text,text,text) to authenticated;

create or replace function public.igc_instagram_profile_summaries()
returns table (
 account_key text, username text, label text,
 following_count bigint, followers_count bigint, pending_count bigint,
 review_count bigint, last_sync_at timestamptz
)
language sql stable security invoker set search_path = ''
as $igc_summary$
 select a.account_key,a.username,a.label,
 case when a.account_key='legacy' then
  coalesce((select s.item_count from public.list_snapshots s
    where s.user_id=a.user_id and s.list_name='following'),0)::bigint
 else coalesce((select s.item_count from public.instagram_list_snapshots s
    where s.user_id=a.user_id and s.account_key=a.account_key and s.list_name='following'),0)::bigint end,
 case when a.account_key='legacy' then
  coalesce((select s.item_count from public.list_snapshots s
    where s.user_id=a.user_id and s.list_name='followers'),0)::bigint
 else coalesce((select s.item_count from public.instagram_list_snapshots s
    where s.user_id=a.user_id and s.account_key=a.account_key and s.list_name='followers'),0)::bigint end,
 case when a.account_key='legacy' then
  coalesce((select s.item_count from public.list_snapshots s
    where s.user_id=a.user_id and s.list_name='pending'),0)::bigint
 else coalesce((select s.item_count from public.instagram_list_snapshots s
    where s.user_id=a.user_id and s.account_key=a.account_key and s.list_name='pending'),0)::bigint end,
 case when a.account_key='legacy' then
  (select count(*) from public.profile_state s where s.user_id=a.user_id)
 else
  (select count(*) from public.instagram_profile_state s where s.user_id=a.user_id and s.account_key=a.account_key) end,
 case when a.account_key='legacy' then
  (select max(s.updated_at) from public.list_snapshots s where s.user_id=a.user_id)
 else
  (select max(s.updated_at) from public.instagram_list_snapshots s
    where s.user_id=a.user_id and s.account_key=a.account_key) end
 from public.instagram_accounts a
 where a.user_id=(select auth.uid())
 order by a.created_at,a.account_key;
$igc_summary$;
revoke all on function public.igc_instagram_profile_summaries() from public, anon;
grant execute on function public.igc_instagram_profile_summaries() to authenticated;
