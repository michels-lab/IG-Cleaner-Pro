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
                                      write_following_cache, read_following_cache, reconcile_following_discovery)
from profile_actions import ActionRobot

from profile_counts_robot import collect_visible_counts, iso_now, read_results, save_results, valid_username
from profile_counts_pacing import (check_pacing, history_path, load_history,
                                   register_visit, finish_visit, wait_required,
                                   DEFAULT_COUNT, DEFAULT_WINDOW_MINUTES, DEFAULT_DELAY_SECONDS,
                                   check_batch_rest, batch_path, load_batch_state,
                                   batch_wait, finish_batch_visit)

MAX_REQUEST = 900_000
MAX_QUEUE = 10_000


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
        self.message = "Sin tarea activa"
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
        self.current_profile = ""

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
            raise ValueError("Falta identidad de la cuenta activa de Insta Cleaner.")
        expected = valid_username(request.get("expected_handle") or "")
        if request.get("expected_handle") and not expected:
            raise ValueError("El nombre de Instagram esperado es inválido.")
        # Pacing is retained internally; novice users do not need to see settings.
        pacing = dict(max_per_window=request.get("max_per_window", DEFAULT_COUNT),
                      window_minutes=request.get("window_minutes", DEFAULT_WINDOW_MINUTES),
                      min_delay_seconds=request.get("min_delay_seconds", DEFAULT_DELAY_SECONDS))
        count, minutes, delay = check_pacing(
            pacing["max_per_window"], pacing["window_minutes"], pacing["min_delay_seconds"])
        rest_count, rest_minutes = check_batch_rest(request.get("pause_every", 0),
                                                     request.get("pause_minutes", 0))
        with self.lock:
            if self.worker and self.worker.is_alive():
                if owner != self.owner or account != self.account:
                    raise ValueError("Hay otra cuenta en ejecución. No se mezclan los perfiles.")
                return self.snapshot()
            if self.status in ("paused", "pausing") and not request.get("resume_requested"):
                if owner != self.owner or account != self.account:
                    raise ValueError("Hay otra cuenta pausada. No se mezclan los perfiles.")
                return self.snapshot()
            self.pause_requested = False
            self.owner, self.account = owner, account
            self.expected_handle = expected or ""
            self.autonomous = True
            self.detected_handle = ""
            self.discovery_complete = False
            self.usernames = []
            self.total = self.progress = 0
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = rest_count, rest_minutes
            self.wait_until = 0
            self.current_profile = ""
            self.message = "Abriendo Instagram para reconocer tu cuenta..."
            self.status = "starting"
            self.stop_signal.clear()
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def start(self, request: dict, load_only: bool = False):
        usernames = request.get("usernames")
        if not isinstance(usernames, list) or not 1 <= len(usernames) <= MAX_QUEUE:
            raise ValueError("La lista debe tener entre 1 y 10,000 perfiles.")
        normalized, seen = [], set()
        for user in usernames:
            clean = valid_username(user)
            if not clean or clean in seen:
                continue
            normalized.append(clean)
            seen.add(clean)
        if not normalized:
            raise ValueError("No se encontraron nombres de usuario válidos.")
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
                raise ValueError("Ya existe una recopilación activa. Detenla antes de iniciar otra.")
            self.owner, self.account, self.usernames = owner, account, normalized
            self.autonomous = False
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
                    self._update("login", "Inicia sesión en Instagram; detectaré tu cuenta automáticamente.")
                    # Instagram changes its sidebar markup and may open the
                    # logged-in profile in another tab. Check every browser tab,
                    # but never guess an identity from an arbitrary profile URL.
                    login_started = time.monotonic()
                    needs_attention_sent = False
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
                        if time.monotonic() - login_started > 40 and not needs_attention_sent:
                            # Keep Chrome open so the owner can finish logging in or
                            # reload, rather than closing the window mid-auth.
                            self._update("needs_attention",
                                         "Instagram is open but its logged-in profile cannot be identified. Use the Chrome window opened by Insta Cleaner and reload Instagram. Detection continues automatically.")
                            needs_attention_sent = True
                        self.stop_signal.wait(3)
                    if self.stop_signal.is_set():
                        self._update("paused", "Detenido antes de iniciar.")
                        return
                    self.detected_handle = handle
                    if self.expected_handle and self.expected_handle != handle:
                        self._update("account_mismatch",
                                     "Instagram abierto: @"+handle+
                                     ". Insta Cleaner tiene @"+self.expected_handle+
                                     " seleccionado. No se mezclarán cuentas.")
                        return
                    cached = read_following_cache(self.followings_path(), handle)
                    self.usernames = cached
                    self.total = len(cached)
                    self._update("discovering", "Leyendo tu lista Following de @"+handle+"...")
                    def save_batch(users, complete):
                        retained = reconcile_following_discovery(cached, users, complete)
                        with self.lock:
                            self.usernames = retained
                            self.total = len(retained)
                            self.discovery_complete = bool(complete)
                            self.message = ("Following detectados: "+str(len(retained))+
                                            (" perfiles (lista provisional)." if not complete else " perfiles."))
                        write_following_cache(self.followings_path(), handle, retained, complete)
                    users, complete = read_following_visible(
                        page, handle, on_batch=save_batch, stop_signal=self.stop_signal)
                    save_batch(users, complete)
                    # Visit the reconciled queue, not the shortened browser snapshot.
                    users = list(self.usernames)
                    if not users:
                        self._update("needs_attention",
                                     "No pude leer la lista Following visible. Comprueba Instagram; no inventaré perfiles.")
                        return
                    if self.stop_signal.is_set():
                        self._update("paused", "Búsqueda interrumpida; lista parcial guardada.")
                        return
                    self._update("running", "Lista Following "+("completa" if complete else "parcial")+
                                 "; recopilando cifras...")
                else:
                    self._update("login", "Inicia sesión en Instagram y pulsa Ya inicié sesión.")
                    while not self.stop_signal.is_set() and not self.login_ready.wait(0.25):
                        pass
                    if self.stop_signal.is_set():
                        self._update("paused", "Detenido antes de iniciar.")
                        return

                saved = read_results(self.result_path())
                visits_file = history_path(self.result_path())
                visits = load_history(visits_file, saved)
                rests_file = batch_path(self.result_path())
                rests = load_batch_state(rests_file)
                remaining = [u for u in self.usernames if saved.get(u, {}).get("status") != "ok"]
                self._update("running", "Consultando perfiles visibles...")
                for index, username in enumerate(remaining, 1):
                    if self.stop_signal.is_set():
                        self._update("paused", "Pausado; los resultados quedan guardados.")
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
                            self._update("paused", "Pausado; los resultados quedan guardados.")
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
                        self._update("blocked", "Instagram solicitó acceso/verificación o limitó las consultas. Se detuvo sin evasión.")
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
                    self._update("running", f"@{username}: {status}. Completados {completed}/{self.total}.", completed)
                if self.stop_signal.is_set():
                    self._update("paused", "Pausado; se guardó el avance.")
                    return
                unresolved = any(saved.get(u, {}).get("status") != "ok" for u in self.usernames)
                self._update("complete" if not unresolved and (not self.autonomous or self.discovery_complete) else "partial",
                             "Datos recopilados. "+("Following completo." if self.discovery_complete else
                             "La lista Following podría estar incompleta; se necesitará revisar el navegador."))
        except Exception as exc:
            self._update("error", "El navegador falló: " + str(exc)[:240])
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
                raise ValueError("No hay una ventana de inicio de sesión pendiente.")
            self.login_ready.set()
            self.message = "Preparando las consultas..."
            return self.snapshot()

    def stop(self):
        """Pause at the next safe checkpoint. Already saved results stay on disk."""
        with self.lock:
            if self.worker and self.worker.is_alive():
                self.pause_requested = True
                self.status = "pausing"
                self.message = "Pausando después de la visita actual; guardando resultados..."
                self.stop_signal.set()
            return self.snapshot()

    def continue_collection(self, request: dict):
        """Explicit user action; a paused job never resumes because the page reloads."""
        with self.lock:
            owner, account = str(request.get("owner") or ""), str(request.get("account") or "")
            if not owner or not account or owner != self.owner or account != self.account:
                raise ValueError("Selecciona el mismo usuario y perfil de Instagram antes de reanudar.")
            if self.worker and self.worker.is_alive():
                raise ValueError("El robot sigue pausando. Espera a que termine la visita actual.")
            if self.status not in ("paused", "partial", "error"):
                raise ValueError("No hay una recopilación pausada para reanudar.")
            request = dict(request)
            request["expected_handle"] = self.expected_handle
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
                raise ValueError("Los tiempos pertenecen a otro usuario o Instagram.")
            self.max_per_window, self.window_minutes, self.min_delay_seconds = count, minutes, delay
            self.pause_every, self.pause_minutes = rest_count, rest_minutes
            self.message = "Tiempos guardados; se aplican desde la siguiente visita."
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
                "discovered": len(self.usernames),
            }

    def following(self):
        with self.lock:
            return {"usernames": list(self.usernames), "handle": self.detected_handle,
                    "complete": self.discovery_complete}

    def results(self):
        with self.lock:
            if not self.owner or not self.account:
                return []
            saved = read_results(self.result_path())
            return [saved[u] for u in self.usernames if u in saved]


