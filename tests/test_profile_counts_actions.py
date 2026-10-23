"""Safety and behavior contract for action-capable Instagram browser robot.

No real Instagram requests are sent in automated tests.
"""
import hashlib
import json
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (ActionRobot, ProtectedBatchCollision, perform_visible_action,
                             _action_issue, _atomic_json, _preclick_identity_blocked,
                             _profile_relationship_control)
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
        self.target_username = None

    def get_by_role(self, role, name=None):
        return FakeMatches([self.clicker] if
                           self.visible and role in self.roles and
                           name.fullmatch(self.label) else [])

    def get_by_text(self, label, exact=True):
        return FakeMatches([self.clicker] if self.visible and
                           (label.fullmatch(self.label) or
                            (self.target_username and label.fullmatch(self.target_username)))
                           else [])

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
        self.header.target_username = target
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
        if selector == "main":
            # Original offline fixtures use only a semantic profile header.
            # A main-only Instagram layout is exercised separately in real
            # Chromium, not fabricated through this unit-test FakePage.
            return FakeRoot("", visible=False)
        if selector == '[role="menu"]':
            return self.menu
        if selector == '[role="dialog"]':
            return self.dialog
        if selector == '[role="listbox"]':
            return FakeMissing()
        if selector == 'input[name="password"]':
            return FakeMissing()
        raise AssertionError("Unexpected locator: " + selector)


