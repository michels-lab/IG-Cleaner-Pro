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

    @Test
    public void realDeveloperBuildSupportsAccountNotesAndRestart() throws Exception {
        Assume.assumeTrue(InstrumentationRegistry.getInstrumentation()
            .getTargetContext().getPackageName().endsWith(".developer"));
        try(ActivityScenario<MainActivity> scenario=ActivityScenario.launch(MainActivity.class)){
            scenario.onActivity(activity ->
                assertTrue("Must use separate .developer app package",
                    activity.getPackageName().endsWith(".developer")));
            untilDeveloperReady(scenario);
            assertEquals("true",js(scenario,
                "(function(){return AndroidBridge.isDeveloperMode() && !!document.getElementById('page-sync')})()"));
            assertEquals("true",js(scenario,
                "(function(){document.getElementById('igcDevAccount').click();"+
                "return !!document.querySelector('#page-sync.active')})()"));
            assertEquals("true",js(scenario,
                "(function(){window.showPage('automations');"+
                "document.getElementById('igcDevPick').click();"+
                "var t=document.getElementById('igcAutoBatchApproval');"+
                "if(!t)return false;"+
                "t.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));"+
                "document.getElementById('igcDevNoteInput').value='Developer Android test observation';"+
                "document.getElementById('igcDevSaveNote').click();"+
                "return document.getElementById('igcDevNotesCount').textContent.includes('saved section note')})()"));
            assertEquals("true",js(scenario,
                "(function(){return document.getElementById('igcDevNotes').textContent.includes('Developer Android test observation')})()"));
            // Real WebView localStorage persistence, no fake external database.
            js(scenario,"location.reload();true");
            untilDeveloperReady(scenario);
            assertEquals("true",js(scenario,
                "(function(){return document.getElementById('igcDevNotes').textContent.includes('Developer Android test observation')})()"));
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
