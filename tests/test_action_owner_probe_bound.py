"""GRANADA owner-profile navigation regression (offline, no Instagram traffic).

A Follow/Requested settling loop may poll up to five times, but should not
navigate to /owner/ once per poll. Each success needs an initial and final
independent owner proof; mismatches/challenges fail closed. This never clicks.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import profile_actions as actions


class OwnerProofBoundTests(unittest.TestCase):
    def page(self):
        page = Mock()
        page.locator.return_value.count.return_value = 0
        page.locator.return_value.is_visible.return_value = False
        return page

    def test_slow_follow_hydration_requires_two_owner_proofs_not_each_poll(self):
        page = self.page()
        owner_calls = []
        states = iter((None, None, None, "follow", "follow"))
        def owner_check(current, expected):
            owner_calls.append((current, expected))
            return True
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "_verified_action_owner", side_effect=owner_check), \
             patch.object(actions, "_follow_state", side_effect=lambda *_: next(states)):
            status, message = actions._verify_final_state(
                page, "my.profile", "target.user", checks=5)
        self.assertEqual(status, "ok", message)
        self.assertEqual(len(owner_calls), 2,
            "Five target settling polls must not issue five owner-profile visits")
        self.assertEqual(page.wait_for_timeout.call_count, 3)
        self.assertTrue(all(expected == "my.profile" for _,expected in owner_calls))

    def test_visible_changed_owner_during_wait_is_blocked(self):
        page = self.page()
        attempts = iter(("my.profile", "my.profile", "other.owner"))
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", side_effect=lambda *_: next(attempts)), \
             patch.object(actions, "_verified_action_owner", return_value=True) as proof, \
             patch.object(actions, "_follow_state", return_value=None) as follow:
            status, message = actions._verify_final_state(
                page, "my.profile", "target.user", checks=5)
        self.assertEqual(status, "blocked", message)
        self.assertEqual(proof.call_count, 1)
        self.assertEqual(follow.call_count, 1)

    def test_final_owner_mismatch_never_claims_success(self):
        page = self.page()
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "_verified_action_owner", side_effect=[True, False]) as owner, \
             patch.object(actions, "_follow_state", return_value="follow"):
            status, message = actions._verify_final_state(
                page, "my.profile", "target.user", checks=5)
        self.assertEqual(status, "blocked", message)
        self.assertEqual(owner.call_count, 2)

    def test_owner_unknown_all_three_attempts_is_blocked(self):
        page = self.page()
        with patch.object(actions, "challenge_detected", return_value=False), \
             patch.object(actions, "signed_in_handle", return_value=None), \
             patch.object(actions, "_verified_action_owner", return_value=False) as owner, \
             patch.object(actions, "_follow_state") as follow:
            status, _ = actions._verify_final_state(page, "my.profile", "target.user")
        self.assertEqual(status, "blocked")
        self.assertEqual(owner.call_count, 3)
        follow.assert_not_called()

    def test_owner_probe_counts_navigation_not_credentials_or_target(self):
        page = self.page()
        page.context.new_page.return_value = self.page()
        observed = []
        actions._OWNER_PROFILE_PROBE.report = lambda: observed.append("visit")
        try:
            with patch.object(actions, "challenge_detected", return_value=False), \
                 patch.object(actions, "signed_in_handle", return_value=None), \
                 patch.object(actions, "verify_selected_owner_profile", return_value="my.profile") as proof:
                result = actions._verified_action_owner(page, "my.profile")
            self.assertTrue(result)
            self.assertEqual(observed, ["visit"])
            self.assertEqual(proof.call_count, 1)
            page.context.new_page.return_value.close.assert_called_once()
        finally:
            actions._OWNER_PROFILE_PROBE.report = None


if __name__ == "__main__":
    unittest.main()
