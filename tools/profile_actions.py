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
import shutil
import subprocess
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
# Explicit independent hourly safety budget. Owner batch size is NEVER a 60m
# throttle; batch breaks and visit history remain separate and persistent.
ACTION_PROFILE_VISITS_PER_HOUR = 120
MAX_ACTIONS_PER_JOB = 1000

def action_wait_detail(visits, rests, *, batch_size, rest_minutes,
                       gap_seconds, now=None):
    """Attribute waits to one of three independent, persisted pacing clocks."""
    now = time.time() if now is None else now
    hourly = wait_required(visits, ACTION_PROFILE_VISITS_PER_HOUR,
                           ACTION_WINDOW_MINUTES, 0, now=now)
    spacing = max(0.0, max(visits, default=-1e30) + gap_seconds - now)
    rest = batch_wait(rests, batch_size if rest_minutes > 0 else 0,
                      rest_minutes, now=now)
    choices = [
        (hourly, "Hourly visit safety limit: " +
         str(ACTION_PROFILE_VISITS_PER_HOUR) + " visits per " +
         str(ACTION_WINDOW_MINUTES) + " minutes"),
        (rest, "Between-batch rest: " + str(rest_minutes) +
         " min after " + str(batch_size) + " profiles"),
        (spacing, "Between-profile spacing: " + str(gap_seconds) + " s"),
    ]
    delay, reason = max(choices, key=lambda item: item[0])
    return max(0.0, delay), (reason if delay > 0 else "")


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


def _assert_unchanged_action_journal(path, snapshot):
    """Reject local journal changes since the worker's last verified snapshot.

    The OS process lease serializes InstaCleaner robots, but another program,
    restore, or manual edit could still modify the file between actions.
    Never overwrite that evidence with a stale in-memory target journal.
    This is a best-effort drift guard, not a cross-process filesystem CAS.
    """
    if not isinstance(snapshot, dict) or _read_json(path, {}) != snapshot:
        raise ValueError(
            "Saved action journal changed on disk. No relationship click or "
            "result overwrite is permitted; inspect the original history.")

MAX_ACTION_TABS = 10
ACTION_CONTROL_WAIT_MS = 20000
# A disconnected/unverified Instagram session must not leave Run stuck forever
# in an apparently active state. Owner can restart after signing in manually.
PUBLIC_ROBOT_LOGIN_WAIT_SECONDS = 240

# Only the current robot worker may report how often it navigates to the
# signed-in owner's own profile. It never includes cookies or account data.
_OWNER_PROFILE_PROBE = threading.local()

def _same_instagram_owner(observed, expected):
    """Exact Instagram handle, case-insensitive; never accept missing identity."""
    return (isinstance(observed, str) and isinstance(expected, str)
            and bool(observed) and bool(expected)
            and observed.casefold() == expected.casefold())


def _find_verified_owner_tab(pages, expected_handle):
    """Observe all Instagram tabs in the SAME robot Chrome; never click.

    The login page we opened can remain stale while the owner signs in on a
    second tab. A verified owner tab is usable only when NO visible tab proves
    a different owner; conflicting identities fail closed instead of guessing.
    A tab URL alone is not identity evidence.
    """
    own_page = None
    mismatch = None
    for candidate in pages:
        try:
            if candidate.is_closed():
                continue
            address = getattr(candidate, "url", "")
            if not isinstance(address, str):
                continue
            parsed = urlparse(address)
            if parsed.scheme != "https" or parsed.hostname not in (
                    "instagram.com", "www.instagram.com"):
                continue
            observed = signed_in_handle(candidate)
            if observed:
                if not _same_instagram_owner(observed, expected_handle):
                    mismatch = observed
                elif own_page is None:
                    own_page = candidate
        except Exception:
            # A tab that cannot be inspected provides no positive auth proof.
            continue
    if mismatch:
        return None, mismatch
    return own_page, None


# Guard against temporary Follow before delayed Requested during hydration.
CANCEL_NO_REQUEST_MIN_WAIT_MS = 5000



def action_tab_stage_limit(tab_flow):
    """Stage a single target by default; preserve optional ten-tab mode.

    By processing A before loading B, sequential mode avoids the automatic
    foreground jump from A -> B -> ... -> A.
    """
    if tab_flow == "sequential":
        return 1
    if tab_flow == "ten_tabs":
        return MAX_ACTION_TABS
    raise ValueError("Choose sequential navigation or ten-tab preparation.")


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

    def record(self, username, status, *, safe_no_click=False):
        item = self.tabs.get(username)
        if item is None:
            return
        if status in ("ok", "skipped", "already_not_following", "already_not_requested") or safe_no_click:
            # Verified outcomes, explicit skips and known pre-click failures
            # close safely; uncertain post-click results retain visible tabs.
            # An ambiguous action, including post-click session loss, cannot.
            if not item["page"].is_closed():
                item["page"].close()
            self.tabs.pop(username, None)
        else:
            item["status"] = status

    def close_unacted_prefetches(self):
        """Release staged no-click tabs after the worker exhausts its cohort.

        Never close a page whose action result is ambiguous. Prefetch means
        navigation only, not a relationship click or a completed review.
        """
        no_action = {"queued", "prefetching", "prefetched",
                     "prefetch_pending", "loading_profile"}
        for username, item in list(self.tabs.items()):
            if item["status"] not in no_action:
                continue
            try:
                if not item["page"].is_closed():
                    item["page"].close()
            except Exception:
                pass
            self.tabs.pop(username, None)

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


def _exact_https_target_profile(page, username):
    """Require the exact target URL on HTTPS before any relationship control."""
    current = urlparse(page.url)
    return (current.scheme == "https"
            and current.hostname in ("www.instagram.com", "instagram.com")
            and current.path.strip("/").casefold() == username.casefold())


def _header_target_identity_visible(page, username):
    """Proof tied specifically to the header that owns its relationship button."""
    try:
        header = page.locator("header").first
        if not header.count() or not header.is_visible():
            return False
        exact = re.compile(r"^\s*@?" + re.escape(username) + r"\s*$", re.I)
        matches = header.get_by_text(exact, exact=True)
        return any(matches.nth(i).is_visible()
                   for i in range(min(matches.count(), 10)))
    except Exception:
        return False


def _target_identity_visible(page, username):
    """Fail closed on conflicting or unproven actionable profile headers.

    Instagram can retain a stale semantic header while the main hero already
    renders a new target. A correct main hero must NEVER authenticate a click
    belonging to a still-visible other/unidentified header. Main-only
    layouts may instead prove their exact hero without a visible header.
    """
    if not _exact_https_target_profile(page, username):
        return False
    try:
        header = page.locator("header").first
        if header.count() and header.is_visible():
            return _header_target_identity_visible(page, username)
    except Exception:
        return False
    return bool(_profile_hero_probe(page, username, []).get("target_visible"))


def _profile_relationship_control(page, username, words):
    """Find one visible action in the verified target's profile hero.

    The <header>-only/semantic-heading-only selector in v120.49 missed real
    Following buttons. Instagram can render its heading in <span> and controls
    in nested divs. A read-only survey checks exact profile username plus
    action location. Never click a Following count or another user's control.
    """
    if not _exact_https_target_profile(page, username):
        return None
    labels = [r"(?:%s)(?:\s*[▾▼⌄])?" % word for word in words]
    header = page.locator("header").first
    if header.count() and header.is_visible() and _header_target_identity_visible(page, username):
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
                                           on_wait=None, can_act=None,
                                           detect_already_not_following=False,
                                           detect_already_not_requested=False):
    """Wait for the real target to finish rendering; never infer no-follow from loading."""
    timeout_ms = ACTION_CONTROL_WAIT_MS if timeout_ms is None else timeout_ms
    started_at = time.monotonic()
    deadline = started_at + timeout_ms / 1000.0
    nonfollow_seen = 0
    nonrequest_seen = 0
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
        if detect_already_not_following:
            # Uniquely scoped Follow / Follow Back in this target's hero is
            # positive evidence of no current follow. Require consecutive
            # observations so loading/transient page states cannot count.
            nonfollow_seen = nonfollow_seen + 1 if _follow_state(page, username) else 0
            if nonfollow_seen >= 3:
                return "already_not_following"
        if detect_already_not_requested:
            # Requested takes precedence; a target-scoped Follow must be stable
            # for multiple reads and past the hydration period before no-request.
            nonrequest_seen = nonrequest_seen + 1 if _follow_state(page, username) else 0
            if (nonrequest_seen >= 3 and
                    (time.monotonic() - started_at) * 1000 >= CANCEL_NO_REQUEST_MIN_WAIT_MS):
                return "already_not_requested"
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
    """Read only this exact target's Follow state, never a sidebar/suggestion."""
    # A Follow button alone is NOT enough to skip an account. The correct URL,
    # signed-in owner (caller) AND an exact visible target username in the
    # profile header or main hero are required.
    if not _profile_hero_probe(page, username, []).get("target_visible"):
        try:
            header = page.locator("header").first
            if not header.count() or not header.is_visible():
                return None
            exact = re.compile(r"^\s*@?" + re.escape(username) + r"\s*$", re.I)
            matches = header.get_by_text(exact, exact=True)
            if not any(matches.nth(i).is_visible()
                       for i in range(min(matches.count(), 10))):
                return None
        except Exception:
            return None
    if _profile_relationship_control(page, username, [r"Follow Back", r"Seguir también"]):
        return "follow_back"
    if _profile_relationship_control(page, username, [r"Follow", r"Seguir"]):
        return "follow"
    return None



def _stable_no_requested_state(page, username):
    """Check exact-target Follow/Follow Back thrice, never click or trust a sidebar."""
    for attempt in range(3):
        current = urlparse(page.url)
        if (current.hostname not in ("www.instagram.com", "instagram.com")
                or current.path.strip("/").casefold() != username.casefold()
                or challenge_detected(page)
                or page.locator('input[name="password"]').count()
                or _profile_relationship_control(
                    page, username, [r"Requested", r"Solicitado", r"Solicitada"])
                or not _follow_state(page, username)):
            return False
        if attempt < 2:
            page.wait_for_timeout(450)
    return True


# A positive signed-in owner proof can be used briefly for the SAME Chrome
# context, but only while its authenticated ds_user_id cookie stays unchanged.
# An unverified/absent cookie never authorizes reuse. Keep only in robot-thread
# memory; never log, serialize, include in a snapshot or persist this value.
OWNER_PROOF_REUSE_SECONDS = 180.0


def _local_owner_session_id(context):
    """Read only the numeric Instagram session identity in current Chrome."""
    try:
        cookies = context.cookies(["https://www.instagram.com/"])
        if not isinstance(cookies, list):
            return None
        values = {item.get("value") for item in cookies
                  if isinstance(item, dict) and item.get("name") == "ds_user_id"}
        if (len(values) != 1 or
                not all(isinstance(value, str) and
                        re.fullmatch(r"[0-9]{1,24}", value) for value in values)):
            return None
        return next(iter(values))
    except Exception:
        return None


