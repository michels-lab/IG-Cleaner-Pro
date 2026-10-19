"""Offline security and lifecycle tests for the installable Windows update manager."""
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import windows_updater as wu
from profile_counts_bridge import Collector, build_server


class BytesResponse(io.BytesIO):
    def __init__(self, body, url):
        super().__init__(body)
        self.url = url

    def geturl(self):
        return self.url


def published(version="120.48", raw=None, stable=True, repository=wu.REPO):
    filename = "IG-Cleaner-Pro-Windows-Setup-v" + version + ".exe"
    tag = "v" + version
    base = "https://github.com/" + repository + "/releases/download/" + tag + "/"
    return {
        "tag_name":tag, "draft":False, "prerelease":not stable,
        "assets":[
            dict(name=filename, size=1_000_100 if raw is None else len(raw),
                 browser_download_url=base+filename),
            dict(name="SHA256SUMS.txt", browser_download_url=base+"SHA256SUMS.txt",
                 size=130)
        ],
        "body":"New test fixture release"
    }


class WindowsUpdaterTests(unittest.TestCase):
    def test_version_and_release_requirements(self):
        self.assertGreater(wu.numeric_version("v120.48"), wu.numeric_version("v120.47"))
        self.assertIsNone(wu.release_setup(published("120.46"), "120.47"))
        self.assertIsNone(wu.release_setup(published("120.47"), "120.47"))
        self.assertEqual(wu.release_setup(published(), "120.47")["version"], "120.48")
        with self.assertRaises(ValueError):
            wu.release_setup(published(stable=False), "120.47")
        with self.assertRaises(ValueError):
            wu.release_setup(published(repository="another-org/another-app"), "120.47")
        broken=published()
        broken["assets"]=broken["assets"][:1]
        with self.assertRaises(ValueError):
            wu.release_setup(broken, "120.47")
        with self.assertRaises(ValueError):
            wu.numeric_version("v120.48-beta")
        with self.assertRaises(ValueError):
            wu.numeric_version("vX.Y")

    def test_sha256_sums_require_unique_exact_filename(self):
        file="IG-Cleaner-Pro-Windows-Setup-v120.48.exe"
        h="a"*64
        self.assertEqual(wu.parse_sums(h+"  "+file+"\n",file),h)
        with self.assertRaisesRegex(ValueError,"missing"):
            wu.parse_sums(h+"  another.exe\n",file)
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            wu.parse_sums(h+"  "+file+"\n"+h+"  "+file+"\n",file)

    def test_feed_state_requires_both_release_and_valid_checksum(self):
        with TemporaryDirectory() as tmp:
            m=wu.WindowsUpdater("120.47",Path(tmp),Path(tmp)/"robots")
            release=published()
            sha="4"*64
            def fetch(url,*_args,**_kwargs):
                return json.dumps(release) if url==wu.RELEASE_API else sha+"  "+release["assets"][0]["name"]+"\n"
            with patch.object(wu,"_fetch_text",side_effect=fetch):
                m.check()
                m.worker.join(timeout=4)
            self.assertFalse(m.worker.is_alive())
            self.assertEqual(m.snapshot()["status"],"update_available")
            self.assertEqual(m.snapshot()["latest"],"v120.48")
            self.assertNotIn("downloaded",m.snapshot())
            self.assertIsNone(m.downloaded)
            self.assertEqual(m.expected_sha,sha)
            with patch.object(wu,"_fetch_text",side_effect=ValueError("offline")):
                m.check()
                m.worker.join(timeout=4)
            self.assertEqual(m.snapshot()["status"],"unavailable")
            self.assertIsNone(m.downloaded)

    def _available(self, root, contents):
        m=wu.WindowsUpdater("120.47",root,root/"robots")
        release=published(raw=contents)
        info=wu.release_setup(release,"120.47")
        m.candidate=info
        m.expected_sha=hashlib.sha256(contents).hexdigest()
        m.state["status"]="update_available"
        return m

    def test_download_checksum_atomic_and_manual_gate(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            content=b"Setup-fixture" + b"x"*(1_000_100-len(b"Setup-fixture"))
            m=self._available(root,content)
            with patch.object(wu,"urlopen",return_value=BytesResponse(content,m.candidate["download_url"])):
                m.download()
                m.worker.join(timeout=4)
            self.assertEqual(m.snapshot()["status"],"ready_to_install")
            self.assertTrue(m.downloaded.is_file())
            self.assertEqual(wu._sha256(m.downloaded),m.expected_sha)
            self.assertFalse(m.downloaded.with_suffix(".exe.partial").exists())
            self.assertEqual(m.snapshot()["progress"],100)
            with self.assertRaisesRegex(ValueError,"Check"):
                m.download()

    def test_download_rejects_changed_content_and_cleans_partial(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            original=b"A"*1_000_100
            m=self._available(root,original)
            with patch.object(wu,"urlopen",return_value=BytesResponse(b"B"*len(original),m.candidate["download_url"])):
                m.download()
                m.worker.join(timeout=4)
            self.assertEqual(m.snapshot()["status"],"error")
            self.assertIsNone(m.downloaded)
            self.assertFalse(list((root/"updates").glob("*.partial")))
            self.assertFalse(list((root/"updates").glob("*.exe")))
            # A third-party redirected body must also fail closed.
            m.state["status"]="update_available"
            with patch.object(wu,"urlopen",return_value=BytesResponse(original,"https://outside.invalid/setup.exe")):
                m.download()
                m.worker.join(timeout=4)
            self.assertEqual(m.snapshot()["status"],"error")

    def test_cancelled_download_never_runs_installer(self):
        with TemporaryDirectory() as tmp:
            content=b"Z"*1_000_100
            m=self._available(Path(tmp),content)
            class CancelOnRead(BytesResponse):
                def read(self,size=-1):
                    m.cancel_download()
                    return super().read(size)
            with patch.object(wu,"urlopen",return_value=CancelOnRead(content,m.candidate["download_url"])):
                m.download()
                m.worker.join(timeout=4)
            self.assertEqual(m.snapshot()["status"],"postponed")
            self.assertIsNone(m.downloaded)
            self.assertFalse(list((Path(tmp)/"updates").glob("*.partial")))

    def test_restore_point_keeps_robot_evidence_not_browser_cookies(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/"app"
            robots=Path(tmp)/"private-robot"
            (home/"workspace-browser").mkdir(parents=True)
            (home/"workspace-browser"/"Cookies").write_text("PRIVATE")
            (home/"IG-Cleaner-Pro.html").write_text("safe-app-file")
            robots.mkdir()
            (robots/"latest.csv").write_text("username,followers\nuser,50")
            (robots/"cycle.reaudit.json").write_text('{"targets":["user"]}')
            (robots/"cycle.done").write_text("user\n")
            (robots/"private.zip").write_text("PRIVATE")
            backup=wu.create_restore_point(home/"backups",home,robots,"120.47")
            with zipfile.ZipFile(backup) as z:
                names=z.namelist()
                self.assertIn("app/IG-Cleaner-Pro.html",names)
                self.assertIn("robot/latest.csv",names)
                self.assertIn("robot/cycle.reaudit.json",names)
                self.assertIn("robot/cycle.done",names)
                self.assertNotIn("Cookies",str(names))
                self.assertNotIn("private.zip",str(names))
                self.assertIn(b"120.47",z.read("BACKUP-INFO.json"))

    def test_restore_point_integrity_manifest_detects_valid_zip_content_change(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)/"app"
            robots=Path(tmp)/"robot"
            home.mkdir()
            robots.mkdir()
            (home/"IG-Cleaner-Pro.html").write_text("installed UI",encoding="utf-8")
            (robots/"history.json").write_text('{"result": "preserved"}',encoding="utf-8")
            backup=wu.create_restore_point(home/"backups",home,robots,"120.53")
            self.assertIsNone(wu.verify_restore_point(backup))
            with zipfile.ZipFile(backup) as z:
                manifest=json.loads(z.read("BACKUP-CHECKSUMS.json"))
                self.assertEqual(manifest["schema"],1)
                self.assertEqual(manifest["files"]["robot/history.json"],
                                 hashlib.sha256(b'{"result": "preserved"}').hexdigest())
                content={name:z.read(name) for name in z.namelist()}
            # Repack a valid ZIP with recomputed CRC but the original manifest:
            # CRC-only checks would accept it, SHA-256 must reject it.
            content["robot/history.json"]=b'{"result": "changed"}'
            with zipfile.ZipFile(backup,"w",compression=zipfile.ZIP_DEFLATED) as z:
                for name,body in content.items():
                    z.writestr(name,body)
            with self.assertRaisesRegex(ValueError,"integrity"):
                wu.verify_restore_point(backup)

    def test_restore_point_missing_manifest_duplicate_and_unsafe_name_fail_closed(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            broken=root/"bad.zip"
            with zipfile.ZipFile(broken,"w") as z:
                z.writestr("BACKUP-INFO.json",'{"schema":2}')
            with self.assertRaises(ValueError):
                wu.verify_restore_point(broken)
            with zipfile.ZipFile(broken,"w") as z:
                z.writestr("BACKUP-INFO.json",'{"schema":2}')
                z.writestr("BACKUP-CHECKSUMS.json",json.dumps({
                    "schema":1,"files":{"robot/../escaped.json":hashlib.sha256(b"bad").hexdigest()}}))
                z.writestr("robot/../escaped.json",b"bad")
            with self.assertRaisesRegex(ValueError,"unsafe"):
                wu.verify_restore_point(broken)
            with zipfile.ZipFile(broken,"a") as z:
                z.writestr("robot/../escaped.json",b"duplicate")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                wu.verify_restore_point(broken)

    def test_restore_point_blocks_symlink_data_and_preserves_existing_files(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            home=root/"app"
            robots=root/"robots"
            secret=root/"private.json"
            secret.write_text("COOKIE-LIKE PRIVATE CONTENT",encoding="utf-8")
            home.mkdir()
            robots.mkdir()
            (robots/"safe.json").write_text('{"audit": 1}',encoding="utf-8")
            try:
                (robots/"linked.json").symlink_to(secret)
            except (OSError, NotImplementedError):
                pass
            backup=wu.create_restore_point(home/"backups",home,robots,"120.53")
            with zipfile.ZipFile(backup) as z:
                self.assertIn("robot/safe.json",z.namelist())
                self.assertNotIn("robot/linked.json",z.namelist())
                self.assertNotIn(b"COOKIE-LIKE PRIVATE CONTENT",b"".join(z.read(n) for n in z.namelist()))

    def test_installer_never_launches_if_finished_backup_integrity_check_fails(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"robots").mkdir()
            (root/"robots"/"saved.json").write_text('{"status":"saved"}')
            installer=root/"updates"/"Setup.exe"
            installer.parent.mkdir()
            installer.write_bytes(b"verified installer")
            m=wu.WindowsUpdater("120.53",root,root/"robots")
            m.downloaded=installer
            m.expected_sha=hashlib.sha256(b"verified installer").hexdigest()
            m.state["status"]="ready_to_install"
            with patch.object(wu,"running_on_windows",return_value=True):
                with patch.object(wu,"verify_restore_point",
                                  side_effect=[None,ValueError("backup integrity failure")]):
                    with patch.object(wu.subprocess,"Popen") as launch:
                        with self.assertRaisesRegex(ValueError,"integrity"):
                            m.install()
                        launch.assert_not_called()
            self.assertEqual(m.snapshot()["status"],"ready_to_install")
            self.assertTrue(list((root/"backups").glob("*.zip")))
            self.assertEqual((root/"robots"/"saved.json").read_text(),'{"status":"saved"}')

    def test_local_server_requires_session_token_and_explicit_install_phrase(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            m=wu.WindowsUpdater("120.47",root,root/"robots")
            server=build_server(Collector(root/"robots",root/"chrome"),"my-private-capability",0,updater=m)
            import http.client
            import threading
            t=threading.Thread(target=server.serve_forever,daemon=True)
            t.start()
            try:
                conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
                conn.request("GET","/api/update/status")
                self.assertEqual(conn.getresponse().status,403)
                conn.close()
                conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
                conn.request("GET","/api/update/status",headers={"X-IGC-Bridge-Token":"my-private-capability","Origin":"null"})
                response=conn.getresponse()
                self.assertEqual(response.status,200)
                self.assertEqual(json.loads(response.read())["current"],"120.47")
                conn.close()
                conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
                body=json.dumps({"confirm":"no"})
                conn.request("POST","/api/update/install",body=body,headers={
                    "X-IGC-Bridge-Token":"my-private-capability","Origin":"null","Content-Type":"application/json"})
                response=conn.getresponse()
                self.assertGreaterEqual(response.status,400)
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
                t.join(timeout=4)

    def test_recheck_checksum_before_installer_with_preserved_data(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/"updates"/"Setup.exe"
            path.parent.mkdir()
            path.write_bytes(b"original")
            m=wu.WindowsUpdater("120.47",root,root/"robots")
            m.downloaded=path
            m.expected_sha=hashlib.sha256(b"original").hexdigest()
            m.state["status"]="ready_to_install"
            path.write_bytes(b"tampered")
            with patch.object(wu,"running_on_windows",return_value=True):
                with patch.object(wu.subprocess,"Popen") as p:
                    with self.assertRaisesRegex(ValueError,"changed"):
                        m.install()
                    p.assert_not_called()
                    self.assertFalse((root/"backups").exists())
            path.write_bytes(b"original")
            (root/"robots").mkdir()
            (root/"robots"/"saved.csv").write_text("preserve")
            with patch.object(wu,"running_on_windows",return_value=True):
                with patch.object(wu.subprocess,"Popen") as p:
                    result=m.install()
            p.assert_called_once()
            self.assertEqual(result["status"],"installer_started")
            self.assertTrue(list((root/"backups").glob("*.zip")))
            self.assertEqual((root/"robots"/"saved.csv").read_text(),"preserve")


if __name__=="__main__":
    unittest.main()
