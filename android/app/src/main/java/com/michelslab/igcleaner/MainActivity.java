package com.michelslab.igcleaner;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.format.DateFormat;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;
import com.google.android.material.progressindicator.LinearProgressIndicator;
import com.google.android.material.snackbar.Snackbar;
import com.google.android.material.textfield.TextInputEditText;

import org.json.JSONArray;
import org.json.JSONObject;

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
    private String currentScreen = "focus";

    private MaterialToolbar toolbar;
    private BottomNavigationView bottomNav;
    private FrameLayout content;
    private TextView globalStatus;

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

    private final Runnable autoSync = new Runnable() {
        @Override public void run() {
            if (api != null && api.hasSession()) {
                runAsync(() -> {
                    touchDevice();
                    mainHandler.post(() -> setGlobalStatus("Sincronizado · " +
                            DateFormat.getTimeFormat(MainActivity.this).format(new Date())));
                }, false);
            }
            mainHandler.postDelayed(this, 15_000);
        }
    };

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

        toolbar = findViewById(R.id.toolbar);
        bottomNav = findViewById(R.id.bottomNav);
        content = findViewById(R.id.content);
        globalStatus = findViewById(R.id.globalStatus);

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
            if (item.getItemId() == R.id.navFocus) {
                showFocusScreen();
                return true;
            }
            if (item.getItemId() == R.id.navAudit) {
                showAuditScreen();
                return true;
            }
            if (item.getItemId() == R.id.navAccount) {
                showAccountScreen();
                return true;
            }
            return false;
        });

        bottomNav.setSelectedItemId(R.id.navFocus);
        showFocusScreen();
        mainHandler.post(autoSync);
    }

    @Override
    protected void onDestroy() {
        mainHandler.removeCallbacks(autoSync);
        io.shutdownNow();
        super.onDestroy();
    }

    @Override
    public void onBackPressed() {
        if ("focus".equals(currentScreen) && currentBatch != null) {
            currentBatch = null;
            showFocusScreen();
            return;
        }
        super.onBackPressed();
    }

    private void showFocusScreen() {
        currentScreen = "focus";
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
            focusSubtitle.setText("Inicia sesión en Cuenta para recibir los Focus preparados en Desktop.");
            addEmptyCard(batchContainer, "Sin cuenta conectada",
                    "La sincronización usa tu correo y un código. No necesitas configurar Supabase.");
            MaterialButton account = new MaterialButton(this);
            account.setText("Ir a Cuenta");
            account.setOnClickListener(v -> bottomNav.setSelectedItemId(R.id.navAccount));
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
        focusSubtitle.setText("Selecciona una tanda preparada en Desktop o continúa una ya iniciada.");
        focusProgress.setVisibility(View.GONE);
        focusProgressLabel.setVisibility(View.GONE);
        profileList.setVisibility(View.GONE);
        focusActions.setVisibility(View.GONE);
        batchScroll.setVisibility(View.VISIBLE);
        batchContainer.removeAllViews();

        if (batches.length() == 0) {
            addEmptyCard(batchContainer, "No hay Focus preparados",
                    "En Desktop usa “Ver siguiente Foco 20/30/40” y sincroniza. Esa tanda aparecerá aquí.");
            return;
        }

        for (int i = 0; i < batches.length(); i++) {
            JSONObject batch = batches.optJSONObject(i);
            if (batch != null) batchContainer.addView(createBatchCard(batch));
        }
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
        currentScreen = "audit";
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
            addEmptyAudit("Inicia sesión en Cuenta para consultar el historial sincronizado.");
        }
    }

    private void loadAudit(String device, String action) {
        if (!api.hasSession()) {
            bottomNav.setSelectedItemId(R.id.navAccount);
            return;
        }

        setGlobalStatus("Cargando Audit…");
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
                setGlobalStatus("Audit listo · " + rows.size() + " perfil(es)");
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

    private void showAccountScreen() {
        currentScreen = "account";
        currentBatch = null;

        View view = LayoutInflater.from(this).inflate(R.layout.screen_account, content, false);
        content.removeAllViews();
        content.addView(view);

        View authGroup = view.findViewById(R.id.authGroup);
        View connectedCard = view.findViewById(R.id.connectedCard);

        if (api.hasSession()) {
            authGroup.setVisibility(View.GONE);
            connectedCard.setVisibility(View.VISIBLE);

            TextView email = view.findViewById(R.id.accountEmail);
            TextView device = view.findViewById(R.id.deviceLabel);
            email.setText(api.getEmail());
            device.setText(deviceLabel() + " · Android");

            view.findViewById(R.id.syncNow).setOnClickListener(v -> syncNow());
            view.findViewById(R.id.logout).setOnClickListener(v -> {
                api.logout();
                setGlobalStatus("Sesión cerrada");
                showAccountScreen();
            });
        } else {
            connectedCard.setVisibility(View.GONE);
            authGroup.setVisibility(View.VISIBLE);

            TextInputEditText email = view.findViewById(R.id.emailInput);
            TextInputEditText code = view.findViewById(R.id.codeInput);
            email.setText(api.getEmail());

            view.findViewById(R.id.sendCode).setOnClickListener(v -> {
                String value = textOf(email);
                setGlobalStatus("Enviando código…");
                runAsync(() -> {
                    api.sendOtp(value);
                    mainHandler.post(() -> {
                        setGlobalStatus("Código enviado");
                        Snackbar.make(content, "Revisa tu correo y escribe el código", Snackbar.LENGTH_LONG).show();
                    });
                }, true);
            });

            view.findViewById(R.id.verifyCode).setOnClickListener(v -> {
                api.setEmail(textOf(email));
                String otp = textOf(code);
                setGlobalStatus("Verificando…");
                runAsync(() -> {
                    api.verifyOtp(otp);
                    touchDevice();
                    mainHandler.post(() -> {
                        setGlobalStatus("Conectado · Android");
                        bottomNav.setSelectedItemId(R.id.navFocus);
                        Snackbar.make(content, "Cuenta conectada", Snackbar.LENGTH_LONG).show();
                    });
                }, true);
            });
        }
    }

    private void syncNow() {
        if (!api.hasSession()) {
            bottomNav.setSelectedItemId(R.id.navAccount);
            Snackbar.make(content, "Inicia sesión para sincronizar", Snackbar.LENGTH_LONG).show();
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

    private void showAbout() {
        new MaterialAlertDialogBuilder(this)
                .setTitle(getString(R.string.about_title))
                .setMessage(getString(R.string.about_body))
                .setPositiveButton("Cerrar", null)
                .show();
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

    private void setGlobalStatus(String value) {
        if (globalStatus != null) globalStatus.setText(value);
    }

    private void runAsync(Task task, boolean reportError) {
        io.submit(() -> {
            try {
                task.run();
            } catch (Exception error) {
                if (reportError) {
                    mainHandler.post(() -> {
                        String message = error.getMessage() == null ? error.getClass().getSimpleName() : error.getMessage();
                        setGlobalStatus("Error · " + message);
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

    private String encode(String value) {
        return URLEncoder.encode(value == null ? "" : value, StandardCharsets.UTF_8);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private interface Task { void run() throws Exception; }
}
