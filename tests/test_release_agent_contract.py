"""Release-agent instructions must never advertise a stale candidate as current."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "distribution-manifest.json"
AGENTS = [
    ROOT / ".github" / "agents" / "release-manager.agent.md",
    ROOT / ".github" / "copilot-instructions.md",
]


class ReleaseAgentContract(unittest.TestCase):
    def test_live_version_governance_is_manifest_and_actual_releases(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        policy = manifest["releasePolicy"]
        stable, candidate = policy["currentStableRelease"], policy["nextRelease"]
        self.assertRegex(stable, r"^v\d+\.\d+$")
        self.assertRegex(candidate, r"^v\d+\.\d+$")
        self.assertNotEqual(stable, candidate)
        self.assertIs(policy["automaticPublishFromMain"], False)
        self.assertIs(policy["explicitManualPublishRequired"], True)
        self.assertIs(policy["githubPrerelease"], False)

        for path in AGENTS:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("releasePolicy.currentStableRelease", text)
                self.assertIn("releasePolicy.nextRelease", text)
                self.assertIn("GitHub Releases", text)
                self.assertIn(".github/workflows/release.yml", text)
                self.assertNotIn("v120.35", text)
                self.assertNotIn("v120.36", text)
                self.assertNotRegex(text, r"(?i)current (?:published )?stable\s*(?::|is).*v\d+\.\d+")
                self.assertNotRegex(text, r"(?i)next (?:governed )?(?:publication )?(?:target|version)\s*(?::|is).*v\d+\.\d+")

    def test_agent_requires_owner_release_and_real_world_acceptance_boundary(self):
        manager = AGENTS[0].read_text(encoding="utf-8").lower()
        copilot = AGENTS[1].read_text(encoding="utf-8").lower()
        self.assertIn("explicit authorization", manager)
        self.assertIn("owner validates only official published release", manager)
        self.assertIn("owner", copilot)
        self.assertIn("actions or branch previews", copilot)
        self.assertIn("rendered android about", manager)


if __name__ == "__main__":
    unittest.main()
