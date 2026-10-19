#!/usr/bin/env python3
"""Insta Cleaner Pro: one-click Windows application with its own robot backend.

The application launches a dedicated, persistent Chrome app-mode window and
runs the token-protected loopback controller in this same process. The user
never needs to start a .cmd or a second backend program. Instagram itself
opens in the separate visible, owner-controlled browser only on request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import secrets

from profile_counts_bridge import Collector, build_server
from windows_updater import WindowsUpdater, numeric_version


APP_NAME = "Insta Cleaner Pro"
BUNDLED_HTML = "IG-Cleaner-Pro.html"
BUNDLED_VERSION = "android-signing.json"


def app_version() -> str:
    """Read the actual packaged version, never assume the public release tag."""
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    metadata = root / "metadata" / BUNDLED_VERSION
    if not metadata.is_file() and not getattr(sys, "frozen", False):
        metadata = root / "release" / BUNDLED_VERSION
    value = str(json.loads(metadata.read_text(encoding="utf-8"))["versionName"])
    numeric_version("v"+value)
    return value


def app_home() -> Path:
    """Stable across updates: file:// page and Chrome workspace identity persist."""
    base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    return base / "Michels Lab" / "Insta Cleaner Pro"


def bundled_html() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "ui" / BUNDLED_HTML


def prepare_html(source: Path, destination: Path) -> Path:
    """Copy only on content change, atomically, without touching workspace data."""
    if not source.is_file():
        raise FileNotFoundError("El ejecutable no incluye la interfaz de Insta Cleaner.")
    incoming = source.read_bytes()
    if len(incoming) < 100_000:
        raise ValueError("La interfaz incluida está incompleta.")
    if destination.is_file() and hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256(incoming).digest():
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".new")
    try:
        with temporary.open("wb") as f:
            f.write(incoming)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


def chrome_path() -> Path:
    """Find installed Chrome without downloading anything or guessing an exe path."""
    candidates = [shutil.which("chrome"), shutil.which("chrome.exe")]
    for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        directory = os.environ.get(env)
        if directory:
            candidates.append(str(Path(directory) / "Google" / "Chrome" / "Application" / "chrome.exe"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise FileNotFoundError("Instala Google Chrome para abrir Insta Cleaner y usar el robot de Instagram.")


def chrome_app_args(executable: Path, page: Path, workspace: Path, port: int, token: str, *, developer=False):
    if not (1 <= port <= 65535) or not token:
        raise ValueError("El puente local no se ha inicializado.")
    url = page.resolve().as_uri() + "#igc-robot=" + str(port) + "." + token + ("&igc-developer=1" if developer else "")
    return [str(executable), "--no-first-run", "--no-default-browser-check",
            "--disable-background-mode", "--user-data-dir=" + str(workspace),
            "--app=" + url]


def acquire_single_instance(*, developer=False):
    """Prevent reopening a second window with a dead port/token for the same profile."""
    if sys.platform != "win32":
        return None
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_bool
    handle = kernel32.CreateMutexW(None, False, "Local\\MichelsLab_InstaCleanerPro_Developer" if developer else "Local\\MichelsLab_InstaCleanerPro_Desktop")
    if not handle:
        raise OSError("No se pudo reservar la instancia de Insta Cleaner.")
    if ctypes.get_last_error() == 183:
        kernel32.CloseHandle(handle)
        raise RuntimeError("Insta Cleaner Pro ya está abierto. Usa la ventana existente.")
    return handle


def release_single_instance(handle):
    if handle is not None and sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.CloseHandle(handle)


def alert(message: str) -> None:
    """User-visible startup errors for --windowed Windows binaries."""
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, APP_NAME, 0x10)
    else:
        print(message, file=sys.stderr)


def stop_safely(server) -> None:
    """Do not lose a just-clicked action when the application window closes."""
    actions = server.actions
    actions.stop_event.set()
    server.collector.stop()
    for job in (actions.worker, server.collector.worker):
        if job and job.is_alive():
            job.join(timeout=60)
    server.shutdown()
    server.server_close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Insta Cleaner Pro Windows con robot integrado")
    parser.add_argument("--healthcheck", action="store_true")
    parser.add_argument("--developer", action="store_true",
                        help="Launch isolated, read-only Developer Edition with local audit/export.")
    parser.add_argument("--smoke-startup", action="store_true",
                        help="Initialize the installed UI and local controller without Instagram.")
    args = parser.parse_args(argv)
    try:
        source = bundled_html()
        if args.smoke_startup:
            # Test the REAL installed executable's file:// and local backend
            # startup path. No sign-in, network calls, browser automation, or
            # destructive workspace resets. Used by silent Setup acceptance.
            home = app_home()
            page = prepare_html(source, home / BUNDLED_HTML)
            if page.stat().st_size < 100_000:
                raise RuntimeError("The installed interface is incomplete.")
            browser = chrome_path()
            if not browser.is_file():
                raise FileNotFoundError("Chrome is required for the Windows app.")
            chrome_workspace = home / "workspace-browser"
            chrome_workspace.mkdir(parents=True, exist_ok=True)
            legacy = Path.home() / ".ig-cleaner-pro"
            manager = WindowsUpdater(app_version(),home,legacy / "profile-counts")
            server = build_server(Collector(legacy / "profile-counts",
                                            legacy / "instagram-browser"),
                                  "installer-smoke-session-token", 0, updater=manager)
            try:
                assert server.server_address[0] == "127.0.0.1"
            finally:
                server.server_close()
            print("PASS: installed UI origin, Chrome, workspace and loopback server.")
            return 0
        if args.healthcheck:
            if not source.is_file() or source.stat().st_size < 100_000:
                raise RuntimeError("Falta la interfaz Desktop dentro del ejecutable.")
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                if not playwright.chromium:
                    raise RuntimeError("No se empaquetó el controlador de Chrome.")
            if not app_version():
                raise RuntimeError("The governed native release metadata is missing.")
            server = build_server(Collector(app_home() / "robot-data", app_home() / "instagram-browser"),
                                  "healthcheck-token")
            server.server_close()
            print("PASS: UI embebida, controlador Playwright y servidor local disponibles.")
            return 0

        mutex = acquire_single_instance(developer=args.developer)
        try:
            home = app_home() / "developer-edition" if args.developer else app_home()
            page = prepare_html(source, home / BUNDLED_HTML)
            browser = chrome_path()
            chrome_workspace = home / "workspace-browser"
            chrome_workspace.mkdir(parents=True, exist_ok=True)
            # Keep existing result and Instagram session paths, so an upgrade
            # retains earlier robot results and the signed-in Instagram browser.
            legacy = Path.home() / ".ig-cleaner-pro"
            collector = (Collector(home / "audit-scratch", home / "instagram-browser")
                         if args.developer else
                         Collector(legacy / "profile-counts", legacy / "instagram-browser"))
            token = secrets.token_urlsafe(32)
            updater = (None if args.developer else
                       WindowsUpdater(app_version(), home, legacy / "profile-counts"))
            server = build_server(
                collector, token, 0, updater=updater,
                developer_mode=args.developer, audit_root=legacy / "profile-counts")
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            # Version awareness starts automatically, but never downloads,
            # installs or changes Instagram state without explicit approval.
            if updater is not None:
                updater.check()
            try:
                chrome = subprocess.Popen(chrome_app_args(
                    browser, page, chrome_workspace, server.server_port, token,
                    developer=args.developer))
                chrome.wait()
            finally:
                stop_safely(server)
            return 0
        finally:
            release_single_instance(mutex)
    except Exception as exc:
        alert("Insta Cleaner no pudo iniciarse:\n" + str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
