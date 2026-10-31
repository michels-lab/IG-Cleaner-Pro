"""The exact failure shown by real Windows: Cancel Pending unexpectedly opens
Instagram's NORMAL 'Dejar de seguir' confirmation after a cohort of successes.

Offline Chromium route intercepts ALL Instagram requests; no real account,
network action, follow or unfollow is ever issued. Preserve WAL phases and
never identify the red Unfollow button as a valid request cancellation.
"""
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile_actions import perform_visible_action, _action_issue
from test_profile_actions_chromium import fake_profile

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


@unittest.skipIf(sync_playwright is None, "Playwright not available")
class CancelRequestChangedToFollowingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True, args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def html(self, *, locale="es", warning=False):
        original = ("Siguiendo" if locale == "es" else "Following")
        requested = ("Solicitado" if locale == "es" else "Requested")
        html = fake_profile(
            locale=locale, request_unfollow=True, include_warning=warning,
        ).replace(">" + original + "</button>",
                  ">" + requested + "</button>", 1)
        if not warning and locale == "es":
            html = html.replace(
                "Are you sure you want to stop following @target.user?",
                "¿Dejar de seguir a @target.user?")
        return html

    def serve(self, html):
        self.context.route("https://www.instagram.com/**",
                           lambda r: r.fulfill(status=200, content_type="text/html",
                                               body=html))

    def test_bare_unfollow_modal_never_confirms_cancel_in_spanish_or_english(self):
        for locale in ("es", "en"):
            with self.subTest(locale=locale):
                self.context.unroute_all()
                self.serve(self.html(locale=locale))
                phases = []
                state, reason = perform_visible_action(
                    self.page, "target.user", "cancel", "my.profile",
                    lambda _: True, on_pre_click=phases.append)
                self.assertEqual(state, "review", reason)
                self.assertTrue(reason.startswith("Cancel pending safety stop:"), reason)
                self.assertIn("No final Unfollow clicked", reason)
                self.assertEqual(_action_issue("cancel", state, reason),
                                 "pending_wrong_relationship_dialog")
                self.assertEqual(phases, ["relationship_control"],
                    "WAL must record the first click but NOT arm an Unfollow confirmation.")
                self.assertEqual(self.page.evaluate("window.__steps"), ["open"],
                    "The red Unfollow button must never be clicked during Cancel Pending.")
                # The unsafe dialog remains open for visual review; not success.
                self.assertTrue(self.page.locator("#request-confirm").is_visible())

    def test_pending_request_changed_to_following_before_first_click(self):
        import profile_actions
        html = self.html(locale="es", warning=False)
        self.serve(html)
        actual = profile_actions._wait_for_profile_relationship_control
        flips = []
        def changed_during_load(page, username, words, **options):
            located = actual(page, username, words, **options)
            if options.get("detect_already_not_requested") and located is not None:
                page.evaluate("document.querySelector('#relationship').textContent='Siguiendo'")
                flips.append(True)
            return located
        phases = []
        with patch.object(profile_actions, "_wait_for_profile_relationship_control",
                          side_effect=changed_during_load):
            state, reason = perform_visible_action(
                self.page, "target.user", "cancel", "my.profile",
                lambda _: True, on_pre_click=phases.append)
        self.assertEqual(flips, [True])
        self.assertEqual(state, "review", reason)
        self.assertIn("Outdated pending request:", reason)
        self.assertEqual(_action_issue("cancel", state, reason),
                         "pending_already_following")
        self.assertEqual(phases, [], "Do not arm a click after Requested became Following.")
        self.assertEqual(self.page.evaluate("window.__steps"), [],
                         "No Instagram relationship control was clicked.")
        self.assertFalse(self.page.locator("#request-confirm").is_visible())

    def test_valid_requested_to_cancel_confirmation_still_executes_once(self):
        for locale in ("es", "en"):
            with self.subTest(locale=locale):
                self.context.unroute_all()
                self.serve(self.html(locale=locale, warning=True))
                phases = []
                state, message = perform_visible_action(
                    self.page, "target.user", "cancel", "my.profile",
                    lambda _: True, on_pre_click=phases.append)
                self.assertEqual(state, "ok", message)
                self.assertEqual(phases,
                                 ["relationship_control", "cancel_request_confirmation"])
                self.assertEqual(self.page.evaluate("window.__steps"),
                                 ["open", "confirmed"],
                                 "Only the already-approved cancel should be confirmed.")


if __name__ == "__main__":
    unittest.main()
