package com.michelslab.igcleaner;

import android.content.Context;
import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public final class SyncApi {
    private static final String BASE_URL = "https://ilmztedebwdzgnlrvwxy.supabase.co";
    private static final String PUBLISHABLE_KEY = "sb_publishable_lR4d9UhSczfs4h90iK21DA_BfnqiBc1";

    private final SharedPreferences prefs;
    private String accessToken;
    private String refreshToken;
    private String email;

    public SyncApi(Context context) {
        prefs = context.getSharedPreferences("igc_sync", Context.MODE_PRIVATE);
        load();
    }

    public String getEmail() { return email == null ? "" : email; }
    public String getAccessToken() { return accessToken == null ? "" : accessToken; }
    public String getRefreshToken() { return refreshToken == null ? "" : refreshToken; }
    public boolean hasSession() { return accessToken != null && !accessToken.isBlank(); }
    public boolean nativeSessionIsNewer() { return prefs.getBoolean("native_newer", false); }
    public void markSessionBridgedToWeb() { prefs.edit().putBoolean("native_newer", false).apply(); }

    public synchronized void adoptWebSession(String rawJson) {
        try {
            if (rawJson == null || rawJson.isBlank() || "null".equals(rawJson.trim())) {
                logout();
                return;
            }
            JSONObject session = new JSONObject(rawJson);
            String nextAccess = session.optString("access_token", "");
            String nextRefresh = session.optString("refresh_token", "");
            if (nextAccess.isBlank()) return;
            accessToken = nextAccess;
            if (!nextRefresh.isBlank()) refreshToken = nextRefresh;
            JSONObject user = session.optJSONObject("user");
            if (user != null && !user.optString("email", "").isBlank()) {
                email = user.optString("email").trim();
            }
            prefs.edit()
                    .putString("access", accessToken)
                    .putString("refresh", refreshToken == null ? "" : refreshToken)
                    .putString("email", email == null ? "" : email)
                    .putBoolean("native_newer", false)
                    .apply();
        } catch (Exception ignored) {
            // Keep the last known-good native session if the WebView sends malformed data.
        }
    }

    public JSONObject webSession() {
        JSONObject out = new JSONObject();
        try {
            out.put("access_token", getAccessToken());
            out.put("refresh_token", getRefreshToken());
            out.put("token_type", "bearer");
            out.put("user", new JSONObject().put("email", getEmail()));
        } catch (Exception ignored) {}
        return out;
    }

    public void setEmail(String value) {
        email = value == null ? "" : value.trim();
        prefs.edit().putString("email", email).apply();
    }

    public void sendOtp(String value) throws Exception {
        setEmail(value);
        if (email.isBlank()) throw new IllegalArgumentException("Escribe tu correo.");
        requestObject("POST", "/auth/v1/otp",
                new JSONObject().put("email", email).put("create_user", true),
                false, null);
    }

    public void verifyOtp(String code) throws Exception {
        if (email.isBlank()) throw new IllegalStateException("Escribe tu correo.");
        String token = code == null ? "" : code.replaceAll("\\s+", "");
        if (token.isBlank()) throw new IllegalArgumentException("Escribe el código del correo.");

        JSONObject result = requestObject("POST", "/auth/v1/verify",
                new JSONObject()
                        .put("type", "email")
                        .put("email", email)
                        .put("token", token),
                false, null);
        saveSession(result);
        if (!hasSession()) throw new IOException("Supabase no devolvió una sesión.");
    }

    public void signInWithPassword(String value, String password) throws Exception {
        setEmail(value);
        if (email.isBlank()) throw new IllegalArgumentException("Escribe tu correo.");
        String pass = password == null ? "" : password;
        if (pass.isBlank()) throw new IllegalArgumentException("Escribe tu contraseña.");

        JSONObject result = requestObject("POST", "/auth/v1/token?grant_type=password",
                new JSONObject()
                        .put("email", email)
                        .put("password", pass),
                false, null);
        saveSession(result);
        if (!hasSession()) throw new IOException("No se pudo iniciar sesión.");
    }

    public void updatePassword(String password) throws Exception {
        String pass = password == null ? "" : password;
        if (pass.length() < 8) throw new IllegalArgumentException("La contraseña debe tener al menos 8 caracteres.");
        if (!hasSession()) throw new IllegalStateException("Verifica primero tu correo.");
        requestObject("PUT", "/auth/v1/user",
                new JSONObject().put("password", pass),
                true, null);
    }

    public void verifyOtpAndSetPassword(String code, String password) throws Exception {
        verifyOtp(code);
        updatePassword(password);
    }

    public void logout() {
        accessToken = "";
        refreshToken = "";
        prefs.edit().remove("access").remove("refresh").remove("native_newer").apply();
    }

    public JSONArray get(String tableQuery) throws Exception {
        String raw = raw("GET", "/rest/v1/" + tableQuery, null, true, null);
        return raw.isBlank() ? new JSONArray() : new JSONArray(raw);
    }

    public void upsert(String table, String conflict, JSONArray rows) throws Exception {
        Map<String, String> headers = new HashMap<>();
        headers.put("Prefer", "resolution=merge-duplicates,return=minimal");
        raw("POST",
                "/rest/v1/" + table + "?on_conflict=" + URLEncoder.encode(conflict, StandardCharsets.UTF_8),
                rows.toString(), true, headers);
    }

    public void patch(String tableQuery, JSONObject body) throws Exception {
        Map<String, String> headers = new HashMap<>();
        headers.put("Prefer", "return=minimal");
        raw("PATCH", "/rest/v1/" + tableQuery, body.toString(), true, headers);
    }

    private void load() {
        email = prefs.getString("email", "");
        accessToken = prefs.getString("access", "");
        refreshToken = prefs.getString("refresh", "");
    }

    private void saveSession(JSONObject result) {
        accessToken = result.optString("access_token", "");
        refreshToken = result.optString("refresh_token", refreshToken == null ? "" : refreshToken);
        JSONObject user = result.optJSONObject("user");
        if (user != null && !user.optString("email").isBlank()) setEmail(user.optString("email"));
        prefs.edit()
                .putString("access", accessToken)
                .putString("refresh", refreshToken)
                .putBoolean("native_newer", true)
                .apply();
    }

    private boolean refreshSession() {
        try {
            if (refreshToken == null || refreshToken.isBlank()) return false;
            JSONObject result = requestObject("POST", "/auth/v1/token?grant_type=refresh_token",
                    new JSONObject().put("refresh_token", refreshToken),
                    false, null);
            saveSession(result);
            return hasSession();
        } catch (Exception ignored) {
            // Do not destroy the remembered session on a transient auth/network failure.
            // The Web workspace may still own a newer rotated refresh token and will bridge
            // it back into native storage as soon as it refreshes successfully.
            return false;
        }
    }

    private JSONObject requestObject(String method, String path, JSONObject body,
                                     boolean auth, Map<String, String> headers) throws Exception {
        String raw = raw(method, path, body == null ? null : body.toString(), auth, headers);
        return raw.isBlank() ? new JSONObject() : new JSONObject(raw);
    }

    private String raw(String method, String path, String body, boolean auth,
                       Map<String, String> headers) throws Exception {
        return raw(method, path, body, auth, headers, true);
    }

    private String raw(String method, String path, String body, boolean auth,
                       Map<String, String> headers, boolean allowRefresh) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) new URL(BASE_URL + path).openConnection();
        connection.setRequestMethod(method);
        connection.setConnectTimeout(15_000);
        connection.setReadTimeout(20_000);
        connection.setRequestProperty("apikey", PUBLISHABLE_KEY);
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setRequestProperty("Accept", "application/json");
        if (auth && hasSession()) connection.setRequestProperty("Authorization", "Bearer " + accessToken);
        if (headers != null) {
            for (Map.Entry<String, String> entry : headers.entrySet()) {
                connection.setRequestProperty(entry.getKey(), entry.getValue());
            }
        }

        if (body != null) {
            connection.setDoOutput(true);
            try (OutputStream stream = connection.getOutputStream()) {
                stream.write(body.getBytes(StandardCharsets.UTF_8));
            }
        }

        int status = connection.getResponseCode();
        InputStream input = status >= 200 && status < 300
                ? connection.getInputStream()
                : connection.getErrorStream();

        String response = "";
        if (input != null) {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
                StringBuilder builder = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) builder.append(line);
                response = builder.toString();
            }
        }

        if ((status == 401 || status == 403) && auth && allowRefresh && refreshSession()) {
            return raw(method, path, body, true, headers, false);
        }

        if (status < 200 || status >= 300) {
            String message = response;
            try {
                JSONObject error = new JSONObject(response);
                message = error.optString("msg",
                        error.optString("message",
                                error.optString("error_description", response)));
            } catch (Exception ignored) {}
            throw new IOException("HTTP " + status + (message.isBlank() ? "" : " · " + message));
        }

        return response;
    }
}
