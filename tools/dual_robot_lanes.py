"""Two independent, owner-scoped Chrome robot lanes: identity supervision only.

Launches two concurrently running Playwright browser contexts with separate
persistent Chrome profile directories. Each lane proves the signed-in owner
from visible Instagram UI; neither lane can execute relationship mutations.
ActionRobot's existing exclusive WAL lease remains intact until the separate
two-action-worker implementation is proven and explicitly owner-accepted.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

from dual_chrome_sessions import DualChromeSessions, APP_OWNER
from profile_counts_instagram import (
    challenge_detected, preserve_instagram_auth_page, signed_in_handle,
)

LOGIN_TIMEOUT_SECONDS = 180


class DualRobotLanes:
    def __init__(self, sessions: DualChromeSessions, *, runner=None):
        self.sessions = sessions
        self.lock = threading.RLock()
        self.runner = runner or self._supervise
        self.owner = None
        self.lanes = {}
        self.started_at = None

    def _validate_pair(self, data):
        if not isinstance(data, dict):
            raise ValueError("Select two registered Instagram workspaces.")
        owner = data.get("owner")
        if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
            raise ValueError("Sign in to InstaCleaner before starting robot lanes.")
        left = self.sessions._workspace(data.get("primary"))
        right = self.sessions._workspace(data.get("secondary"))
        if left[0] == right[0] or left[1] == right[1]:
            raise ValueError("Dual robot lanes require two different Instagram accounts.")
        if (data.get("read_only_consent") is not True
                or data.get("acknowledge_no_actions") is not True
                or data.get("confirmation") != "dual-robots:" + left[0] + ":" + right[0]):
            raise ValueError("Approve both exact accounts for read-only verification; no actions.")
        return owner, left, right

    def _report(self, account, state, message, *, verified=False):
        with self.lock:
            lane = self.lanes.get(account)
            if lane is None:
                return
            lane["state"] = state
            lane["message"] = message
            lane["verified"] = bool(verified)
            lane["updated_at"] = time.time()

    def start_pair(self, data):
        owner, first, second = self._validate_pair(data)
        with self.lock:
            if any(lane["thread"].is_alive() for lane in self.lanes.values()):
                raise ValueError("Stop the previous supervised Chrome robot lanes first.")
            if self.owner is not None and self.owner != owner:
                raise ValueError("Another app owner has an existing supervised session; restart InstaCleaner.")
            self.owner = owner
            self.started_at = time.time()
            self.lanes = {}
            for account, handle in (first, second):
                # Same account never shares a browser profile with the other lane.
                folder = self.sessions.directory(owner, account)
                ev = threading.Event()
                lane = dict(account=account, expected_handle=handle,
                            session_dir=folder, stop=ev, thread=None,
                            state="starting", verified=False,
                            message="Starting an isolated Chrome session.",
                            updated_at=self.started_at)
                self.lanes[account] = lane
            if self.lanes[first[0]]["session_dir"] == self.lanes[second[0]]["session_dir"]:
                self.lanes.clear()
                raise ValueError("The two robot browsers have colliding sessions.")
            for account in (first[0], second[0]):
                thread = threading.Thread(
                    target=self._run_guarded, args=(account,), daemon=True,
                    name="igc-readonly-robot-" + account[:20])
                self.lanes[account]["thread"] = thread
            try:
                for account in (first[0], second[0]):
                    self.lanes[account]["thread"].start()
            except Exception:
                for lane in self.lanes.values():
                    lane["stop"].set()
                raise
            return self._snapshot_locked()

    def _run_guarded(self, account):
        with self.lock:
            lane = self.lanes[account]
            folder, handle, stop = lane["session_dir"], lane["expected_handle"], lane["stop"]
        try:
            self.runner(account, handle, folder, stop)
        except Exception as exc:
            self._report(account, "blocked",
                         "This Chrome lane did not verify its Instagram identity. "
                         "Close its other Chrome windows if the profile is in use. "
                         "No actions were performed: " + str(exc)[:110])
        finally:
            with self.lock:
                lane = self.lanes.get(account)
                if lane is not None:
                    if lane["stop"].is_set():
                        lane["state"], lane["message"] = "stopped", "Stopped by owner; no actions performed."
                    elif lane["state"] not in ("blocked", "stopped"):
                        lane["state"], lane["message"] = "closed", "Chrome closed; no actions performed."
                    lane["verified"] = False
                    lane["updated_at"] = time.time()

    def _supervise(self, account, handle, folder: Path, stop: threading.Event):
        from playwright.sync_api import sync_playwright
        folder.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as pw:
            # Browser directories here are NOT the old shared action robot's
            # Chrome profile. If manually opened Chrome already holds one,
            # Chromium must fail safely; never borrow a different profile.
            context = pw.chromium.launch_persistent_context(
                user_data_dir=str(folder), channel="chrome",
                headless=False, viewport={"width": 1180, "height": 860})
            try:
                pages = [p for p in context.pages if not p.is_closed()]
                page = next((p for p in pages if preserve_instagram_auth_page(p)),
                            pages[0] if pages else context.new_page())
                if not preserve_instagram_auth_page(page):
                    page.goto("https://www.instagram.com/",
                              wait_until="domcontentloaded", timeout=45000)
                deadline = time.monotonic() + LOGIN_TIMEOUT_SECONDS
                while not stop.is_set():
                    tabs = [p for p in context.pages if not p.is_closed()]
                    if not tabs:
                        self._report(account, "closed", "Chrome window closed; no actions performed.")
                        return
                    if any(challenge_detected(p) for p in tabs):
                        self._report(account, "blocked",
                                     "Instagram requires a security challenge. "
                                     "Stop and verify manually; no automatic retries.")
                        return
                    handles = set()
                    for p in tabs:
                        observed = signed_in_handle(p)
                        if observed:
                            handles.add(observed.casefold())
                    if handles - {handle.casefold()}:
                        self._report(account, "blocked",
                                     "Wrong Instagram account detected in this Chrome lane. "
                                     "Expected @" + handle + ". No actions performed.")
                        return
                    if handle.casefold() in handles:
                        self._report(account, "verified",
                                     "Visibly verified @" + handle +
                                     " in its isolated Chrome session (READ ONLY).",
                                     verified=True)
                    elif time.monotonic() >= deadline:
                        self._report(account, "blocked",
                                     "Owner login was not verified within the time limit; no actions.")
                        return
                    else:
                        self._report(account, "login",
                                     "Sign in manually to @" + handle +
                                     " in THIS isolated Chrome window.",
                                     verified=False)
                    stop.wait(1)
            finally:
                context.close()

    def _snapshot_locked(self):
        return {
            "status": ("running" if any(
                x["thread"] is not None and x["thread"].is_alive()
                for x in self.lanes.values()) else "idle"),
            "owner": self.owner,
            "two_lanes": len(self.lanes) == 2,
            "actions_enabled": False,
            "mode": "identity_verification_only",
            "lanes": [
                {"account": lane["account"],
                 "expected_handle": lane["expected_handle"],
                 "state": lane["state"],
                 "message": lane["message"],
                 "verified": lane["verified"],
                 "running": lane["thread"] is not None and lane["thread"].is_alive()}
                for lane in self.lanes.values()
            ],
        }

    def snapshot(self, owner):
        with self.lock:
            if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
                raise ValueError("Invalid app owner for the dual Chrome robot status.")
            if self.owner is not None and owner != self.owner:
                raise ValueError("Cannot read another app owner's Chrome robot lanes.")
            return self._snapshot_locked()

    def stop_pair(self, data):
        if not isinstance(data, dict):
            raise ValueError("Invalid dual Chrome robot stop request.")
        owner = data.get("owner")
        if (not isinstance(owner, str) or not APP_OWNER.fullmatch(owner)
                or data.get("confirmation") != "dual-robots-stop:" + owner):
            raise ValueError("Explicitly confirm the exact owner before stopping both lanes.")
        with self.lock:
            if self.owner is not None and owner != self.owner:
                raise ValueError("Cannot stop another user's Chrome robot lanes.")
            for lane in self.lanes.values():
                lane["stop"].set()
            return self._snapshot_locked()

    def shutdown(self):
        with self.lock:
            lanes = list(self.lanes.values())
            for lane in lanes:
                lane["stop"].set()
        for lane in lanes:
            thread = lane["thread"]
            if thread is not None and thread.is_alive():
                thread.join(timeout=8)
