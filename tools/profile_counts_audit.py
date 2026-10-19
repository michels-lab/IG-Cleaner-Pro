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
import re
import secrets
from pathlib import Path

COLUMNS = ("username", "followers", "following", "checked_at", "source", "status", "approximate")
USERNAME = re.compile(r"[A-Za-z0-9._]{1,30}\\Z")
INTEGER_COUNT = re.compile(r"[0-9]+\\Z")


def _valid_reading(row: dict) -> bool:
    """Only fully evidenced success rows can enter dated history or count as measured.

    Historical CSVs can have malformed 'ok' records. Never fabricate a zero,
    reinterpret a compact count or overwrite older valid readings with them.
    """
    if not isinstance(row, dict) or row.get("status") != "ok":
        return False
    name = str(row.get("username") or "")
    if not USERNAME.fullmatch(name):
        return False
    for key in ("followers", "following"):
        value = str(row.get(key) if row.get(key) is not None else "")
        if not INTEGER_COUNT.fullmatch(value):
            return False
    try:
        checked = dt.datetime.fromisoformat(str(row.get("checked_at") or "").replace("Z", "+00:00"))
    except (TypeError, ValueError, OverflowError):
        return False
    if checked.tzinfo is None or checked.utcoffset() is None:
        return False
    return checked.astimezone(dt.timezone.utc) <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=60)


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
        0 if not _valid_reading(saved.get(u, {})) else 1,
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


def _done_path(path: Path, cycle: dict) -> Path:
    """Stable cycle-specific append-only completion log, never a per-visit rewrite."""
    identity = cycle.get("cycle_id")
    if not isinstance(identity, str) or not re.fullmatch(r"[0-9a-f]{24}", identity):
        raise ValueError("Corrupted audit cycle identifier; no history was overwritten.")
    return path.with_name(path.name + "." + identity + ".done")


def _runtime(cycle: dict, done: list[str]) -> dict:
    cycle["done"] = done
    cycle["_done_lookup"] = set(done)
    cycle["_target_lookup"] = set(cycle["targets"])
    return cycle


def new_cycle(path: Path, usernames: list[str], saved: dict) -> dict:
    # Old completion logs are kept unchanged for recovery. The new cycle's
    # random ID ensures it never reuses a prior append-only log.
    manifest = {
        "schema": "igc-profile-reaudit-v1",
        "mode": "oldest_first",
        "cycle_id": secrets.token_hex(12),
        "targets": ordered_audit_targets(usernames, saved),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    }
    _atomic_json(path, manifest)
    return _runtime(manifest, [])


def resume_cycle(path: Path, usernames: list[str]) -> dict:
    if not path.is_file():
        raise ValueError("The saved re-audit cycle was not found. Start a new cycle explicitly.")
    with path.open("r", encoding="utf-8") as file:
        cycle = json.load(file)
    allowed = set(usernames)
    targets = cycle.get("targets", [])
    if (cycle.get("schema") != "igc-profile-reaudit-v1" or cycle.get("mode") != "oldest_first"
        or not isinstance(targets, list)
        or len(targets) != len(set(targets)) or any(u not in allowed for u in targets)):
        raise ValueError("The saved re-audit queue differs from this Instagram workspace; start a new cycle.")
    done_file = _done_path(path, cycle)
    if done_file.is_file():
        with done_file.open("r", encoding="utf-8") as saved:
            done = saved.read().splitlines()
    else:
        done = []
    target_set = set(targets)
    if len(done) != len(set(done)) or any(u not in target_set for u in done):
        raise ValueError("The saved re-audit progress log is invalid. No counts were deleted.")
    return _runtime(cycle, done)


def mark_attempt(path: Path, cycle: dict, username: str) -> dict:
    if username not in cycle["_target_lookup"]:
        raise ValueError("Cannot record an unselected audit profile.")
    if username in cycle["_done_lookup"]:
        return cycle
    done_file = _done_path(path, cycle)
    done_file.parent.mkdir(parents=True, exist_ok=True)
    with done_file.open("a", encoding="utf-8", newline="\n") as output:
        output.write(username + "\n")
        output.flush()
        os.fsync(output.fileno())
    cycle["done"].append(username)
    cycle["_done_lookup"].add(username)
    return cycle


def append_dated_reading(path: Path, row: dict) -> None:
    """Append successes only. Preserve historical data; never wipe old readings."""
    if not _valid_reading(row):
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
        if not _valid_reading(row):
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
