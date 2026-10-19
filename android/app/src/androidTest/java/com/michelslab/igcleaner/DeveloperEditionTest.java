package com.michelslab.igcleaner;

import android.webkit.WebView;
import android.database.Cursor;
import android.net.Uri;
import android.provider.MediaStore;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Assume;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import static org.junit.Assert.*;

/** Installed Developer APK: actual WebView/auth route/annotation persistence. */
@RunWith(AndroidJUnit4.class)
public class DeveloperEditionTest {
    private String js(ActivityScenario<MainActivity> scenario, String expression) throws Exception {
        CountDownLatch latch = new CountDownLatch(1);
        AtomicReference<String> actual = new AtomicReference<>("");
        scenario.onActivity(activity -> {
            WebView web = activity.findViewById(R.id.workspaceWebView);
            assertNotNull("Developer launcher must open the actual workspace WebView",web);
            web.evaluateJavascript(expression, value -> {
                actual.set(value);latch.countDown();
            });
        });
        assertTrue("WebView JavaScript callback timed out",latch.await(15,TimeUnit.SECONDS));
        return actual.get();
    }

    private void untilDeveloperReady(ActivityScenario<MainActivity> scenario) throws Exception {
        for(int attempt=0;attempt<30;attempt++){
            String visible=js(scenario,
                "(function(){var d=document.getElementById('igcDevConsole');return d&&d.style.display==='flex'})()");
            if("true".equals(visible)) return;
            Thread.sleep(400L);
        }
        fail("Android Developer panel never appeared on real embedded WebView");
    }

    private void untilJsTrue(ActivityScenario<MainActivity> scenario,
                             String expression, String description) throws Exception {
        String last = "unobserved";
        for (int attempt = 0; attempt < 40; attempt++) {
            last = js(scenario, expression);
            if ("true".equals(last)) return;
            Thread.sleep(300L);
        }
        fail(description + "; last WebView result: " + last);
    }

