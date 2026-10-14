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

from profile_counts_instagram import (signed_in_handle, challenge_detected, read_following_visible,
                                      write_following_cache, read_following_cache, reconcile_following_discovery,
                                      verify_selected_owner_profile, FollowingControlUnavailable)
from profile_actions import ActionRobot

from profile_counts_robot import collect_visible_counts, iso_now, read_results, save_results, valid_username
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
        self.import_stage = None  # ephemeral, owner-scoped upload until commit

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
        with self.lock:
            if self.actions and self.actions.worker and self.actions.worker.is_alive():
                raise ValueError("An Instagram action robot is running. Pause it before Profile Counts.")
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
            self.autonomous = True
            self.detected_handle = ""
            self.discover_following = discover
            self.queue_source = "instagram" if discover else "imported"
            self.discovery_complete = False
            self.usernames = [] if discover else normalized
            self.total = len(self.usernames)
            saved = read_results(self.result_path())
            self.progress = sum(saved.get(u, {}).get("status") == "ok" for u in self.usernames)
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = rest_count, rest_minutes
            self.wait_until = 0
            self.current_profile = ""
            self.message = "Opening Instagram to verify your session..."
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
            raise ValueError("Se requiere identidad de propietario e Instagram activo.")
        count, minutes, delay = check_pacing(
            request.get("max_per_window", request.get("per_hour", DEFAULT_COUNT)),
            request.get("window_minutes", DEFAULT_WINDOW_MINUTES),
            request.get("min_delay_seconds", DEFAULT_DELAY_SECONDS),
        )
        pause_every, pause_minutes = check_batch_rest(
            request.get("pause_every", 0),
            request.get("pause_minutes", 0),
        )
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("A collection is already running. Stop it before starting another.")
            self.owner, self.account, self.usernames = owner, account, normalized
            self.autonomous = False
            self.discover_following = False
            self.queue_source = "imported"
            self.detected_handle = ""
            self.discovery_complete = False
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = pause_every, pause_minutes
            self.wait_until = 0
            self.current_profile = ""
            saved = read_results(self.result_path())
            self.total = len(normalized)
            self.progress = sum(u in saved and saved[u].get("status") == "ok" for u in normalized)
            self.message = ("Registros guardados recuperados; pulsa Iniciar para continuar."
                            if load_only else "Iniciando navegador visible...")
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
                page = browser.pages[0] if browser.pages else browser.new_page()
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
                            self._update("blocked", "Instagram requested verification; collection stopped.")
                            return
                        identified = {u for p in pages if (u := signed_in_handle(p))}
                        if len(identified) > 1:
                            self._update("account_mismatch", "Different Instagram sessions were detected. Close extra accounts and retry.")
                            return
                        handle = next(iter(identified), None)
                        if handle:
                            break
                        elapsed = time.monotonic() - login_started
                        if (elapsed > 15 and not owner_profile_probed and
                                self.expected_handle and not self.stop_signal.is_set()):
                            # A collapsed Instagram Home can omit Profile nav.
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
                remaining = [u for u in self.usernames if saved.get(u, {}).get("status") != "ok"]
                self._update("running", "Checking visible Instagram profiles...")
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
                    saved[username] = row
                    save_results(self.result_path(), saved)
                    completed = sum(u in saved and saved[u].get("status") == "ok" for u in self.usernames)
                    self._update("running", f"@{username}: {status}. Completed {completed}/{self.total}.", completed)
                if self.stop_signal.is_set():
                    self._update("paused", "Paused; progress was saved.")
                    return
                unresolved = any(saved.get(u, {}).get("status") != "ok" for u in self.usernames)
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
            good = sum(saved.get(u, {}).get("status") == "ok" for u in self.usernames)
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
                "total": self.total,
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
            return {"usernames": list(self.usernames) if self.queue_source == "instagram" else [],
                    "handle": self.detected_handle, "complete": self.discovery_complete}

    def results(self):
        with self.lock:
            if not self.owner or not self.account:
                return []
            saved = read_results(self.result_path())
            return [saved[u] for u in self.usernames if u in saved]


def build_server(collector: Collector, token: str, port: int = 0):
    actions = ActionRobot(collector, collector.data_dir, collector.session_dir)
    collector.actions = actions
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
                self._send(403, {"error": "Solo se admite la app local."})
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
            elif self.path == "/api/following":
                self._send(200, collector.following())
            elif self.path == "/api/actions/status":
                self._send(200, actions.snapshot())
            else:
                self._send(404, {"error": "Ruta desconocida."})

        def do_POST(self):
            if not self._authorized():
                return
            if self.path not in ("/api/start", "/api/load", "/api/stop", "/api/resume", "/api/auto", "/api/queue/init", "/api/queue/append", "/api/continue", "/api/config", "/api/actions/start", "/api/actions/pause", "/api/actions/continue", "/api/actions/protect", "/api/actions/skip"):
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
                if self.path == "/api/actions/start":
                    result = actions.start(data)
                elif self.path == "/api/actions/continue":
                    result = actions.start(data, resume=True)
                elif self.path == "/api/actions/pause":
                    result = actions.pause(data)
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
            except (ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": str(exc)})

        def log_message(self, format, *args):
            # Never write the app token, following list or Instagram usernames to logs.
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    # Native Windows launcher owns this server and pauses jobs before exit.
    server.actions = actions
    server.collector = collector
    return server


def main():
    parser = argparse.ArgumentParser(description="Puente local de Insta Cleaner ↔ robot visible de Instagram.")
    parser.add_argument("--app", type=Path, help="Path to your Desktop HTML file (same version as your app).")
    parser.add_argument("--healthcheck", action="store_true", help="Prueba empaquetado Playwright + servidor local, sin abrir Instagram.")
    parser.add_argument("--port", type=int, default=0, help="Puerto local (0 = aleatorio disponible).")
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
        print("PASS: runtime Playwright y servidor local disponibles (no prueba Instagram).")
        return
    if not args.app or not args.app.is_file() or args.app.suffix.lower() != ".html":
        parser.error("--app necesita un archivo Desktop HTML existente.")
    secret = secrets.token_urlsafe(32)
    collector = Collector(args.data_dir, args.session_dir)
    server = build_server(collector, secret, args.port)
    port = server.server_port
    print(f"Robot local preparado. Puerto: {port}. No se expone a Internet.")
    print("No compartas el enlace de inicio: contiene una clave temporal del controlador local.")
    webbrowser.open(args.app.resolve().as_uri() + "#igc-robot=" + str(port) + "." + secret)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        collector.stop()
        print("Robot detenido. Los resultados se conservan para retomarlos.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
