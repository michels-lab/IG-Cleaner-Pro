#!/usr/bin/env python3
"""Extract the APK signer certificate SHA-256 from apksigner --print-certs output."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_CERT_SHA256 = re.compile(r"certificate SHA-256 digest:\s*([0-9A-Fa-f:]+)")


def extract_certificate_sha256(text: str) -> str:
    """Return the first valid certificate SHA-256 digest, normalized to lowercase hex."""

    for match in _CERT_SHA256.finditer(text):
        normalized = match.group(1).replace(":", "").lower()
        if len(normalized) == 64 and all(ch in "0123456789abcdef" for ch in normalized):
            return normalized
    raise ValueError("apksigner output did not contain a valid certificate SHA-256 digest")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <apksigner-output-file|->", file=sys.stderr)
        return 2

    source = argv[1]
    text = sys.stdin.read() if source == "-" else Path(source).read_text(encoding="utf-8")
    try:
        print(extract_certificate_sha256(text))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
