#!/usr/bin/env python3
"""Owner-approved Instagram browser actions (not Meta API).

Actions run only against a named, visible Chrome session. A changed layout,
unverified account, login challenge or ambiguous result stops the job.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import urlparse

from profile_counts_instagram import signed_in_handle, challenge_detected, verify_selected_owner_profile, preserve_instagram_auth_page
from profile_counts_robot import valid_username
from profile_counts_pacing import (
    check_pacing, check_batch_rest, history_path, batch_path, load_history,
    load_batch_state, wait_required, batch_wait, register_visit, finish_visit,
    finish_batch_visit,
)

TASKS = {"unfollow": "unfollow", "cancel": "cancel request", "audit": "read-only followback audit"}
ACTION_WINDOW_MINUTES = 60
MAX_ACTIONS_PER_JOB = 1000

# Retry only verified pre-click misses after owner approves a new batch.
MISSING_RELATIONSHIP_CONTROL = (
    "The profile does not show the state required for this action. "
    "No unique Following/Requested control was found in the verified target profile; "
    "nothing clicked."
)
LEGACY_MISSING_RELATIONSHIP_CONTROL = "The profile does not show the state required for this action."


def _atomic_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, type(default)):
            raise ValueError("Tipo de registro incorrecto.")
        return value
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError("Corrupted robot activity journal. Review it before continuing.") from exc


MAX_ACTION_TABS = 10
ACTION_CONTROL_WAIT_MS = 20000



class ActionTabPool:
    """Keep up to ten visible target tabs; close only verified outcomes.

    Playwright pages are owned by the existing single robot thread. A pending
    manual review stays open and consumes a slot; it is never silently recycled
    for a different Instagram profile or replayed.
    """

    def __init__(self, context, limit=MAX_ACTION_TABS):
        self.context = context
        self.limit = limit
        self.tabs = {}

    def _prune_manually_closed(self):
        for user, item in list(self.tabs.items()):
            if item["page"].is_closed():
                self.tabs.pop(user, None)

    def open(self, username):
        self._prune_manually_closed()
        if username in self.tabs or len(self.tabs) >= self.limit:
            return None
        target = self.context.new_page()
        self.tabs[username] = {"page": target, "status": "checking",
                               "visit_started_at": None}
        return target

    def prepared(self, username):
        """Return the existing live target tab, never allocate another."""
        self._prune_manually_closed()
        item = self.tabs.get(username)
        return item["page"] if item is not None else None

    def record(self, username, status):
        item = self.tabs.get(username)
        if item is None:
            return
        if status in ("ok", "skipped"):
            # A confirmed result (or explicit pre-click skip) can be closed.
            # An ambiguous action, including post-click session loss, cannot.
            if not item["page"].is_closed():
                item["page"].close()
            self.tabs.pop(username, None)
        else:
            item["status"] = status

    def overview(self):
        self._prune_manually_closed()
        return [{"username": user, "status": item["status"]}
                for user, item in self.tabs.items()]

    def has_open_tabs(self):
        return bool(self.overview())


def _users(raw):
    if not isinstance(raw, list) or len(raw) > MAX_ACTIONS_PER_JOB:
        raise ValueError("The batch must contain no more than 1,000 profiles.")
    out = []
    for item in raw:
        user = valid_username(item)
        if not user:
            raise ValueError("The batch contains an invalid username.")
        if user not in out:
            out.append(user)
    return out


def _visible_named_control(root, words, roles=("button", "menuitem"), text_fallback=False):
    """A uniquely named, visible control; duplicates and uncertainty fail closed."""
    for word in words:
        label = re.compile(r"^\s*(?:" + word + r")\s*$", re.I)
        seen = []
        for role in roles:
            matches = root.get_by_role(role, name=label)
            try:
                if matches.count() > 8:
                    raise RuntimeError("Too many matching controls; manual review required.")
                seen.extend(matches.nth(i) for i in range(matches.count())
                            if matches.nth(i).is_visible())
            except RuntimeError:
                raise
            except Exception:
                continue
        if not seen and text_fallback:
            try:
                matches = root.get_by_text(label, exact=True)
                if matches.count() > 8:
                    raise RuntimeError("Too many matching text labels; manual review required.")
                seen.extend(matches.nth(i) for i in range(matches.count())
                            if matches.nth(i).is_visible())
            except RuntimeError:
                raise
            except Exception:
                continue
        if len(seen) == 1:
            return seen[0]
        if len(seen) > 1:
            raise RuntimeError("Multiple equivalent options were found. No ambiguous click will be performed.")
    return None


def _visible_button(root, words):
    return _visible_named_control(root, words, roles=("button",))


_PROFILE_HERO_PROBE = r"""
(main, info) => {
    // Read-only DOM survey: never click or mutate Instagram. Do not export
    // page text, cookies, follower lists, DOM snippets or login information.
    const cleaned = value => String(value || "")
        .replace(/[\u200b-\u200d\ufeff]/g, "")
        .replace(/[▼▾⌄∨˅⌃]/g, " ")
        .replace(/\s+/g, " ").trim().toLowerCase();
    const visible = element => {
        if (!element) return false;
        const box = element.getBoundingClientRect();
        const css = getComputedStyle(element);
        return box.width > 5 && box.height > 5 &&
               css.display !== "none" && css.visibility !== "hidden";
    };
    const root = main.getBoundingClientRect();
    // Instagram may render the username as a span/div, not an h1/h2/h3.
    // Require the *visible exact target handle* in the upper profile hero.
    const target = cleaned(info.username);
    const anchors = Array.from(
        main.querySelectorAll("h1,h2,h3,span,div,a,strong"), element => element
    ).slice(0, 2500).filter(element => {
        if (!visible(element)) return false;
        const box = element.getBoundingClientRect();
        const label = cleaned(element.innerText).replace(/^@/, "");
        return label === target && box.top >= root.top - 24 &&
               box.top - root.top < 650;
    }).sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
    const anchor = anchors[0];
    const words = (info.words || []).map(cleaned);
    const controls = Array.from(main.querySelectorAll(
        'button,[role="button"],[tabindex="0"]'
    )).slice(0, 300);
    let exactText = 0;
    let near = 0;
    const selected = [];
    controls.forEach((element, index) => {
        if (!visible(element) || element.closest('nav,aside,article,[role="dialog"],[role="menu"]')) return;
        const text = cleaned(element.innerText);
        const aria = cleaned(element.getAttribute("aria-label"));
        if (!words.includes(text) && !words.includes(aria)) return;
        exactText++;
        if (!anchor) return;
        const r = element.getBoundingClientRect();
        const a = anchor.getBoundingClientRect();
        const dx = Math.abs((r.left+r.right)/2 - (a.left+a.right)/2);
        const dy = r.top - a.top;
        if (dx > 800 || dy < -100 || dy > 450 ||
            r.top - root.top > 900) return;
        near++;
        selected.push(index);
    });
    // A Following counter/link is never an action candidate. Count only
    // clickable role/button/tabindex elements, not visual text nodes.
    return {
        target_visible: Boolean(anchor),
        match_count: selected.length,
        candidate_indices: selected,
        control_text_count: exactText,
        near_controls: near,
        main_present: true
    };
}
"""


def _profile_hero_probe(page, username, words):
    """Bounded, read-only control/identity evidence from the actual robot tab."""
    try:
        main = page.locator("main").first
        if not main.count() or not main.is_visible():
            return {"target_visible": False, "main_present": False,
                    "control_text_count": 0, "candidate_indices": []}
        # Static vocabulary only, no untrusted selectors/evaluation code.
        names = [re.sub(r"\\", "", word) for word in words]
        result = main.evaluate(_PROFILE_HERO_PROBE,
                               {"username": username, "words": names})
        if isinstance(result, dict):
            return result
    except Exception:
        pass
    return {"target_visible": False, "main_present": True,
            "control_text_count": 0, "candidate_indices": [], "unavailable": True}


def _profile_relationship_control(page, username, words):
    """Find one visible action in the verified target's profile hero.

    The <header>-only/semantic-heading-only selector in v120.49 missed real
    Following buttons. Instagram can render its heading in <span> and controls
    in nested divs. A read-only survey checks exact profile username plus
    action location. Never click a Following count or another user's control.
    """
    current = urlparse(page.url)
    if (current.hostname not in ("www.instagram.com", "instagram.com")
            or current.path.strip("/").casefold() != username.casefold()):
        return None
    labels = [r"(?:%s)(?:\s*[▾▼⌄])?" % word for word in words]
    header = page.locator("header").first
    if header.count() and header.is_visible():
        found = _visible_named_control(header, labels, roles=("button",))
        if found is not None:
            return found
    probe = _profile_hero_probe(page, username, words)
    indices = probe.get("candidate_indices", [])
    if len(indices) > 1:
        raise RuntimeError("Multiple equivalent options: Multiple matching profile action controls; no click. Manual review required.")
    if not probe.get("target_visible") or len(indices) != 1:
        if not probe.get("target_visible"):
            return None
        return _profile_visual_pointer_control(page, username, words)
    main = page.locator("main").first
    control = main.locator('button,[role="button"],[tabindex="0"]').nth(indices[0])
    if not control.is_visible():
        return None
    return control



_POINTER_PROFILE_PROBE = r"""
(main, info) => {
    // Return only a safe DOM handle and a count. No raw HTML/page text leaves Chrome.
    const clean = value => String(value || "").replace(/[\u200b-\u200d\ufeff]/g, "")
        .replace(/[▼▾⌄∨˅⌃]/g, " ").replace(/\s+/g, " ").trim().toLowerCase();
    const visible = el => {
        if (!el || el.closest('nav,aside,article,[role="dialog"],[role="menu"]')) return false;
        const r = el.getBoundingClientRect(), css = getComputedStyle(el);
        return r.width > 5 && r.height > 5 &&
            css.display !== "none" && css.visibility !== "hidden";
    };
    const rect = main.getBoundingClientRect();
    const anchors = [...main.querySelectorAll("h1,h2,h3,span,div,strong")]
        .filter(el => visible(el) && clean(el.innerText).replace(/^@/, "") === clean(info.username)
            && el.getBoundingClientRect().top >= rect.top - 24
            && el.getBoundingClientRect().top - rect.top < 650);
    if (!anchors.length) return {count: 0, element: null};
    const anchor = anchors[0].getBoundingClientRect();
    const validWords = (info.words || []).map(clean);
    const selected = new Set();
    for (const leaf of main.querySelectorAll("span,div,strong")) {
        if (!visible(leaf) || !validWords.includes(clean(leaf.innerText))) continue;
        let el = leaf, found = null;
        for (let depth = 0; el && depth < 5 && el !== main; depth++, el = el.parentElement) {
            if (!visible(el) || el.closest("a[href]")) break;
            const tag = el.tagName.toLowerCase();
            if (tag === "a") break;
            const text = clean(el.innerText);
            // Never click a multi-control container or a numeric Following count.
            if (text !== clean(leaf.innerText)) break;
            const css = getComputedStyle(el);
            if (tag === "button" || el.getAttribute("role") === "button" ||
                el.tabIndex === 0 || css.cursor === "pointer") {
                found = el;
            }
        }
        if (!found || !visible(found)) continue;
        const r = found.getBoundingClientRect();
        const dx = Math.abs((r.left+r.right-anchor.left-anchor.right)/2);
        const dy = r.top - anchor.top;
        if (dx > 800 || dy < -100 || dy > 450 || r.top-rect.top > 900) continue;
        selected.add(found);
    }
    // Ignore nested text containers referring to the same clickable ancestor.
    const uniq = [...selected].filter(el => ![...selected].some(other =>
        el !== other && other.contains(el) && clean(other.innerText) === clean(el.innerText)));
    return {count: uniq.length, element: uniq.length === 1 ? uniq[0] : null};
}
"""


def _profile_visual_pointer_control(page, username, words):
    """Bounded fallback for unique cursor-pointer Instagram div/span controls.

    The cursor alone is insufficient: exact target URL, target hero username,
    unique Following/Requested label and geometric scope are all required.
    """
    main = page.locator("main").first
    if not main.count() or not main.is_visible():
        return None
    handle = main.evaluate_handle(_POINTER_PROFILE_PROBE, {
        "username": username, "words": [re.sub(r"\\", "", word) for word in words]})
    try:
        count = handle.get_property("count").json_value()
        if count > 1:
            raise RuntimeError("Multiple equivalent options: ambiguous visual Instagram relationship controls; no click.")
        if count != 1:
            return None
        control = handle.get_property("element").as_element()
        if control is None or not control.is_visible():
            return None
        return control
    finally:
        handle.dispose()

def _notify_readiness(on_wait, phase, started_at, timeout_ms):
    """Progress-only callback; does not decide which Instagram element to click."""
    if on_wait:
        on_wait(phase, max(0, int(time.monotonic() - started_at)),
                max(1, int(timeout_ms / 1000)))


def _wait_for_target_profile_shell(page, username, *, timeout_ms=None,
                                   on_wait=None, can_act=None):
    """Wait for the target's *rendered* identity region, not DOMContentLoaded."""
    timeout_ms = ACTION_CONTROL_WAIT_MS if timeout_ms is None else timeout_ms
    started_at = time.monotonic()
    deadline = started_at + timeout_ms / 1000.0
    while True:
        if can_act and not can_act(username):
            return False
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return False
        current = urlparse(page.url)
        if (current.hostname not in ("www.instagram.com", "instagram.com")
                or current.path.strip("/").casefold() != username.casefold()):
            return False
        header = page.locator("header").first
        if header.count() and header.is_visible() and header.inner_text(timeout=2000).strip():
            return True
        if _profile_hero_probe(page, username, []).get("target_visible"):
            return True
        _notify_readiness(on_wait, "loading_profile", started_at, timeout_ms)
        remaining_ms = int((deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            return False
        page.wait_for_timeout(min(500, remaining_ms))


def _wait_for_profile_relationship_control(page, username, words, *,
                                           timeout_ms=None,
                                           on_wait=None, can_act=None):
    """Wait for the real target to finish rendering; never infer no-follow from loading."""
    timeout_ms = ACTION_CONTROL_WAIT_MS if timeout_ms is None else timeout_ms
    started_at = time.monotonic()
    deadline = started_at + timeout_ms / 1000.0
    while True:
        if can_act and not can_act(username):
            return None
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return None
        current = urlparse(page.url)
        if (current.hostname not in ("www.instagram.com", "instagram.com")
                or current.path.strip("/").casefold() != username.casefold()):
            return None
        control = _profile_relationship_control(page, username, words)
        if control is not None:
            return control
        # A blank shell is not evidence that Instagram lacks Following.
        header = page.locator("header").first
        has_header = bool(header.count() and header.is_visible())
        main = page.locator("main").first
        has_main = bool(main.count() and main.is_visible())
        phase = ("waiting_relationship_control" if has_header or has_main
                 else "loading_profile")
        _notify_readiness(on_wait, phase, started_at, timeout_ms)
        remaining_ms = int((deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            return None
        page.wait_for_timeout(min(500, remaining_ms))


def _wait_for_unfollow_option(page, username, *, timeout_ms=None,
                              on_wait=None):
    """Wait for a unique menu action without repeating the Following click."""
    timeout_ms = ACTION_CONTROL_WAIT_MS if timeout_ms is None else timeout_ms
    started_at = time.monotonic()
    deadline = started_at + timeout_ms / 1000.0
    while True:
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return None
        current = urlparse(page.url)
        if (current.hostname not in ("www.instagram.com", "instagram.com")
                or current.path.strip("/").casefold() != username.casefold()):
            return None
        choice = _unfollow_option(page)
        if choice is not None:
            return choice
        _notify_readiness(on_wait, "waiting_unfollow_menu", started_at, timeout_ms)
        remaining_ms = int((deadline - time.monotonic()) * 1000)
        if remaining_ms <= 0:
            return None
        page.wait_for_timeout(min(500, remaining_ms))


def _relationship_layout_note(page, username, words):
    """Plain category-only evidence; never include owner credentials or DOM."""
    probe = _profile_hero_probe(page, username, words)
    return (" Profile layout: main=" +
            ("yes" if probe.get("main_present") else "no") +
            ", exact username=" + ("yes" if probe.get("target_visible") else "no") +
            ", named interactive controls=" + str(probe.get("control_text_count", 0)) +
            ", eligible controls=" + str(len(probe.get("candidate_indices", []))) +
            (", read-only inspection unavailable" if probe.get("unavailable") else "") +
            ". Nothing clicked.")


def _unfollow_option(page):
    """Look in an opened action menu/dialog first; never follow unrelated UI text."""
    names = [r"Unfollow", r"Dejar de seguir"]
    # Public profiles typically show an action menu (not a confirmation dialog).
    for selector in ('[role="menu"]', '[role="dialog"]', '[role="listbox"]'):
        areas = page.locator(selector)
        try:
            visible = [areas.nth(i) for i in range(min(areas.count(), 8))
                       if areas.nth(i).is_visible()]
        except Exception:
            visible = []
        if visible:
            if len(visible) > 1:
                raise RuntimeError("Multiple menus are open; manual review required.")
            return _visible_named_control(visible[0], names, text_fallback=True)
    # Some Instagram menus are rendered as plain DOM without a menu role.
    # Only do a global search after verifying the user's active session AND
    # that the current page is the exact intended target profile.
    return _visible_named_control(page, names, text_fallback=True)


def _visible_dialog(page):
    """Choose the single visible dialog; Instagram can leave hidden dialogs in DOM."""
    dialogs = page.locator('[role="dialog"]')
    total = dialogs.count()
    if total > 12:
        raise RuntimeError("Too many dialogs; manual review required.")
    open_dialogs = [dialogs.nth(i) for i in range(total)
                    if dialogs.nth(i).is_visible()]
    if len(open_dialogs) > 1:
        raise RuntimeError("Multiple dialogs are visible. No ambiguous click will be performed.")
    return open_dialogs[0] if open_dialogs else None


def _request_cancel_confirmation(dialog, username):
    """Recognize the pending-request dialog Instagram currently labels Unfollow.

    An ordinary unfollow and a rejected follow request can share the same
    action label. The positive evidence is Requested on the header (checked by
    caller), the request-to-follow-again warning, and the exact target @handle.
    A bare Cancel button is always a dismiss option, never cancel-request.
    """
    explicit = _visible_named_control(
        dialog, [r"Cancel Request", r"Cancelar solicitud",
                 r"Retirar solicitud", r"Withdraw Request"], text_fallback=True)
    if explicit is not None:
        return explicit
    unfollow = _visible_named_control(
        dialog, [r"Unfollow", r"Dejar de seguir"], text_fallback=True)
    if unfollow is None:
        return None
    context = dialog.inner_text(timeout=4000)
    # A trailing period may be sentence punctuation, but @handle.extra is
    # a different Instagram username and must not pass an exact-match gate.
    expected = (r"(?<![A-Za-z0-9_.])@" + re.escape(username)
                + r"(?![A-Za-z0-9_]|\.[A-Za-z0-9_])")
    if not re.search(expected, context, re.I):
        return None
    english = (re.search(r"\brequest\s+to\s+follow\b", context, re.I) and
               re.search(r"\bagain\b", context, re.I))
    spanish = (re.search(r"\bsolicitud\b|\bsolicitar\b", context, re.I) and
               re.search(r"\bseguir\b", context, re.I) and
               re.search(r"\bvolver\b|\botra\b|\bde\s+nuevo\b|\bnuevamente\b",
                         context, re.I))
    if not (english or spanish):
        return None
    return unfollow


def _follow_state(page, username):
    """Verify the result on the exact target, not an unrelated Follow link."""
    if _profile_relationship_control(page, username, [r"Follow Back", r"Seguir también"]):
        return "follow_back"
    if _profile_relationship_control(page, username, [r"Follow", r"Seguir"]):
        return "follow"
    return None



def _verified_action_owner(page, expected_handle):
    """Fail-closed session proof for collapsed Instagram sidebar layouts.

    On another user's profile, Instagram often hides the nav Profile href
    even though the session is signed in. Inspect a separate, read-only tab in
    the SAME persistent Chrome context. Require matching owner header AND an
    Edit profile control; URL, target username, or a stored handle alone never
    prove ownership. Keep the target page (and any menu) untouched.
    """
    if challenge_detected(page):
        return False
    passwords = page.locator('input[name="password"]')
    if any(passwords.nth(i).is_visible() for i in range(min(passwords.count(), 6))):
        return False
    identified = signed_in_handle(page)
    if identified is not None:
        return identified.casefold() == expected_handle.casefold()
    check = None
    try:
        check = page.context.new_page()
        return verify_selected_owner_profile(check, expected_handle) == expected_handle
    except Exception:
        return False
    finally:
        if check is not None:
            try:
                check.close()
            except Exception:
                pass

def _verify_final_state(page, expected_handle, username, *, checks=3):
    """Allow short UI settling but never infer success from a completed click."""
    for _ in range(checks):
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification after the action."
        # The owner UI can transiently disappear during an Instagram rerender.
        # Retry ONLY read-only identity evidence, never the relationship click.
        owner_proven = False
        for owner_attempt in range(3):
            if challenge_detected(page) or page.locator('input[name="password"]').count():
                return "blocked", "Instagram requested verification after the action."
            if _verified_action_owner(page, expected_handle):
                owner_proven = True
                break
            if owner_attempt < 2:
                page.wait_for_timeout(900)
        if not owner_proven:
            return "blocked", "Could not verify the current Instagram session after the action. Review manually; do not repeat the click."
        state = _follow_state(page, username)
        if state == "follow_back":
            return "ok", ("Action confirmed: Follow Back. "
                          "The person still follows you, but you no longer follow them.")
        if state == "follow":
            return "ok", ("Action confirmed: Follow. "
                          "You no longer follow this account; it does not show a followback.")
        page.wait_for_timeout(650)
    return "review", "Final state is ambiguous. Do not repeat this action automatically."



def _verify_unfollow_after_readonly_refresh(page, username, expected_handle):
    """One read-only target refresh may prove a delayed Unfollow completion.

    Never issue a second relationship-changing click and never declare success
    unless the same target now visibly displays Follow / Follow Back.
    """
    prefix = "Final state is ambiguous after a read-only refresh. "
    try:
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification after the action."
        page.goto("https://www.instagram.com/" + username + "/",
                  wait_until="domcontentloaded", timeout=45000)
        result, message = _verify_final_state(page, expected_handle, username, checks=3)
        if result == "ok":
            return result, "Unfollow confirmed after a read-only profile refresh. " + message
        if result == "blocked":
            return result, message + " Unfollow may already have occurred; do not repeat it."
        return "review", prefix + "No verified Follow state appeared. Do not repeat the click."
    except Exception:
        return "review", prefix + "Instagram could not be checked safely. Do not repeat the click."


def _verify_cancel_after_readonly_refresh(page, username, expected_handle):
    """Confirm a clicked pending-request cancellation by *reading*, never clicking.

    Instagram sometimes keeps a stale Requested header immediately after the
    click, even when the server has accepted it. A single fresh profile load
    may reveal Follow / Follow Back; only that is a confirmed cancellation.
    A remaining Requested / Following / unknown state stays a manual review.
    Never make a second relationship-changing click or silently retry.
    """
    prefix = "Pending cancellation unverified after read-only refresh: "
    target = "https://www.instagram.com/" + username + "/"
    try:
        page.goto(target, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(750)
        current = urlparse(page.url)
        if (current.hostname not in ("www.instagram.com", "instagram.com")
                or current.path.strip("/").casefold() != username.casefold()):
            return "review", prefix + "Instagram redirected away from the target; do not repeat the action."
        result, message = _verify_final_state(page, expected_handle, username, checks=2)
        if result == "ok":
            return "ok", ("Cancel Request confirmed after a read-only profile refresh. " + message)
        if result == "blocked":
            return result, message + " Cancellation may already have occurred; do not repeat it."
        if _profile_relationship_control(page, username, [r"Requested", r"Solicitado", r"Solicitada"]):
            return "review", prefix + ("Instagram still displays Requested. "
                                        "Do not repeat; check the profile manually.")
        if _profile_relationship_control(page, username, [r"Following", r"Siguiendo"]):
            return "review", prefix + ("Instagram now displays Following, not a cancelled request. "
                                        "Review the relationship manually.")
        return "review", prefix + "No unambiguous Follow state was visible. Do not repeat the action."
    except Exception as exc:
        return "review", prefix + ("The target could not be checked safely (" +
                                     str(exc)[:100] + "). Do not repeat the action.")


def _preclick_no_action(entry):
    """Recognize a known failed *first* click, never an uncertain outcome.

    Prior versions labeled these misses "nothing clicked" but blocked them
    forever as attempted. Rechecking requires a new owner-approved batch.
    """
    if _preclick_identity_blocked(entry):
        return True
    if not isinstance(entry, dict) or entry.get("status") != "review":
        return False
    message = str(entry.get("message") or "")
    if (entry.get("issue") == "profile_load_timeout"
            and message.startswith(MISSING_RELATIONSHIP_CONTROL + " Waiting timed out:")
            and "No action clicked." in message):
        return True
    return (entry.get("issue") == "missing_profile_info"
            and (message in (LEGACY_MISSING_RELATIONSHIP_CONTROL,
                             MISSING_RELATIONSHIP_CONTROL)
                 or message.startswith(MISSING_RELATIONSHIP_CONTROL + " Profile layout:")))


def _preclick_identity_blocked(entry):
    """Only retry historical failures that explicitly prove no click occurred.

    Unknown 'blocked', errors and review states are never replayed:
    they could represent actions already applied on Instagram.
    """
    if not isinstance(entry, dict) or entry.get("status") != "blocked":
        return False
    message = str(entry.get("message") or "")
    return (
        message.startswith("The active Instagram account cannot be verified. No action was performed.")
        or message == "Instagram session verification failed before the first click. No action performed."
    )

def _action_issue(task, result, message):
    """Stable codes for the owner-facing anomalies report, independent of UI locale."""
    if task == "unfollow" and result == "ok" and ("Action confirmed: Follow Back." in message or "Follow Back / Seguir también" in message):
        return "unexpected_followback"
    if task == "cancel" and result == "review" and message.startswith(("Outdated pending request:", "Pendiente desactualizado:")):
        return "pending_already_following"
    if task == "cancel" and result == "review" and message.startswith(("The request no longer appears", "La solicitud ya no aparece")):
        return "pending_not_requested"
    if task == "cancel" and result == "review" and message.startswith("Pending cancellation unverified after read-only refresh:"):
        return "pending_cancel_unverified"
    if result == "review" and message.startswith(("This account follows you", "El perfil indica que ya te sigue")):
        return "mutual_before_action"
    if (result == "review" and message.startswith(MISSING_RELATIONSHIP_CONTROL)
            and " Waiting timed out:" in message and "No action clicked." in message):
        return "profile_load_timeout"
    if result == "review" and message.startswith(("The profile does not show", "El perfil no muestra")):
        return "missing_profile_info"
    if result in ("review", "error", "blocked"):
        return "requires_manual_review"
    return ""


def perform_visible_action(page, username, task, expected_handle, can_act=None,
                           on_wait=None, *, preloaded=False):
    """Execute real visible public-menu/private-confirmation flows conservatively.

    A public profile commonly needs Following -> menu Unfollow -> Follow.
    Private profiles may additionally ask for confirmation. The robot inspects
    what is actually shown rather than assuming any profile privacy state.
    """
    if task not in TASKS:
        raise ValueError("Unknown action.")
    if on_wait:
        on_wait("loading_profile", 0, 45)
    target_url = "https://www.instagram.com/" + username + "/"
    current_url = urlparse(page.url)
    if (not preloaded
            or current_url.hostname not in ("www.instagram.com", "instagram.com")
            or current_url.path.strip("/").casefold() != username.casefold()):
        page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
    # A prepared target page may still be hydrating; identity/control waits
    # below apply exactly the same checks as ordinary navigation.
    if not _wait_for_target_profile_shell(page, username, on_wait=on_wait,
                                         can_act=can_act):
        if can_act and not can_act(username):
            return "skipped", "Skipped or protected before a relationship click."
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification."
        url = urlparse(page.url)
        if url.hostname not in ("www.instagram.com", "instagram.com") or url.path.strip("/").casefold() != username.casefold():
            return "blocked", "Instagram redirected to another profile."
        main = page.locator("main").first
        if main.count() and main.is_visible() and main.inner_text(timeout=2000).strip():
            return "blocked", ("The target profile heading or exact username could not be verified. "
                               "No action was performed.")
        return "review", (MISSING_RELATIONSHIP_CONTROL +
            " Waiting timed out: profile identity has not loaded after 20 seconds. "
            "No action clicked. Leave this tab open for manual review.")
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "blocked", "Instagram requested verification."
    if not _verified_action_owner(page, expected_handle):
        return "blocked", "The active Instagram account cannot be verified. No action was performed. Open your own profile in Chrome and confirm Edit profile appears."
    url = urlparse(page.url)
    if url.hostname not in ("www.instagram.com", "instagram.com") or url.path.strip("/").lower() != username:
        return "blocked", "Instagram redirected to another profile."
    header = page.locator("header").first
    if not header.count() or not header.is_visible():
        # Some layouts use a role=button directly in the profile's main area
        # without a semantic header. The helper independently requires an
        # exact visible @username heading before permitting any action.
        main = page.locator("main").first
        if not main.count() or not main.is_visible():
            return "blocked", "The target profile area could not be found."
        # Exact visible username may be a span or div, not a heading tag.
        if not _profile_hero_probe(page, username, []).get("target_visible"):
            return "blocked", ("The target profile heading or exact username could not be verified. "
                               "No action was performed.")
    if task == "unfollow" and header.count() and header.is_visible() and re.search(r"\b(follows you|te sigue)\b",
                                          header.inner_text(timeout=4000), re.I):
        return "review", "This account follows you; review required."
    active = (_wait_for_profile_relationship_control(
                  page, username, [r"Following", r"Siguiendo"],
                  on_wait=on_wait, can_act=can_act)
              if task == "unfollow" else
              _wait_for_profile_relationship_control(
                  page, username, [r"Requested", r"Solicitado", r"Solicitada"],
                  on_wait=on_wait, can_act=can_act))
    if active is None:
        if can_act and not can_act(username):
            return "skipped", "Skipped or protected while waiting for profile controls."
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification before the first click."
        if task == "cancel":
            if _profile_relationship_control(page, username, [r"Following", r"Siguiendo"]):
                return "review", ("Outdated pending request: Instagram now shows Following; "
                                  "the follow request was accepted. No relationship was changed.")
            if _follow_state(page, username):
                return "review", ("The request no longer appears as Requested; "
                                  "no change was made.")
        control_name = ("Following/Siguiendo" if task == "unfollow"
                        else "Requested/Solicitado")
        return "review", (MISSING_RELATIONSHIP_CONTROL +
            " Waiting timed out: " + control_name +
            " was not verifiable after 20 seconds. No action clicked. "
            "The tab remains open for manual review; the robot will not silently skip it." +
            _relationship_layout_note(
                page, username, ([r"Following", r"Siguiendo"] if task == "unfollow"
                                 else [r"Requested", r"Solicitado", r"Solicitada"])))
    if can_act and not can_act(username):
        return "skipped", "Skipped or protected before the first click."
    if not _verified_action_owner(page, expected_handle):
        return "blocked", "Instagram session verification failed before the first click. No action performed."
    active.click(timeout=10000)

    if task == "unfollow":
        # The FIRST click only opens a menu on public accounts.
        # Locate the "Unfollow" command in that menu (or a direct dialog).
        choice = _wait_for_unfollow_option(page, username, on_wait=on_wait)
        if choice is None:
            # Rare layouts change directly on the first click. Do not guess.
            return _verify_final_state(page, expected_handle, username)
        if can_act and not can_act(username):
            return "review", "Menu opened, but protection changed. Review before continuing."
        if not _verified_action_owner(page, expected_handle):
            return "review", "Session could not be reverified before the final Unfollow click. Inspect the open menu manually."
        choice.click(timeout=10000)
        # Public: await the final state; private accounts may show a second dialog.
        status, message = _verify_final_state(page, expected_handle, username, checks=2)
        if status in ("ok", "blocked"):
            return status, message
        # Private: Instagram may prompt one more explicit confirmation.
        dialog = _visible_dialog(page)
        if dialog is not None:
            confirm = _visible_named_control(dialog,
                    [r"Unfollow", r"Dejar de seguir", r"Confirm", r"Confirmar"],
                    text_fallback=True)
            if confirm:
                if can_act and not can_act(username):
                    return "review", "Private confirmation pending; protection changed."
                if not _verified_action_owner(page, expected_handle):
                    return "review", "Session changed or could not be confirmed before private Unfollow confirmation."
                confirm.click(timeout=10000)
                return _verify_final_state(page, expected_handle, username)
        return _verify_unfollow_after_readonly_refresh(page, username, expected_handle)

    # Cancel sent follow request: Instagram layouts vary between direct toggles
    # and explicit Cancel Request confirmation.
    dialog = _visible_dialog(page)
    if dialog is not None:
        choice = _request_cancel_confirmation(dialog, username)
        if choice is None:
            return "review", "The dialog does not clearly identify this pending request. No click was performed."
        if can_act and not can_act(username):
            return "review", "Protection changed before canceling the request."
        if not _verified_action_owner(page, expected_handle):
            return "review", "Session could not be reverified before Cancel Request confirmation. No final click was performed."
        choice.click(timeout=10000)
    # A click may have succeeded even if Instagram's client UI has not caught
    # up. A *read-only* fresh profile load may confirm it; never click again.
    result, details = _verify_final_state(page, expected_handle, username)
    if result != "review":
        return result, details
    return _verify_cancel_after_readonly_refresh(page, username, expected_handle)



def classify_followback_search(dialog, username, *, text=None, usernames=None):
    """Fail-closed classification of Instagram's OWN followers search results.

    A missing 'Follows you' tag is not evidence of non-followback.
    Negative requires Instagram explicitly rendering an empty search result.
    """
    own = valid_username(username)
    found = set(usernames if usernames is not None else [])
    if own in found:
        return "follows_you"
    empty = re.search(r"\b(no results found|no results|no users found|no se encontraron resultados|sin resultados|no hay resultados)\b",
                      text if text is not None else dialog.inner_text(timeout=4000), re.I)
    return "not_following" if empty and not found else "unverified"


def perform_visible_followback_audit(page, username, expected_handle):
    """Read-only audit: search a candidate in the signed-in owner's Followers.

    Never click Follow, Following, Requested, Unfollow, or Cancel Request.
    """
    if signed_in_handle(page) != expected_handle:
        return "review", "unverified", "Active Instagram identity could not be confirmed."
    page.goto("https://www.instagram.com/" + expected_handle + "/",
              wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(950)
    if challenge_detected(page) or signed_in_handle(page) != expected_handle:
        return "blocked", "unverified", "Instagram challenge or identity mismatch."
    link = page.locator('a[href*="/followers/"]')
    # Match the owner's exact Followers URL. Never inspect another account.
    target = None
    for i in range(min(link.count(), 15)):
        item = link.nth(i)
        href = item.get_attribute("href") or ""
        if item.is_visible() and re.search(r"/" + re.escape(expected_handle) + r"/followers/?(?:\?|$)", href, re.I):
            target = item
            break
    if target is None:
        return "review", "unverified", "Owner Followers link unavailable; no conclusion."
    target.click(timeout=12000)
    dialog = page.locator('[role="dialog"]').last
    dialog.wait_for(state="visible", timeout=12000)
    # Different layouts label the visible search as Search or Buscar.
    searches = dialog.locator('input[placeholder*="Search"], input[placeholder*="Buscar"], input[aria-label*="Search"], input[aria-label*="Buscar"]')
    if searches.count() != 1 or not searches.first.is_visible():
        return "review", "unverified", "Followers search field unavailable; no conclusion."
    searches.first.fill(username)
    page.wait_for_timeout(1400)
    observations = []
    for _ in range(2):
        if challenge_detected(page) or signed_in_handle(page) != expected_handle:
            return "blocked", "unverified", "Instagram challenge or identity mismatch during audit."
        links = dialog.locator("a[href]").evaluate_all(
            "(els) => els.filter(el => el.getBoundingClientRect().width > 0).map(el => el.getAttribute('href') || '')")
        from profile_counts_instagram import user_from_href
        matches = [u for href in links if (u := user_from_href(href))]
        result = classify_followback_search(dialog, username, usernames=matches)
        observations.append(result)
        page.wait_for_timeout(450)
    if observations == ["follows_you", "follows_you"]:
        return "ok", "follows_you", "Verified: appears in your live Instagram Followers search."
    if observations == ["not_following", "not_following"]:
        return "ok", "not_following", "Verified: Instagram explicitly shows no results for this username in your Followers."
    return "review", "unverified", "Followers search gave incomplete or inconsistent evidence."


def recheck_action_readonly(page, username, task, expected_handle, previous,
                            *, on_wait=None, preloaded=False):
    """Verify the previous automatic action without any relationship-changing click."""
    if task == "audit":
        result, _relation, details = perform_visible_followback_audit(
            page, username, expected_handle)
        return result, details
    if not isinstance(previous, dict) or previous.get("status") not in (
            "ok", "review", "error", "blocked") or _preclick_no_action(previous):
        return "review", ("No completed Instagram action exists for this profile. "
                          "Automatic read-only recheck did not click anything.")
    target = "https://www.instagram.com/" + username + "/"
    current = urlparse(page.url)
    if (not preloaded or current.hostname not in ("www.instagram.com", "instagram.com")
            or current.path.strip("/").casefold() != username.casefold()):
        page.goto(target, wait_until="domcontentloaded", timeout=45000)
    if not _wait_for_target_profile_shell(page, username, on_wait=on_wait):
        return "review", "Profile did not load during automatic read-only recheck."
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "blocked", "Instagram requires verification. No relationship click made."
    result, details = _verify_final_state(page, expected_handle, username, checks=3)
    return result, ("Read-only batch recheck: " + details +
                    " No new relationship-changing click was made.")


class ActionRobot:
    def __init__(self, collector, data_dir: Path, session_dir: Path):
        self.collector, self.data_dir, self.session_dir = collector, data_dir, session_dir
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.worker = None
        self.owner = self.account = self.handle = self.task = ""
        self.targets = []
        self.open_review_tabs = []
        self.current_wait = None
        self.review_only = False
        self.active_batch_id = ""
        self.skipped = set()
        self.max_count = 30
        self.window_minutes = ACTION_WINDOW_MINUTES
        self.min_delay_seconds = 10.0
        self.rest_minutes = 5.0
        self.status, self.message = "idle", "No active actions"
        self.current = ""
        self.wait_until = 0.0

    def _base_for(self, owner, account, task):
        ident = "\0".join((owner, account, task))
        digest = hashlib.sha256(ident.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("instagram-actions-" + digest + ".json")

    def _base(self, task=None):
        return self._base_for(self.owner, self.account, task or self.task)

    def attempted_history(self, data):
        """Read a named owner/account/task journal even on a fresh Windows launch.

        The normal snapshot has no active task until the first job starts.
        A cold-start selection must not assume that means past actions vanished.
        This read never opens Chrome, alters protection, or replays a click.
        """
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        task = str(data.get("task") or "")
        if (not owner or not account or len(owner) > 200 or len(account) > 120
                or task not in TASKS):
            raise ValueError("Select a valid owner, Instagram workspace and action task.")
        with self.lock:
            journal = _read_json(self._base_for(owner, account, task), {})
        attempted = sorted(user for user, record in journal.items()
            if valid_username(user) == user and isinstance(record, dict)
            and record.get("status") in ("ok", "review", "error", "blocked")
            and not _preclick_no_action(record))
        return {"owner": owner, "account": account, "task": task,
                "attempted_usernames": attempted}

    def _review_batches_file_for(self, owner, account, task):
        base = self._base_for(owner, account, task)
        return base.with_name(base.stem + "-batch-reviews.json")

    def _review_batches(self, owner, account, task):
        return _read_json(self._review_batches_file_for(owner, account, task), [])

    def _pending_review(self, owner, account, task):
        batches = self._review_batches(owner, account, task)
        return next((entry for entry in reversed(batches)
                     if not entry.get("approved_at")), None)

    def batch_review(self, data):
        owner, account, task = self._review_scope(data)
        with self.lock:
            entry = self._pending_review(owner, account, task)
            return {"owner": owner, "account": account, "task": task,
                    "batch": dict(entry) if entry else None}

    def _review_scope(self, data):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        task = str(data.get("task") or "").strip()
        if not owner or not account or len(owner) > 200 or len(account) > 120 or task not in TASKS:
            raise ValueError("Choose a valid owner, Instagram account and robot task.")
        return owner, account, task

    def approve_batch(self, data):
        owner, account, task = self._review_scope(data)
        batch_id = str(data.get("batch_id") or "")
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Wait for the robot to finish before approving the batch.")
            entries = self._review_batches(owner, account, task)
            match = next((entry for entry in reversed(entries)
                         if entry.get("id") == batch_id and not entry.get("approved_at")), None)
            if match is None:
                raise ValueError("The pending batch changed. Refresh before confirming.")
            if data.get("confirmation") != "reviewed:" + batch_id:
                raise ValueError("Only your explicit batch confirmation can mark this reviewed.")
            journal = _read_json(self._base_for(owner, account, task), {})
            rechecked = match.get("recheck_results") or {}
            approved = []
            unresolved = []
            for username in match["targets"]:
                result = rechecked.get(username, {}).get("status")
                if result is None:
                    result = journal.get(username, {}).get("status")
                if result == "ok":
                    approved.append(username)
                else:
                    unresolved.append(username)
            match["approved_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            match["approved_usernames"] = approved
            match["unresolved_usernames"] = unresolved
            _atomic_json(self._review_batches_file_for(owner, account, task), entries)
            return {"owner": owner, "account": account, "task": task,
                    "batch_id": batch_id, "approved_usernames": approved,
                    "unresolved_usernames": unresolved, "approved_at": match["approved_at"]}

    def recheck_batch(self, data):
        owner, account, task = self._review_scope(data)
        with self.collector.browser_admission, self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("The Instagram robot is already active.")
            if self.collector.worker and self.collector.worker.is_alive():
                raise ValueError("Pause Profile Counts before rechecking an action batch.")
            entry = self._pending_review(owner, account, task)
            if (not entry or data.get("batch_id") != entry["id"]
                    or data.get("confirmation") != "recheck:" + entry["id"]):
                raise ValueError("Confirm the exact unapproved batch before rechecking.")
            expected = valid_username(data.get("expected_handle"))
            if not expected:
                raise ValueError("Verify the active Instagram handle first.")
            # Never initiate a relationship-changing click during recheck.
            self.owner, self.account, self.handle, self.task = owner, account, expected, task
            self.targets = list(entry["targets"])
            self.active_batch_id = entry["id"]
            self.review_only = True
            self.open_review_tabs = []
            self.current_wait = None
            self.skipped.clear()
            self.max_count, self.window_minutes, self.min_delay_seconds = check_pacing(
                int(data.get("batch_size", 30)), ACTION_WINDOW_MINUTES,
                data.get("gap_seconds", 10))
            rest_input = data.get("rest_minutes", 5)
            _, self.rest_minutes = check_batch_rest(
                self.max_count if rest_input else 0, rest_input)
            self.stop_event.clear()
            self.status, self.message = "starting", "Rechecking unapproved batch in Chrome (read-only)."
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def _save_recheck_result(self, user, result, message):
        entries = self._review_batches(self.owner, self.account, self.task)
        entry = next((x for x in reversed(entries)
                      if x.get("id") == self.active_batch_id and not x.get("approved_at")), None)
        if entry:
            entry.setdefault("recheck_results", {})[user] = {
                "status": result, "message": message,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            _atomic_json(self._review_batches_file_for(self.owner, self.account, self.task), entries)

    def _protection_file(self):
        ident = "\0".join((self.owner, self.account))
        digest = hashlib.sha256(ident.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("action-protected-" + digest + ".json")

    def _protected(self):
        return set(_read_json(self._protection_file(), []))

    def _journal(self):
        return _read_json(self._base(), {})

    def _protected_for(self, username):
        with self.lock:
            return username in self._protected()

    def protect(self, data):
        owner, account = str(data.get("owner") or ""), str(data.get("account") or "")
        # Protection updates apply only to the currently selected authenticated
        # owner/profile; never allow a UI switch to overwrite another scope.
        with self.lock:
            if not self.owner or (owner, account) != (self.owner, self.account):
                raise ValueError("Select the same account to update protected profiles.")
            names = _users(data.get("protected", []))
            protected = self._protected()
            # Additive while running: a concurrent UI update can only protect.
            protected.update(names)
            _atomic_json(self._protection_file(), sorted(protected))
            return self.snapshot()

    def skip(self, data):
        with self.lock:
            if (str(data.get("owner") or ""), str(data.get("account") or "")) != (self.owner, self.account):
                raise ValueError("The action batch belongs to another Instagram account.")
            user = valid_username(data.get("username"))
            if not user or user not in self.targets:
                raise ValueError("This profile is not in the current batch.")
            self.skipped.add(user)
            return self.snapshot()

    def start(self, data, *, resume=False):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        expected = valid_username(data.get("expected_handle"))
        task = str(data.get("task") or "")
        targets = _users(data.get("targets"))
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("Select an Insta Cleaner login and Instagram workspace first.")
        if not expected:
            raise ValueError("Assign the active Instagram @handle before starting.")
        if task not in TASKS or not targets:
            raise ValueError("Select a job containing valid profiles.")
        count = int(data.get("batch_size", 30))
        if count != data.get("batch_size", 30) or not 1 <= count <= 1000:
            raise ValueError("The batch size must be between 1 and 1,000.")
        max_count, window, delay = check_pacing(count, ACTION_WINDOW_MINUTES,
                                                 data.get("gap_seconds", 10))
        rest_input = data.get("rest_minutes", 5)
        every, rest = check_batch_rest(count if rest_input else 0, rest_input)
        if data.get("confirmation") != task + ":" + str(len(targets)):
            raise ValueError("The batch was not explicitly approved.")
        if task == "unfollow" and data.get("followers_evidence") is not True:
            raise ValueError("A complete Followers list has not been verified.")
        with self.collector.browser_admission, self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("An Instagram action robot is already running.")
            if self.collector.worker and self.collector.worker.is_alive():
                raise ValueError("Finish or pause Profile Counts before starting an action robot.")
            if resume and (owner, account, task) != (self.owner, self.account, self.task):
                raise ValueError("Cannot resume a different task or account.")
            if resume and self.status not in ("paused", "error", "review", "blocked"):
                raise ValueError("There is no paused task to resume.")
            self.owner, self.account, self.handle, self.task = owner, account, expected, task
            if not resume:
                if self._pending_review(owner, account, task):
                    raise ValueError("This batch has not been marked Reviewed. Recheck the existing batch automatically or approve it first.")
                previous = self._journal()
                if all((record := previous.get(user, {})).get("status") in ("ok", "review", "error", "blocked")
                       and not _preclick_no_action(record) for user in targets):
                    raise ValueError("Every selected profile was already attempted in this task. Choose a fresh batch or review uncertain results; the robot will not repeat actions.")
            self.targets = targets
            self.review_only = False
            if not resume:
                entries = self._review_batches(owner, account, task)
                batch_id = hashlib.sha256((str(time.time_ns()) + "\\0" +
                                          owner + "\\0" + account + "\\0" + task).encode()).hexdigest()[:24]
                entries.append({"id": batch_id, "targets": list(targets),
                                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                "approved_at": None, "recheck_results": {}})
                _atomic_json(self._review_batches_file_for(owner, account, task), entries)
                self.active_batch_id = batch_id
            self.open_review_tabs = []
            self.current_wait = None
            if not resume:
                self.skipped.clear()
            self.max_count, self.window_minutes, self.min_delay_seconds = max_count, window, delay
            self.rest_minutes = rest
            # A newly authorized batch uses the owner's current visible
            # favorites. During an active run protection may only be added.
            saved_protected = set(_users(data.get("protected", [])))
            if resume:
                saved_protected.update(self._protected())
            _atomic_json(self._protection_file(), sorted(saved_protected))
            self.stop_event.clear()
            self.status, self.message = "starting", "Opening Instagram in Chrome…"
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def pause(self, data):
        with self.lock:
            if (str(data.get("owner") or ""), str(data.get("account") or "")) != (self.owner, self.account):
                raise ValueError("The task belongs to another Instagram account.")
            if self.worker and self.worker.is_alive():
                self.status, self.message = "pausing", "Pausing after the current visit…"
                self.stop_event.set()
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            journal = self._journal() if self.owner and self.task else {}
            rows = {u: journal.get(u, {}) for u in self.targets}
            # Persisted action journal spans ALL earlier batches, not merely
            # the latest 30 selected targets. Send usernames only, no secrets.
            attempted_usernames = sorted(u for u, record in journal.items()
                if isinstance(record, dict)
                and record.get("status") in ("ok", "review", "error", "blocked")
                and not _preclick_no_action(record))
            protected = self._protected() if self.owner else set()
            successful = sum(x.get("status") == "ok" for x in rows.values())
            reviewed = sum(x.get("status") in ("review", "error", "blocked") for x in rows.values())
            issues = [{"username": u, "status": rows[u].get("status", "pending"),
                       "issue": rows[u].get("issue", ""),
                       "message": rows[u].get("message", ""),
                       "at": rows[u].get("at", "")}
                      for u in self.targets if rows[u].get("issue")]
            ignored = sum(u in protected for u in self.targets)
            skipped = sum(u in self.skipped for u in self.targets)
            completed_states = ("ok", "review", "error", "blocked")
            processed = sum(rows[u].get("status") in completed_states
                            or u in protected or u in self.skipped for u in self.targets)
            pending = sum(u not in protected and u not in self.skipped and
                          rows[u].get("status") not in completed_states
                          for u in self.targets)
            return {"status": self.status, "message": self.message,
                    "owner": self.owner, "account": self.account, "task": self.task,
                    "current_profile": self.current,
                    "running": bool(self.worker and self.worker.is_alive()),
                    "total": len(self.targets), "processed": processed,
                    "pending": pending, "successful": successful,
                    "errors": reviewed, "protected": ignored, "skipped": skipped,
                    "issue_count": len(issues), "issues": issues,
                    "attempted_usernames": attempted_usernames,
                    "remaining": pending,
                    "wait_seconds": max(0, int(self.wait_until-time.time()+0.999)) if self.wait_until else 0,
                    "open_review_tabs": list(self.open_review_tabs),
                    "current_wait": dict(self.current_wait) if self.current_wait else None,
                    "max_action_tabs": MAX_ACTION_TABS,
                    "review_only": self.review_only,
                    "review_batch": dict(self._pending_review(self.owner, self.account, self.task))
                        if self.owner and self.account and self.task else None,
                    "rows": [{"username": u, "status": rows[u].get("status", "pending"),
                              "audit_relation": rows[u].get("audit_relation", ""),
                              "issue": rows[u].get("issue", ""),
                              "message": rows[u].get("message", ""),
                              "at": rows[u].get("at", "")} for u in self.targets]}

    def _record_readiness(self, username, phase, elapsed, limit, action_tabs):
        """Make active Instagram loading/Following waits visible in Automations."""
        phrases = {
            "loading_profile": "Instagram profile page is still loading",
            "waiting_relationship_control": "Waiting for Following/Requested control",
            "waiting_unfollow_menu": "Waiting for Unfollow menu",
        }
        with self.lock:
            self.status = "waiting"
            self.current_wait = {
                "username": username, "phase": phase,
                "elapsed_seconds": elapsed, "timeout_seconds": limit,
            }
            self.message = ("@" + username + ": " + phrases.get(phase, "Waiting for Instagram") +
                            " (" + str(elapsed) + "/" + str(limit) + " s)")
            if action_tabs and username in action_tabs.tabs:
                action_tabs.tabs[username]["status"] = phase
                self.open_review_tabs = action_tabs.overview()

    def _run(self):
        browser = None
        try:
            from playwright.sync_api import sync_playwright
            self.session_dir.mkdir(parents=True, exist_ok=True)
            with sync_playwright() as pw:
                options = {"user_data_dir": str(self.session_dir), "headless": False,
                           "viewport": {"width": 1180, "height": 860}}
                if getattr(sys, "frozen", False):
                    browser = pw.chromium.launch_persistent_context(channel="chrome", **options)
                else:
                    try:
                        browser = pw.chromium.launch_persistent_context(**options)
                    except Exception:
                        browser = pw.chromium.launch_persistent_context(channel="chrome", **options)
                # Never overwrite a restored human login/CAPTCHA page with
                # an automatic Home navigation when opening persistent Chrome.
                open_pages = [p for p in browser.pages if not p.is_closed()]
                page = next((p for p in open_pages if preserve_instagram_auth_page(p)),
                            open_pages[0] if open_pages else browser.new_page())
                if not preserve_instagram_auth_page(page):
                    page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
                with self.lock:
                    self.status, self.message = "login", "Sign in to Chrome as @" + self.handle
                while not self.stop_event.is_set():
                    if any(challenge_detected(tab) for tab in browser.pages if not tab.is_closed()):
                        with self.lock:
                            self.status, self.message = (
                                "blocked",
                                "Instagram requested a reCAPTCHA or account security check. "
                                "The robot stopped before performing actions. Complete account "
                                "verification manually; no automatic challenge retries are allowed."
                            )
                        return
                    signed = signed_in_handle(page)
                    if signed:
                        if signed != self.handle:
                            with self.lock:
                                self.status, self.message = "blocked", "Chrome is signed in as @" + signed + "; expected @" + self.handle
                            return
                        break
                    self.stop_event.wait(3)
                if self.stop_event.is_set():
                    with self.lock: self.status = "paused"
                    return
                journal = self._journal()
                path = self._base()
                visits_file, rests_file = history_path(path), batch_path(path)
                visits = load_history(visits_file)
                rests = load_batch_state(rests_file)
                action_tabs = ActionTabPool(browser) if self.task != "audit" else None
                stopped_for_review = False
                if action_tabs:
                    # Prepare a genuine ten-profile window *before* attempting
                    # any relationship-changing clicks. All navigation still
                    # honors the owner's per-visit cadence and mandatory rests.
                    stage_names = []
                    for candidate in self.targets:
                        previous = journal.get(candidate, {})
                        if (self._protected_for(candidate) or candidate in self.skipped
                                or (not self.review_only and
                                    previous.get("status") in ("ok", "review", "error", "blocked")
                                    and not _preclick_no_action(previous))):
                            continue
                        if len(stage_names) >= MAX_ACTION_TABS:
                            break
                        if action_tabs.open(candidate) is None:
                            break
                        action_tabs.tabs[candidate]["status"] = "queued"
                        stage_names.append(candidate)
                    with self.lock:
                        self.open_review_tabs = action_tabs.overview()
                        self.message = ("Preparing " + str(len(stage_names)) +
                                        " Instagram profile tabs with saved visit spacing.")
                    for warm_user in stage_names:
                        if self.stop_event.is_set():
                            break
                        while not self.stop_event.is_set():
                            delay = max(
                                wait_required(visits, self.max_count, self.window_minutes,
                                              self.min_delay_seconds),
                                batch_wait(rests,
                                           self.max_count if self.rest_minutes > 0 else 0,
                                           self.rest_minutes))
                            if delay <= 0:
                                break
                            with self.lock:
                                self.status = "waiting"
                                self.wait_until = time.time() + delay
                                self.message = ("Preparing ten tabs: waiting " +
                                                str(int(delay+0.999)) +
                                                " s before opening @" + warm_user)
                            self.stop_event.wait(min(delay, 2.0))
                        if self.stop_event.is_set():
                            break
                        with self.lock:
                            self.wait_until = 0
                            self.status = "waiting"
                            self.message = "Preparing @" + warm_user + " in Chrome"
                        tab = action_tabs.tabs[warm_user]
                        tab["status"] = "loading_profile"
                        visits = register_visit(visits_file, visits)
                        started = visits[-1]
                        tab["visit_started_at"] = started
                        try:
                            tab["page"].goto(
                                "https://www.instagram.com/" + warm_user + "/",
                                wait_until="commit", timeout=30000)
                            tab["status"] = "prefetched"
                        except Exception:
                            # This was a read-only navigation: no action click.
                            # Retain the tab and record a safe diagnostic later.
                            tab["status"] = "prefetch_pending"
                        finally:
                            visits = finish_visit(visits_file, visits,
                                                  started_at=started)
                            rests = finish_batch_visit(
                                rests_file, rests,
                                self.max_count if self.rest_minutes > 0 else 0,
                                self.rest_minutes)
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                        if (not tab["page"].is_closed()
                                and (challenge_detected(tab["page"]) or
                                     tab["page"].locator('input[name="password"]').count())):
                            with self.lock:
                                self.status = "blocked"
                                self.message = ("Instagram requested sign-in or a security "
                                                "check during read-only tab preparation. "
                                                "No relationship-changing click was made.")
                            stopped_for_review = True
                            break
                for target_index, user in enumerate(
                        [] if stopped_for_review else self.targets):
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progress saved; select Resume."
                        return
                    # Safe pre-click login failures are retryable after a user
                    # explicitly starts another batch. Never replay ambiguous
                    # or potentially clicked results automatically.
                    previous = journal.get(user, {})
                    if not self.review_only and _preclick_no_action(previous):
                        journal.pop(user, None)
                        _atomic_json(path, journal)
                        previous = {}
                    if (self._protected_for(user) or user in self.skipped or
                        (not self.review_only and
                         previous.get("status") in ("ok", "review", "error", "blocked"))):
                        continue
                    # Already-prefetched target tabs have paid for their
                    # visit in the persistent ledger. Do not wait/charge again.
                    existing_tab = action_tabs.prepared(user) if action_tabs else None
                    if existing_tab is None:
                        while not self.stop_event.is_set():
                            delay = max(wait_required(visits, self.max_count,
                                                      self.window_minutes,
                                                      self.min_delay_seconds),
                                        batch_wait(rests,
                                                   self.max_count if self.rest_minutes > 0 else 0,
                                                   self.rest_minutes))
                            if delay <= 0: break
                            with self.lock:
                                self.status, self.wait_until = "waiting", time.time() + delay
                                self.message = "Scheduled cooldown: " + str(int(delay+0.999)) + " s"
                            self.stop_event.wait(min(delay, 2.0))
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progress saved; select Resume."
                        return
                    with self.lock:
                        self.wait_until = 0
                        self.current = user
                        self.status, self.message = "running", "Checking @" + user
                    if self._protected_for(user) or user in self.skipped:
                        continue
                    work_page = page
                    prepared_item = None
                    if action_tabs:
                        work_page = action_tabs.prepared(user)
                        if work_page is not None:
                            prepared_item = action_tabs.tabs[user]
                        else:
                            work_page = action_tabs.open(user)
                        if work_page is None:
                            with self.lock:
                                self.status = "review"
                                self.message = ("Ten Instagram tabs need manual review. "
                                                "No additional relationship action was attempted.")
                            stopped_for_review = True
                            break
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                    if prepared_item and prepared_item.get("visit_started_at") is not None:
                        current_visit_started = prepared_item["visit_started_at"]
                    else:
                        visits = register_visit(visits_file, visits)
                        current_visit_started = visits[-1]

                    # A single next profile may load read-only in another tab
                    # while the current profile is resolving its controls.
                    # Never prefetch through Instagram faster than the owner's
                    # configured visit pacing or across a mandatory batch rest.
                    next_user = None
                    for candidate in ([] if self.review_only else
                                      self.targets[target_index + 1:]):
                        prior = journal.get(candidate, {})
                        if (not self._protected_for(candidate)
                                and candidate not in self.skipped
                                and (not action_tabs or
                                     action_tabs.prepared(candidate) is None)
                                and (prior.get("status") not in ("ok", "review", "error", "blocked")
                                     or _preclick_no_action(prior))):
                            next_user = candidate
                            break
                    prefetch_attempted = False

                    def paced_prefetch(phase):
                        nonlocal visits, prefetch_attempted
                        if (not action_tabs or not next_user or prefetch_attempted
                                or phase not in ("waiting_relationship_control",
                                                 "waiting_unfollow_menu")
                                or self.stop_event.is_set()
                                or self._protected_for(next_user)
                                or next_user in self.skipped):
                            return
                        if (self.rest_minutes > 0
                                and int(rests.get("count", 0)) + 1 >= self.max_count):
                            return  # Do not prefetch across a mandatory batch rest.
                        if (wait_required(visits, self.max_count, self.window_minutes,
                                          self.min_delay_seconds) > 0
                                or batch_wait(rests,
                                              self.max_count if self.rest_minutes > 0 else 0,
                                              self.rest_minutes) > 0):
                            return
                        if action_tabs.prepared(next_user) is not None:
                            return
                        prepared_page = action_tabs.open(next_user)
                        if prepared_page is None:
                            return  # Ten review tabs already occupy all slots.
                        prefetch_attempted = True
                        # Journal a visit BEFORE any navigation, even if Chrome
                        # crashes or the read-only preload raises an exception.
                        visits = register_visit(visits_file, visits)
                        action_tabs.tabs[next_user]["visit_started_at"] = visits[-1]
                        action_tabs.tabs[next_user]["status"] = "prefetching"
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                        try:
                            prepared_page.goto(
                                "https://www.instagram.com/" + next_user + "/",
                                wait_until="commit", timeout=12000)
                            action_tabs.tabs[next_user]["status"] = "prefetched"
                        except Exception:
                            # Read-only preparation failed. The target stays in
                            # its tab; normal readiness checks decide the result
                            # without silently skipping or issuing any click.
                            action_tabs.tabs[next_user]["status"] = "prefetch_pending"
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()

                    relation = ""
                    try:
                        if self.review_only:
                            relation = ""
                            result, details = recheck_action_readonly(
                                work_page, user, self.task, self.handle, previous,
                                on_wait=lambda phase, elapsed, limit:
                                    self._record_readiness(user, phase, elapsed, limit,
                                                           action_tabs),
                                preloaded=bool(prepared_item and
                                               prepared_item.get("status") == "prefetched"))
                        elif self.task == "audit":
                            result, relation, details = perform_visible_followback_audit(
                                work_page, user, self.handle)
                        elif prepared_item and prepared_item.get("status") == "prefetch_pending":
                            relation = ""
                            result = "review"
                            details = (MISSING_RELATIONSHIP_CONTROL +
                                       " Waiting timed out: read-only tab preparation failed. "
                                       "No action clicked. Inspect the open profile tab.")
                        else:
                            relation = ""
                            result, details = perform_visible_action(
                                work_page, user, self.task, self.handle,
                                lambda name: not self.stop_event.is_set() and
                                not self._protected_for(name) and name not in self.skipped,
                                on_wait=lambda phase, elapsed, limit: (
                                    self._record_readiness(user, phase, elapsed, limit,
                                                           action_tabs),
                                    paced_prefetch(phase)),
                                preloaded=bool(prepared_item and
                                               prepared_item.get("status") == "prefetched"))
                    except Exception as exc:
                        result, details = "error", "The action could not be verified: " + str(exc)[:200]
                    finally:
                        if not (prepared_item and
                                prepared_item.get("visit_started_at") is not None):
                            visits = finish_visit(
                                visits_file, visits, started_at=current_visit_started)
                            rests = finish_batch_visit(
                                rests_file, rests,
                                self.max_count if self.rest_minutes > 0 else 0,
                                self.rest_minutes)
                    with self.lock:
                        self.current_wait = None
                    # Persist the result BEFORE closing any confirmed tab.
                    # A browser close failure must never erase a clicked action
                    # from the account-scoped no-replay journal.
                    issue = _action_issue(self.task, result, details) if result != "skipped" else ""
                    if self.review_only:
                        self._save_recheck_result(user, result, details)
                    elif result != "skipped":
                        journal[user] = {"status": result, "message": details,
                                         "audit_relation": relation,
                                         "issue": issue,
                                         "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                        _atomic_json(path, journal)
                    if action_tabs:
                        try:
                            action_tabs.record(user, result)
                        except Exception:
                            # No relationship click is ever repeated to recover
                            # from a tab closing problem.
                            pass
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                    if result == "skipped":
                        continue
                    if result != "ok":
                        if self.review_only:
                            # Read-only automatic review should check the rest
                            # of the batch, not demand one-by-one manual work.
                            continue
                        # No-click preflight anomalies can be reviewed together after
                        # the batch. Potentially clicked/ambiguous results still stop.
                        if self.task == "audit" and result == "review":
                            continue
                        if issue in ("pending_already_following", "pending_not_requested",
                                     "mutual_before_action", "missing_profile_info"):
                            continue
                        with self.lock:
                            self.status, self.message = result, "@" + user + ": " + details
                        stopped_for_review = True
                        break
                with self.lock:
                    rechecked = (self._pending_review(self.owner, self.account, self.task)
                                 or {}).get("recheck_results", {}) if self.review_only else {}
                    remaining = sum(u not in self._protected() and u not in self.skipped and
                                    (rechecked.get(u, {}).get("status") if self.review_only
                                     else journal.get(u, {}).get("status")) != "ok"
                                    for u in self.targets)
                    if not stopped_for_review:
                        self.status = "partial" if remaining else "complete"
                        self.message = ("Batch reviewed: some profiles require manual verification."
                                        if remaining else "Batch complete; results saved.")
                # Unverified target tabs must remain visible for manual inspection.
                # The Playwright persistent context is deliberately held open
                # until the owner manually pauses or closes the target tabs.
                if action_tabs and action_tabs.has_open_tabs():
                    with self.lock:
                        self.status = "review"
                        self.open_review_tabs = action_tabs.overview()
                        self.message = (
                            "Unverified Instagram tabs remain open for manual review. "
                            "Inspect them before selecting Pause; Pause closes Chrome. "
                            "No relationship click will be repeated.")
                    while not self.stop_event.is_set() and action_tabs.has_open_tabs():
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                        self.stop_event.wait(1)
                    if self.stop_event.is_set():
                        with self.lock:
                            self.status = "paused"
                            self.message = ("Robot paused by owner. Unverified history was "
                                            "preserved; no automatic click will be retried.")
                    else:
                        with self.lock:
                            self.open_review_tabs = []
        except Exception as exc:
            with self.lock:
                self.status, self.message = "error", "Robot stopped: " + str(exc)[:220]
        finally:
            with self.lock:
                self.current, self.wait_until, self.current_wait = "", 0, None
            if browser:
                try: browser.close()
                except Exception: pass
            with self.lock:
                self.open_review_tabs = []
