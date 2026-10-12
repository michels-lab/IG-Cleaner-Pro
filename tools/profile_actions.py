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

from profile_counts_instagram import signed_in_handle, challenge_detected
from profile_counts_robot import valid_username
from profile_counts_pacing import (
    check_pacing, check_batch_rest, history_path, batch_path, load_history,
    load_batch_state, wait_required, batch_wait, register_visit, finish_visit,
    finish_batch_visit,
)

TASKS = {"unfollow": "dejar de seguir", "cancel": "cancelar solicitud"}
ACTION_WINDOW_MINUTES = 60
MAX_ACTIONS_PER_JOB = 1000


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
        raise ValueError("Registro del robot dañado: revisa antes de continuar.") from exc


def _users(raw):
    if not isinstance(raw, list) or len(raw) > MAX_ACTIONS_PER_JOB:
        raise ValueError("La tanda debe incluir hasta 1,000 perfiles.")
    out = []
    for item in raw:
        user = valid_username(item)
        if not user:
            raise ValueError("La tanda contiene un nombre de usuario inválido.")
        if user not in out:
            out.append(user)
    return out


def _visible_button(root, words):
    """Match a single visible button with an exact localized accessible label."""
    for word in words:
        matches = root.get_by_role("button", name=re.compile(r"^\s*" + word + r"\s*$", re.I))
        try:
            candidates = [matches.nth(i) for i in range(min(matches.count(), 6))
                          if matches.nth(i).is_visible()]
        except Exception:
            candidates = []
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise RuntimeError("Hay múltiples botones equivalentes; no se hará clic a ciegas.")
    return None


def perform_visible_action(page, username, task, expected_handle, can_act=None):
    """Performs one observable action and verifies a visible Follow button afterward.

    Requires navigation identity as well as the signed-in owner navigation link.
    The button choices are deliberately strict: if Instagram changes its UI,
    manual review is safer than guessing.
    """
    if task not in TASKS:
        raise ValueError("Acción desconocida.")
    page.goto("https://www.instagram.com/" + username + "/", wait_until="domcontentloaded",
              timeout=45000)
    page.wait_for_timeout(1000)
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "blocked", "Instagram solicitó acceso o verificación."
    signed = signed_in_handle(page)
    if signed != expected_handle:
        return "blocked", "No se puede verificar el Instagram activo; ninguna acción realizada."
    url = urlparse(page.url)
    if url.hostname not in ("www.instagram.com", "instagram.com") or url.path.strip("/").lower() != username:
        return "blocked", "Instagram redirigió a otro perfil."
    header = page.locator("header").first
    if not header.count() or not header.is_visible():
        return "blocked", "No se encontró la cabecera del perfil."
    # Do not unfollow a user when the live profile explicitly shows reciprocity.
    if task == "unfollow" and re.search(r"\b(follows you|te sigue)\b",
                                          header.inner_text(timeout=4000), re.I):
        return "review", "El perfil indica que ya te sigue; requiere revisión."
    # Match control only inside the target profile header, not recommendations.
    if task == "unfollow":
        active = _visible_button(header, [r"Following", r"Siguiendo"])
        confirm_words = [r"Unfollow", r"Dejar de seguir"]
    else:
        active = _visible_button(header, [r"Requested", r"Solicitado", r"Solicitada"])
        confirm_words = [r"Cancel Request", r"Cancelar solicitud", r"Cancelar"]
    if active is None:
        return "review", "No aparece el estado requerido del perfil; revisar manualmente."
    if can_act and not can_act(username):
        return "skipped", "Perfil protegido u omitido antes del clic."
    active.click(timeout=10000)
    page.wait_for_timeout(500)
    dialog = page.locator('[role="dialog"]').last
    confirm_root = dialog if dialog.count() and dialog.is_visible() else page
    confirmation = _visible_button(confirm_root, confirm_words)
    if confirmation:
        if can_act and not can_act(username):
            return "review", "Se abrió el diálogo, pero la protección cambió; confirmar estado manualmente."
        confirmation.click(timeout=10000)
    page.wait_for_timeout(1200)
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "blocked", "Instagram mostró acceso/verificación tras la acción."
    if signed_in_handle(page) != expected_handle:
        return "blocked", "No se puede verificar la sesión tras la acción."
    new_header = page.locator("header").first
    if _visible_button(new_header, [r"Follow", r"Seguir", r"Follow Back", r"Seguir también"]):
        return "ok", "Acción confirmada en el perfil visible."
    return "review", "Clic realizado, pero el estado final no es verificable. No repetir automáticamente."


