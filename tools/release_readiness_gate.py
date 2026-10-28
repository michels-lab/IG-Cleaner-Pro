#!/usr/bin/env python3
"""Fail-closed owner COMPLETION gate; CI success is never authorization to ship.

Checks a tracked hold and verifiable open GitHub issues before release. This
runs in BOTH the initial release-request gate and just before gh release create.
No Instagram credentials, external mutations or owner identities are stored.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "release" / "release-readiness.json"
REQUIRED_P0 = {164, 172, 173, 176}
REQUIRED_ACCEPTANCE = {
    "two_actual_chrome_sessions_identified_by_instagram_handle",
    "simultaneous_two_account_automation_isolated_and_safely_verified",
    "real_owner_followers_following_complete_without_profile_by_profile",
    "real_owner_unfollow_exact_target_verified_and_journaled",
    "real_owner_cancel_pending_exact_target_verified_and_journaled",
    "batches_protected_history_and_no_repeat_regressions_verified",
    "physical_windows_public_developer_update_backup_acceptance",
    "android_public_developer_acceptance",
}


class ReleaseBlocked(ValueError):
    """Prevent publication; never turn a missing proof into a pass."""


def check_readiness(readiness: dict, tag: str, issue_states: dict[int, str]) -> None:
    if readiness.get("schema") != "ig-cleaner-release-readiness-v1":
        raise ReleaseBlocked("Missing or unexpected owner completion-gate schema.")
    if not re.fullmatch(r"v\d+\.\d+", tag):
        raise ReleaseBlocked("Invalid release tag.")
    if readiness.get("release_hold") is not False:
        raise ReleaseBlocked(
            "RELEASE BLOCKED BY OWNER: product is unfinished; no release, even if CI passed."
        )
    if readiness.get("next_version") != tag:
        raise ReleaseBlocked("Owner acceptance does not match this exact release tag.")
    acceptance = readiness.get("critical_acceptance")
    if not isinstance(acceptance, dict) or not REQUIRED_ACCEPTANCE.issubset(acceptance):
        raise ReleaseBlocked("Missing one or more mandatory real-world acceptance checks.")
    incomplete = sorted(key for key in REQUIRED_ACCEPTANCE if acceptance.get(key) is not True)
    if incomplete:
        raise ReleaseBlocked("Real product acceptance incomplete: " + ", ".join(incomplete))
    owner = readiness.get("owner_final_acceptance")
    if not isinstance(owner, dict) or (
        owner.get("approved") is not True
        or owner.get("release_tag") != tag
        or not isinstance(owner.get("evidence"), str)
        or len(owner["evidence"].strip()) < 12
    ):
        raise ReleaseBlocked("Owner has NOT explicitly accepted the completed app and release.")
    issues = readiness.get("required_closed_issues")
    if (
        not isinstance(issues, list)
        or not all(isinstance(item, int) and item > 0 for item in issues)
        or len(issues) != len(set(issues))
        or not REQUIRED_P0.issubset(set(issues))
    ):
        raise ReleaseBlocked("Blocking GitHub issue list is missing or weaker than P0 minimum.")
    for number in issues:
        if issue_states.get(number) != "closed":
            raise ReleaseBlocked(
                f"Issue #{number} is open, unknown or not verified CLOSED; no release."
            )


def live_issue_states(numbers: list[int]) -> dict[int, str]:
    if not os.getenv("GH_TOKEN"):
        raise ReleaseBlocked("Cannot verify GitHub blocker states without GH_TOKEN.")
    repo = os.getenv("GITHUB_REPOSITORY", "michels-lab/IG-Cleaner-Pro")
    if repo != "michels-lab/IG-Cleaner-Pro":
        raise ReleaseBlocked("Repository mismatch in live completion gate.")
    states = {}
    for number in numbers:
        try:
            value = subprocess.run(
                ["gh", "api", f"repos/{repo}/issues/{number}", "--jq", ".state"],
                check=True, capture_output=True, text=True, timeout=30,
            ).stdout.strip()
        except (subprocess.CalledProcessError, OSError, subprocess.TimeoutExpired) as exc:
            raise ReleaseBlocked(f"Cannot verify mandatory GitHub issue #{number}") from exc
        if value not in {"open", "closed"}:
            raise ReleaseBlocked(f"Unrecognized GitHub issue #{number} state.")
        states[number] = value
    return states


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    try:
        readiness = json.loads(READINESS_PATH.read_text(encoding="utf-8"))
        # Always fail locally before querying any remote service when the owner
        # hold or acceptance requirements are unsatisfied.
        check_readiness(readiness, args.tag, {})
    except ReleaseBlocked as ex:
        # When all local readiness fields pass, the only remaining failure is
        # unverified issue state. Verify those ONLY for live use.
        if args.live and str(ex).startswith("Issue #"):
            states = live_issue_states(readiness["required_closed_issues"])
            check_readiness(readiness, args.tag, states)
        else:
            raise
    else:
        if args.live:
            states = live_issue_states(readiness["required_closed_issues"])
            check_readiness(readiness, args.tag, states)
        else:
            raise ReleaseBlocked("Offline cannot prove GitHub issues are closed.")
    print(f"Owner completion gate PASSED for {args.tag} with all blockers CLOSED")


if __name__ == "__main__":
    try:
        main()
    except ReleaseBlocked as exc:
        raise SystemExit("::error::" + str(exc))
