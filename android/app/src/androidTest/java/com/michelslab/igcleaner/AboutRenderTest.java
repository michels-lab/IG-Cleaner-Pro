package com.michelslab.igcleaner;

import android.graphics.Bitmap;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import androidx.test.core.app.ActivityScenario;
import androidx.test.ext.junit.runners.AndroidJUnit4;
import androidx.test.platform.app.InstrumentationRegistry;
import com.google.android.material.appbar.MaterialToolbar;
import org.junit.Test;
import org.junit.runner.RunWith;
import java.io.File;
import java.io.FileOutputStream;

import static androidx.test.espresso.Espresso.onView;
import static androidx.test.espresso.action.ViewActions.scrollTo;
import static androidx.test.espresso.matcher.RootMatchers.isDialog;
import static androidx.test.espresso.assertion.ViewAssertions.matches;
import static androidx.test.espresso.matcher.ViewMatchers.isDisplayed;
import static androidx.test.espresso.matcher.ViewMatchers.isCompletelyDisplayed;
import static androidx.test.espresso.matcher.ViewMatchers.withId;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

/**
 * Executes the *actual* installed Android app rather than source/XML token scans.
 * Screenshots are QA evidence, NOT proof of a human's visual approval.
 */
@RunWith(AndroidJUnit4.class)
public class AboutRenderTest {
    private void assertMeasured(int id, int minWidth, int minHeight) {
        onView(withId(id)).inRoot(isDialog()).check((view, error) -> {
            if (error != null) throw error;
            assertNotNull("The About view must exist", view);
            assertTrue("About view " + id + " has zero/clipped width: " + view.getWidth(),
                    view.getWidth() >= minWidth);
            assertTrue("About view " + id + " has zero/clipped height: " + view.getHeight(),
                    view.getHeight() >= minHeight);
            assertTrue("About view " + id + " is hidden", view.getVisibility() == View.VISIBLE);
            if (view instanceof ImageView) {
                assertNotNull("About image drawable missing", ((ImageView) view).getDrawable());
            }
        });
    }

    private void screenshot(String label) throws Exception {
        InstrumentationRegistry.getInstrumentation().waitForIdleSync();
        Bitmap frame = InstrumentationRegistry.getInstrumentation().getUiAutomation().takeScreenshot();
        assertNotNull("Could not capture running Android screen", frame);
        String viewport = InstrumentationRegistry.getArguments().getString("viewport", "unknown");
        File dir = new File(InstrumentationRegistry.getInstrumentation()
                .getTargetContext().getExternalFilesDir(null), "igc-ui-capture");
        assertTrue("Cannot create screenshot directory", dir.isDirectory() || dir.mkdirs());
        File target = new File(dir, "about-" + viewport + "-" + label + ".png");
        try (FileOutputStream out = new FileOutputStream(target)) {
            assertTrue("Could not encode PNG", frame.compress(Bitmap.CompressFormat.PNG, 100, out));
        }
        frame.recycle();
        assertTrue("Screenshot is empty", target.length() > 3000);
    }

    @Test
    public void realHomeRendersNavigationAndWorkspace() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            onView(withId(R.id.toolbar)).check(matches(isCompletelyDisplayed()));
            onView(withId(R.id.bottomNav)).check(matches(isCompletelyDisplayed()));
            onView(withId(R.id.globalStatus)).check(matches(isDisplayed()));
            onView(withId(R.id.content)).check((view, error) -> {
                if (error != null) throw error;
                assertTrue("Home workspace is not measured", view.getWidth() >= 190
                        && view.getHeight() >= 200);
            });

            InstrumentationRegistry.getInstrumentation().waitForIdleSync();
            Bitmap frame = InstrumentationRegistry.getInstrumentation().getUiAutomation().takeScreenshot();
            assertNotNull("Cannot capture real Home screen", frame);
            String viewport = InstrumentationRegistry.getArguments().getString("viewport", "unknown");
            File dir = new File(InstrumentationRegistry.getInstrumentation()
                    .getTargetContext().getExternalFilesDir(null), "igc-ui-capture");
            assertTrue(dir.isDirectory() || dir.mkdirs());
            File target = new File(dir, "home-" + viewport + "-initial.png");
            try (FileOutputStream out = new FileOutputStream(target)) {
                assertTrue("Could not save Home capture", frame.compress(Bitmap.CompressFormat.PNG, 100, out));
            }
            frame.recycle();
            assertTrue("Home screenshot unexpectedly blank/empty", target.length() > 3000);
        }
    }

    @Test
    public void realAboutHasVisibleAuthorStudioAndReachableSocials() throws Exception {
        try (ActivityScenario<MainActivity> scenario = ActivityScenario.launch(MainActivity.class)) {
            scenario.onActivity(activity -> {
                MaterialToolbar toolbar = activity.findViewById(R.id.toolbar);
                assertNotNull("Toolbar unavailable", toolbar);
                assertTrue("Could not open actual About", toolbar.getMenu()
                        .performIdentifierAction(R.id.actionAbout, 0));
            });

            // Regression: at compact width a horizontal 0dp weighted panel was
            // stacked vertically without updating its width or weight.
            assertMeasured(R.id.aboutPairRow, 190, 140);
            assertMeasured(R.id.aboutAuthorColumn, 120, 95);
            assertMeasured(R.id.aboutStudioColumn, 120, 75);
            assertMeasured(R.id.aboutVersion, 80, 14);
            assertMeasured(R.id.aboutInstagram, 150, 40);
            assertMeasured(R.id.aboutFacebook, 150, 40);
            assertMeasured(R.id.aboutLinkedin, 150, 40);
            assertMeasured(R.id.aboutGithub, 150, 40);
            assertMeasured(R.id.aboutEmail, 150, 40);
            assertMeasured(R.id.aboutPortraitImage, 70, 80);
            assertMeasured(R.id.aboutStudioImage, 110, 70);

            // Previous green test scrolled to Email, yet its captured pixels
            // still showed zero social links. All five must be visible on entry.
            for (int linkId : new int[] {
                    R.id.aboutInstagram, R.id.aboutFacebook, R.id.aboutLinkedin,
                    R.id.aboutGithub, R.id.aboutEmail
            }) {
                onView(withId(linkId)).inRoot(isDialog())
                        .check(matches(isCompletelyDisplayed()));
            }
            screenshot("author");
            onView(withId(R.id.aboutAuthorColumn)).inRoot(isDialog()).perform(scrollTo());
            onView(withId(R.id.aboutStudioColumn)).inRoot(isDialog()).perform(scrollTo());
            screenshot("studio");
            onView(withId(R.id.aboutEmail)).inRoot(isDialog()).perform(scrollTo());
            onView(withId(R.id.aboutEmail)).inRoot(isDialog()).check(matches(isDisplayed()));
            screenshot("socials");
        }
    }
}
