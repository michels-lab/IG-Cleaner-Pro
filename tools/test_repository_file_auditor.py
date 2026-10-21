"""Synthetic local Git repository tests; no production file mutations."""
import datetime as dt
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("file_steward",HERE/"repository_file_auditor.py")
audit=importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class FileStewardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        subprocess.run(["git","init","-q",str(self.root)],check=True)
        for key,value in (("user.name","Test"),("user.email","test@example.invalid")):
            subprocess.run(["git","-C",str(self.root),"config",key,value],check=True)
        (self.root/"docs").mkdir()
        (self.root/"README.md").write_text("[ok](docs/notes.md) [bad](missing.md) [offsite](https://example.org)\n",encoding="utf-8")
        (self.root/"docs/notes.md").write_text("Last reviewed: 2026-01-01\n",encoding="utf-8")
        (self.root/"docs/copy.md").write_text("Last reviewed: 2026-01-01\n",encoding="utf-8")
        (self.root/"feature.py").write_text("print(1)\n")
        (self.root/"mystery.abc").write_text("x\n")
        subprocess.run(["git","-C",str(self.root),"add","-A"],check=True)
        subprocess.run(["git","-C",str(self.root),"commit","-qm","synthetic"],check=True)
        self.policy={**audit.DEFAULT,"canonical_logs":["PROJECT_LOG.md"]}
    def test_tracked_tree_and_findings(self):
        r=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        self.assertEqual(r["tracked_files_total"],5)
        self.assertEqual(r["classified_files_total"],5)
        codes={f["code"] for f in r["findings"]}
        for code in ("BROKEN_RELATIVE_LINK","DUPLICATE_DOC_CONTENT","MISSING_LOG","OLD_REVIEW_DATE","UNKNOWN_PURPOSE"):
            self.assertIn(code,codes)
        self.assertFalse(r["deletion_approved"])
    def test_not_affected_by_untracked_temp(self):
        before=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        (self.root/"unsaved_personal_notes.txt").write_text("private")
        after=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        self.assertEqual(before["inventory_fingerprint"],after["inventory_fingerprint"])
        self.assertFalse(after["untracked_audited"])
    def test_link_boundaries(self):
        paths={"docs/a.md","docs/b.md"}
        self.assertEqual(audit.link_result("docs/a.md","b.md#fragment",paths),(True,"docs/b.md"))
        self.assertIsNone(audit.link_result("docs/a.md","https://example.com",paths))
        self.assertFalse(audit.link_result("docs/a.md","../../secret",paths)[0])
    def test_log_does_not_repeat_on_identical_snapshot(self):
        result=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        audit.write_reports(self.root,result,self.policy)
        log=self.root/"docs/audits/FILE_GOVERNANCE_LOG.md"
        snapshot=log.read_text()
        audit.write_reports(self.root,result,self.policy)
        self.assertEqual(log.read_text(),snapshot)
        summary=(self.root/"reports/file-governance/SUMMARY.json").read_text()
        self.assertNotIn("unsaved_personal_notes",summary)
        self.assertNotIn("README.md",summary)
    def test_instacleaner_product_files_have_correct_roles(self):
        samples = {
            "tools/profile_actions.py": "source",
            "tools/ig_cleaner_desktop.py": "source",
            "tests/test_action_click_wal.py": "test",
            "desktop/ig_cleaner_pro_v120_27_synced_companion.html": "web_ui",
            "android/app/src/main/AndroidManifest.xml": "config",
            "release/distribution-manifest.json": "config",
            "packaging/windows-installer/InstaCleanerPro.iss": "build_script",
            "packaging/chrome-extension/manifest.json": "config",
            ".github/workflows/profile-counts-windows-preview.yml": "workflow",
            "docs/CURRENT_HANDOFF.md": "document",
        }
        for path, role in samples.items():
            with self.subTest(path=path):
                self.assertEqual(audit.identify(path,{})[0], role)

    def test_unrelated_extensionless_content_is_never_assumed_to_be_app_data(self):
        self.assertEqual(audit.identify("unrelated_project/system/customDict",{})[0], "unknown")
        self.assertEqual(audit.identify("unrelated_project/0/customField",{})[0], "unknown")

    def test_windows_preview_pushes_only_for_product_changes(self):
        workflow=(HERE.parent / ".github/workflows/profile-counts-windows-preview.yml").read_text()
        push=workflow.split("  push:\n",1)[1].split("  pull_request:\n",1)[0]
        self.assertIn("    paths:\n",push)
        self.assertIn("'tools/profile_actions.py'",push)
        self.assertIn("'desktop/ig_cleaner_pro_v120_27_synced_companion.html'",push)
        self.assertNotIn("'tools/repository_file_auditor.py'",push)
        self.assertNotIn("'tools/test_repository_file_auditor.py'",push)
        # GitHub Actions YAML lists must use one consistent child indentation.
        # Mixing 8- and 6-space bullets made the whole workflow invalid,
        # even though the file-steward tests themselves passed.
        candidates=[line for line in push.splitlines() if line.lstrip().startswith("- ")]
        self.assertEqual(len(candidates), 42)
        self.assertTrue(all(line.startswith("      - '") for line in candidates),
                        "Every product-only push path must be a valid, aligned YAML sequence item")
    def test_android_backup_rules_not_disposable(self):
        self.assertEqual(audit.identify("android/app/src/main/res/xml/backup_rules.xml", {})[0], "config")
    def test_historical_is_not_assumed_obsolete(self):
        self.assertIsNotNone(audit.HISTORY.search("docs/archive/2026-01-01-experiment.md"))
    def test_idempotent_digests(self):
        a=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        b=audit.scan(self.root,self.policy,dt.date(2026,10,21))
        self.assertEqual(a["evidence_fingerprint"],b["evidence_fingerprint"])

if __name__=="__main__": unittest.main()
