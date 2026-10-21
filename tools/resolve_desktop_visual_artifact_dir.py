#!/usr/bin/env python3
"""Locate exact-commit Desktop visual proof inside a downloaded GitHub artifact.

actions/upload-artifact uses the least common ancestor of its multi-folder
paths. One archived layout contains manifest.json at the download root;
the other retains the original desktop-visual/ directory. Never generate or
silently substitute missing evidence; all screenshot hashes are checked later.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def evidence_root(download: Path) -> Path:
    base = Path(download)
    if not base.is_dir() or base.is_symlink():
        raise ValueError("Desktop visual artifact directory is missing or linked")
    candidates = (base, base / "desktop-visual")
    valid = []
    for candidate in candidates:
        if candidate.is_symlink() or not candidate.is_dir():
            continue
        paths = (candidate / "manifest.json", candidate / "michelslab-manifest.json")
        if all(p.is_file() and not p.is_symlink() for p in paths):
            valid.append(candidate)
    if len(valid) != 1:
        raise ValueError(
            "Expected exactly one complete, real Desktop screenshot evidence "
            "folder (flat or desktop-visual/); no fallback to simulated evidence.")
    resolved_base = base.resolve()
    resolved = valid[0].resolve()
    if not resolved.is_relative_to(resolved_base):
        raise ValueError("Desktop evidence may not escape the downloaded artifact")
    return resolved


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True, type=Path)
    args = parser.parse_args()
    print(evidence_root(args.artifact))


if __name__ == "__main__":
    main()
