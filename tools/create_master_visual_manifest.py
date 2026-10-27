#!/usr/bin/env python3
"""Adapt existing, real IG Cleaner screenshots to the studio's shared UI gate.

The source manifests retain complete platform-specific evidence. This adapter
selects a nonduplicated Home/About representative at each viewport and binds
them to the exact tested runtime artifact; it never creates screenshots.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def create_manifest(platform: str, source: Path, artifact: Path, source_sha: str) -> dict:
    document = json.loads(source.read_text(encoding="utf-8"))
    if len(source_sha) != 40 or any(c not in "0123456789abcdef" for c in source_sha.lower()):
        raise ValueError("Full 40-character source SHA required")
    if document.get("source_commit", "").lower() != source_sha.lower():
        raise ValueError("Existing runtime screenshots belong to a different source commit")
    if not artifact.is_file():
        raise ValueError("Actual runtime candidate artifact is missing")
    artifact_hash = digest(artifact)
    expected_schema = {
        "android": "michelslab-rendered-ui-v1",
        "desktop": "igc-desktop-runtime-visual-v1",
    }[platform]
    if document.get("schema") != expected_schema:
        raise ValueError("Unexpected source evidence format")
    expected_hash = (
        document.get("artifact_sha256", {}).get("android") if platform == "android"
        else document.get("html_sha256")
    )
    if expected_hash != artifact_hash:
        raise ValueError("Screenshots are not bound to this exact runtime artifact")

    base = source.resolve().parent
    prefix = Path("android/igc-ui-capture") if platform == "android" else Path()
    screenshots = []
    # Android instrumentation now captures precisely Home+complete About per size.
    # Reject stale old eight-frame manifests rather than ignoring obsolete frames.
    if platform == "android" and len(document.get("screenshots", [])) != 4:
        raise ValueError("Expected exactly four distinct real Android Home/About screenshots")
    seen_digests = set()
    for viewport in ("compact", "wide"):
        for surface, section in (
            ("home", "initial"),
            ("about", "complete" if platform == "android" else "initial"),
        ):
            matches = [
                shot for shot in document.get("screenshots", [])
                if shot.get("viewport") == viewport
                and shot.get("surface") == surface
                and shot.get("section") == section
            ]
            if len(matches) != 1:
                raise ValueError(f"Expected one real {platform}/{viewport}/{surface} screenshot")
            shot = matches[0]
            name = shot.get("path")
            if not isinstance(name, str) or not name or Path(name).name != name:
                raise ValueError("Screenshot path must be a simple file name")
            rel = prefix / name
            file = (base / rel).resolve()
            if not file.is_relative_to(base) or not file.is_file():
                raise ValueError(f"Real screenshot file missing or escapes evidence root: {name}")
            actual_digest = digest(file)
            if actual_digest != shot.get("sha256"):
                raise ValueError(f"Screenshot digest mismatch: {name}")
            if actual_digest in seen_digests:
                raise ValueError("Duplicate actual screenshots cannot satisfy distinct UI surfaces")
            seen_digests.add(actual_digest)
            if shot.get("candidate_artifact_sha256", artifact_hash) != artifact_hash:
                raise ValueError(f"Screenshot {name} refers to another build artifact")
            if shot.get("platform") != platform:
                raise ValueError("Screenshot platform mismatch")
            shots = dict(shot)
            shots["path"] = rel.as_posix()
            shots["candidate_artifact_sha256"] = artifact_hash
            screenshots.append(shots)
    return {
        "schema": "michelslab-rendered-ui-v1",
        "source_commit": source_sha,
        "artifact_sha256": {platform: artifact_hash},
        "screenshots": screenshots,
        "human_visual_review": {"decision": "PENDING", "reviewer": None},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True, choices=("android", "desktop"))
    parser.add_argument("--source-manifest", required=True, type=Path)
    parser.add_argument("--artifact", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.source_manifest.resolve().parent != args.out.resolve().parent:
        parser.error("Adapted manifest must stay beside original screenshot manifest")
    try:
        result = create_manifest(args.platform, args.source_manifest, args.artifact, args.source_sha)
    except (OSError, KeyError, TypeError, ValueError) as error:
        parser.error(f"Cannot bind captured runtime evidence: {error}")
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Master UI evidence prepared: {args.platform}, 2 real viewports, Home+About, exact artifact SHA-256.")
    print("Owner visual review remains PENDING POST-RELEASE; this is not physical-device acceptance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