    @Test
    public void nativeDeveloperCloudWritesCannotReachProduction() throws Exception {
        Assume.assumeTrue(InstrumentationRegistry.getInstrumentation()
            .getTargetContext().getPackageName().endsWith(".developer"));
        assertTrue(SyncApi.blocksDeveloperMutation("POST", "/rest/v1/profile_state"));
        assertTrue(SyncApi.blocksDeveloperMutation("PATCH", "/rest/v1/instagram_accounts"));
        assertTrue(SyncApi.blocksDeveloperMutation("DELETE", "/rest/v1/rpc/igc_delete_instagram_profile"));
        assertTrue(SyncApi.blocksDeveloperMutation("PUT", "/auth/v1/user"));
        assertFalse(SyncApi.blocksDeveloperMutation("POST", "/auth/v1/otp"));
        assertFalse(SyncApi.blocksDeveloperMutation("POST", "/auth/v1/token?grant_type=password"));
        assertFalse(SyncApi.blocksDeveloperMutation("GET", "/rest/v1/instagram_accounts"));
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                SyncApi api=new SyncApi(activity);
                try {
                    api.deleteUnscoped("instagram_accounts?user_id=not.is.null");
                    fail("Developer native cloud delete must be rejected BEFORE network.");
                } catch(Exception denied) {
                    assertTrue("Expected intentional developer guard, not network error",
                        denied.getMessage().contains("Developer Edition"));
                }
            });
        }
    }

    @Test
    public void realDeveloperBuildSupportsAccountNotesAndRestart() throws Exception {
        Assume.assumeTrue(InstrumentationRegistry.getInstrumentation()
            .getTargetContext().getPackageName().endsWith(".developer"));
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(MainActivity.class)){
            scenario.onActivity(activity ->
                assertTrue("Must use separate .developer app package",
                    activity.getPackageName().endsWith(".developer")));
            untilDeveloperReady(scenario);
            untilJsTrue(scenario,
                "(function(){return document.readyState==='complete' "+
                "&& typeof window.showPage==='function' "+
                "&& AndroidBridge.isDeveloperMode() "+
                "&& !!document.getElementById('page-sync')})()",
                "Developer native bridge or account screen not ready");
            // Separate navigation, selection and saving. Performing them all
            // inside one evaluateJavascript() is racy: WebView may respond
            // null if a screen transition invalidates the pending callback,
            // even when the button's action completed successfully.
            js(scenario, "document.getElementById('igcDevAccount').click();true");
            untilJsTrue(scenario,
                "(function(){return !!document.querySelector('#page-sync.active')})()",
                "Developer Account navigation did not activate the real sign-in screen");
            js(scenario, "window.showPage('automations');true");
            untilJsTrue(scenario,
                "(function(){return !!document.querySelector('#page-automations.active')})()",
                "Automations page failed to render before section selection");
            js(scenario,
                "(function(){var b=document.getElementById('igcDevPick');"+
                "if(!b)return false;b.click();return true})()");
            untilJsTrue(scenario,
                "(function(){var b=document.getElementById('igcDevPick');"+
                "return !!b&&b.textContent.includes('Cancel selection')})()",
                "Developer section picker did not activate");
            js(scenario,
                "(function(){var t=document.getElementById('igcAutoBatchApproval');"+
                "if(!t)return false;"+
                "t.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));"+
                "return true})()");
            untilJsTrue(scenario,
                "(function(){var t=document.getElementById('igcDevSelected');"+
                "return !!t&&t.textContent.includes('igcAutoBatchApproval')})()",
                "Developer section picker did not retain precise control locator");
            js(scenario,
                "(function(){var input=document.getElementById('igcDevNoteInput');"+
                "var save=document.getElementById('igcDevSaveNote');"+
                "if(!input||!save)return false;"+
                "input.value='Developer Android test observation';save.click();return true})()");
            untilJsTrue(scenario,
                "(function(){var count=document.getElementById('igcDevNotesCount');"+
                "var notes=document.getElementById('igcDevNotes');"+
                "return !!count&&count.textContent.includes('saved section note')"+
                "&&!!notes&&notes.textContent.includes('Developer Android test observation')})()",
                "Developer note was not saved to the chosen workspace");
            // Wait for the actual *new document* after navigation, not a
            // stale panel that is still visible while reload is in progress.
            js(scenario,"window.__igcTestBeforeReload=true;location.reload();true");
            boolean restored=false;
            for(int attempt=0;attempt<50;attempt++){
                String state=js(scenario,
                    "(function(){var notes=document.getElementById('igcDevNotes');"+
                    "return !window.__igcTestBeforeReload && notes &&"+
                    "notes.textContent.includes('Developer Android test observation')})()");
                if("true".equals(state)){restored=true;break;}
                Thread.sleep(350L);
            }
            assertTrue("Developer notes failed to restore in a new WebView document after reload",
                       restored);
            assertEquals("true",js(scenario,
                "(function(){return document.getElementById('igcDevNotes').textContent.includes('igcAutoBatchApproval')})()"));
            assertEquals("true",js(scenario,
                "(function(){window.confirm=function(){return true};"+
                "document.getElementById('igcDevExportJson').click();return true})()"));
            // Open the actual native MediaStore export; a mock Blob/download
            // button does not prove this file reaches the Android user.
            String exported=null;
            for(int attempt=0;attempt<24&&exported==null;attempt++){
                Thread.sleep(400L);
                AtomicReference<String> report=new AtomicReference<>(null);
                scenario.onActivity(activity -> {
                    String[] projection={MediaStore.Downloads._ID,MediaStore.Downloads.DISPLAY_NAME};
                    try(Cursor cursor=activity.getContentResolver().query(
                        MediaStore.Downloads.EXTERNAL_CONTENT_URI,projection,
                        MediaStore.Downloads.DISPLAY_NAME+" LIKE ?",
                        new String[]{"IG-Cleaner-Developer-Audit-%.json"},null)){
                        if(cursor==null)return;
                        while(cursor.moveToNext()){
                            Uri uri=Uri.withAppendedPath(MediaStore.Downloads.EXTERNAL_CONTENT_URI,
                                String.valueOf(cursor.getLong(0)));
                            try(InputStream input=activity.getContentResolver().openInputStream(uri)){
                                if(input==null)continue;
                                ByteArrayOutputStream bytes=new ByteArrayOutputStream();
                                input.transferTo(bytes);
                                String json=bytes.toString(StandardCharsets.UTF_8);
                                if(json.contains("Developer Android test observation")
                                        &&json.contains("igcAutoBatchApproval")){
                                    report.set(json);break;
                                }
                            }catch(Exception ignored){}
                        }
                    }
                });
                exported=report.get();
            }
            assertNotNull("No exported annotated JSON appeared in native Android Downloads",exported);
            assertTrue(exported.contains("owner_section_annotations"));
        }
    }
}
