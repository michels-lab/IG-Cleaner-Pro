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


    def test_pending_52_cloud_vs_zero_html_has_visible_provenance(self):
        # Native Android must not present an imported/cloud copy as live Instagram.
        self.assertIn('list_name,payload,item_count,captured_at,source_device,updated_at', self.sync)
        self.assertIn('case "pending" -> {', self.sync)
        self.assertIn('pendingCapturedAt = parseInstant(captured).toEpochMilli()', self.sync)
        self.assertIn('pendingSnapshotPresent = readyPendingPresent', self.sync)
        self.assertIn('pendingSnapshotCached = false', self.sync)
        self.assertIn('pendingSnapshotCapturedAt = readyPendingCapturedAt', self.sync)
        self.assertIn('pendingSourceExplanation()', SOURCE)
        self.assertIn('NOT a live Instagram count', SOURCE)
        self.assertIn('CACHED REQUESTS', SOURCE)
        self.assertIn('SAVED REQUESTS', SOURCE)
        self.assertIn('homePendingCount.setText(pendingSnapshotPresent ?', SOURCE)
        self.assertIn('kpiMain.setText("—")', SOURCE)
        self.assertIn('No Pending export was synchronized', SOURCE)
        layout = (pathlib.Path(__file__).resolve().parents[1] /
                  "android/app/src/main/res/layout/screen_mobile_workspace.xml").read_text(encoding="utf-8")
        self.assertIn('android:id="@+id/homePendingLabel"', layout)

    def test_cache_keeps_pending_history_but_never_claims_it_is_fresh(self):
        load = SOURCE[SOURCE.index('private boolean loadWorkspaceCache()'):
                      SOURCE.index('private void saveWorkspaceCache()')]
        save = SOURCE[SOURCE.index('private void saveWorkspaceCache()'):
                      SOURCE.index('private void clearWorkspaceCache()')]
        clear = SOURCE[SOURCE.index('private void clearWorkspaceCacheForProfile('):
                       SOURCE.index('private String cacheSuffix()', SOURCE.index('private void clearWorkspaceCacheForProfile('))]
        for field in ['pending_present_', 'pending_captured_at_']:
            self.assertIn(field, load)
            self.assertIn(field, save)
            self.assertIn(field, clear)
        self.assertIn('pendingSnapshotCached = true;', load)
        # A failed/offline fetch must keep the cached 52 distinguishable from cloud.
        self.assertIn('boolean restored = loadWorkspaceCache()', SOURCE)
        self.assertIn('renderMobileWorkspace();', SOURCE)
        # Account A -> B -> A cannot reuse A's in-memory 52 while B loads.
        self.assertIn('pendingSnapshotPresent = false;', self.profile_change)
        self.assertIn('pendingSnapshotCapturedAt = 0L;', self.profile_change)
        self.assertIn('pendingSnapshotCached = false;', self.profile_change)
        reset = SOURCE[SOURCE.index('private void resetAfterAccountChange()'):
                       SOURCE.index('private void showWorkspaceScreen(', SOURCE.index('private void resetAfterAccountChange()'))]
        self.assertIn('pendingSnapshotPresent = false;', reset)
        self.assertIn('pendingSnapshotCached = false;', reset)
        self.assertIn('pendingSnapshotCapturedAt = 0L;', reset)

    def test_focus_refresh_carries_same_pending_source_truth(self):
        body = SOURCE[SOURCE.index('private void refreshFocusSourceData()'):
                      SOURCE.index('private Set<String> activeFocusUsernames()', SOURCE.index('private void refreshFocusSourceData()'))]
        self.assertIn('captured_at,source_device,updated_at', body)
        self.assertIn('pendingSnapshotPresent = pendingPresent', body)
        self.assertIn('pendingSnapshotCached = false', body)
        self.assertIn('pendingSnapshotCapturedAt = pendingCapturedAt', body)


    def test_pending_review_history_fetch_is_complete_beyond_provider_page_cap(self):
        # Negative regression: a single limit=20000 query can return only
        # the newest server-capped 1000 rows, losing older Pending decisions.
        start = SOURCE.index('private JSONArray loadCompleteProfileStates()')
        end = SOURCE.index('private void mergeRemoteProfileState(', start)
        method = SOURCE[start:end]
        self.assertIn('loadCompleteProfileStates()', self.sync)
        self.assertNotIn('limit=20000', self.sync)
        self.assertIn('&order=username.asc,module.asc&limit=', method)
        self.assertIn('&offset=', method)
        self.assertIn('offset += page.length()', method,
                      'Advance by actual rows returned; provider may cap below 1000')
        self.assertIn('if (page.length() == 0) return complete;', method)
        self.assertIn('!seen.add(username + "|" + module)', method,
                      'Duplicate/truncated pages cannot silently create false Pending')
        self.assertIn('throw new IllegalStateException', method)
        focus_start = SOURCE.index('private void refreshFocusSourceData()')
        focus_end = SOURCE.index('private Set<String> activeFocusUsernames()', focus_start)
        self.assertIn('loadCompleteProfileStates()', SOURCE[focus_start:focus_end],
                      'Focus and Home must not disagree about Pending reviews')


if __name__ == "__main__":
    unittest.main()
