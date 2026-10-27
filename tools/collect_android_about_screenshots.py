#!/usr/bin/env python3
"""Transfer real installed-Android UI PNG evidence without scoped-storage adb pull.

Only a debug APK signed for emulator testing supports "run-as"; this helper
never accesses production app sessions or Android release signing material.
"""
import argparse
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

EXPECTED = tuple(
    f"{surface}-{viewport}-{section}.png"
    for viewport in ("compact", "wide")
    for surface, sections in (
        ("home", ("initial",)),
        ("about", ("complete",)),
    )
    for section in sections
)
SIZES = {"compact": (720, 1280), "wide": (1080, 1920)}
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def collect(adb: str, package: str, output: Path) -> tuple[Path, ...]:
    """Atomically publish exactly four DISTINCT surface/viewport APK-backed screenshots, never partials."""
    if output.exists():
        raise ValueError(f"Refusing stale Android screenshot output: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".android-evidence-", dir=output.parent))
    transferred = []
    try:
        for filename in EXPECTED:
            command = [
                adb, "exec-out", "run-as", package,
                "cat", f"files/igc-ui-capture/{filename}",
            ]
            try:
                result = subprocess.run(command, capture_output=True, check=False, timeout=30)
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise RuntimeError(f"Could not transfer installed screenshot {filename}: {exc}") from exc
            if result.returncode != 0:
                err = result.stderr.decode("utf-8", errors="replace").strip()
                raise RuntimeError(
                    f"Debug-app private screenshot {filename} unavailable "
                    f"(adb exit {result.returncode}): {err[:500]}"
                )
            data = result.stdout
            if len(data) <= 3000 or not data.startswith(PNG_MAGIC) or data[12:16] != b"IHDR":
                raise ValueError(f"Missing, tiny or invalid PNG evidence: {filename}")
            dims = struct.unpack(">II", data[16:24])
            viewport = filename.split("-")[1]
            if dims != SIZES[viewport]:
                raise ValueError(f"Wrong actual Android viewport for {filename}: {dims}")
            (staging / filename).write_bytes(data)
            transferred.append(filename)
        if len(transferred) != 8:
            raise RuntimeError("Expected four installed APK Home/About screenshots")
        os.replace(staging, output)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return tuple(output / name for name in transferred)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--package", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    screenshots = collect(args.adb, args.package, args.out)
    print(f"SUCCESS: {len(screenshots)} private-app screenshot PNGs transferred; "
          "independent nonblank and APK-hash visual validation remains required.")


if __name__ == "__main__":
    main()
