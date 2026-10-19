"""Persistent, deterministic visit scheduler for the user-controlled local robot.

Two independent limits apply before opening each profile:
  * rolling count of visits within a time window
  * minimum spacing since the previous visit
Every attempted visit consumes a slot, including unavailable/error/blocked.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
from pathlib import Path
import time

MAX_WINDOW_COUNT = 10000
MAX_WINDOW_MINUTES = 1440
MAX_DELAY_SECONDS = 3600
DEFAULT_COUNT = 50
DEFAULT_WINDOW_MINUTES = 60
DEFAULT_DELAY_SECONDS = 72.0


def check_pacing(count, minutes, delay):
    try:
        count_value = int(count)
        minutes_value = int(minutes)
        delay_value = float(delay)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Los límites de consulta deben ser números válidos.") from exc
    if isinstance(count, bool) or isinstance(minutes, bool):
        raise ValueError("El tamaño de tanda y los minutos deben ser enteros.")
    if count_value != count or minutes_value != minutes:
        raise ValueError("El tamaño de tanda y los minutos deben ser enteros.")
    if not 1 <= count_value <= MAX_WINDOW_COUNT:
        raise ValueError("Perfiles por ventana: elige de 1 a 10,000.")
    if not 1 <= minutes_value <= MAX_WINDOW_MINUTES:
        raise ValueError("Ventana: elige de 1 a 1,440 minutos.")
    if not math.isfinite(delay_value) or not 0 <= delay_value <= MAX_DELAY_SECONDS:
        raise ValueError("Espera mínima: elige de 0 a 3,600 segundos.")
    return count_value, minutes_value, delay_value


def _from_iso(stamp):
    try:
        dt_value = dt.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if dt_value.tzinfo is None:
            return None
        return dt_value.timestamp()
    except (TypeError, ValueError, OverflowError):
        return None


def history_path(results_file: Path):
    return results_file.with_suffix(results_file.suffix + ".visits.json")


def load_history(file: Path, previous_results=None, now=None):
    """Upgrade existing result files conservatively when no visit log exists."""
    now = time.time() if now is None else now
    existing_ledger = file.exists()
    if existing_ledger:
        try:
            raw = json.loads(file.read_text(encoding="utf-8"))
            if not isinstance(raw, list):
                raise ValueError("Historial de visitas inválido.")
        except (OSError, ValueError, TypeError) as exc:
            # A damaged file is NOT interpreted as zero history: that would
            # remove user-requested pacing after a crash.
            raise ValueError("No se puede leer el historial de pausas. Conserva el archivo y revisa su estado.") from exc
    else:
        raw = [_from_iso(r.get("checked_at", "")) for r in (previous_results or {}).values()]
    values=[]
    for item in raw:
        if existing_ledger:
            # A syntactically valid JSON array is not necessarily a valid visit
            # ledger. Dropping malformed/future records here silently resets the
            # rate budget, so stop the robot and retain the original bytes.
            if (isinstance(item, bool) or not isinstance(item, (int, float))
                    or not math.isfinite(item) or item <= 0 or item > now + 60):
                raise ValueError(
                    "The saved Profile Counts visit history has invalid or future timestamps. "
                    "The original journal was preserved; resolve the clock/journal issue before restarting."
                )
        if isinstance(item, (int, float)) and not isinstance(item, bool) and math.isfinite(item) and 0 < item <= now + 60:
            if item >= now - MAX_WINDOW_MINUTES * 60:
                values.append(float(item))
    return sorted(values)


def save_history(file: Path, events):
    """Record an attempted visit before navigation, without storing usernames."""
    file.parent.mkdir(parents=True, exist_ok=True)
    temp = file.with_suffix(file.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as out:
        json.dump(events, out, separators=(",", ":"))
        out.flush()
        os.fsync(out.fileno())
    os.replace(temp, file)


def wait_required(events, count: int, minutes: int, delay: float, now=None):
    """Seconds until both limits allow the next profile; no network requests."""
    count, minutes, delay = check_pacing(count, minutes, delay)
    now = time.time() if now is None else now
    recent = sorted(t for t in events if now - minutes * 60 <= t <= now + 60)
    wait_gap = max(0.0, max(events, default=-1e30) + delay - now)
    if len(recent) >= count:
        # The oldest of the most recent COUNT events must leave the window.
        wait_window = max(0.0, recent[-count] + minutes * 60 - now + 0.05)
    else:
        wait_window = 0.0
    return max(wait_gap, wait_window)


def finish_visit(file: Path, events, at=None, *, started_at=None):
    """Close a recorded visit even when a next page was prefetched meanwhile.

    A prefetch must already have its own durable visit slot. Without started_at
    retain the historical last-entry behavior for existing callers.
    """
    if not events:
        raise ValueError("No hay una visita activa para finalizar.")
    at = time.time() if at is None else at
    recent = list(events)
    index = len(recent) - 1
    if started_at is not None:
        indexes = [i for i, timestamp in enumerate(recent) if timestamp == started_at]
        if len(indexes) != 1:
            raise ValueError("El registro de visita cambió; no se puede confirmar su pausa.")
        index = indexes[0]
    recent[index] = max(recent[index], at)
    save_history(file, recent)
    return recent


def register_visit(file: Path, events, at=None):
    at = time.time() if at is None else at
    recent = [stamp for stamp in events if stamp > at - MAX_WINDOW_MINUTES * 60]
    recent.append(at)
    save_history(file, recent)
    return recent

def check_batch_rest(every, minutes):
    try:
        every_value = int(every)
        minutes_value = float(minutes)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("La pausa de tanda debe utilizar números válidos.") from exc
    if (isinstance(every, bool) or every_value != every or
            not math.isfinite(minutes_value)):
        raise ValueError("La pausa de tanda necesita un entero de perfiles y minutos válidos.")
    if every_value == 0 and minutes_value == 0:
        return 0, 0.0
    if not 1 <= every_value <= 10000 or not 0 < minutes_value <= 1440:
        raise ValueError("Pausa de tanda: ambos valores deben ser positivos; perfiles 1–10,000 y minutos hasta 1,440.")
    return every_value, minutes_value


def batch_path(results_file: Path):
    return results_file.with_suffix(results_file.suffix + ".batch.json")


def load_batch_state(path: Path):
    if not path.exists():
        return {"count":0,"rest_until":0.0,"every":0,"minutes":0.0}
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(state, dict) or
                type(state.get("count")) is not int or
                not 0 <= state["count"] <= 10000 or
                isinstance(state.get("rest_until"), bool) or
                not isinstance(state.get("rest_until"), (int, float)) or
                not math.isfinite(state["rest_until"]) or
                state["rest_until"] < 0 or
                type(state.get("every")) is not int or
                isinstance(state.get("minutes"), bool) or
                not isinstance(state.get("minutes"), (int, float)) or
                not math.isfinite(state["minutes"])):
            raise ValueError("Invalid persisted Profile Counts batch-rest state.")
        every, minutes = check_batch_rest(state["every"], state["minutes"])
        if state["count"] > 0 and (not every or state["count"] >= every):
            raise ValueError("Invalid saved batch counter; previous pacing state was preserved.")
        return state
    except (OSError, ValueError, TypeError, KeyError) as exc:
        raise ValueError("El registro local de pausas de tanda está dañado. No se reiniciará automáticamente.") from exc


def save_batch_state(path: Path, state: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as out:
        json.dump(state, out, separators=(",", ":"))
        out.flush()
        os.fsync(out.fileno())
    os.replace(temp, path)


def batch_wait(state: dict, every: int, minutes: float, now=None):
    if not every:
        return 0.0
    now = time.time() if now is None else now
    return max(0.0, float(state.get("rest_until",0)) - now)


def finish_batch_visit(file: Path, state: dict, every: int, minutes: float, now=None):
    """Counts attempted profiles and schedules a long rest each N profiles.

    The counter survives restarts and does not include passwords/usernames.
    A changed batch size begins a new counter while preserving any active rest.
    """
    every, minutes = check_batch_rest(every, minutes)
    if not every:
        return state
    now = time.time() if now is None else now
    matching = state.get("every") == every and state.get("minutes") == minutes
    count = int(state.get("count", 0)) if matching else 0
    count += 1
    until = float(state.get("rest_until", 0))
    if count >= every:
        count = 0
        until = max(until, now + minutes * 60)
    updated={"count":count,"rest_until":until,"every":every,"minutes":minutes}
    save_batch_state(file, updated)
    return updated