class ActionRobot:
    def __init__(self, collector, data_dir: Path, session_dir: Path):
        self.collector, self.data_dir, self.session_dir = collector, data_dir, session_dir
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.worker = None
        self.owner = self.account = self.handle = self.task = ""
        self.targets = []
        self.skipped = set()
        self.max_count = 30
        self.window_minutes = ACTION_WINDOW_MINUTES
        self.min_delay_seconds = 10.0
        self.rest_minutes = 5.0
        self.status, self.message = "idle", "Sin acciones activas"
        self.current = ""
        self.wait_until = 0.0

    def _base(self, task=None):
        ident = "\0".join((self.owner, self.account, task or self.task))
        digest = hashlib.sha256(ident.encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("instagram-actions-" + digest + ".json")

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
                raise ValueError("Selecciona la misma cuenta para actualizar protegidos.")
            names = _users(data.get("protected", []))
            protected = self._protected()
            # Additive while running: a concurrent UI update can only protect.
            protected.update(names)
            _atomic_json(self._protection_file(), sorted(protected))
            return self.snapshot()

    def skip(self, data):
        with self.lock:
            if (str(data.get("owner") or ""), str(data.get("account") or "")) != (self.owner, self.account):
                raise ValueError("La tanda de acciones pertenece a otro Instagram.")
            user = valid_username(data.get("username"))
            if not user or user not in self.targets:
                raise ValueError("El perfil no forma parte de esta tanda.")
            self.skipped.add(user)
            return self.snapshot()

    def start(self, data, *, resume=False):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        expected = valid_username(data.get("expected_handle"))
        task = str(data.get("task") or "")
        targets = _users(data.get("targets"))
        if not owner or not account or len(owner) > 200 or len(account) > 120:
            raise ValueError("Elige primero el usuario de Insta Cleaner y su Instagram.")
        if not expected:
            raise ValueError("Asigna el @Instagram activo antes de operar.")
        if task not in TASKS or not targets:
            raise ValueError("Selecciona una tarea con perfiles válidos.")
        count = int(data.get("batch_size", 30))
        if count != data.get("batch_size", 30) or not 1 <= count <= 1000:
            raise ValueError("El tamaño de tanda debe estar entre 1 y 1,000.")
        max_count, window, delay = check_pacing(count, ACTION_WINDOW_MINUTES,
                                                 data.get("gap_seconds", 10))
        rest_input = data.get("rest_minutes", 5)
        every, rest = check_batch_rest(count if rest_input else 0, rest_input)
        if data.get("confirmation") != task + ":" + str(len(targets)):
            raise ValueError("La tanda no fue aprobada explícitamente.")
        if task == "unfollow" and data.get("followers_evidence") is not True:
            raise ValueError("No se verificó una lista completa de Followers.")
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Ya hay un robot de acciones activo.")
            if self.collector.worker and self.collector.worker.is_alive():
                raise ValueError("Termina o pausa Profile Counts antes de ejecutar acciones.")
            if resume and (owner, account, task) != (self.owner, self.account, self.task):
                raise ValueError("No se puede reanudar otra tarea o cuenta.")
            if resume and self.status not in ("paused", "error", "review", "blocked"):
                raise ValueError("No hay una tarea pausada para reanudar.")
            self.owner, self.account, self.handle, self.task = owner, account, expected, task
            self.targets = targets
            if not resume:
                self.skipped.clear()
            self.max_count, self.window_minutes, self.min_delay_seconds = max_count, window, delay
            self.rest_minutes = rest
            saved_protected = self._protected()
            saved_protected.update(_users(data.get("protected", [])))
            _atomic_json(self._protection_file(), sorted(saved_protected))
            self.stop_event.clear()
            self.status, self.message = "starting", "Abriendo Instagram en Chrome…"
            self.worker = threading.Thread(target=self._run, daemon=True)
            self.worker.start()
            return self.snapshot()

    def pause(self, data):
        with self.lock:
            if (str(data.get("owner") or ""), str(data.get("account") or "")) != (self.owner, self.account):
                raise ValueError("La tarea corresponde a otro Instagram.")
            if self.worker and self.worker.is_alive():
                self.status, self.message = "pausing", "Pausando tras la visita actual…"
                self.stop_event.set()
            return self.snapshot()

    def snapshot(self):
        with self.lock:
            journal = self._journal() if self.owner and self.task else {}
            rows = {u: journal.get(u, {}) for u in self.targets}
            protected = self._protected() if self.owner else set()
            successful = sum(x.get("status") == "ok" for x in rows.values())
            reviewed = sum(x.get("status") in ("review", "error", "blocked") for x in rows.values())
            ignored = sum(u in protected for u in self.targets)
            skipped = sum(u in self.skipped for u in self.targets)
            return {"status": self.status, "message": self.message,
                    "owner": self.owner, "account": self.account, "task": self.task,
                    "current_profile": self.current,
                    "running": bool(self.worker and self.worker.is_alive()),
                    "total": len(self.targets), "successful": successful,
                    "errors": reviewed, "protected": ignored, "skipped": skipped,
                    "remaining": sum(u not in protected and u not in self.skipped and rows[u].get("status") != "ok"
                                     for u in self.targets),
                    "wait_seconds": max(0, int(self.wait_until-time.time()+0.999)) if self.wait_until else 0,
                    "rows": [{"username": u, "status": rows[u].get("status", "pending"),
                              "message": rows[u].get("message", ""),
                              "at": rows[u].get("at", "")} for u in self.targets]}

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
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
                with self.lock:
                    self.status, self.message = "login", "Inicia sesión en Chrome como @" + self.handle
                while not self.stop_event.is_set():
                    if challenge_detected(page):
                        with self.lock:
                            self.status, self.message = "blocked", "Instagram exige verificación."
                        return
                    signed = signed_in_handle(page)
                    if signed:
                        if signed != self.handle:
                            with self.lock:
                                self.status, self.message = "blocked", "Chrome usa @" + signed + " y se esperaba @" + self.handle
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
                for user in self.targets:
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progreso guardado; pulsa Reanudar."
                        return
                    if self._protected_for(user) or user in self.skipped or journal.get(user, {}).get("status") == "ok":
                        continue
                    while not self.stop_event.is_set():
                        delay = max(wait_required(visits, self.max_count, self.window_minutes,
                                                  self.min_delay_seconds),
                                    batch_wait(rests, self.max_count if self.rest_minutes > 0 else 0,
                                               self.rest_minutes))
                        if delay <= 0: break
                        with self.lock:
                            self.status, self.wait_until = "waiting", time.time() + delay
                            self.message = "Pausa programada: " + str(int(delay+0.999)) + " s"
                        self.stop_event.wait(min(delay, 2.0))
                    if self.stop_event.is_set():
                        with self.lock: self.status, self.message = "paused", "Progreso guardado; pulsa Reanudar."
                        return
                    with self.lock:
                        self.wait_until = 0
                        self.current = user
                        self.status, self.message = "running", "Consultando @" + user
                    if self._protected_for(user) or user in self.skipped:
                        continue
                    visits = register_visit(visits_file, visits)
                    try:
                        result, details = perform_visible_action(
                            page, user, self.task, self.handle,
                            lambda name: not self.stop_event.is_set() and
                            not self._protected_for(name) and name not in self.skipped)
                    except Exception as exc:
                        result, details = "error", "No se verificó la acción: " + str(exc)[:200]
                    finally:
                        visits = finish_visit(visits_file, visits)
                        rests = finish_batch_visit(
                            rests_file, rests,
                            self.max_count if self.rest_minutes > 0 else 0, self.rest_minutes)
                    if result == "skipped":
                        continue
                    journal[user] = {"status": result, "message": details,
                                     "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    _atomic_json(path, journal)
                    if result != "ok":
                        with self.lock:
                            self.status, self.message = result, "@" + user + ": " + details
                        return
                with self.lock:
                    self.status, self.message = "complete", "Tanda terminada; resultados guardados."
        except Exception as exc:
            with self.lock:
                self.status, self.message = "error", "Robot detenido: " + str(exc)[:220]
        finally:
            with self.lock:
                self.current, self.wait_until = "", 0
            if browser:
                try: browser.close()
                except Exception: pass
