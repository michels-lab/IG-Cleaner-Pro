"""GRANADA: durable pre-click intent prevents replay after power loss.

Fixtures are local fake Chrome pages; CI never accesses Instagram accounts.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import (
    ActionRobot, _preclick_no_action, perform_visible_action, _atomic_json)
from profile_counts_bridge import Collector
from test_profile_counts_actions import FakePage


class Interruption(BaseException):
    """Simulate abrupt power loss, not caught by ordinary Exception handlers."""


class DurableClickIntentTests(unittest.TestCase):
    def make_robot(self, base, task="unfollow", target="chosen.user"):
        root = Path(base)
        counts = Collector(root/"counts", root/"chrome")
        robot = ActionRobot(counts, root/"canonical-journal", counts.session_dir)
        robot.owner, robot.account, robot.handle = "owner.account", "ig-account", "owner.name"
        robot.task, robot.targets = task, [target]
        robot.active_batch_id = "approved-batch-123"
        return robot

    def test_power_loss_after_intent_before_first_click_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            robot = self.make_robot(directory)
            target = "chosen.user"
            journal, path = robot._journal(), robot._base()
            page = FakePage("unfollow", target=target)
            def power_lost(phase):
                robot._persist_action_click_intent(journal, path, target, phase)
                raise Interruption("power cut immediately after durable write")
            with patch("profile_actions.challenge_detected", return_value=False), \
                 patch("profile_actions.signed_in_handle", return_value="owner.name"):
                with self.assertRaises(Interruption):
                    perform_visible_action(page,target,"unfollow","owner.name",
                                           on_pre_click=power_lost)
            self.assertEqual(page.header.clicker.clicked, 0)
            self.assertEqual(page.menu.clicker.clicked, 0)
            cold = self.make_robot(directory)
            persisted = cold._journal()[target]
            self.assertEqual(persisted["status"],"review")
            self.assertEqual(persisted["issue"],"interrupted_action_uncertain")
            self.assertEqual(persisted["click_intent"]["phase"],"relationship_control")
            self.assertFalse(_preclick_no_action(persisted))
            history = cold.attempted_history({
                "owner":"owner.account","account":"ig-account","task":"unfollow"})
            self.assertIn(target, history["attempted_usernames"])
            # No cold restart may manufacture a new approved batch for a
            # possibly-clicked target even when the original Chrome is gone.
            with self.assertRaisesRegex(ValueError,"No untouched profiles remain"):
                cold.start({"owner":"owner.account","account":"ig-account",
                            "expected_handle":"owner.name","task":"unfollow",
                            "targets":[target],"batch_size":1,"protected":[],
                            "gap_seconds":10,"rest_minutes":0,
                            "followers_evidence":True,"confirmation":"unfollow:1"})

    def test_all_real_unfollow_phases_are_saved_before_each_click(self):
        with tempfile.TemporaryDirectory() as directory:
            target = "private.profile"
            robot = self.make_robot(directory, target=target)
            journal,path = robot._journal(),robot._base()
            page = FakePage("unfollow", target=target, private=True)
            phases = []
            def before_click(phase):
                counts = (page.header.clicker.clicked,page.menu.clicker.clicked,
                          page.dialog.clicker.clicked)
                phases.append((phase,counts))
                robot._persist_action_click_intent(journal,path,target,phase)
                self.assertEqual(json.loads(path.read_text())[target]
                                 ["click_intent"]["phase"],phase)
            with patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"):
                status,_ = perform_visible_action(page,target,"unfollow",
                                                  "owner.name",on_pre_click=before_click)
            self.assertEqual(status,"ok")
            self.assertEqual(phases, [
                ("relationship_control",(0,0,0)),
                ("unfollow_menu",(1,0,0)),
                ("private_unfollow_confirmation",(1,1,0)),
            ])
            self.assertEqual(journal[target]["click_intent"]["phases"],
                             ["relationship_control","unfollow_menu",
                              "private_unfollow_confirmation"])

    def test_cancel_confirmation_stages_and_duplicate_phase_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            target="requested.profile"
            robot=self.make_robot(directory,task="cancel",target=target)
            journal,path=robot._journal(),robot._base()
            page=FakePage("cancel",target=target)
            phases=[]
            def save(phase):
                phases.append(phase)
                robot._persist_action_click_intent(journal,path,target,phase)
            with patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"):
                status,_=perform_visible_action(page,target,"cancel","owner.name",
                                                on_pre_click=save)
            self.assertEqual(status,"ok")
            self.assertEqual(phases,["relationship_control","cancel_request_confirmation"])
            self.assertEqual(journal[target]["click_intent"]["phases"],phases)
            before=path.read_bytes()
            with self.assertRaisesRegex(ValueError,"already armed"):
                robot._persist_action_click_intent(journal,path,target,"relationship_control")
            self.assertEqual(before,path.read_bytes())

    def test_proven_no_click_does_not_create_false_intent(self):
        with tempfile.TemporaryDirectory() as directory:
            robot=self.make_robot(directory,task="cancel")
            page=FakePage("cancel")
            page.header.label="Follow"
            with patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"), \
                 patch("profile_actions.ACTION_CONTROL_WAIT_MS",30), \
                 patch("profile_actions.CANCEL_NO_REQUEST_MIN_WAIT_MS",0):
                status,_=perform_visible_action(
                    page,"target.user","cancel","owner.name",
                    on_pre_click=lambda phase:self.fail("No click intent permitted"))
            self.assertEqual(status,"already_not_requested")
            self.assertFalse(robot._base().exists())

    def test_disk_write_failure_prohibits_any_relationship_click(self):
        with tempfile.TemporaryDirectory() as directory:
            robot=self.make_robot(directory)
            target="chosen.user"
            journal,path=robot._journal(),robot._base()
            page=FakePage("unfollow",target=target)
            def refuse(phase):
                with patch("profile_actions._atomic_json",side_effect=OSError("disk full")):
                    robot._persist_action_click_intent(journal,path,target,phase)
            with patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"):
                with self.assertRaisesRegex(OSError,"disk full"):
                    perform_visible_action(page,target,"unfollow","owner.name",
                                           on_pre_click=refuse)
            self.assertEqual(page.header.clicker.clicked,0)
            self.assertFalse(path.exists())
            self.assertEqual(journal,{})

    def test_previous_safe_failure_remains_in_attempt_history_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            robot=self.make_robot(directory,task="cancel")
            target="chosen.user"
            journal,path=robot._journal(),robot._base()
            previous={"status":"blocked",
                      "message":"The active Instagram account cannot be verified. No action was performed."}
            journal[target]=previous
            _atomic_json(path,journal)
            record=robot._persist_action_click_intent(
                journal,path,target,"relationship_control")
            self.assertEqual(record["attempt_history"],[previous])
            self.assertFalse(_preclick_no_action(record))
            self.assertEqual(record["click_intent"]["batch_id"],"approved-batch-123")

if __name__=="__main__":
    unittest.main()
