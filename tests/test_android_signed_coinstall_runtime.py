"""Offline adversarial tests for the mandatory FINAL signed Android emulator gate.

A fake adb is intentionally used ONLY for unit tests. The real release workflow
must additionally install BOTH production-signed APKs in a real emulator.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "verify_production_android_coinstall.sh"

FAKE_ADB = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
scenario = os.environ.get("IGC_MOCK_SCENARIO", "pass")
path = Path(os.environ["IGC_MOCK_STATE"])
state = json.loads(path.read_text()) if path.exists() else {"current": "", "probes": 0, "commands": []}
state["commands"].append(args)
def save():
    path.write_text(json.dumps(state))

if args == ["shell", "getprop", "sys.boot_completed"]:
    print("0" if scenario == "not_booted" else "1")
elif args[:2] == ["install", "-r"]:
    if scenario == "developer_install_fails" and "developer" in args[-1]:
        print("Failure [INSTALL_FAILED]")
        save()
        sys.exit(1)
    print("Success")
elif args == ["shell", "pm", "list", "packages"]:
    print("package:com.michelslab.igcleaner")
    if scenario != "developer_missing":
        print("package:com.michelslab.igcleaner.developer")
elif args[:3] == ["shell", "am", "start"] and len(args) == 5 and args[3] == "-n":
    if scenario == "am_error":
        print("Error: Activity class does not exist")
        save()
        sys.exit(1)
    state["current"] = args[-1].split("/")[0]
    state["probes"] = 0
    print("Starting: Intent { cmp=" + args[-1] + " }")
elif args == ["shell", "dumpsys", "activity", "activities"]:
    state["probes"] += 1
    if scenario == "never_resumed" or state["probes"] < 3:
        print("topResumedActivity=ActivityRecord{launcher/Other}")
    elif scenario == "wrong_foreground" and state["current"].endswith(".developer"):
        print("topResumedActivity=ActivityRecord{com.fake/.MainActivity}")
    else:
        print("topResumedActivity=ActivityRecord{u0 " + state["current"] + "/.MainActivity t42}")
elif args[:2] == ["shell", "pidof"] and len(args) == 3:
    if scenario != "no_process" and args[-1] == state["current"]:
        print("4567")
elif args[:3] == ["shell", "pm", "path"] and len(args) == 4:
    if scenario != "missing_postlaunch_package":
        print("package:/data/app/test/base.apk")
else:
    print("unexpected adb command", args, file=sys.stderr)
    save()
    sys.exit(2)
save()
'''


class SignedCoInstallGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in (
            "android/app/build/outputs/apk/release/app-release.apk",
            "android/app/build/outputs/apk/developer/app-developer.apk",
        ):
            file = self.root / rel
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(b"fixture-not-a-real-signed-apk")
        bindir = self.root / "bin"
        bindir.mkdir()
        adb = bindir / "adb"
        adb.write_text(FAKE_ADB, encoding="utf-8")
        adb.chmod(0o755)
        sleep = bindir / "sleep"
        sleep.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        sleep.chmod(0o755)
        self.env = {**os.environ, "PATH": str(bindir) + os.pathsep + os.environ["PATH"],
                    "IGC_MOCK_STATE": str(self.root / "state.json")}

    def run_gate(self, scenario):
        return subprocess.run(
            ["bash", str(GATE)],
            cwd=self.root,
            env={**self.env, "IGC_MOCK_SCENARIO": scenario},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=25,
        )

    def test_delayed_both_foreground_launches_and_postlaunch_coexistence(self):
        run = self.run_gate("pass")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("public Android MainActivity foreground", run.stdout)
        self.assertIn("Developer Android MainActivity foreground", run.stdout)
        state = json.loads((self.root / "state.json").read_text())
        starts = [cmd[-1] for cmd in state["commands"] if cmd[:3] == ["shell", "am", "start"]]
        self.assertEqual(starts, [
            "com.michelslab.igcleaner/.MainActivity",
            "com.michelslab.igcleaner.developer/com.michelslab.igcleaner.MainActivity",
        ])
        self.assertNotIn("-W", json.dumps(state["commands"]))
        for pkg in ("com.michelslab.igcleaner", "com.michelslab.igcleaner.developer"):
            self.assertIn(["shell", "pm", "path", pkg], state["commands"])

    def test_never_accepts_installed_but_wrong_foreground_or_missing_process(self):
        for scenario in ("never_resumed", "wrong_foreground", "no_process"):
            with self.subTest(scenario=scenario):
                (self.root / "state.json").unlink(missing_ok=True)
                run = self.run_gate(scenario)
                self.assertNotEqual(run.returncode, 0)
                self.assertNotIn("stable public + Developer", run.stdout)

    def test_refuses_missing_boot_package_and_failed_install(self):
        for scenario in ("not_booted", "developer_missing", "developer_install_fails",
                         "missing_postlaunch_package", "am_error"):
            with self.subTest(scenario=scenario):
                (self.root / "state.json").unlink(missing_ok=True)
                run = self.run_gate(scenario)
                self.assertNotEqual(run.returncode, 0)

    def test_missing_apk_fails_without_any_adb(self):
        (self.root / "android/app/build/outputs/apk/developer/app-developer.apk").unlink()
        run = self.run_gate("pass")
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse((self.root / "state.json").exists())


if __name__ == "__main__":
    unittest.main()
