#!/usr/bin/env python3
"""Loopback-only controller for the visible Instagram browser robot.

Run on the user's PC. Opens IG Cleaner with a session-only capability token in
the FILE URL fragment. Does not expose an Internet listener or store passwords.
"""
from __future__ import annotations

import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import sys
import threading
import time
import webbrowser

from profile_counts_instagram import (signed_in_handle, challenge_detected, safe_to_probe_owner_from_home, preserve_instagram_auth_page, read_following_visible,
                                      write_following_cache, read_following_cache, reconcile_following_discovery,
                                      verify_selected_owner_profile, FollowingControlUnavailable)
from profile_actions import ActionRobot, ProtectedBatchCollision
from live_relationship_snapshot import LiveRelationships
from robot_interlock import ActionSessionBusy
from dual_chrome_sessions import DualChromeSessions
from dual_robot_lanes import DualRobotLanes

from profile_counts_robot import collect_visible_counts, iso_now, read_results, save_results, valid_username, valid_saved_measurement
from profile_counts_audit import (audit_cycle_path, dated_history_path, new_cycle,
                                  resume_cycle, mark_attempt, append_dated_reading,
                                  seed_latest_readings, read_dated_page)
from profile_counts_pacing import (check_pacing, history_path, load_history,
                                   register_visit, finish_visit, wait_required,
                                   DEFAULT_COUNT, DEFAULT_WINDOW_MINUTES, DEFAULT_DELAY_SECONDS,
                                   check_batch_rest, batch_path, load_batch_state,
                                   batch_wait, finish_batch_visit)

MAX_REQUEST = 900_000
MAX_IMPORT_CHUNK = 2_000  # transport limit per request, not an account-size limit


