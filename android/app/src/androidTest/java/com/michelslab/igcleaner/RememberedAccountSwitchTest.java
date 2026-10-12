package com.michelslab.igcleaner;

import static org.junit.Assert.*;

import android.content.Context;
import androidx.test.core.app.ApplicationProvider;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import org.json.JSONObject;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.UUID;

/** Exercises encrypted login slots on a real Android Keystore/emulator.
 * No network, real credentials, or production accounts are used.
 */
@RunWith(AndroidJUnit4.class)
public class RememberedAccountSwitchTest {
    @Test public void switchingLoginsKeepsSeparateTokenAndOnlySignOutForgetsActive() throws Exception {
        Context context = ApplicationProvider.getApplicationContext();
        AccountSessionVault vault = new AccountSessionVault(context);
        SyncApi api = new SyncApi(context);
        String prefix = UUID.randomUUID().toString().replace("-", "");
        String one = "first." + prefix + "@example.test";
        String two = "second." + prefix + "@example.test";
        long expiry = System.currentTimeMillis()/1000L + 3600;
        JSONObject a = new JSONObject()
                .put("access_token", "access-first-" + prefix)
                .put("refresh_token", "refresh-first-" + prefix)
                .put("expires_at", expiry)
                .put("user", new JSONObject().put("email", one));
        JSONObject b = new JSONObject()
                .put("access_token", "access-second-" + prefix)
                .put("refresh_token", "refresh-second-" + prefix)
                .put("expires_at", expiry)
                .put("user", new JSONObject().put("email", two));
        vault.store(one, a);
        vault.store(two, b);
        try {
            assertTrue(vault.accounts().contains(one));
            assertTrue(vault.accounts().contains(two));
            assertFalse(context.getSharedPreferences("igc_account_sessions_v1",
                    Context.MODE_PRIVATE).getString("session:" + one, "")
                    .contains("refresh-first"));
            api.activateRememberedAccount(one);
            assertEquals(one, api.getEmail());
            assertEquals("access-first-" + prefix, api.getAccessToken());
            api.activateRememberedAccount(two);
            assertEquals(two, api.getEmail());
            assertEquals("access-second-" + prefix, api.getAccessToken());
            assertTrue(api.rememberedAccounts().contains(one));
            api.logout();
            assertFalse(api.hasSession());
            assertFalse(vault.accounts().contains(two));
            assertTrue(vault.accounts().contains(one));
            api.activateRememberedAccount(one);
            assertEquals(one, api.getEmail());
        } finally {
            vault.remove(one);
            vault.remove(two);
            api.prepareAnotherAccount();
        }
    }

    @Test public void mismatchCannotActivateDifferentAccount() throws Exception {
        Context context = ApplicationProvider.getApplicationContext();
        AccountSessionVault vault = new AccountSessionVault(context);
        String target = "mismatch." + UUID.randomUUID() + "@example.test";
        try {
            JSONObject fake = new JSONObject()
                    .put("access_token", "a")
                    .put("refresh_token", "r")
                    .put("expires_at", System.currentTimeMillis()/1000L + 3600)
                    .put("user", new JSONObject().put("email", "different@example.test"));
            vault.store(target, fake);
            assertThrows(IllegalArgumentException.class,
                    () -> new SyncApi(context).activateRememberedAccount(target));
        } finally {
            vault.remove(target);
        }
    }
}
