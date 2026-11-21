"""Integrated Windows app startup contracts; no live Instagram requests."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import ig_cleaner_desktop as native
from profile_counts_bridge import Collector, build_server


class DesktopAppTests(unittest.TestCase):
    def test_stable_html_path_preserves_data_and_avoids_unnecessary_overwrite(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, dest = root / "bundle.html", root / "profile" / "IG-Cleaner-Pro.html"
            src.write_bytes(b"A" * 100_001)
            dest.parent.mkdir()
            (dest.parent / "user-backup.json").write_text('{"retain":true}', encoding="utf-8")
            self.assertEqual(native.prepare_html(src, dest), dest)
            self.assertEqual(dest.read_bytes(), src.read_bytes())
            timestamp = dest.stat().st_mtime_ns
            native.prepare_html(src, dest)
            self.assertEqual(dest.stat().st_mtime_ns, timestamp)
            src.write_bytes(b"B" * 100_001)
            native.prepare_html(src, dest)
            self.assertEqual(dest.read_bytes(), src.read_bytes())
            self.assertTrue((dest.parent / "user-backup.json").is_file())
            self.assertFalse((dest.parent / (dest.name + ".new")).exists())

    def test_incomplete_bundle_fails_without_overwriting_workspace(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            src, dst = root / "source.html", root / "workspace.html"
            dst.write_text("keep", encoding="utf-8")
            src.write_text("bad", encoding="utf-8")
            with self.assertRaises(ValueError):
                native.prepare_html(src, dst)
            self.assertEqual(dst.read_text(encoding="utf-8"), "keep")

    def test_chrome_app_mode_is_one_window_with_private_persistent_workspace(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            icon = home / "chrome.exe"
            icon.write_bytes(b"stub")
            html = home / "IG-Cleaner-Pro.html"
            html.write_bytes(b"fake")
            profile = home / "workspace-browser"
            args = native.chrome_app_args(icon, html, profile, 31777, "abcdefghijklmnopqrstuvwxyz012345")
            self.assertEqual(args[0], str(icon))
            self.assertIn("--disable-background-mode", args)
            self.assertIn("--user-data-dir=" + str(profile), args)
            self.assertTrue(any(s.startswith("--app=file:") for s in args))
            self.assertTrue(any("#igc-robot=31777." in s for s in args))
            self.assertFalse(any(s.endswith(".cmd") for s in args))

    def test_second_windows_instance_cannot_claim_same_workspace(self):
        if sys.platform != "win32":
            self.skipTest("Windows named mutex")
        handle = native.acquire_single_instance(workspace="primary")
        second = None
        try:
            with self.assertRaisesRegex(RuntimeError, "ventana abierta"):
                native.acquire_single_instance(workspace="primary")
            second = native.acquire_single_instance(workspace="secondary")
            self.assertIsNotNone(second, "A second independent account window is allowed.")
            with self.assertRaisesRegex(RuntimeError, "ventana abierta"):
                native.acquire_single_instance(workspace="secondary")
        finally:
            native.release_single_instance(second)
            native.release_single_instance(handle)

    def test_cancelling_account_chooser_starts_no_server_chrome_or_user_data(self):
        # Native dialog Cancel is a true no-op: no local action controller,
        # no Chrome tab, no accidental identity migration or workspaces.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (patch.object(native.sys, "platform", "win32"),
                  patch.object(native, "bundled_html", return_value=root / "bundle.html"),
                  patch.object(native, "select_workspace", return_value=None) as picker,
                  patch.object(native, "prepare_html") as prepare,
                  patch.object(native, "acquire_single_instance") as mutex,
                  patch.object(native, "build_server") as backend,
                  patch.object(native, "chrome_path") as browser,
                  patch.object(native.subprocess, "Popen") as spawn):
                self.assertEqual(native.main([]), 0)
                picker.assert_called_once_with()
                prepare.assert_not_called()
                mutex.assert_not_called()
                backend.assert_not_called()
                browser.assert_not_called()
                spawn.assert_not_called()
                self.assertEqual(list(root.iterdir()), [])

    def test_app_same_server_as_actions_and_counts(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            collector = Collector(root / "counts", root / "ig-browser")
            server = build_server(collector, "local-only-test", 0)
            try:
                self.assertIs(server.collector, collector)
                self.assertIs(server.actions.collector, collector)
                self.assertEqual(server.server_address[0], "127.0.0.1")
                self.assertGreater(server.server_port, 0)
            finally:
                server.server_close()

    def test_closing_application_requests_safe_stop(self):
        calls = []
        class FakeWorker:
            def is_alive(self):
                return True
            def join(self, timeout):
                calls.append(("join", timeout))
        class FakeEvent:
            def set(self):
                calls.append("stop_requested")
        class FakeActions:
            stop_event = FakeEvent()
            worker = FakeWorker()
        class FakeCollector:
            worker = FakeWorker()
            def stop(self):
                calls.append("collector_paused")
        class FakeServer:
            actions = FakeActions()
            collector = FakeCollector()
            def shutdown(self):
                calls.append("shutdown")
            def server_close(self):
                calls.append("closed")
        native.stop_safely(FakeServer())
        self.assertEqual(calls[0:2], ["stop_requested", "collector_paused"])
        self.assertEqual(calls[-2:], ["shutdown", "closed"])

    def test_developer_shutdown_stops_real_action_worker_and_live_probe(self):
        calls = []
        class FakeWorker:
            def is_alive(self): return True
            def join(self, timeout): calls.append(("join", timeout))
        class FakeEvent:
            def set(self): calls.append("stop_action")
        class FakeAction:
            stop_event = FakeEvent()
            worker = FakeWorker()
        class FakeCollector:
            worker = FakeWorker()
            def stop(self): calls.append("stop_counts")
        class FakeProbe:
            worker = FakeWorker()
            def stop(self): calls.append("stop_live_probe")
        class FakeServer:
            actions = FakeAction()
            collector = FakeCollector()
            dev_action_tests = FakeAction()
            live_probe = FakeProbe()
            def shutdown(self): calls.append("server_shutdown")
            def server_close(self): calls.append("server_closed")
        native.stop_safely(FakeServer())
        self.assertEqual(calls.count("stop_action"), 2)
        self.assertIn("stop_live_probe", calls)
        self.assertEqual(calls.count(("join", 60)), 4)
        self.assertEqual(calls[-2:], ["server_shutdown", "server_closed"])

    def test_launcher_starts_only_one_executable_not_cmd(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui = root / "ui.html"
            ui.write_bytes(b"<html><body>" + b"A"*100_001 + b"</body></html>")
            chrome = root / "chrome.exe"
            chrome.write_bytes(b"stub")
            class FakeProcess:
                def wait(self):
                    return 0
            with (patch.object(native, "bundled_html", return_value=ui),
                  patch.object(native, "app_home", return_value=root / "app"),
                  patch.object(native, "chrome_path", return_value=chrome),
                  patch.object(native, "stop_safely", wraps=native.stop_safely) as stop,
                  patch.object(native.subprocess, "Popen", return_value=FakeProcess()) as launch):
                result = native.main(['--workspace', 'primary'])
            self.assertEqual(result, 0)
            self.assertEqual(launch.call_count, 1)
            self.assertTrue(launch.call_args.args[0][-1].startswith("--app=file:"))
            self.assertEqual(stop.call_count, 1)


    def test_interface_and_preview_instructions_use_integrated_executable(self):
        root = Path(__file__).resolve().parents[1]
        html = (root / "desktop" / "ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
        readme = (root / "packaging" / "profile-counts" / "README.txt").read_text(encoding="utf-8")
        self.assertNotIn("Start-Insta-Cleaner-Robot.cmd", html)
        self.assertNotIn("IGCleanerProfileCounts.exe --healthcheck", readme)
        self.assertIn("InstaCleanerPro.exe --healthcheck", readme)
        self.assertIn("InstaCleanerPro.exe", html)
        self.assertNotIn('id="igcDualSecondary"', html)
        self.assertNotIn('class="igc-dual-workspace"', html)
        self.assertIn('id="igcAutomationTabActions"', html)
        self.assertIn('id="igcAutomationTabHistory"', html)



    def _run_startup_fault(self, workspace, *, update_error=False,
                           chrome_error=False, thread_error=False):
        """Exercise real main() exception boundary without Chrome/Instagram."""
        from contextlib import ExitStack
        from unittest.mock import Mock

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            ui = root / "ui.html"
            ui.write_bytes(b"<html><body>" + b"X" * 101000 + b"</body></html>")
            chrome = root / "chrome.exe"
            chrome.write_bytes(b"stub")
            server = Mock()
            server.server_port = 33477
            server.actions.worker = None
            server.collector.worker = None
            updater = Mock()
            if update_error:
                updater.check.side_effect = OSError("offline or updater denied")
            thread = Mock()
            if thread_error:
                thread.start.side_effect = RuntimeError("thread refused")
            process = Mock()
            process.wait.return_value = 0

            with ExitStack() as stack:
                stack.enter_context(patch.object(native, "bundled_html", return_value=ui))
                stack.enter_context(patch.object(native, "app_home", return_value=root / "app"))
                stack.enter_context(patch.object(native, "chrome_path", return_value=chrome))
                stack.enter_context(patch.object(native, "app_version", return_value="120.80"))
                stack.enter_context(patch.object(native, "WindowsUpdater", return_value=updater))
                stack.enter_context(patch.object(native, "window_collector", return_value=Mock()))
                stack.enter_context(patch.object(native, "build_server", return_value=server))
                stack.enter_context(patch.object(native, "acquire_single_instance", return_value=123))
                release = stack.enter_context(patch.object(native, "release_single_instance"))
                stack.enter_context(patch.object(native.threading, "Thread", return_value=thread))
                spawned = stack.enter_context(patch.object(native.subprocess, "Popen", return_value=process))
                warning = stack.enter_context(patch.object(native, "alert"))
                if chrome_error:
                    spawned.side_effect = OSError("Chrome launch refused")
                result = native.main(["--workspace", workspace])

            release.assert_called_once_with(123)
            if thread_error:
                self.assertEqual(result, 1)
                thread.start.assert_called_once()
                spawned.assert_not_called()
                updater.check.assert_not_called()
                # Server thread was never started: shutdown() would deadlock.
                server.server_close.assert_called_once()
                server.shutdown.assert_not_called()
                warning.assert_called_once()
            else:
                thread.start.assert_called_once()
                updater.check.assert_called_once()
                spawned.assert_called_once()
                server.actions.stop_event.set.assert_called_once()
                server.collector.stop.assert_called_once()
                server.shutdown.assert_called_once()
                server.server_close.assert_called_once()
                if chrome_error:
                    self.assertEqual(result, 1)
                    process.wait.assert_not_called()
                    warning.assert_called_once()
                else:
                    self.assertEqual(result, 0)
                    process.wait.assert_called_once()
                    warning.assert_not_called()
                app_args = spawned.call_args.args[0]
                self.assertTrue(any(x.startswith("--user-data-dir=")
                                    and ("secondary" in x) == (workspace == "secondary")
                                    for x in app_args))
            return result

    def test_optional_updater_failure_never_blocks_both_windows(self):
        for workspace in ("primary", "secondary"):
            with self.subTest(workspace=workspace):
                self._run_startup_fault(workspace, update_error=True)

    def test_chrome_launch_error_releases_loopback_and_slot(self):
        for workspace in ("primary", "secondary"):
            with self.subTest(workspace=workspace):
                self._run_startup_fault(workspace, chrome_error=True)

    def test_server_thread_start_failure_closes_socket_without_deadlock(self):
        for workspace in ("primary", "secondary"):
            with self.subTest(workspace=workspace):
                self._run_startup_fault(workspace, thread_error=True)


if __name__ == "__main__":
    unittest.main()
