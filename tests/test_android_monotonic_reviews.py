"""Prevent Android regression where a stale workspace snapshot hides reviews."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java").read_text(encoding="utf-8")


class AndroidReviewMergeRegression(unittest.TestCase):
    def test_merge_is_per_profile_not_global_snapshot(self):
        start = SOURCE.index("private void mergeRemoteProfileState(")
        end = SOURCE.index("private boolean loadWorkspaceCache()", start)
        body = SOURCE[start:end]
        self.assertNotIn("reviewedAt <= snapshotUpdatedAt", body)
        self.assertNotIn("if (snapshotUpdatedAt > 0", body)
        self.assertIn('old.optLong("reviewedAt", 0) >= reviewedAt', body)
        self.assertIn('context.optJSONObject("meta")', body)
        self.assertIn('relation = "No me sigue"', body)
        self.assertIn("done.add(username)", body)

if __name__ == "__main__":
    unittest.main()
