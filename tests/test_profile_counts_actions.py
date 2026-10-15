"""Safety and behavior contract for action-capable Instagram browser robot.

No real Instagram requests are sent in automated tests.
"""
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import ActionRobot, perform_visible_action, _action_issue, _atomic_json, _preclick_identity_blocked
from profile_counts_bridge import Collector


class NoClickIdentityRecoveryTests(unittest.TestCase):
    def test_only_proven_preclick_failures_may_retry_on_new_authorized_batch(self):
        self.assertTrue(_preclick_identity_blocked({
            "status":"blocked",
            "message":"The active Instagram account cannot be verified. No action was performed."
        }))
        self.assertTrue(_preclick_identity_blocked({
            "status":"blocked",
            "message":"The active Instagram account cannot be verified. No action was performed. Open your own profile in Chrome and confirm Edit profile appears."
        }))
        for entry in [
            {"status":"blocked","message":"Instagram requested verification after the action."},
            {"status":"blocked","message":"The active Instagram account changed during the action."},
            {"status":"review","message":"Final state is ambiguous."},
            {"status":"ok","message":"Action confirmed."},
        ]:
            self.assertFalse(_preclick_identity_blocked(entry))

class FakeButton:
    def __init__(self, click):
        self.clicked = 0
        self.callback = click

    def is_visible(self):
        return True

    def click(self, timeout=10000):
        self.clicked += 1
        self.callback()


class FakeMatches:
    def __init__(self, buttons):
        self.buttons = buttons

    def count(self):
        return len(self.buttons)

    def nth(self, i):
        return self.buttons[i]


class FakeRoot:
    @property
    def first(self):
        return self

    @property
    def last(self):
        return self

    def __init__(self, label, callback=None, visible=True, roles=("button",)):
        self.label = label
        self.visible = visible
        self.roles = roles
        self.clicker = FakeButton(callback or (lambda: None))

    def get_by_role(self, role, name=None):
        return FakeMatches([self.clicker] if
                           self.visible and role in self.roles and
                           name.fullmatch(self.label) else [])

    def get_by_text(self, label, exact=True):
        return FakeMatches([self.clicker] if self.visible and
                           label.fullmatch(self.label) else [])

    def nth(self, i):
        return self

    def count(self):
        return int(self.visible)

    def is_visible(self):
        return self.visible

    def inner_text(self, timeout=4000):
        return self.label


class FakeMissing:
    def count(self):
        return 0


class FakePage:
    def __init__(self, task, target="target.user", private=False):
        self.url = "https://www.instagram.com/"
        self.target = target
        self.private = private
        self.menu = FakeRoot("Unfollow", self.choose_unfollow,
                             visible=False, roles=("menuitem",))
        self.dialog = FakeRoot("Unfollow" if task == "unfollow" else "Cancel Request",
                               self.confirm, visible=False)
        self.header = FakeRoot("Following" if task == "unfollow" else "Requested",
                               self.open_action)
        self.delay = []

    def open_action(self):
        if self.header.label in ("Following", "Siguiendo"):
            self.menu.visible = True
        else:
            self.dialog.visible = True

    def choose_unfollow(self):
        self.menu.visible = False
        if self.private:
            self.dialog.visible = True
        else:
            self.header.label = getattr(self, "after_label", "Follow")

    def confirm(self):
        self.dialog.visible = False
        self.header.label = getattr(self, "after_label", "Follow")

    def goto(self, url, **_):
        self.url = url

    def wait_for_timeout(self, ms):
        self.delay.append(ms)

    def locator(self, selector):
        if selector == "header":
            return self.header
        if selector == '[role="menu"]':
            return self.menu
        if selector == '[role="dialog"]':
            return self.dialog
        if selector == '[role="listbox"]':
            return FakeMissing()
        if selector == 'input[name="password"]':
            return FakeMissing()
        raise AssertionError("Unexpected locator: " + selector)


