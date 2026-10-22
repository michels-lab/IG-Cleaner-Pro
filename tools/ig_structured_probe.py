#!/usr/bin/env python3
"""Conservative read-only structured Instagram lookup in the OWNER'S browser.

The URL/headers are based on a user-provided, unverified Webpack sample. This
is not an official Instagram API, not a network-accessible server and not a
replacement for a live owner-verified test. Browser-session secrets must NEVER
leave the browser execution context or appear in the returned diagnostics.

No mutations, follow/unfollow/cancel, session export or API retry. A missing
search hit NEVER proves "not following", including after HTTP 200.
"""
from __future__ import annotations

from urllib.parse import urlparse

from profile_counts_robot import valid_username

# Static JavaScript only. No input may be interpolated into source; execute
# inside an independently verified signed-in Instagram page in Chrome.
_READ_ONLY_FOLLOWING_LOOKUP = r"""
async ({username}) => {
  const unknown = () => ({code: 'STRUCTURED_UNAVAILABLE'});
  const host = window.location.hostname;
  if (host !== 'www.instagram.com' && host !== 'instagram.com') return unknown();
  if (window.location.protocol !== 'https:') return unknown();
  if (!/^[A-Za-z0-9._]{1,30}$/.test(username)) return unknown();

  const cookieValue = key => {
    const item = document.cookie.split(';').map(s => s.trim()).find(s =>
      s.startsWith(key + '='));
    return item ? decodeURIComponent(item.slice(key.length + 1)) : '';
  };
  // Only the numeric owner ID is used. It and the CSRF token remain in Chrome.
  const ownerId = cookieValue('ds_user_id');
  if (!/^\d{1,24}$/.test(ownerId)) return {code: 'STRUCTURED_SESSION_REQUIRED'};
  const url = new URL('/api/v1/friendships/' + ownerId + '/following/', location.origin);
  url.searchParams.set('count', '50');
  url.searchParams.set('query', username);
  url.searchParams.set('search_surface', 'follow_list_page');

  const headers = {'Accept': 'application/json',
                   'X-IG-App-ID': '936619743392459',
                   'X-ASBD-ID': '129477',
                   'X-Requested-With': 'XMLHttpRequest'};
  const csrf = cookieValue('csrftoken');
  if (csrf) headers['X-CSRFToken'] = csrf;
  const abort = new AbortController();
  const timeout = setTimeout(() => abort.abort(), 12000);
  try {
    // GET only, no body, no Instagram relationship mutations or retries.
    const response = await fetch(url.toString(), {
      method: 'GET', credentials: 'same-origin', redirect: 'error',
      headers, signal: abort.signal
    });
    if (response.status === 429 || response.status === 403)
      return {code: 'STRUCTURED_RATE_LIMITED'};
    if (!response.ok) return unknown();
    const data = await response.json();
    if (!data || data.status === 'fail' || !Array.isArray(data.users))
      return unknown();

    const exact = data.users.filter(u => u && typeof u.username === 'string' &&
        u.username.toLowerCase() === username.toLowerCase());
    if (exact.length !== 1) return unknown();
    const id = String(exact[0].pk_id ?? exact[0].pk ?? exact[0].id ?? '');
    if (!/^\d{1,24}$/.test(id)) return unknown();
    // The query is bounded. A POSITIVE exact match is evidence that the
    // backend returned this following entry. ABSENCE is not negative proof.
    return {code: 'FOLLOWING_STRUCTURED'};
  } catch (_) {
    return unknown();
  } finally {
    clearTimeout(timeout);
  }
}
"""

_STRUCTURED_CODES = frozenset({
    "FOLLOWING_STRUCTURED", "STRUCTURED_RATE_LIMITED",
    "STRUCTURED_SESSION_REQUIRED", "STRUCTURED_UNAVAILABLE",
})


def inspect_structured_following(page, username: str, *, owner_verified: bool = False) -> str:
    """One private read-only GET; never performs a mutation or proves absence.

    Caller MUST independently verify the signed-in owner and precise target
    before calling. Explicit flag prevents accidental use in non-verified
    workflows; credentials stay inside the page.evaluate JavaScript.
    """
    if not owner_verified or valid_username(username) != username:
        return "STRUCTURED_UNAVAILABLE"
    try:
        current = urlparse(page.url)
        if (current.scheme != "https" or
                current.hostname not in ("instagram.com", "www.instagram.com") or
                current.path.strip("/").casefold() != username.casefold()):
            return "STRUCTURED_UNAVAILABLE"
        output = page.evaluate(_READ_ONLY_FOLLOWING_LOOKUP, {"username": username})
        if isinstance(output, dict) and output.get("code") in _STRUCTURED_CODES:
            return output["code"]
    except Exception:
        pass
    return "STRUCTURED_UNAVAILABLE"
