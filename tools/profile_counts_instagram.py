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
PROFILE_PICTURE_TERMS = re.compile(r"\b(profile|perfil)\s+(?:picture|photo|pic|image|foto)\b", re.I)


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
        user = user_from_href(anchor.get("href"))
        if not user:
            continue
        # A feed link titled "See profile" is NOT an account-identity signal.
        # Accept only clearly labeled navigation/sidebar anchors.
        if anchor.get("in_navigation") and (
            PROFILE_PICTURE_TERMS.search(str(anchor.get("image_alt") or "")) or
            PROFILE_TERMS.search(label)
        ):
            hits.add(user)
    return next(iter(hits)) if len(hits) == 1 else None


def visible_link_descriptors(page):
    return page.evaluate("""() => [...document.querySelectorAll('a[href], [role=link][href]')]
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
          in_navigation: !!el.closest('nav, aside, [role=navigation]')
        }))""")


def own_profile_from_switcher_rows(rows):
    """A visible compact Switch-account row is positive owner identity evidence.

    Use only ordinary profile links in the SAME small row as the Switch
    control, not unrelated suggested accounts or usernames in feed posts.
    Conflicting rows/links fail closed.
    """
    identities = set()
    for row in rows:
        handles = {u for href in row.get("hrefs", [])
                   if (u := user_from_href(href))}
        if not handles:
            continue
        if len(handles) != 1:
            return None
        identities.update(handles)
    return next(iter(identities)) if len(identities) == 1 else None


def visible_switcher_account_rows(page):
    """Read compact visible own-account / Switch rows on Instagram Home.

    The desktop Home recommendations rail shows the signed-in user adjacent
    to a Switch control even when Instagram hides/restructures Profile nav.
    Never infer identity from 'Suggested for you' links alone.
    """
    return page.evaluate("""() => {
      const visible = (node) => {
        const r = node.getBoundingClientRect();
        return r.width > 0 && r.height > 0 && r.bottom > 0 &&
          r.top < innerHeight && r.right > 0 && r.left < innerWidth;
      };
      const switchLabel = /^(?:switch|cambiar|cambiar cuenta|changer|wechseln)$/i;
      const rows = [], keys = new Set();
      for (const el of document.querySelectorAll('button,[role="button"],a,span,div')) {
        if (el.childElementCount > 3) continue;
        const label = (el.getAttribute('aria-label') || el.textContent || '').trim();
        if (label.length > 30 || !switchLabel.test(label) || !visible(el) ||
            el.closest('[role="dialog"]')) continue;
        let parent = el.parentElement;
        for (let depth=0; parent && depth<7; depth++, parent=parent.parentElement) {
          const r=parent.getBoundingClientRect();
          if (r.width > 760 || r.height > 200) break;
          const hrefs=[...parent.querySelectorAll('a[href]')]
            .filter(visible).map(a => a.getAttribute('href') || '');
          if (!hrefs.length) continue;
          const key=hrefs.join('|');
          if (!keys.has(key)) { rows.push({hrefs}); keys.add(key); }
          break;
        }
      }
      return rows;
    }""")


def signed_in_handle(page):
    """Return exactly one visibly proven logged-in identity, or None.

    Instagram sometimes removes the Profile navigation anchor. An owner's
    own profile with an Edit profile button AND matching header username is
    alternate positive evidence, never an arbitrary URL or a Follow button.
    """
    passwords = page.locator('input[name="password"]')
    if any(passwords.nth(i).is_visible() for i in range(min(passwords.count(), 6))):
        return None
    via_nav = own_profile_from_anchors(visible_link_descriptors(page))
    via_switcher = own_profile_from_switcher_rows(visible_switcher_account_rows(page))
    from_own_page = own_profile_edit_identity(page)
    identities = {h.casefold() for h in (via_nav, via_switcher, from_own_page) if h}
    if len(identities) != 1:
        return None  # never guess if trusted identity signals disagree or vanish
    return next(iter(identities))


