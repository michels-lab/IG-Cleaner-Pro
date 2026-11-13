-- Applied to Supabase ig-cleaner-sync on 2026-11-13 UTC.
-- An offline device must not overwrite a newer confirmed review.
-- Both the legacy and account-isolated data paths use the same guard.
-- This remains SECURITY INVOKER and does not bypass ownership RLS.
create or replace function public.igc_preserve_newest_review()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if new.reviewed_at < old.reviewed_at then
    return old;
  end if;
  return new;
end
$$;

drop trigger if exists igc_preserve_newest_review on public.profile_state;
create trigger igc_preserve_newest_review
before update on public.profile_state
for each row execute function public.igc_preserve_newest_review();

drop trigger if exists igc_preserve_newest_review on public.instagram_profile_state;
create trigger igc_preserve_newest_review
before update on public.instagram_profile_state
for each row execute function public.igc_preserve_newest_review();
