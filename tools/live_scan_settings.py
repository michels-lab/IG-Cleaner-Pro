"""Versioned, bounded settings for read-only bulk Instagram list collection.

The reference Webpack script used persisted timing controls, request cycles
and safety rests. This original implementation exposes only the relevant
*read-only list* controls, not Unfollow timing, and NEVER lets Custom weaken
the built-in recommended safety floor. Presets are not official Meta quotas.
"""
from __future__ import annotations

import math

SCHEMA = "igc-live-bulk-settings-v1"
FIELDS = ("page_size", "page_delay_ms", "short_every", "short_rest_ms",
          "long_every", "long_rest_ms", "repeat_minutes")
DEFAULTS = {
    "page_size": 200, "page_delay_ms": 2500,
    "short_every": 5, "short_rest_ms": 12000,
    "long_every": 25, "long_rest_ms": 90000,
    "repeat_minutes": 15,
}
PRESETS = {
    "recommended": dict(DEFAULTS),
    "cautious": {
        "page_size": 100, "page_delay_ms": 5000,
        "short_every": 5, "short_rest_ms": 25000,
        "long_every": 20, "long_rest_ms": 180000,
        "repeat_minutes": 30,
    },
}
# Bounds are app product guardrails, not Instagram API permissions.
LIMITS = {
    "page_size": (25, 200),
    "page_delay_ms": (2500, 30000),
    "short_every": (2, 5),
    "short_rest_ms": (12000, 180000),
    "long_every": (10, 25),
    "long_rest_ms": (90000, 600000),
    "repeat_minutes": (15, 180),
}


def validate_settings(value):
    """Reject malformed, unsupported or less-safe settings atomically."""
    if not isinstance(value, dict):
        raise ValueError("Choose a validated Instagram read-only scan settings profile.")
    profile = value.get("preset")
    if profile in PRESETS:
        if set(value) - {"preset", "values"}:
            raise ValueError("Unknown Instagram safety settings.")
        # The preset cannot be altered via arbitrary client-provided values.
        if "values" in value and value["values"] not in ({}, None, PRESETS[profile]):
            raise ValueError("Preset values must match the protected server defaults.")
        return {"schema": SCHEMA, "preset": profile, "values": dict(PRESETS[profile])}
    if profile != "custom":
        raise ValueError("Select Recommended, Cautious or Custom.")
    values = value.get("values")
    if not isinstance(values, dict) or set(values) != set(FIELDS):
        raise ValueError("All seven Custom safeguards must be set.")
    clean = {}
    for name in FIELDS:
        v = values[name]
        lo, hi = LIMITS[name]
        if type(v) is not int or not lo <= v <= hi:
            raise ValueError(name + " must be a whole number between " + str(lo) +
                             " and " + str(hi) + ".")
        clean[name] = v
    if clean["long_every"] <= clean["short_every"]:
        raise ValueError("The long rest must follow more pages than the short rest.")
    if clean["long_rest_ms"] < clean["short_rest_ms"]:
        raise ValueError("The long rest must not be shorter than the short rest.")
    return {"schema": SCHEMA, "preset": "custom", "values": clean}


def effective_settings(saved):
    """Untrusted or obsolete saved settings safely fall back to Recommended."""
    if not isinstance(saved, dict) or saved.get("schema") != SCHEMA:
        return validate_settings({"preset": "recommended"})
    try:
        return validate_settings({"preset": saved.get("preset"),
                                  "values": saved.get("values")})
    except (TypeError, ValueError, OverflowError):
        return validate_settings({"preset": "recommended"})
