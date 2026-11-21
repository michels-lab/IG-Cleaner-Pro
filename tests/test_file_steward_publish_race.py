"""Exercise the ACTUAL File Steward publish shell against a moving local git origin.

No GitHub writes, credentials, user browser, Instagram, or external network.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/file-governance-audit.yml"
GENERATED = (
    "reports/file-governance/FILE_GOVERNANCE.json",
    "reports/file-governance/FILE_GOVERNANCE.md",
    "reports/file-governance/SUMMARY.json",
    "docs/audits/FILE_GOVERNANCE_LOG.md",
)
AUDITOR = """
from pathlib import Path
source = Path("tracked.txt").read_text(encoding="utf8").strip()
for path in [
    "reports/file-governance/FILE_GOVERNANCE.json",
    "reports/file-governance/FILE_GOVERNANCE.md",
    "reports/file-governance/SUMMARY.json",
    "docs/audits/FILE_GOVERNANCE_LOG.md",
]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("AUDITED " + source + "\\n", encoding="utf8")
"""


def git(folder: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=folder, check=check,
                          text=True, capture_output=True)


def checkout_script() -> str:
    text = WORKFLOW.read_text(encoding="utf8")
    anchor = "      - name: Commit only generated audit reports in this repository\n"
    assert text.count(anchor) == 1, "A single audited publish step must exist"
    block = text.split(anchor, 1)[1]
    assert "if: github.event_name != 'pull_request' && github.ref == 'refs/heads/main'" in block
    assert "        run: |\n" in block
    script = block.split("        run: |\n", 1)[1]
    return textwrap.dedent(script)


class FileStewardMovingMainTests(unittest.TestCase):
    def test_publisher_regenerates_latest_remote_instead_of_rebasing_old_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bare, initial, runner, competing = (
                root / "remote.git", root / "seed",
                root / "runner", root / "other_writer",
            )
            bare.mkdir()
            git(bare, "init", "--bare", "--initial-branch=main")
            initial.mkdir()
            git(initial, "init", "-b", "main")
            git(initial, "config", "user.name", "fixture")
            git(initial, "config", "user.email", "fixture@example.invalid")
            (initial / "tracked.txt").write_text("old", encoding="utf8")
            (initial / "tools").mkdir()
            (initial / "tools/repository_file_auditor.py").write_text(
                textwrap.dedent(AUDITOR), encoding="utf8")
            for path in GENERATED:
                target = initial / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("original", encoding="utf8")
            git(initial, "add", ".")
            git(initial, "commit", "-m", "initial tracked inventory")
            first = git(initial, "rev-parse", "HEAD").stdout.strip()
            git(initial, "remote", "add", "origin", str(bare))
            git(initial, "push", "--set-upstream", "origin", "main")

            git(root, "clone", str(bare), str(runner))
            git(root, "clone", str(bare), str(competing))
            for folder in (runner, competing):
                git(folder, "config", "user.name", "fixture")
                git(folder, "config", "user.email", "fixture@example.invalid")

            # Runner has stale GENERATED files, just like the real bot's
            # initial audit before a concurrent main merge.
            subprocess.run(["python3", "tools/repository_file_auditor.py",
                            "--repo", "."], cwd=runner, check=True)
            self.assertEqual((runner / GENERATED[0]).read_text(), "AUDITED old\n")

            # Another valid main writer changes BOTH audit input and the audit
            # log. The old bot's commit+rebase strategy would conflict here.
            (competing / "tracked.txt").write_text("latest", encoding="utf8")
            for path in GENERATED:
                (competing / path).write_text("COMPETING evidence\n", encoding="utf8")
            git(competing, "add", ".")
            git(competing, "commit", "-m", "new source and concurrent steward")
            competing_sha = git(competing, "rev-parse", "HEAD").stdout.strip()
            git(competing, "push", "origin", "HEAD:main")
            assert competing_sha != first

            env = {**os.environ, "GITHUB_SHA": first}
            process = subprocess.run(
                ["bash", "-c", checkout_script()],
                cwd=runner, env=env, text=True, capture_output=True,
            )
            self.assertEqual(process.returncode, 0,
                             process.stdout + "\n" + process.stderr)
            git(root, "clone", str(bare), str(root / "verified"))
            verify = root / "verified"
            self.assertEqual((verify / "tracked.txt").read_text(), "latest")
            for path in GENERATED:
                self.assertEqual((verify / path).read_text(), "AUDITED latest\n",
                                 "Must regenerate against latest main: " + path)
            self.assertEqual(git(verify, "merge-base", "--is-ancestor",
                                 competing_sha, "HEAD").returncode, 0)

    def test_publish_is_main_only_and_never_uses_force_push(self):
        script = checkout_script()
        workflow = WORKFLOW.read_text(encoding="utf8")
        self.assertIn("github.ref == 'refs/heads/main'", workflow)
        self.assertIn("git merge-base --is-ancestor", script)
        self.assertIn("git reset --hard origin/main", script)
        self.assertIn("python3 tools/repository_file_auditor.py --repo .", script)
        self.assertIn("git push origin HEAD:main", script)
        self.assertNotIn("--force", script)
        self.assertNotIn("git rebase", script)


if __name__ == "__main__":
    unittest.main()