class Collector:
    def __init__(self, data_dir: Path, session_dir: Path):
        self.data_dir = data_dir
        self.session_dir = session_dir
        self.lock = threading.RLock()
        self.browser_admission = threading.RLock()  # shared across all Chrome robots
        self.login_ready = threading.Event()
        self.stop_signal = threading.Event()
        self.pause_requested = False
        self.worker = None
        self.status = "idle"
        self.message = "No active job"
        self.progress = 0
        self.total = 0
        self.owner = ""
        self.account = ""
        self.usernames = []
        self.max_per_window = DEFAULT_COUNT
        self.window_minutes = DEFAULT_WINDOW_MINUTES
        self.min_delay_seconds = DEFAULT_DELAY_SECONDS
        self.pause_every = 0
        self.pause_minutes = 0.0
        self.wait_until = 0
        self.autonomous = False
        self.expected_handle = ""
        self.detected_handle = ""
        self.discovery_complete = False
        self.discover_following = False
        self.queue_source = ""
        self.current_profile = ""
        self.actions = None
        self.live_relationships = None
        self.import_stage = None  # ephemeral, owner-scoped upload until commit
        self.audit_mode = "first_pass"
        self.audit_cycle = None

    def begin_import(self, request):
        """Prepare an atomic user-list transfer; never replace a running job."""
        owner = str(request.get("owner") or "").strip()
        account = str(request.get("account") or "").strip()
        total = request.get("total")
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("Select a valid account before uploading.")
        if type(total) is not int or total < 1:
            raise ValueError("Import total must be a positive integer.")
        with self.lock:
            if (self.worker and self.worker.is_alive()) or (
                self.actions and self.actions.worker and self.actions.worker.is_alive()
            ):
                raise ValueError("Pause the active Instagram robot before uploading another job.")
            transfer = secrets.token_urlsafe(20)
            self.import_stage = dict(owner=owner, account=account, total=total,
                                     transfer=transfer, usernames=[], seen=set())
            return {"transfer": transfer, "received": 0, "total": total}

    def append_import(self, request):
        """Bound a single HTTP request, not the overall relationship data size."""
        users = request.get("usernames")
        if not isinstance(users, list) or not 1 <= len(users) <= MAX_IMPORT_CHUNK:
            raise ValueError("Send a chunk of 1 to 2,000 usernames.")
        if any(not isinstance(u, str) or not valid_username(u) for u in users):
            raise ValueError("Import contains invalid profile usernames.")
        owner = str(request.get("owner") or "")
        account = str(request.get("account") or "")
        with self.lock:
            stage = self.import_stage
            if (not stage or stage["owner"] != owner or stage["account"] != account or
                not secrets.compare_digest(stage["transfer"], str(request.get("transfer") or ""))):
                raise ValueError("Import session or account mismatch.")
            if request.get("offset") != len(stage["usernames"]):
                raise ValueError("Import chunk is out of order; retry from the confirmed offset.")
            if len(stage["usernames"]) + len(users) > stage["total"]:
                raise ValueError("Import chunk exceeds the declared total.")
            # Reject an entire invalid chunk atomically; never partially append.
            normalized = [valid_username(u) for u in users]
            if len(set(normalized)) != len(normalized) or any(
                name in stage["seen"] for name in normalized
            ):
                raise ValueError("Duplicate username in imported chunks.")
            stage["seen"].update(normalized)
            stage["usernames"].extend(normalized)
            return {"received": len(stage["usernames"]), "total": stage["total"]}

    def result_path(self):
        # No owner/usernames in filenames or URL paths.
        identity = self.owner + "\0" + self.account
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("profile-counts-" + digest + ".csv")

    def followings_path(self):
        return self.result_path().with_suffix(".following.json")

    def auto_start(self, request: dict):
        """Called once by the local Desktop client. No CSV or start click needed."""
        owner = str(request.get("owner") or "").strip()
        account = str(request.get("account") or "").strip()
        if not owner or not account or len(owner)>200 or len(account)>120:
            raise ValueError("Select a valid IG Cleaner login and Instagram workspace.")
        expected = valid_username(request.get("expected_handle") or "")
        if request.get("expected_handle") and not expected:
            raise ValueError("The expected Instagram username is invalid.")
        # Prefer the owner's already imported Following. Its list is source
        # data for this read-only counts scan, never proof of current followback.
        raw_users = request.get("usernames", [])
        if not isinstance(raw_users, list):
            raise ValueError("Imported usernames must be an array.")
        transfer = request.get("transfer")
        use_stage = request.get("use_staged_import") is True
        discover = request.get("discover_following") is True
        if use_stage and (raw_users or discover):
            raise ValueError("Use either the staged import or optional browser discovery.")
        normalized = list(dict.fromkeys(
            u for value in raw_users if (u := valid_username(value))
        ))
        if discover and normalized:
            raise ValueError("Choose imported profiles OR optional Instagram Following discovery.")
        # Pacing is retained internally; novice users do not need to see settings.
        pacing = dict(max_per_window=request.get("max_per_window", DEFAULT_COUNT),
                      window_minutes=request.get("window_minutes", DEFAULT_WINDOW_MINUTES),
                      min_delay_seconds=request.get("min_delay_seconds", DEFAULT_DELAY_SECONDS))
        count, minutes, delay = check_pacing(
            pacing["max_per_window"], pacing["window_minutes"], pacing["min_delay_seconds"])
        rest_count, rest_minutes = check_batch_rest(request.get("pause_every", 0),
                                                     request.get("pause_minutes", 0))
        with self.browser_admission, self.lock:
            if self.actions and self.actions.worker and self.actions.worker.is_alive():
                raise ValueError("An Instagram action robot is running. Pause it before Profile Counts.")
            if self.live_relationships and self.live_relationships.worker and self.live_relationships.worker.is_alive():
                raise ValueError("Pause the live Followers/Following verification before Profile Counts.")
            if use_stage:
                stage = self.import_stage
                if (not stage or stage["owner"] != owner or stage["account"] != account or
                    not secrets.compare_digest(stage["transfer"], str(transfer or "")) or
                    len(stage["usernames"]) != stage["total"]):
                    raise ValueError("Imported profile upload is incomplete or belongs to another account.")
                normalized = list(stage["usernames"])
            if not discover and not normalized:
                raise ValueError("Import Following profiles first or explicitly choose optional discovery.")
            if self.worker and self.worker.is_alive():
                if owner != self.owner or account != self.account:
                    raise ValueError("Another Instagram account is currently active. Accounts will not be mixed.")
                return self.snapshot()
            if self.status in ("paused", "pausing") and not request.get("resume_requested"):
                if owner != self.owner or account != self.account:
                    raise ValueError("Another account is paused; profiles will not be mixed.")
                return self.snapshot()
            if use_stage:
                self.import_stage = None  # consumed only on successful job acceptance
            self.pause_requested = False
            self.owner, self.account = owner, account
            self.expected_handle = expected or ""
            audit_mode = request.get("audit_mode", "first_pass")
            if audit_mode not in ("first_pass", "oldest_first"):
                raise ValueError("Unsupported Profile Counts audit mode.")
            if audit_mode == "oldest_first" and discover:
                raise ValueError("Re-audits require the already imported Following list.")
            self.autonomous = True
            self.audit_mode = audit_mode
            self.audit_cycle = None
            self.detected_handle = ""
            self.discover_following = discover
            self.queue_source = "instagram" if discover else "imported"
            self.discovery_complete = False
            self.usernames = [] if discover else normalized
            self.total = len(self.usernames)
            saved = read_results(self.result_path())
            # One-time, additive legacy migration: imported prior successes
            # appear in dated history before any later recheck can change them.
            seed_latest_readings(dated_history_path(self.result_path()), saved)
            if self.audit_mode == "oldest_first":
                cycle_file = audit_cycle_path(self.result_path())
                # A user-reopened Windows session continues an unfinished
                # cycle with its original frozen order. A completed cycle
                # starts a genuinely new oldest-first pass on explicit click.
                previous = (resume_cycle(cycle_file, self.usernames)
                            if cycle_file.is_file() else None)
                if request.get("resume_requested") and previous is None:
                    raise ValueError("No previous re-audit cycle exists to resume.")
                if request.get("resume_requested") and previous is not None:
                    self.audit_cycle = previous
                elif previous and len(previous["done"]) < len(previous["targets"]):
                    self.audit_cycle = previous
                else:
                    self.audit_cycle = new_cycle(cycle_file, self.usernames, saved)
                self.progress = len(self.audit_cycle["done"])
            else:
                self.progress = sum(valid_saved_measurement(saved.get(u)) for u in self.usernames)
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = rest_count, rest_minutes
            self.wait_until = 0
            self.current_profile = ""
            self.message = ("Resuming "+str(len(self.audit_cycle["done"]))+"/"+
                            str(len(self.audit_cycle["targets"]))+" dated re-audit profiles..."
                            if self.audit_cycle and self.audit_cycle["done"] else
                            "Opening Instagram to verify your session...")
            self.status = "starting"
            self.stop_signal.clear()
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def start(self, request: dict, load_only: bool = False):
        usernames = request.get("usernames")
        if not isinstance(usernames, list) or not usernames:
            raise ValueError("Provide at least one valid profile.")
        normalized, seen = [], set()
        for user in usernames:
            clean = valid_username(user)
            if not clean or clean in seen:
                continue
            normalized.append(clean)
            seen.add(clean)
        if not normalized:
            raise ValueError("No valid usernames were found.")
        owner = str(request.get("owner") or "").strip()
        account = str(request.get("account") or "").strip()
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("An Insta Cleaner owner and active Instagram workspace are required.")
        count, minutes, delay = check_pacing(
            request.get("max_per_window", request.get("per_hour", DEFAULT_COUNT)),
            request.get("window_minutes", DEFAULT_WINDOW_MINUTES),
            request.get("min_delay_seconds", DEFAULT_DELAY_SECONDS),
        )
        pause_every, pause_minutes = check_batch_rest(
            request.get("pause_every", 0),
            request.get("pause_minutes", 0),
        )
        with self.browser_admission, self.lock:
            if self.actions and self.actions.worker and self.actions.worker.is_alive():
                raise ValueError("Pause the active Instagram action robot before starting Profile Counts.")
            if self.live_relationships and self.live_relationships.worker and self.live_relationships.worker.is_alive():
                raise ValueError("Pause the live Followers/Following verification before Profile Counts.")
            if self.worker and self.worker.is_alive():
                raise ValueError("A collection is already running. Stop it before starting another.")
            self.owner, self.account, self.usernames = owner, account, normalized
            self.autonomous = False
            self.audit_mode = "first_pass"
            self.audit_cycle = None
            self.discover_following = False
            self.queue_source = "imported"
            self.detected_handle = ""
            self.discovery_complete = False
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = pause_every, pause_minutes
            self.wait_until = 0
            self.current_profile = ""
            saved = read_results(self.result_path())
            seed_latest_readings(dated_history_path(self.result_path()), saved)
            self.total = len(normalized)
            self.progress = sum(valid_saved_measurement(saved.get(u)) for u in normalized)
            self.message = ("Saved results restored; select Start to continue."
                            if load_only else "Opening visible browser...")
            self.status = "idle" if load_only else "starting"
            self.stop_signal.clear()
            self.pause_requested = False
            self.login_ready.clear()
            if not load_only:
                self.worker = threading.Thread(target=self._run, daemon=True)
                self.worker.start()
            return self.snapshot()

    def _update(self, status: str, message: str, progress=None):
        with self.lock:
            self.status, self.message = status, message
            if progress is not None:
                self.progress = progress

    def _run(self):
        browser = None
        try:
            from playwright.sync_api import sync_playwright
            self.session_dir.mkdir(parents=True, exist_ok=True)
            with sync_playwright() as pw:
                launch_args = dict(
                    user_data_dir=str(self.session_dir),
                    headless=False,
                    viewport={"width": 1180, "height": 860},
                )
                # The Windows portable EXE ships the Playwright driver, not a
                # 150 MB Chromium download. Prefer a locally installed Chrome
                # when frozen; source installs can use playwright Chromium.
                if getattr(sys, "frozen", False):
                    browser = pw.chromium.launch_persistent_context(channel="chrome", **launch_args)
                else:
                    try:
                        browser = pw.chromium.launch_persistent_context(**launch_args)
                    except Exception:
                        browser = pw.chromium.launch_persistent_context(channel="chrome", **launch_args)
                # Persistent Chrome may reopen at Instagram's manual CAPTCHA or
                # login screen. Never force Home over an active human challenge.
                open_pages = [p for p in browser.pages if not p.is_closed()]
                page = next((p for p in open_pages if preserve_instagram_auth_page(p)),
                            open_pages[0] if open_pages else browser.new_page())
                if not preserve_instagram_auth_page(page):
                    page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45_000)
                if self.autonomous:
                    self._update("login", "Sign in to Instagram; your account will be detected automatically.")
                    # Instagram changes its sidebar markup and may open the
                    # logged-in profile in another tab. Check every browser tab,
                    # but never guess an identity from an arbitrary profile URL.
                    login_started = time.monotonic()
                    needs_attention_sent = False
                    owner_profile_probed = False
                    while not self.stop_signal.is_set():
                        pages = [p for p in browser.pages if not p.is_closed()]
                        if any(challenge_detected(p) for p in pages):
                            # A real security checkpoint belongs to the user
                            # and Instagram. Do not navigate, probe identity,
                            # refresh, or resume collection while it is visible.
                            # Keep Chrome open for optional HUMAN verification.
                            # If Instagram redirects to login again, detection
                            # remains idle until ownership is positively proven.
                            self._update(
                                "needs_verification",
                                "Instagram requires manual CAPTCHA/security verification. "
                                "The robot is waiting without navigating or changing accounts. "
                                "If verification returns to login, do not repeatedly retry the robot; "
                                "check Instagram account access in regular Chrome. "
                                "You can Pause safely; saved results remain intact."
                            )
                            self.stop_signal.wait(3)
                            continue
                        identified = {u for p in pages if (u := signed_in_handle(p))}
                        if len(identified) > 1:
                            self._update("account_mismatch", "Different Instagram sessions were detected. Close extra accounts and retry.")
                            return
                        handle = next(iter(identified), None)
                        if handle:
                            break
                        elapsed = time.monotonic() - login_started
                        if (elapsed > 15 and not owner_profile_probed and
                                self.expected_handle and not self.stop_signal.is_set() and
                                safe_to_probe_owner_from_home(page)):
                            # A collapsed Instagram Home can omit Profile nav.
                            # Probe only from Home; never interrupt login/recaptcha.
                            # Visit the *selected* own profile once and require
                            # visible Edit profile evidence; expected alone is
                            # never treated as proof of the signed-in account.
                            owner_profile_probed = True
                            try:
                                handle = verify_selected_owner_profile(page, self.expected_handle)
                            except Exception:
                                handle = None  # transient/auth/navigation failures stay unverified
                            if handle:
                                break
                        if elapsed > 40 and not needs_attention_sent:
                            # Keep Chrome open so the owner can finish logging in or
                            # reload, rather than closing the window mid-auth.
                            self._update("needs_attention",
                                         "Instagram is open but its logged-in profile cannot be identified. Use the Chrome window opened by Insta Cleaner and reload Instagram. Detection continues automatically.")
                            needs_attention_sent = True
                        self.stop_signal.wait(3)
                    if self.stop_signal.is_set():
                        self._update("paused", "Stopped before starting.")
                        return
                    self.detected_handle = handle
                    if self.expected_handle and self.expected_handle != handle:
                        self._update("account_mismatch",
                                     "Instagram signed in as: @"+handle+
                                     ". Insta Cleaner currently selected: @"+self.expected_handle+
                                     " selected. Accounts will not be mixed.")
                        return

                    if not self.discover_following:
                        if not self.usernames:
                            self._update("needs_attention", "No imported Following list was provided.")
                            return
                        self._update(
                            "running",
                            f"Verified @{handle}. Reading counts for {len(self.usernames):,} "
                            "already imported profiles; Following discovery is not required."
                        )
                    else:
                        cached = read_following_cache(self.followings_path(), handle)
                        self.usernames = cached
                        self.total = len(cached)
                        self._update("discovering", "Reading the Following list of @"+handle+"...")
                        def save_batch(users, complete):
                            retained = reconcile_following_discovery(cached, users, complete)
                            with self.lock:
                                self.usernames = retained
                                self.total = len(retained)
                                self.discovery_complete = bool(complete)
                                self.message = ("Following profiles found: "+str(len(retained))+
                                                (" profiles (provisional list)." if not complete else " profiles."))
                            write_following_cache(self.followings_path(), handle, retained, complete)
                        # A recognized owner does not guarantee Instagram exposes
                        # a /following/ anchor. Keep Chrome open and allow the owner
                        # to open Following manually; retry without erasing caches.
                        while not self.stop_signal.is_set():
                            try:
                                users, complete = read_following_visible(
                                    page, handle, on_batch=save_batch,
                                    stop_signal=self.stop_signal)
                                break
                            except FollowingControlUnavailable as exc:
                                self._update(
                                    "needs_attention",
                                    str(exc) + " Open Following on your own profile "
                                    "in the Instagram Chrome window. Detection will retry "
                                    "automatically; your saved counts are preserved."
                                )
                                self.stop_signal.wait(4)
                        if self.stop_signal.is_set():
                            self._update("paused", "Collection paused; saved results were preserved.")
                            return
                        save_batch(users, complete)
                        # Visit the reconciled queue, not the shortened browser snapshot.
                        users = list(self.usernames)
                        if not users:
                            self._update("needs_attention",
                                         "Could not read the visible Following list. Check Instagram; no profiles will be invented.")
                            return
                        if self.stop_signal.is_set():
                            self._update("paused", "Search interrupted; partial Following list saved.")
                            return
                        self._update("running", "Following list "+("complete" if complete else "partial")+
                                     "; collecting visible counts...")
                else:
                    self._update("login", "Sign in to Instagram and select I have signed in.")
                    while not self.stop_signal.is_set() and not self.login_ready.wait(0.25):
                        pass
                    if self.stop_signal.is_set():
                        self._update("paused", "Stopped before starting.")
                        return

                saved = read_results(self.result_path())
                visits_file = history_path(self.result_path())
                visits = load_history(visits_file, saved)
                rests_file = batch_path(self.result_path())
                rests = load_batch_state(rests_file)
                if self.audit_mode == "oldest_first":
                    if not self.audit_cycle:
                        raise RuntimeError("A user-confirmed re-audit cycle is required.")
                    done = set(self.audit_cycle["done"])
                    remaining = [u for u in self.audit_cycle["targets"] if u not in done]
                else:
                    remaining = [u for u in self.usernames if not valid_saved_measurement(saved.get(u))]
                self._update("running", "Re-auditing oldest measurements..."
                             if self.audit_mode == "oldest_first" else
                             "Checking visible Instagram profiles...")
                for index, username in enumerate(remaining, 1):
                    if self.stop_signal.is_set():
                        self._update("paused", "Paused; saved results were preserved.")
                        return
                    while True:
                        waiting = max(
                            wait_required(visits, self.max_per_window, self.window_minutes,
                                          self.min_delay_seconds),
                            batch_wait(rests, self.pause_every, self.pause_minutes),
                        )
                        if waiting <= 0:
                            break
                        with self.lock:
                            self.wait_until = time.time() + waiting
                            self.message = (f"Pausa programada: {int(waiting + 0.999)} s antes de "
                                            f"@{username}.")
                        if self.stop_signal.wait(waiting):
                            self._update("paused", "Paused; saved results were preserved.")
                            return
                    with self.lock:
                        self.wait_until = 0
                        self.current_profile = username
                    # Persist a budget event BEFORE navigating. Crashes and
                    # blocked/login pages cannot silently reset the cooldown.
                    visits = register_visit(visits_file, visits)
                    try:
                        status, counts = collect_visible_counts(page, username)
                    finally:
                        visits = finish_visit(visits_file, visits)
                        rests = finish_batch_visit(rests_file, rests, self.pause_every,
                                                   self.pause_minutes)
                    if status in ("login_required", "blocked"):
                        self._update("blocked", "Instagram required verification or limited requests. The job stopped without attempting to bypass restrictions.")
                        return
                    row = {
                        "username": username, "followers": "", "following": "",
                        "checked_at": iso_now(), "source": "instagram_visible_profile_browser",
                        "status": status, "approximate": "false"
                    }
                    if counts:
                        row.update(followers=str(counts[0]), following=str(counts[1]),
                                   approximate=str(bool(counts[2])).lower())
                    # A later blocked/failed recheck never erases the last
                    # successful observation from the latest-results index.
                    previous = saved.get(username, {})
                    if not valid_saved_measurement(previous) or status == "ok":
                        if status == "ok":
                            append_dated_reading(dated_history_path(self.result_path()), row)
                        saved[username] = row
                        save_results(self.result_path(), saved)
                    if self.audit_mode == "oldest_first":
                        # Journal completion AFTER all durable per-profile writes.
                        self.audit_cycle = mark_attempt(audit_cycle_path(self.result_path()),
                                                        self.audit_cycle, username)
                        completed = len(self.audit_cycle["done"])
                        denominator = len(self.audit_cycle["targets"])
                    else:
                        completed = sum(valid_saved_measurement(saved.get(u)) for u in self.usernames)
                        denominator = self.total
                    self._update("running", f"@{username}: {status}. Completed {completed}/{denominator}.", completed)
                if self.stop_signal.is_set():
                    self._update("paused", "Paused; progress was saved.")
                    return
                unresolved = any(not valid_saved_measurement(saved.get(u)) for u in self.usernames)
                if self.audit_mode == "oldest_first":
                    done = len(self.audit_cycle["done"])
                    total = len(self.audit_cycle["targets"])
                    self._update("complete" if done == total else "partial",
                                 f"Re-audit completed {done}/{total} selected profiles. "
                                 "All valid dated readings were preserved.")
                    return
                self._update("complete" if not unresolved and
                             (self.queue_source == "imported" or not self.autonomous or self.discovery_complete)
                             else "partial",
                             "Imported profile counts processed. The import is a snapshot, not proof of live followback."
                             if self.queue_source == "imported" else
                             "Data collected. "+("Following complete." if self.discovery_complete else
                             "The Following list may be incomplete and requires browser review."))
        except Exception as exc:
            self._update("error", "Browser error: " + str(exc)[:240])
        finally:
            with self.lock:
                self.wait_until = 0
                self.current_profile = ""
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass

    def resume(self):
        with self.lock:
            if self.status != "login":
                raise ValueError("There is no pending Instagram sign-in window.")
            self.login_ready.set()
            self.message = "Preparing requests..."
            return self.snapshot()

    def stop(self):
        """Pause at the next safe checkpoint. Already saved results stay on disk."""
        with self.lock:
            if self.worker and self.worker.is_alive():
                self.pause_requested = True
                self.status = "pausing"
                self.message = "Pausing after the current profile; saving results..."
                self.stop_signal.set()
            return self.snapshot()

    def continue_collection(self, request: dict):
        """Explicit user action; a paused job never resumes because the page reloads."""
        with self.lock:
            owner, account = str(request.get("owner") or ""), str(request.get("account") or "")
            if not owner or not account or owner != self.owner or account != self.account:
                raise ValueError("Select the same app login and Instagram account before resuming.")
            if self.worker and self.worker.is_alive():
                raise ValueError("The robot is still pausing. Finish the current visit before resuming.")
            if self.status not in ("paused", "partial", "error"):
                raise ValueError("There is no paused collection to resume.")
            request = dict(request)
            request["expected_handle"] = self.expected_handle
            request["discover_following"] = self.discover_following
            request["usernames"] = [] if self.discover_following else list(self.usernames)
            request["resume_requested"] = True
            request["audit_mode"] = self.audit_mode
        return self.auto_start(request)

    def update_config(self, request: dict):
        """New pacing applies from the next profile; no cooldown history is erased."""
        owner, account = str(request.get("owner") or ""), str(request.get("account") or "")
        count, minutes, delay = check_pacing(
            request.get("max_per_window"), request.get("window_minutes"),
            request.get("min_delay_seconds"))
        rest_count, rest_minutes = check_batch_rest(
            request.get("pause_every", 0), request.get("pause_minutes", 0))
        with self.lock:
            if not owner or owner != self.owner or account != self.account:
                raise ValueError("Pacing settings belong to a different login or Instagram account.")
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = rest_count, rest_minutes
            self.message = "Pacing saved; settings apply from the next profile."
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            saved = read_results(self.result_path()) if self.owner and self.account else {}
            good = sum(valid_saved_measurement(saved.get(u)) for u in self.usernames)
            error = sum(saved.get(u, {}).get("status") == "error" for u in self.usernames)
            unavailable = sum(saved.get(u, {}).get("status") == "unavailable" for u in self.usernames)
            analyzed = good + error + unavailable
            return {
                "analyzed": analyzed,
                "successful": good,
                "errors": error,
                "unavailable": unavailable,
                "pending": max(0, self.total - analyzed),
                "remaining": max(0, self.total - good),
                "current_profile": self.current_profile,
                "status": self.status,
                "message": self.message,
                "progress": self.progress,
                "total": len(self.audit_cycle["targets"]) if self.audit_cycle else self.total,
                "audit_mode": self.audit_mode,
                "audit_completed": len(self.audit_cycle["done"]) if self.audit_cycle else 0,
                "audit_total": len(self.audit_cycle["targets"]) if self.audit_cycle else 0,
                "max_per_window": self.max_per_window,
                "window_minutes": self.window_minutes,
                "min_delay_seconds": self.min_delay_seconds,
                "pause_every": self.pause_every,
                "pause_minutes": self.pause_minutes,
                "wait_seconds": max(0, int(self.wait_until - time.time() + 0.999)) if self.wait_until else 0,
                "owner": self.owner,
                "account": self.account,
                "running": bool(self.worker and self.worker.is_alive()),
                "autonomous": self.autonomous,
                "detected_handle": self.detected_handle,
                "discovery_complete": self.discovery_complete,
                "queue_source": self.queue_source,
                "discovered": len(self.usernames),
                "queue_transport": "chunked" if self.queue_source == "imported" else "browser",
            }

    def following(self):
        with self.lock:
            # A directly imported queue is already in Desktop; avoid sending a
            # potentially enormous duplicate JSON response every five seconds.
            return {"usernames": list(self.usernames) if self.queue_source != "imported" else [],
                    "handle": self.detected_handle, "complete": self.discovery_complete}

    def dated_history(self, offset=0, size=1000):
        with self.lock:
            if not self.owner or not self.account:
                return {"rows": [], "next_offset": None}
            return read_dated_page(dated_history_path(self.result_path()), offset, size)

    def results(self):
        with self.lock:
            if not self.owner or not self.account:
                return []
            saved = read_results(self.result_path())
            rows = []
            for username in self.usernames:
                if username not in saved:
                    continue
                row = saved[username]
                if row.get("status") == "ok" and not valid_saved_measurement(row):
                    # Only sanitize the API response. Do not rewrite the CSV:
                    # owner evidence and historic timestamps must remain intact.
                    rows.append({**row, "status": "invalid_evidence",
                                 "evidence_warning": "Previous success record is missing verified counts or date; recheck required."})
                else:
                    rows.append(row)
            return rows