def own_profile_edit_identity(page):
    """A named own-profile header AND Edit profile control prove ownership.

    A URL or username heading on someone else's public profile never suffices.
    """
    candidate = user_from_href(getattr(page, "url", ""))
    if not candidate:
        return None
    header = page.locator("header").first
    if not header.count() or not header.is_visible():
        return None
    edit = re.compile(r"^\s*(?:edit profile|editar perfil|modifier le profil|profil bearbeiten)\s*$", re.I)
    controls = [header.get_by_role(role, name=edit) for role in ("button", "link")]
    names = header.locator("h1,h2,[role=heading]").all_inner_texts()
    if sum(c.count() for c in controls) == 1 and any(
        str(n).strip().lstrip("@").casefold() == candidate for n in names
    ):
        return candidate
    return None


def verify_selected_owner_profile(page, expected_handle, *, on_navigation=None):
    """One read-only direct profile visit if Home has no verified identity.

    The selected @handle is a destination, NEVER ownership proof. A matching
    header and visible Edit profile control are required. No API/clicks.
    """
    expected = valid_username(expected_handle)
    if not expected or challenge_detected(page):
        return None
    passwords = page.locator('input[name="password"]')
    if any(passwords.nth(i).is_visible() for i in range(min(passwords.count(), 6))):
        return None
    # Count the ACTUAL own-profile navigation just before Chrome attempts it,
    # not creation of a blank tab that might fail the login/challenge guard.
    if callable(on_navigation):
        on_navigation()
    page.goto(following_page_url(expected), wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(900)
    passwords = page.locator('input[name="password"]')
    if challenge_detected(page) or any(
        passwords.nth(i).is_visible() for i in range(min(passwords.count(), 6))
    ):
        return None
    proven = own_profile_edit_identity(page)
    return expected if proven and proven.casefold() == expected.casefold() else None


def challenge_detected(page):
    """Recognize real Instagram security interstitials without interacting with them.

    Instagram's /auth_platform/recaptcha?apc=... is a separate route from its
    older /challenge/ and /checkpoint/ screens. Never attempt account actions,
    own-profile probing, or repeated navigation while it is visible.
    """
    path = urlparse(getattr(page, "url", "") or "").path.casefold().rstrip("/")
    if any(path == prefix or path.startswith(prefix + "/") for prefix in (
        "/challenge", "/checkpoint", "/auth_platform/recaptcha",
    )):
        return True
    try:
        text = page.locator("body").inner_text(timeout=2500).casefold()
        return any(marker in text for marker in BLOCK_MARKERS) or any(
            phrase in text for phrase in (
                "i'm not a robot", "i’m not a robot", "recaptcha enterprise",
                "verify you are human", "verify you're human",
            )
        )
    except Exception:
        return False


def safe_to_probe_owner_from_home(page):
    """Never navigate off a live login/CAPTCHA screen to infer owner identity.

    The optional read-only profile probe is only appropriate from actual
    Instagram Home with no visible password field. Do not interrupt sign-in,
    login challenges, or an in-progress authentication redirect.
    """
    location = urlparse(getattr(page, "url", "") or "")
    if location.hostname not in ("instagram.com", "www.instagram.com"):
        return False
    if location.path not in ("", "/") or challenge_detected(page):
        return False
    try:
        fields = page.locator('input[type="password"], input[name="password"]')
        return not any(fields.nth(i).is_visible() for i in range(min(fields.count(), 6)))
    except Exception:
        return False


def preserve_instagram_auth_page(page):
    """Do not refresh or navigate away from a restored human login/checkpoint.

    Persistent Chrome may reopen directly at /auth_platform/recaptcha or Login.
    A forced page.goto(Home) at startup disrupts that verification. Existing
    signed-in profile pages remain eligible for normal owner checks.
    """
    location = urlparse(getattr(page, "url", "") or "")
    if location.hostname not in ("instagram.com", "www.instagram.com"):
        return False
    path = location.path.casefold().rstrip("/")
    if any(path == prefix or path.startswith(prefix + "/") for prefix in (
        "/accounts/login", "/accounts/signup", "/auth_platform",
        "/challenge", "/checkpoint",
    )):
        return True
    if challenge_detected(page):
        return True
    try:
        fields = page.locator('input[type="password"], input[name="password"]')
        return any(fields.nth(i).is_visible() for i in range(min(fields.count(), 6)))
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



class FollowingControlUnavailable(RuntimeError):
    """Visible owner Following control is missing/ambiguous; wait for human help."""


FOLLOWING_WORD = re.compile(r"\b(?:following|seguidos|seguidas|suivis|abonnements)\b", re.I)


def _visible_following_dialog(page):
    """Only accept an actual visible Following dialog; not unrelated popups."""
    dialogs = page.locator('[role="dialog"]')
    for i in range(min(dialogs.count(), 6)):
        dialog = dialogs.nth(i)
        if not dialog.is_visible():
            continue
        label = " ".join(filter(None, (
            dialog.get_attribute("aria-label") or "",
            dialog.get_attribute("title") or "",
            dialog.inner_text(timeout=2000)[:180],
        )))
        if FOLLOWING_WORD.search(label):
            return dialog
    return None


def _owner_following_control(page, own):
    """Find the owner's Following control within the profile header only.

    Instagram renders it as an anchor, button or nonsemantic clickable text
    depending on screen and language. Never click a feed/suggested profile.
    """
    header = page.locator("header").first
    if not header.count() or not header.is_visible():
        return None
    selectors = ('a[href*="/following"]', "a", "button", '[role="button"]')
    for selector in selectors:
        controls = header.locator(selector)
        for i in range(min(controls.count(), 24)):
            el = controls.nth(i)
            if not el.is_visible():
                continue
            href = el.get_attribute("href") or ""
            label = " ".join(filter(None, (
                el.get_attribute("aria-label") or "",
                el.get_attribute("title") or "",
                el.inner_text(timeout=2000)[:100],
            )))
            if href and re.search(r"/following/?(?:\?|$)", href, re.I):
                if not re.search(r"^/(?:"+re.escape(own)+r")/following/?", href, re.I):
                    continue
                return el
            if FOLLOWING_WORD.search(label) and len(label) <= 130:
                return el
    # Some Instagram versions attach their click handler to a generic parent,
    # and only a small 'following' text label is exposed inside the header.
    labels = header.get_by_text(FOLLOWING_WORD)
    for i in range(min(labels.count(), 18)):
        el = labels.nth(i)
        if el.is_visible():
            label = el.inner_text(timeout=2000).strip()
            if len(label) <= 60 and FOLLOWING_WORD.search(label):
                return el
    return None


def read_following_visible(page, username, on_batch=None, stop_signal=None,
                           max_scrolls=2500):
    """Read visible profile anchors in the Following dialog as it scrolls.

    Returns (list_of_handles, complete). A list is incomplete if the browser
    dialog cannot be found, loading stalls, or the user stops it.
    """
    own = valid_username(username)
    if not own:
        raise ValueError("Invalid selected Instagram account.")
    # When a user has manually opened Following to help the robot, do not
    # navigate away and destroy the open dialog on the next check.
    on_own_profile = user_from_href(page.url) == own
    if not on_own_profile:
        page.goto(following_page_url(own), wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(900)
    if challenge_detected(page):
        raise RuntimeError("Instagram requested verification or restricted access.")
    if user_from_href(page.url) != own:
        raise FollowingControlUnavailable("Instagram did not display the selected owner's profile.")
    # URL alone is never owner/session proof, including for manual dialog use.
    if signed_in_handle(page) != own and own_profile_edit_identity(page) != own:
        raise FollowingControlUnavailable("The signed-in Instagram owner could not be verified on the profile page.")
    dialog = _visible_following_dialog(page)
    control = _owner_following_control(page, own)
    expected = None
    if control is not None:
        expected = expected_following_count(
            control.get_attribute("title"),
            control.get_attribute("aria-label"),
            control.inner_text(timeout=3000),
        )
    if dialog is None:
        if control is None:
            raise FollowingControlUnavailable(
                "The Following control is not visible in the owner's profile header."
            )
        control.click(timeout=12000)
        try:
            page.locator('[role="dialog"]').last.wait_for(state="visible", timeout=7000)
        except Exception as exc:
            raise FollowingControlUnavailable(
                "The Following list did not open. Open it manually in Chrome."
            ) from exc
        dialog = _visible_following_dialog(page)
        if dialog is None:
            raise FollowingControlUnavailable(
                "The visible popup was not the owner's Following list."
            )

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
