package com.michelslab.igcleaner;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

import org.json.JSONObject;

import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Multiple account sessions, encrypted with this device's Android Keystore.
 * Only session tokens, never passwords. No cloud upload or cross-owner merge.
 * On keystore reset/corruption a saved session is unusable and must be reauthenticated.
 */
public final class AccountSessionVault {
    private static final String ALIAS = "igc_multi_account_sessions_v1";
    private final SharedPreferences storage;

    public AccountSessionVault(Context context) {
        storage = context.getSharedPreferences("igc_account_sessions_v1", Context.MODE_PRIVATE);
    }

    private static String normalized(String email) {
        return email == null ? "" : email.trim().toLowerCase(Locale.ROOT);
    }

    private SecretKey secret() throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(ALIAS))
            return (SecretKey) store.getKey(ALIAS, null);
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(ALIAS,
                KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).build());
        return generator.generateKey();
    }

    private static String key(String email) {
        // The email is visible as the account label; tokens are never part of a key.
        return "session:" + normalized(email);
    }

    public synchronized void store(String email, JSONObject session) throws Exception {
        final String identity = normalized(email);
        if (identity.isBlank() || !identity.contains("@") ||
                session == null || session.optString("access_token").isBlank() ||
                session.optString("refresh_token").isBlank())
            throw new IllegalArgumentException("No se puede guardar una sesión incompleta.");
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, secret());
        cipher.updateAAD(identity.getBytes(StandardCharsets.UTF_8));
        byte[] encrypted = cipher.doFinal(session.toString().getBytes(StandardCharsets.UTF_8));
        JSONObject envelope = new JSONObject()
                .put("iv", Base64.encodeToString(cipher.getIV(), Base64.NO_WRAP))
                .put("payload", Base64.encodeToString(encrypted, Base64.NO_WRAP));
        storage.edit().putString(key(identity), envelope.toString()).apply();
    }

    public synchronized JSONObject read(String email) throws Exception {
        String identity = normalized(email);
        String raw = storage.getString(key(identity), "");
        if (raw.isBlank()) return null;
        JSONObject envelope = new JSONObject(raw);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, secret(),
                new GCMParameterSpec(128, Base64.decode(envelope.getString("iv"), Base64.NO_WRAP)));
        cipher.updateAAD(identity.getBytes(StandardCharsets.UTF_8));
        JSONObject session = new JSONObject(new String(cipher.doFinal(
                Base64.decode(envelope.getString("payload"), Base64.NO_WRAP)), StandardCharsets.UTF_8));
        JSONObject user = session.optJSONObject("user");
        if (user == null || !identity.equals(normalized(user.optString("email"))))
            throw new IllegalArgumentException("La sesión guardada corresponde a otra cuenta.");
        return session;
    }

    public synchronized List<String> accounts() {
        List<String> result = new ArrayList<>();
        for (String name : storage.getAll().keySet())
            if (name.startsWith("session:")) result.add(name.substring("session:".length()));
        Collections.sort(result);
        return result;
    }

    public synchronized void remove(String email) {
        storage.edit().remove(key(email)).apply();
    }
}
