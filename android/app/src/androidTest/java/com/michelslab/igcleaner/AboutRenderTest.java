package com.michelslab.igcleaner;

import android.graphics.Bitmap;
import android.graphics.Rect;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.UiDevice;

import com.google.android.material.appbar.MaterialToolbar;

import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.File;
import java.io.FileOutputStream;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Installed-APK layout acceptance. Read actual visible view rectangles from
 * the native window rather than UIAutomator By.text(), which can be blind to
 * the test Activity's focused window on some API 35 emulator instances.
 * Screenshots come from UiAutomation.takeScreenshot(), never XML mockups.
 */
@RunWith(AndroidJUnit4.class)
public class AboutRenderTest {
    private Rect requireVisibleView(View view, String name, int minimumWidth, int minimumHeight) {
        assertNotNull(name + " missing from actual window", view);
        assertEquals(name + " marked hidden", View.VISIBLE, view.getVisibility());
        Rect rect = new Rect();
        assertTrue(name + " not visible in active window", view.getGlobalVisibleRect(rect));
        assertTrue(name + " too narrow: " + rect,
                rect.width() >= minimumWidth);
        assertTrue(name + " clipped vertically: " + rect,
                rect.height() >= minimumHeight);
        // UiDevice reports physical screen bounds, while app DisplayMetrics can
        // exclude status/navigation insets and falsely mark visible dialogs offscreen.
        UiDevice device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
        assertTrue(name + " outside physical screen: " + rect,
                rect.left >= 0 && rect.top >= 0 &&
                rect.right <= device.getDisplayWidth() &&
                rect.bottom <= device.getDisplayHeight());
        if (view instanceof ImageView)
            assertNotNull(name + " missing real drawable", ((ImageView)view).getDrawable());
        return rect;
    }

    private View findTextView(View root, String expected) {
        if (root instanceof TextView && expected.contentEquals(((TextView)root).getText()))
            return root;
        if (root instanceof ViewGroup) {
            ViewGroup group = (ViewGroup)root;
            for (int i=0; i<group.getChildCount(); i++) {
                View found = findTextView(group.getChildAt(i), expected);
                if (found != null) return found;
            }
        }
        return null;
    }

    private void screenshot(String surface, String label) throws Exception {
        InstrumentationRegistry.getInstrumentation().waitForIdleSync();
        Bitmap frame = InstrumentationRegistry.getInstrumentation().getUiAutomation().takeScreenshot();
        assertNotNull("Emulator failed to capture real " + surface + " screen", frame);
        String viewport = InstrumentationRegistry.getArguments().getString("viewport", "unknown");
        File dir = new File(InstrumentationRegistry.getInstrumentation().getTargetContext()
                .getExternalFilesDir(null), "igc-ui-capture");
        assertTrue("Screenshot directory unavailable", dir.isDirectory() || dir.mkdirs());
        File target = new File(dir, surface + "-" + viewport + "-" + label + ".png");
        try(FileOutputStream out = new FileOutputStream(target)) {
            assertTrue("PNG compression failed",frame.compress(Bitmap.CompressFormat.PNG,100,out));
        }
        frame.recycle();
        assertTrue("Screenshot contains no pixels",target.length()>3000);
    }

    @Test
    public void realHomeRendersNavigationAndWorkspace() throws Exception {
        try(ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            InstrumentationRegistry.getInstrumentation().waitForIdleSync();
            scenario.onActivity(activity -> {
                MaterialToolbar bar = activity.findViewById(R.id.toolbar);
                requireVisibleView(bar,"Home toolbar",190,70);
                requireVisibleView(activity.findViewById(R.id.bottomNav),"Home nav",190,75);
                requireVisibleView(activity.findViewById(R.id.globalStatus),"Home status",150,20);
                requireVisibleView(activity.findViewById(R.id.content),"Home workspace",190,180);
                requireVisibleView(activity.findViewById(R.id.appBrandTitle),"App title",100,20);
                assertTrue("App title changed", "Instagram Cleaner Pro".contentEquals(
                        ((TextView) activity.findViewById(R.id.appBrandTitle)).getText()));
                View aboutLabel = findTextView(bar,"About");
                requireVisibleView(aboutLabel,"About permanent top action",40,32);
                assertNotNull("About top action must exist",bar.getMenu().findItem(R.id.actionAbout));
                assertTrue("About item hidden in menu",bar.getMenu().findItem(R.id.actionAbout).isVisible());
            });
            screenshot("home","initial");
        }
    }

    @Test
    public void realAboutHasVisibleAuthorStudioAndReachableSocials() throws Exception {
        try(ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                MaterialToolbar bar = activity.findViewById(R.id.toolbar);
                assertNotNull("Native toolbar absent",bar);
                assertTrue("Could not open real About dialog",
                        bar.getMenu().performIdentifierAction(R.id.actionAbout,0));
            });
            InstrumentationRegistry.getInstrumentation().waitForIdleSync();
            scenario.onActivity(activity -> {
                assertNotNull("No native About dialog",activity.activeAboutDialog);
                assertNotNull("Dialog has no window",activity.activeAboutDialog.getWindow());
                View dialog = activity.activeAboutDialog.getWindow().getDecorView();

                Rect app = requireVisibleView(dialog.findViewById(R.id.aboutProductImage),
                        "App logo",130,105);
                Rect studio = requireVisibleView(dialog.findViewById(R.id.aboutStudioImage),
                        "Michel's Lab logo",150,100);
                assertTrue("App/studio marks must be side by side",app.right < studio.left + 25);
                assertTrue("App/studio marks vertically misaligned",
                        Math.abs(app.centerY()-studio.centerY()) < 50);

                Rect dev = requireVisibleView(dialog.findViewById(R.id.aboutDeveloperName),
                        "Developer name",190,28);
                assertEquals("Michel Armando Duarte Flores",
                        ((TextView)dialog.findViewById(R.id.aboutDeveloperName)).getText().toString());
                assertTrue("Developer information must be below both brand marks",
                        dev.top > Math.min(app.bottom,studio.bottom)-4);
                requireVisibleView(dialog.findViewById(R.id.aboutStudioLabel),"Studio name",90,18);
                requireVisibleView(dialog.findViewById(R.id.aboutStudioSlogan),"Studio slogan",80,17);

                Rect portrait = requireVisibleView(dialog.findViewById(R.id.aboutPortraitImage),
                        "Full author portrait",190,320);
                assertTrue("Portrait must appear below developer name",
                        portrait.top >= dev.bottom-8);
                for(String id : new String[]{"aboutInstagram","aboutFacebook","aboutLinkedin","aboutGithub","aboutEmail"}) {
                    int res = activity.getResources().getIdentifier(id,"id",activity.getPackageName());
                    assertTrue("Missing canonical social resource: "+id,res!=0);
                    Rect social = requireVisibleView(dialog.findViewById(res),id,140,66);
                    assertTrue("Social links must be beside, not under a tiny portrait: "+id,
                            social.left >= portrait.right-10);
                }
                MaterialToolbar toolbar = activity.findViewById(R.id.toolbar);
                assertNotNull("Native toolbar missing", toolbar);
                assertEquals("Only Sync and About belong in the global top menu", 2,
                        toolbar.getMenu().size());
                assertNotNull("Sync must be preserved", toolbar.getMenu().findItem(R.id.actionSync));
                assertNotNull("About must be preserved", toolbar.getMenu().findItem(R.id.actionAbout));
            });
            screenshot("about","author");
            screenshot("about","studio");
            screenshot("about","socials");
        }
    }
}
