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

TASKS = {"unfollow": "unfollow", "cancel": "cancel request", "audit": "read-only followback audit"}
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


def _visible_named_control(root, words, roles=("button", "menuitem"), text_fallback=False):
    """A uniquely named, visible control; duplicates and uncertainty fail closed."""
    for word in words:
        label = re.compile(r"^\s*(?:" + word + r")\s*$", re.I)
        seen = []
        for role in roles:
            matches = root.get_by_role(role, name=label)
            try:
                if matches.count() > 8:
                    raise RuntimeError("Demasiados controles similares; requiere revisión.")
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
                    raise RuntimeError("Demasiados textos equivalentes; requiere revisión.")
                seen.extend(matches.nth(i) for i in range(matches.count())
                            if matches.nth(i).is_visible())
            except RuntimeError:
                raise
            except Exception:
                continue
        if len(seen) == 1:
            return seen[0]
        if len(seen) > 1:
            raise RuntimeError("Hay múltiples opciones equivalentes; no se hará clic a ciegas.")
    return None


def _visible_button(root, words):
    return _visible_named_control(root, words, roles=("button",))


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
                raise RuntimeError("Hay varios menús abiertos; revisar manualmente.")
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
        raise RuntimeError("Demasiados diálogos; requiere revisión.")
    open_dialogs = [dialogs.nth(i) for i in range(total)
                    if dialogs.nth(i).is_visible()]
    if len(open_dialogs) > 1:
        raise RuntimeError("Varios diálogos visibles; no se ejecutará un clic ambiguo.")
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


def _follow_state(header):
    """Return verified post-action relation without conflating follow-back.

    Follow Back / Seguir también: they follow the owner; owner no longer follows.
    Follow / Seguir: owner no longer follows; no follow-back is indicated.
    """
    if _visible_button(header, [r"Follow Back", r"Seguir también"]):
        return "follow_back"
    if _visible_button(header, [r"Follow", r"Seguir"]):
        return "follow"
    return None


def _verify_final_state(page, expected_handle, *, checks=3):
    """Allow short UI settling but never infer success from a completed click."""
    for _ in range(checks):
        if challenge_detected(page) or page.locator('input[name="password"]').count():
            return "blocked", "Instagram mostró acceso/verificación tras la acción."
        if signed_in_handle(page) != expected_handle:
            return "blocked", "La cuenta de Instagram cambió durante la acción."
        header = page.locator("header").first
        if header.count() and header.is_visible():
            state = _follow_state(header)
            if state == "follow_back":
                return "ok", ("Acción confirmada: Follow Back / Seguir también. "
                              "La persona aún te sigue, pero tú ya no la sigues.")
            if state == "follow":
                return "ok", ("Acción confirmada: Follow / Seguir. "
                              "Ya no la sigues; el perfil no muestra followback.")
        page.wait_for_timeout(650)
    return "review", "Estado final ambiguo: no repetir esta operación automáticamente."


def _action_issue(task, result, message):
    """Stable codes for the owner-facing anomalies report, independent of UI locale."""
    if task == "unfollow" and result == "ok" and "Follow Back / Seguir también" in message:
        return "unexpected_followback"
    if task == "cancel" and result == "review" and message.startswith("Pendiente desactualizado:"):
        return "pending_already_following"
    if task == "cancel" and result == "review" and message.startswith("La solicitud ya no aparece"):
        return "pending_not_requested"
    if result == "review" and message.startswith("El perfil indica que ya te sigue"):
        return "mutual_before_action"
    if result == "review" and message.startswith("El perfil no muestra"):
        return "missing_profile_info"
    if result in ("review", "error", "blocked"):
        return "requires_manual_review"
    return ""