def _verified_action_owner(page, expected_handle):
    """Prove the signed-in owner without repeatedly reopening /owner/.

    Prefer the target's *live* visible owner identity. If Instagram hides that
    navigation, accept a recently proved owner profile ONLY while the same
    persistent Chrome context retains the exact bound authenticated user ID.
    Check this cookie afresh for EACH action and final-state verification; a
    different/missing value, expired proof, challenged page, or visibly wrong
    owner revokes reuse. Then re-open a read-only owner proof tab, fail closed
    on any ambiguity and never carry the proof between Chrome jobs.

    The selected username or profile URL alone never authenticates ownership.
    """
    if challenge_detected(page):
        _OWNER_PROFILE_PROBE.bound_session = None
        return False
    passwords = page.locator('input[name="password"]')
    if any(passwords.nth(i).is_visible() for i in range(min(passwords.count(), 6))):
        _OWNER_PROFILE_PROBE.bound_session = None
        return False
    current = urlparse(getattr(page, "url", ""))
    if current.scheme != "https" or current.hostname not in (
            "www.instagram.com", "instagram.com"):
        _OWNER_PROFILE_PROBE.bound_session = None
        return False
    identified = signed_in_handle(page)
    if identified is not None:
        if not _same_instagram_owner(identified, expected_handle):
            _OWNER_PROFILE_PROBE.bound_session = None
            return False
        # A visible owner is a fresh proof in its own right; the fallback
        # cache requires independent matching owner-profile evidence.
        return True

    context = page.context
    session_id = _local_owner_session_id(context)
    bound = getattr(_OWNER_PROFILE_PROBE, "bound_session", None)
    if bound is not None:
        if (session_id and bound["context"] is context
                and _same_instagram_owner(bound["handle"], expected_handle)
                and bound["session_id"] == session_id
                and 0 <= time.monotonic() - bound["verified_at"] <
                OWNER_PROOF_REUSE_SECONDS):
            # Fresh browser-cookie evidence with previous own-profile + Edit
            # profile proof, never a mere remembered username.
            return True
        _OWNER_PROFILE_PROBE.bound_session = None

    check = None
    try:
        check = context.new_page()
        verified = verify_selected_owner_profile(
            check, expected_handle,
            on_navigation=getattr(_OWNER_PROFILE_PROBE, "report", None))
        if not _same_instagram_owner(verified, expected_handle):
            return False
        # Never succeed on a stale proof if the Chrome owner session switched
        # WHILE Instagram loaded its own profile. Without a cookie, preserve
        # the original live owner-profile proof but do not cache it.
        session_after = _local_owner_session_id(context)
        if session_id is not None and session_after != session_id:
            return False
        if session_id and session_after == session_id:
            _OWNER_PROFILE_PROBE.bound_session = {
                "context": context,
                "handle": expected_handle,
                "session_id": session_id,
                "verified_at": time.monotonic(),
            }
        return True
    except Exception:
        return False
    finally:
        if check is not None:
            try:
                check.close()
            except Exception:
                pass


def _verify_final_state(page, expected_handle, username, *, checks=3):
    """Wait for exact target state with TWO owner proofs, not one per poll.

    A missing Instagram sidebar previously caused five or more read-only
    /owner/ navigations while the target's Follow control hydrated. Establish
    an owner proof before polling, check any newly visible account identity and
    login/challenge at EACH poll, and require a fresh owner proof immediately
    before reporting success. No relationship-changing click occurs here.

    Never retain identity across jobs, targets, profile reload boundaries or
    actual irreversible clicks. A changed owner at either proof fails closed.
    """
    owner_proven = False
    for owner_attempt in range(3):
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification after the action."
        observed = signed_in_handle(page)
        if observed is not None and not _same_instagram_owner(observed, expected_handle):
            return "blocked", "Current Instagram account changed during verification."
        if _verified_action_owner(page, expected_handle):
            owner_proven = True
            break
        if owner_attempt < 2:
            page.wait_for_timeout(900)
    if not owner_proven:
        return "blocked", ("Could not verify the current Instagram session after "
                           "the action. Review manually; do not repeat the click.")
    for attempt in range(checks):
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram requested verification after the action."
        # A newly visible wrong Profile navigation disproves the earlier proof.
        # Hidden Profile navigation is inconclusive, NOT evidence of an owner.
        observed = signed_in_handle(page)
        if observed is not None and not _same_instagram_owner(observed, expected_handle):
            return "blocked", "Current Instagram account changed during verification."
        state = _follow_state(page, username)
        if state in ("follow_back", "follow"):
            # Even when a state looks settled, a second fresh signed-in owner
            # check is mandatory. The owner could have switched in Chrome.
            if not _verified_action_owner(page, expected_handle):
                return "blocked", ("Could not reverify Instagram owner at the final "
                                   "read-only observation; no action replay allowed.")
            if challenge_detected(page) or page.locator('input[name="password"]').count():
                return "blocked", "Instagram requested verification after the action."
            # Target relationship might have rerendered during the owner proof.
            if _follow_state(page, username) != state:
                if attempt < checks-1:
                    page.wait_for_timeout(650)
                continue
            if state == "follow_back":
                return "ok", ("Action confirmed: Follow Back. "
                              "The person still follows you, but you no longer follow them.")
            return "ok", ("Action confirmed: Follow. "
                          "You no longer follow this account; it does not show a followback.")
        if attempt < checks-1:
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
        # The fresh page may hydrate its exact target hero after DOMContentLoaded.
        # Allow bounded read-only settling, NEVER another relationship click.
        result, message = _verify_final_state(page, expected_handle, username, checks=5)
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
        # Cancellation can settle after the first new document has loaded.
        # Re-observe only; a previously clicked request is never clicked again.
        result, message = _verify_final_state(page, expected_handle, username, checks=4)
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


SAVED_ACTION_STATES = {"ok", "already_not_following", "already_not_requested",
                       "review", "error", "blocked"}
SAVED_CLICK_PHASES = {"relationship_control", "unfollow_menu",
                      "private_unfollow_confirmation", "cancel_request_confirmation"}


def _invalid_saved_action_record(record):
    """A present unrecognized journal entry may conceal an irreversible click."""
    if not isinstance(record, dict):
        return True
    status = record.get("status")
    if not isinstance(status, str) or status not in SAVED_ACTION_STATES:
        return True
    # A present-but-null click intent is malformed, not proof that no
    # click happened. Only ABSENCE of this field means no intent was saved.
    if "click_intent" not in record:
        return False
    intent = record["click_intent"]
    phase = intent.get("phase") if isinstance(intent, dict) else None
    if not isinstance(phase, str) or phase not in SAVED_CLICK_PHASES:
        return True
    # A terminal success cannot coexist with an unresolved write-ahead click.
    # The journal is suspicious even if its recorded status says "ok".
    return (status in {"ok", "already_not_following", "already_not_requested"}
            and intent.get("outcome_recorded") is not True)


def _public_action_record(record):
    """Readable non-destructive status; never invent an action terminal."""
    if not _invalid_saved_action_record(record):
        return record
    return {"status": "review", "issue": "invalid_saved_action_evidence",
            "message": ("Saved action history contains unrecognized evidence. "
                        "No automatic repeat is permitted; inspect it read-only.")}


def _public_click_phase(record):
    intent = record.get("click_intent") if isinstance(record, dict) else None
    phase = intent.get("phase") if isinstance(intent, dict) else None
    return phase if isinstance(phase, str) and phase in SAVED_CLICK_PHASES else ""


def _preclick_no_action(entry):
    """Recognize a known failed *first* click, never an uncertain outcome.

    Prior versions labeled these misses "nothing clicked" but blocked them
    forever as attempted. Rechecking requires a new owner-approved batch.
    """
    # A durable click intent is never retryable simply because a later
    # read-only probe or stale error text resembles a pre-click failure.
    if _invalid_saved_action_record(entry) or entry.get("click_intent") is not None or (
            entry.get("issue") == "interrupted_action_uncertain"):
        return False
    if _preclick_identity_blocked(entry):
        return True
    # The owner-supplied GraphQL transport can refuse before its FIRST POST.
    # Such rows may be revisited only under a fresh owner-approved cohort.
    # An armed WAL always wins and can NEVER be replayed.
    if (entry.get("issue") == "reference_preclick_unavailable"
            and entry.get("status") in ("review", "blocked")
            and str(entry.get("message") or "").startswith((
                "Reference Unfollow read-only lookup:",
                "Reference Unfollow session preparation unavailable.",
                "Reference Unfollow: ambiguous target ID;",
                "Reference Unfollow: exact Instagram target or signed-in owner not verified;",
                "Reference Unfollow: target or owner changed before mutation;"))):
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


def _saved_journal_blocks_action(journal, username):
    """Fail closed on every saved target except an explicitly proven no-click miss.

    This single rule governs ten-tab prefetch admission and the actual action
    loop. An empty or malformed present record is never an untouched profile.
    """
    if username not in journal:
        return False
    return not _preclick_no_action(journal[username])


def _benign_preclick_issue(issue, record):
    """Continue only genuinely unclicked recoverable profile anomalies.

    Historical issue labels alone are not proof that an action was untouched:
    an Instagram DOM failure may occur AFTER a write-ahead click intent. In
    that case the worker must stop and retain the uncertain tab for review,
    even if the text resembles a familiar harmless missing-control error.
    """
    return (issue in {"pending_already_following", "pending_not_requested",
                      "mutual_before_action", "missing_profile_info",
                      "profile_load_timeout", "reference_preclick_unavailable"}
            and isinstance(record, dict)
            and "click_intent" not in record
            and not _invalid_saved_action_record(record))


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
        or message == "Instagram session could not be verified before skipping a non-followed profile."
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
    if task == "unfollow" and result in ("review", "blocked") and message.startswith((
        "Reference Unfollow read-only lookup:",
        "Reference Unfollow session preparation unavailable.",
        "Reference Unfollow: ambiguous target ID;",
        "Reference Unfollow: exact Instagram target or signed-in owner not verified;",
        "Reference Unfollow: target or owner changed before mutation;")):
        return "reference_preclick_unavailable"
    if result in ("review", "error", "blocked"):
        return "requires_manual_review"
    return ""


