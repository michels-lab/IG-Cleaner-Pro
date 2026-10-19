"""Guard the *published* update guidance against reserved candidate version drift."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "distribution-manifest.json"
UPDATE_GUIDE = ROOT / "docs" / "UPDATE_AND_STATE_MIGRATION.md"
README = ROOT / "README.md"


class UpdateGuideContract(unittest.TestCase):
    def test_guide_uses_current_published_stable_not_reserved_candidate(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        stable = manifest["releasePolicy"]["currentStableRelease"]
        reserved = manifest["releasePolicy"]["nextRelease"]
        self.assertRegex(stable, r"^v\\d+\\.\\d+$")
        self.assertRegex(reserved, r"^v\\d+\\.\\d+$")
        self.assertNotEqual(stable, reserved)

        guide = UPDATE_GUIDE.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn(f"Published stable: [{stable}]", guide)
        self.assertIn(f"https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/{stable}", guide)
        self.assertIn(f"Next reserved version: {reserved} (not published)", guide)
        self.assertIn(f"**{stable} — official stable GitHub release", readme)
        current_claims = re.findall(r"currently (v\\d+\\.\\d+)", guide)
        self.assertGreaterEqual(len(current_claims), 2)
        self.assertEqual(set(current_claims), {stable},
                         "Update guide must not tell users an old or reserved version is currently shipped.")

    def test_publishing_and_device_qa_are_not_conflated_with_candidate_builds(self):
        guide = UPDATE_GUIDE.read_text(encoding="utf-8")
        self.assertIn("does not authorize a release", guide)
        self.assertIn("official installed published release", guide)
        self.assertIn("not the candidate asset names", guide)
        self.assertIn("browser origin", guide)
        self.assertIn("idempotently", guide)


if __name__ == "__main__":
    unittest.main()
