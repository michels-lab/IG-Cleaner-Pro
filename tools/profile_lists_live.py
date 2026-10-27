"""Read-only Instagram relationship lists from authenticated same-origin bulk pages.

Own implementation of the owner's supplied idea: download the two membership
collections via sequential JSON cursor pages, compare stable numeric account IDs,
not HTML profile visits. Do not copy third-party bundled code, take actions, send
cookies elsewhere, or treat a partial result as complete.

Instagram's private endpoints are undocumented and may refuse this read.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

try:
    from .profile_counts_robot import valid_username
    from .profile_counts_instagram import signed_in_handle, challenge_detected
except ImportError:
    from profile_counts_robot import valid_username
    from profile_counts_instagram import signed_in_handle, challenge_detected


class LiveListsUnavailable(RuntimeError):
    """No complete, verifiable read-only list was acquired."""


# A *page* is an API JSON response holding many members, not a user profile.
# Instagram can return far fewer than the requested count; 250 pages cannot
# safely be translated into "25,000 accounts". Bound both pages and records.
DEFAULT_MAX_PAGES = 1500
DEFAULT_PAGE_SIZE = 200
MAX_UNIQUE_USERS = 100_000
MAX_STALLED_PAGES = 8
_NUMERIC_ID = re.compile(r"^[0-9]{1,30}$")


def _verified_session(page, expected):
    uri = urlparse(getattr(page, "url", "") or "")
    if (uri.scheme != "https" or
            uri.hostname not in ("www.instagram.com", "instagram.com") or
            challenge_detected(page) or
            signed_in_handle(page) != expected):
        raise LiveListsUnavailable(
            "The exact signed-in Instagram owner was not visibly verified. "
            "No live lists or account changes were performed.")


def read_live_friendship_list(page, expected_handle, relation, *,
                              max_pages=DEFAULT_MAX_PAGES,
                              page_size=DEFAULT_PAGE_SIZE,
                              on_page=None, on_progress=None,
                              identities=False):
    """Read an ENTIRE followers/following membership set using paginated GET.

    identities=True returns {stable_numeric_instagram_id: username} for reliable
    cross-list membership comparison. The default returns a frozen set of names
    for legacy read-only consumers. Never visits an individual target profile.
    No partial results escape this function: 429/challenge/owner mismatch,
    cursor errors, duplicate IDs, budget or empty-page stalls all fail closed.
    """
    expected = valid_username(expected_handle)
    if not expected or expected != expected_handle or relation not in ("followers", "following"):
        raise ValueError("Select an exact Instagram owner and a valid read-only list.")
    if type(max_pages) is not int or not 1 <= max_pages <= DEFAULT_MAX_PAGES:
        raise ValueError("Read-only bulk collection must have a 1–1500-page budget.")
    if type(page_size) is not int or not 1 <= page_size <= DEFAULT_PAGE_SIZE:
        raise ValueError("Read-only bulk collection uses 1–200 members per request.")
    if type(identities) is not bool:
        raise ValueError("Identity comparison must be explicitly enabled.")

    _verified_session(page, expected)
    seen_cursors, cursor = set(), None
    names, id_to_name, name_to_id = set(), {}, {}
    stalled = 0
    for page_number in range(1, max_pages + 1):
        if on_page is not None:
            on_page(relation, page_number)
        _verified_session(page, expected)
        # ONLY one same-origin JSON request for a whole chunk of people.
        # No GET to each person's profile; no POST / GraphQL mutations.
        # Credentials remain in the owner's own Chrome context.
        packet = page.evaluate("""async ({kind, cursor, pageSize}) => {
          const cookie=document.cookie.split('; ').find(x=>x.startsWith('ds_user_id='));
          const ownerId=cookie ? cookie.slice('ds_user_id='.length) : '';
          if (!/^[0-9]{1,24}$/.test(ownerId))return {error:'owner_id_not_available'};
          const url=new URL('/api/v1/friendships/'+ownerId+'/'+kind+'/',location.origin);
          url.searchParams.set('count',String(pageSize));
          if(cursor)url.searchParams.set('max_id',cursor);
          try{
            const response=await fetch(url.toString(),{
              method:'GET',credentials:'same-origin',
              headers:{'X-IG-App-ID':'936619743392459','X-ASBD-ID':'129477',
                       'X-Requested-With':'XMLHttpRequest',Accept:'application/json'},
              cache:'no-store',signal:AbortSignal.timeout(20000)
            });
            if(!response.ok)return {error:'http_'+response.status};
            const body=await response.json();
            if(!body||body.status!=='ok'||!Array.isArray(body.users))
              return {error:'unexpected_shape'};
            return {
              members:body.users.map(u=>({
                id:u?.pk??u?.id??u?.pk_id??null,
                username:u?.username??null
              })),
              next:body.next_max_id==null?null:String(body.next_max_id),
              has_more:body.has_more??null
            };
          }catch{return {error:'read_failed'};}
        }""", {"kind": relation, "cursor": cursor, "pageSize": page_size})
        if (not isinstance(packet, dict) or packet.get("error") or
                packet.get("status") not in (None, "ok")):
            reason = packet.get("error") if isinstance(packet, dict) else "invalid_response"
            raise LiveListsUnavailable(
                "Instagram's bulk " + relation + " request failed (" + str(reason)[:40] +
                "). No incomplete/negative membership conclusions.")

        members = packet.get("members")
        # Support legacy read-only *test fixtures*, not incomplete live IDs:
        # our actual Chrome JavaScript ALWAYS returns the members shape.
        legacy = members is None and not identities
        rows = packet.get("usernames") if legacy else members
        if not isinstance(rows, list) or len(rows) > page_size:
            raise LiveListsUnavailable("Malformed bulk list page; no conclusions.")
        count_before = len(names)
        for member in rows:
            if legacy:
                username, member_id = member, None
            elif isinstance(member, dict):
                username, member_id = member.get("username"), member.get("id")
            else:
                raise LiveListsUnavailable("Live list member is malformed.")
            valid = valid_username(username)
            if valid is None or valid != username:
                raise LiveListsUnavailable("Invalid username in Instagram bulk page.")
            name = valid.casefold()
            if not legacy:
                stable_id = str(member_id) if type(member_id) in (int, str) else ""
                if not _NUMERIC_ID.fullmatch(stable_id):
                    raise LiveListsUnavailable("Instagram did not supply stable member IDs.")
                if stable_id in id_to_name and id_to_name[stable_id] != name:
                    raise LiveListsUnavailable("Account identity changed during bulk scan.")
                if name in name_to_id and name_to_id[name] != stable_id:
                    raise LiveListsUnavailable("Conflicting account IDs during bulk scan.")
                id_to_name[stable_id], name_to_id[name] = name, stable_id
            names.add(name)

        if len(names) > MAX_UNIQUE_USERS:
            raise LiveListsUnavailable(
                "Bulk list exceeded its 100,000-member memory safety budget. "
                "No partial results are considered complete.")
        if on_progress is not None:
            on_progress(relation, len(names))
        next_cursor = packet.get("next")
        # Only an explicit terminal proof may support "not following back".
        if type(packet.get("has_more")) is not bool:
            raise LiveListsUnavailable(
                "Instagram omitted pagination completeness; no negative conclusions.")
        if not next_cursor:
            if packet["has_more"] is True:
                raise LiveListsUnavailable("Instagram indicates more members but no cursor.")
            _verified_session(page, expected)
            return dict(id_to_name) if identities else frozenset(names)
        if packet["has_more"] is False:
            raise LiveListsUnavailable("Instagram supplied cursor but has_more=false.")
        if not isinstance(next_cursor, str) or len(next_cursor) > 512:
            raise LiveListsUnavailable("Invalid Instagram bulk pagination cursor.")
        if next_cursor == cursor or next_cursor in seen_cursors:
            raise LiveListsUnavailable("Repeating Instagram bulk cursor; scan incomplete.")
        stalled = stalled + 1 if count_before == len(names) else 0
        if stalled >= MAX_STALLED_PAGES:
            raise LiveListsUnavailable(
                "Instagram bulk pagination stopped yielding new accounts; "
                "no false negative conclusions.")
        seen_cursors.add(next_cursor)
        cursor = next_cursor
        page.wait_for_timeout(800)  # conservative read-only pacing
    raise LiveListsUnavailable(
        "Bulk " + relation + " pagination remained unfinished after " +
        str(max_pages) + " pages (" + str(len(names)) +
        " unique accounts received). This was NOT a per-profile scan. "
        "No partial/negative conclusions.")