def build_server(collector: Collector, token: str, port: int = 0, updater=None,
                 *, developer_mode=False, audit_root=None):
    # Developer remains read-only by default. The ONLY relationship-changing
    # path is exact-target owner-confirmed Developer action testing. This path
    # writes canonical shared journals under a cross-process admission lease.
    if developer_mode:
        from developer_audit import run_audit, ai_prompt
        from developer_live_probe import DeveloperLiveProbe
    audit_root = Path(audit_root) if audit_root is not None else collector.data_dir
    live_probe = (DeveloperLiveProbe(audit_root, collector.session_dir)
                  if developer_mode else None)
    # Owner-approved Developer action tests intentionally write the canonical
    # action/protection journal, rather than creating a parallel history that
    # would later allow the public robot to replay the same Instagram click.
    # The Chrome session remains separate from the public Windows robot.
    dev_action_tests = (ActionRobot(collector, audit_root, collector.session_dir)
                        if developer_mode else None)
    developer_session_gate = threading.RLock()
    actions = ActionRobot(collector, collector.data_dir, collector.session_dir)
    collector.actions = actions
    live_relationships = LiveRelationships(collector, actions, collector.data_dir, collector.session_dir)
    collector.live_relationships = live_relationships
    # Chrome login cookies MUST live outside exportable counts/journal data.
    # Keep them next to the legacy browser session, never inside data_dir.
    dual_chrome_sessions = DualChromeSessions(collector.session_dir.parent / "account-browser-profiles")
    dual_robot_lanes = (DualRobotLanes(dual_chrome_sessions) if not developer_mode else None)
    class Handler(BaseHTTPRequestHandler):
        def _header(self, code, content_type="application/json"):
            self.send_response(code)
            self.send_header("Content-Type", content_type + "; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            # Local file pages use an opaque/null origin; a random session-only
            # X-IGC-Bridge-Token is additionally REQUIRED for every API request.
            self.send_header("Access-Control-Allow-Origin", "null")
            self.send_header("Access-Control-Allow-Headers", "X-IGC-Bridge-Token, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Private-Network", "true")
            self.end_headers()

        def _send(self, code, data):
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self._header(code)
            self.wfile.write(payload)

        def _authorized(self):
            if self.headers.get("Origin") not in (None, "null"):
                self._send(403, {"error": "Only the local Insta Cleaner app is allowed."})
                return False
            if not secrets.compare_digest(self.headers.get("X-IGC-Bridge-Token", ""), token):
                self._send(403, {"error": "Invalid local access token."})
                return False
            return True

        def do_OPTIONS(self):
            if self.headers.get("Origin") != "null":
                self._send(403, {"error": "Origen no admitido."})
                return
            self._header(204)

        def do_GET(self):
            if not self._authorized():
                return
            if self.path == "/api/status":
                self._send(200, collector.snapshot())
            elif self.path == "/api/results":
                self._send(200, {"rows": collector.results()})
            elif self.path.startswith("/api/history?"):
                from urllib.parse import urlsplit, parse_qs
                qs = parse_qs(urlsplit(self.path).query)
                try:
                    offset = int(qs.get("offset", ["0"])[0])
                    size = int(qs.get("size", ["1000"])[0])
                    self._send(200, collector.dated_history(offset, size))
                except (ValueError, TypeError) as exc:
                    self._send(400, {"error": str(exc)})
            elif self.path == "/api/following":
                self._send(200, collector.following())
            elif self.path == "/api/actions/status":
                self._send(200, actions.snapshot())
            elif self.path.startswith("/api/actions/dual-robots/status?") and not developer_mode:
                from urllib.parse import urlsplit, parse_qs
                params = parse_qs(urlsplit(self.path).query)
                owner = params.get("owner", [""])[0]
                try:
                    self._send(200, dual_robot_lanes.snapshot(owner))
                except ValueError as exc:
                    self._send(400, {"error": str(exc)})
            elif self.path == "/api/developer/live-status" and developer_mode:
                self._send(200, live_probe.snapshot())
            elif self.path == "/api/developer/action-status" and developer_mode:
                self._send(200, dev_action_tests.snapshot())
            elif self.path == "/api/update/status":
                self._send(200, updater.snapshot() if updater else
                           {"status":"unavailable","message":"Native Windows updater is not attached."})
            else:
                self._send(404, {"error": "Ruta desconocida."})

        def do_POST(self):
            if not self._authorized():
                return
            if self.path not in ("/api/start", "/api/load", "/api/stop", "/api/resume", "/api/auto", "/api/queue/init", "/api/queue/append", "/api/continue", "/api/config", "/api/actions/start", "/api/actions/history", "/api/actions/pause", "/api/actions/cancel-batch", "/api/actions/continue", "/api/actions/protect", "/api/actions/skip", "/api/actions/review-batch", "/api/actions/approve-batch", "/api/actions/defer-protected-batch", "/api/actions/replan-batch", "/api/actions/new-batch", "/api/actions/deferred-batches", "/api/actions/recheck-batch", "/api/actions/recheck-history", "/api/actions/history-recheck-status", "/api/actions/open-profile", "/api/actions/open-dual-chrome", "/api/actions/dual-robots/start", "/api/actions/dual-robots/stop", "/api/actions/dual-robots/stop-one", "/api/actions/dual-robots/restart-one", "/api/actions/live-start", "/api/actions/live-stop", "/api/actions/live-results", "/api/developer/audit", "/api/developer/live-start", "/api/developer/live-stop", "/api/developer/action-start", "/api/developer/action-stop", "/api/update/check", "/api/update/download", "/api/update/cancel", "/api/update/install"):
                self._send(404, {"error": "Ruta desconocida."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 0 or length > MAX_REQUEST:
                    raise ValueError("The list exceeds the maximum size.")
                body = self.rfile.read(length)
                data = json.loads(body or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("Invalid request.")
                if developer_mode and self.path not in (
                        "/api/developer/audit", "/api/developer/live-start",
                        "/api/developer/live-stop", "/api/developer/action-start",
                        "/api/developer/action-stop"):
                    raise ValueError("Developer Edition permits only diagnostics and explicitly owner-approved bounded action tests; normal robot/update commands are disabled.")
                if self.path == "/api/developer/live-start" and developer_mode:
                    with developer_session_gate:
                        if (dev_action_tests.worker and
                                dev_action_tests.worker.is_alive()):
                            raise ValueError("Pause the Developer live action test before opening read-only Chrome.")
                        result = live_probe.start(data)
                elif self.path == "/api/developer/live-stop" and developer_mode:
                    result = live_probe.stop()
                elif self.path == "/api/developer/action-start" and developer_mode:
                    with developer_session_gate:
                        if live_probe.worker and live_probe.worker.is_alive():
                            raise ValueError("Finish read-only Developer Chrome inspection first.")
                        task, targets = data.get("task"), data.get("targets")
                        if (task not in ("unfollow", "cancel") or
                                not isinstance(targets, list) or
                                not 1 <= len(targets) <= 10 or
                                any(not isinstance(user, str) or valid_username(user) != user for user in targets) or
                                len(set(targets)) != len(targets)):
                            raise ValueError("A live Developer test requires 1–10 distinct exact Instagram targets and Unfollow or Cancel.")
                        expected_consent = "LIVE_TEST:" + task + ":" + ",".join(targets)
                        if (data.get("explicit_consent") != expected_consent or
                                data.get("acknowledge_real_changes") is not True):
                            raise ValueError("Explicit confirmation of the exact profiles and irreversible real Instagram actions is required.")
                        if task == "unfollow" and data.get("followers_evidence") is not True:
                            raise ValueError("Confirm your verified Followers evidence before the real Unfollow test.")
                        # Run the exact existing verified action robot, with all
                        # its account/target/owner identity, protected exclusions,
                        # previous-click no-replay and saved batch guards.
                        # Never allow the client to bypass the journal authority.
                        request = dict(data)
                        request["batch_size"] = len(targets)
                        request["gap_seconds"] = max(10, float(data.get("gap_seconds") or 10))
                        request["rest_minutes"] = 0
                        request["confirmation"] = task + ":" + str(len(targets))
                        result = dev_action_tests.start(request)
                elif self.path == "/api/developer/action-stop" and developer_mode:
                    result = dev_action_tests.pause(data)
                elif self.path in (
                        "/api/developer/live-start", "/api/developer/live-stop",
                        "/api/developer/action-start", "/api/developer/action-stop"):
                    raise ValueError("Developer live diagnostics/actions require the separate Developer Edition.")
                elif self.path == "/api/developer/audit" and developer_mode:
                    report = run_audit(audit_root)
                    result = {"report": report,
                              "ai_prompt": ai_prompt(report, data.get("client_checks"))}
                elif self.path == "/api/developer/audit":
                    raise ValueError("Developer diagnostics are unavailable in the regular edition.")
                elif self.path.startswith("/api/update/"):
                    if updater is None:
                        raise ValueError("Windows updates are available only in the installed application.")
                    if self.path == "/api/update/check":
                        result = updater.check()
                    elif self.path == "/api/update/download":
                        result = updater.download()
                    elif self.path == "/api/update/cancel":
                        result = updater.cancel_download()
                    elif self.path == "/api/update/install":
                        if data.get("confirm") != "run_installer":
                            raise ValueError("Installing a verified update requires explicit owner confirmation.")
                        result = updater.install()
                    else:
                        raise ValueError("Unknown update action.")
                elif self.path == "/api/actions/open-dual-chrome":
                    result = dual_chrome_sessions.open_pair(data)
                elif self.path == "/api/actions/dual-robots/start":
                    result = dual_robot_lanes.start_pair(data)
                elif self.path == "/api/actions/dual-robots/stop":
                    result = dual_robot_lanes.stop_pair(data)
                elif self.path == "/api/actions/dual-robots/stop-one":
                    result = dual_robot_lanes.stop_one(data)
                elif self.path == "/api/actions/dual-robots/restart-one":
                    result = dual_robot_lanes.restart_one(data)
                elif self.path == "/api/actions/live-settings":
                    result = live_relationships.configuration(data)
                elif self.path == "/api/actions/live-start":
                    result = live_relationships.start(data)
                elif self.path == "/api/actions/live-stop":
                    result = live_relationships.pause(data)
                elif self.path == "/api/actions/live-results":
                    result = live_relationships.results(data)
                elif self.path == "/api/actions/history":
                    result = actions.attempted_history(data)
                elif self.path == "/api/actions/review-batch":
                    result = actions.batch_review(data)
                elif self.path == "/api/actions/approve-batch":
                    result = actions.approve_batch(data)
                elif self.path == "/api/actions/defer-protected-batch":
                    result = actions.defer_protected_batch(data)
                elif self.path == "/api/actions/replan-batch":
                    result = actions.replan_incomplete_batch(data)
                elif self.path == "/api/actions/new-batch":
                    result = actions.set_aside_incomplete_batch(data)
                elif self.path == "/api/actions/deferred-batches":
                    result = actions.deferred_batch_history(data)
                elif self.path == "/api/actions/open-profile":
                    result = actions.open_profile(data)
                elif self.path == "/api/actions/recheck-batch":
                    result = actions.recheck_batch(data)
                elif self.path == "/api/actions/recheck-history":
                    result = actions.recheck_history(data)
                elif self.path == "/api/actions/history-recheck-status":
                    result = actions.historical_recheck_status(data)
                elif self.path == "/api/actions/start":
                    result = actions.start(data)
                elif self.path == "/api/actions/continue":
                    result = actions.start(data, resume=True)
                elif self.path == "/api/actions/pause":
                    result = actions.pause(data)
                elif self.path == "/api/actions/cancel-batch":
                    result = actions.cancel_current_batch(data)
                elif self.path == "/api/actions/protect":
                    result = actions.protect(data)
                elif self.path == "/api/actions/skip":
                    result = actions.skip(data)
                elif self.path == "/api/start":
                    result = collector.start(data)
                elif self.path == "/api/queue/init":
                    result = collector.begin_import(data)
                elif self.path == "/api/queue/append":
                    result = collector.append_import(data)
                elif self.path == "/api/auto":
                    result = collector.auto_start(data)
                elif self.path == "/api/load":
                    result = collector.start(data, load_only=True)
                elif self.path == "/api/stop":
                    result = collector.stop()
                elif self.path == "/api/continue":
                    result = collector.continue_collection(data)
                elif self.path == "/api/config":
                    result = collector.update_config(data)
                else:
                    result = collector.resume()
                self._send(200, result)
            except ProtectedBatchCollision as exc:
                # A conflict is not a partial start. Return the exact
                # normalized collision set to the local owner-only UI so it
                # can replan without reusing the first approval.
                self._send(409, {
                    "error": str(exc),
                    "code": "stale_protected_batch",
                    "protected_usernames": exc.usernames,
                    "conflicting_count": len(exc.usernames),
                    "batch_size": exc.batch_size,
                    "task": exc.task,
                    "retry_requires_confirmation": True,
                })
            except ActionSessionBusy as exc:
                self._send(409, {"error": str(exc),
                                 "code": "cross_process_action_busy",
                                 "retry_requires_confirmation": False,
                                 "safe_no_click": True})
            except (ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": str(exc)})

        def log_message(self, format, *args):
            # Never write the app token, following list or Instagram usernames to logs.
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    # Native Windows launcher owns this server and pauses jobs before exit.
    server.actions = actions
    server.collector = collector
    server.live_relationships = live_relationships
    server.dual_chrome_sessions = dual_chrome_sessions
    server.dual_robot_lanes = dual_robot_lanes
    # The native host must also stop/await the Developer-only browser worker
    # and action lease before closing the loopback server or app process.
    server.dev_action_tests = dev_action_tests
    server.live_probe = live_probe
    return server


def main():
    parser = argparse.ArgumentParser(description="Local Insta Cleaner bridge for the visible Instagram browser robot.")
    parser.add_argument("--app", type=Path, help="Path to your Desktop HTML file (same version as your app).")
    parser.add_argument("--healthcheck", action="store_true", help="Check bundled Playwright and local server without opening Instagram.")
    parser.add_argument("--port", type=int, default=0, help="Local port (0 selects an available port).")
    parser.add_argument("--data-dir", type=Path, default=Path.home()/".ig-cleaner-pro"/"profile-counts")
    parser.add_argument("--session-dir", type=Path, default=Path.home()/".ig-cleaner-pro"/"instagram-browser")
    args = parser.parse_args()
    if args.healthcheck:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            if not pw.chromium:
                raise RuntimeError("Playwright could not initialize Chromium.")
        probe = build_server(Collector(args.data_dir, args.session_dir), "offline-check-token")
        probe.server_close()
        print("PASS: Playwright and local server available (not a live Instagram test).")
        return
    if not args.app or not args.app.is_file() or args.app.suffix.lower() != ".html":
        parser.error("--app requires an existing Desktop HTML file.")
    secret = secrets.token_urlsafe(32)
    collector = Collector(args.data_dir, args.session_dir)
    server = build_server(collector, secret, args.port)
    port = server.server_port
    print(f"Local robot ready. Port: {port}. The server is not exposed to the internet.")
    print("Do not share this launch link: it contains a temporary local controller token.")
    webbrowser.open(args.app.resolve().as_uri() + "#igc-robot=" + str(port) + "." + secret)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        collector.stop()
        collector.live_relationships.stop_event.set()
        print("Robot stopped. Saved results remain available for resuming.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
