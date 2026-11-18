"""Fail closed if a rerun leaves duplicate or incomplete Android artifacts."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from select_android_release_visual_artifact import select_artifact_id

NAME = "ig-cleaner-real-android-about-" + "a" * 40
RUN = 123


def artifact(identifier, size, *, name=NAME, run=RUN, expired=False):
    return {"id": identifier, "name": name, "size_in_bytes": size,
            "expired": expired, "workflow_run": {"id": run}}


class ArtifactPickerTests(unittest.TestCase):
    def test_cancelled_placeholder_plus_successful_rerun(self):
        # A real case: two same-name uploads on one workflow run; the first is
        # tiny because cancelled-run upload-artifact used if: always().
        payload = {"artifacts": [artifact(1, 186), artifact(2, 9_319_397)]}
        self.assertEqual(select_artifact_id(payload, NAME, RUN), 2)

    def test_only_incomplete_or_expired_is_rejected(self):
        for data in ([artifact(1, 186)], [artifact(1, 9_319_397, expired=True)], []):
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, "exactly one"):
                select_artifact_id({"artifacts": data}, NAME, RUN)

    def test_two_complete_artifacts_are_ambiguous(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            select_artifact_id({"artifacts": [artifact(1, 9_319_397), artifact(2, 9_500_000)]}, NAME, RUN)

    def test_foreign_name_and_workflow_run_cannot_satisfy_release(self):
        rows = [artifact(2, 9_319_397, run=999), artifact(3, 8_500_000, name="another-sha")]
        with self.assertRaisesRegex(ValueError, "exactly one"):
            select_artifact_id({"artifacts": rows}, NAME, RUN)

    def test_malformed_payload_or_metadata_fails_closed(self):
        for payload in ({}, {"artifacts": None}, {"artifacts": [None]}, {"artifacts": [artifact(True, 9_319_397)]}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                select_artifact_id(payload, NAME, RUN)


if __name__ == "__main__":
    unittest.main()
