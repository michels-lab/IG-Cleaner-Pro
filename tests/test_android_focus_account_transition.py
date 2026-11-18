"""P0 regression: native Focus may not switch owner/account in the middle of IO."""
import pathlib
import re
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] /
          "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java").read_text(encoding="utf-8")


def method(name, next_name=None):
    start = SOURCE.index("private void " + name + "(")
    end = SOURCE.find("\n    private ", start + len(name) + 14)
    return SOURCE[start:end if end > start else len(SOURCE)]


class NativeFocusTransitionRegression(unittest.TestCase):
    def test_profile_switch_commits_on_ui_before_next_io_operation(self):
        body = method("changeInstagramProfile")
        self.assertIn("io.execute(() -> {", body)
        self.assertIn("postAccountTransitionAndWait(() -> applyInstagramProfileChange(key, label))", body)
        self.assertNotIn("io.execute(() -> mainHandler.post", body)
        barrier = method("postAccountTransitionAndWait")
        self.assertIn("CountDownLatch applied = new CountDownLatch(1)", barrier)
        self.assertIn("mainHandler.post(() -> {", barrier)
        self.assertIn("finally { applied.countDown(); }", barrier)
        self.assertIn("applied.await();", barrier)
        self.assertIn("if (failure.get() != null) throw failure.get()", barrier)

    def test_owner_switch_and_logout_are_serialized_and_reset_generation(self):
        account = SOURCE[SOURCE.index("savedAccountSignIn.setVisibility("):
                         SOURCE.index("private void resetAfterAccountChange()")]
        self.assertIn("api.prepareAnotherAccount();", account)
        self.assertIn("api.activateRememberedAccount(selected);", account)
        self.assertEqual(account.count("postAccountTransitionAndWait(() -> {"), 3)
        self.assertIn('runAsync(() -> {\n                api.logout();', account)
        self.assertNotIn("            api.logout();\n            resetAfterAccountChange();", account)
        reset = SOURCE[SOURCE.index("private void resetAfterAccountChange()"):
                       SOURCE.index("private void showWorkspaceScreen(", SOURCE.index("private void resetAfterAccountChange()"))]
        self.assertIn("++workspaceSyncGeneration;", reset)
        self.assertIn("syncedPending = new JSONArray();", reset)

    def test_focus_runs_only_in_original_owner_instagram_and_generation(self):
        scoped = method("runFocusScopedAsync")
        for gate in [
            "final String owner = api.getEmail();",
            "final String instagram = api.getInstagramProfile();",
            "final long generation = workspaceSyncGeneration;",
            "generation != workspaceSyncGeneration",
            "!owner.equalsIgnoreCase(api.getEmail())",
            "!instagram.equals(api.getInstagramProfile())",
            "task.run();",
        ]:
            self.assertIn(gate, scoped)
        for name in ["loadBatches", "createFocusBatch", "createDoubleCheckBatch",
                     "loadBatch", "openFocusProfile", "finalizeBatch"]:
            body = method(name)
            self.assertIn("runFocusScopedAsync(() -> {", body, name)
            self.assertNotIn("runAsync(() -> {", body, name)

    def test_webview_session_bridge_does_not_mutate_owner_on_foreign_thread(self):
        bridge = SOURCE[SOURCE.index("public void syncSession(String sessionJson)"):
                        SOURCE.index("public void openNativeFocus()", SOURCE.index("public void syncSession(String sessionJson)"))]
        self.assertRegex(bridge, r"io\.execute\(\(\) -> \{[\s\S]*?api\.adoptWebSession\(sessionJson\)")
        self.assertIn("postAccountTransitionAndWait(() -> {", bridge)
        self.assertIn("resetAfterAccountChange(true)", bridge,
                      "A WebView-mediated login must not destroy the active WebView")
        resets = SOURCE[SOURCE.index("private void resetAfterAccountChange()"):
                        SOURCE.index("private void showWorkspaceScreen(")]
        self.assertIn("if (!preserveActiveWebView) disposeWorkspaceWebView();", resets)

    def test_confirmed_profile_deletion_commits_legacy_scope_before_next_job(self):
        body = SOURCE[SOURCE.index("private void showFinalInstagramDeleteConfirmation("):
                      SOURCE.index("private void changeInstagramProfile(")]
        self.assertIn("api.deleteInstagramProfile(key, username);", body)
        self.assertIn("postAccountTransitionAndWait(() -> {", body)
        self.assertIn('applyInstagramProfileChange("legacy", "Datos anteriores")', body)
        self.assertLess(body.index("api.deleteInstagramProfile(key, username);"),
                        body.index("postAccountTransitionAndWait(() -> {"))
        self.assertNotIn('mainHandler.post(() -> {\n                            api.setInstagramProfile("legacy"', body)

    def test_no_new_cloud_delete_or_real_instagram_actions(self):
        # This branch is strictly a sequencing/rejection change; new effects
        # must not be injected into auth and Focus transition helpers.
        for name in ["changeInstagramProfile", "postAccountTransitionAndWait", "runFocusScopedAsync"]:
            body = method(name)
            for forbidden in ["deleteUnscoped(", "deleteInstagramProfile(", "perform_visible_action",
                              "profile_state?on_conflict=", "clearWorkspaceCacheForProfile("]:
                self.assertNotIn(forbidden, body)


if __name__ == "__main__":
    unittest.main()
