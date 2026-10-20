#!/usr/bin/env python3
"""Owner-triggered REAL Instagram DOM diagnosis for the isolated Windows Developer Edition.

ONLY read-only profile navigation and DOM inspection. The owner signs in manually
inside the Developer Chrome profile. No relationship clicks, CAPTCHA bypass,
credentials, screenshot, raw username, HTML or Instagram network trace export.
Results are bounded aggregate codes; original production journals are NEVER edited.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import threading
import time
from urllib.parse import urlparse

from profile_counts_robot import valid_username
from profile_counts_instagram import (
    challenge_detected, preserve_instagram_auth_page, signed_in_handle,
    verify_selected_owner_profile,
)
from profile_actions import (
    _follow_state, _profile_relationship_control, _verified_action_owner,
    _wait_for_target_profile_shell,
)

LIVE_CODES = frozenset({
    "FOLLOWING_VISIBLE", "NOT_FOLLOWING_VISIBLE", "REQUESTED_VISIBLE",
    "NO_REQUEST_VISIBLE", "NOW_FOLLOWING", "RELATIONSHIP_UNKNOWN",
    "TARGET_IDENTITY_UNVERIFIED", "OWNER_IDENTITY_UNVERIFIED",
    "LOGIN_REQUIRED", "LOGIN_ACCOUNT_MISMATCH", "SECURITY_CHALLENGE",
    "PROFILE_REDIRECT", "PROFILE_LOAD_TIMEOUT", "DOM_PROBE_EXCEPTION",
    "BROWSER_START_FAILED", "STOPPED_BY_OWNER",
})
ALLOWED_TASKS = frozenset({"unfollow", "cancel"})
MAX_SAMPLES = 5
SCAN_LABELS = {
    "FOLLOWING_VISIBLE": "Exact target's Following control found; unfollow control locator is available.",
    "NOT_FOLLOWING_VISIBLE": "Exact target consistently shows Follow; no Unfollow needed at observation time.",
    "REQUESTED_VISIBLE": "Exact target's Requested control found; cancellation entry is available.",
    "NO_REQUEST_VISIBLE": "Exact target consistently shows Follow; no pending request visible at observation time.",
    "NOW_FOLLOWING": "Exact target shows Following; an old pending request may have been accepted.",
    "RELATIONSHIP_UNKNOWN": "No unique action control was verified on the target; inspect Instagram's live profile layout.",
    "TARGET_IDENTITY_UNVERIFIED": "Profile heading or username could not be proven; no action attempted.",
    "OWNER_IDENTITY_UNVERIFIED": "Logged-in owner could not be proven; no action attempted.",
    "LOGIN_REQUIRED": "Sign in manually in the Developer Chrome window, then re-run.",
    "LOGIN_ACCOUNT_MISMATCH": "Chrome account differs from the workspace selected in InstaCleaner.",
    "SECURITY_CHALLENGE": "Instagram requires manual security verification; stopped without bypass.",
    "PROFILE_REDIRECT": "Instagram redirected away from the exact target.",
    "PROFILE_LOAD_TIMEOUT": "Instagram target profile did not finish rendering.",
    "DOM_PROBE_EXCEPTION": "A bounded DOM inspection failed; inspect selectors offline.",
    "BROWSER_START_FAILED": "Chrome or the persistent Developer browser profile could not be opened.",
    "STOPPED_BY_OWNER": "The owner stopped the read-only inspection.",
}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _journal_path(root: Path, owner: str, account: str, task: str):
    identity = "\0".join((owner, account, task))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
    return root / ("instagram-actions-" + digest + ".json")


def select_real_issues(root: Path, owner: str, account: str, task: str, limit: int):
    """Sample genuine unresolved owner records, never arbitrary third-party suggestions."""
    path = _journal_path(Path(root), owner, account, task)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 5_000_000:
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return []
    if not isinstance(raw, dict):
        return []
    eligible = [
        (user, record) for user, record in raw.items()
        if isinstance(user, str) and valid_username(user) == user
        and isinstance(record, dict) and record.get("status") in ("review", "blocked", "error")
    ]
    eligible.sort(key=lambda pair: str(pair[1].get("at") or ""), reverse=True)
    return [user for user, _ in eligible[:limit]]


def inspect_real_profile(page, username, task, expected_handle):
    """Use real action selectors, but NEVER .click() or mutate a relationship."""
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "SECURITY_CHALLENGE"
    current = urlparse(page.url)
    if current.hostname not in ("instagram.com", "www.instagram.com") or (
            current.path.strip("/").casefold() != username.casefold()):
        return "PROFILE_REDIRECT"
    if not _wait_for_target_profile_shell(page, username, timeout_ms=8000):
        return "PROFILE_LOAD_TIMEOUT"
    if not _verified_action_owner(page, expected_handle):
        return "OWNER_IDENTITY_UNVERIFIED"
    try:
        wanted = ([r"Following", r"Siguiendo"] if task == "unfollow" else
                  [r"Requested", r"Solicitado", r"Solicitada"])
        if _profile_relationship_control(page, username, wanted) is not None:
            return "FOLLOWING_VISIBLE" if task == "unfollow" else "REQUESTED_VISIBLE"
        # An HTML "Follow" in a suggested user sidebar is NOT proof. This
        # helper independently requires exact target identity and a hero control.
        if _follow_state(page, username):
            page.wait_for_timeout(350)
            if _follow_state(page, username) and (
                    _profile_relationship_control(page, username, wanted) is None):
                return "NOT_FOLLOWING_VISIBLE" if task == "unfollow" else "NO_REQUEST_VISIBLE"
        if task == "cancel" and _profile_relationship_control(
                page, username, [r"Following", r"Siguiendo"]) is not None:
            return "NOW_FOLLOWING"
        return "RELATIONSHIP_UNKNOWN"
    except Exception:
        return "DOM_PROBE_EXCEPTION"


class DeveloperLiveProbe:
    """One visible, isolated Chrome worker at a time; privacy-safe status export."""

    def __init__(self, source_journals: Path, browser_dir: Path):
        self.root = Path(source_journals)
        self.browser_dir = Path(browser_dir)
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.worker = None
        self.scope = None
        self.state = "idle"
        self.phase = "not_started"
        self.total = 0
        self.checked = 0
        self.codes = Counter()
        self.events = []
        self.started_at = None
        self.finished_at = None

    def _public(self):
        return {
            "schema": "igc-developer-live-instagram-readonly-v1",
            "source": "owner_installed_developer_chrome_real_instagram",
            "evidence": "real_visible_dom_no_relationship_click",
            "state": self.state,
            "phase": self.phase,
            "total": self.total,
            "checked": self.checked,
            "counts": dict(sorted(self.codes.items())),
            "events": list(self.events),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "contains_usernames": False,
            "limitations": [
                "Real signed-in Instagram DOM is inspected; no Unfollow or Cancel Request is clicked.",
                "Visible Follow or Requested state is a point-in-time observation, not evidence of a prior action succeeding.",
                "A failing selector does not prove that an Instagram relationship changed.",
                "The Developer Chrome session is independent; log in to it manually.",
            ],
        }

    def snapshot(self):
        with self.lock:
            return self._public()

    def start(self, data):
        owner, account = str(data.get("owner") or "").strip(), str(data.get("account") or "").strip()
        task = str(data.get("task") or "")
        handle = valid_username(data.get("expected_handle") or "")
        number = data.get("max_profiles", 3)
        if (not owner or not account or len(owner) > 200 or len(account) > 120
                or task not in ALLOWED_TASKS or not handle
                or type(number) is not int or not 1 <= number <= MAX_SAMPLES):
            raise ValueError("Select a valid signed-in owner, Instagram account, action and 1–5 samples.")
        if data.get("confirmation") != "READ_ONLY_REAL_INSTAGRAM":
            raise ValueError("Real Chrome inspection requires explicit owner confirmation.")
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("A real Instagram Developer probe is already in progress.")
            targets = select_real_issues(self.root, owner, account, task, number)
            if not targets:
                raise ValueError("No saved failed robot records for this account and action. Do not invent test targets.")
            self.stop_event.clear()
            self.state = "starting"
            self.phase = "opening_isolated_chrome"
            self.total, self.checked = len(targets), 0
            self.codes, self.events = Counter(), []
            self.started_at, self.finished_at = _now(), None
            self.scope = (owner, account, task)
            self.worker = threading.Thread(target=self._run, args=(targets, task, handle), daemon=True)
            self.worker.start()
            return self._public()

    def stop(self):
        self.stop_event.set()
        with self.lock:
            return self._public()

    def _add(self, index, code):
        if code not in LIVE_CODES:
            code = "DOM_PROBE_EXCEPTION"
        with self.lock:
            self.codes[code] += 1
            self.events.append({"sample": index, "code": code,
                                "meaning": SCAN_LABELS[code], "timestamp": _now()})
            self.checked += 1

    def _run(self, targets, task, handle):
        browser = None
        try:
            from playwright.sync_api import sync_playwright
            self.browser_dir.mkdir(parents=True, exist_ok=True)
            with sync_playwright() as pw:
                opts = {"user_data_dir": str(self.browser_dir),
                        "headless": False, "viewport": {"width": 1180, "height": 860}}
                if getattr(sys, "frozen", False):
                    browser = pw.chromium.launch_persistent_context(channel="chrome", **opts)
                else:
                    try:
                        browser = pw.chromium.launch_persistent_context(**opts)
                    except Exception:
                        browser = pw.chromium.launch_persistent_context(channel="chrome", **opts)
                pages = [p for p in browser.pages if not p.is_closed()]
                page = next((p for p in pages if preserve_instagram_auth_page(p)),
                            pages[0] if pages else browser.new_page())
                if not preserve_instagram_auth_page(page):
                    page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
                deadline = time.monotonic() + 75
                authenticated = False
                while not self.stop_event.is_set() and time.monotonic() < deadline:
                    if challenge_detected(page):
                        self._add(0, "SECURITY_CHALLENGE")
                        break
                    signed = signed_in_handle(page)
                    if signed and signed.casefold() != handle.casefold():
                        self._add(0, "LOGIN_ACCOUNT_MISMATCH")
                        break
                    if signed and signed.casefold() == handle.casefold():
                        authenticated = True
                        break
                    with self.lock:
                        self.state, self.phase = "waiting_for_login", "login_manually_in_developer_chrome"
                    self.stop_event.wait(3)
                if not authenticated:
                    if not self.codes and not self.stop_event.is_set():
                        self._add(0, "LOGIN_REQUIRED")
                    return
                with self.lock:
                    self.state, self.phase = "running", "read_only_profile_checks"
                for i, user in enumerate(targets, 1):
                    if self.stop_event.is_set():
                        break
                    try:
                        page.goto("https://www.instagram.com/" + user + "/",
                                  wait_until="domcontentloaded", timeout=45000)
                        code = inspect_real_profile(page, user, task, handle)
                    except Exception:
                        code = "DOM_PROBE_EXCEPTION"
                    self._add(i, code)
                    if code in ("SECURITY_CHALLENGE", "OWNER_IDENTITY_UNVERIFIED",
                                "PROFILE_REDIRECT"):
                        break  # Do not continue navigating when trust is uncertain.
                    self.stop_event.wait(1)
        except Exception:
            if not self.stop_event.is_set():
                self._add(0, "BROWSER_START_FAILED")
        finally:
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass
            with self.lock:
                self.state = "stopped" if self.stop_event.is_set() else "complete"
                self.phase = "done_no_actions_clicked"
                self.finished_at = _now()