def perform_visible_action(page, username, task, expected_handle, can_act=None,
                           on_wait=None, *, preloaded=False, on_pre_click=None,
                           use_reference_transport=True):
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
    if (url.scheme != "https" or
            url.hostname not in ("www.instagram.com", "instagram.com") or
            url.path.strip("/").casefold() != username.casefold()):
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
        # An account may follow the owner without the owner following it.
        # Preserve the mutual guard unless Follow Back is definitely visible.
        if _follow_state(page, username):
            page.wait_for_timeout(500)
            if (_follow_state(page, username) and
                    _profile_relationship_control(page, username,
                                                  [r"Following", r"Siguiendo"]) is None):
                return "already_not_following", (
                    "Already not following: verified Follow / Follow Back on this target. "
                    "No relationship-changing click; continuing to next profile.")
        return "review", "This account follows you; review required."
    if task == "unfollow" and on_pre_click is not None and use_reference_transport:
        # The owner-supplied Pasted text(3).txt uses an authenticated
        # exact-ID following lookup and usePolarisUnfollowMutation. Do not
        # simulate a visible-button click as evidence that this happened.
        # The caller supplies its durable pre-click journal and real session
        # verification; no fallback second mutation is allowed.
        from instagram_unfollow_reference import reference_unfollow
        return reference_unfollow(
            page, username, expected_handle,
            can_act=can_act, on_pre_click=on_pre_click,
            verify_owner=_verified_action_owner,
            verify_target=lambda browser_page, user:
                (_exact_https_target_profile(browser_page, user) and
                 _target_identity_visible(browser_page, user)),
            verify_after=_verify_unfollow_after_readonly_refresh)

    active = (_wait_for_profile_relationship_control(
                  page, username, [r"Following", r"Siguiendo"],
                  on_wait=on_wait, can_act=can_act,
                  detect_already_not_following=True)
              if task == "unfollow" else
              _wait_for_profile_relationship_control(
                  page, username, [r"Requested", r"Solicitado", r"Solicitada"],
                  on_wait=on_wait, can_act=can_act,
                  detect_already_not_requested=True))
    if active == "already_not_following":
        if not _verified_action_owner(page, expected_handle):
            return "blocked", "Instagram session could not be verified before skipping a non-followed profile."
        return "already_not_following", (
            "Already not following: verified Follow / Follow Back for this exact profile. "
            "No Unfollow clicked; continuing to next profile.")
    if active == "already_not_requested":
        if can_act and not can_act(username):
            return "skipped", "Skipped or protected before confirming no pending request."
        if not _verified_action_owner(page, expected_handle):
            return "blocked", "The Instagram owner changed before no-request verification. No click."
        if not _stable_no_requested_state(page, username):
            return "review", ("The Follow / Requested state changed during read-only verification. "
                              "No Cancel Request click was made; inspect manually.")
        return "already_not_requested", (
            "Already not requested: verified stable Follow / Follow Back on this exact target "
            "under the signed-in owner, with no Requested control. "
            "No Cancel Request clicked; no active outgoing request to cancel.")
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
        note = _relationship_layout_note(
            page, username, ([r"Following", r"Siguiendo"] if task == "unfollow"
                             else [r"Requested", r"Solicitado", r"Solicitada"]))
        if task == "unfollow":
            # The session may have changed while a slow profile was hydrating.
            # Re-verify owner immediately before even this read-only lookup.
            if not _verified_action_owner(page, expected_handle):
                return "blocked", ("Instagram account could not be verified"
                                   " before structured diagnosis. No click.")
            if challenge_detected(page) or page.locator('input[name="password"]').count():
                return "blocked", "Instagram requested verification. No click."
            # Same-owner browser-local GET is diagnostic only. No new
            # relationship mutation, action replay or public API guarantee.
            from ig_structured_probe import inspect_structured_following
            structured = inspect_structured_following(
                page, username, owner_verified=True)
            if structured == "FOLLOWING_STRUCTURED":
                note += (" Structured lookup: Instagram returned this exact"
                         " profile in your Following list, but the required"
                         " Following control is missing. No action clicked.")
            elif structured == "STRUCTURED_RATE_LIMITED":
                return "blocked", ("Instagram rejected the read-only Following"
                                   " lookup (403/429). No action clicked; stop.")
            elif structured == "STRUCTURED_SESSION_REQUIRED":
                # A cookie unavailable to JavaScript does NOT prove the
                # already owner-verified Chrome login is invalid. The optional
                # private API diagnostic must never override the real UI
                # missing-control review or create an auth false positive.
                note += (" Structured lookup unavailable (owner ID cookie"
                         " not exposed); Chrome identity is not disproved."
                         " No action clicked.")
            else:
                note += (" Structured lookup could not verify Following;"
                         " absence is NOT proof of an unfollow. No click.")
        return "review", (MISSING_RELATIONSHIP_CONTROL +
            " Waiting timed out: " + control_name +
            " was not verifiable after 20 seconds. No action clicked. "
            "The tab remains open for manual review; the robot will not silently skip it." +
            note)
    if can_act and not can_act(username):
        return "skipped", "Skipped or protected before the first click."
    if not _verified_action_owner(page, expected_handle):
        return "blocked", "Instagram session verification failed before the first click. No action performed."
    if not (_exact_https_target_profile(page, username) and
            _target_identity_visible(page, username)):
        return "review", ("The exact target profile changed before the first click. "
                          "No relationship action clicked; review manually.")
    # Durable write-ahead intent MUST be fsynced and atomically renamed
    # before Playwright may initiate even a menu-opening relationship click.
    # Failure to persist intent prevents the click entirely.
    if on_pre_click:
        on_pre_click("relationship_control")
    active.click(timeout=10000)

    if task == "unfollow":
        # The FIRST click only opens a menu on public accounts.
        # Locate the "Unfollow" command in that menu (or a direct dialog).
        choice = _wait_for_unfollow_option(page, username, on_wait=on_wait)
        if choice is None:
            # The first Following click might have changed the optimistic UI.
            # Independently reload once; never count uncommitted UI state as OK.
            return _verify_unfollow_after_readonly_refresh(
                page, username, expected_handle)
        if can_act and not can_act(username):
            return "review", "Menu opened, but protection changed. Review before continuing."
        if not _verified_action_owner(page, expected_handle):
            return "review", "Session could not be reverified before the final Unfollow click. Inspect the open menu manually."
        if not (_exact_https_target_profile(page, username) and
                _target_identity_visible(page, username)):
            return "review", ("The target profile changed with the Unfollow menu open. "
                              "No further click; review the saved intent manually.")
        if on_pre_click:
            on_pre_click("unfollow_menu")
        choice.click(timeout=10000)
        # Public: await the final state; private accounts may show a second dialog.
        status, message = _verify_final_state(page, expected_handle, username, checks=2)
        if status == "blocked":
            return status, message
        if status == "ok":
            # Instagram may render Follow optimistically BEFORE its server
            # accepts an Unfollow. A persisted state requires a fresh GET.
            return _verify_unfollow_after_readonly_refresh(
                page, username, expected_handle)
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
                if not (_exact_https_target_profile(page, username) and
                        _target_identity_visible(page, username)):
                    return "review", ("The target changed before private Unfollow confirmation. "
                                      "No further click; review the saved intent manually.")
                if on_pre_click:
                    on_pre_click("private_unfollow_confirmation")
                confirm.click(timeout=10000)
                return _verify_unfollow_after_readonly_refresh(
                    page, username, expected_handle)
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
        if not (_exact_https_target_profile(page, username) and
                _target_identity_visible(page, username)):
            return "review", ("The target changed before Cancel Request confirmation. "
                              "No further click; review the saved intent manually.")
        if on_pre_click:
            on_pre_click("cancel_request_confirmation")
        choice.click(timeout=10000)
    # A click may have succeeded even if Instagram's client UI has not caught
    # up. A *read-only* fresh profile load may confirm it; never click again.
    result, details = _verify_final_state(page, expected_handle, username)
    if result == "blocked":
        return result, details
    # Both optimistic Follow and uncertain Requested need a read-only reload.
    # No second cancellation click is ever allowed after write-ahead intent.
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
    if not _same_instagram_owner(signed_in_handle(page), expected_handle):
        return "review", "unverified", "Active Instagram identity could not be confirmed."
    # A read-only audit reuses the SAME verified owner's Followers dialog.
    # Reloading the owner profile for every target is unnecessary traffic
    # and was causing repeated Playwright 45-second navigation failures.
    parsed = urlparse(getattr(page, "url", "") or "")
    on_owner = (parsed.hostname in ("www.instagram.com", "instagram.com")
                and parsed.path.strip("/").casefold() == expected_handle.casefold())
    if not on_owner:
        try:
            page.goto("https://www.instagram.com/" + expected_handle + "/",
                      wait_until="domcontentloaded", timeout=15000)
        except Exception:
            return ("review", "unverified",
                    "Owner Followers page unavailable: Chrome navigation timed out or failed. "
                    "No conclusion and no relationship click; stop repeated retries.")
        page.wait_for_timeout(950)
    if (challenge_detected(page) or
            not _same_instagram_owner(signed_in_handle(page), expected_handle)):
        return "blocked", "unverified", "Instagram challenge or identity mismatch."
    dialog = page.locator('[role="dialog"]').last
    if not dialog.count() or not dialog.is_visible():
        link = page.locator('a[href*="/followers/"]')
        target = None
        for i in range(min(link.count(), 15)):
            item = link.nth(i)
            href = item.get_attribute("href") or ""
            # Exact owner, no other profile's Followers widget.
            if (item.is_visible() and re.search(
                    r"/" + re.escape(expected_handle) + r"/followers/?(?:\\?|$)",
                    href, re.I)):
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
        if (challenge_detected(page) or
                not _same_instagram_owner(signed_in_handle(page), expected_handle)):
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
                            *, on_wait=None, preloaded=False,
                            allow_unacted_observation=False,
                            distinguish_observation=False):
    """Verify the previous automatic action without any relationship-changing click."""
    if task == "audit":
        result, _relation, details = perform_visible_followback_audit(
            page, username, expected_handle)
        return result, details
    if (not isinstance(previous, dict) or previous.get("status") not in
            ("ok", "already_not_following", "already_not_requested", "review", "error", "blocked")
            or (_preclick_no_action(previous) and not allow_unacted_observation)):
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
    if previous.get("status") == "already_not_requested":
        if not _verified_action_owner(page, expected_handle):
            return "blocked", "Read-only no-request verification could not prove owner; no click."
        if _stable_no_requested_state(page, username):
            return "already_not_requested", (
                "Read-only recheck: still no active outgoing request on this exact target. No click.")
        return "review", (
            "Read-only recheck: previous no-request result is no longer verified. No click.")
    if previous.get("status") == "already_not_following":
        # Do not describe an old non-followed profile as a new successful Unfollow.
        if not _verified_action_owner(page, expected_handle):
            return "blocked", "Read-only recheck could not verify the owner; no click."
        state = _follow_state(page, username)
        if state:
            return "already_not_following", (
                "Read-only recheck: still not following this exact profile. No click.")
        return "review", (
            "Read-only recheck: prior non-followed state could not be confirmed; no click.")
    result, details = _verify_final_state(page, expected_handle, username, checks=3)
    if allow_unacted_observation and not distinguish_observation:
        # Preserve the historical read-only audit's original result contract.
        return result, ("Current read-only relationship observation: " +
                        details.replace("Action confirmed:", "Current visible state:") +
                        " No relationship-changing click was made by this scan.")
    if allow_unacted_observation and distinguish_observation:
        # Observing a current relationship is NOT evidence that an earlier
        # Unfollow succeeded. A positive Following/Requested reading permits
        # a later, separately authorized action only for proven zero-click rows.
        if result == "ok":
            return "observed_not_following", (
                "Read-only observation: the exact target now shows Follow / Follow Back. "
                "No relationship-changing click was made by this scan.")
        if not _verified_action_owner(page, expected_handle):
            return "blocked", "Read-only observation could not verify the signed-in owner; no click."
        if task == "unfollow" and _profile_relationship_control(
                page, username, [r"Following", r"Siguiendo"]):
            return "still_following", (
                "Read-only observation: still Following this exact profile. "
                "No click. Only an explicitly approved proven-no-click retry is eligible.")
        if task == "cancel" and _profile_relationship_control(
                page, username, [r"Requested", r"Solicitado", r"Solicitada"]):
            return "still_requested", (
                "Read-only observation: this exact profile still displays Requested. "
                "No click. Only an explicitly approved proven-no-click retry is eligible.")
        return result, ("Current read-only relationship observation: " +
                        details.replace("Action confirmed:", "Current visible state:") +
                        " No relationship-changing click was made by this scan.")
    return result, ("Read-only batch recheck: " + details +
                    " No new relationship-changing click was made.")


class ProtectedBatchCollision(ValueError):
    """No action batch was written: exact approved cohort became protected."""

    def __init__(self, usernames, *, task, batch_size):
        self.usernames = sorted(usernames)
        self.task = task
        self.batch_size = batch_size
        n = len(self.usernames)
        super().__init__(
            f"Approved batch is stale: {n} selected profile(s) are now "
            "protected on this Windows device. Refresh the protected list and "
            "review a NEW cohort; the previous approval was not used."
        )


