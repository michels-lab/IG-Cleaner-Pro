"""Android native workspace sync may not reapply old account data after A-B-A."""
import pathlib
import unittest

SOURCE = (pathlib.Path(__file__).resolve().parents[1] /
          "android/app/src/main/java/com/michelslab/igcleaner/MainActivity.java").read_text(encoding="utf-8")


class NativeWorkspaceRaceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        begin = SOURCE.index("private void loadMobileWorkspace()")
        end = SOURCE.index("private void mergeRemoteProfileState(", begin)
        cls.sync = SOURCE[begin:end]
        a = SOURCE.index("private void applyInstagramProfileChange(")
        b = SOURCE.index("private void showNativeAccountScreen(", a)
        cls.profile_change = SOURCE[a:b]

    def test_requests_have_monotonically_new_generations(self):
        self.assertIn("private volatile long workspaceSyncGeneration", SOURCE)
        self.assertIn("final long requestGeneration = ++workspaceSyncGeneration", self.sync)
        self.assertIn("++workspaceSyncGeneration;", self.profile_change,
                      "Switching A-B-A must cancel the first A result")
        self.assertIn("requestGeneration != workspaceSyncGeneration", self.sync)

    def test_owner_and_instagram_identity_checked_before_any_cache_write(self):
        self.assertIn("final String loadingOwner = api.getEmail()", self.sync)
        self.assertIn("!loadingOwner.equalsIgnoreCase(api.getEmail())", self.sync)
        self.assertIn("!loadingInstagram.equals(api.getInstagramProfile())", self.sync)
        start = self.sync.index("mainHandler.post(() -> {")
        accept = self.sync.index("if (requestGeneration != workspaceSyncGeneration", start)
        cache = self.sync.index("saveWorkspaceCache()", start)
        self.assertLess(accept, cache, "Reject old response before writing disk cache")
        self.assertLess(self.sync.index("!loadingOwner.equalsIgnoreCase(api.getEmail())"), cache)
        self.assertNotIn("saveWorkspaceCache();", self.sync[:start],
                         "Worker thread must not write another account's cache")

    def test_old_completion_does_not_hide_new_loading_indicator(self):
        finally_body = self.sync[self.sync.index("} finally {"):]
        self.assertIn("if (requestGeneration != workspaceSyncGeneration) return;", finally_body)
        self.assertLess(finally_body.index("if (requestGeneration != workspaceSyncGeneration)"),
                        finally_body.index("workspaceSyncProgress.setVisibility(View.GONE)"))

    def test_new_account_displays_only_its_fresh_state(self):
        self.assertIn("syncedFollowing = new JSONArray()", self.profile_change)
        self.assertIn("syncedFollowers = new JSONArray()", self.profile_change)
        self.assertIn("syncedWorkspaceState = new JSONObject()", self.profile_change)
        # First setInstagramProfile handles label refresh for the same account.
        # Only the second invocation changes the underlying Instagram scope.
        self.assertLess(self.profile_change.index("++workspaceSyncGeneration"),
                        self.profile_change.rindex("api.setInstagramProfile(key, label)"))


if __name__ == "__main__":
    unittest.main()
