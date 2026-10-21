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
        // MainActivity.bootstrapWorkspace() reloads once after preparing the
        // native account session. The panel may be visible in the FIRST document
        // before that reload replaces its DOM. Wait for the finished native
        // second document, not just a panel that is about to disappear.
        String last = "unobserved";
        for (int attempt = 0; attempt < 60; attempt++) {
            last = js(scenario,
                "(function(){var h=document.getElementById('igcDevConsole');" +
                "return document.readyState==='complete' &&" +
                "sessionStorage.getItem('igc_android_bootstrapped')==='1' &&" +
                "document.documentElement.classList.contains('igc-android-host') &&" +
                "h && h.style.display==='flex' &&" +
                "!!document.getElementById('igcDevAccount') &&" +
                "!!document.getElementById('page-sync') &&" +
                "typeof window.showPage==='function' &&" +
                "AndroidBridge.isDeveloperMode()})()");
            if ("true".equals(last)) return;
            Thread.sleep(400L);
        }
        // Only structural flags. No account data, cookies, tokens or storage
        // values. Never synthesize the Account button or bypass its real click.
        String diagnostic = js(scenario,
            "(function(){var h=document.getElementById('igcDevConsole');" +
            "return JSON.stringify({ready:document.readyState," +
            "nativeHost:document.documentElement.classList.contains('igc-android-host')," +
            "bootstrapFlag:sessionStorage.getItem('igc_android_bootstrapped')==='1'," +
            "panelVisible:!!h&&h.style.display==='flex'," +
            "buttonMounted:!!document.getElementById('igcDevAccount')," +
            "syncMounted:!!document.getElementById('page-sync')," +
            "showPageType:typeof window.showPage," +
            "developerBridge:AndroidBridge.isDeveloperMode()})})()");
        fail("Real Android Developer WebView not ready after native bootstrap;" +
             " last=" + last + "; safe flags=" + diagnostic);
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
                "&& document.documentElement.classList.contains('igc-android-host') "+
                "&& !!document.getElementById('igcDevAccount') "+
                "&& !!document.getElementById('page-sync')})()",
                "Developer native bridge or account screen not ready");
            // Separate navigation, selection and saving. Performing them all
            // inside one evaluateJavascript() is racy: WebView may respond
            // null if a screen transition invalidates the pending callback,
            // even when the button's action completed successfully.
            // Exercise the owner-visible button first. Capture ONLY route
            // ids/boolean state (never login inputs, session tokens, or cookies).
            // A WebView evaluateJavascript callback returning true alone does
            // not prove the click handler actually opened the account view.
            String clickEvidence = js(scenario,
                "(function(){try{var b=document.getElementById('igcDevAccount');"+
                "if(!b)return 'MISSING_BUTTON';"+
                "b.click();var p=document.querySelector('.page.active');"+
                "return JSON.stringify({button:true,sync:!!document.getElementById('page-sync'),"+
                "active:p?p.id:null,showPage:typeof window.showPage})"+
                "}catch(e){return 'CLICK_EXCEPTION:'+String(e&&e.name||'Error')+':'+String(e&&e.message||'')}})()");
            assertFalse("Developer Account button was not mounted: "+clickEvidence,
                clickEvidence.contains("MISSING_BUTTON"));
            assertFalse("Developer Account click handler raised: "+clickEvidence,
                clickEvidence.contains("CLICK_EXCEPTION"));
            try {
                untilJsTrue(scenario,
                    "(function(){return !!document.querySelector('#page-sync.active')})()",
                    "Developer Account navigation did not activate the real sign-in screen");
            } catch (AssertionError navigationFailure) {
                // This probe is read-only: it cannot accidentally "fix" a broken
                // button by invoking showPage itself. It distinguishes sync
                // injection, active-screen collision and stale page navigation.
                String diagnostic = js(scenario,
                    "(function(){var p=document.querySelector('.page.active');"+
                    "var sync=document.getElementById('page-sync');"+
                    "var btn=document.getElementById('igcDevAccount');"+
                    "return JSON.stringify({ready:document.readyState,"+
                    "syncExists:!!sync,syncActive:!!sync&&sync.classList.contains('active'),"+
                    "activePage:p?p.id:null,buttonExists:!!btn,"+
                    "developerPanel:!!document.getElementById('igcDevConsole'),"+
                    "showPageType:typeof window.showPage})})()");
                fail(navigationFailure.getMessage()+
                    "; immediately after click: "+clickEvidence+
                    "; safe WebView route diagnostic: "+diagnostic);
            }
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
