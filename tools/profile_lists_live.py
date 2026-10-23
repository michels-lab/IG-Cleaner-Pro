"""Optional owner-approved, read-only Instagram relationship list snapshot.

Based on the owner-provided same-origin friendships paging reference. This is
not Profile Counts (individual people's numerical counts), does not mutate
relationships, never exports cookies, and never infers a negative from partial
or throttled results. Instagram may change or block this undocumented endpoint.
"""
from __future__ import annotations

from urllib.parse import urlparse

try:
    from .profile_counts_robot import valid_username
    from .profile_counts_instagram import signed_in_handle, challenge_detected
except ImportError:
    from profile_counts_robot import valid_username
    from profile_counts_instagram import signed_in_handle, challenge_detected


class LiveListsUnavailable(RuntimeError):
    """No complete, verifiable read-only list was acquired."""


def _verified_session(page, expected):
    uri = urlparse(getattr(page, "url", "") or "")
    if (uri.scheme != "https" or
            uri.hostname not in ("www.instagram.com", "instagram.com") or
            challenge_detected(page) or
            signed_in_handle(page) != expected):
        raise LiveListsUnavailable(
            "The exact signed-in Instagram owner was not visibly verified. "
            "No live lists or account changes were performed.")


def read_live_friendship_list(page, expected_handle, relation, *, max_pages=250,
                              on_page=None):
    """Read a complete current followers/following list via owner's same-origin Chrome.

    Returns usernames only, never owner ID, session data, or raw network results.
    'not in list' is only meaningful after every cursor page was validated.
    This optional collector is independent of the existing rendered Profile
    Counts robot and does not call any relationship mutation endpoint.
    """
    expected = valid_username(expected_handle)
    if not expected or expected != expected_handle or relation not in ("followers", "following"):
        raise ValueError("Select an exact Instagram owner and a valid read-only list.")
    if type(max_pages) is not int or max_pages < 1 or max_pages > 250:
        raise ValueError("A read-only list is limited to 1–250 pages.")
    _verified_session(page, expected)
    seen, cursor, usernames = set(), None, set()
    for page_number in range(1, max_pages + 1):
        if on_page is not None:
            on_page(relation, page_number)
        _verified_session(page, expected)
        # Session-bound JS runs in the user's existing Instagram tab.
        # It never returns ds_user_id, cookies, headers, or response body.
        packet = page.evaluate("""async ({kind, cursor}) => {
          const item=document.cookie.split('; ').find(x=>x.startsWith('ds_user_id='));
          const id=item ? item.slice('ds_user_id='.length) : '';
          if (!/^\\d{1,24}$/.test(id))return {error:'owner_id_not_available'};
          const url=new URL('/api/v1/friendships/'+id+'/'+kind+'/',location.origin);
          url.searchParams.set('count','100');
          if(cursor)url.searchParams.set('max_id',cursor);
          try{
            const response=await fetch(url.toString(),{
              method:'GET',credentials:'same-origin',
              headers:{'X-IG-App-ID':'936619743392459','X-ASBD-ID':'129477',
                       'X-Requested-With':'XMLHttpRequest',Accept:'application/json'},
              cache:'no-store'
            });
            if(!response.ok)return {error:'http_'+response.status};
            const body=await response.json();
            if(!body||body.status!=='ok'||!Array.isArray(body.users))
              return {error:'unexpected_shape'};
            return {usernames:body.users.map(u=>u?.username??null),
                    next:body.next_max_id??null,has_more:body.has_more??null};
          }catch{return {error:'read_failed'};}
        }""", {"kind": relation, "cursor": cursor})
        if not isinstance(packet, dict) or packet.get("error"):
            reason = packet.get("error") if isinstance(packet, dict) else "invalid_response"
            raise LiveListsUnavailable(
                "Instagram live " + relation + " list unavailable (" + str(reason)[:40] +
                "). List incomplete; no negative relationship conclusions.")
        rows = packet.get("usernames")
        if not isinstance(rows, list) or len(rows) > 100:
            raise LiveListsUnavailable("Live list page was malformed; no conclusions.")
        for item in rows:
            user = valid_username(item)
            if user is None or user != item:
                raise LiveListsUnavailable("Invalid live list username; no conclusions.")
            usernames.add(user.casefold())
        next_cursor = packet.get("next")
        if not next_cursor:
            if packet.get("has_more") is True:
                raise LiveListsUnavailable(
                    "Instagram indicated more profiles without a cursor; list incomplete.")
            _verified_session(page, expected)
            return frozenset(usernames)
        if not isinstance(next_cursor, str) or len(next_cursor) > 512:
            raise LiveListsUnavailable("Invalid pagination cursor; list incomplete.")
        if next_cursor in seen or next_cursor == cursor:
            raise LiveListsUnavailable("Repeated live list cursor; list incomplete.")
        seen.add(next_cursor)
        cursor = next_cursor
        page.wait_for_timeout(800)  # no aggressive pagination / hammering
    raise LiveListsUnavailable(
        "Live list reached its 250-page safety limit. No negative conclusions.")