class ActionSafetyTests(unittest.TestCase):
    def test_unfollow_requires_live_following_and_confirmed_follow_state(self):
        page = FakePage("unfollow")
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "ok")
        self.assertEqual(page.header.clicker.clicked, 1)
        self.assertEqual(page.menu.clicker.clicked, 1)
        self.assertEqual(page.dialog.clicker.clicked, 0, "Public profiles do not always ask for confirmation.")

    def test_private_unfollow_confirms_only_when_dialog_appears(self):
        page = FakePage("unfollow", private=True)
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "ok")
        self.assertEqual(page.header.clicker.clicked, 1)
        self.assertEqual(page.menu.clicker.clicked, 1)
        self.assertEqual(page.dialog.clicker.clicked, 1)

    def test_public_spanish_menu_unfollow_without_second_confirmation(self):
        page = FakePage("unfollow")
        page.header.label, page.menu.label = "Siguiendo", "Dejar de seguir"
        page.after_label = "Seguir"
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "ok")
        self.assertEqual(page.menu.clicker.clicked, 1)
        self.assertEqual(page.dialog.clicker.clicked, 0)

    def test_private_spanish_menu_then_confirmation(self):
        page = FakePage("unfollow", private=True)
        page.header.label, page.menu.label = "Siguiendo", "Dejar de seguir"
        page.dialog.label = "Dejar de seguir"
        page.after_label = "Seguir"
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "ok")
        self.assertEqual(page.menu.clicker.clicked, 1)
        self.assertEqual(page.dialog.clicker.clicked, 1)

    def test_cancel_requires_requested_button_and_verified_follow(self):
        page = FakePage("cancel")
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "cancel", "my.profile")
        self.assertEqual(status, "ok")
        self.assertEqual(page.dialog.clicker.clicked, 1)

    def test_pending_but_now_following_no_unfollow_and_incident(self):
        page=FakePage("cancel")
        page.header.label="Following"
        with patch("profile_actions.challenge_detected",return_value=False), \
             patch("profile_actions.signed_in_handle",return_value="my.profile"):
            status, message=perform_visible_action(page,"target.user","cancel","my.profile")
        self.assertEqual(status,"review")
        self.assertEqual(_action_issue("cancel",status,message),"pending_already_following")
        self.assertEqual(page.header.clicker.clicked,0)
        self.assertEqual(page.menu.clicker.clicked,0)
        self.assertEqual(page.dialog.clicker.clicked,0)

    def test_pending_without_requested_or_following_is_not_clicked(self):
        page=FakePage("cancel")
        page.header.label="Follow"
        with patch("profile_actions.challenge_detected",return_value=False), \
             patch("profile_actions.signed_in_handle",return_value="my.profile"):
            status, message=perform_visible_action(page,"target.user","cancel","my.profile")
        self.assertEqual(status,"review")
        self.assertEqual(_action_issue("cancel",status,message),"pending_not_requested")
        self.assertEqual(page.header.clicker.clicked,0)

    def test_followback_anomaly_has_dedicated_issue_code(self):
        # Old on-disk messages must still classify after the UI switches to English.
        legacy="Acción confirmada: Follow Back / Seguir también. La persona aún te sigue."
        current="Action confirmed: Follow Back. The person still follows you."
        self.assertEqual(_action_issue("unfollow","ok",legacy),"unexpected_followback")
        self.assertEqual(_action_issue("unfollow","ok",current),"unexpected_followback")
        self.assertEqual(_action_issue("unfollow","ok","Action confirmed: Follow."),"")
        self.assertEqual(_action_issue("cancel","review",
            "Outdated pending request: Instagram now shows Following;"),
            "pending_already_following")
        self.assertEqual(_action_issue("cancel","review",
            "Pendiente desactualizado: Instagram muestra Following"),
            "pending_already_following")

    def test_persisted_exception_report_survives_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            counts=Collector(root / "data",root / "session")
            robot=ActionRobot(counts,counts.data_dir,counts.session_dir)
            robot.owner, robot.account, robot.task = "ownerA","igA","cancel"
            robot.targets=["accepted.now","unknown.info"]
            _atomic_json(robot._base(),{
                "accepted.now":{"status":"review","issue":"pending_already_following",
                                "message":"Pendiente desactualizado: Instagram muestra Following","at":"2026-10-12"},
                "unknown.info":{"status":"review","issue":"missing_profile_info",
                                "message":"No hay información","at":"2026-10-12"}})
            snapshot=robot.snapshot()
            self.assertEqual(snapshot["issue_count"],2)
            self.assertEqual({i["issue"] for i in snapshot["issues"]},
                             {"pending_already_following","missing_profile_info"})
            second=ActionRobot(counts,counts.data_dir,counts.session_dir)
            second.owner,second.account,second.task=robot.owner,robot.account,robot.task
            second.targets=list(robot.targets)
            self.assertEqual(second.snapshot()["issue_count"],2)
            second.account="other-ig"
            self.assertEqual(second.snapshot()["issue_count"],0)

    def test_protected_profile_never_clicked(self):
        page = FakePage("unfollow")
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow",
                                               "my.profile", lambda _: False)
        self.assertEqual(status, "skipped")
        self.assertEqual(page.header.clicker.clicked, 0)

    def test_wrong_active_account_is_hard_stop(self):
        page = FakePage("cancel")
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="wrong.profile"):
            status, _ = perform_visible_action(page, "target.user", "cancel", "my.profile")
        self.assertEqual(status, "blocked")
        self.assertEqual(page.header.clicker.clicked, 0)

    def test_unexpected_follow_button_is_manual_review(self):
        page = FakePage("unfollow")
        page.header.label = "Follow"
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, _ = perform_visible_action(page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "review")
        self.assertEqual(page.header.clicker.clicked, 0)

    def test_protection_and_session_boundaries(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            counts = Collector(root / "data", root / "session")
            actions = ActionRobot(counts, counts.data_dir, counts.session_dir)
            # Simulate a controlled paused job, never launch Playwright here.
            actions.owner, actions.account = "owner1", "instagram1"
            actions.handle, actions.task = "my.profile", "unfollow"
            actions.targets = ["one.user", "two.user"]
            actions.status = "paused"
            with self.assertRaises(ValueError):
                actions.protect({"owner":"owner2", "account":"instagram1",
                                 "protected":["one.user"]})
            actions.protect({"owner":"owner1", "account":"instagram1",
                             "protected":["one.user"]})
            self.assertTrue(actions._protected_for("one.user"))
            actions.skip({"owner":"owner1", "account":"instagram1",
                          "username":"two.user"})
            self.assertIn("two.user", actions.skipped)
            result = actions.snapshot()
            self.assertEqual(result["remaining"], 0)
            self.assertEqual(result["protected"], 1)
            self.assertEqual(result["skipped"], 1)

    def test_requires_explicit_approved_queue_and_full_followers(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            counts=Collector(root / "data", root / "session")
            actions=ActionRobot(counts, counts.data_dir, counts.session_dir)
            payload={"owner":"owner1","account":"instagram1",
                     "expected_handle":"my.profile", "task":"unfollow",
                     "targets":["one.user"],"batch_size":30,
                     "gap_seconds":10,"rest_minutes":5}
            with self.assertRaisesRegex(ValueError, "explicitly approved"):
                actions.start(payload)
            payload["confirmation"]="unfollow:1"
            with self.assertRaisesRegex(ValueError, "Followers"):
                actions.start(payload)
            payload["followers_evidence"]=True
            actions._run=lambda: None
            result=actions.start(payload)
            actions.worker.join(timeout=2)
            self.assertEqual(result["total"],1)
            self.assertEqual(result["account"],"instagram1")


if __name__ == "__main__":
    unittest.main()
