package com.michelslab.igcleaner;

import android.graphics.Bitmap;
import android.graphics.Rect;
import android.view.View;
import android.widget.ImageView;

import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import androidx.test.uiautomator.By;
import androidx.test.uiautomator.UiDevice;
import androidx.test.uiautomator.UiObject2;
import androidx.test.uiautomator.Until;

import com.google.android.material.appbar.MaterialToolbar;
import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.File;
import java.io.FileOutputStream;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * True on-device Home/About measurement and screenshots, with UIAutomator for
 * cross-window visibility. Espresso root-matching is intentionally not used:
 * Android 35 emulator intermittently loses app-window focus even when views are
 * actually displayed, yielding spurious RootViewWithoutFocusException errors.
 */
@RunWith(AndroidJUnit4.class)
public class AboutRenderTest {
    private UiDevice device() {
        return UiDevice.getInstance(InstrumentationRegistry.getInstrumentation());
    }

    private void requireNative(View view, String name, int width, int height) {
        assertNotNull(name + " missing from launched activity", view);
        assertTrue(name + " is hidden", view.getVisibility() == View.VISIBLE);
        assertTrue(name + " has zero/narrow measured width: " + view.getWidth(),
                view.getWidth() >= width);
        assertTrue(name + " has zero/small measured height: " + view.getHeight(),
                view.getHeight() >= height);
        if (view instanceof ImageView) {
            assertNotNull(name + " must have a rendered drawable", ((ImageView)view).getDrawable());
        }
    }

    private UiObject2 requireText(String label) {
        UiObject2 object = device().wait(Until.findObject(By.text(label)), 20000);
        assertNotNull("Missing actual visible Android text: " + label, object);
        return object;
    }

    private UiObject2 requireResource(String id, int minWidth, int minHeight) {
        String pkg = InstrumentationRegistry.getInstrumentation().getTargetContext().getPackageName();
        UiObject2 object = device().wait(Until.findObject(By.res(pkg + ":id/" + id)), 20000);
        assertNotNull("Missing actual on-screen About control: " + id, object);
        Rect bounds = object.getVisibleBounds();
        assertTrue("About control " + id + " is clipped/hidden: " + bounds,
                bounds.width() >= minWidth && bounds.height() >= minHeight);
        assertTrue("About control outside active display: " + id, bounds.top >= 0 &&
                bounds.bottom <= device().getDisplayHeight());
        return object;
    }

    private void screenshot(String surface, String label) throws Exception {
        InstrumentationRegistry.getInstrumentation().waitForIdleSync();
        Bitmap frame=InstrumentationRegistry.getInstrumentation().getUiAutomation().takeScreenshot();
        assertNotNull("Emulator failed to capture visible screen: " + surface, frame);
        String viewport=InstrumentationRegistry.getArguments().getString("viewport", "unknown");
        File dir = new File(InstrumentationRegistry.getInstrumentation()
                .getTargetContext().getExternalFilesDir(null), "igc-ui-capture");
        assertTrue("Screenshot destination missing", dir.isDirectory() || dir.mkdirs());
        File target=new File(dir, surface + "-" + viewport + "-" + label + ".png");
        try (FileOutputStream out = new FileOutputStream(target)) {
            assertTrue("PNG compression failed", frame.compress(Bitmap.CompressFormat.PNG,100,out));
        }
        frame.recycle();
        assertTrue("Empty actual screen capture: " + target, target.length()>3000);
    }

    @Test
    public void realHomeRendersNavigationAndWorkspace() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                requireNative(activity.findViewById(R.id.toolbar), "Home toolbar", 190, 70);
                requireNative(activity.findViewById(R.id.bottomNav), "Home navigation", 190, 75);
                requireNative(activity.findViewById(R.id.globalStatus), "Home status", 150, 20);
                requireNative(activity.findViewById(R.id.content), "Home workspace", 190, 180);
            });
            requireText("Instagram Cleaner Pro");
            screenshot("home","initial");
        }
    }

    @Test
    public void realAboutHasVisibleAuthorStudioAndReachableSocials() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                MaterialToolbar toolbar=activity.findViewById(R.id.toolbar);
                assertNotNull("Cannot locate actual native toolbar",toolbar);
                assertTrue("Could not open real About dialog",
                    toolbar.getMenu().performIdentifierAction(R.id.actionAbout,0));
            });
            requireText("Michel Duarte");
            requireText("Michel’s Lab");
            requireText("TOOLS WITH IDENTITY.");

            // Only check actual visible rectangles: a resource present in XML or
            // attached to an invisible 0dp panel does NOT satisfy this test.
            requireResource("aboutPortraitImage", 60, 70);
            requireResource("aboutStudioImage", 80, 60);
            screenshot("about","author");
            screenshot("about","studio");

            for (String link : new String[] {
                "aboutInstagram","aboutFacebook","aboutLinkedin","aboutGithub","aboutEmail"
            }) {
                // 39dp buttons at 320dpi should expose nearly 78px of height.
                // 70%-visible Email (55px) must fail, as in the v120.36 regression.
                requireResource(link, 140, 66);
            }
            screenshot("about","socials");
        }
    }
}
