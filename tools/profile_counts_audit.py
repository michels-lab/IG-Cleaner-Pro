"""Crash-resumable, owner-scoped oldest-first Windows Profile Counts audits.

No Instagram login, scraping, or relationship mutation occurs here. A cycle is
created only by an explicit user action, then journaled after every attempted
profile. Unmeasured profiles precede oldest successful measurements.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
from pathlib import Path

COLUMNS = ("username", "followers", "following", "checked_at", "source", "status", "approximate")


def audit_cycle_path(results_path: Path) -> Path:
    return results_path.with_suffix(".reaudit.json")


def dated_history_path(results_path: Path) -> Path:
    return results_path.with_suffix(".dated.csv")


def _stamp(row: dict) -> dt.datetime:
    try:
        date = dt.datetime.fromisoformat(str(row.get("checked_at", "")).replace("Z", "+00:00"))
        return date if date.tzinfo else date.replace(tzinfo=dt.timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return dt.datetime.min.replace(tzinfo=dt.timezone.utc)


def ordered_audit_targets(usernames: list[str], saved: dict) -> list[str]:
    """Whole imported queue, prioritizing never-successful; oldest successful last."""
    unique = list(dict.fromkeys(usernames))
    original = {u: i for i, u in enumerate(unique)}
    return sorted(unique, key=lambda u: (
        0 if saved.get(u, {}).get("status") != "ok" else 1,
        _stamp(saved.get(u, {})), original[u]
    ))


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".new")
    try:
        with temp.open("w", encoding="utf-8") as file:
            json.dump(value, file, ensure_ascii=False, separators=(",", ":"))
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def new_cycle(path: Path, usernames: list[str], saved: dict) -> dict:
    cycle = {
        "schema": "igc-profile-reaudit-v1",
        "mode": "oldest_first",
        "targets": ordered_audit_targets(usernames, saved),
        "done": [],
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    }
    _atomic_json(path, cycle)
    return cycle


def resume_cycle(path: Path, usernames: list[str]) -> dict:
    if not path.is_file():
        raise ValueError("The saved re-audit cycle was not found. Start a new cycle explicitly.")
    with path.open("r", encoding="utf-8") as file:
        cycle = json.load(file)
    allowed = set(usernames)
    targets = cycle.get("targets", [])
    done = cycle.get("done", [])
    if (cycle.get("schema") != "igc-profile-reaudit-v1" or cycle.get("mode") != "oldest_first"
        or not isinstance(targets, list) or not isinstance(done, list)
        or len(targets) != len(set(targets)) or any(u not in allowed for u in targets)
        or any(u not in targets for u in done) or len(done) != len(set(done))):
        raise ValueError("The saved re-audit queue differs from this Instagram workspace; start a new cycle.")
    return cycle


def mark_attempt(path: Path, cycle: dict, username: str) -> dict:
    if username not in cycle["targets"]:
        raise ValueError("Cannot record an unselected audit profile.")
    if username not in cycle["done"]:
        cycle["done"].append(username)
        _atomic_json(path, cycle)
    return cycle


def append_dated_reading(path: Path, row: dict) -> None:
    """Append successes only. Preserve historical data; never wipe old readings."""
    if row.get("status") != "ok" or any(str(row.get(k, "")) == "" for k in
                                           ("username", "followers", "following", "checked_at")):
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS, extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerow(row)
        file.flush()
        os.fsync(file.fileno())


def seed_latest_readings(path: Path, saved: dict) -> int:
    """Migrate old one-reading-per-profile Windows results without losing dates.

    Safe to repeat after interruptions: append only missing dated successes.
    The old latest-results CSV stays unmodified.
    """
    seen = set()
    if path.is_file():
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            for row in csv.DictReader(source):
                seen.add(tuple(str(row.get(k, "")) for k in
                               ("username", "checked_at", "followers", "following")))
    additions = []
    for row in saved.values():
        if row.get("status") != "ok" or any(not str(row.get(k, "")) for k in
                                               ("username", "checked_at", "followers", "following")):
            continue
        identity = tuple(str(row.get(k, "")) for k in
                         ("username", "checked_at", "followers", "following"))
        if identity not in seen:
            additions.append(row)
            seen.add(identity)
    if not additions:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    is_new = not path.exists() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=COLUMNS, extrasaction="ignore")
        if is_new:
            writer.writeheader()
        writer.writerows(additions)
        target.flush()
        os.fsync(target.fileno())
    return len(additions)


def read_dated_page(path: Path, offset: int, size: int) -> dict:
    if not isinstance(offset, int) or not isinstance(size, int) or offset < 0 or not 1 <= size <= 2000:
        raise ValueError("History pagination must use a nonnegative offset and size 1–2,000.")
    if not path.exists():
        return {"rows": [], "next_offset": None}
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        import itertools
        segment = list(itertools.islice(reader, offset, offset + size + 1))
    more = len(segment) > size
    return {"rows": segment[:size], "next_offset": offset + size if more else None}