def perform_visible_action(page, username, task, expected_handle, can_act=None):
    """Execute real visible public-menu/private-confirmation flows conservatively.

    A public profile commonly needs Following -> menu Unfollow -> Follow.
    Private profiles may additionally ask for confirmation. The robot inspects
    what is actually shown rather than assuming any profile privacy state.
    """
    if task not in TASKS:
        raise ValueError("Acción desconocida.")
    page.goto("https://www.instagram.com/" + username + "/", wait_until="domcontentloaded",
              timeout=45000)
    page.wait_for_timeout(1000)
    if challenge_detected(page) or page.locator('input[name="password"]').count():
        return "blocked", "Instagram solicitó acceso o verificación."
    if signed_in_handle(page) != expected_handle:
        return "blocked", "No se puede verificar el Instagram activo; ninguna acción realizada."
    url = urlparse(page.url)
    if url.hostname not in ("www.instagram.com", "instagram.com") or url.path.strip("/").lower() != username:
        return "blocked", "Instagram redirigió a otro perfil."
    header = page.locator("header").first
    if not header.count() or not header.is_visible():
        return "blocked", "No se encontró la cabecera del perfil."
    if task == "unfollow" and re.search(r"\b(follows you|te sigue)\b",
                                          header.inner_text(timeout=4000), re.I):
        return "review", "El perfil indica que ya te sigue; requiere revisión."
    active = (_visible_button(header, [r"Following", r"Siguiendo"])
              if task == "unfollow" else
              _visible_button(header, [r"Requested", r"Solicitado", r"Solicitada"]))
    if active is None:
        if task == "cancel":
            if _visible_button(header, [r"Following", r"Siguiendo"]):
                return "review", ("Pendiente desactualizado: Instagram muestra Siguiendo / Following; "
                                  "la solicitud ya fue aceptada. No se modificó el seguimiento.")
            if _follow_state(header):
                return "review", ("La solicitud ya no aparece como Requested / Solicitado; "
                                  "no se realizó ningún cambio.")
        return "review", "El perfil no muestra el estado necesario para esta acción."
    if can_act and not can_act(username):
        return "skipped", "Omitido o protegido antes del primer clic."
    active.click(timeout=10000)
    page.wait_for_timeout(450)

    if task == "unfollow":
        # The FIRST click only opens a menu on public accounts.
        # Locate the "Unfollow" command in that menu (or a direct dialog).
        choice = _unfollow_option(page)
        if choice is None:
            # Rare layouts change directly on the first click. Do not guess.
            return _verify_final_state(page, expected_handle)
        if can_act and not can_act(username):
            return "review", "Se abrió el menú, pero la protección cambió; revisar antes de continuar."
        choice.click(timeout=10000)
        page.wait_for_timeout(650)
        # Public: new Follow button should be visible already.
        status, message = _verify_final_state(page, expected_handle, checks=2)
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
                    return "review", "Confirmación privada pendiente; protección cambió."
                confirm.click(timeout=10000)
                return _verify_final_state(page, expected_handle)
        return "review", "No se pudo confirmar si el perfil requiere otro paso; no se repetirá el clic."

    # Cancel sent follow request: Instagram layouts vary between direct toggles
    # and explicit Cancel Request confirmation.
    dialog = _visible_dialog(page)
    if dialog is not None:
        choice = _request_cancel_confirmation(dialog, username)
        if choice is None:
            return "review", "La confirmación no demuestra que sea la solicitud pendiente del perfil; no se hará clic."
        if can_act and not can_act(username):
            return "review", "Protección modificada antes de cancelar solicitud."
        choice.click(timeout=10000)
    return _verify_final_state(page, expected_handle)



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
            # A newly authorized batch uses the owner's current visible
            # favorites. During an active run protection may only be added.
            saved_protected = set(_users(data.get("protected", [])))
            if resume:
                saved_protected.update(self._protected())
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
                    "remaining": pending,
                    "wait_seconds": max(0, int(self.wait_until-time.time()+0.999)) if self.wait_until else 0,
                    "rows": [{"username": u, "status": rows[u].get("status", "pending"),
                              "issue": rows[u].get("issue", ""),
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
                    # Ambiguous results may have clicked already: never replay
                    # them automatically, even on Resume.
                    if (self._protected_for(user) or user in self.skipped or
                        journal.get(user, {}).get("status") in ("ok", "review", "error", "blocked")):
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
                        if self.task == "audit":
                            result, relation, details = perform_visible_followback_audit(
                                page, user, self.handle)
                        else:
                            relation = ""
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
                    issue = _action_issue(self.task, result, details)
                    journal[user] = {"status": result, "message": details,
                                     "audit_relation": relation,
                                     "issue": issue,
                                     "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
                    _atomic_json(path, journal)
                    if result != "ok":
                        # No-click preflight anomalies can be reviewed together after
                        # the batch. Potentially clicked/ambiguous results still stop.
                        if self.task == "audit" and result == "review":
                            continue
                        if issue in ("pending_already_following", "pending_not_requested",
                                     "mutual_before_action", "missing_profile_info"):
                            continue
                        with self.lock:
                            self.status, self.message = result, "@" + user + ": " + details
                        return
                with self.lock:
                    remaining = sum(u not in self._protected() and u not in self.skipped and
                                    journal.get(u, {}).get("status") != "ok"
                                    for u in self.targets)
                    self.status = "partial" if remaining else "complete"
                    self.message = ("Tanda revisada: hay perfiles que requieren verificación manual."
                                    if remaining else "Tanda terminada; resultados guardados.")
        except Exception as exc:
            with self.lock:
                self.status, self.message = "error", "Robot detenido: " + str(exc)[:220]
        finally:
            with self.lock:
                self.current, self.wait_until = "", 0
            if browser:
                try: browser.close()
                except Exception: pass