class TargetIdentityRegressionTests(unittest.TestCase):
    """Previously stale Instagram SPA headers were accepted by URL alone."""

    def test_wrong_visible_header_never_supplies_action_control(self):
        page = FakePage("unfollow")
        page.goto("https://www.instagram.com/target.user/")
        page.header.target_username = "other.user"
        self.assertIsNone(_profile_relationship_control(
            page, "target.user", [r"Following"]))
        # The exact matching rendered target remains eligible.
        page.header.target_username = "target.user"
        self.assertIsNotNone(_profile_relationship_control(
            page, "target.user", [r"Following"]))
        page.url = "http://www.instagram.com/target.user/"
        self.assertIsNone(_profile_relationship_control(
            page, "target.user", [r"Following"]))

    def test_stale_profile_before_first_click_fails_closed(self):
        page = FakePage("unfollow")
        page.header.target_username = "other.user"
        # Reproduce a hydration race in which an earlier inspection returned
        # a live Following button but the visible hero now names another user.
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"), \
             patch("profile_actions._wait_for_profile_relationship_control",
                   return_value=page.header):
            status, note = perform_visible_action(
                page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "review")
        self.assertIn("No relationship action clicked", note)
        self.assertEqual(page.header.clicker.clicked, 0)
        self.assertEqual(page.menu.clicker.clicked, 0)

    def test_target_swap_after_opening_unfollow_menu_never_clicks_menu(self):
        page = FakePage("unfollow")
        old_open = page.header.clicker.callback

        def switch_hero_after_open():
            old_open()
            page.header.target_username = "other.user"

        page.header.clicker.callback = switch_hero_after_open
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, note = perform_visible_action(
                page, "target.user", "unfollow", "my.profile")
        self.assertEqual(status, "review")
        self.assertIn("No further click", note)
        self.assertEqual(page.header.clicker.clicked, 1)
        self.assertEqual(page.menu.clicker.clicked, 0)

    def test_target_swap_after_opening_pending_dialog_never_confirms(self):
        page = FakePage("cancel")
        old_open = page.header.clicker.callback

        def switch_hero_after_open():
            old_open()
            page.header.target_username = "other.user"

        page.header.clicker.callback = switch_hero_after_open
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"):
            status, note = perform_visible_action(
                page, "target.user", "cancel", "my.profile")
        self.assertEqual(status, "review")
        self.assertIn("No further click", note)
        self.assertEqual(page.header.clicker.clicked, 1)
        self.assertEqual(page.dialog.clicker.clicked, 0)


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
             patch("profile_actions.signed_in_handle",return_value="my.profile"), \
             patch("profile_actions.ACTION_CONTROL_WAIT_MS",30), \
             patch("profile_actions.CANCEL_NO_REQUEST_MIN_WAIT_MS",0):
            status, message=perform_visible_action(page,"target.user","cancel","my.profile")
        self.assertEqual(status,"already_not_requested")
        self.assertIn("No Cancel Request clicked",message)
        self.assertEqual(_action_issue("cancel",status,message),"")
        self.assertEqual(page.header.clicker.clicked,0)

    def test_already_not_requested_survives_restart_and_never_claims_click(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot.owner, robot.account, robot.task = "owner", "instagram", "cancel"
            robot.targets = ["no.request"]
            _atomic_json(robot._base(), {"no.request": {
                "status": "already_not_requested",
                "message": "No Cancel Request clicked; no active outgoing request.",
                "at": "2026-10-20T00:00:00Z", "issue": ""}})
            snapshot = robot.snapshot()
            self.assertEqual(snapshot["successful"], 0)
            self.assertEqual(snapshot["already_not_requested"], 1)
            self.assertEqual(snapshot["remaining"], 0)
            cold = ActionRobot(counts, counts.data_dir, counts.session_dir)
            history = cold.attempted_history({
                "owner": "owner", "account": "instagram", "task": "cancel"})
            self.assertEqual(history["attempted_usernames"], ["no.request"])
            self.assertNotIn("no.request", history["reusable_usernames"])
            for foreign in (
                {"owner": "other", "account": "instagram", "task": "cancel"},
                {"owner": "owner", "account": "other", "task": "cancel"},
                {"owner": "owner", "account": "instagram", "task": "unfollow"}
            ):
                self.assertNotIn("no.request", cold.attempted_history(foreign)["attempted_usernames"])

    def test_cancel_wrong_owner_follow_back_cannot_skip_request(self):
        page = FakePage("cancel")
        page.header.label = "Follow Back"
        with patch("profile_actions.challenge_detected",return_value=False), \
             patch("profile_actions.signed_in_handle",return_value="wrong.owner"), \
             patch("profile_actions.ACTION_CONTROL_WAIT_MS",30), \
             patch("profile_actions.CANCEL_NO_REQUEST_MIN_WAIT_MS",0):
            status, _ = perform_visible_action(page, "target.user", "cancel", "my.profile")
        self.assertEqual(status, "blocked")
        self.assertEqual(page.header.clicker.clicked, 0)

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
        # An unanchored Follow label is not proof that the CURRENT target is
        # already unfollowed. Keep it unresolved, never click or silently skip.
        page = FakePage("unfollow")
        page.header.label = "Follow"
        page.header.target_username = "different.user"  # Unanchored button.
        with patch("profile_actions.challenge_detected", return_value=False), \
             patch("profile_actions.signed_in_handle", return_value="my.profile"), \
             patch("profile_actions.ACTION_CONTROL_WAIT_MS", 650):
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

    def test_new_desktop_batch_cannot_implicitly_unprotect_saved_profile(self):
        # Only fake worker threads are used: no Instagram navigation or clicks.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot._run = lambda: None
            robot.owner, robot.account, robot.task = "owner1", "instagram1", "cancel"
            _atomic_json(robot._protection_file(), ["permanent.user"])

            first = {"owner": "owner1", "account": "instagram1",
                     "expected_handle": "my.profile", "task": "cancel",
                     "targets": ["first.user"], "batch_size": 20,
                     "gap_seconds": 10, "rest_minutes": 5,
                     "protected": [], "confirmation": "cancel:1"}
            robot.start(first)
            robot.worker.join(timeout=2)
            self.assertTrue(robot._protected_for("permanent.user"),
                            "Omitting persisted favorites from the UI must not erase them")
            self.assertIn("permanent.user", robot._protected())

            # An authorized next robot mode shares that SAME Instagram owner's
            # global safety list but retains task-specific action journals.
            second = dict(first, task="unfollow", targets=["second.user"],
                          confirmation="unfollow:1", followers_evidence=True,
                          protected=["new.favorite"])
            robot.start(second)
            robot.worker.join(timeout=2)
            self.assertEqual(robot._protected(),
                             {"permanent.user", "new.favorite"})
            robot._protected_for("second.user")

            # A different Instagram workspace does not inherit these guards:
            # the source of truth is the owner + Instagram account pair.
            other = ActionRobot(counts, counts.data_dir, counts.session_dir)
            other._run = lambda: None
            other.start(dict(first, account="instagram2", targets=["other.user"],
                             protected=["new.other"], confirmation="cancel:1"))
            other.worker.join(timeout=2)
            self.assertEqual(other._protected(), {"new.other"})
            self.assertEqual(robot._protected(),
                             {"permanent.user", "new.favorite"})

    def test_live_protection_survives_empty_next_batch_ui_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            first = ActionRobot(counts, counts.data_dir, counts.session_dir)
            first.owner, first.account, first.task = "owner1", "instagram1", "cancel"
            first._run = lambda: None
            first.protect({"owner": "owner1", "account": "instagram1",
                           "protected": ["saved.from.review"]})
            restarted = ActionRobot(counts, counts.data_dir, counts.session_dir)
            restarted._run = lambda: None
            restarted.start({"owner": "owner1", "account": "instagram1",
                             "expected_handle": "my.profile", "task": "unfollow",
                             "targets": ["unfollow.user"],
                             "batch_size": 30, "gap_seconds": 10,
                             "rest_minutes": 5, "protected": [],
                             "followers_evidence": True,
                             "confirmation": "unfollow:1"})
            restarted.worker.join(timeout=2)
            self.assertTrue(restarted._protected_for("saved.from.review"))

    def test_stale_disk_protected_cohort_rejected_atomically_then_replanned(self):
        # No browser or Instagram account is contacted: the worker is faked.
        for task, size in (("unfollow", 40), ("cancel", 30)):
            with self.subTest(task=task), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                counts = Collector(root / "data", root / "session")
                robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
                robot._run = lambda: None
                owner, account = "owner-A", "ig-one"
                protected = ["acct005", "acct016"]
                path = robot._protection_file_for(owner, account)
                _atomic_json(path, protected)
                original_file = path.read_bytes()
                all_targets = [f"acct{i:03d}" for i in range(75)]
                first = all_targets[:size]
                payload = dict(owner=owner, account=account, task=task,
                               expected_handle="my.profile", targets=first,
                               batch_size=size, gap_seconds=10, rest_minutes=5,
                               protected=[], confirmation=f"{task}:{size}",
                               followers_evidence=task=="unfollow")
                review_file = robot._review_batches_file_for(owner, account, task)
                journal_file = robot._base_for(owner, account, task)
                with self.assertRaises(ProtectedBatchCollision) as raised:
                    robot.start(payload)
                conflict = raised.exception
                self.assertEqual(conflict.usernames, protected)
                self.assertEqual(conflict.task, task)
                self.assertEqual(conflict.batch_size, size)
                self.assertEqual(path.read_bytes(), original_file)
                self.assertFalse(review_file.exists())
                self.assertFalse(journal_file.exists())
                self.assertIsNone(robot.worker)
                self.assertEqual(robot.owner, "")
                self.assertEqual(robot.status, "idle")
                self.assertFalse(counts.session_dir.exists(),
                                 "Rejected batch must not launch Chrome")

                # The next exact cohort is computed from the full imported
                # list; it is a distinct owner-approved plan with a NEW token.
                corrected = [u for u in all_targets if u not in protected][:size]
                robot.start(dict(payload, targets=corrected))
                robot.worker.join(timeout=2)
                self.assertEqual(robot.targets, corrected)
                self.assertEqual(robot._protected(), set(protected))
                self.assertEqual(len(robot._review_batches(owner, account, task)), 1)

    def test_stale_ui_and_existing_review_batch_do_not_get_rewritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot._run = lambda: None
            scope = {"owner": "ownerA", "account": "account1",
                     "expected_handle": "my.profile", "task": "cancel",
                     "batch_size": 30, "gap_seconds": 10, "rest_minutes": 5,
                     "confirmation": "cancel:30"}
            targets = [f"pending{i:03d}" for i in range(30)]
            # A UI-selected favorite must also invalidate its own proposed
            # cohort even without an existing disk file.
            with self.assertRaises(ProtectedBatchCollision) as rejected:
                robot.start({**scope, "targets": targets,
                             "protected": ["pending008"]})
            self.assertEqual(rejected.exception.usernames, ["pending008"])
            self.assertFalse(robot._protection_file_for("ownerA", "account1").exists())
            self.assertFalse(robot._review_batches_file_for(
                "ownerA", "account1", "cancel").exists())

            robot.start({**scope, "targets": targets, "protected": []})
            robot.worker.join(timeout=2)
            original = robot._pending_review("ownerA", "account1", "cancel")
            path = robot._review_batches_file_for("ownerA", "account1", "cancel")
            before = path.read_bytes()
            robot.protect({"owner": "ownerA", "account": "account1",
                           "protected": ["pending008"]})
            with self.assertRaises(ProtectedBatchCollision):
                robot.start({**scope, "targets": targets, "protected": [],
                             "batch_id": original["id"]})
            self.assertEqual(path.read_bytes(), before,
                             "An unapproved cohort must never be overwritten")
            self.assertEqual(robot.active_batch_id, original["id"])
            self.assertFalse(robot.worker.is_alive())

            # Same username in another Instagram account is not a conflict.
            other = ActionRobot(counts, counts.data_dir, counts.session_dir)
            other._run = lambda: None
            other.start({**scope, "account": "account2", "targets": targets,
                         "protected": []})
            other.worker.join(timeout=2)
            self.assertEqual(len(other._review_batches(
                "ownerA", "account2", "cancel")), 1)

    def test_rejected_cohort_has_local_replan_protocol(self):
        source = (Path(__file__).resolve().parents[1] /
                  "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(
                      encoding="utf-8")
        bridge = (Path(__file__).resolve().parents[1] /
                  "tools/profile_counts_bridge.py").read_text(encoding="utf-8")
        self.assertIn('except ProtectedBatchCollision as exc:', bridge)
        self.assertIn('"code": "stale_protected_batch"', bridge)
        self.assertIn('"protected_usernames": exc.usernames', bridge)
        self.assertIn('if(value.code==="stale_protected_batch")', source)
        self.assertIn('igcAutoReplanStaleProtected(e,originalScope,originalMode)', source)
        self.assertIn('for(const user of users){write("unfollow",user,true);write("cancel",user,true)}', source)
        self.assertIn('Choose Run again to inspect and confirm a NEW eligible batch', source)
        self.assertNotIn('requestAction("start",data).catch(', source)

    def test_protected_pending_batch_can_be_safely_deferred_without_reviewed(self):
        # New (protected) favorites during an already authorized batch must
        # never force unprotection or false Reviewed on untouched profiles.
        for task, size in (("cancel", 30), ("unfollow", 40)):
            with self.subTest(task=task), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                counts = Collector(root / "data", root / "session")
                robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
                robot._run = lambda: None
                scope = dict(owner="owner-one", account="instagram-one", task=task,
                             expected_handle="my.profile", batch_size=size,
                             gap_seconds=10, rest_minutes=5,
                             followers_evidence=task=="unfollow",
                             confirmation=f"{task}:{size}")
                imported = [f"candidate{i:03d}" for i in range(90)]
                robot.start(dict(scope, targets=imported[:size], protected=[]))
                robot.worker.join(timeout=2)
                pending = robot._pending_review(scope["owner"], scope["account"], task)
                self.assertIsNotNone(pending)
                batch_id = pending["id"]
                journal_path = robot._base_for(scope["owner"], scope["account"], task)
                _atomic_json(journal_path, {
                    "candidate001": {"status": "ok", "message": "Confirmed action",
                                     "at": "2026-10-20T00:00:00Z"},
                    "candidate002": {"status": "review", "message": "Uncertain after click",
                                     "at": "2026-10-20T00:01:00Z"},
                })
                original_journal = journal_path.read_bytes()
                robot.protect({"owner": scope["owner"], "account": scope["account"],
                               "protected": ["candidate005", "candidate018"]})
                protection_path = robot._protection_file_for(
                    scope["owner"], scope["account"])
                original_guard = protection_path.read_bytes()
                original_batch = robot.batch_review(scope)["batch"]
                self.assertEqual(original_batch["protected_in_cohort"],
                                 ["candidate005", "candidate018"])
                self.assertEqual(original_batch["action_results"]["candidate002"]["status"],
                                 "review")
                with self.assertRaises(ProtectedBatchCollision):
                    robot.start(dict(scope, targets=imported[:size],
                                     batch_id=batch_id, protected=[]))

                for invalid in (
                    dict(scope, batch_id="not-the-batch",
                         confirmation="defer-protected:not-the-batch"),
                    dict(scope, batch_id=batch_id, confirmation="defer-protected:wrong"),
                    dict(scope, batch_id=batch_id, account="instagram-two",
                         confirmation="defer-protected:"+batch_id),
                    dict(scope, batch_id=batch_id, owner="owner-two",
                         confirmation="defer-protected:"+batch_id),
                    dict(scope, batch_id=batch_id, task="audit",
                         confirmation="defer-protected:"+batch_id),
                ):
                    with self.subTest(invalid=invalid):
                        with self.assertRaises(ValueError):
                            robot.defer_protected_batch(invalid)
                class BusyWorker:
                    def is_alive(self): return True
                robot.worker = BusyWorker()
                with self.assertRaisesRegex(ValueError, "Pause all Chrome robots"):
                    robot.defer_protected_batch(dict(
                        scope, batch_id=batch_id,
                        confirmation="defer-protected:"+batch_id))
                robot.worker = None
                counts.worker = BusyWorker()
                with self.assertRaisesRegex(ValueError, "Pause all Chrome robots"):
                    robot.defer_protected_batch(dict(
                        scope, batch_id=batch_id,
                        confirmation="defer-protected:"+batch_id))
                counts.worker = None

                archived = robot.defer_protected_batch(dict(
                    scope, batch_id=batch_id,
                    confirmation="defer-protected:"+batch_id))
                self.assertFalse(archived["marked_reviewed"])
                self.assertEqual(archived["approved_usernames"], [])
                self.assertEqual(archived["action_recorded"], 2)
                self.assertEqual(archived["untouched"], size-2)
                self.assertEqual(archived["protected_usernames"],
                                 ["candidate005", "candidate018"])
                self.assertEqual(journal_path.read_bytes(), original_journal)
                self.assertEqual(protection_path.read_bytes(), original_guard)
                entries = robot._review_batches(scope["owner"], scope["account"], task)
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["targets"], imported[:size])
                self.assertIsNone(entries[0]["approved_at"])
                self.assertEqual(entries[0]["deferred_reason"], "protected_collision")
                self.assertFalse(robot.batch_review(scope)["batch"])
                with self.assertRaises(ValueError):
                    robot.approve_batch({**scope, "batch_id": batch_id,
                                         "confirmation": "reviewed:"+batch_id})
                with self.assertRaises(ValueError):
                    robot.defer_protected_batch(dict(
                        scope, batch_id=batch_id,
                        confirmation="defer-protected:"+batch_id))
                # Old click journals survive; a completely NEW, explicitly
                # approved selection is now possible without either protected
                # profile or the two saved uncertain/completed action targets.
                self.assertEqual(set(robot.attempted_history(scope)["attempted_usernames"]),
                                 {"candidate001", "candidate002"})
                excluded = {"candidate001", "candidate002",
                            "candidate005", "candidate018"}
                corrected = [u for u in imported if u not in excluded][:size]
                robot.start(dict(scope, targets=corrected, protected=[]))
                robot.worker.join(timeout=2)
                new_batch = robot._pending_review(scope["owner"], scope["account"], task)
                self.assertNotEqual(new_batch["id"], batch_id)
                self.assertEqual(new_batch["targets"], corrected)
                self.assertEqual(len(robot._review_batches(
                    scope["owner"], scope["account"], task)), 2)

    def test_archived_batch_summary_survives_restart_and_is_owner_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot._run = lambda: None
            scope = {"owner": "userA", "account": "igA", "task": "cancel"}
            payload = {**scope, "expected_handle": "my.profile",
                       "targets": ["first.user", "second.user"], "batch_size": 30,
                       "gap_seconds": 10, "rest_minutes": 5,
                       "protected": [], "confirmation": "cancel:2"}
            robot.start(payload)
            robot.worker.join(timeout=2)
            batch_id = robot._pending_review("userA", "igA", "cancel")["id"]
            robot.protect({**scope, "protected": ["second.user"]})
            robot.defer_protected_batch({
                **scope, "batch_id": batch_id,
                "confirmation": "defer-protected:" + batch_id})
            cold = ActionRobot(counts, counts.data_dir, counts.session_dir)
            summary = cold.deferred_batch_history(scope)
            self.assertTrue(summary["read_only"])
            self.assertEqual(summary["total_deferred"], 1)
            self.assertEqual(summary["recent"][0]["batch_id"], batch_id)
            self.assertEqual(summary["recent"][0]["target_count"], 2)
            self.assertEqual(summary["recent"][0]["protected_count"], 1)
            self.assertEqual(summary["recent"][0]["untouched"], 2)
            self.assertFalse(summary["recent"][0]["marked_reviewed"])
            self.assertNotIn("targets", summary["recent"][0],
                             "Default UI summaries must not leak username lists")
            for other in (
                {**scope, "account": "igB"},
                {**scope, "owner": "userB"},
                {**scope, "task": "unfollow"},
            ):
                result = cold.deferred_batch_history(other)
                self.assertEqual(result["total_deferred"], 0)
                self.assertEqual(result["recent"], [])

    def test_resized_40_keeps_untouched_users_reusable_not_archived(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot._run = lambda: None
            original = [f"cohort{i:03d}" for i in range(40)]
            scope = dict(owner="owner", account="instagram", task="cancel",
                         expected_handle="owner.handle", batch_size=40,
                         rest_minutes=0, gap_seconds=10, protected=[],
                         confirmation="cancel:40", targets=original)
            robot.start(scope)
            robot.worker.join(timeout=2)
            pending = robot._pending_review("owner","instagram","cancel")
            batch_id = pending["id"]
            journal_path = robot._base_for("owner","instagram","cancel")
            _atomic_json(journal_path,{
                "cohort000":{"status":"review","message":"Ambiguous possible click",
                             "at":"2026-10-20T00:01:00Z"},
                "cohort001":{"status":"ok","message":"Confirmed earlier click",
                             "at":"2026-10-20T00:02:00Z"}
            })
            original_bytes = journal_path.read_bytes()
            review_path = robot._review_batches_file_for("owner","instagram","cancel")
            original_review = review_path.read_bytes()
            request = dict(owner="owner",account="instagram",task="cancel",
                           batch_id=batch_id,desired_batch_size=10,
                           confirmation="replan-size:"+batch_id+":10")
            for invalid in (
                {**request,"confirmation":"wrong"},
                {**request,"batch_id":"other"},
                {**request,"desired_batch_size":40},
                {**request,"desired_batch_size":0},
                {**request,"desired_batch_size":10.0},
                {**request,"owner":"other-owner"},
                {**request,"account":"other-instagram"},
            ):
                with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                    robot.replan_incomplete_batch(invalid)
            self.assertEqual(journal_path.read_bytes(),original_bytes)
            self.assertEqual(review_path.read_bytes(),original_review)
            class Active:
                def is_alive(self): return True
            counts.worker=Active()
            with self.assertRaisesRegex(ValueError,"Pause all Chrome robots"):
                robot.replan_incomplete_batch(request)
            counts.worker=None
            result=robot.replan_incomplete_batch(request)
            self.assertFalse(result["marked_reviewed"])
            self.assertEqual(result["approved_usernames"],[])
            self.assertEqual(result["previous_size"],40)
            self.assertEqual(result["requested_new_size"],10)
            self.assertEqual(result["active_size"],10)
            self.assertEqual(result["reusable_after_active"],28)
            self.assertEqual(result["status"],"replanned_active_cohort_not_archived")
            self.assertEqual(journal_path.read_bytes(),original_bytes)
            # Same cohort remains active, with the original 40 preserved;
            # unprocessed profiles remain reusable without archiving.
            active=robot._pending_review("owner","instagram","cancel")
            self.assertEqual(active["id"],batch_id)
            self.assertEqual(active["targets"],original[2:12])
            self.assertEqual(active["original_targets"],original)
            self.assertEqual(active["carryover_targets"],original[12:])
            self.assertEqual(active["selected_batch_size"],10)
            self.assertIsNone(active.get("deferred_at"))
            self.assertIsNone(active.get("approved_at"))
            self.assertEqual(robot.deferred_batch_history({
                "owner":"owner","account":"instagram","task":"cancel"})["total_deferred"],0)
            cold=ActionRobot(counts,counts.data_dir,counts.session_dir)
            history=cold.attempted_history({
                "owner":"owner","account":"instagram","task":"cancel"})
            self.assertEqual(set(history["attempted_usernames"]),
                             {"cohort000","cohort001"})
            self.assertIn("cohort039",history["reusable_usernames"])
            self.assertNotIn("cohort000",history["reusable_usernames"])
            for other in (
                {"owner":"other","account":"instagram","task":"cancel"},
                {"owner":"owner","account":"other","task":"cancel"},
                {"owner":"owner","account":"instagram","task":"unfollow"},
            ):
                self.assertEqual(cold.attempted_history(other)["reusable_usernames"],[])
            cold._run=lambda: None
            cold.start({**scope,"targets":original[2:12],"batch_size":10,
                        "batch_id":batch_id,"confirmation":"cancel:10"})
            cold.worker.join(timeout=2)
            self.assertEqual(journal_path.read_bytes(),original_bytes)
            # Only the new active ten can be Reviewed, and only after their
            # actions are independently recorded.
            with self.assertRaises(ValueError):
                cold.approve_batch({"owner":"owner","account":"instagram",
                                    "task":"cancel","batch_id":batch_id,
                                    "confirmation":"reviewed:"+batch_id})
            journal=json.loads(journal_path.read_text(encoding="utf-8"))
            for u in original[2:12]:
                journal[u]={"status":"ok","message":"Confirmed for test"}
            _atomic_json(journal_path,journal)
            approved=cold.approve_batch({"owner":"owner","account":"instagram",
                                         "task":"cancel","batch_id":batch_id,
                                         "confirmation":"reviewed:"+batch_id})
            self.assertEqual(len(approved["approved_usernames"]),10)
            later=ActionRobot(counts,counts.data_dir,counts.session_dir)
            remainder=later.attempted_history({
                "owner":"owner","account":"instagram","task":"cancel"})["reusable_usernames"]
            self.assertEqual(remainder,original[12:])
            later._run=lambda: None
            later.start({**scope,"targets":remainder[:10],"batch_size":10,
                         "confirmation":"cancel:10"})
            later.worker.join(timeout=2)
            self.assertEqual(later._pending_review(
                "owner","instagram","cancel")["targets"],original[12:22])
            self.assertEqual(len(later._review_batches("owner","instagram","cancel")),2)
            self.assertEqual(later.deferred_batch_history({
                "owner":"owner","account":"instagram","task":"cancel"})["total_deferred"],0)
            self.assertEqual(json.loads(journal_path.read_text())["cohort000"]["status"],
                             "review","Uncertain original click never became reusable")

    def test_defer_requires_a_durable_protected_collision(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            robot._run = lambda: None
            payload = dict(owner="owner", account="account", task="cancel",
                           expected_handle="my.profile", targets=["first.user"],
                           batch_size=30, gap_seconds=10, rest_minutes=5,
                           protected=[], confirmation="cancel:1")
            robot.start(payload)
            robot.worker.join(timeout=2)
            pending = robot._pending_review("owner", "account", "cancel")
            batch_id = pending["id"]
            review_file = robot._review_batches_file_for("owner", "account", "cancel")
            original = review_file.read_bytes()
            with self.assertRaisesRegex(ValueError, "no saved protected collision"):
                robot.defer_protected_batch({
                    "owner": "owner", "account": "account", "task": "cancel",
                    "batch_id": batch_id, "confirmation": "defer-protected:"+batch_id})
            self.assertEqual(review_file.read_bytes(), original)
            self.assertEqual(robot._pending_review(
                "owner", "account", "cancel")["id"], batch_id)
            # A protected profile outside this cohort is not justification
            # to retire the current owner-approved batch.
            robot.protect({"owner": "owner", "account": "account",
                           "protected": ["unrelated.user"]})
            with self.assertRaisesRegex(ValueError, "no saved protected collision"):
                robot.defer_protected_batch({
                    "owner": "owner", "account": "account", "task": "cancel",
                    "batch_id": batch_id, "confirmation": "defer-protected:"+batch_id})
            self.assertEqual(review_file.read_bytes(), original)

    def test_desktop_defer_control_requires_explicit_confirmation(self):
        root = Path(__file__).resolve().parents[1]
        desktop = (root / "desktop/ig_cleaner_pro_v120_27_synced_companion.html").read_text(
            encoding="utf-8")
        bridge = (root / "tools/profile_counts_bridge.py").read_text(encoding="utf-8")
        self.assertIn('id="igcAutoDeferProtected"', desktop)
        self.assertIn('window.igcAutoDeferProtectedBatch=async function()', desktop)
        self.assertIn('check=await requestAction("review-batch"', desktop)
        self.assertIn('if(!window.confirm(warning))return', desktop)
        self.assertIn('confirmation:"defer-protected:"+b.id', desktop)
        self.assertIn('requestAction("defer-protected-batch"', desktop)
        self.assertIn('result.marked_reviewed!==false', desktop)
        self.assertIn('defer.style.display=blocked.length?', desktop)
        self.assertIn('"/api/actions/defer-protected-batch"', bridge)
        self.assertIn('result = actions.defer_protected_batch(data)', bridge)
        self.assertIn('"/api/actions/deferred-batches"', bridge)
        self.assertIn('result = actions.deferred_batch_history(data)', bridge)
        self.assertIn('id="igcAutoDeferredSummary"', desktop)
        self.assertIn('requestAction("deferred-batches"', desktop)

    def test_explicit_unprotect_is_confirmed_owner_scoped_and_idle_only(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            counts = Collector(root / "data", root / "session")
            robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            scope = {"owner": "owner1", "account": "instagram1"}
            other = {"owner": "owner1", "account": "instagram2"}

            # Cold Windows boot: an unbound loopback controller MUST reject
            # arbitrary owner-scope mutations. UI stages favorites locally and
            # passes them only with the next explicitly approved batch.
            with self.assertRaisesRegex(ValueError, "same account"):
                robot.protect({**scope, "protected": ["never.click"]})
            self.assertFalse(robot._protection_file_for(
                scope["owner"], scope["account"]).exists())
            robot.owner, robot.account, robot.task = "owner1", "instagram1", "cancel"
            robot.protect({**scope, "protected": ["never.click"]})
            robot.protect({**scope, "protected": []})
            self.assertIn("never.click", json.loads(
                robot._protection_file_for(scope["owner"], scope["account"]).read_text()))
            path = robot._protection_file_for(scope["owner"], scope["account"])
            # Backward compatibility: never change the prior saved-journal
            # filename when introducing a no-implicit-unprotect protocol.
            expected_digest = hashlib.sha256(b"owner1\0instagram1").hexdigest()[:32]
            self.assertEqual(path.name, "action-protected-" + expected_digest + ".json")
            original = path.read_bytes()
            for rejected in (
                {**scope, "unprotected": ["never.click"]},
                {**scope, "unprotected": ["never.click"], "confirmation": "unprotect:other"},
                {**scope, "protected": ["new"], "unprotected": ["never.click"],
                 "confirmation": "unprotect:never.click"},
            ):
                with self.subTest(rejected=rejected):
                    with self.assertRaisesRegex(ValueError, "confirmation|separate commands"):
                        robot.protect(rejected)
                    self.assertEqual(path.read_bytes(), original)

            robot.owner, robot.account, robot.task = "owner1", "instagram1", "unfollow"
            robot.status = "running"
            robot.worker = type("ActiveWorker", (), {"is_alive": lambda self: True})()
            confirmed = {**scope, "unprotected": ["never.click"],
                         "confirmation": "unprotect:never.click"}
            with self.assertRaisesRegex(ValueError, "active robot"):
                robot.protect(confirmed)
            with self.assertRaisesRegex(ValueError, "same account"):
                robot.protect({**other, "protected": ["other.user"]})
            self.assertEqual(path.read_bytes(), original)

            robot.worker = None
            robot.status = "paused"
            robot.protect(confirmed)
            self.assertEqual(json.loads(path.read_text()), [])
            # Unprotecting this owner never unprotects another Instagram scope.
            other_robot = ActionRobot(counts, counts.data_dir, counts.session_dir)
            other_robot.owner, other_robot.account, other_robot.task = (
                other["owner"], other["account"], "cancel")
            other_robot.protect({**other, "protected": ["other.user"]})
            self.assertEqual(json.loads(other_robot._protection_file_for(
                other["owner"], other["account"]).read_text()), ["other.user"])
            self.assertEqual(json.loads(path.read_text()), [])

    def test_desktop_toggle_never_sends_addition_for_unprotect(self):
        html = (Path(__file__).resolve().parents[1] / "desktop" /
                "ig_cleaner_pro_v120_27_synced_companion.html").read_text(encoding="utf-8")
        section = html.split("window.igcAutoProtect=async function(kind,user)", 1)[1].split(
            "window.igcAutoClearSkipped=", 1)[0]
        self.assertIn("unprotected:[u],confirmation:\"unprotect:\"+u", section)
        self.assertIn("if(!window.confirm(", section)
        self.assertIn("await requestAction(\"protect\"", section)
        self.assertIn("write(kind,u,nextProtected)", section)
        self.assertIn("Saved protection unchanged", section)
        self.assertIn("Protected locally for the next approved Windows batch", section)
        self.assertNotIn("requestAction(\"protect\",{...actionOwner(),protected:[u]}).catch", section)

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
