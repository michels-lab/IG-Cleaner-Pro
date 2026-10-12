"""Discover the signed-in account and its Following list from rendered Instagram pages.

No GraphQL/private endpoints, network API calls, saved passwords, CAPTCHA handling,
or actions that follow/unfollow accounts. UI selectors are best-effort and require
a real owner-session acceptance test after Instagram changes its layout.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
from urllib.parse import urlparse

try:
    from .profile_counts_robot import valid_username, BLOCK_MARKERS, parse_number
except ImportError:
    from profile_counts_robot import valid_username, BLOCK_MARKERS, parse_number

RESERVED = frozenset((
    "about", "accounts", "api", "challenge", "developer", "direct", "directory",
    "emails", "explore", "graphql", "help", "legal", "login", "logout", "p",
    "privacy", "reels", "reel", "stories", "tags", "terms", "web",
))
PROFILE_TERMS = re.compile(r"\b(profile|perfil|profil|profilo|profilbild)\b", re.I)


def user_from_href(href):
    """Accept only ordinary Instagram /username/ links, never post/API URLs."""
    if not isinstance(href, str) or not href:
        return None
    parsed = urlparse(href)
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return None
    if parsed.netloc and parsed.hostname not in ("www.instagram.com", "instagram.com"):
        return None
    segments = [s for s in parsed.path.split("/") if s]
    if len(segments) != 1 or segments[0].lower() in RESERVED:
        return None
    return valid_username(segments[0])


def own_profile_from_anchors(anchors):
    """Require a clearly labeled Profile navigation link (never guess from feed)."""
    hits = set()
    for anchor in anchors:
        # Profile photos in the FEED also have "profile picture" alt text.
        # Only trust explicit navigation labels or pictures inside the nav.
        label = " ".join(str(anchor.get(k) or "") for k in
                         ("text", "aria", "title", "svg_title", "svg_aria"))
        if anchor.get("in_navigation"):
            label += " " + str(anchor.get("image_alt") or "")
        user = user_from_href(anchor.get("href"))
        if user and PROFILE_TERMS.search(label):
            hits.add(user)
    return next(iter(hits)) if len(hits) == 1 else None


def visible_link_descriptors(page):
    return page.evaluate("""() => [...document.querySelectorAll('a[href]')]
        .filter(el => { const r=el.getBoundingClientRect();
          return r.width>0 && r.height>0 && r.bottom>0; })
        .map(el => ({
          href: el.getAttribute('href') || '',
          text: (el.innerText || '').trim().slice(0,80),
          aria: el.getAttribute('aria-label') || '',
          title: el.getAttribute('title') || '',
          image_alt: el.querySelector('img')?.getAttribute('alt') || '',
          svg_title: el.querySelector('svg title')?.textContent || '',
          svg_aria: el.querySelector('svg[aria-label]')?.getAttribute('aria-label') || '',
          in_navigation: !!el.closest('nav, [role=navigation]')
        }))""")


def signed_in_handle(page):
    """None while login form is visible or account identity remains ambiguous."""
    if page.locator('input[name="password"]').count():
        return None
    return own_profile_from_anchors(visible_link_descriptors(page))


def challenge_detected(page):
    url = (page.url or "").lower()
    if "/challenge/" in url or "/checkpoint/" in url:
        return True
    try:
        text = page.locator("body").inner_text(timeout=2500).lower()
        return any(marker in text for marker in BLOCK_MARKERS)
    except Exception:
        return False


def following_page_url(username):
    return f"https://www.instagram.com/{username}/"


def _scroll_visible_following(dialog):
    """Scroll the largest real scrollable element within the visible dialog."""
    return dialog.evaluate("""el => {
      const all=[el,...el.querySelectorAll('*')];
      const scrollable=all.filter(e => {
        const style=getComputedStyle(e);
        return e.scrollHeight>e.clientHeight+45 && e.clientHeight>60 &&
          ['auto','scroll','overlay'].includes(style.overflowY);
      }).sort((a,b)=>(b.clientHeight*b.scrollHeight)-(a.clientHeight*a.scrollHeight));
      const node=scrollable[0] || all.filter(e=>e.scrollHeight>e.clientHeight+45)
        .sort((a,b)=>b.scrollHeight-a.scrollHeight)[0];
      if(!node) return {scrollable:false,atEnd:true};
      const before=node.scrollTop;
      node.scrollTop=Math.min(node.scrollHeight, before+Math.max(200,node.clientHeight*0.9));
      node.dispatchEvent(new Event('scroll',{bubbles:true}));
      return {scrollable:true,
        atEnd:node.scrollTop+node.clientHeight>=node.scrollHeight-8,
        moved:node.scrollTop>before+1,
        height:node.scrollHeight};
    }""")


def expected_following_count(*labels):
    """Use only an exact, visible Following counter as completion evidence.

    Abbreviations such as 11.8K cannot prove the exact number of handles and
    must not be treated as a successful full scan.
    """
    for label in labels:
        match = re.search(r"(?<!\w)(\d[\d.,\s\u00a0\u202f]*(?:[kKmM]|[ ]mil|[ ]millones)?)",
                          str(label or ""), re.I)
        if not match:
            continue
        parsed = parse_number(match.group(1))
        if parsed and not parsed[1]:
            return parsed[0]
    return None


def reconcile_following_discovery(cached, observed, complete):
    """Preserve older same-account handles during a partial browser rescan.

    A positively completed visible scan replaces the cache: old accounts might
    have been unfollowed. Incomplete scans can only *add* to the provisional
    queue, never erase an earlier checkpoint.
    """
    fresh = list(dict.fromkeys(
        u for raw in observed if (u := valid_username(raw))
    ))
    if complete:
        return fresh
    return list(dict.fromkeys(
        [u for raw in cached if (u := valid_username(raw))] + fresh
    ))


def read_following_visible(page, username, on_batch=None, stop_signal=None,
                           max_scrolls=2500):
    """Read visible profile anchors in the Following dialog as it scrolls.

    Returns (list_of_handles, complete). A list is incomplete if the browser
    dialog cannot be found, loading stalls, or the user stops it.
    """
    own = valid_username(username)
    if not own:
        raise ValueError("Cuenta activa de Instagram inválida.")
    page.goto(following_page_url(own), wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(900)
    if challenge_detected(page):
        raise RuntimeError("Instagram solicita verificación o limita el acceso.")
    links = page.locator('a[href*="/following/"]')
    candidate = None
    for i in range(min(links.count(), 12)):
        link = links.nth(i)
        href = link.get_attribute("href") or ""
        if re.search(r"/" + re.escape(own) + r"/following/?(?:\?|$)", href, re.I):
            candidate = link
            break
    if candidate is None:
        raise RuntimeError("No está visible el enlace Following de la cuenta iniciada.")
    expected = expected_following_count(
        candidate.get_attribute("title"),
        candidate.get_attribute("aria-label"),
        candidate.inner_text(timeout=3000),
    )
    candidate.click(timeout=12000)
    dialog = page.locator('[role="dialog"]').last
    dialog.wait_for(state="visible", timeout=12000)

    seen = set()
    collected = []
    no_progress = 0
    prior = 0
    for _ in range(max_scrolls):
        if stop_signal and stop_signal.is_set():
            return collected, False
        hrefs = dialog.locator("a[href]").evaluate_all(
            "(els) => els.map(a => a.getAttribute('href') || '')")
        for href in hrefs:
            u = user_from_href(href)
            if u and u != own and u not in seen:
                seen.add(u)
                collected.append(u)
        if len(collected) != prior:
            prior = len(collected)
            no_progress = 0
            if on_batch:
                on_batch(list(collected), False)
        else:
            no_progress += 1
        scroll = _scroll_visible_following(dialog)
        if scroll.get("atEnd") and no_progress >= 4:
            # Scrolling to the bottom is not proof that lazy-loaded Following
            # finished. Never claim completeness when fewer handles than an
            # exact visible total were read, or when only a rounded count exists.
            complete = expected is not None and len(collected) >= expected
            if on_batch:
                on_batch(list(collected), complete)
            return collected, complete
        if no_progress >= 18:
            return collected, False
        page.wait_for_timeout(450)
    return collected, False


def write_following_cache(file: Path, handle: str, users, complete: bool):
    file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "igc-browser-following-v1",
        "instagram_handle": valid_username(handle),
        "usernames": list(dict.fromkeys(u for user in users if (u := valid_username(user)))),
        "complete": bool(complete),
        "updated_at": time.time()
    }
    tmp = file.with_suffix(file.suffix+".tmp")
    with tmp.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, ensure_ascii=False, separators=(",", ":"))
        fp.flush()
        os.fsync(fp.fileno())
    os.replace(tmp, file)


def read_following_cache(file: Path, handle: str):
    if not file.exists():
        return []
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        if (data.get("schema") != "igc-browser-following-v1" or
                data.get("instagram_handle") != valid_username(handle)):
            return []
        return list(dict.fromkeys(
            u for val in data.get("usernames", [])
            if (u := valid_username(val))
        ))
    except (OSError, ValueError, TypeError, AttributeError):
        return []
