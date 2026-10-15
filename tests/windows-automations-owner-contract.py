#!/usr/bin/env python3
"""Guard the Windows installer guidance and English robot status/errors.

Instagram's Spanish UI terms and historical action-journal classification must
remain recognizable; only newly generated owner-facing messages are English.
"""
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from profile_actions import ActionRobot  # noqa: E402
from profile_counts_bridge import Collector  # noqa: E402
from profile_counts_robot import read_queue  # noqa: E402

guide = (ROOT / "packaging/profile-counts/README.txt").read_text(encoding="utf-8")
ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
publisher = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
required = (
    "InstaCleanerPro.exe",
    "Automations → Automation Center",
    "Profile Counts progress, individual results",
    "Insights** contains aggregate account statistics",
    "owner/account-scoped records in IndexedDB",
    "Followback Audit",
    "one robot may navigate",
    "imported Following list",
    "explicitly approve",
    "not yet",
    "simulated",
)
for item in required:
    assert item.casefold() in guide.casefold(), f"Windows instructions omit {item!r}"
for forbidden in ("Insights → Profile Counts", "Insights > Profile Counts",
                  "Start-Insta-Cleaner-Robot.cmd",
                  "A separate IndexedDB migration",
                  "Current stable v120.42"):
    assert forbidden not in guide, f"Windows instructions are stale: {forbidden}"
assert "packaging/profile-counts/README.txt" in publisher
assert "python3 tests/windows-automations-owner-contract.py" in ci
assert "python3 tests/windows-automations-owner-contract.py" in publisher

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    collector = Collector(root / "data", root / "session")
    robot = ActionRobot(collector, root / "data", root / "session")
    assert robot.message == "No active actions"
    try:
        robot.protect({"owner": "wrong", "account": "wrong", "protected": ["test.account"]})
    except ValueError as e:
        assert "Select the same account" in str(e)
    else:
        raise AssertionError("Wrong-scope protections must be refused")

    try:
        robot.start({"owner": "", "account": "", "task": "cancel",
                     "targets": ["test.account"]})
    except ValueError as e:
        assert "Select an Insta Cleaner login" in str(e)
    else:
        raise AssertionError("A robot may not run without account identity")

    try:
        collector.start({"owner": "", "account": "", "usernames": ["test.account"]},
                        load_only=True)
    except ValueError as e:
        assert "owner and active Instagram workspace" in str(e)
    else:
        raise AssertionError("Collection must reject missing identity")

    try:
        read_queue(root / "not-present.csv")
    except ValueError as e:
        assert "Profile queue file not found" in str(e)
    else:
        raise AssertionError("Missing CSV must be rejected")

# Do NOT delete Spanish matches used to parse actual Instagram UI, including
# 'Seguir', 'Cancelar solicitud' and legacy journal messages from old releases.
actions = (ROOT / "tools/profile_actions.py").read_text(encoding="utf-8")
for backwards_compatible_term in ("Cancelar solicitud", "Seguir también"):
    assert backwards_compatible_term in actions
print("Windows automation instructions and English owner messages: PASS")