def build_server(collector: Collector, token: str, port: int = 0):
    actions = ActionRobot(collector, collector.data_dir, collector.session_dir)
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
                self._send(403, {"error": "Token local inválido."})
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
            if self.path not in ("/api/start", "/api/load", "/api/stop", "/api/resume", "/api/auto", "/api/continue", "/api/config", "/api/actions/start", "/api/actions/pause", "/api/actions/continue", "/api/actions/protect", "/api/actions/skip"):
                self._send(404, {"error": "Ruta desconocida."})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 0 or length > MAX_REQUEST:
                    raise ValueError("La lista excede el tamaño máximo.")
                body = self.rfile.read(length)
                data = json.loads(body or b"{}")
                if not isinstance(data, dict):
                    raise ValueError("Solicitud inválida.")
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
    parser.add_argument("--app", type=Path, help="Ruta del HTML Desktop (misma versión que ya usas).")
    parser.add_argument("--healthcheck", action="store_true", help="Prueba empaquetado Playwright + servidor local, sin abrir Instagram.")
    parser.add_argument("--port", type=int, default=0, help="Puerto local (0 = aleatorio disponible).")
    parser.add_argument("--data-dir", type=Path, default=Path.home()/".ig-cleaner-pro"/"profile-counts")
    parser.add_argument("--session-dir", type=Path, default=Path.home()/".ig-cleaner-pro"/"instagram-browser")
    args = parser.parse_args()
    if args.healthcheck:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            if not pw.chromium:
                raise RuntimeError("Playwright no inicializó Chromium.")
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
