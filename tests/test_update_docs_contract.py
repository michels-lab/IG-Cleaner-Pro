"""Guard the *published* update guidance against reserved candidate version drift."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release" / "distribution-manifest.json"
UPDATE_GUIDE = ROOT / "docs" / "UPDATE_AND_STATE_MIGRATION.md"
README = ROOT / "README.md"
COUNTS_GUIDE = ROOT / "docs" / "PROFILE_COUNTS_ROBOT.md"


class UpdateGuideContract(unittest.TestCase):
    def test_guide_uses_current_published_stable_not_reserved_candidate(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        stable = manifest["releasePolicy"]["currentStableRelease"]
        reserved = manifest["releasePolicy"]["nextRelease"]
        self.assertRegex(stable, r"^v\d+\.\d+$")
        self.assertRegex(reserved, r"^v\d+\.\d+$")
        self.assertNotEqual(stable, reserved)

        guide = UPDATE_GUIDE.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn(f"Published stable: [{stable}]", guide)
        self.assertIn(f"https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/{stable}", guide)
        self.assertIn(f"Next reserved version: {reserved} (not published)", guide)
        self.assertIn(f"**{stable} — official stable GitHub release", readme)
        current_claims = re.findall(r"currently (v\d+\.\d+)", guide)
        self.assertGreaterEqual(len(current_claims), 2)
        self.assertEqual(set(current_claims), {stable},
                         "Update guide must not tell users an old or reserved version is currently shipped.")

    def test_readme_all_current_and_reserved_release_claims_match_manifest(self):
        """Catch stale owner-facing guidance, not just the first README banner."""
        policy = json.loads(MANIFEST.read_text(encoding="utf-8"))["releasePolicy"]
        stable = policy["currentStableRelease"]
        reserved = policy["nextRelease"]
        readme = README.read_text(encoding="utf-8")
        self.assertIn(
            f"**{stable} — official stable GitHub release",
            readme,
        )
        self.assertIn(
            f"https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/{stable}",
            readme,
        )
        claims = re.findall(
            r"\*\*Current published stable: (v\d+\.\d+)\. "
            r"Next reserved version: (v\d+\.\d+), not published\.\*\*$",
            readme,
        )
        self.assertEqual(claims, [(stable, reserved)])
        # Detect the historical stale one-line claim even if the valid
        # manifest-backed banner also exists elsewhere in the README.
        self.assertEqual(
            re.findall(r"(?im)\bcurrent published stable:\s*(v\d+\.\d+)", readme),
            [stable],
        )
        self.assertIn("Publication does not prove live Instagram Unfollow", readme)
        self.assertIn("owner tests only officially published installers", readme)
        self.assertNotIn(
            f"**{reserved} — official stable GitHub release",
            readme,
            "Do not advertise the reserved version as published before promotion.",
        )

    def test_profile_counts_guide_uses_release_feed_not_obsolete_stable_claim(self):
        guide = COUNTS_GUIDE.read_text(encoding="utf-8")
        self.assertIn("releasePolicy.currentStableRelease", guide)
        self.assertIn("releasePolicy.nextRelease", guide)
        self.assertIn("official GitHub Releases", guide)
        self.assertIn("official published release", guide)
        self.assertNotIn("v120.48 Pending Requests batch fixes are still", guide)
        self.assertNotRegex(guide, r"current Windows guidance\s*\(v[0-9]+\.[0-9]+")
        self.assertIn("historical [v120.47 release]", guide)
        self.assertIn("not claims about the latest stable", guide)

    def test_publishing_and_device_qa_are_not_conflated_with_candidate_builds(self):
        guide = UPDATE_GUIDE.read_text(encoding="utf-8")
        self.assertIn("does not authorize a release", guide)
        self.assertIn("official installed published release", guide)
        self.assertIn("not the candidate asset names", guide)
        self.assertIn("browser origin", guide)
        self.assertIn("idempotently", guide)


if __name__ == "__main__":
    unittest.main()
