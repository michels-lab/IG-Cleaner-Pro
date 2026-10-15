"""Regression: Instagram reCAPTCHA is an auth blocker, never a browsing target.

This tests only simulated page URLs/visible content. It does not contact
Instagram, solve verification, or test an actual user's signed-in Chrome.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_instagram import challenge_detected, safe_to_probe_owner_from_home


class FakeLocator:
    def __init__(self, *, content="", visible=False):
        self.content = content
        self.visible = visible

    def count(self):
        return 1 if self.visible else 0

    def nth(self, _):
        return self

    def is_visible(self):
        return self.visible

    def inner_text(self, timeout=2500):
        return self.content


class FakePage:
    def __init__(self, url, *, body="", password=False):
        self.url, self.body, self.password = url, body, password

    def locator(self, selector):
        if selector == "body":
            return FakeLocator(content=self.body)
        if selector == 'input[type="password"], input[name="password"]':
            return FakeLocator(visible=self.password)
        raise AssertionError("Unexpected access to page: " + selector)


class ReCaptchaRegressionTests(unittest.TestCase):
    def test_actual_owner_screenshot_recaptcha_route_blocks_without_page_text(self):
        for url in (
            "https://www.instagram.com/auth_platform/recaptcha?apc=safe-fixture",
            "https://instagram.com/auth_platform/recaptcha/",
            "https://instagram.com/challenge/",
            "https://instagram.com/checkpoint/security",
        ):
            with self.subTest(url=url):
                page = FakePage(url)
                self.assertTrue(challenge_detected(page))
                self.assertFalse(safe_to_probe_owner_from_home(page))

    def test_visible_recaptcha_and_human_verification_stop_collection(self):
        for message in ("I'm not a robot", "We've used Google's reCAPTCHA Enterprise product",
                        "Verify you are human"):
            with self.subTest(message=message):
                self.assertTrue(challenge_detected(FakePage(
                    "https://www.instagram.com/", body=message)))

    def test_login_and_redirect_never_trigger_automated_owner_probe(self):
        for page in (
            FakePage("https://www.instagram.com/accounts/login/"),
            FakePage("https://www.instagram.com/accounts/login/?next=%2F"),
            FakePage("https://www.instagram.com/", password=True),
            FakePage("https://www.instagram.com/direct/inbox/"),
            FakePage("https://www.google.com/recaptcha/"),
        ):
            with self.subTest(url=page.url):
                self.assertFalse(safe_to_probe_owner_from_home(page))

    def test_only_regular_home_without_login_form_can_probe(self):
        page = FakePage("https://www.instagram.com/")
        self.assertFalse(challenge_detected(page))
        self.assertTrue(safe_to_probe_owner_from_home(page))
        self.assertFalse(challenge_detected(FakePage(
            "https://www.instagram.com/friend/", body="A nice photo of my robot")))
        self.assertFalse(safe_to_probe_owner_from_home(FakePage(
            "https://www.instagram.com/friend/")))

    def test_both_robots_stop_on_challenge_without_bypassing_security(self):
        root = Path(__file__).resolve().parents[1]
        bridge = (root / "tools/profile_counts_bridge.py").read_text(encoding="utf-8")
        actions = (root / "tools/profile_actions.py").read_text(encoding="utf-8")
        detector = (root / "tools/profile_counts_instagram.py").read_text(encoding="utf-8")
        self.assertIn("safe_to_probe_owner_from_home(page)", bridge)
        self.assertIn("any(challenge_detected(p) for p in pages)", bridge)
        self.assertIn("any(challenge_detected(tab) for tab in browser.pages", actions)
        self.assertIn('"blocked"', actions)
        self.assertIn('"/auth_platform/recaptcha"', detector)
        self.assertNotIn("captcha_solver", detector)


if __name__ == "__main__":
    unittest.main()
