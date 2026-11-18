#!/usr/bin/env python3
"""Select one complete real Android visual artifact from an exact workflow run.

A cancelled workflow attempt can leave a tiny artifact with the SAME name as
the later successful rerun. Selecting by name alone can download the empty one.
This selects by verified metadata only; the downstream APK/screenshot hash gate
still validates every file. Ambiguity is an error, never a guess.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

MIN_COMPLETE_BYTES = 1_000_000


def select_artifact_id(payload: dict, expected_name: str, run_id: int) -> int:
    artifacts = payload.get("artifacts") if isinstance(payload, dict) else None
    if not isinstance(artifacts, list) or not expected_name or not isinstance(run_id, int) or run_id <= 0:
        raise ValueError("Malformed GitHub artifact metadata or expected run")
    candidates = []
    for artifact in artifacts:
        if not isinstance(artifact, dict) or artifact.get("name") != expected_name:
            continue
        identity = artifact.get("workflow_run")
        if isinstance(identity, dict) and identity.get("id") != run_id:
            continue
        if artifact.get("expired") is not False:
            continue
        artifact_id = artifact.get("id")
        size = artifact.get("size_in_bytes")
        if type(artifact_id) is not int or artifact_id <= 0 or type(size) is not int:
            continue
        if size > MIN_COMPLETE_BYTES:
            candidates.append(artifact_id)
    if len(candidates) != 1:
        raise ValueError(
            "Expected exactly one complete Android screenshot artifact for "
            "the exact run; an empty, duplicate or missing artifact blocks release"
        )
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--run", required=True, type=int)
    args = parser.parse_args()
    payload = json.loads(args.metadata.read_text(encoding="utf-8"))
    print(select_artifact_id(payload, args.name, args.run))


if __name__ == "__main__":
    main()
