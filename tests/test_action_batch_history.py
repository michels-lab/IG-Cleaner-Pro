"""Reopen / second-batch journal guards, no live Instagram requests."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import ActionRobot
from profile_counts_bridge import Collector

class ActionBatchHistoryTests(unittest.TestCase):
    def _action(self, root):
        collector=Collector(root/"counts",root/"chrome")
        return ActionRobot(collector,root/"actions",root/"chrome")

    def _request(self, users, task="cancel"):
        return dict(owner="owner1",account="ig_account_1",expected_handle="owner.name",
                    task=task, targets=users,batch_size=len(users),
                    gap_seconds=10,rest_minutes=0,protected=[],
                    confirmation=f"{task}:{len(users)}")

    def test_prior_two_batches_are_exposed_for_next_batch(self):
        with TemporaryDirectory() as temporary:
            robot=self._action(Path(temporary))
            request=self._request(["a.one"])
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value=False
                robot.start(request)
                for k in range(1, 81):
                    user=f"target.{k}"
                    status="review" if k==79 else "ok"
                    existing=robot._journal()
                    existing[user]={"status":status,"message":"Click may have occurred."}
                    from profile_actions import _atomic_json
                    _atomic_json(robot._base(),existing)
                robot.targets=["target.75","target.79","fresh.81"]
                state=robot.snapshot()
                self.assertIn("target.75",state["attempted_usernames"])
                self.assertIn("target.79",state["attempted_usernames"])
                self.assertNotIn("fresh.81",state["attempted_usernames"])
                self.assertEqual(len(state["attempted_usernames"]),80)
                # A new UI selection can exclude all 80 historical attempts,
                # not only the active batch displayed in snapshot.rows.
                with self.assertRaisesRegex(ValueError,"already attempted"):
                    robot.start(self._request(["target.79"]))
                robot.start(self._request(["fresh.81"]))
                self.assertEqual(robot.targets,["fresh.81"])

    def test_no_click_failure_is_retryable_but_uncertain_click_is_not(self):
        with TemporaryDirectory() as temporary:
            robot=self._action(Path(temporary))
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value=False
                robot.start(self._request(["pending.old"]))
                from profile_actions import _atomic_json
                _atomic_json(robot._base(),{
                    "pending.old":{"status":"blocked","message":
                        "The active Instagram account cannot be verified. No action was performed."},
                    "pending.clicked":{"status":"review","message":
                        "Pending cancellation unverified after read-only refresh: Requested."}
                })
                self.assertNotIn("pending.old",robot.snapshot()["attempted_usernames"])
                self.assertIn("pending.clicked",robot.snapshot()["attempted_usernames"])
                robot.start(self._request(["pending.old"]))
                with self.assertRaisesRegex(ValueError,"already attempted"):
                    robot.start(self._request(["pending.clicked"]))

    def test_read_prior_attempts_on_fresh_windows_launch_without_starting_worker(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            existing = self._action(root)
            from profile_actions import _atomic_json
            _atomic_json(existing._base_for("owner1", "ig_account_1", "cancel"), {
                "already.done": {"status": "ok"},
                "uncertain.click": {"status": "review", "message": "Click may have occurred."},
                "before.click": {"status": "blocked", "message":
                    "The active Instagram account cannot be verified. No action was performed."}
            })
            cold = self._action(root)
            self.assertEqual(cold.status, "idle")
            scope = {"owner": "owner1", "account": "ig_account_1", "task": "cancel"}
            data = cold.attempted_history(scope)
            self.assertEqual(data["attempted_usernames"], ["already.done", "uncertain.click"])
            self.assertIsNone(cold.worker)
            self.assertEqual(cold.targets, [])
            for changed in ({"account": "another_account"}, {"owner": "another_owner"},
                            {"task": "unfollow"}):
                other = {**scope, **changed}
                self.assertEqual(cold.attempted_history(other)["attempted_usernames"], [])
            with self.assertRaisesRegex(ValueError, "valid owner"):
                cold.attempted_history({**scope, "task": "invalid"})

    def test_journal_is_owner_and_task_scoped(self):
        with TemporaryDirectory() as temporary:
            robot=self._action(Path(temporary))
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value=False
                robot.start(self._request(["test.one"]))
                from profile_actions import _atomic_json
                _atomic_json(robot._base(),{"test.one":{"status":"ok"}})
                self.assertIn("test.one",robot.snapshot()["attempted_usernames"])
                robot.start(self._request(["test.one"],task="audit"))
                self.assertEqual(robot.snapshot()["attempted_usernames"],[])
                fresh=self._request(["test.one"])
                fresh["owner"]="another-owner"
                robot.start(fresh)
                self.assertEqual(robot.snapshot()["attempted_usernames"],[])

if __name__=="__main__":
    unittest.main()
