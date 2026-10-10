package com.michelslab.igcleaner;

import android.content.Context;

import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;

import org.json.JSONArray;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

@RunWith(AndroidJUnit4.class)
public final class FocusInsightsTest {
    private final Context ctx = InstrumentationRegistry.getInstrumentation().getTargetContext();

    @Test
    public void followingAndFollowerDatesHaveCorrectDirectionAndHistory() throws Exception {
        JSONObject item = new JSONObject().put("username", "alpha")
                .put("context", new JSONObject().put("context", "Revisar relación"));
        Map<String, JSONObject> following = new HashMap<>();
        Map<String, JSONObject> followers = new HashMap<>();
        following.put("alpha", new JSONObject().put("timestamp", 1730000000L));
        followers.put("alpha", new JSONObject().put("timestamp", 1731000000L));
        JSONObject state = new JSONObject()
                .put("reviewedMeta", new JSONObject()
                        .put("alpha", new JSONObject()
                                .put("reviewedAt", 1735000000000L)
                                .put("reviewReason", "keep")))
                .put("profileHistory", new JSONObject()
                        .put("alpha", new JSONObject().put("opened", 2)
                                .put("reviewed", 1)));
        String detail = FocusInsights.detail(ctx, item, "main", following, followers,
                new HashMap<>(), state);
        assertTrue(detail.contains("Lo seguiste: "));
        assertTrue(detail.contains("Te siguió: "));
        assertTrue(detail.contains("hace "));
        assertTrue(detail.contains("Tú lo seguiste primero"));
        assertTrue(detail.contains("Última revisión:"));
        assertTrue(detail.contains("Decisión: keep"));
        assertTrue(detail.contains("2 aperturas"));
        assertTrue(detail.contains("Revisar relación"));
    }

    @Test
    public void oldDesktopBatchDatesSurviveNewSnapshotAndUnknownsStayUnknown() throws Exception {
        JSONObject cx = new JSONObject().put("row",
                new JSONObject().put("dateMain", 1731000000L)
                        .put("dateOther", 1730000000L));
        JSONObject old = new JSONObject().put("username", "alpha")
                .put("context", cx);
        String date = FocusInsights.detail(ctx, old, "mutual",
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new JSONObject());
        assertTrue(date.contains("Lo seguiste: "));
        assertTrue(date.contains("Te siguió: "));
        assertTrue(date.contains("Tú lo seguiste primero"));

        JSONObject missing = new JSONObject().put("username", "beta");
        String unknown = FocusInsights.detail(ctx, missing, "main",
                new HashMap<>(), new HashMap<>(), new HashMap<>(), new JSONObject());
        assertTrue(unknown.contains("Lo seguiste: Sin fecha"));
        assertTrue(unknown.contains("Te siguió: Sin fecha"));
        assertTrue(unknown.contains("no verificable"));
        assertFalse(unknown.contains("1970"));
        assertFalse(unknown.contains("Tú lo seguiste primero"));
        Map<String, JSONObject> partialFollowing = new HashMap<>();
        partialFollowing.put("beta", new JSONObject().put("timestamp", 1730000000L));
        JSONObject partialState = new JSONObject().put("followersEvidence",
                new JSONObject().put("partial", true));
        String partial = FocusInsights.detail(ctx, missing, "main", partialFollowing,
                new HashMap<>(), new HashMap<>(), partialState);
        assertTrue("Partial HTML absence is not verified no-follow-back",
                partial.contains("NO VERIFICABLE"));
    }

    @Test
    public void pendingAndLastBatchUseOwnDatesAndSourceDevice() throws Exception {
        Map<String, JSONObject> pending = new HashMap<>();
        pending.put("request", new JSONObject().put("timestamp", 1730000000L));
        String detail = FocusInsights.detail(ctx,
                new JSONObject().put("username", "request"), "pending",
                new HashMap<>(), new HashMap<>(), pending, new JSONObject());
        assertTrue(detail.contains("Solicitud enviada: "));
        assertFalse(detail.contains("Lo seguiste:"));

        JSONObject batch = new JSONObject().put("created_at", "2026-10-07T14:30:00Z")
                .put("completed_at", "2026-10-08T14:30:00Z")
                .put("status", "completed")
                .put("target_size", 30)
                .put("created_device", "desktop");
        String history = FocusInsights.batchHistory(ctx, batch);
        assertTrue(history.contains("Última tanda:"));
        assertTrue(history.contains("30 perfiles"));
        assertTrue(history.contains("Completada"));
        assertTrue(history.contains("desktop"));
        assertTrue(history.contains("Finalizada:"));
    }
}
