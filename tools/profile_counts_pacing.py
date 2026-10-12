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
    if file.exists():
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


def finish_visit(file: Path, events, at=None):
    """Anchor the minimum inter-profile pause to the END of the prior visit.

    An attempted visit was already written before navigation, so a crash
    cannot erase its budget. After the page returns, extend the latest
    timestamp to the completion moment, making the real pause explicit.
    """
    if not events:
        raise ValueError("No hay una visita activa para finalizar.")
    at = time.time() if at is None else at
    recent = list(events)
    recent[-1] = max(recent[-1], at)
    save_history(file, recent)
    return recent


def register_visit(file: Path, events, at=None):
    at = time.time() if at is None else at
    recent = [stamp for stamp in events if stamp > at - MAX_WINDOW_MINUTES * 60]
    recent.append(at)
    save_history(file, recent)
    return recent
