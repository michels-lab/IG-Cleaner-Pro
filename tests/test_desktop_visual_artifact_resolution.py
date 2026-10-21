"""Release P0: accept genuine flat/nested GitHub artifact layouts only.

This test does not create, approve, or fake browser screenshot evidence;
the separate release validator must authenticate all actual screenshots.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from resolve_desktop_visual_artifact_dir import evidence_root


class VisualArtifactRootContract(unittest.TestCase):
    def complete(self, where: Path):
        where.mkdir(parents=True, exist_ok=True)
        (where / "manifest.json").write_text("{}", encoding="utf-8")
        (where / "michelslab-manifest.json").write_text("{}", encoding="utf-8")

    def test_flat_artifact_accepted(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.complete(base)
            self.assertEqual(evidence_root(base), base.resolve())

    def test_nested_multi_directory_upload_accepted(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.complete(base / "desktop-visual")
            (base / "automation-center").mkdir()
            self.assertEqual(evidence_root(base), (base / "desktop-visual").resolve())

    def test_missing_or_partial_artifact_is_not_accepted(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            with self.assertRaisesRegex(ValueError, "exactly one complete"):
                evidence_root(base)
            (base / "manifest.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "exactly one complete"):
                evidence_root(base)

    def test_duplicate_manifests_cannot_choose_stale_or_wrong_sha(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.complete(base)
            self.complete(base / "desktop-visual")
            with self.assertRaisesRegex(ValueError, "exactly one complete"):
                evidence_root(base)

    def test_external_symlink_must_not_be_followed(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            outside = base / "outside"
            outside.mkdir()
            self.complete(outside)
            inner = base / "download"
            inner.mkdir()
            try:
                (inner / "desktop-visual").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("No symlink privileges on runner")
            with self.assertRaisesRegex(ValueError, "exactly one complete"):
                evidence_root(inner)


if __name__ == "__main__":
    unittest.main()
