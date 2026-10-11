-- Safe and atomic removal of a named Instagram workspace. Never touches v120.38 legacy rows.
-- Every statement is executed as the authenticated caller (RLS), in one transaction.
create or replace function public.igc_delete_instagram_profile(
  p_account_key text,
  p_expected_username text
) returns boolean
language plpgsql
security invoker
set search_path = ''
as $igc_delete$
declare
  v_owner uuid := (select auth.uid());
  v_username text;
begin
  if v_owner is null then
    raise exception 'Inicia sesión para eliminar un perfil';
  end if;
  if p_account_key is null or p_account_key = 'legacy'
     or p_account_key !~ '^ig_[a-z0-9_-]{8,64}$' then
    raise exception 'Los datos anteriores no se pueden eliminar desde perfiles';
  end if;

  select username into v_username
    from public.instagram_accounts
   where user_id = v_owner and account_key = p_account_key
   for update;
  if not found then
    raise exception 'Este perfil no existe en tu cuenta';
  end if;
  if v_username is distinct from p_expected_username then
    raise exception 'El nombre de Instagram cambió. Actualiza la lista antes de eliminar';
  end if;

  -- Child rows first (foreign keys deliberately RESTRICT registry deletion).
  -- Any failure rolls back every DELETE, never leaving a half-deleted profile.
  delete from public.instagram_focus_batch_items where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_focus_batches where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_profile_state where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_audit_events where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_list_snapshots where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_workspace_state where user_id=v_owner and account_key=p_account_key;
  delete from public.instagram_accounts where user_id=v_owner and account_key=p_account_key;
  if not found then
    raise exception 'El perfil no se pudo eliminar. Vuelve a intentarlo';
  end if;
  return true;
end;
$igc_delete$;

revoke all on function public.igc_delete_instagram_profile(text,text) from PUBLIC, anon;
grant execute on function public.igc_delete_instagram_profile(text,text) to authenticated;
