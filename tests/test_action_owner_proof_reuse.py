"""Regression: owner-profile fallback navigates once per valid session, not per target.

Offline-only fake Chrome: no Instagram access, cookies, passwords or mutation.
All owner proofs still need a positive rendered Edit profile/header result first.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import profile_actions as actions


def make_page(context=None):
    page = Mock()
    page.url = "https://www.instagram.com/target.user/"
    page.locator.return_value.count.return_value = 0
    page.locator.return_value.is_visible.return_value = False
    page.context = context or Mock()
    return page


def owner_cookie(value):
    return [{"name": "ds_user_id", "value": value, "domain": ".instagram.com",
             "path": "/", "secure": True}]


class OwnerProofReuseTests(unittest.TestCase):
    def setUp(self):
        actions._OWNER_PROFILE_PROBE.bound_session = None
        self.nav_count = []
        actions._OWNER_PROFILE_PROBE.report = lambda: self.nav_count.append("owner")

    def tearDown(self):
        actions._OWNER_PROFILE_PROBE.bound_session = None
        actions._OWNER_PROFILE_PROBE.report = None

    def proof(self, *_args, on_navigation=None):
        if on_navigation:
            on_navigation()
        return "my.profile"

    def test_hidden_sidebar_proves_owner_once_for_multiple_targets(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        first, second = make_page(context), make_page(context)
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
            self.assertTrue(actions._verified_action_owner(first, "my.profile"))
            self.assertTrue(actions._verified_action_owner(second, "my.profile"))
            self.assertTrue(actions._verified_action_owner(first, "my.profile"))
        self.assertEqual(context.new_page.call_count, 1)
        self.assertEqual(self.nav_count, ["owner"])
        self.assertGreaterEqual(context.cookies.call_count, 3)

    def test_final_state_requires_two_fresh_cookie_reads_without_two_navigations(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        page = make_page(context)
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof), \
             patch.object(actions, "_follow_state", return_value="follow"):
            state, note = actions._verify_final_state(page, "my.profile", "target.user")
        self.assertEqual(state, "ok", note)
        self.assertEqual(context.new_page.call_count, 1)
        self.assertGreaterEqual(context.cookies.call_count, 3)
        self.assertEqual(self.nav_count, ["owner"])

    def test_changed_session_cookie_requires_fresh_owner_proof_and_blocks_on_mismatch(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        first, second = make_page(context), make_page(context)
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=[self.proof(first, "my.profile"), None]):
            self.assertTrue(actions._verified_action_owner(first, "my.profile"))
            context.cookies.return_value = owner_cookie("98765")
            self.assertFalse(actions._verified_action_owner(second, "my.profile"))
        self.assertEqual(context.new_page.call_count, 2)
        self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)

    def test_login_challenge_revokes_cached_proof(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        first, second = make_page(context), make_page(context)
        with patch.object(actions, "challenge_detected", side_effect=[False, True]), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
            self.assertTrue(actions._verified_action_owner(first, "my.profile"))
            self.assertFalse(actions._verified_action_owner(second, "my.profile"))
        self.assertEqual(context.new_page.call_count, 1)
        self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)

    def test_visible_wrong_owner_revokes_cache_without_navigation(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", side_effect=[None, "different.profile"]), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
            self.assertTrue(actions._verified_action_owner(make_page(context), "my.profile"))
            self.assertFalse(actions._verified_action_owner(make_page(context), "my.profile"))
        self.assertEqual(context.new_page.call_count, 1)
        self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)

    def test_missing_or_ambiguous_cookie_never_binds_owner_for_reuse(self):
        for missing in ([], owner_cookie("123") + owner_cookie("987"), owner_cookie("garbage")):
            with self.subTest(cookies=missing):
                actions._OWNER_PROFILE_PROBE.bound_session = None
                context = Mock()
                context.cookies.return_value = missing
                with patch.object(actions, "challenge_detected", return_value=False), \
                     patch.object(actions, "signed_in_handle", return_value=None), \
                     patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
                    self.assertTrue(actions._verified_action_owner(make_page(context), "my.profile"))
                    self.assertTrue(actions._verified_action_owner(make_page(context), "my.profile"))
                self.assertEqual(context.new_page.call_count, 2)
                self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)

    def test_expired_binding_requires_new_positive_owner_proof(self):
        context = Mock()
        context.cookies.return_value = owner_cookie("12345")
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof), \
             patch.object(actions.time, "monotonic", side_effect=[100.0, 281.0, 281.1]):
            self.assertTrue(actions._verified_action_owner(make_page(context), "my.profile"))
            self.assertTrue(actions._verified_action_owner(make_page(context), "my.profile"))
        self.assertEqual(context.new_page.call_count, 2)

    def test_session_switch_during_owner_navigation_fails_closed(self):
        context = Mock()
        context.cookies.side_effect = [owner_cookie("12345"), owner_cookie("67890")]
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
            self.assertFalse(actions._verified_action_owner(make_page(context), "my.profile"))
        self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)

    def test_no_cross_context_or_wrong_protocol_reuse(self):
        first_context = Mock()
        first_context.cookies.return_value = owner_cookie("12345")
        second_context = Mock()
        second_context.cookies.return_value = owner_cookie("12345")
        second = make_page(second_context)
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "verify_selected_owner_profile", side_effect=self.proof):
            self.assertTrue(actions._verified_action_owner(make_page(first_context), "my.profile"))
            self.assertTrue(actions._verified_action_owner(second, "my.profile"))
            second.url = "http://www.instagram.com/target.user/"
            self.assertFalse(actions._verified_action_owner(second, "my.profile"))
        self.assertEqual(first_context.new_page.call_count, 1)
        self.assertEqual(second_context.new_page.call_count, 1)
        self.assertIsNone(actions._OWNER_PROFILE_PROBE.bound_session)


if __name__ == "__main__":
    unittest.main()
