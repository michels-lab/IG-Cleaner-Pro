-- Applied to ig-cleaner-sync on 2026-11-13 UTC.
-- A delayed device must not revert a newer Following/Followers/Pending import.
-- Source captured_at represents the original successful user import time.
-- Protection works for legacy and isolated Instagram profile tables.
create or replace function public.igc_preserve_newest_list_snapshot()
returns trigger
language plpgsql
security invoker
set search_path = ''
as $$
begin
  if new.captured_at <= old.captured_at then
    return old;
  end if;
  return new;
end
$$;

drop trigger if exists igc_preserve_newest_list_snapshot on public.list_snapshots;
create trigger igc_preserve_newest_list_snapshot
before update on public.list_snapshots
for each row execute function public.igc_preserve_newest_list_snapshot();

drop trigger if exists igc_preserve_newest_list_snapshot on public.instagram_list_snapshots;
create trigger igc_preserve_newest_list_snapshot
before update on public.instagram_list_snapshots
for each row execute function public.igc_preserve_newest_list_snapshot();
