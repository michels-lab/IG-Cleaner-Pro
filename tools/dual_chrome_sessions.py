"""Two independent persistent Chrome logins for manual Instagram inspection.

Not parallel relationship-changing robots; action WAL and leases stay unchanged.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import threading
from pathlib import Path

try:
    from .profile_counts_robot import valid_username
except ImportError:
    from profile_counts_robot import valid_username

ACCOUNT_KEY = re.compile(r"^(legacy|ig_[a-z0-9_-]{8,64})$")
APP_OWNER = re.compile(r"^u_[a-z0-9]+_[0-9]{1,4}$")


def installed_chrome():
    paths = [shutil.which("chrome.exe"), shutil.which("chrome")]
    for key in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        if os.environ.get(key):
            paths.append(str(Path(os.environ[key]) / "Google" / "Chrome" / "Application" / "chrome.exe"))
    for path in paths:
        if path and Path(path).is_file():
            return Path(path)
    raise ValueError("Google Chrome is required for isolated Instagram windows.")


class DualChromeSessions:
    """Each app owner + Instagram workspace gets a different user-data-dir."""

    def __init__(self, data_dir, *, chrome_locator=installed_chrome, launcher=subprocess.Popen):
        self.root = Path(data_dir) / "isolated-instagram-sessions-v1"
        self.chrome_locator = chrome_locator
        self.launcher = launcher
        self.lock = threading.RLock()

    @staticmethod
    def _workspace(item):
        if not isinstance(item, dict):
            raise ValueError("Select two Instagram workspaces.")
        key, raw_handle = item.get("account"), item.get("expected_handle")
        if not isinstance(key, str) or not ACCOUNT_KEY.fullmatch(key):
            raise ValueError("Invalid Instagram workspace identifier.")
        if not isinstance(raw_handle, str) or not raw_handle or valid_username(raw_handle) != raw_handle.lower():
            raise ValueError("Select a valid Instagram @username for each workspace.")
        return key, valid_username(raw_handle)

    def directory(self, owner, account):
        digest = hashlib.sha256((owner + "\0" + account).encode("utf-8")).hexdigest()[:32]
        return self.root / digest

    def open_pair(self, data):
        owner = data.get("owner")
        if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
            raise ValueError("Sign in to InstaCleaner before opening two Chrome sessions.")
        primary, secondary = self._workspace(data.get("primary")), self._workspace(data.get("secondary"))
        if primary[0] == secondary[0] or primary[1] == secondary[1]:
            raise ValueError("Select different Instagram workspaces and different usernames.")
        if (data.get("read_only_consent") is not True or
                data.get("confirmation") != "dual-chrome:" + primary[0] + ":" + secondary[0]):
            raise ValueError("Confirm both Instagram accounts before opening Chrome.")
        left = self.directory(owner, primary[0])
        right = self.directory(owner, secondary[0])
        if left == right or left.resolve() == right.resolve():
            raise ValueError("Chrome profile directory collision.")
        chrome = self.chrome_locator()
        with self.lock:
            # Do not touch the existing robot's persisted Chrome session.
            left.mkdir(parents=True, exist_ok=True)
            right.mkdir(parents=True, exist_ok=True)
            def args(folder):
                return [str(chrome), "--no-first-run", "--no-default-browser-check",
                        "--new-window", "--user-data-dir=" + str(folder),
                        "https://www.instagram.com/"]
            self.launcher(args(left))
            try:
                self.launcher(args(right))
            except Exception as exc:
                raise ValueError("Chrome window B did not launch after window A. No 
                                 "Instagram action was performed.") from exc
        return {"status": "launched", "windows_requested": 2, "owner": owner,
                "accounts": [primary[0], secondary[0]], "handles": [primary[1], secondary[1]],
                "distinct_chrome_profiles": True, "actions_enabled": False,
                "note": "Login manually in both separate Chrome windows and verify the account "
                        "in each. Automated relationship actions remain serialized."}
