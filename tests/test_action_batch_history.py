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

class FakeTargetTab:
    def __init__(self):
        self.closed = False

    def is_closed(self):
        return self.closed

    def close(self):
        self.closed = True


class FakeTabContext:
    def __init__(self):
        self.created = []

    def new_page(self):
        page = FakeTargetTab()
        self.created.append(page)
        return page


class ActionTabPoolTests(unittest.TestCase):
    def test_five_tabs_are_kept_separate_and_only_verified_actions_close(self):
        from profile_actions import ActionTabPool
        context = FakeTabContext()
        pool = ActionTabPool(context)
        a = pool.open("first.person")
        b = pool.open("second.person")
        c = pool.open("third.person")
        d = pool.open("fourth.person")
        e = pool.open("fifth.person")
        self.assertEqual(len(context.created), 5)
        self.assertIsNone(pool.open("sixth.person"))
        pool.record("first.person", "review")
        pool.record("second.person", "blocked")
        self.assertFalse(a.is_closed())
        self.assertFalse(b.is_closed())
        self.assertIsNone(pool.open("fourth.person"))
        pool.record("third.person", "ok")
        self.assertFalse(d.is_closed())
        self.assertFalse(e.is_closed())
        self.assertTrue(c.is_closed())
        self.assertFalse(a.is_closed())
        self.assertFalse(b.is_closed())
        fourth = pool.open("sixth.person")
        self.assertIsNotNone(fourth)
        self.assertEqual(set(x["username"] for x in pool.overview()),
                         {"first.person", "second.person", "fourth.person",
                          "fifth.person", "sixth.person"})
        self.assertIsNone(pool.open("sixth.person"))

    def test_manual_owner_close_frees_slot_without_confirming_result(self):
        from profile_actions import ActionTabPool
        context = FakeTabContext()
        pool = ActionTabPool(context)
        a = pool.open("unverified.one")
        a.close()  # Explicit manual close, never robot-confirmed success.
        self.assertEqual(pool.overview(), [])
        self.assertIsNotNone(pool.open("new.person"))
        self.assertFalse(pool.tabs["new.person"]["page"].is_closed())

    def test_explicit_skip_can_close_but_ambiguous_click_must_not(self):
        from profile_actions import ActionTabPool
        context = FakeTabContext()
        pool = ActionTabPool(context)
        skipped = pool.open("protected.person")
        uncertain = pool.open("possibly.clicked")
        pool.record("protected.person", "skipped")
        pool.record("possibly.clicked", "error")
        self.assertTrue(skipped.is_closed())
        self.assertFalse(uncertain.is_closed())
        self.assertEqual(pool.overview(), [
            {"username": "possibly.clicked", "status": "error"}])


class ActionBatchHistoryTests(unittest.TestCase):
    def _action(self, root):
        collector=Collector(root/"counts",root/"chrome")
        return ActionRobot(collector,root/"actions",root/"chrome")

    def _request(self, users, task="cancel"):
        return dict(owner="owner1",account="ig_account_1",expected_handle="owner.name",
                    task=task, targets=users,batch_size=len(users),
                    gap_seconds=10,rest_minutes=0,protected=[],
                    followers_evidence=task=="unfollow",
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

    def test_legacy_missing_following_is_a_known_safe_preclick_retry(self):
        from profile_actions import (
            _atomic_json, _preclick_no_action,
            LEGACY_MISSING_RELATIONSHIP_CONTROL, MISSING_RELATIONSHIP_CONTROL
        )
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            robot = self._action(root)
            historical = {
                "missing.old": {
                    "status": "review", "issue": "missing_profile_info",
                    "message": LEGACY_MISSING_RELATIONSHIP_CONTROL
                },
                "missing.new": {
                    "status": "review", "issue": "missing_profile_info",
                    "message": MISSING_RELATIONSHIP_CONTROL
                },
                "missing.diagnostic": {
                    "status": "review", "issue": "missing_profile_info",
                    "message": MISSING_RELATIONSHIP_CONTROL +
                        " Profile layout: main=yes, exact username=yes, named interactive controls=0, eligible controls=0. Nothing clicked."
                },
                "maybe.clicked": {
                    "status": "review", "issue": "pending_cancel_unverified",
                    "message": "Pending cancellation unverified after read-only refresh: Requested."
                },
                "unproven": {
                    "status": "review", "issue": "missing_profile_info",
                    "message": "Some unknown issue; it might already have been clicked."
                },
                "reported.no.click": {
                    "status": "review", "issue": "requires_manual_review",
                    "message": LEGACY_MISSING_RELATIONSHIP_CONTROL
                }
            }
            _atomic_json(robot._base_for("owner1", "ig_account_1", "unfollow"), historical)
            cold = self._action(root)
            scope = {"owner": "owner1", "account": "ig_account_1", "task": "unfollow"}
            attempts = cold.attempted_history(scope)["attempted_usernames"]
            self.assertEqual(attempts,
                             ["maybe.clicked", "reported.no.click", "unproven"])
            self.assertTrue(_preclick_no_action(historical["missing.old"]))
            self.assertTrue(_preclick_no_action(historical["missing.new"]))
            self.assertTrue(_preclick_no_action(historical["missing.diagnostic"]))
            self.assertFalse(_preclick_no_action(historical["maybe.clicked"]))
            self.assertFalse(_preclick_no_action(historical["unproven"]))
            self.assertFalse(_preclick_no_action(historical["reported.no.click"]))
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                # New explicit owner approval is required to rerun the
                # profiles where no relationship-changing click occurred.
                cold.start(self._request(["missing.old"], task="unfollow"))
                self.assertEqual(cold.targets, ["missing.old"])
                cold.start(self._request(["missing.new"], task="unfollow"))
                with self.assertRaisesRegex(ValueError, "already attempted"):
                    cold.start(self._request(["maybe.clicked"], task="unfollow"))

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
