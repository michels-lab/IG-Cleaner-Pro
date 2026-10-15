"""Owner-approved Windows Setup updates for Insta Cleaner Pro.

Read-only anonymous stable GitHub Releases checking is automatic; downloads and
Setup execution are always explicit foreground owner actions. No Instagram,
cookies or relationship state is accessed. Untrusted downloads fail closed.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import threading
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile

RELEASE_API = "https://api.github.com/repos/michels-lab/IG-Cleaner-Pro/releases/latest"
REPO = "michels-lab/IG-Cleaner-Pro"
SETUP_PATTERN = re.compile(r"IG-Cleaner-Pro-Windows-Setup-v(\d+\.\d+)\.exe$")
VERSION = re.compile(r"v(\d+)\.(\d+)$")
SHA = re.compile(r"^[0-9a-fA-F]{64}$")
MAX_SETUP_BYTES = 12 * 1024**3  # Installer artifact safety limit, NOT profile/data limit.


def running_on_windows() -> bool:
    return os.name == "nt"


def numeric_version(value: str) -> tuple[int, int]:
    match = VERSION.fullmatch(str(value or ""))
    if not match:
        raise ValueError("Unknown Windows app version format.")
    return int(match[1]), int(match[2])


def release_setup(release: dict, current: str) -> dict | None:
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("Update feed is not a published stable release.")
    tag = str(release.get("tag_name") or "")
    if numeric_version(tag) <= numeric_version("v" + current):
        return None
    name = f"IG-Cleaner-Pro-Windows-Setup-{tag}.exe"
    assets = release.get("assets", [])
    if not isinstance(assets, list):
        raise ValueError("Invalid GitHub release assets.")
    by_name = {a.get("name"): a for a in assets if isinstance(a, dict)}
    setup, sums = by_name.get(name), by_name.get("SHA256SUMS.txt")
    if setup is None or sums is None:
        raise ValueError("The stable release has no verified Windows Setup yet.")
    prefix = f"https://github.com/{REPO}/releases/download/{tag}/"
    for asset in (setup, sums):
        expected = prefix + asset["name"]
        if asset.get("browser_download_url") != expected:
            raise ValueError("Release asset URL is not in the official product channel.")
    expected_bytes = setup.get("size")
    if type(expected_bytes) is not int or not 1_000_000 <= expected_bytes <= MAX_SETUP_BYTES:
        raise ValueError("Unexpected Setup asset size.")
    return dict(version=tag[1:],tag=tag,name=name,download_url=setup["browser_download_url"],
                sums_url=sums["browser_download_url"],size=expected_bytes,
                notes=str(release.get("body") or "")[:6000],
                release_url=f"https://github.com/{REPO}/releases/tag/{tag}")


def parse_sums(body: str, filename: str) -> str:
    matches = []
    for line in body.splitlines():
        found = re.match(r"^([0-9A-Fa-f]{64})\s+\*?(.+?)\s*$", line)
        if found and found[2] == filename:
            matches.append(found[1].lower())
    if len(matches) != 1 or not SHA.fullmatch(matches[0]):
        raise ValueError("Setup SHA-256 is missing or ambiguous in official release checksums.")
    return matches[0]


def _request(url: str):
    return Request(url, headers={"Accept": "application/vnd.github+json",
                                 "User-Agent": "InstaCleanerPro-Windows-Updater"})


def _allowed_redirect(response) -> bool:
    url = urlparse(response.geturl())
    host = (url.hostname or "").lower()
    return url.scheme == "https" and (
        host == "github.com" or host == "api.github.com"
        or host.endswith(".githubusercontent.com")
    )


def _fetch_text(url: str, limit=1_500_000) -> str:
    with urlopen(_request(url), timeout=25) as response:
        if not _allowed_redirect(response):
            raise ValueError("Update metadata redirected outside GitHub.")
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Update metadata exceeds the maximum safe response size.")
    return data.decode("utf-8-sig")


def _sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            checksum.update(chunk)
    return checksum.hexdigest()


def create_restore_point(destination: Path, local_app_home: Path, robot_results: Path, version: str) -> Path:
    """Snapshot state files, NOT browser passwords, cookie stores or raw ZIPs."""
    destination.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    backup = destination / f"IG-Cleaner-Pro-State-{version}-{timestamp}.zip"
    temp = backup.with_suffix(".zip.partial")
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1) as zipf:
            meta = {"schema":1,"app_version":version,"utc_created":timestamp,
                    "contents":"local UI file and robot result CSV/JSON journals only",
                    "excluded":"Chrome session profiles/cookies and raw Instagram uploads"}
            zipf.writestr("BACKUP-INFO.json", json.dumps(meta))
            ui = local_app_home / "IG-Cleaner-Pro.html"
            if ui.is_file() and not ui.is_symlink():
                zipf.write(ui, arcname="app/IG-Cleaner-Pro.html")
            if robot_results.is_dir():
                for path in robot_results.rglob("*"):
                    if path.is_symlink() or not path.is_file() or path.suffix.lower() not in (".csv",".json",".done"):
                        continue
                    relative = path.relative_to(robot_results)
                    zipf.write(path, arcname=str(Path("robot") / relative).replace("\\", "/"))
        os.replace(temp, backup)
    finally:
        temp.unlink(missing_ok=True)
    return backup


class WindowsUpdater:
    """Thread-safe update manager exposed ONLY via session-token loopback."""
    def __init__(self, current: str, app_home: Path, robot_results: Path):
        numeric_version("v"+current)
        self.current = current
        self.app_home = Path(app_home)
        self.robot_results = Path(robot_results)
        self.lock = threading.RLock()
        self.cancel = threading.Event()
        self.worker = None
        self.candidate = None
        self.expected_sha = None
        self.downloaded = None
        self.state = {"status":"idle","current":current,"latest":None,
                      "progress":0,"message":"Updates have not been checked yet.",
                      "release_url":None,"notes":""}

    def snapshot(self):
        with self.lock:
            return dict(self.state)

    def _set(self, **fields):
        with self.lock:
            self.state.update(fields)

    def _start(self, name, target):
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Another updater operation is still running.")
            self.cancel.clear()
            self._set(status=name,message=name.replace("_"," ").capitalize(),progress=0)
            self.worker = threading.Thread(target=target, daemon=True)
            self.worker.start()
        return self.snapshot()

    def check(self):
        return self._start("checking", self._check)

    def _check(self):
        try:
            release = json.loads(_fetch_text(RELEASE_API))
            info = release_setup(release, self.current)
            if info is None:
                with self.lock:
                    self.candidate = self.expected_sha = self.downloaded = None
                    self._set(status="up_to_date",latest=release.get("tag_name"),
                              message="No newer verified Windows Setup is published.",
                              progress=100,release_url=None,notes="")
                return
            expected = parse_sums(_fetch_text(info["sums_url"]), info["name"])
            with self.lock:
                self.candidate,self.expected_sha,self.downloaded = info, expected, None
                self._set(status="update_available",latest=info["tag"],
                          message="A newer Windows Setup is available. Download requires your approval.",
                          release_url=info["release_url"],notes=info["notes"],progress=0)
        except Exception as exc:
            self._set(status="unavailable",message="Could not verify official update: "+str(exc)[:250])

    def download(self):
        with self.lock:
            if self.state["status"] != "update_available" or not self.candidate or not self.expected_sha:
                raise ValueError("Check for a verified newer Windows Setup before downloading.")
        return self._start("downloading", self._download)

    def _download(self):
        with self.lock:
            info = dict(self.candidate)
            digest = self.expected_sha
        target_dir = self.app_home / "updates"
        target_dir.mkdir(parents=True, exist_ok=True)
        destination = target_dir / info["name"]
        pending = destination.with_suffix(".exe.partial")
        try:
            h = hashlib.sha256()
            received = 0
            with urlopen(_request(info["download_url"]),timeout=45) as response:
                if not _allowed_redirect(response):
                    raise ValueError("Setup download redirected outside GitHub.")
                with pending.open("wb") as file:
                    while chunk := response.read(1024*1024):
                        if self.cancel.is_set():
                            raise InterruptedError("Download cancelled by owner.")
                        received += len(chunk)
                        if received > MAX_SETUP_BYTES or received > info["size"]:
                            raise ValueError("Setup exceeded its declared release size.")
                        h.update(chunk)
                        file.write(chunk)
                        self._set(progress=int(100*received/info["size"]))
                    file.flush()
                    os.fsync(file.fileno())
            if received != info["size"] or h.hexdigest() != digest:
                raise ValueError("Downloaded Setup size or SHA-256 does not match the official release.")
            os.replace(pending, destination)
            with self.lock:
                self.downloaded = destination
                self._set(status="ready_to_install",message="Verified Setup downloaded. Installation needs your confirmation.",progress=100)
        except InterruptedError:
            self._set(status="postponed",message="Download cancelled; no installer launched.")
        except Exception as exc:
            self._set(status="error",message="Update download failed: "+str(exc)[:240])
        finally:
            pending.unlink(missing_ok=True)

    def cancel_download(self):
        self.cancel.set()
        return self.snapshot()

    def install(self):
        with self.lock:
            if self.worker and self.worker.is_alive():
                raise ValueError("Wait for the update download to finish.")
            if self.state["status"] != "ready_to_install" or not self.downloaded or not self.expected_sha:
                raise ValueError("There is no downloaded, verified Setup ready to install.")
            installer,expected = self.downloaded,self.expected_sha
        if not running_on_windows():
            raise RuntimeError("Windows Setup can only be launched on Windows.")
        if _sha256(installer) != expected:
            raise ValueError("The downloaded Setup changed after verification; installation was blocked.")
        backup = create_restore_point(self.app_home/"backups",self.app_home,self.robot_results,self.current)
        try:
            subprocess.Popen([str(installer)],close_fds=True)
        except Exception:
            self._set(status="error",message="Could not launch Windows Setup. User data and backup were preserved.")
            raise
        self._set(status="installer_started",
                  message="Windows Setup started. Complete or cancel its wizard; no installation success is assumed.",
                  notes=f"Local pre-update state backup: {backup.name}")
        return self.snapshot()
