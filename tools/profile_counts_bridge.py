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

from profile_counts_robot import (
    collect_visible_counts, iso_now, last_visit, read_results,
    save_results, seconds_since, valid_username,
)

MAX_REQUEST = 900_000
MAX_QUEUE = 10_000


class Collector:
    def __init__(self, data_dir: Path, session_dir: Path):
        self.data_dir = data_dir
        self.session_dir = session_dir
        self.lock = threading.RLock()
        self.login_ready = threading.Event()
        self.stop_signal = threading.Event()
        self.worker = None
        self.status = "idle"
        self.message = "Sin tarea activa"
        self.progress = 0
        self.total = 0
        self.owner = ""
        self.account = ""
        self.usernames = []
        self.per_hour = 50

    def result_path(self):
        # No owner/usernames in filenames or URL paths.
        identity = self.owner + "\0" + self.account
        digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("profile-counts-" + digest + ".csv")

    def start(self, request: dict):
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
        try:
            per_hour = int(request.get("per_hour", 50))
        except (TypeError, ValueError) as exc:
            raise ValueError("El ritmo de perfiles por hora es inválido.") from exc
        if not 1 <= per_hour <= 60:
            raise ValueError("El ritmo permitido es de 1 a 60 perfiles por hora.")
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Ya existe una recopilación activa. Detenla antes de iniciar otra.")
            self.owner, self.account, self.usernames, self.per_hour = owner, account, normalized, per_hour
            saved = read_results(self.result_path())
            self.total = len(normalized)
            self.progress = sum(u in saved and saved[u].get("status") == "ok" for u in normalized)
            self.message = "Iniciando navegador visible..."
            self.status = "starting"
            self.stop_signal.clear()
            self.login_ready.clear()
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
                self._update("login", "Inicia sesión en la ventana de Instagram y luego pulsa 'Ya inicié sesión' en Insta Cleaner.")
                while not self.stop_signal.is_set() and not self.login_ready.wait(0.25):
                    pass
                if self.stop_signal.is_set():
                    self._update("stopped", "Detenido antes de iniciar.")
                    return

                saved = read_results(self.result_path())
                remaining = [u for u in self.usernames if saved.get(u, {}).get("status") != "ok"]
                self._update("running", "Consultando perfiles visibles...")
                for index, username in enumerate(remaining, 1):
                    if self.stop_signal.is_set():
                        self._update("stopped", "Pausado; los resultados quedan guardados.")
                        return
                    delay = max(0, 3600 / self.per_hour - seconds_since(last_visit(saved)))
                    if delay and self.stop_signal.wait(delay):
                        self._update("stopped", "Pausado; los resultados quedan guardados.")
                        return
                    status, counts = collect_visible_counts(page, username)
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
                self._update("complete", "Terminó la cola. Los perfiles sin cifras siguen marcados como no disponibles.")
        except Exception as exc:
            self._update("error", "El navegador falló: " + str(exc)[:240])
        finally:
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
        self.stop_signal.set()
        with self.lock:
            if self.status in ("starting", "login", "running"):
                self.message = "Deteniendo la tarea de forma segura..."
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            return {
                "status": self.status,
                "message": self.message,
                "progress": self.progress,
                "total": self.total,
                "per_hour": self.per_hour,
                "owner": self.owner,
                "account": self.account,
                "running": bool(self.worker and self.worker.is_alive()),
            }

    def results(self):
        with self.lock:
            if not self.owner or not self.account:
                return []
            saved = read_results(self.result_path())
            return [saved[u] for u in self.usernames if u in saved]


def build_server(collector: Collector, token: str, port: int = 0):
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
            else:
                self._send(404, {"error": "Ruta desconocida."})

        def do_POST(self):
            if not self._authorized():
                return
            if self.path not in ("/api/start", "/api/stop", "/api/resume"):
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
                if self.path == "/api/start":
                    result = collector.start(data)
                elif self.path == "/api/stop":
                    result = collector.stop()
                else:
                    result = collector.resume()
                self._send(200, result)
            except (ValueError, json.JSONDecodeError) as exc:
                self._send(400, {"error": str(exc)})

        def log_message(self, format, *args):
            # Never write the app token, following list or Instagram usernames to logs.
            return

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


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
