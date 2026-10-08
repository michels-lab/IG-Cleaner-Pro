package com.michelslab.igcleaner;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.ContentValues;
import android.content.SharedPreferences;
import android.net.Uri;
import android.provider.MediaStore;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.Environment;
import android.text.format.DateFormat;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.HapticFeedbackConstants;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.ProgressBar;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.button.MaterialButtonToggleGroup;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;
import com.google.android.material.progressindicator.LinearProgressIndicator;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;
import com.google.android.material.textfield.TextInputLayout;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public final class MainActivity extends AppCompatActivity {
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    private SyncApi api;
    private String deviceId;
    private String currentScreen = "workspace";
    private String workspaceTargetPage = "";

    private MaterialToolbar toolbar;
    private BottomNavigationView bottomNav;
    private FrameLayout content;
    private TextView globalStatus;
    private TextView brandContext;

    private WebView workspaceWebView;
    private ProgressBar workspaceLoading;
    private ValueCallback<Uri[]> filePathCallback;
    private static final int FILE_CHOOSER_REQUEST = 12035;
    private static final String[] SYNC_TABLES = new String[]{
            "devices",
            "audit_events",
            "focus_batches",
            "focus_batch_items",
            "profile_state",
            "list_snapshots",
            "workspace_state"
    };

    private View mobileWorkspaceView;
    private RecyclerView workspaceProfileList;
    private WorkspaceProfileAdapter workspaceAdapter;
    private TextView mobileWorkspaceTitle;
    private TextView mobileWorkspaceSubtitle;
    private TextView workspaceSectionTitle;
    private TextView workspaceSectionSubtitle;
    private TextView kpiMain;
    private TextView kpiMainLabel;
    private TextView kpiSecondary;
    private TextView kpiSecondaryLabel;
    private TextView homeReviewCount;
    private TextView homeReviewLabel;
    private TextView homeMutualCount;
    private TextView homeFollowerCount;
    private TextView homePendingCount;
    private View homeKpis;
    private View sectionKpis;
    private View reviewTabsScroll;
    private TextInputLayout workspaceSearchLayout;
    private LinearProgressIndicator workspaceSyncProgress;
    private SwipeRefreshLayout workspaceRefresh;
    private JSONArray syncedFollowing = new JSONArray();
    private JSONArray syncedFollowers = new JSONArray();
    private JSONArray syncedPending = new JSONArray();
    private JSONObject syncedWorkspaceState = new JSONObject();
    private boolean syncedReviewStateAvailable = false;
    private String workspaceSection = "home";
    private static final String CACHE_PREFS = "igc_workspace_cache";

    private View focusView;
    private TextView focusTitle;
    private TextView focusSubtitle;
    private LinearProgressIndicator focusProgress;
    private TextView focusProgressLabel;
    private ScrollView batchScroll;
    private LinearLayout batchContainer;
    private RecyclerView profileList;
    private LinearLayout focusActions;
    private MaterialButton nextPending;
    private MaterialButton finishBatch;
    private MaterialButton refreshFocus;
    private ProfileAdapter focusAdapter;

    private JSONObject currentBatch;
    private JSONArray currentItems = new JSONArray();
    private final Map<String, JSONObject> itemByUsername = new HashMap<>();
    private final Set<String> opened = new HashSet<>();
    private final Set<String> remotelyReviewed = new HashSet<>();
    private final Map<String, String> reviewedDevice = new HashMap<>();

    private View auditView;
    private RecyclerView auditList;
    private MaterialButton finishAudit;
    private ProfileAdapter auditAdapter;
    private final Map<String, JSONObject> auditEventByUsername = new HashMap<>();
    private final Set<String> auditOpened = new HashSet<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        api = new SyncApi(this);
        deviceId = getSharedPreferences("igc_sync", MODE_PRIVATE)
                .getString("device_id", "");
        if (deviceId.isBlank()) {
            deviceId = "android_" + UUID.randomUUID();
            getSharedPreferences("igc_sync", MODE_PRIVATE)
                    .edit().putString("device_id", deviceId).apply();
        }

        View root = findViewById(R.id.mainRoot);
        toolbar = findViewById(R.id.toolbar);
        bottomNav = findViewById(R.id.bottomNav);
        content = findViewById(R.id.content);
        globalStatus = findViewById(R.id.globalStatus);
        brandContext = findViewById(R.id.brandContext);

        // Keep app content below the status bar, while the bottom navigation owns
        // the navigation-bar inset. This avoids double-insetting and clipped labels
        // on Samsung 3-button navigation as well as gesture navigation.
        final int navBaseHeight = dp(80);
        final int navBaseTop = dp(4);
        final int navBaseBottom = dp(8);
        ViewCompat.setOnApplyWindowInsetsListener(root, (v, insets) -> {
            Insets status = insets.getInsets(WindowInsetsCompat.Type.statusBars());
            Insets navigation = insets.getInsets(WindowInsetsCompat.Type.navigationBars());
            v.setPadding(0, status.top, 0, 0);

            ViewGroup.LayoutParams params = bottomNav.getLayoutParams();
            int targetHeight = navBaseHeight + navigation.bottom;
            if (params.height != targetHeight) {
                params.height = targetHeight;
                bottomNav.setLayoutParams(params);
            }
            bottomNav.setPadding(
                    bottomNav.getPaddingLeft(),
                    navBaseTop,
                    bottomNav.getPaddingRight(),
                    navBaseBottom + navigation.bottom);
            return insets;
        });
        ViewCompat.requestApplyInsets(root);

        toolbar.setOnMenuItemClickListener(item -> {
            if (item.getItemId() == R.id.actionSync) {
                syncNow();
                return true;
            }
            if (item.getItemId() == R.id.actionAbout) {
                showAbout();
                return true;
            }
            return false;
        });

        bottomNav.setOnItemSelectedListener(item -> {
            bottomNav.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK);
            if (item.getItemId() == R.id.navHome) {
                showMobileWorkspaceScreen("home");
                return true;
            }
            if (item.getItemId() == R.id.navReview) {
                showMobileWorkspaceScreen("review");
                return true;
            }
            if (item.getItemId() == R.id.navFocus) {
                showFocusScreen();
                return true;
            }
            if (item.getItemId() == R.id.navActivity) {
                showAuditScreen();
                return true;
            }
            if (item.getItemId() == R.id.navProfile) {
                showNativeAccountScreen();
                return true;
            }
            return false;
        });

        bottomNav.setSelectedItemId(R.id.navHome);
    }

    @Override
    protected void onDestroy() {
        disposeWorkspaceWebView();
        io.shutdownNow();
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if (("advanced".equals(currentScreen) || "account".equals(currentScreen)) && workspaceWebView != null && workspaceWebView.canGoBack()) {
            workspaceWebView.goBack();
            return;
        }
        if ("focus".equals(currentScreen) && currentBatch != null) {
            currentBatch = null;
            showFocusScreen();
            return;
        }
        super.onBackPressed();
    }


    private void showMobileWorkspaceScreen() {
        showMobileWorkspaceScreen("home");
    }

    private void showMobileWorkspaceScreen(String initialSection) {
        disposeWorkspaceWebView();
        currentScreen = "workspace";
        currentBatch = null;
        workspaceSection = initialSection == null || initialSection.isBlank() ? "home" : initialSection;
        setBrandContext("home".equals(workspaceSection) ? "HOME" : "REVIEW");

        mobileWorkspaceView = LayoutInflater.from(this).inflate(R.layout.screen_mobile_workspace, content, false);
        content.removeAllViews();
        content.addView(mobileWorkspaceView);

        workspaceProfileList = mobileWorkspaceView.findViewById(R.id.workspaceProfileList);
        mobileWorkspaceTitle = mobileWorkspaceView.findViewById(R.id.mobileWorkspaceTitle);
        mobileWorkspaceSubtitle = mobileWorkspaceView.findViewById(R.id.mobileWorkspaceSubtitle);
        workspaceSectionTitle = mobileWorkspaceView.findViewById(R.id.workspaceSectionTitle);
        workspaceSectionSubtitle = mobileWorkspaceView.findViewById(R.id.workspaceSectionSubtitle);
        kpiMain = mobileWorkspaceView.findViewById(R.id.kpiMain);
        kpiMainLabel = mobileWorkspaceView.findViewById(R.id.kpiMainLabel);
        kpiSecondary = mobileWorkspaceView.findViewById(R.id.kpiSecondary);
        kpiSecondaryLabel = mobileWorkspaceView.findViewById(R.id.kpiSecondaryLabel);
        homeReviewCount = mobileWorkspaceView.findViewById(R.id.homeReviewCount);
        homeReviewLabel = mobileWorkspaceView.findViewById(R.id.homeReviewLabel);
        homeMutualCount = mobileWorkspaceView.findViewById(R.id.homeMutualCount);
        homeFollowerCount = mobileWorkspaceView.findViewById(R.id.homeFollowerCount);
        homePendingCount = mobileWorkspaceView.findViewById(R.id.homePendingCount);
        homeKpis = mobileWorkspaceView.findViewById(R.id.homeKpis);
        sectionKpis = mobileWorkspaceView.findViewById(R.id.sectionKpis);
        reviewTabsScroll = mobileWorkspaceView.findViewById(R.id.reviewTabsScroll);
        workspaceSearchLayout = mobileWorkspaceView.findViewById(R.id.workspaceSearchLayout);
        workspaceSyncProgress = mobileWorkspaceView.findViewById(R.id.workspaceSyncProgress);
        workspaceRefresh = mobileWorkspaceView.findViewById(R.id.workspaceRefresh);

        workspaceAdapter = new WorkspaceProfileAdapter(row -> {
            mobileWorkspaceView.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
            openInstagram(row.username);
        });
        workspaceProfileList.setLayoutManager(new LinearLayoutManager(this));
        workspaceProfileList.setAdapter(workspaceAdapter);

        MaterialButtonToggleGroup tabs = mobileWorkspaceView.findViewById(R.id.workspaceTabs);
        int initialTab = switch (workspaceSection) {
            case "mutuals" -> R.id.tabMutuals;
            case "followers" -> R.id.tabFollowers;
            case "pending" -> R.id.tabPending;
            default -> R.id.tabReview;
        };
        tabs.check(initialTab);
        tabs.addOnButtonCheckedListener((group, checkedId, isChecked) -> {
            if (!isChecked) return;
            group.performHapticFeedback(HapticFeedbackConstants.CLOCK_TICK);
            if (checkedId == R.id.tabReview) workspaceSection = "review";
            else if (checkedId == R.id.tabMutuals) workspaceSection = "mutuals";
            else if (checkedId == R.id.tabFollowers) workspaceSection = "followers";
            else if (checkedId == R.id.tabPending) workspaceSection = "pending";
            renderMobileWorkspace();
        });

        TextInputEditText search = mobileWorkspaceView.findViewById(R.id.workspaceSearch);
        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence value, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence value, int start, int before, int count) {
                if (workspaceAdapter != null) workspaceAdapter.filter(value == null ? "" : value.toString());
            }
            @Override public void afterTextChanged(Editable value) {}
        });

        workspaceRefresh.setColorSchemeResources(R.color.ig_cyan, R.color.ig_blue, R.color.ig_violet);
        workspaceRefresh.setProgressBackgroundColorSchemeResource(R.color.ig_surface_2);
        workspaceRefresh.setOnRefreshListener(this::loadMobileWorkspace);

        if (!api.hasSession()) {
            mobileWorkspaceTitle.setText("Sign in required");
            mobileWorkspaceSubtitle.setText("Open Profile to connect your account and restore your synced workspace.");
            workspaceSectionTitle.setText("Your lists stay private");
            workspaceSectionSubtitle.setText("Once connected, Home and Review restore automatically.");
            workspaceAdapter.submit(new ArrayList<>());
            homeKpis.setVisibility(View.GONE);
            sectionKpis.setVisibility(View.GONE);
            reviewTabsScroll.setVisibility(View.GONE);
            workspaceSearchLayout.setVisibility(View.GONE);
            return;
        }

        boolean restored = loadWorkspaceCache();
        if (restored) {
            renderMobileWorkspace();
            mobileWorkspaceSubtitle.setText("Cached workspace restored · checking for updates…");
        }
        workspaceSyncProgress.setVisibility(View.VISIBLE);
        loadMobileWorkspace();
    }

    private void loadMobileWorkspace() {
        if (!api.hasSession()) return;
        setGlobalStatus("SYNCING • restoring latest state");
        if (workspaceSyncProgress != null) workspaceSyncProgress.setVisibility(View.VISIBLE);

        runAsync(() -> {
            try {
                touchDevice();
                JSONArray snapshots = api.get("list_snapshots?select=list_name,payload,item_count,updated_at");
                JSONArray stateRows = api.get("workspace_state?select=payload,updated_at&state_key=eq.primary&limit=1");
                JSONArray profileStates = api.get("profile_state?select=username,module,reviewed_at,reviewed_device,decision,protected,context&order=reviewed_at.desc&limit=20000");

                JSONObject stateRow = stateRows.length() > 0 ? stateRows.optJSONObject(0) : null;
                syncedReviewStateAvailable = stateRow != null || profileStates.length() > 0;
                JSONObject state = stateRow == null ? null : stateRow.optJSONObject("payload");
                if (state == null) state = new JSONObject();
                long snapshotUpdatedAt = stateRow == null
                        ? 0L
                        : parseInstant(stateRow.optString("updated_at", "")).toEpochMilli();
                state.put("_snapshotUpdatedAt", snapshotUpdatedAt);
                mergeRemoteProfileState(state, profileStates);

                JSONArray following = new JSONArray();
                JSONArray followers = new JSONArray();
                JSONArray pending = new JSONArray();

                for (int i = 0; i < snapshots.length(); i++) {
                    JSONObject snap = snapshots.optJSONObject(i);
                    if (snap == null) continue;
                    JSONArray payload = snap.optJSONArray("payload");
                    if (payload == null) payload = new JSONArray();
                    switch (snap.optString("list_name")) {
                        case "following" -> following = payload;
                        case "followers" -> followers = payload;
                        case "pending" -> pending = payload;
                    }
                }

                syncedFollowing = following;
                syncedFollowers = followers;
                syncedPending = pending;
                syncedWorkspaceState = state;
                saveWorkspaceCache();

                mainHandler.post(() -> {
                    if (!"workspace".equals(currentScreen) || mobileWorkspaceView == null) return;
                    renderMobileWorkspace();
                    setGlobalStatus("SYNCED • " + DateFormat.getTimeFormat(this).format(new Date()));
                });
            } finally {
                mainHandler.post(() -> {
                    if (workspaceSyncProgress != null) workspaceSyncProgress.setVisibility(View.GONE);
                    if (workspaceRefresh != null) workspaceRefresh.setRefreshing(false);
                });
            }
        }, true);
    }

    private void mergeRemoteProfileState(JSONObject state, JSONArray profileStates) throws Exception {
        Set<String> done = jsonStringSet(state.optJSONArray("done"));
        Set<String> protectedUsers = jsonStringSet(state.optJSONArray("protected"));
        JSONObject reviewedMeta = state.optJSONObject("reviewedMeta");
        if (reviewedMeta == null) reviewedMeta = new JSONObject();
        JSONObject pendingReviewed = state.optJSONObject("pendingReviewedMeta");
        if (pendingReviewed == null) pendingReviewed = new JSONObject();

        long snapshotUpdatedAt = state.optLong("_snapshotUpdatedAt", 0L);

        for (int i = 0; i < profileStates.length(); i++) {
            JSONObject row = profileStates.optJSONObject(i);
            if (row == null) continue;
            String username = row.optString("username", "").toLowerCase(Locale.ROOT);
            if (username.isBlank()) continue;
            long reviewedAt = parseInstant(row.optString("reviewed_at")).toEpochMilli();
            if (reviewedAt <= 0) continue;

            // A complete Desktop workspace snapshot is authoritative for every
            // profile state at or before its own timestamp. Only reviews that
            // happened after that snapshot are overlaid from profile_state.
            if (snapshotUpdatedAt > 0 && reviewedAt <= snapshotUpdatedAt) continue;

            String module = row.optString("module", "main");

            if (row.optBoolean("protected", false)) protectedUsers.add(username);

            if ("pending".equals(module)) {
                JSONObject old = pendingReviewed.optJSONObject(username);
                if (old == null || reviewedAt >= old.optLong("reviewedAt", 0)) {
                    pendingReviewed.put(username, new JSONObject()
                            .put("reviewedAt", reviewedAt)
                            .put("decision", row.optString("decision", ""))
                            .put("label", "Sync · " + row.optString("reviewed_device", "remote")));
                }
                continue;
            }

            JSONObject context = row.optJSONObject("context");
            JSONObject rowContext = context == null ? null : context.optJSONObject("row");
            JSONObject old = reviewedMeta.optJSONObject(username);
            if (old != null && old.optLong("reviewedAt", 0) > reviewedAt) continue;

            String mode = ("followers".equals(module) || "mutual".equals(module)) ? "followers" : "following";
            JSONObject meta = new JSONObject()
                    .put("mode", mode)
                    .put("reviewedAt", reviewedAt)
                    .put("reviewReason", row.optString("decision", ""))
                    .put("reviewSource", "sync:" + row.optString("reviewed_device", "remote"));

            if (rowContext != null) {
                meta.put("relation", rowContext.optString("relation", ""));
                meta.put("relationGood", rowContext.optBoolean("relationGood", false));
                meta.put("followsBack", rowContext.optBoolean("followsBack", false));
                meta.put("isFollower", rowContext.optBoolean("isFollower", false));
                meta.put("iFollow", "following".equals(mode) || rowContext.optBoolean("iFollow", false));
                meta.put("dateMain", rowContext.optLong("dateMain", 0));
            }
            reviewedMeta.put(username, meta);
            done.add(username);
        }

        JSONArray doneArray = new JSONArray();
        for (String username : done) doneArray.put(username);
        JSONArray protectedArray = new JSONArray();
        for (String username : protectedUsers) protectedArray.put(username);
        state.put("done", doneArray);
        state.put("protected", protectedArray);
        state.put("reviewedMeta", reviewedMeta);
        state.put("pendingReviewedMeta", pendingReviewed);
    }

    private boolean loadWorkspaceCache() {
        try {
            SharedPreferences cache = getSharedPreferences(CACHE_PREFS, MODE_PRIVATE);
            String suffix = cacheSuffix();
            String following = cache.getString("following_" + suffix, "");
            String followers = cache.getString("followers_" + suffix, "");
            String pending = cache.getString("pending_" + suffix, "");
            String state = cache.getString("state_" + suffix, "");
            if (following.isBlank() || followers.isBlank()) return false;
            syncedFollowing = new JSONArray(following);
            syncedFollowers = new JSONArray(followers);
            syncedPending = pending.isBlank() ? new JSONArray() : new JSONArray(pending);
            syncedWorkspaceState = state.isBlank() ? new JSONObject() : new JSONObject(state);
            syncedReviewStateAvailable = cache.getBoolean("review_state_available_" + suffix, false);
            return true;
        } catch (Exception ignored) {
            return false;
        }
    }

    private void saveWorkspaceCache() {
        try {
            String suffix = cacheSuffix();
            getSharedPreferences(CACHE_PREFS, MODE_PRIVATE).edit()
                    .putString("following_" + suffix, syncedFollowing.toString())
                    .putString("followers_" + suffix, syncedFollowers.toString())
                    .putString("pending_" + suffix, syncedPending.toString())
                    .putString("state_" + suffix, syncedWorkspaceState.toString())
                    .putBoolean("review_state_available_" + suffix, syncedReviewStateAvailable)
                    .putLong("updated_" + suffix, System.currentTimeMillis())
                    .apply();
        } catch (Exception ignored) {}
    }

    private void clearWorkspaceCache() {
        SharedPreferences cache = getSharedPreferences(CACHE_PREFS, MODE_PRIVATE);
        String suffix = cacheSuffix();
        cache.edit()
                .remove("following_" + suffix)
                .remove("followers_" + suffix)
                .remove("pending_" + suffix)
                .remove("state_" + suffix)
                .remove("review_state_available_" + suffix)
                .remove("updated_" + suffix)
                .apply();
    }

    private String cacheSuffix() {
        String email = api.getEmail() == null ? "" : api.getEmail().trim().toLowerCase(Locale.ROOT);
        return Integer.toHexString(email.hashCode());
    }

    private int countPendingUnresolved(JSONObject pendingReviewed, JSONObject pendingSnooze) {
        int unresolved = 0;
        long now = System.currentTimeMillis();
        for (int i = 0; i < syncedPending.length(); i++) {
            JSONObject p = syncedPending.optJSONObject(i);
            if (p == null) continue;
            String username = p.optString("username", "").toLowerCase(Locale.ROOT);
            if (username.isBlank()) continue;
            JSONObject meta = pendingReviewed == null ? null : pendingReviewed.optJSONObject(username);
            long snoozeUntil = pendingSnooze == null ? 0 : pendingSnooze.optLong(username, 0);
            boolean resolved = meta != null && meta.optLong("reviewedAt", 0) > 0;
            if (!resolved && snoozeUntil <= now) unresolved++;
        }
        return unresolved;
    }

    private void renderMobileWorkspace() {
        if (workspaceAdapter == null) return;

        Map<String, JSONObject> followingMapNative = jsonArrayByUsername(syncedFollowing);
        Map<String, JSONObject> followersMapNative = jsonArrayByUsername(syncedFollowers);
        Set<String> done = jsonStringSet(syncedWorkspaceState.optJSONArray("done"));
        Set<String> protectedUsers = jsonStringSet(syncedWorkspaceState.optJSONArray("protected"));
        JSONObject snooze = syncedWorkspaceState.optJSONObject("snooze");
        JSONObject reviewedMeta = syncedWorkspaceState.optJSONObject("reviewedMeta");
        JSONObject pendingReviewed = syncedWorkspaceState.optJSONObject("pendingReviewedMeta");
        JSONObject pendingSnooze = syncedWorkspaceState.optJSONObject("pendingSnooze");

        int mutuals = countMutuals(followingMapNative, followersMapNative);
        int unresolvedReview = 0;
        for (Map.Entry<String, JSONObject> entry : followingMapNative.entrySet()) {
            if (followersMapNative.containsKey(entry.getKey())) continue;
            if (!isNativeFollowingResolved(entry.getKey(), entry.getValue(), done, protectedUsers, snooze, reviewedMeta)) {
                unresolvedReview++;
            }
        }
        int unresolvedPending = countPendingUnresolved(pendingReviewed, pendingSnooze);

        boolean home = "home".equals(workspaceSection);
        homeKpis.setVisibility(home ? View.VISIBLE : View.GONE);
        reviewTabsScroll.setVisibility(home ? View.GONE : View.VISIBLE);
        sectionKpis.setVisibility(home ? View.GONE : View.VISIBLE);
        workspaceSearchLayout.setVisibility(home ? View.GONE : View.VISIBLE);
        mobileWorkspaceTitle.setText(home ? "Home" : "Review");

        homeReviewCount.setText(syncedReviewStateAvailable ? String.valueOf(unresolvedReview) : "—");
        homeReviewLabel.setText(syncedReviewStateAvailable ? "REVIEW PENDING" : "REVIEW STATE");
        homeMutualCount.setText(String.valueOf(mutuals));
        homeFollowerCount.setText(String.valueOf(followersMapNative.size()));
        homePendingCount.setText(String.valueOf(unresolvedPending));

        List<WorkspaceProfileAdapter.Row> rows = new ArrayList<>();
        int main = 0;
        int total = 0;

        if (home) {
            for (Map.Entry<String, JSONObject> entry : followingMapNative.entrySet()) {
                String username = entry.getKey();
                if (followersMapNative.containsKey(username)) continue;
                if (!isNativeFollowingResolved(username, entry.getValue(), done, protectedUsers, snooze, reviewedMeta)) {
                    if (rows.size() < 30) rows.add(new WorkspaceProfileAdapter.Row(
                            username, nativeDateDetail(entry.getValue(), "Needs review"), "REVIEW"));
                }
            }
            workspaceSectionTitle.setText(syncedReviewStateAvailable ? "Continue review" : "Restore review history");
            workspaceSectionSubtitle.setText(!syncedReviewStateAvailable
                    ? "Your relationship lists are synced, but Desktop has not published its review history yet. Sync Desktop v120.35 once to restore the real pending count."
                    : (unresolvedReview == 0
                        ? "Your main cleanup queue is clear."
                        : unresolvedReview + " profiles still need a decision. Tap one to open Instagram."));
        } else if ("review".equals(workspaceSection)) {
            int rawNotBack = 0;
            for (Map.Entry<String, JSONObject> entry : followingMapNative.entrySet()) {
                String username = entry.getKey();
                if (followersMapNative.containsKey(username)) continue;
                rawNotBack++;
                if (!isNativeFollowingResolved(username, entry.getValue(), done, protectedUsers, snooze, reviewedMeta)) {
                    rows.add(new WorkspaceProfileAdapter.Row(
                            username, nativeDateDetail(entry.getValue(), "You follow"), "NOT BACK"));
                }
            }
            main = syncedReviewStateAvailable ? unresolvedReview : rawNotBack;
            total = rawNotBack;
            workspaceSectionTitle.setText("Not following back");
            workspaceSectionSubtitle.setText(syncedReviewStateAvailable
                    ? "Only unresolved accounts. Reviewed, protected and snoozed profiles stay out of this queue."
                    : "Review history has not been restored yet. These are raw relationship matches, not confirmed pending reviews.");
            kpiMainLabel.setText(syncedReviewStateAvailable ? "PENDING" : "RAW MATCHES");
            kpiSecondaryLabel.setText("RAW TOTAL");
        } else if ("mutuals".equals(workspaceSection)) {
            for (Map.Entry<String, JSONObject> entry : followingMapNative.entrySet()) {
                if (!followersMapNative.containsKey(entry.getKey())) continue;
                rows.add(new WorkspaceProfileAdapter.Row(
                        entry.getKey(), nativeDateDetail(entry.getValue(), "You follow each other"), "MUTUAL"));
            }
            main = rows.size();
            total = followingMapNative.size();
            workspaceSectionTitle.setText("Mutuals");
            workspaceSectionSubtitle.setText("People who follow you and you follow back.");
            kpiMainLabel.setText("MUTUALS");
            kpiSecondaryLabel.setText("FOLLOWING");
        } else if ("followers".equals(workspaceSection)) {
            for (Map.Entry<String, JSONObject> entry : followersMapNative.entrySet()) {
                boolean mutual = followingMapNative.containsKey(entry.getKey());
                rows.add(new WorkspaceProfileAdapter.Row(
                        entry.getKey(),
                        nativeDateDetail(entry.getValue(), mutual ? "You follow back" : "Follower only"),
                        mutual ? "MUTUAL" : "FOLLOWER"));
            }
            main = rows.size();
            total = Math.max(0, followersMapNative.size() - mutuals);
            workspaceSectionTitle.setText("Followers");
            workspaceSectionSubtitle.setText("Your synchronized followers list.");
            kpiMainLabel.setText("FOLLOWERS");
            kpiSecondaryLabel.setText("FOLLOWER ONLY");
        } else {
            long now = System.currentTimeMillis();
            for (int i = 0; i < syncedPending.length(); i++) {
                JSONObject p = syncedPending.optJSONObject(i);
                if (p == null) continue;
                String username = p.optString("username", "").toLowerCase(Locale.ROOT);
                if (username.isBlank()) continue;
                JSONObject meta = pendingReviewed == null ? null : pendingReviewed.optJSONObject(username);
                long snoozeUntil = pendingSnooze == null ? 0 : pendingSnooze.optLong(username, 0);
                boolean resolved = meta != null && meta.optLong("reviewedAt", 0) > 0;
                if (!resolved && snoozeUntil <= now) {
                    rows.add(new WorkspaceProfileAdapter.Row(
                            username, nativeDateDetail(p, "Request sent"), "PENDING"));
                }
            }
            main = unresolvedPending;
            total = syncedPending.length();
            workspaceSectionTitle.setText("Requests");
            workspaceSectionSubtitle.setText("Sent follow requests still waiting for review.");
            kpiMainLabel.setText("PENDING");
            kpiSecondaryLabel.setText("RAW TOTAL");
        }

        if (!home) {
            kpiMain.setText(String.valueOf(main));
            kpiSecondary.setText(String.valueOf(total));
        }
        mobileWorkspaceSubtitle.setText(syncedFollowing.length() + " following · " +
                syncedFollowers.length() + " followers · " + syncedPending.length() + " requests");
        workspaceAdapter.submit(rows);
    }

    private boolean isNativeFollowingResolved(String username, JSONObject source,
                                              Set<String> done, Set<String> protectedUsers,
                                              JSONObject snooze, JSONObject reviewedMeta) {
        if (protectedUsers.contains(username)) return true;
        if (snooze != null && snooze.optLong(username, 0) > System.currentTimeMillis()) return true;
        if (!done.contains(username) || reviewedMeta == null) return false;

        JSONObject meta = reviewedMeta.optJSONObject(username);
        if (meta == null) return false;
        if (!"following".equals(meta.optString("mode"))) return false;
        if (meta.optBoolean("relationGood", true)) return false;
        if (meta.optBoolean("followsBack", true)) return false;
        if (meta.optBoolean("isFollower", true)) return false;

        long reviewedAt = meta.optLong("reviewedAt", 0);
        long dateMain = source == null ? 0 : source.optLong("timestamp", 0);
        return reviewedAt > 0 && (dateMain <= 0 || dateMain * 1000L <= reviewedAt);
    }

    private Map<String, JSONObject> jsonArrayByUsername(JSONArray array) {
        LinkedHashMap<String, JSONObject> out = new LinkedHashMap<>();
        if (array == null) return out;
        for (int i = 0; i < array.length(); i++) {
            JSONObject row = array.optJSONObject(i);
            if (row == null) continue;
            String username = row.optString("username", "").toLowerCase(Locale.ROOT);
            if (!username.isBlank()) out.put(username, row);
        }
        return out;
    }

    private Set<String> jsonStringSet(JSONArray array) {
        Set<String> out = new HashSet<>();
        if (array == null) return out;
        for (int i = 0; i < array.length(); i++) {
            String value = array.optString(i, "").toLowerCase(Locale.ROOT);
            if (!value.isBlank()) out.add(value);
        }
        return out;
    }

    private int countMutuals(Map<String, JSONObject> following, Map<String, JSONObject> followers) {
        int count = 0;
        for (String username : following.keySet()) if (followers.containsKey(username)) count++;
        return count;
    }

    private String nativeDateDetail(JSONObject row, String prefix) {
        long ts = row == null ? 0 : row.optLong("timestamp", 0);
        if (ts <= 0) return prefix;
        try {
            Date date = new Date(ts * 1000L);
            return prefix + " · " + DateFormat.getMediumDateFormat(this).format(date);
        } catch (Exception ignored) {
            return prefix;
        }
    }

    private void showWorkspaceScreen() {
        showWorkspaceScreen("", "FULL WORKSPACE");
    }

    private void showWorkspaceAccountScreen() {
        showNativeAccountScreen();
    }

    private void showNativeAccountScreen() {
        disposeWorkspaceWebView();
        currentScreen = "account_native";
        setBrandContext("PROFILE");

        View view = LayoutInflater.from(this).inflate(R.layout.screen_account, content, false);
        content.removeAllViews();
        content.addView(view);

        LinearLayout authGroup = view.findViewById(R.id.authGroup);
        LinearLayout otpGroup = view.findViewById(R.id.otpGroup);
        MaterialCardView connectedCard = view.findViewById(R.id.connectedCard);
        TextInputEditText emailInput = view.findViewById(R.id.emailInput);
        TextInputEditText passwordInput = view.findViewById(R.id.passwordInput);
        TextInputEditText codeInput = view.findViewById(R.id.codeInput);
        TextInputEditText newPasswordInput = view.findViewById(R.id.newPasswordInput);
        MaterialButton passwordSignIn = view.findViewById(R.id.passwordSignIn);
        MaterialButton useCode = view.findViewById(R.id.useCode);
        MaterialButton sendCode = view.findViewById(R.id.sendCode);
        MaterialButton verifyCode = view.findViewById(R.id.verifyCode);
        MaterialButton sync = view.findViewById(R.id.syncNow);
        MaterialButton managePassword = view.findViewById(R.id.managePassword);
        MaterialButton exportCloudData = view.findViewById(R.id.exportCloudData);
        MaterialButton deleteCloudData = view.findViewById(R.id.deleteCloudData);
        MaterialButton logout = view.findViewById(R.id.logout);
        TextView accountEmail = view.findViewById(R.id.accountEmail);
        TextView label = view.findViewById(R.id.deviceLabel);

        emailInput.setText(api.getEmail());
        boolean connected = api.hasSession();
        authGroup.setVisibility(connected ? View.GONE : View.VISIBLE);
        connectedCard.setVisibility(connected ? View.VISIBLE : View.GONE);
        accountEmail.setText(api.getEmail());
        label.setText(deviceLabel() + " · session remembered on this device");

        passwordSignIn.setOnClickListener(v -> {
            v.performHapticFeedback(HapticFeedbackConstants.CONFIRM);
            setGlobalStatus("SIGNING IN • password");
            runAsync(() -> {
                api.signInWithPassword(textOf(emailInput), rawTextOf(passwordInput));
                touchDevice();
                mainHandler.post(() -> {
                    setGlobalStatus("CONNECTED • session restored");
                    showNativeAccountScreen();
                    Snackbar.make(content, "Signed in successfully", Snackbar.LENGTH_SHORT).show();
                });
            }, true);
        });

        useCode.setOnClickListener(v -> {
            boolean show = otpGroup.getVisibility() != View.VISIBLE;
            otpGroup.setVisibility(show ? View.VISIBLE : View.GONE);
            useCode.setText(show ? "Hide verification options" : "First time or forgot password?");
        });

        sendCode.setOnClickListener(v -> {
            setGlobalStatus("SENDING CODE • check your email");
            runAsync(() -> {
                api.sendOtp(textOf(emailInput));
                mainHandler.post(() -> {
                    setGlobalStatus("CODE SENT • waiting for verification");
                    Snackbar.make(content, "Verification code sent", Snackbar.LENGTH_LONG).show();
                });
            }, true);
        });

        verifyCode.setOnClickListener(v -> {
            setGlobalStatus("VERIFYING • securing account");
            runAsync(() -> {
                api.setEmail(textOf(emailInput));
                api.verifyOtpAndSetPassword(textOf(codeInput), rawTextOf(newPasswordInput));
                touchDevice();
                mainHandler.post(() -> {
                    setGlobalStatus("CONNECTED • password saved");
                    showNativeAccountScreen();
                    Snackbar.make(content, "Email verified and password saved", Snackbar.LENGTH_LONG).show();
                });
            }, true);
        });

        sync.setOnClickListener(v -> {
            setGlobalStatus("SYNCING • account and device");
            runAsync(() -> {
                touchDevice();
                mainHandler.post(() -> {
                    setGlobalStatus("SYNCED • " + DateFormat.getTimeFormat(this).format(new Date()));
                    Snackbar.make(content, "Account synced", Snackbar.LENGTH_SHORT).show();
                });
            }, true);
        });

        managePassword.setOnClickListener(v -> {
            TextInputEditText passwordField = new TextInputEditText(this);
            passwordField.setHint("New password");
            passwordField.setInputType(android.text.InputType.TYPE_CLASS_TEXT |
                    android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD);
            int pad = dp(20);
            passwordField.setPadding(pad, dp(10), pad, dp(10));

            new MaterialAlertDialogBuilder(this)
                    .setTitle("Set password")
                    .setMessage("Use at least 8 characters. This password will work for future sign-ins.")
                    .setView(passwordField)
                    .setNegativeButton("Cancel", null)
                    .setPositiveButton("Save", (dialog, which) -> {
                        setGlobalStatus("UPDATING • password");
                        runAsync(() -> {
                            api.updatePassword(rawTextOf(passwordField));
                            mainHandler.post(() -> {
                                setGlobalStatus("SECURE • password updated");
                                Snackbar.make(content, "Password updated", Snackbar.LENGTH_LONG).show();
                            });
                        }, true);
                    })
                    .show();
        });

        exportCloudData.setOnClickListener(v -> exportSyncedCloudData());
        deleteCloudData.setOnClickListener(v -> confirmDeleteSyncedCloudData());

        logout.setOnClickListener(v -> {
            clearWorkspaceCache();
            api.logout();
            setGlobalStatus("SIGNED OUT");
            showNativeAccountScreen();
        });
    }

    private void showWorkspaceScreen(String targetPage, String subtitle) {
        workspaceTargetPage = targetPage == null ? "" : targetPage;
        currentScreen = workspaceTargetPage.isBlank() ? "advanced" : "account";
        currentBatch = null;
        setBrandContext("ADVANCED TOOLS");
        disposeWorkspaceWebView();

        View view = LayoutInflater.from(this).inflate(R.layout.screen_workspace, content, false);
        content.removeAllViews();
        content.addView(view);

        workspaceWebView = view.findViewById(R.id.workspaceWebView);
        workspaceLoading = view.findViewById(R.id.workspaceLoading);

        WebSettings settings = workspaceWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setSupportMultipleWindows(false);
        settings.setJavaScriptCanOpenWindowsAutomatically(false);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setUserAgentString(settings.getUserAgentString() + " IGCleanerAndroid/120.35");

        workspaceWebView.setBackgroundColor(getColor(R.color.ig_bg));
        workspaceWebView.addJavascriptInterface(new WorkspaceBridge(), "AndroidBridge");

        workspaceWebView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                filePathCallback = callback;
                try {
                    Intent intent = params.createIntent();
                    startActivityForResult(intent, FILE_CHOOSER_REQUEST);
                    return true;
                } catch (Exception error) {
                    filePathCallback = null;
                    Snackbar.make(content, "No pude abrir el selector de archivos.", Snackbar.LENGTH_LONG).show();
                    return false;
                }
            }
        });

        workspaceWebView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String host = uri.getHost() == null ? "" : uri.getHost().toLowerCase(Locale.ROOT);
                if (host.contains("instagram.com")) {
                    openExternalUri(uri);
                    return true;
                }
                if ("http".equals(uri.getScheme()) || "https".equals(uri.getScheme())) {
                    openExternalUri(uri);
                    return true;
                }
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                workspaceLoading.setVisibility(View.GONE);
                bootstrapWorkspace();
            }
        });

        workspaceWebView.loadUrl("file:///android_asset/ig_cleaner_pro_v120_27_synced_companion.html");
        setGlobalStatus("ADVANCED TOOLS • desktop engine");
    }

    private void bootstrapWorkspace() {
        if (workspaceWebView == null) return;
        try {
            JSONObject cfg = new JSONObject()
                    .put("email", api.getEmail())
                    .put("auto", true);
            JSONObject device = new JSONObject()
                    .put("id", deviceId)
                    .put("type", "android")
                    .put("label", deviceLabel());

            String session = api.hasSession() ? api.webSession().toString() : "null";
            boolean nativeSessionNewer = api.hasSession() && api.nativeSessionIsNewer();
            String sessionBridge = "";
            if (api.hasSession()) {
                String quoted = JSONObject.quote(session);
                sessionBridge = nativeSessionNewer
                        ? "localStorage.setItem('igc_v12027_supabase_session'," + quoted + ");"
                        : "if(!localStorage.getItem('igc_v12027_supabase_session'))localStorage.setItem('igc_v12027_supabase_session'," + quoted + ");";
            }
            String targetPage = workspaceTargetPage == null ? "" : workspaceTargetPage;
            String js = "(function(){"
                    + "try{"
                    + "localStorage.setItem('igc_v12027_supabase_config'," + JSONObject.quote(cfg.toString()) + ");"
                    + sessionBridge
                    + "localStorage.setItem('igc_v12026_device_identity'," + JSONObject.quote(device.toString()) + ");"
                    + "if(!sessionStorage.getItem('igc_android_bootstrapped')){sessionStorage.setItem('igc_android_bootstrapped','1');location.reload();return;}"
                    + "var ws=localStorage.getItem('igc_v12027_supabase_session');if(ws){try{AndroidBridge.syncSession(ws);}catch(_){}}"
                    + "document.documentElement.classList.add('igc-android-host');"
                    + "if(!document.getElementById('igcAndroidHostStyle')){var s=document.createElement('style');s.id='igcAndroidHostStyle';"
                    + "s.textContent='.igc-commandbar{position:sticky;top:0}.igc-stage{min-width:0}.igc-workspace{padding-bottom:24px}.igc-rail{max-height:100vh}.igc-engine-badge:after{content:\" · Android\";}';document.head.appendChild(s);}"
                    + (!targetPage.isBlank()
                        ? "if(typeof window.showPage==='function')window.showPage(" + JSONObject.quote(targetPage) + ");"
                        : "")
                    + "var go=function(){AndroidBridge.openNativeFocus();};"
                    + "['focusMode20','focusMode30','focusMode40'].forEach(function(n){if(typeof window[n]==='function')window[n]=go;});"
                    + "if(typeof window.followersMutualFocusN==='function')window.followersMutualFocusN=function(){go();};"
                    + "if(typeof window.followersFocusN==='function')window.followersFocusN=function(){go();};"
                    + "if(typeof window.pendingFocusN==='function')window.pendingFocusN=function(){go();};"
                    + "if(typeof window.followersFocusRiskN==='function')window.followersFocusRiskN=function(){go();};"
                    + "if(typeof window.pendingFocusRiskN==='function')window.pendingFocusRiskN=function(){go();};"
                    + "var orig=window.open;var last=0;window.open=function(u,t,f){"
                    + "if(/instagram\\.com/i.test(String(u||''))){var now=Date.now();if(now-last<700){AndroidBridge.bulkOpenBlocked();return null;}last=now;AndroidBridge.openInstagramUrl(String(u));return null;}"
                    + "return orig?orig.call(window,u,t,f):null;};"
                    + "}catch(e){console.error('Android bootstrap',e);}"
                    + "})();";
            workspaceWebView.evaluateJavascript(js, null);
        } catch (Exception error) {
            setGlobalStatus("Workspace: error de sesión");
        }
    }

    private void disposeWorkspaceWebView() {
        if (workspaceWebView == null) return;
        try {
            workspaceWebView.stopLoading();
            workspaceWebView.onPause();
            workspaceWebView.removeJavascriptInterface("AndroidBridge");
            workspaceWebView.destroy();
        } catch (Exception ignored) {}
        workspaceWebView = null;
        workspaceLoading = null;
    }

    private void openExternalUri(Uri uri) {
        try {
            Intent intent = new Intent(Intent.ACTION_VIEW, uri);
            startActivity(intent);
        } catch (Exception error) {
            Snackbar.make(content, "No se pudo abrir el enlace.", Snackbar.LENGTH_LONG).show();
        }
    }

    private String saveBytesToDownloads(String fileName, String mimeType, byte[] bytes) throws Exception {
        String safeName = (fileName == null || fileName.isBlank())
                ? "ig_cleaner_export_" + System.currentTimeMillis()
                : fileName.replaceAll("[\\\\/:*?\"<>|]", "_");

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, safeName);
            values.put(MediaStore.Downloads.MIME_TYPE,
                    mimeType == null || mimeType.isBlank() ? "application/octet-stream" : mimeType);
            values.put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/IG Cleaner");
            Uri outUri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (outUri == null) throw new IllegalStateException("No se pudo crear la descarga.");
            try (OutputStream stream = getContentResolver().openOutputStream(outUri)) {
                if (stream == null) throw new IllegalStateException("No se pudo abrir la descarga.");
                stream.write(bytes);
            }
            return "Descargas/IG Cleaner/" + safeName;
        }

        File dir = new File(getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS), "IG Cleaner");
        if (!dir.exists() && !dir.mkdirs()) throw new IllegalStateException("No se pudo crear la carpeta.");
        File out = new File(dir, safeName);
        try (FileOutputStream stream = new FileOutputStream(out)) {
            stream.write(bytes);
        }
        return out.getAbsolutePath();
    }

    private void saveWorkspaceExport(String fileName, String mimeType, String dataUrl) {
        runAsync(() -> {
            int comma = dataUrl.indexOf(',');
            String payload = comma >= 0 ? dataUrl.substring(comma + 1) : dataUrl;
            byte[] bytes = android.util.Base64.decode(payload, android.util.Base64.DEFAULT);
            String savedLabel = saveBytesToDownloads(
                    fileName == null || fileName.isBlank()
                            ? "ig_cleaner_export_" + System.currentTimeMillis() + ".html"
                            : fileName,
                    mimeType == null || mimeType.isBlank() ? "text/html" : mimeType,
                    bytes);

            mainHandler.post(() -> Snackbar.make(content,
                    "Exportado: " + savedLabel, Snackbar.LENGTH_LONG).show());
        }, true);
    }

    private JSONArray fetchAllCloudRows(String table) throws Exception {
        JSONArray all = new JSONArray();
        int offset = 0;
        while (true) {
            JSONArray page = api.get(table + "?select=*&limit=1000&offset=" + offset);
            for (int i = 0; i < page.length(); i++) all.put(page.get(i));
            if (page.length() < 1000) break;
            offset += page.length();
        }
        return all;
    }

    private void exportSyncedCloudData() {
        if (!api.hasSession()) {
            Snackbar.make(content, "Sign in first.", Snackbar.LENGTH_LONG).show();
            return;
        }
        setGlobalStatus("EXPORTING • synchronized cloud data");
        runAsync(() -> {
            JSONObject root = new JSONObject()
                    .put("schema", "ig-cleaner-cloud-export-v1")
                    .put("exportedAt", Instant.now().toString())
                    .put("account", api.getEmail())
                    .put("device", new JSONObject()
                            .put("id", deviceId)
                            .put("type", "android")
                            .put("label", deviceLabel()))
                    .put("note", "Contains only synchronized IG Cleaner Pro data. It does not contain the original Instagram export.");

            JSONObject tables = new JSONObject();
            JSONObject counts = new JSONObject();
            int total = 0;
            for (String table : SYNC_TABLES) {
                JSONArray rows = fetchAllCloudRows(table);
                tables.put(table, rows);
                counts.put(table, rows.length());
                total += rows.length();
            }
            root.put("counts", counts);
            root.put("tables", tables);

            String fileName = "IG-Cleaner-Pro-cloud-export-" + System.currentTimeMillis() + ".json";
            String savedLabel = saveBytesToDownloads(
                    fileName,
                    "application/json",
                    root.toString(2).getBytes(StandardCharsets.UTF_8));
            int finalTotal = total;
            mainHandler.post(() -> {
                setGlobalStatus("EXPORTED • " + finalTotal + " synchronized rows");
                Snackbar.make(content, "Cloud export: " + savedLabel, Snackbar.LENGTH_LONG).show();
            });
        }, true);
    }

    private void confirmDeleteSyncedCloudData() {
        if (!api.hasSession()) {
            Snackbar.make(content, "Sign in first.", Snackbar.LENGTH_LONG).show();
            return;
        }

        new MaterialAlertDialogBuilder(this)
                .setTitle("Delete synchronized cloud data?")
                .setMessage("This deletes the cloud copy for this IG Cleaner account. Your original Instagram export and independent local backups are not deleted.")
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Continue", (firstDialog, firstWhich) ->
                        new MaterialAlertDialogBuilder(this)
                                .setTitle("Final confirmation")
                                .setMessage("Delete all synchronized lists, review state, Focus batches, audit events and device rows? The app will sign out afterward so auto-sync cannot immediately upload them again.")
                                .setNegativeButton("Cancel", null)
                                .setPositiveButton("Delete cloud", (secondDialog, secondWhich) ->
                                        deleteSyncedCloudData())
                                .show())
                .show();
    }

    private void deleteSyncedCloudData() {
        setGlobalStatus("DELETING • synchronized cloud data");
        runAsync(() -> {
            String[] deleteOrder = new String[]{
                    "focus_batch_items",
                    "focus_batches",
                    "profile_state",
                    "audit_events",
                    "list_snapshots",
                    "workspace_state",
                    "devices"
            };
            for (String table : deleteOrder) {
                api.delete(table + "?user_id=not.is.null");
            }

            clearWorkspaceCache();
            syncedFollowing = new JSONArray();
            syncedFollowers = new JSONArray();
            syncedPending = new JSONArray();
            syncedWorkspaceState = new JSONObject();
            syncedReviewStateAvailable = false;
            api.logout();

            mainHandler.post(() -> {
                setGlobalStatus("CLOUD DATA DELETED • signed out");
                showNativeAccountScreen();
                Snackbar.make(content,
                        "Synchronized cloud data deleted. Local independent backups were not removed.",
                        Snackbar.LENGTH_LONG).show();
            });
        }, true);
    }

    private final class WorkspaceBridge {
        @JavascriptInterface
        public void syncSession(String sessionJson) {
            api.adoptWebSession(sessionJson);
            mainHandler.post(() -> {
                if (api.hasSession()) {
                    setGlobalStatus("Cuenta conectada · sesión compartida");
                } else {
                    setGlobalStatus("Sesión cerrada");
                }
            });
        }

        @JavascriptInterface
        public void openNativeFocus() {
            mainHandler.post(() -> bottomNav.setSelectedItemId(R.id.navFocus));
        }

        @JavascriptInterface
        public void openInstagramUrl(String url) {
            mainHandler.post(() -> {
                try {
                    Uri uri = Uri.parse(url);
                    String username = uri.getPathSegments().isEmpty() ? "" : uri.getPathSegments().get(0);
                    if (!username.isBlank()) openInstagram(username);
                    else openExternalUri(uri);
                } catch (Exception ignored) {}
            });
        }

        @JavascriptInterface
        public void bulkOpenBlocked() {
            mainHandler.post(() -> Toast.makeText(MainActivity.this,
                    "En Android usa Focus: un perfil por vez.", Toast.LENGTH_SHORT).show());
        }

        @JavascriptInterface
        public void saveBase64(String fileName, String mimeType, String dataUrl) {
            saveWorkspaceExport(fileName, mimeType, dataUrl);
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_CHOOSER_REQUEST) {
            if (filePathCallback != null) {
                Uri[] result = resultCode == RESULT_OK
                        ? WebChromeClient.FileChooserParams.parseResult(resultCode, data)
                        : null;
                filePathCallback.onReceiveValue(result);
                filePathCallback = null;
            }
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    private void showFocusScreen() {
        disposeWorkspaceWebView();
        currentScreen = "focus";
        setBrandContext("FOCUS");
        currentBatch = null;
        clearFocusState();

        focusView = LayoutInflater.from(this).inflate(R.layout.screen_focus, content, false);
        content.removeAllViews();
        content.addView(focusView);

        focusTitle = focusView.findViewById(R.id.focusTitle);
        focusSubtitle = focusView.findViewById(R.id.focusSubtitle);
        focusProgress = focusView.findViewById(R.id.focusProgress);
        focusProgressLabel = focusView.findViewById(R.id.focusProgressLabel);
        batchScroll = focusView.findViewById(R.id.batchScroll);
        batchContainer = focusView.findViewById(R.id.batchContainer);
        profileList = focusView.findViewById(R.id.profileList);
        focusActions = focusView.findViewById(R.id.focusActions);
        nextPending = focusView.findViewById(R.id.nextPending);
        finishBatch = focusView.findViewById(R.id.finishBatch);
        refreshFocus = focusView.findViewById(R.id.refreshFocus);

        focusAdapter = new ProfileAdapter(this::openFocusProfile);
        profileList.setLayoutManager(new LinearLayoutManager(this));
        profileList.setAdapter(focusAdapter);

        nextPending.setOnClickListener(v -> openNextPending());
        finishBatch.setOnClickListener(v -> confirmFinishBatch());
        refreshFocus.setOnClickListener(v -> {
            if (currentBatch == null) loadBatches();
            else loadBatch(currentBatch);
        });

        if (!api.hasSession()) {
            focusSubtitle.setText("Sign in from Profile to receive Focus batches prepared on Desktop.");
            addEmptyCard(batchContainer, "Account required",
                    "Use your email and password. Verification code is only needed for first-time setup or recovery.");
            MaterialButton account = new MaterialButton(this);
            account.setText("Go to Profile");
            account.setOnClickListener(v -> bottomNav.setSelectedItemId(R.id.navProfile));
            batchContainer.addView(account);
            return;
        }

        focusSubtitle.setText("Abre un perfil a la vez. El checklist registra apertura; tú confirmas la revisión al final.");
        loadBatches();
    }

    private void clearFocusState() {
        currentItems = new JSONArray();
        itemByUsername.clear();
        opened.clear();
        remotelyReviewed.clear();
        reviewedDevice.clear();
    }

    private void loadBatches() {
        setGlobalStatus("Buscando Focus…");
        runAsync(() -> {
            touchDevice();
            JSONArray batches = api.get("focus_batches?select=*&status=in.(prepared,active)&order=created_at.desc&limit=30");
            mainHandler.post(() -> {
                if (!"focus".equals(currentScreen) || focusView == null) return;
                renderBatches(batches);
                setGlobalStatus("Focus actualizado · " + batches.length() + " tanda(s)");
            });
        }, true);
    }

    private void renderBatches(JSONArray batches) {
        currentBatch = null;
        clearFocusState();
        focusTitle.setText("Focus");
        focusSubtitle.setText("Crea una tanda aquí o continúa una preparada en cualquier dispositivo.");
        focusProgress.setVisibility(View.GONE);
        focusProgressLabel.setVisibility(View.GONE);
        profileList.setVisibility(View.GONE);
        focusActions.setVisibility(View.GONE);
        batchScroll.setVisibility(View.VISIBLE);
        batchContainer.removeAllViews();

        batchContainer.addView(createFocusBuilderCard());

        if (batches.length() == 0) {
            addEmptyCard(batchContainer, "No hay tandas activas",
                    "Puedes crear Foco 20/30/40 directamente en Android. Se guardará en tu cuenta y Desktop podrá verla.");
            return;
        }

        for (int i = 0; i < batches.length(); i++) {
            JSONObject batch = batches.optJSONObject(i);
            if (batch != null) batchContainer.addView(createBatchCard(batch));
        }
    }

    private View createFocusBuilderCard() {
        MaterialCardView card = new MaterialCardView(this);
        card.setCardBackgroundColor(getColor(R.color.ig_surface_2));
        card.setStrokeColor(getColor(R.color.ig_border_strong));
        card.setStrokeWidth(dp(1));
        card.setRadius(dp(20));

        LinearLayout inner = new LinearLayout(this);
        inner.setOrientation(LinearLayout.VERTICAL);
        inner.setPadding(dp(16), dp(16), dp(16), dp(16));

        TextView eyebrow = text("CREATE ON ANDROID", 10, R.color.ig_cyan, true);
        TextView title = text("New Focus", 20, R.color.ig_text, true);
        TextView body = text("Choose Review, Mutuals, Followers or Requests, then create a frozen Focus 20/30/40 from the same synced state used by Desktop.",
                12, R.color.ig_muted, false);

        MaterialButton create = new MaterialButton(this);
        create.setText("Create Focus");
        create.setAllCaps(false);
        create.setCornerRadius(dp(14));
        LinearLayout.LayoutParams buttonLp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(50));
        buttonLp.setMargins(0, dp(12), 0, 0);
        create.setLayoutParams(buttonLp);
        create.setOnClickListener(v -> showCreateFocusDialog());

        inner.addView(eyebrow);
        inner.addView(title);
        inner.addView(body);
        inner.addView(create);
        card.addView(inner);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, dp(14));
        card.setLayoutParams(lp);
        return card;
    }

    private void showCreateFocusDialog() {
        if (!api.hasSession()) {
            bottomNav.setSelectedItemId(R.id.navProfile);
            return;
        }

        String[] labels = {
                "Review · no te siguen",
                "Mutuals · se siguen mutuamente",
                "Followers · tú no los sigues",
                "Requests · solicitudes pendientes"
        };
        String[] modules = {"main", "mutual", "followers", "pending"};
        final int[] selected = {0};

        new MaterialAlertDialogBuilder(this)
                .setTitle("Create Focus")
                .setSingleChoiceItems(labels, 0, (dialog, which) -> selected[0] = which)
                .setNegativeButton("Cancel", null)
                .setPositiveButton("Next", (dialog, which) ->
                        showFocusSizeDialog(modules[selected[0]]))
                .show();
    }

    private void showFocusSizeDialog(String module) {
        String[] sizes = {"Focus 20", "Focus 30", "Focus 40"};
        int[] values = {20, 30, 40};
        new MaterialAlertDialogBuilder(this)
                .setTitle(focusModuleLabel(module))
                .setItems(sizes, (dialog, which) -> createFocusBatch(module, values[which]))
                .setNegativeButton("Cancel", null)
                .show();
    }

    private void createFocusBatch(String module, int requestedSize) {
        setGlobalStatus("PREPARING • " + focusModuleLabel(module) + " " + requestedSize);
        runAsync(() -> {
            touchDevice();
            refreshFocusSourceData();

            if (!syncedReviewStateAvailable) {
                throw new IllegalStateException("Review history has not finished syncing. Sync Desktop once, then Android can create Focus independently.");
            }

            Set<String> alreadyInFocus = activeFocusUsernames();
            List<JSONObject> candidates = buildNativeFocusCandidates(module, alreadyInFocus);
            if (candidates.isEmpty()) {
                throw new IllegalStateException("No eligible profiles are available for " + focusModuleLabel(module) + ".");
            }

            int count = Math.min(requestedSize, candidates.size());
            List<JSONObject> selected = new ArrayList<>(candidates.subList(0, count));
            String batchId = "focus_android_" + System.currentTimeMillis() + "_" +
                    UUID.randomUUID().toString().replace("-", "").substring(0, 8);
            String now = Instant.now().toString();
            String label = "Android · " + focusModuleLabel(module) + " · Focus " + requestedSize;

            JSONObject batch = new JSONObject()
                    .put("id", batchId)
                    .put("module", module)
                    .put("label", label)
                    .put("target_size", count)
                    .put("status", "prepared")
                    .put("created_device", "android")
                    .put("created_at", now)
                    .put("source_signature", "android-v120.35:" + module + ":" + requestedSize)
                    .put("updated_at", now);
            api.upsert("focus_batches", "user_id,id", new JSONArray().put(batch));

            JSONArray items = new JSONArray();
            for (int i = 0; i < selected.size(); i++) {
                JSONObject candidate = selected.get(i);
                items.put(new JSONObject()
                        .put("batch_id", batchId)
                        .put("position", i + 1)
                        .put("username", candidate.optString("username"))
                        .put("status", "pending")
                        .put("context", candidate.optJSONObject("context") == null
                                ? new JSONObject()
                                : candidate.optJSONObject("context"))
                        .put("updated_at", now));
            }
            api.upsert("focus_batch_items", "user_id,batch_id,username", items);

            insertEvent("", "batch_created", module, batchId, label, count, "",
                    new JSONObject()
                            .put("requested_size", requestedSize)
                            .put("created_device", "android")
                            .put("usernames", usernames(items)));

            mainHandler.post(() -> {
                if (!"focus".equals(currentScreen)) return;
                Snackbar.make(content,
                        count == requestedSize
                                ? "Focus " + requestedSize + " creado en Android"
                                : "Solo había " + count + " perfiles elegibles; se creó la tanda con esos perfiles",
                        Snackbar.LENGTH_LONG).show();
                loadBatch(batch);
            });
        }, true);
    }

    private void refreshFocusSourceData() throws Exception {
        JSONArray snapshots = api.get("list_snapshots?select=list_name,payload,item_count,updated_at");
        JSONArray stateRows = api.get("workspace_state?select=payload,updated_at&state_key=eq.primary&limit=1");
        JSONArray profileStates = api.get("profile_state?select=username,module,reviewed_at,reviewed_device,decision,protected,context&order=reviewed_at.desc&limit=20000");

        JSONObject stateRow = stateRows.length() > 0 ? stateRows.optJSONObject(0) : null;
        JSONObject state = stateRow == null ? null : stateRow.optJSONObject("payload");
        if (state == null) state = new JSONObject();
        long snapshotUpdatedAt = stateRow == null
                ? 0L
                : parseInstant(stateRow.optString("updated_at", "")).toEpochMilli();
        state.put("_snapshotUpdatedAt", snapshotUpdatedAt);
        syncedReviewStateAvailable = stateRow != null || profileStates.length() > 0;
        mergeRemoteProfileState(state, profileStates);

        JSONArray following = new JSONArray();
        JSONArray followers = new JSONArray();
        JSONArray pending = new JSONArray();
        for (int i = 0; i < snapshots.length(); i++) {
            JSONObject snap = snapshots.optJSONObject(i);
            if (snap == null) continue;
            JSONArray payload = snap.optJSONArray("payload");
            if (payload == null) payload = new JSONArray();
            switch (snap.optString("list_name")) {
                case "following" -> following = payload;
                case "followers" -> followers = payload;
                case "pending" -> pending = payload;
            }
        }

        syncedFollowing = following;
        syncedFollowers = followers;
        syncedPending = pending;
        syncedWorkspaceState = state;
        saveWorkspaceCache();
    }

    private Set<String> activeFocusUsernames() throws Exception {
        Set<String> usernames = new HashSet<>();
        JSONArray batches = api.get("focus_batches?select=id&status=in.(prepared,active)&limit=50");
        for (int i = 0; i < batches.length(); i++) {
            JSONObject batch = batches.optJSONObject(i);
            if (batch == null) continue;
            String id = batch.optString("id", "");
            if (id.isBlank()) continue;
            JSONArray items = api.get("focus_batch_items?select=username,status&batch_id=eq." +
                    encode(id) + "&status=in.(pending,opened)");
            for (int j = 0; j < items.length(); j++) {
                String username = items.optJSONObject(j) == null
                        ? ""
                        : items.optJSONObject(j).optString("username", "").toLowerCase(Locale.ROOT);
                if (!username.isBlank()) usernames.add(username);
            }
        }
        return usernames;
    }

    private List<JSONObject> buildNativeFocusCandidates(String module, Set<String> excluded) throws Exception {
        Map<String, JSONObject> following = jsonArrayByUsername(syncedFollowing);
        Map<String, JSONObject> followers = jsonArrayByUsername(syncedFollowers);
        Set<String> done = jsonStringSet(syncedWorkspaceState.optJSONArray("done"));
        Set<String> protectedUsers = jsonStringSet(syncedWorkspaceState.optJSONArray("protected"));
        JSONObject snooze = syncedWorkspaceState.optJSONObject("snooze");
        JSONObject reviewedMeta = syncedWorkspaceState.optJSONObject("reviewedMeta");
        JSONObject pendingReviewed = syncedWorkspaceState.optJSONObject("pendingReviewedMeta");
        JSONObject pendingSnooze = syncedWorkspaceState.optJSONObject("pendingSnooze");

        List<JSONObject> out = new ArrayList<>();
        long now = System.currentTimeMillis();

        if ("main".equals(module)) {
            for (Map.Entry<String, JSONObject> entry : following.entrySet()) {
                String username = entry.getKey();
                JSONObject source = entry.getValue();
                if (followers.containsKey(username) || excluded.contains(username)) continue;
                if (isNativeFollowingResolved(username, source, done, protectedUsers, snooze, reviewedMeta)) continue;
                out.add(nativeFocusCandidate(username, source, module,
                        "Doesn't follow you back", false, true));
            }
        } else if ("mutual".equals(module)) {
            for (Map.Entry<String, JSONObject> entry : followers.entrySet()) {
                String username = entry.getKey();
                if (!following.containsKey(username) || excluded.contains(username)) continue;
                JSONObject source = entry.getValue();
                if (isNativeReviewedForMode(username, source, "followers",
                        done, protectedUsers, snooze, reviewedMeta)) continue;
                out.add(nativeFocusCandidate(username, source, module,
                        "You follow each other", true, true));
            }
        } else if ("followers".equals(module)) {
            for (Map.Entry<String, JSONObject> entry : followers.entrySet()) {
                String username = entry.getKey();
                if (following.containsKey(username) || excluded.contains(username)) continue;
                JSONObject source = entry.getValue();
                if (isNativeReviewedForMode(username, source, "followers",
                        done, protectedUsers, snooze, reviewedMeta)) continue;
                out.add(nativeFocusCandidate(username, source, module,
                        "Follower you don't follow back", true, false));
            }
        } else if ("pending".equals(module)) {
            for (int i = 0; i < syncedPending.length(); i++) {
                JSONObject source = syncedPending.optJSONObject(i);
                if (source == null) continue;
                String username = source.optString("username", "").toLowerCase(Locale.ROOT);
                if (username.isBlank() || excluded.contains(username)) continue;
                JSONObject meta = pendingReviewed == null ? null : pendingReviewed.optJSONObject(username);
                long snoozeUntil = pendingSnooze == null ? 0L : pendingSnooze.optLong(username, 0L);
                boolean reviewed = meta != null && meta.optLong("reviewedAt", 0L) > 0L;
                if (reviewed || snoozeUntil > now) continue;
                out.add(nativeFocusCandidate(username, source, module,
                        "Pending follow request", false, true));
            }
        }

        out.sort((a, b) -> compareFocusTimestamp(
                a.optJSONObject("source"),
                b.optJSONObject("source"),
                a.optString("username"),
                b.optString("username")));
        return out;
    }

    private JSONObject nativeFocusCandidate(String username, JSONObject source, String module,
                                            String contextText, boolean isFollower, boolean iFollow) throws Exception {
        JSONObject row = new JSONObject()
                .put("relation", contextText)
                .put("relationGood", "mutual".equals(module))
                .put("followsBack", "mutual".equals(module))
                .put("isFollower", isFollower)
                .put("iFollow", iFollow)
                .put("dateMain", source == null ? 0 : source.optLong("timestamp", 0));

        JSONObject context = new JSONObject()
                .put("context", contextText)
                .put("source", "android")
                .put("row", row);

        return new JSONObject()
                .put("username", username)
                .put("source", source == null ? new JSONObject() : source)
                .put("context", context);
    }

    private int compareFocusTimestamp(JSONObject a, JSONObject b, String usernameA, String usernameB) {
        long ta = a == null ? 0L : a.optLong("timestamp", 0L);
        long tb = b == null ? 0L : b.optLong("timestamp", 0L);
        if (ta > 0 && tb > 0 && ta != tb) return Long.compare(ta, tb);
        if (ta > 0 && tb <= 0) return -1;
        if (ta <= 0 && tb > 0) return 1;
        return usernameA.compareTo(usernameB);
    }

    private boolean isNativeReviewedForMode(String username, JSONObject source, String mode,
                                            Set<String> done, Set<String> protectedUsers,
                                            JSONObject snooze, JSONObject reviewedMeta) {
        if (protectedUsers.contains(username)) return true;
        if (snooze != null && snooze.optLong(username, 0L) > System.currentTimeMillis()) return true;
        if (!done.contains(username) || reviewedMeta == null) return false;

        JSONObject meta = reviewedMeta.optJSONObject(username);
        if (meta == null || !mode.equals(meta.optString("mode", ""))) return false;

        long reviewedAt = meta.optLong("reviewedAt", 0L);
        long sourceAt = source == null ? 0L : source.optLong("timestamp", 0L) * 1000L;
        return reviewedAt > 0L && (sourceAt <= 0L || sourceAt <= reviewedAt);
    }

    private String focusModuleLabel(String module) {
        return switch (module) {
            case "mutual" -> "Mutuals";
            case "followers" -> "Followers";
            case "pending" -> "Requests";
            default -> "Review";
        };
    }

    private View createBatchCard(JSONObject batch) {
        MaterialCardView card = new MaterialCardView(this);
        card.setCardBackgroundColor(getColor(R.color.ig_surface));
        card.setStrokeColor(getColor(R.color.ig_border));
        card.setStrokeWidth(dp(1));
        card.setRadius(dp(20));
        card.setClickable(true);
        card.setFocusable(true);

        LinearLayout inner = new LinearLayout(this);
        inner.setOrientation(LinearLayout.VERTICAL);
        inner.setPadding(dp(16), dp(14), dp(16), dp(14));

        TextView title = text(batch.optString("label", "Focus"),
                18, R.color.ig_text, true);
        int target = batch.optInt("target_size", 0);
        String module = batch.optString("module", "review");
        String status = batch.optString("status", "prepared");
        TextView meta = text(target + " perfiles · " + module + " · " + status,
                12, R.color.ig_muted, false);

        inner.addView(title);
        inner.addView(meta);
        card.addView(inner);

        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, dp(10));
        card.setLayoutParams(lp);
        card.setOnClickListener(v -> loadBatch(batch));
        return card;
    }

    private void loadBatch(JSONObject batch) {
        currentBatch = batch;
        clearFocusState();
        setGlobalStatus("Cargando " + batch.optString("label", "Focus") + "…");

        runAsync(() -> {
            String currentStatus = batch.optString("status", "prepared");
            if ("prepared".equals(currentStatus)) {
                String now = Instant.now().toString();
                api.patch("focus_batches?id=eq." + encode(batch.optString("id")),
                        new JSONObject().put("status", "active").put("updated_at", now));
                batch.put("status", "active");
            }
            String batchId = encode(batch.optString("id"));
            JSONArray items = api.get("focus_batch_items?select=*&batch_id=eq." + batchId + "&order=position.asc");
            currentItems = items;

            for (int i = 0; i < items.length(); i++) {
                JSONObject item = items.optJSONObject(i);
                if (item == null) continue;
                String username = item.optString("username");
                itemByUsername.put(username, item);
                String status = item.optString("status", "pending");
                if (!"pending".equals(status)) opened.add(username);
                if ("reviewed".equals(status)) {
                    remotelyReviewed.add(username);
                    reviewedDevice.put(username, item.optString("reviewed_device", "otro dispositivo"));
                }
            }

            String module = encode(batch.optString("module", "review"));
            JSONArray states = api.get("profile_state?select=username,reviewed_at,reviewed_device&module=eq." +
                    module + "&order=reviewed_at.desc&limit=20000");
            Instant created = parseInstant(batch.optString("created_at"));

            for (int i = 0; i < states.length(); i++) {
                JSONObject state = states.optJSONObject(i);
                if (state == null) continue;
                String username = state.optString("username");
                Instant reviewedAt = parseInstant(state.optString("reviewed_at"));
                if (reviewedAt.compareTo(created) >= 0 && itemByUsername.containsKey(username)) {
                    opened.add(username);
                    remotelyReviewed.add(username);
                    reviewedDevice.put(username, state.optString("reviewed_device", "otro dispositivo"));
                }
            }

            mainHandler.post(() -> {
                if (!"focus".equals(currentScreen) || currentBatch != batch) return;
                renderCurrentBatch();
                setGlobalStatus("Tanda lista · " + opened.size() + "/" + currentItems.length());
            });
        }, true);
    }

    private void renderCurrentBatch() {
        batchScroll.setVisibility(View.GONE);
        profileList.setVisibility(View.VISIBLE);
        focusActions.setVisibility(View.VISIBLE);
        focusProgress.setVisibility(View.VISIBLE);
        focusProgressLabel.setVisibility(View.VISIBLE);

        String label = currentBatch == null ? "Focus" : currentBatch.optString("label", "Focus");
        focusTitle.setText(label);
        focusSubtitle.setText("Toca un perfil → se abre Instagram → vuelve aquí y continúa.");

        List<ProfileAdapter.ProfileRow> rows = new ArrayList<>();
        for (int i = 0; i < currentItems.length(); i++) {
            JSONObject item = currentItems.optJSONObject(i);
            if (item == null) continue;
            String username = item.optString("username");
            boolean checked = opened.contains(username);
            JSONObject cx = item.optJSONObject("context");
            String detail = contextText(cx);
            String badge;
            if (remotelyReviewed.contains(username)) {
                badge = "REVISADO " + cap(reviewedDevice.get(username));
            } else if (checked) {
                badge = "ABIERTO";
            } else {
                badge = "PENDIENTE";
            }
            rows.add(new ProfileAdapter.ProfileRow(username, detail, checked, badge, item));
        }
        focusAdapter.submit(rows);
        updateFocusProgress();
    }

    private void updateFocusProgress() {
        int total = currentItems.length();
        int done = opened.size();
        focusProgress.setMax(Math.max(total, 1));
        focusProgress.setProgressCompat(done, true);
        focusProgressLabel.setText(done + " / " + total + " perfiles abiertos");
        finishBatch.setEnabled(total > 0 && done >= total);
        finishBatch.setText(done >= total ? "Finalizar revisión" : "Faltan " + Math.max(0, total - done));
    }

    private void openNextPending() {
        for (ProfileAdapter.ProfileRow row : focusAdapter.rows()) {
            if (!row.checked) {
                openFocusProfile(row);
                return;
            }
        }
        Toast.makeText(this, "Ya abriste todos los perfiles de esta tanda.", Toast.LENGTH_SHORT).show();
    }

    private void openFocusProfile(ProfileAdapter.ProfileRow row) {
        boolean wasChecked = row.checked;
        row.checked = true;
        opened.add(row.username);
        focusAdapter.notifyDataSetChanged();
        updateFocusProgress();
        openInstagram(row.username);

        JSONObject item = row.payload instanceof JSONObject ? (JSONObject) row.payload : itemByUsername.get(row.username);
        boolean preserveReviewed = remotelyReviewed.contains(row.username);

        runAsync(() -> {
            String now = Instant.now().toString();
            String batchId = encode(currentBatch.optString("id"));
            String username = encode(row.username);

            JSONObject patch = new JSONObject()
                    .put("opened_at", now)
                    .put("opened_device", "android")
                    .put("updated_at", now);
            if (!preserveReviewed) patch.put("status", "opened");

            api.patch("focus_batch_items?batch_id=eq." + batchId + "&username=eq." + username, patch);
            insertEvent(row.username,
                    wasChecked ? "reopened" : "opened",
                    currentBatch.optString("module", "review"),
                    currentBatch.optString("id"),
                    currentBatch.optString("label", "Focus"),
                    currentItems.length(),
                    "",
                    new JSONObject().put("via", "android_checklist"));
        }, false);
    }

    private void confirmFinishBatch() {
        if (currentItems.length() == 0 || opened.size() < currentItems.length()) return;
        new MaterialAlertDialogBuilder(this)
                .setTitle("Finalizar revisión")
                .setMessage("¿Confirmas que revisaste los " + currentItems.length() +
                        " perfiles? Abrir un perfil y revisarlo son eventos distintos; esta confirmación marca la tanda como revisada.")
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Sí, revisados", (dialog, which) -> finalizeBatch())
                .show();
    }

    private void finalizeBatch() {
        setGlobalStatus("Guardando revisión…");
        runAsync(() -> {
            String now = Instant.now().toString();
            String batchId = currentBatch.optString("id");
            String module = currentBatch.optString("module", "review");
            JSONArray states = new JSONArray();

            for (int i = 0; i < currentItems.length(); i++) {
                JSONObject item = currentItems.optJSONObject(i);
                if (item == null) continue;
                String username = item.optString("username");

                api.patch("focus_batch_items?batch_id=eq." + encode(batchId) +
                                "&username=eq." + encode(username),
                        new JSONObject()
                                .put("status", "reviewed")
                                .put("reviewed_at", now)
                                .put("reviewed_device", "android")
                                .put("updated_at", now));

                JSONObject state = new JSONObject()
                        .put("username", username)
                        .put("module", module)
                        .put("reviewed_at", now)
                        .put("reviewed_device", "android")
                        .put("reviewed_device_id", deviceId)
                        .put("decision", "")
                        .put("protected", false)
                        .put("context", item.optJSONObject("context") == null
                                ? new JSONObject()
                                : item.optJSONObject("context"))
                        .put("updated_at", now);
                states.put(state);

                insertEvent(username, "reviewed", module, batchId,
                        currentBatch.optString("label", "Focus"),
                        currentItems.length(), "",
                        new JSONObject().put("via", "android_batch_finalize"));
            }

            api.upsert("profile_state", "user_id,username,module", states);
            api.patch("focus_batches?id=eq." + encode(batchId),
                    new JSONObject()
                            .put("status", "completed")
                            .put("completed_at", now)
                            .put("updated_at", now));

            insertEvent("", "batch_completed", module, batchId,
                    currentBatch.optString("label", "Focus"),
                    currentItems.length(), "",
                    new JSONObject().put("usernames", usernames(currentItems)));

            mainHandler.post(() -> {
                setGlobalStatus("Tanda completada en Android");
                currentBatch = null;
                showFocusScreen();
                Snackbar.make(content, "Revisión sincronizada con Desktop", Snackbar.LENGTH_LONG).show();
            });
        }, true);
    }

    private void showAuditScreen() {
        disposeWorkspaceWebView();
        currentScreen = "audit";
        setBrandContext("ACTIVITY");
        currentBatch = null;
        auditOpened.clear();
        auditEventByUsername.clear();

        auditView = LayoutInflater.from(this).inflate(R.layout.screen_audit, content, false);
        content.removeAllViews();
        content.addView(auditView);

        auditList = auditView.findViewById(R.id.auditList);
        finishAudit = auditView.findViewById(R.id.finishAudit);
        auditAdapter = new ProfileAdapter(this::openAuditProfile);
        auditList.setLayoutManager(new LinearLayoutManager(this));
        auditList.setAdapter(auditAdapter);

        auditView.findViewById(R.id.auditAndroidReviewed).setOnClickListener(v -> loadAudit("android", "reviewed"));
        auditView.findViewById(R.id.auditDesktopReviewed).setOnClickListener(v -> loadAudit("desktop", "reviewed"));
        auditView.findViewById(R.id.auditAndroidOpened).setOnClickListener(v -> loadAudit("android", "opened"));
        auditView.findViewById(R.id.auditDesktopOpened).setOnClickListener(v -> loadAudit("desktop", "opened"));
        finishAudit.setOnClickListener(v -> finishAuditSession());

        if (!api.hasSession()) {
            addEmptyAudit("Sign in from Profile to load cross-device activity.");
        }
    }

    private void loadAudit(String device, String action) {
        if (!api.hasSession()) {
            bottomNav.setSelectedItemId(R.id.navProfile);
            return;
        }

        setGlobalStatus("LOADING • activity");
        runAsync(() -> {
            JSONArray events = api.get("audit_events?select=*&device_type=eq." + encode(device) +
                    "&action=eq." + encode(action) + "&order=event_at.desc&limit=200");

            LinkedHashMap<String, JSONObject> unique = new LinkedHashMap<>();
            for (int i = 0; i < events.length() && unique.size() < 20; i++) {
                JSONObject event = events.optJSONObject(i);
                if (event == null) continue;
                String username = event.optString("username");
                if (!username.isBlank()) unique.putIfAbsent(username, event);
            }

            List<ProfileAdapter.ProfileRow> rows = new ArrayList<>();
            auditEventByUsername.clear();
            auditOpened.clear();

            for (Map.Entry<String, JSONObject> entry : unique.entrySet()) {
                JSONObject event = entry.getValue();
                auditEventByUsername.put(entry.getKey(), event);
                String detail = prettyEventTime(event.optString("event_at")) +
                        " · " + cap(event.optString("device_type", device));
                rows.add(new ProfileAdapter.ProfileRow(
                        entry.getKey(), detail, false, action.toUpperCase(Locale.ROOT), event));
            }

            mainHandler.post(() -> {
                if (!"audit".equals(currentScreen)) return;
                auditAdapter.submit(rows);
                finishAudit.setVisibility(rows.isEmpty() ? View.GONE : View.VISIBLE);
                TextView subtitle = auditView.findViewById(R.id.auditSubtitle);
                subtitle.setText(rows.isEmpty()
                        ? "No hay perfiles para este filtro todavía."
                        : rows.size() + " perfiles · toca uno para abrirlo y auditarlo.");
                setGlobalStatus("ACTIVITY READY • " + rows.size() + " profiles");
            });
        }, true);
    }

    private void addEmptyAudit(String message) {
        TextView subtitle = auditView.findViewById(R.id.auditSubtitle);
        subtitle.setText(message);
        finishAudit.setVisibility(View.GONE);
        auditAdapter.submit(new ArrayList<>());
    }

    private void openAuditProfile(ProfileAdapter.ProfileRow row) {
        row.checked = true;
        auditOpened.add(row.username);
        auditAdapter.notifyDataSetChanged();
        openInstagram(row.username);

        JSONObject origin = row.payload instanceof JSONObject
                ? (JSONObject) row.payload
                : auditEventByUsername.get(row.username);

        runAsync(() -> insertEvent(row.username, "audit_opened", "audit",
                origin == null ? "" : origin.optString("batch_id"),
                "Audit Android", auditAdapter.getItemCount(), "",
                new JSONObject()
                        .put("originDevice", origin == null ? "" : origin.optString("device_type"))
                        .put("originEventId", origin == null ? "" : origin.optString("id"))), false);
    }

    private void finishAuditSession() {
        if (auditOpened.isEmpty()) {
            Toast.makeText(this, "Abre al menos un perfil antes de cerrar la auditoría.", Toast.LENGTH_SHORT).show();
            return;
        }

        setGlobalStatus("Guardando auditoría…");
        runAsync(() -> {
            for (String username : auditOpened) {
                JSONObject origin = auditEventByUsername.get(username);
                insertEvent(username, "audited", "audit",
                        origin == null ? "" : origin.optString("batch_id"),
                        "Audit Android", auditOpened.size(), "",
                        new JSONObject()
                                .put("originDevice", origin == null ? "" : origin.optString("device_type"))
                                .put("originEventId", origin == null ? "" : origin.optString("id")));
            }
            int count = auditOpened.size();
            mainHandler.post(() -> {
                setGlobalStatus("Auditoría registrada · " + count + " perfil(es)");
                Snackbar.make(content, "Auditoría guardada sin cambiar la revisión original", Snackbar.LENGTH_LONG).show();
            });
        }, true);
    }

    private void syncNow() {
        if (("advanced".equals(currentScreen) || "account".equals(currentScreen))
                && workspaceWebView != null) {
            setGlobalStatus("Sincronizando Workspace…");
            workspaceWebView.evaluateJavascript(
                    "(function(){if(typeof window.igcSyncNow==='function'){window.igcSyncNow();return 'ok';}return 'missing';})()",
                    null);
            return;
        }

        if (!api.hasSession()) {
            bottomNav.setSelectedItemId(R.id.navProfile);
            Snackbar.make(content, "Inicia sesión para sincronizar", Snackbar.LENGTH_LONG).show();
            return;
        }

        if ("workspace".equals(currentScreen)) {
            loadMobileWorkspace();
            return;
        }

        setGlobalStatus("Sincronizando…");
        runAsync(() -> {
            touchDevice();
            mainHandler.post(() -> {
                setGlobalStatus("Sincronizado · " + DateFormat.getTimeFormat(this).format(new Date()));
                if ("focus".equals(currentScreen) && currentBatch == null) loadBatches();
            });
        }, true);
    }

    // Keep the active native About window addressable for real-view geometry QA.
    // Clear it on dismiss to avoid retaining a closed dialog.
    androidx.appcompat.app.AlertDialog activeAboutDialog;

    private void showAbout() {
        View about = LayoutInflater.from(this).inflate(R.layout.dialog_about, null, false);
        // Brand logos stay side by side at every supported width; the large
        // developer portrait and five links share the body without nested cards.
        // No fold-hiding or 0dp weighted column changes on compact devices.
        TextView aboutVersion = about.findViewById(R.id.aboutVersion);
        try {
            String installedVersion = getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            aboutVersion.setText("v" + installedVersion + " · SORT • DECLUTTER • FOCUS");
        } catch (android.content.pm.PackageManager.NameNotFoundException error) {
            aboutVersion.setText("SORT • DECLUTTER • FOCUS");
        }
        bindAboutLink(about, R.id.aboutInstagram, "https://www.instagram.com/realmichelduarte/");
        bindAboutLink(about, R.id.aboutFacebook, "https://www.facebook.com/realmichelduarte");
        bindAboutLink(about, R.id.aboutLinkedin, "https://www.linkedin.com/in/realmichelduart/");
        bindAboutLink(about, R.id.aboutGithub, "https://github.com/realmichelduarte");
        bindAboutLink(about, R.id.aboutEmail, "mailto:realmichelduarte@gmail.com");
        activeAboutDialog = new MaterialAlertDialogBuilder(this)
                .setView(about)
                .setPositiveButton("Close", null)
                .show();
        androidx.appcompat.app.AlertDialog aboutDialog = activeAboutDialog;
        aboutDialog.setOnDismissListener(d -> activeAboutDialog = null);
        // Keep the action footer inside the same navy gradient as the
        // product/author content instead of Material's disconnected grey bar.
        if (aboutDialog.getWindow() != null) {
            aboutDialog.getWindow().setBackgroundDrawableResource(R.drawable.bg_about_canvas);
        }
        android.widget.Button closeButton =
                aboutDialog.getButton(android.content.DialogInterface.BUTTON_POSITIVE);
        if (closeButton != null) {
            closeButton.setTextColor(
                    androidx.core.content.ContextCompat.getColor(this, R.color.ig_cyan));
        }
    }

    private void bindAboutLink(View about, int buttonId, String url) {
        View button = about.findViewById(buttonId);
        button.setOnClickListener(v -> {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
            } catch (ActivityNotFoundException error) {
                Toast.makeText(this, "No app available to open link", Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void touchDevice() throws Exception {
        JSONObject device = new JSONObject()
                .put("device_id", deviceId)
                .put("device_type", "android")
                .put("label", deviceLabel())
                .put("last_seen", Instant.now().toString());
        api.upsert("devices", "user_id,device_id", new JSONArray().put(device));
    }

    private void insertEvent(String username, String action, String module,
                             String batchId, String batchLabel, int batchSize,
                             String decision, JSONObject meta) throws Exception {
        JSONObject event = new JSONObject()
                .put("id", "ev_android_" + UUID.randomUUID())
                .put("event_at", Instant.now().toString())
                .put("username", username == null || username.isBlank() ? JSONObject.NULL : username)
                .put("action", action)
                .put("device_id", deviceId)
                .put("device_type", "android")
                .put("device_label", deviceLabel())
                .put("module", module == null || module.isBlank() ? "unknown" : module)
                .put("batch_id", batchId == null || batchId.isBlank() ? JSONObject.NULL : batchId)
                .put("batch_label", batchLabel == null ? "" : batchLabel)
                .put("batch_size", batchSize)
                .put("decision", decision == null ? "" : decision)
                .put("meta", meta == null ? new JSONObject() : meta);

        api.upsert("audit_events", "user_id,id", new JSONArray().put(event));
    }

    private void openInstagram(String username) {
        Uri uri = Uri.parse("https://www.instagram.com/" + username + "/");
        Intent instagram = new Intent(Intent.ACTION_VIEW, uri);
        instagram.setPackage("com.instagram.android");

        try {
            startActivity(instagram);
        } catch (ActivityNotFoundException notInstalled) {
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            } catch (Exception error) {
                Snackbar.make(content, "No se pudo abrir @" + username, Snackbar.LENGTH_LONG).show();
            }
        }
    }

    private String contextText(JSONObject context) {
        if (context == null) return "Toca para abrir en Instagram";
        String[] keys = {"context", "reason", "evidence", "change", "history"};
        List<String> parts = new ArrayList<>();
        for (String key : keys) {
            String value = context.optString(key, "");
            if (!value.isBlank() && !parts.contains(value)) parts.add(value);
            if (parts.size() >= 2) break;
        }
        return parts.isEmpty() ? "Toca para abrir en Instagram" : String.join(" · ", parts);
    }

    private JSONArray usernames(JSONArray items) {
        JSONArray out = new JSONArray();
        for (int i = 0; i < items.length(); i++) {
            JSONObject item = items.optJSONObject(i);
            if (item != null) out.put(item.optString("username"));
        }
        return out;
    }

    private void addEmptyCard(LinearLayout parent, String titleValue, String bodyValue) {
        MaterialCardView card = new MaterialCardView(this);
        card.setCardBackgroundColor(getColor(R.color.ig_surface));
        card.setStrokeColor(getColor(R.color.ig_border));
        card.setStrokeWidth(dp(1));
        card.setRadius(dp(20));

        LinearLayout inner = new LinearLayout(this);
        inner.setOrientation(LinearLayout.VERTICAL);
        inner.setPadding(dp(18), dp(18), dp(18), dp(18));
        inner.addView(text(titleValue, 18, R.color.ig_text, true));
        inner.addView(text(bodyValue, 13, R.color.ig_muted, false));
        card.addView(inner);
        parent.addView(card);
    }

    private TextView text(String value, int sp, int colorRes, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(sp);
        view.setTextColor(getColor(colorRes));
        if (bold) view.setTypeface(view.getTypeface(), android.graphics.Typeface.BOLD);
        view.setPadding(0, dp(3), 0, dp(3));
        return view;
    }

    private void setBrandContext(String value) {
        if (brandContext != null) brandContext.setText((value == null || value.isBlank()) ? "MICHEL'S LAB" : value);
    }

    private void setGlobalStatus(String value) {
        if (globalStatus != null) globalStatus.setText(value == null ? "" : value);
    }

    private String friendlyError(Exception error) {
        String raw = error.getMessage() == null ? error.getClass().getSimpleName() : error.getMessage();
        String lower = raw.toLowerCase(Locale.ROOT);
        if (lower.contains("invalid login credentials") || lower.contains("invalid credentials")) {
            return "Email or password is incorrect.";
        }
        if (lower.contains("token has expired") || lower.contains("jwt expired") || lower.contains("http 401") || lower.contains("http 403")) {
            return "Your session expired. Sign in again from Profile.";
        }
        if (lower.contains("network") || lower.contains("timed out") || lower.contains("timeout") || lower.contains("unable to resolve")) {
            return "Connection problem. Your cached lists are still available.";
        }
        return raw;
    }

    private void runAsync(Task task, boolean reportError) {
        io.submit(() -> {
            try {
                task.run();
            } catch (Exception error) {
                if (reportError) {
                    mainHandler.post(() -> {
                        String message = friendlyError(error);
                        setGlobalStatus("ATTENTION • " + message);
                        Snackbar.make(content, message, Snackbar.LENGTH_LONG).show();
                    });
                }
            }
        });
    }

    private String deviceLabel() {
        String manufacturer = Build.MANUFACTURER == null ? "" : Build.MANUFACTURER.trim();
        String model = Build.MODEL == null ? "Android" : Build.MODEL.trim();
        if (manufacturer.isBlank()) return model;
        if (model.toLowerCase(Locale.ROOT).startsWith(manufacturer.toLowerCase(Locale.ROOT))) return model;
        return manufacturer + " " + model;
    }

    private String cap(String value) {
        if (value == null || value.isBlank()) return "OTRO";
        return value.substring(0, 1).toUpperCase(Locale.ROOT) + value.substring(1);
    }

    private String prettyEventTime(String iso) {
        try {
            Date date = Date.from(Instant.parse(iso));
            return DateFormat.getMediumDateFormat(this).format(date) + " · " +
                    DateFormat.getTimeFormat(this).format(date);
        } catch (Exception ignored) {
            return iso == null ? "" : iso;
        }
    }

    private Instant parseInstant(String value) {
        try {
            return Instant.parse(value);
        } catch (Exception ignored) {
            return Instant.EPOCH;
        }
    }

    private String textOf(TextInputEditText input) {
        return input.getText() == null ? "" : input.getText().toString().trim();
    }

    private String rawTextOf(TextInputEditText input) {
        return input.getText() == null ? "" : input.getText().toString();
    }

    private String encode(String value) {
        return URLEncoder.encode(value == null ? "" : value, StandardCharsets.UTF_8);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private interface Task { void run() throws Exception; }
}
