#!/usr/bin/env python3
"""Visible, user-session browser collector for IG Cleaner Pro.

Reads only displayed Instagram profile count labels. No Instagram private APIs,
password capture, anti-bot bypass, automatic follow/unfollow, or hidden endpoints.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlparse

try:
    # tests import tools.profile_counts_robot, whereas the portable launcher
    # imports profile_counts_robot from its own script directory.
    from .profile_counts_pacing import (check_pacing, history_path, load_history, register_visit, finish_visit,
                                        wait_required, DEFAULT_COUNT, DEFAULT_WINDOW_MINUTES,
                                        DEFAULT_DELAY_SECONDS,
                                        check_batch_rest, batch_path, load_batch_state, batch_wait, finish_batch_visit)
except ImportError:
    from profile_counts_pacing import (check_pacing, history_path, load_history, register_visit, finish_visit,
                                       wait_required, DEFAULT_COUNT, DEFAULT_WINDOW_MINUTES,
                                       DEFAULT_DELAY_SECONDS,
                                       check_batch_rest, batch_path, load_batch_state, batch_wait, finish_batch_visit)

FIELDS = ("username", "followers", "following", "checked_at", "source", "status", "approximate")
USERNAME = re.compile(r"^[A-Za-z0-9._]{1,30}$")
LABEL = {
    "followers": r"(?:followers?|seguidores?|abonnés|follower)",
    "following": r"(?:following|seguidos?|seguidas?|abonnements|abbonamenti)",
}
BLOCK_MARKERS = (
    "challenge_required", "suspicious login", "confirm it's you",
    "confirm it's you", "verify your identity", "try again later",
    "wait a few minutes", "help us confirm", "checkpoint_required",
    "confirma que eres tú", "inténtalo de nuevo más tarde",
)
UNAVAILABLE_MARKERS = (
    "sorry, this page isn't available", "this page isn't available",
    "esta página no está disponible", "page not found",
)


def parse_number(raw: str):
    """Return (count, approximate). Refuse impossible/ambiguous values."""
    value = re.sub(r"\s+", "", raw.strip()).lower().replace("\u202f", "")
    value = value.replace("\u00a0", "")
    factor = 1
    suffix = re.search(r"(mil|millones|million|m|k)$", value, re.I)
    if suffix:
        unit = suffix.group(1).lower()
        factor = 1000000 if unit in ("millones", "million", "m") else 1000
        value = value[:-len(suffix.group(1))]
    if not re.fullmatch(r"\d[\d.,]*", value):
        return None
    if factor > 1:
        # "12,3K" / "12.3K" represent rounded, approximate counts.
        decimal = value.replace(",", ".")
        if decimal.count(".") > 1:
            return None
        return round(float(decimal) * factor), True
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", value):
        return int(value.replace(",", "").replace(".", "")), False
    if re.fullmatch(r"\d+", value):
        return int(value), False
    return None


def parse_profile_counts(*texts: str):
    """Extract only two independently visible counts from header/meta labels."""
    for text in texts:
        found = {}
        for target, label in LABEL.items():
            patterns = (
                rf"(?<!\w)([\d][\d.,\s\u00a0\u202f]*(?:[kKmM]|[ ]mil|[ ]millones)?)\s+{label}\b",
                rf"\b{label}\b\s*:?\s*([\d][\d.,\s\u00a0\u202f]*(?:[kKmM]|[ ]mil|[ ]millones)?)",
            )
            for pattern in patterns:
                for match in re.finditer(pattern, text or "", re.IGNORECASE):
                    parsed = parse_number(match.group(1))
                    if parsed is not None:
                        found[target] = parsed
                        break
                if target in found:
                    break
        if len(found) == 2:
            return found["followers"][0], found["following"][0], (found["followers"][1] or found["following"][1])
    return None


def valid_username(raw):
    value = str(raw or "").strip().lstrip("@")
    # 'http.cat', 'httpshop' and similar are valid Instagram handles.
    # Only a real absolute URL with scheme delimiter should be parsed as one.
    if value.lower().startswith(("http://", "https://")):
        parsed = urlparse(value)
        if parsed.hostname not in ("www.instagram.com", "instagram.com"):
            return None
        value = parsed.path.strip("/").split("/")[0]
    return value.lower() if USERNAME.fullmatch(value) else None


def read_queue(path: Path):
    if not path.is_file():
        raise ValueError(f"Profile queue file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("The CSV is empty.")
        keys = {k.lower().strip(): k for k in reader.fieldnames}
        column = next((keys[k] for k in ("username", "usuario", "profile", "perfil") if k in keys), None)
        if not column:
            raise ValueError("The Insta Cleaner CSV must contain a username column.")
        seen, usernames = set(), []
        for row in reader:
            user = valid_username(row.get(column))
            if user and user not in seen:
                usernames.append(user)
                seen.add(user)
        return usernames


def read_results(path: Path):
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return {r["username"]: r for r in csv.DictReader(f) if valid_username(r.get("username"))}


def save_results(path: Path, results: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results[u] for u in sorted(results))
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


def iso_now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def seconds_since(iso):
    try:
        value = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (dt.datetime.now(dt.timezone.utc) - value).total_seconds()
    except (ValueError, TypeError):
        return float("inf")


def last_visit(results):
    return max((r.get("checked_at", "") for r in results.values()), default="")


def collect_visible_counts(page, username: str):
    """Navigates an ordinary page and reads rendered labels, never web APIs."""
    try:
        page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=45000)
        page.wait_for_timeout(1800)
        page_text = page.locator("body").inner_text(timeout=10000)
        lowered = page_text.lower()
        if any(token in lowered for token in BLOCK_MARKERS):
            return "blocked", None
        # Login forms are localized; do not depend on the English "log in" label.
        if page.locator('input[name="password"]').count():
            return "login_required", None
        if any(token in lowered for token in UNAVAILABLE_MARKERS):
            return "unavailable", None
        header = page.locator("header").first
        header_text = header.inner_text(timeout=4500) if header.count() else ""
        description = page.locator('meta[name="description"]').first
        meta_text = description.get_attribute("content") if description.count() else ""
        counts = parse_profile_counts(header_text, meta_text)
        if counts:
            return "ok", counts
        return "unavailable", None
    except Exception:
        # Network errors and DOM shifts are explicitly not interpreted as zero.
        return "error", None


def run(args):
    usernames = read_queue(args.input)
    if not usernames:
        raise ValueError("The file contains no valid usernames.")
    results = read_results(args.output)
    max_count, window_minutes, min_delay = check_pacing(
        args.max_per_window if args.max_per_window is not None else args.per_hour,
        args.window_minutes, args.min_delay_seconds)
    visits_file = history_path(args.output)
    visits = load_history(visits_file, results)
    pause_every, pause_minutes = check_batch_rest(args.pause_every, args.pause_minutes)
    rests_file = batch_path(args.output)
    rests = load_batch_state(rests_file)
    pending = [u for u in usernames if u not in results or
               (args.retry_unavailable and results[u].get("status") in ("error", "unavailable", "login_required"))]
    if args.max_profiles:
        pending = pending[:args.max_profiles]
    print(f"Profiles queued: {len(usernames)}. Remaining in this run: {len(pending)}.")
    print(f"Results saved to {args.output}. Resuming will preserve earlier records.")
    if not pending:
        return 0
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise ValueError("Install Playwright with: python -m pip install playwright && python -m playwright install chromium") from e

    args.session_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch_persistent_context(
            user_data_dir=str(args.session_dir),
            headless=False,
            viewport={"width": 1180, "height": 860},
        )
        try:
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=45000)
            print("Sign in to Instagram in this window if needed.")
            input("Once your account is ready, return to this terminal and press Enter to start: ")
            for index, username in enumerate(pending, 1):
                while True:
                    waiting = max(wait_required(visits, max_count, window_minutes, min_delay),
                                  batch_wait(rests, pause_every, pause_minutes))
                    if waiting <= 0:
                        break
                    print(f"Pausa programada antes de @{username}: {waiting:.1f} segundos.")
                    time.sleep(waiting)
                visits = register_visit(visits_file, visits)
                try:
                    status, counts = collect_visible_counts(page, username)
                finally:
                    visits = finish_visit(visits_file, visits)
                    rests = finish_batch_visit(rests_file, rests, pause_every, pause_minutes)
                stamp = iso_now()
                if status in ("blocked", "login_required"):
                    print(f"Stopped at @{username}: {status}. Manual review required; challenges will not be bypassed.")
                    # Do not retry automatically. Stop rather than hammering Instagram.
                    break
                row = dict(username=username, followers="", following="", checked_at=stamp,
                           source="instagram_visible_profile_browser", status=status, approximate="false")
                if counts:
                    row.update(followers=str(counts[0]), following=str(counts[1]),
                               approximate=str(bool(counts[2])).lower())
                results[username] = row
                save_results(args.output, results)
                print(f"[{index}/{len(pending)}] @{username}: {row['followers'] or '—'} followers, "
                      f"{row['following'] or '—'} following ({status})")
        finally:
            browser.close()
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Collect visible Instagram profile counts using a local browser and your own session.")
    parser.add_argument("--input", required=True, type=Path, help="CSV exported by Insta Cleaner (username,profile_url).")
    parser.add_argument("--output", type=Path, default=Path("profile_counts_results.csv"), help="Persistent results and progress CSV.")
    parser.add_argument("--per-hour", type=int, default=DEFAULT_COUNT, help="Legacy compatibility: hourly maximum if --max-per-window is omitted.")
    parser.add_argument("--max-per-window", type=int, help="Maximum profile visits per window (1 to 10,000).")
    parser.add_argument("--window-minutes", type=int, default=DEFAULT_WINDOW_MINUTES, help="Pacing window length in minutes (1 to 1,440).")
    parser.add_argument("--min-delay-seconds", type=float, default=DEFAULT_DELAY_SECONDS, help="Minimum delay between profile visits in seconds (0 to 3,600).")
    parser.add_argument("--pause-every", type=int, default=0, help="Optional longer break after every N profiles; 0 disables it.")
    parser.add_argument("--pause-minutes", type=float, default=0, help="Duration of each longer break, in minutes; 0 disables it.")
    parser.add_argument("--max-profiles", type=int, default=0, help="0: all pending profiles; otherwise limit profiles per run.")
    parser.add_argument("--session-dir", type=Path, default=Path.home()/".ig-cleaner-pro"/"instagram-browser",
                        help="Local browser session folder. Treat this as private data.")
    parser.add_argument("--retry-unavailable", action="store_true", help="Revisit errors and unavailable profiles; never repeat successful results.")
    args = parser.parse_args(argv)
    try:
        check_pacing(args.max_per_window if args.max_per_window is not None else args.per_hour,
                     args.window_minutes, args.min_delay_seconds)
        check_batch_rest(args.pause_every, args.pause_minutes)
    except ValueError as exc:
        parser.error(str(exc))
    if args.max_profiles < 0:
        parser.error("--max-profiles cannot be negative")
    try:
        return run(args)
    except (ValueError, KeyboardInterrupt) as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