from robot_interlock import ActionLease

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
        self.owner_profile_visits = 0  # read-only owner fallback, distinct from target visits
        self.review_only = False
        self.review_profiles_only = False
        self.audit_source = "visible"
        self.history_recheck_mode = False
        self.historical_seen = set()
        self.historical_not_following_seen = set()
        self.continuing_batch = False
        self.active_batch_id = ""
        self.cancel_requested = False
        self.cancel_batch_id = ""
        self.skipped = set()
        self.batch_size = 30
        self.tab_flow = "sequential"
        self.max_count = ACTION_PROFILE_VISITS_PER_HOUR
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

    def _target_visits_file_for(self, owner, account, task):
        """Owner/account/task-scoped write-ahead evidence of target navigation."""
        base = self._base_for(owner, account, task)
        return base.with_name(base.stem + "-target-visits.json")

    def _visited_usernames(self, owner, account, task, journal):
        """All past targets, including confirmed, no-click and interrupted visits."""
        visits = _read_json(self._target_visits_file_for(owner, account, task), {})
        if (not isinstance(journal, dict) or
                any(valid_username(u) != u or not isinstance(record, dict)
                    for u, record in visits.items())):
            raise ValueError("Saved target-visit history is invalid; inspect it before a new batch.")
        return sorted(set(journal) | set(visits))

    def _reserve_target_visit(self, username):
        """Persist BEFORE opening an Instagram target URL; never imply a click."""
        if self.review_only or self.task not in ("unfollow", "cancel"):
            return
        path = self._target_visits_file_for(self.owner, self.account, self.task)
        marks = _read_json(path, {})
        if username not in marks:
            marks[username] = {
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "batch_id": self.active_batch_id,
                "state": "target_navigation_reserved_not_action_confirmed",
            }
            _atomic_json(path, marks)

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
            cohorts = self._review_batches(owner, account, task)
            protected = set(_read_json(self._protection_file_for(owner, account), []))
        reusable = []
        for entry in cohorts:
            if not isinstance(entry, dict): continue
            base = entry.get("original_targets") or []
            if not isinstance(base, list): continue
            for user in base:
                if (valid_username(user) == user and user not in protected and
                        (user not in journal or
                         (not _invalid_saved_action_record(journal[user]) and
                          _preclick_no_action(journal[user])))):
                    reusable.append(user)
        visited = self._visited_usernames(owner, account, task, journal)
        attempted = sorted(user for user, record in journal.items()
            if valid_username(user) == user and
            (_invalid_saved_action_record(record) or
             (record.get("status") in SAVED_ACTION_STATES
              and not _preclick_no_action(record))))
        # Timestamp/provenance for the full saved journal, not only the
        # most recent active cohort. No cookies, HTTP payloads or secrets.
        history_rows = []
        for username, record in journal.items():
            if valid_username(username) != username:
                continue
            clean = _public_action_record(record)
            history_rows.append({
                "username": username,
                "status": clean.get("status", "review"),
                "issue": clean.get("issue", ""),
                "message": clean.get("message", ""),
                "at": str(record.get("at") or "") if isinstance(record, dict) else "",
                "click_phase": _public_click_phase(record),
            })
        return {"owner": owner, "account": account, "task": task,
                "attempted_usernames": attempted,
                "visited_usernames": visited,
                "reusable_usernames": list(dict.fromkeys(reusable)),
                "history_rows": history_rows}

    def _review_batches_file_for(self, owner, account, task):
        base = self._base_for(owner, account, task)
        return base.with_name(base.stem + "-batch-reviews.json")

    def _historical_recheck_file_for(self, owner, account, task):
        base = self._base_for(owner, account, task)
        return base.with_name(base.stem + "-historical-rechecks.json")

    def historical_recheck_status(self, data):
        owner, account, task = self._review_scope(data)
        with self.lock:
            saved = _read_json(self._historical_recheck_file_for(owner, account, task), {})
            rows = saved.get("results", {}) if isinstance(saved, dict) else {}
            if not isinstance(rows, dict): rows = {}
            counts = {"observed_not_following": 0, "observed_not_requested": 0,
                      "still_unresolved": 0, "total": 0}
            for record in rows.values():
                if not isinstance(record, dict): continue
                state = record.get("observation")
                if state in counts: counts[state] += 1
                counts["total"] += 1
            return {"owner": owner, "account": account, "task": task,
                    "counts": counts,
                    "completed_at": saved.get("completed_at") if isinstance(saved, dict) else None,
                    "source": "read_only_no_relationship_click"}

    def _review_batches(self, owner, account, task):
        return _read_json(self._review_batches_file_for(owner, account, task), [])

    def _pending_review(self, owner, account, task):
        batches = self._review_batches(owner, account, task)
        return next((entry for entry in reversed(batches)
                     if not entry.get("approved_at") and not entry.get("deferred_at")), None)

    def open_profile(self, data):
        """Open an owner-selected issue in the robot's persistent Chrome profile.

        Never fall back to the system default browser (which uses a different
        Instagram login). No credentials or cookies leave the local machine.
        This is manual navigation only; it never changes a relationship.
        """
        owner, account, task = self._review_scope(data)
        username = valid_username(data.get("username"))
        if not username:
            raise ValueError("Choose a valid Instagram profile.")
        with self.lock:
            running = bool(self.worker and self.worker.is_alive())
            if running and (owner, account, task) != (self.owner, self.account, self.task):
                raise ValueError("Another Instagram account owns the active robot session.")
            # Manual review is allowed after restarting Windows: opening the
            # same persistent Chrome directory is navigation, not a robot action.
            # A fresh process has no active self.owner/task and must not prevent
            # visiting earlier journal issues in the saved browser session.
            session = self.session_dir.resolve()
        candidates = [shutil.which("chrome.exe"), shutil.which("chrome")]
        for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(env)
            if base:
                candidates.append(str(Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe"))
        chrome = next((str(Path(p)) for p in candidates if p and Path(p).is_file()), None)
        if chrome is None:
            raise ValueError("Google Chrome is required to reopen the robot's authenticated session.")
        # Chrome's process singleton reuses the existing browser when this
        # user-data-dir is already active. Do not open the app's UI profile.
        url = "https://www.instagram.com/" + username + "/"
        try:
            subprocess.Popen([chrome, "--user-data-dir=" + str(session),
                              "--new-tab", url],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, close_fds=True)
        except OSError as exc:
            raise ValueError("Unable to reopen robot Chrome: " + str(exc)) from exc
        return {"status": "opening", "username": username,
                "session": "robot-persistent-chrome", "relationship_action": False}

    def batch_review(self, data):
        owner, account, task = self._review_scope(data)
        with self.lock:
            entry = self._pending_review(owner, account, task)
            if entry:
                journal = _read_json(self._base_for(owner, account, task), {})
                details = dict(entry)
                # Disk-only protection may have changed after this cohort was
                # saved. Return a read-only conflict list to the owner UI.
                guard = set(_read_json(self._protection_file_for(owner, account), []))
                details["protected_in_cohort"] = sorted(set(entry["targets"]) & guard)
                def _safe_batch_result(username):
                    if username not in journal:
                        return {"status": "pending", "message": "",
                                "safe_no_click": False}
                    source = journal[username]
                    public = _public_action_record(source)
                    return {"status": public.get("status", "review"),
                            "message": public.get("message", ""),
                            "safe_no_click": (
                                not _invalid_saved_action_record(source) and
                                _preclick_no_action(source))}
                details["action_results"] = {
                    username: _safe_batch_result(username)
                    for username in entry["targets"]}
            else:
                details = None
            return {"owner": owner, "account": account, "task": task,
                    "batch": details}

    def deferred_batch_history(self, data):
        """Read-only local evidence of owner-scoped archived cohorts.

        Summaries never promote review or overwrite original action journals.
        Users can inspect why an old authorized batch stopped after protection
        changes and distinguish it from their new active cohort.
        """
        owner, account, task = self._review_scope(data)
        with self.lock:
            saved = self._review_batches(owner, account, task)
            deferred = [
                entry for entry in saved
                if isinstance(entry, dict) and entry.get("deferred_at")
            ]
            recent = list(reversed(deferred))[:20]
            rows = [
                {"batch_id": str(entry.get("id", "")),
                 "created_at": str(entry.get("created_at", "")),
                 "deferred_at": str(entry.get("deferred_at", "")),
                 "reason": str(entry.get("deferred_reason", "")),
                 "target_count": len(entry.get("targets", []))
                    if isinstance(entry.get("targets"), list) else 0,
                 "protected_count": len(entry.get("deferred_protected_usernames", []))
                    if isinstance(entry.get("deferred_protected_usernames"), list) else 0,
                 "action_recorded": int(entry.get("deferred_action_recorded") or 0),
                 "untouched": int(entry.get("deferred_untouched") or 0),
                 "marked_reviewed": False}
                for entry in recent
            ]
            return {"owner": owner, "account": account, "task": task,
                    "total_deferred": len(deferred), "recent": rows,
                    "read_only": True, "source": "local_saved_action_batches"}

    def _review_scope(self, data):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        task = str(data.get("task") or "").strip()
        if not owner or not account or len(owner) > 200 or len(account) > 120 or task not in TASKS:
            raise ValueError("Choose a valid owner, Instagram account and robot task.")
        return owner, account, task

    def replan_incomplete_batch(self, data):
        """Resize the active incomplete cohort; keep every unused profile reusable.

        No archiving, no review approval, no clicks and no lost original targets.
        The persistent original/carryover identities are retained in the SAME
        pending batch. Only untouched or explicitly proven pre-click misses
        may enter the newly selected 1–1,000-person batch.
        """
        owner, account, task = self._review_scope(data)
        batch_id = str(data.get("batch_id") or "")
        desired = data.get("desired_batch_size")
        if (type(desired) is not int or not 1 <= desired <= 1000
                or not batch_id or data.get("confirmation") !=
                "replan-size:" + batch_id + ":" + str(desired)):
            raise ValueError("Replanning requires exact current batch and selected size.")
        with self.collector.browser_admission, self.lock:
            if (self.worker and self.worker.is_alive()) or (
                    self.collector.worker and self.collector.worker.is_alive()):
                raise ValueError("Pause all Chrome robots before replanning a saved batch.")
            if self.owner and (owner, account) != (self.owner, self.account):
                raise ValueError("A different Instagram workspace is bound to the robot.")
            entries = self._review_batches(owner, account, task)
            pending = next((e for e in reversed(entries)
                            if not e.get("approved_at") and not e.get("deferred_at")), None)
            if not pending or pending.get("id") != batch_id:
                raise ValueError("The saved batch changed; refresh and confirm again.")
            old_size = len(pending.get("targets", []))
            if old_size == desired:
                raise ValueError("Saved cohort already matches the selected size.")
            baseline = pending.get("original_targets") or pending["targets"]
            if (not isinstance(baseline, list) or
                    any(valid_username(u) != u for u in baseline)):
                raise ValueError("Original cohort is invalid; preserve it for manual review.")
            journal = _read_json(self._base_for(owner, account, task), {})
            protected = set(_read_json(self._protection_file_for(owner, account), []))
            # A present malformed/empty/statusless record is NOT an untouched
            # profile. Replanning must use the same strict no-replay evidence
            # as start() and the Developer forensic auditor.
            safe = [u for u in baseline if u not in protected and (
                u not in journal or
                (not _invalid_saved_action_record(journal[u])
                 and _preclick_no_action(journal[u])))]
            safe = list(dict.fromkeys(safe))
            if not safe:
                raise ValueError("No untouched or proven no-click profiles remain; verify prior attempts.")
            new_targets = safe[:desired]
            pending["original_targets"] = list(baseline)
            pending["targets"] = new_targets
            pending["carryover_targets"] = safe[len(new_targets):]
            pending["selected_batch_size"] = desired
            pending.setdefault("replan_history", []).append({
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "previous_active_size": old_size,
                "selected_size": desired,
                "next_active_size": len(new_targets),
                "reusable_after_next_batch": len(safe) - len(new_targets),
            })
            _atomic_json(self._review_batches_file_for(owner, account, task), entries)
            return {"owner": owner, "account": account, "task": task,
                    "batch_id": batch_id, "previous_size": old_size,
                    "requested_new_size": desired, "active_size": len(new_targets),
                    "reusable_after_active": len(safe) - len(new_targets),
                    "action_recorded": len(baseline) - len(safe),
                    "marked_reviewed": False, "approved_usernames": [],
                    "next_batch_requires_confirmation": True,
                    "status": "replanned_active_cohort_not_archived"}

    def set_aside_incomplete_batch(self, data):
        """Owner-confirmed safe transition from unfinished N to a NEW N.

        This does not resize the original cohort, approve any result, visit
        Instagram or mutate the action journal. It archives the *exact* saved
        cohort so a fresh, independently approved batch may be planned.
        Previously untouched names remain visible and eligible. Any possible
        click or malformed journal entry stays excluded from automatic retry.
        """
        owner, account, task = self._review_scope(data)
        batch_id = str(data.get("batch_id") or "")
        desired = data.get("desired_batch_size")
        if (type(desired) is not int or not 1 <= desired <= 1000 or
                not batch_id or
                data.get("confirmation") != "new-batch:" + batch_id + ":" + str(desired)):
            raise ValueError("Confirm the exact saved batch and requested new size.")
        with self.collector.browser_admission, self.lock:
            if ((self.worker and self.worker.is_alive()) or
                    (self.collector.worker and self.collector.worker.is_alive())):
                raise ValueError("Finish or pause active Chrome robots before planning a new batch.")
            if self.owner and (owner, account) != (self.owner, self.account):
                raise ValueError("A different Instagram workspace is bound to the robot.")
            entries = self._review_batches(owner, account, task)
            pending = next((e for e in reversed(entries)
                            if not e.get("approved_at") and not e.get("deferred_at")), None)
            if not pending or pending.get("id") != batch_id:
                raise ValueError("Saved cohort changed. Refresh before selecting a new batch.")
            targets = pending.get("targets")
            if (not isinstance(targets, list) or not targets or
                    len(targets) > MAX_ACTIONS_PER_JOB or
                    any(valid_username(u) != u for u in targets) or
                    len(set(targets)) != len(targets)):
                raise ValueError("Invalid saved cohort; preserve it for manual inspection.")
            journal = _read_json(self._base_for(owner, account, task), {})
            protected = set(_read_json(self._protection_file_for(owner, account), []))
            historical = pending.get("original_targets") or targets
            carried = pending.get("carryover_targets") or []
            # Include earlier unacted carryovers so every original name stays
            # represented after a previous resize. NEVER replay clicked or
            # invalid attempts simply because the user selects a new size.
            lineage = list(dict.fromkeys([*historical, *targets, *carried]))
            reusable = [
                username for username in lineage
                if valid_username(username) == username
                and username not in protected
                and (username not in journal or (
                    not _invalid_saved_action_record(journal[username]) and
                    _preclick_no_action(journal[username])))
            ]
            recorded = sum(username in journal for username in lineage)
            pending["deferred_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            pending["deferred_reason"] = "owner_new_batch_explicit"
            pending["deferred_action_recorded"] = recorded
            pending["deferred_untouched"] = len(reusable)
            pending["requested_next_batch_size"] = desired
            pending["marked_reviewed"] = False
            # Single atomic write; do not touch saved click WAL, history, or
            # protection at all. Reruns using a stale ID will be refused.
            _atomic_json(self._review_batches_file_for(owner, account, task), entries)
            return {"owner": owner, "account": account, "task": task,
                    "batch_id": batch_id, "saved_size": len(targets),
                    "requested_new_size": desired, "reusable_usernames": reusable,
                    "previous_action_records": recorded,
                    "marked_reviewed": False, "approved_usernames": [],
                    "next_batch_requires_confirmation": True,
                    "status": "saved_cohort_set_aside_for_new_batch"}

    def defer_protected_batch(self, data):
        """Archive a blocked cohort without approving any profile or action."""
        owner, account, task = self._review_scope(data)
        batch_id = str(data.get("batch_id") or "")
        if not batch_id or data.get("confirmation") != "defer-protected:" + batch_id:
            raise ValueError("Deferring a protected cohort requires explicit batch confirmation.")
        with self.collector.browser_admission, self.lock:
            if (self.worker and self.worker.is_alive()) or (
                    self.collector.worker and self.collector.worker.is_alive()):
                raise ValueError("Pause all Chrome robots before deferring a protected batch.")
            if self.owner and (owner, account) != (self.owner, self.account):
                raise ValueError("A different Instagram workspace is bound to the robot.")
            entries = self._review_batches(owner, account, task)
            pending = next((entry for entry in reversed(entries)
                            if not entry.get("approved_at") and not entry.get("deferred_at")), None)
            if not pending or pending.get("id") != batch_id:
                raise ValueError("The unapproved batch changed. Refresh before deferring.")
            protected = set(_read_json(self._protection_file_for(owner, account), []))
            collisions = sorted(set(pending["targets"]) & protected)
            if not collisions:
                raise ValueError("This cohort has no saved protected collision. Continue its exact batch.")
            journal = _read_json(self._base_for(owner, account, task), {})
            observed = [u for u in pending["targets"]
                        if isinstance(journal.get(u), dict) and journal[u].get("status")]
            # Preserve original targets and uncertainty: no fake Reviewed,
            # no replay and no modification of action/protection journals.
            pending["deferred_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            pending["deferred_reason"] = "protected_collision"
            pending["deferred_protected_usernames"] = collisions
            pending["deferred_action_recorded"] = len(observed)
            pending["deferred_untouched"] = len(pending["targets"]) - len(observed)
            _atomic_json(self._review_batches_file_for(owner, account, task), entries)
            return {"owner": owner, "account": account, "task": task,
                    "batch_id": batch_id, "deferred_at": pending["deferred_at"],
                    "protected_usernames": collisions,
                    "action_recorded": len(observed),
                    "untouched": len(pending["targets"]) - len(observed),
                    "approved_usernames": [], "marked_reviewed": False,
                    "next_batch_requires_confirmation": True}

    def approve_batch(self, data):
        owner, account, task = self._review_scope(data)
        batch_id = str(data.get("batch_id") or "")
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Wait for the robot to finish before approving the batch.")
            entries = self._review_batches(owner, account, task)
            match = next((entry for entry in reversed(entries)
                         if entry.get("id") == batch_id and not entry.get("approved_at")
                         and not entry.get("deferred_at")), None)
            if match is None:
                raise ValueError("The pending batch changed. Refresh before confirming.")
            if data.get("confirmation") != "reviewed:" + batch_id:
                raise ValueError("Only your explicit batch confirmation can mark this reviewed.")
            journal = _read_json(self._base_for(owner, account, task), {})
            rechecked = match.get("recheck_results") or {}
            # Approval closes the pending cohort: do not strand profiles that
            # never received an actual attempt or a read-only observation.
            # A recorded uncertain outcome may remain unresolved, but it
            # cannot silently promote an untouched target to Reviewed.
            untouched = [
                username for username in match["targets"]
                if not (isinstance(journal.get(username), dict)
                        and journal[username].get("status"))
                and not (isinstance(rechecked.get(username), dict)
                         and rechecked[username].get("status"))
            ]
            if untouched:
                raise ValueError(
                    "The batch still has " + str(len(untouched)) +
                    " untouched profiles. Continue the saved cohort before approval.")
            # Never let a malformed but superficially "ok" journal row
            # become approved through its forged/stale status field.
            if any(username in journal and
                   _invalid_saved_action_record(journal[username])
                   for username in match["targets"]):
                raise ValueError(
                    "Invalid saved action evidence requires manual review;"
                    " do not mark this batch approved.")
            approved = []
            unresolved = []
            for username in match["targets"]:
                result = rechecked.get(username, {}).get("status")
                if result is None:
                    result = journal.get(username, {}).get("status")
                if result in ("ok", "already_not_following", "already_not_requested"):
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

    def recheck_history(self, data):
        """Revisit unresolved old journal records; no repeat relationship clicks."""
        owner, account, task = self._review_scope(data)
        if task not in ("unfollow", "cancel"):
            raise ValueError("Historical recheck applies only to relationship tasks.")
        expected = valid_username(data.get("expected_handle"))
        if not expected or data.get("confirmation") != "history-read-only:" + task:
            raise ValueError("Confirm the selected account and read-only re-audit.")
        count, window, delay = check_pacing(
            int(data.get("batch_size", 30)), ACTION_WINDOW_MINUTES,
            data.get("gap_seconds", 10))
        rest_input = data.get("rest_minutes", 5)
        _, rest = check_batch_rest(count if rest_input else 0, rest_input)
        with self.collector.browser_admission, self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Pause the action robot before historical read-only checks.")
            if self.collector.worker and self.collector.worker.is_alive():
                raise ValueError("Pause Profile Counts before historical read-only checks.")
            journal = _read_json(self._base_for(owner, account, task), {})
            targets = [username for username, record in journal.items()
                       if valid_username(username) == username
                       and isinstance(record, dict)
                       and record.get("status") in ("review", "error", "blocked")]
            if not targets:
                raise ValueError("No unresolved historical profiles need re-audit.")
            self.owner, self.account, self.handle, self.task = owner, account, expected, task
            protected = self._protected()
            targets = [name for name in targets if name not in protected]
            if not targets:
                raise ValueError("All unresolved historical profiles are protected.")
            old = _read_json(self._historical_recheck_file_for(owner, account, task), {})
            results = old.get("results", {}) if isinstance(old, dict) else {}
            if not isinstance(results, dict): results = {}
            # Do not always re-open the same first 1,000 old failures.
            # Prefer entries never read, then the oldest unresolved observation.
            # Already-confirmed read-only Follow state is complete *as a scan*
            # but never approved as a historical Unfollow action.
            to_revisit = [name for name in targets
                          if not (isinstance(results.get(name), dict)
                                  and results[name].get("observation") == "observed_not_following")]
            if not to_revisit:
                raise ValueError("All historical failed actions already have a read-only current-state observation.")
            to_revisit.sort(key=lambda name: (
                0 if name not in results else 1,
                str(results.get(name, {}).get("at", "")) if isinstance(results.get(name), dict) else "",
                name))
            self.targets = to_revisit[:MAX_ACTIONS_PER_JOB]
            self.active_batch_id = ""
            self.review_only, self.history_recheck_mode = True, True
            self.review_profiles_only = False
            self.historical_seen, self.historical_not_following_seen = set(), set()
            self.continuing_batch = False
            self.open_review_tabs, self.current_wait = [], None
            self.skipped.clear()
            self.batch_size = count
            self.tab_flow = "sequential"
            self.max_count, self.window_minutes, self.min_delay_seconds = ACTION_PROFILE_VISITS_PER_HOUR, window, delay
            self.rest_minutes = rest
            self.stop_event.clear()
            self.cancel_requested = False
            self.cancel_batch_id = ""
            self.status, self.message = ("starting",
                "Re-auditing unresolved historical profiles (read-only, no actions).")
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

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
            only_issues = data.get("review_profiles_only") is True
            if "review_profiles_only" in data and not isinstance(data["review_profiles_only"], bool):
                raise ValueError("Review-only selection must be explicit and Boolean.")
            if only_issues and task not in ("unfollow", "cancel"):
                raise ValueError("Targeted Review scan supports only Unfollow or Cancel Pending.")
            if only_issues:
                journal = _read_json(self._base_for(owner, account, task), {})
                if not isinstance(journal, dict):
                    raise ValueError("Original action journal is invalid. No Chrome navigation.")
                protected = set(_read_json(self._protection_file_for(owner, account), []))
                targets = [u for u in entry["targets"]
                           if u not in protected and
                           (u not in journal or
                            (isinstance(journal[u], dict) and
                             journal[u].get("status") in ("review", "error", "blocked")))]
                if not targets:
                    raise ValueError("No Review or untouched profiles remain to inspect.")
            else:
                targets = list(entry["targets"])
            self.targets = targets
            self.active_batch_id = entry["id"]
            self.review_only = True
            self.review_profiles_only = only_issues
            self.history_recheck_mode = False
            self.continuing_batch = False
            self.open_review_tabs = []
            self.current_wait = None
            self.skipped.clear()
            self.batch_size = int(data.get("batch_size", 30))
            self.tab_flow = "sequential"  # read-only rechecks do not need ten-tab jumping
            self.max_count, self.window_minutes, self.min_delay_seconds = check_pacing(
                ACTION_PROFILE_VISITS_PER_HOUR, ACTION_WINDOW_MINUTES,
                data.get("gap_seconds", 10))
            rest_input = data.get("rest_minutes", 5)
            _, self.rest_minutes = check_batch_rest(
                self.batch_size if rest_input else 0, rest_input)
            self.stop_event.clear()
            self.cancel_requested = False
            self.cancel_batch_id = ""
            self.status, self.message = "starting", (
                "Reopening only Review and untouched profiles in Chrome (read-only)."
                if only_issues else "Rechecking unapproved batch in Chrome (read-only).")
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def _save_recheck_result(self, user, result, message):
        if self.history_recheck_mode:
            path = self._historical_recheck_file_for(self.owner, self.account, self.task)
            saved = _read_json(path, {})
            if not isinstance(saved, dict): saved = {}
            rows = saved.setdefault("results", {})
            if not isinstance(rows, dict): rows = {};saved["results"] = rows
            previous = rows.get(user, {})
            events = previous.get("observations", []) if isinstance(previous, dict) else []
            observation = ("observed_not_requested"
                           if self.task == "cancel" and result == "already_not_requested"
                           else "observed_not_following"
                           if result in ("ok", "already_not_following", "already_not_requested")
                           else "still_unresolved")
            record = {"observation": observation, "verification_status": result,
                      "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      "read_only": True}
            rows[user] = {**record, "observations": list(events)[-24:] + [record]}
            saved["completed_at"] = record["at"]
            _atomic_json(path, saved)
            self.historical_seen.add(user)
            if observation in ("observed_not_following", "observed_not_requested"):
                self.historical_not_following_seen.add(user)
            else:
                self.historical_not_following_seen.discard(user)
            return
        entries = self._review_batches(self.owner, self.account, self.task)
        entry = next((x for x in reversed(entries)
                      if x.get("id") == self.active_batch_id and not x.get("approved_at")), None)
        if entry:
            entry.setdefault("recheck_results", {})[user] = {
                "status": result, "message": message,
                "read_only": True,
                "observation_only": self.review_profiles_only,
                "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            _atomic_json(self._review_batches_file_for(self.owner, self.account, self.task), entries)

    def _discard_stale_recheck(self, username):
        """An actual later action supersedes old read-only observations.

        Preserve all original click journals. Never let a prior incomplete
        recheck result hide a newly verified action in the approval panel.
        """
        entries = self._review_batches(self.owner, self.account, self.task)
        entry = next((x for x in reversed(entries)
                      if x.get("id") == self.active_batch_id and not x.get("approved_at")), None)
        if entry and username in entry.get("recheck_results", {}):
            entry["recheck_results"].pop(username, None)
            _atomic_json(self._review_batches_file_for(
                self.owner, self.account, self.task), entries)

    def _protection_file_for(self, owner, account):
        ident = "\0".join((owner, account))
        digest = hashlib.sha256(ident.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("action-protected-" + digest + ".json")

    def _protection_file(self):
        return self._protection_file_for(self.owner, self.account)

    def _protected(self):
        return set(_read_json(self._protection_file(), []))

    def _journal(self):
        return _read_json(self._base(), {})

    def _protected_for(self, username):
        with self.lock:
            return username in self._protected()

    def protect(self, data):
        """Persist owner/account protections; removing one requires explicit intent.

        A UI toggle used to send "protected=[username]" for BOTH directions.
        A missing user in a batch snapshot is never sufficient to unprotect.
        """
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("Select an Insta Cleaner owner and Instagram workspace.")
        additions = _users(data.get("protected", []))
        removals = _users(data.get("unprotected", []))
        if additions and removals:
            raise ValueError("Protect and unprotect require separate commands.")
        if removals and (len(removals) != 1 or
                         data.get("confirmation") != "unprotect:" + removals[0]):
            raise ValueError("Removing a saved protection requires explicit confirmation.")
        with self.lock:
            active = bool(self.worker and self.worker.is_alive())
            # Never change a different owner's saved guard during an active
            # robot; also retain paused-task identity guards.
            if not self.owner or (owner, account) != (self.owner, self.account):
                # The loopback token alone does not authenticate an arbitrary
                # owner scope. Before any task binds this process to an
                # Instagram workspace, protection may be staged LOCALLY by
                # the UI and is persisted with the next approved batch.
                raise ValueError("Select the same account to update protected profiles.")
            if removals and active:
                raise ValueError("Pause and finish the active robot before removing protection.")
            path = self._protection_file_for(owner, account)
            protected = set(_read_json(path, []))
            protected.update(additions)
            protected.difference_update(removals)
            _atomic_json(path, sorted(protected))
            if (owner, account) == (self.owner, self.account):
                return self.snapshot()
            return {"owner": owner, "account": account,
                    "protected": len(protected), "running": False,
                    "status": "idle", "message": "Saved protection updated for this workspace."}

    def skip(self, data):
        with self.lock:
            if (str(data.get("owner") or ""), str(data.get("account") or "")) != (self.owner, self.account):
                raise ValueError("The action batch belongs to another Instagram account.")
            user = valid_username(data.get("username"))
            if not user or user not in self.targets:
                raise ValueError("This profile is not in the current batch.")
            self.skipped.add(user)
            return self.snapshot()

    def _finish_owner_cancel_locked(self):
        """Archive only the selected unapproved cohort; NEVER change the action WAL."""
        if not self.cancel_requested:
            return
        batch_id = self.cancel_batch_id
        if batch_id:
            entries = self._review_batches(self.owner, self.account, self.task)
            pending = next((e for e in reversed(entries)
                            if not e.get("approved_at") and not e.get("deferred_at")), None)
            if pending is None or pending.get("id") != batch_id:
                raise ValueError("Saved cohort changed during cancellation; evidence preserved.")
            journal = _read_json(self._base(), {})
            if not isinstance(journal, dict):
                raise ValueError("Action journal is invalid; preserve it for inspection.")
            targets = pending.get("targets", [])
            if not isinstance(targets, list):
                raise ValueError("Saved cohort invalid; preserve it for inspection.")
            recorded = sum(u in journal for u in targets)
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            pending["deferred_at"] = now
            pending["cancelled_by_owner_at"] = now
            pending["deferred_reason"] = "owner_cancelled"
            pending["deferred_action_recorded"] = recorded
            pending["deferred_untouched"] = len(targets) - recorded
            pending["marked_reviewed"] = False
            _atomic_json(self._review_batches_file_for(self.owner, self.account, self.task), entries)
        self.cancel_requested = False
        self.cancel_batch_id = ""
        self.status = "cancelled"
        self.message = ("Batch cancelled. Saved actions and possible clicks were preserved. "
                        "You can switch jobs after Chrome closes.")
        self.wait_until = 0
        self.current_wait = None

    def cancel_current_batch(self, data):
        """Stop the next operations; never erase or repeat an in-flight action."""
        owner, account, task = self._review_scope(data)
        with self.lock:
            if (owner, account, task) != (self.owner, self.account, self.task):
                raise ValueError("Cancel must name the active owner, account and robot task.")
            # A historical/recheck scan is READ-ONLY. Stopping that scan must
            # never archive a separate action cohort just because it exists.
            pending = (None if self.review_only else
                       self._pending_review(owner, account, task))
            batch_id = pending.get("id") if pending else ""
            if ((data.get("batch_id") or "") != batch_id or
                    data.get("confirmation") != "cancel-batch:" + batch_id):
                raise ValueError("Confirm the exact saved cohort before cancelling.")
            if not batch_id and not (self.worker and self.worker.is_alive()):
                raise ValueError("There is no active or saved unfinished job to cancel.")
            self.cancel_requested = True
            self.cancel_batch_id = batch_id
            if self.worker and self.worker.is_alive():
                self.stop_event.set()
                self.status = "cancelling"
                self.message = ("Cancellation requested. The current operation may be in flight; "
                                "no new targets will start. Original evidence is preserved.")
            else:
                try:
                    self._finish_owner_cancel_locked()
                except Exception:
                    self.cancel_requested = False
                    self.cancel_batch_id = ""
                    raise
            return self.snapshot()

    def _run_with_lease(self, lease):
        # The worker, not the HTTP request thread, owns the full action lease.
        # Always free it on login failure, exception, pause, or final review.
        try:
            self._run()
        finally:
            lease.release()

    def start(self, data, *, resume=False):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        expected = valid_username(data.get("expected_handle"))
        task = str(data.get("task") or "")
        targets = _users(data.get("targets"))
        audit_source = str(data.get("audit_source") or "visible")
        if (audit_source not in ("visible", "live_lists") or
                (task != "audit" and audit_source != "visible")):
            raise ValueError("Alternative live lists are only available for read-only Followback Audit.")
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("Select an Insta Cleaner login and Instagram workspace first.")
        if not expected:
            raise ValueError("Assign the active Instagram @handle before starting.")
        if task not in TASKS or not targets:
            raise ValueError("Select a job containing valid profiles.")
        tab_flow = str(data.get("tab_flow") or "sequential")
        action_tab_stage_limit(tab_flow)  # reject unknown navigation modes
        count = int(data.get("batch_size", 30))
        if count != data.get("batch_size", 30) or not 1 <= count <= 1000:
            raise ValueError("The batch size must be between 1 and 1,000.")
        max_count, window, delay = check_pacing(ACTION_PROFILE_VISITS_PER_HOUR, ACTION_WINDOW_MINUTES,
                                                 data.get("gap_seconds", 10))
        rest_input = data.get("rest_minutes", 5)
        every, rest = check_batch_rest(count if rest_input else 0, rest_input)
        if data.get("confirmation") != task + ":" + str(len(targets)):
            raise ValueError("The batch was not explicitly approved.")
        if task == "unfollow" and data.get("followers_evidence") is not True:
            raise ValueError("A complete Followers list has not been verified.")
        retry_selection = data.get("review_retry_usernames")
        if retry_selection is not None:
            if task not in ("unfollow", "cancel") or resume or not isinstance(retry_selection, list):
                raise ValueError("Review retry requires a new named owner-approved relationship action.")
            if not retry_selection or _users(retry_selection) != retry_selection or len(set(retry_selection)) != len(retry_selection):
                raise ValueError("Review retry requires a nonempty unique valid target list.")
            if not set(retry_selection).issubset(set(targets)):
                raise ValueError("Review retry must be a subset of the exact saved cohort.")
            if data.get("review_retry_confirmation") != "review-retry:" + str(data.get("batch_id") or "") + ":" + ",".join(retry_selection):
                raise ValueError("Review retry requires separate exact-target consent.")
        lease = ActionLease(self.data_dir).acquire()
        started = False
        try:
            with self.collector.browser_admission, self.lock:
                if self.worker and self.worker.is_alive():
                    raise ValueError("An Instagram action robot is already running.")
                if self.collector.worker and self.collector.worker.is_alive():
                    raise ValueError("Finish or pause Profile Counts before starting an action robot.")
                if resume and (owner, account, task) != (self.owner, self.account, self.task):
                    raise ValueError("Cannot resume a different task or account.")
                if resume and self.status not in ("paused", "error", "review", "blocked"):
                    raise ValueError("There is no paused task to resume.")
                if resume and self.review_only:
                    raise ValueError("Read-only verification cannot resume as an Unfollow job.")
                if resume and targets != self.targets:
                    raise ValueError("Resuming actions cannot change the saved target cohort.")
                if resume and task == "audit" and audit_source != self.audit_source:
                    raise ValueError("Resume must preserve the originally approved audit source.")
                pending_entry = None if resume else self._pending_review(owner, account, task)
                if not resume:
                    if pending_entry:
                        if (data.get("batch_id") != pending_entry["id"] or
                                targets != pending_entry["targets"]):
                            raise ValueError("An unapproved batch exists. Continue its exact saved ID and profiles; never replace it.")
                    elif data.get("batch_id"):
                        raise ValueError("Saved batch changed. Refresh before restarting actions.")
                    # Validate the EXACT owner-approved cohort before writing ANY
                    # review-batch row or rebinding the worker. A stale Desktop
                    # favorites snapshot cannot know about disk-only protections.
                    # Do not silently trim/reapprove targets: ask the owner to
                    # inspect and approve the replacement list explicitly.
                    disk_guard = set(_read_json(self._protection_file_for(owner, account), []))
                    ui_guard = set(_users(data.get("protected", [])))
                    collision = sorted(set(targets) & (disk_guard | ui_guard))
                    if collision:
                        raise ProtectedBatchCollision(
                            collision, task=task, batch_size=len(targets))
                if retry_selection is not None:
                    if pending_entry is None:
                        raise ValueError("Review retry cannot create a new cohort.")
                    # Explicit scan/consent + durable zero-click proof is required.
                    # A preceding possible click remains blocked regardless of
                    # current Following state.
                    observations = pending_entry.get("recheck_results", {})
                    for user in retry_selection:
                        observed = observations.get(user, {})
                        prior = _read_json(self._base_for(owner, account, task), {}).get(user)
                        if prior is not None and not _preclick_no_action(prior):
                            raise ValueError("A previous action may have clicked @" + user + "; no automatic replay.")
                        expected_state = "still_following" if task == "unfollow" else "still_requested"
                        if not isinstance(observed, dict) or observed.get("status") != expected_state or not observed.get("observation_only") or not observed.get("read_only"):
                            raise ValueError("Run the read-only Review scan and verify current relationship before retry.")
                        try:
                            timestamp = time.strptime(observed["at"], "%Y-%m-%dT%H:%M:%SZ")
                            import calendar
                            age = time.time() - calendar.timegm(timestamp)
                        except (TypeError, KeyError, ValueError):
                            raise ValueError("Missing review observation timestamp.")
                        if age < -120 or age > 900:
                            raise ValueError("Review observation expired; re-inspect profiles before action.")
                # Check original exact-scope evidence BEFORE rebinding,
                # persisting a new cohort or opening any Instagram tab.
                previous = _read_json(self._base_for(owner, account, task), {})
                if any(user in previous and _invalid_saved_action_record(previous[user])
                       for user in targets):
                    raise ValueError(
                        "Selected targets have invalid saved action evidence. "
                        "Inspect the original journal read-only; never auto-retry.")
                # A NEW action cohort must never navigate already inspected targets,
                # even if the previous visit ended before any relationship click.
                # Only continuing the exact saved cohort may retry proven no-click.
                if not resume and pending_entry is None and task in ("unfollow", "cancel"):
                    visited = set(self._visited_usernames(owner, account, task, previous))
                    reused = sorted(set(targets) & visited)
                    if reused:
                        raise ValueError(
                            "New batch includes " + str(len(reused)) +
                            " previously opened/reviewed Instagram profile(s): @" +
                            ", @".join(reused[:5]) +
                            ". They are excluded from automatic new batches. "
                            "Use the saved-cohort Continue or an explicit read-only recheck.")
                self.owner, self.account, self.handle, self.task = owner, account, expected, task
                if not resume and not (task == "audit" and audit_source == "live_lists"):
                    if all((record := previous.get(user, {})).get("status") in ("ok", "already_not_following", "already_not_requested", "review", "error", "blocked")
                           and not _preclick_no_action(record)
                           for user in targets):
                        raise ValueError("No untouched profiles remain. Do not replay actions with uncertain outcomes.")
                self.targets = list(retry_selection) if retry_selection is not None else targets
                self.audit_source = audit_source
                self.review_only = False
                self.review_profiles_only = False
                self.history_recheck_mode = False
                if not resume:
                    self.continuing_batch = pending_entry is not None
                    if pending_entry:
                        self.active_batch_id = pending_entry["id"]
                    else:
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
                self.owner_profile_visits = 0
                if not resume:
                    self.skipped.clear()
                self.batch_size = count
                self.tab_flow = tab_flow
                self.max_count, self.window_minutes, self.min_delay_seconds = max_count, window, delay
                self.rest_minutes = rest
                # A newly authorized batch uses the owner's current visible
                # favorites. During an active run protection may only be added.
                # The UI's visible favorites list can be stale or incomplete after
                # a browser restart, an offline import or an account switch. Never
                # turn absence from that payload into an implicit "unprotect".
                # Both Unfollow and Cancel consult this owner/account-scoped guard
                # immediately before any click. Explicit removal requires its own
                # separate, owner-confirmed operation outside active jobs.
                saved_protected = self._protected()
                saved_protected.update(_users(data.get("protected", [])))
                _atomic_json(self._protection_file(), sorted(saved_protected))
                self.stop_event.clear()
                self.cancel_requested = False
                self.cancel_batch_id = ""
                self.status, self.message = "starting", "Opening Instagram in Chrome…"
                self.worker = threading.Thread(target=self._run_with_lease, args=(lease,), daemon=True)
                self.worker.start()
                started = True
                return self.snapshot()
        finally:
            if not started:
                lease.release()

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
            rows = {u: (_public_action_record(journal[u]) if u in journal else {})
                    for u in self.targets}
            historical_checked = len(self.historical_seen) if self.history_recheck_mode else 0
            historical_not_following = (
                len(self.historical_not_following_seen) if self.history_recheck_mode else 0)
            # Persisted action journal spans ALL earlier batches, not merely
            # the latest 30 selected targets. Send usernames only, no secrets.
            visited_usernames = self._visited_usernames(
                self.owner, self.account, self.task, journal) if self.owner and self.task else []
            attempted_usernames = sorted(u for u, record in journal.items()
                if valid_username(u) == u and
                (_invalid_saved_action_record(record) or
                 (record.get("status") in SAVED_ACTION_STATES
                  and not _preclick_no_action(record))))
            protected = self._protected() if self.owner else set()
            successful = sum(x.get("status") == "ok" for x in rows.values())
            already_not_following = sum(x.get("status") == "already_not_following"
                                        for x in rows.values())
            already_not_requested = sum(x.get("status") == "already_not_requested"
                                        for x in rows.values())
            reviewed = sum(x.get("status") in ("review", "error", "blocked") for x in rows.values())
            issues = [{"username": u, "status": rows[u].get("status", "pending"),
                       "issue": rows[u].get("issue", ""),
                       "message": rows[u].get("message", ""),
                       "safe_no_click": _preclick_no_action(rows[u]),
                       "click_phase": _public_click_phase(rows[u]),
                       "at": rows[u].get("at", "")}
                      for u in self.targets if rows[u].get("issue")]
            ignored = sum(u in protected for u in self.targets)
            skipped = sum(u in self.skipped for u in self.targets)
            completed_states = ("ok", "already_not_following", "already_not_requested", "review", "error", "blocked")
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
                    "already_not_following": already_not_following,
                    "already_not_requested": already_not_requested,
                    "errors": reviewed, "protected": ignored, "skipped": skipped,
                    "issue_count": len(issues), "issues": issues,
                    "attempted_usernames": attempted_usernames,
                    "visited_usernames": visited_usernames,
                    "remaining": pending,
                    "wait_seconds": max(0, int(self.wait_until-time.time()+0.999)) if self.wait_until else 0,
                    "open_review_tabs": list(self.open_review_tabs),
                    "audit_source": self.audit_source if self.task == "audit" else None,
                    "current_wait": dict(self.current_wait) if self.current_wait else None,
                    "max_action_tabs": MAX_ACTION_TABS,
                    "tab_flow": self.tab_flow,
                    "target_tabs_per_wave": action_tab_stage_limit(self.tab_flow),
                    "owner_profile_visits": self.owner_profile_visits,
                    "batch_size": self.batch_size,
                    "hourly_visit_limit": self.max_count,
                    "hourly_visit_window_minutes": self.window_minutes,
                    "review_only": self.review_only,
                    "cancel_requested": self.cancel_requested,
                    "continuing_batch": self.continuing_batch,
                    "history_recheck": self.history_recheck_mode,
                    "historical_checked": historical_checked,
                    "historical_not_following": historical_not_following,
                    "review_batch": (self._pending_review(self.owner, self.account, self.task)
                        if self.owner and self.account and self.task else None),
                    "rows": [{"username": u, "status": rows[u].get("status", "pending"),
                              "audit_relation": rows[u].get("audit_relation", ""),
                              "issue": rows[u].get("issue", ""),
                              "message": rows[u].get("message", ""),
                              "click_phase": _public_click_phase(rows[u]),
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

    def _persist_action_click_intent(self, journal, path, username, phase):
        """Write-ahead no-replay barrier; durable BEFORE any relationship click.

        The owner may lose power after Playwright sends a click but before its
        callback returns. Startup must therefore treat an orphan intent as
        *uncertain*, not a proven no-click and not a successful action.
        """
        if self.stop_event.is_set() or self.cancel_requested:
            raise ValueError("Owner stopped the batch before the relationship click; do not proceed.")
        if self.review_only or self.task not in ("unfollow", "cancel"):
            raise ValueError("Read-only jobs cannot stage a relationship click.")
        if not self.owner or not self.account or not self.active_batch_id:
            raise ValueError("Cannot stage an action without a saved owner-approved batch.")
        allowed = {
            "unfollow": {"relationship_control", "unfollow_menu",
                         "private_unfollow_confirmation"},
            "cancel": {"relationship_control", "cancel_request_confirmation"},
        }
        if phase not in allowed[self.task]:
            raise ValueError("Unknown Instagram click phase; refusing to act.")
        before = journal.get(username, {})
        if username in journal and _invalid_saved_action_record(before):
            raise ValueError("Invalid saved action evidence. No relationship click allowed.")
        if before.get("click_intent"):
            prior = before["click_intent"]
            if (prior.get("batch_id") != self.active_batch_id or
                    prior.get("task") != self.task):
                raise ValueError("Another action intent already exists. No replay allowed.")
            phases = list(prior.get("phases", []))
            attempt_history = list(before.get("attempt_history", []))
        else:
            if (before.get("status") in ("ok", "already_not_following",
                                         "already_not_requested", "review", "error",
                                         "blocked")
                    and not _preclick_no_action(before)):
                raise ValueError("Existing possible click must be reviewed; no replay.")
            phases = []
            attempt_history = list(before.get("attempt_history", []))
            if before.get("status"):
                attempt_history.append({k: v for k, v in before.items()
                                        if k != "attempt_history"})
        if phase in phases:
            raise ValueError("A relationship click phase was already armed; no replay.")
        phases.append(phase)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        pending = {
            "status": "review",
            "issue": "interrupted_action_uncertain",
            "message": ("A real Instagram click was prepared but its outcome "
                        "may be unknown. Do not retry automatically. "
                        "Inspect this target read-only."),
            "at": now,
            "click_intent": {
                "batch_id": self.active_batch_id,
                "task": self.task,
                "phase": phase,
                "phases": phases,
                "written_at": now,
                "requires_manual_review": True,
            },
            "attempt_history": attempt_history,
        }
        # Publishing only AFTER fsync+rename preserves the original evidence
        # when a disk error prevents the click.
        # Last-chance disk check before EACH click phase. A stale memory
        # snapshot must not erase a newly written result or uncertain intent.
        _assert_unchanged_action_journal(path, journal)
        updated = dict(journal)
        updated[username] = pending
        _atomic_json(path, updated)
        journal[username] = pending
        with self.lock:
            self.status = "running"
            self.message = ("@" + username + ": " + phase.replace("_", " ") +
                            " saved to durable action journal; verifying Instagram.")
        return pending

    def _record_owner_profile_visit(self):
        with self.lock:
            self.owner_profile_visits += 1

    def _run(self):
        browser = None
        _OWNER_PROFILE_PROBE.bound_session = None
        _OWNER_PROFILE_PROBE.report = self._record_owner_profile_visit
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
                login_started = time.monotonic()
                with self.lock:
                    self.status, self.message = "login", ("Waiting for manual Instagram sign-in "
                        "as @" + self.handle + " in the robot Chrome window. No actions clicked.")
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
                    # Instagram may complete manual login in a NEW tab while
                    # the original page remains at Login. Scan only the same
                    # robot Chrome context, never the system/browser profile.
                    verified_page, mismatched = _find_verified_owner_tab(
                        browser.pages, self.handle)
                    if mismatched:
                        with self.lock:
                            self.status, self.message = ("blocked",
                                "Robot Chrome includes a signed-in Instagram tab for @" +
                                mismatched + "; expected @" + self.handle +
                                ". Conflicting owner identity; no relationship action clicked.")
                        return
                    if verified_page is not None:
                        page = verified_page
                        break
                    if time.monotonic() - login_started >= PUBLIC_ROBOT_LOGIN_WAIT_SECONDS:
                        with self.lock:
                            self.status, self.message = ("blocked",
                                "Robot Chrome did not confirm Instagram login as @" +
                                self.handle + " within four minutes. Sign in manually "
                                "in that Chrome window and restart the saved batch; "
                                "no profiles were unfollowed or cancelled.")
                        return
                    self.stop_event.wait(3)
                if self.stop_event.is_set():
                    with self.lock: self.status = "paused"
                    return
                journal = self._journal()
                # Sign-in may take minutes after start() validated the cohort.
                # Recheck original disk evidence before opening any target tabs.
                if (not isinstance(journal, dict) or
                        any(u in journal and _invalid_saved_action_record(journal[u])
                            for u in self.targets)):
                    with self.lock:
                        self.status = "blocked"
                        self.message = (
                            "Saved Instagram action evidence is invalid or changed "
                            "during sign-in. No profile action was attempted. "
                            "Keep the original journal and inspect Issues before retrying.")
                    return
                path = self._base()
                visits_file, rests_file = history_path(path), batch_path(path)
                visits = load_history(visits_file)
                rests = load_batch_state(rests_file)
                action_tabs = ActionTabPool(browser) if self.task != "audit" else None
                live_snapshot = self.task == "audit" and self.audit_source == "live_lists"
                live_followers = live_following = None
                if live_snapshot:
                    # This is explicitly selected by the owner: read-only,
                    # same-origin requests via the already verified session.
                    # Both lists must be complete before any negative claim.
                    try:
                        try:
                            from .profile_lists_live import read_live_friendship_list
                        except ImportError:
                            from profile_lists_live import read_live_friendship_list
                        def progress_live(kind, index):
                            if self.stop_event.is_set():
                                raise ValueError("Owner stopped live list collection.")
                            with self.lock:
                                self.status = "running"
                                self.message = ("Reading live " + kind +
                                                " · page " + str(index) +
                                                " (read-only; no account changes)")
                        live_followers = read_live_friendship_list(
                            page, self.handle, "followers", on_page=progress_live)
                        live_following = read_live_friendship_list(
                            page, self.handle, "following", on_page=progress_live)
                    except Exception as exc:
                        with self.lock:
                            self.status = "paused" if self.stop_event.is_set() else "blocked"
                            self.message = ("Live Followers/Following option unavailable: " +
                                            str(exc)[:200] +
                                            " No inferred non-followbacks. "
                                            "The previous UI audit remains available.")
                        return
                stopped_for_review = False
                def stage_next_wave(start_index):
                    """Stage one target by default; ten only on explicit selection.

                    Visit pacing and rest apply to each navigation. Never
                    reallocate a tab while unresolved tabs from an older wave
                    remain visible for manual inspection. A sequential target
                    is processed immediately, BEFORE opening the next user.
                    """
                    nonlocal visits, rests, stopped_for_review
                    if not action_tabs or action_tabs.has_open_tabs():
                        return False
                    # Sequential avoids jumping back to the first tab after
                    # opening ten in Chrome. Legacy ten-tab staging stays opt-in.
                    stage_limit = action_tab_stage_limit(self.tab_flow)
                    stage_names = []
                    for candidate in self.targets[start_index:]:
                        previous = journal.get(candidate, {})
                        if (self._protected_for(candidate) or candidate in self.skipped
                                or (not self.review_only and
                                    _saved_journal_blocks_action(journal, candidate))):
                            continue
                        if len(stage_names) >= stage_limit:
                            break
                        if action_tabs.open(candidate) is None:
                            break
                        action_tabs.tabs[candidate]["status"] = "queued"
                        stage_names.append(candidate)
                    with self.lock:
                        self.open_review_tabs = action_tabs.overview()
                        self.message = (
                            "Opening the next Instagram profile sequentially."
                            if self.tab_flow == "sequential" else
                            "Preparing " + str(len(stage_names)) +
                            " Instagram profile tabs with saved visit spacing.")
                    for warm_user in stage_names:
                        if self.stop_event.is_set():
                            break
                        while not self.stop_event.is_set():
                            delay, wait_reason = action_wait_detail(
                                visits, rests, batch_size=self.batch_size,
                                rest_minutes=self.rest_minutes,
                                gap_seconds=self.min_delay_seconds)
                            if delay <= 0:
                                break
                            with self.lock:
                                self.status = "waiting"
                                self.wait_until = time.time() + delay
                                self.message = (
                                    "Waiting " + str(int(delay+0.999)) +
                                    " s (" + wait_reason + ") before @" + warm_user +
                                    (" (sequential)" if self.tab_flow == "sequential"
                                     else " (ten-tab preparation)"))
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
                        # Write-ahead profile-visit record prevents a later NEW
                        # cohort from re-opening a URL after a crash/forced close.
                        self._reserve_target_visit(warm_user)
                        try:
                            tab["page"].goto(
                                "https://www.instagram.com/" + warm_user + "/",
                                wait_until="domcontentloaded", timeout=30000)
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
                                self.batch_size if self.rest_minutes > 0 else 0,
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
                    return bool(stage_names) and not stopped_for_review

                for target_index, user in enumerate(
                        [] if stopped_for_review else self.targets):
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progress saved; select Resume."
                        return
                    # Safe pre-click login failures are retryable after a user
                    # explicitly starts another batch. Never replay ambiguous
                    # or potentially clicked results automatically.
                    previous = journal.get(user, {})
                    # Retry only proven no-click outcomes. Keep old evidence
                    # until the new outcome has been written, never delete
                    # historical failures just to unblock the queue.
                    if (self._protected_for(user) or user in self.skipped or
                        (not self.review_only and not live_snapshot and
                         _saved_journal_blocks_action(journal, user))):
                        if action_tabs and action_tabs.prepared(user) is not None:
                            action_tabs.record(user, "skipped", safe_no_click=True)
                            with self.lock:
                                self.open_review_tabs = action_tabs.overview()
                        continue
                    if action_tabs and action_tabs.prepared(user) is None:
                        if action_tabs.has_open_tabs():
                            with self.lock:
                                self.status = "review"
                                self.message = ("An unresolved tab remains from the previous "
                                                "ten-profile wave. Review it before the next "
                                                "wave; no uncertain click will be retried.")
                            stopped_for_review = True
                            break
                        if not stage_next_wave(target_index):
                            if stopped_for_review or self.stop_event.is_set():
                                break
                            continue
                    # The prepared target (one sequential tab or one of ten)
                    # has already paid for its initial visit. Do not charge again.
                    existing_tab = action_tabs.prepared(user) if action_tabs else None
                    if existing_tab is None and not live_snapshot:
                        while not self.stop_event.is_set():
                            delay, wait_reason = action_wait_detail(
                                visits, rests, batch_size=self.batch_size,
                                rest_minutes=self.rest_minutes,
                                gap_seconds=self.min_delay_seconds)
                            if delay <= 0: break
                            with self.lock:
                                self.status, self.wait_until = "waiting", time.time() + delay
                                self.message = ("Scheduled wait: " + str(int(delay+0.999)) +
                                                " s (" + wait_reason + ")")
                            self.stop_event.wait(min(delay, 2.0))
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progress saved; select Resume."
                        return
                    with self.lock:
                        self.wait_until = 0
                        self.current = user
                        self.status, self.message = "running", "Checking @" + user
                    if self._protected_for(user) or user in self.skipped:
                        if action_tabs and action_tabs.prepared(user) is not None:
                            action_tabs.record(user, "skipped", safe_no_click=True)
                            with self.lock:
                                self.open_review_tabs = action_tabs.overview()
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
                    elif live_snapshot:
                        current_visit_started = None  # No target profile visit occurred.
                    else:
                        visits = register_visit(visits_file, visits)
                        current_visit_started = visits[-1]

                    # Sequential: this is the only staged target.
                    # Legacy: focus previously staged ten tabs in turn.
                    if action_tabs and not work_page.is_closed():
                        work_page.bring_to_front()

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
                                               prepared_item.get("status") == "prefetched"),
                                allow_unacted_observation=(self.history_recheck_mode or
                                                            self.review_profiles_only),
                                distinguish_observation=self.review_profiles_only)
                        elif self.task == "audit" and live_snapshot:
                            if user.casefold() not in live_following:
                                result, relation = "review", "unverified"
                                details = ("Live Following does not include @" + user +
                                           "; this imported candidate is stale. "
                                           "No relationship action or non-followback inference.")
                            else:
                                relation = ("follows_you" if user.casefold() in live_followers
                                            else "not_following")
                                result = "ok"
                                details = ("Complete current Followers and Following lists "
                                           "confirm @" + user +
                                           (" follows you." if relation == "follows_you"
                                            else " does not follow you.") +
                                           " Read-only; no relationship click.")
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
                                on_wait=lambda phase, elapsed, limit:
                                    self._record_readiness(user, phase, elapsed, limit,
                                                           action_tabs),
                                preloaded=bool(prepared_item and
                                               prepared_item.get("status") == "prefetched"),
                                on_pre_click=lambda phase:
                                    self._persist_action_click_intent(
                                        journal, path, user, phase))
                    except Exception as exc:
                        if (self.cancel_requested and self.stop_event.is_set() and
                                str(exc).startswith("Owner stopped the batch before the relationship click;")):
                            # The guarded WAL proves no mutation was armed for
                            # this target. Keep it untouched, not an attempted
                            # click that would block safe future selection.
                            result, details = "skipped", "Owner cancelled before any click."
                        else:
                            result, details = "error", "The action could not be verified: " + str(exc)[:200]
                    finally:
                        if not live_snapshot and not (prepared_item and
                                prepared_item.get("visit_started_at") is not None):
                            visits = finish_visit(
                                visits_file, visits, started_at=current_visit_started)
                            rests = finish_batch_visit(
                                rests_file, rests,
                                self.batch_size if self.rest_minutes > 0 else 0,
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
                        # A disk edit during Chrome navigation (or after a
                        # possible click) is not permission to replace it.
                        # In particular leave durable uncertain-click evidence
                        # intact rather than writing a false success result.
                        _assert_unchanged_action_journal(path, journal)
                        previous_attempt = journal.get(user, {})
                        history = list(previous_attempt.get("attempt_history", []))
                        if previous_attempt.get("status"):
                            history.append({k: v for k, v in previous_attempt.items()
                                            if k != "attempt_history"})
                        journal[user] = {"status": result, "message": details,
                                         "audit_relation": relation, "issue": issue,
                                         "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                         "attempt_history": history,
                                         # Retain exact write-ahead phase trail
                                         # when the post-click result is saved.
                                         **({"click_intent": {
                                               **previous_attempt["click_intent"],
                                               "outcome_recorded": True,
                                               "outcome_status": result,
                                               "requires_manual_review": result not in
                                                   ("ok", "already_not_following",
                                                    "already_not_requested"),
                                            }} if previous_attempt.get("click_intent") else {})}
                        _atomic_json(path, journal)
                        self._discard_stale_recheck(user)
                    if action_tabs:
                        try:
                            # Read-only inspections cannot change relationships:
                            # release their tabs even when earlier history is
                            # uncertain. Original action journals stay intact.
                            safely_unclicked = self.review_only or _preclick_no_action(journal.get(user, {}))
                            action_tabs.record(user, result, safe_no_click=safely_unclicked)
                        except Exception:
                            # No relationship click is ever repeated to recover
                            # from a tab closing problem.
                            pass
                        with self.lock:
                            self.open_review_tabs = action_tabs.overview()
                    if result == "skipped":
                        continue
                    if result not in ("ok", "already_not_following", "already_not_requested"):
                        if self.review_only:
                            # Read-only automatic review should check the rest
                            # of the batch, not demand one-by-one manual work.
                            continue
                        # No-click preflight anomalies can be reviewed together after
                        # the batch. Potentially clicked/ambiguous results still stop.
                        if self.task == "audit" and details.startswith("Owner Followers page unavailable:"):
                            # One failed owner navigation affects the entire
                            # read-only batch; stop instead of repeating it.
                            with self.lock:
                                self.status, self.message = "blocked", details
                            stopped_for_review = True
                            break
                        if self.task == "audit" and result == "review":
                            continue
                        if _preclick_no_action(journal.get(user, {})):
                            # Safe no-click: record and move to the next target.
                            # A challenge or possibly clicked action is NOT safe.
                            continue
                        if _benign_preclick_issue(issue, journal.get(user, {})):
                            # A familiar issue label cannot override a durable
                            # possible-click barrier. Stop on every uncertain
                            # post-click outcome and preserve its tab/journal.
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
                                     else journal.get(u, {}).get("status"))
                                    not in ("ok", "already_not_following", "already_not_requested")
                                    for u in self.targets)
                    if not stopped_for_review:
                        self.status = "partial" if remaining else "complete"
                        self.message = (
                            "Historical re-audit finished: read-only observations saved. No action re-clicked or approved."
                            if self.history_recheck_mode else
                            ("Batch reviewed: some profiles require manual verification."
                             if remaining else "Batch complete; results saved."))
                # Prefetch-only tabs never had action clicks. Do not trap the
                # robot in manual-review mode just because a later unvisited
                # target is still prefetched in one of the 10 open slots.
                if action_tabs:
                    action_tabs.close_unacted_prefetches()
                    with self.lock:
                        self.open_review_tabs = action_tabs.overview()
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
            _OWNER_PROFILE_PROBE.bound_session = None
            _OWNER_PROFILE_PROBE.report = None
            with self.lock:
                self.current, self.wait_until, self.current_wait = "", 0, None
            if browser:
                try: browser.close()
                except Exception: pass
            with self.lock:
                self.open_review_tabs = []
                if self.cancel_requested:
                    try:
                        self._finish_owner_cancel_locked()
                    except Exception as exc:
                        self.cancel_requested = False
                        self.cancel_batch_id = ""
                        self.status = "blocked"
                        self.message = ("Chrome stopped, but the saved cohort could not be "
                                        "archived: " + str(exc)[:180] +
                                        ". Review the original journal before another batch.")
