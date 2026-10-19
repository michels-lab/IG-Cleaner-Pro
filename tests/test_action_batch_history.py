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
    def test_ten_tabs_hold_unverified_and_close_only_confirmed(self):
        from profile_actions import ActionTabPool, MAX_ACTION_TABS
        self.assertEqual(MAX_ACTION_TABS, 10)
        context = FakeTabContext()
        pool = ActionTabPool(context)
        users = [f"profile.{n}" for n in range(1, 11)]
        tabs = {user: pool.open(user) for user in users}
        self.assertEqual(len(context.created), 10)
        self.assertTrue(all(tab is not None for tab in tabs.values()))
        self.assertIsNone(pool.open("profile.11"))
        pool.record("profile.1", "review")
        pool.record("profile.2", "blocked")
        pool.record("profile.3", "error")
        self.assertFalse(any(tabs[name].is_closed() for name in users))
        self.assertIsNone(pool.open("profile.11"),
                          "Unverified tabs must not be silently evicted")
        pool.record("profile.4", "ok")
        self.assertTrue(tabs["profile.4"].is_closed())
        self.assertFalse(tabs["profile.1"].is_closed())
        eleventh = pool.open("profile.11")
        self.assertIsNotNone(eleventh)
        self.assertIsNone(pool.open("profile.12"))
        self.assertEqual(len(pool.overview()), 10)
        self.assertEqual(
            {entry["username"] for entry in pool.overview()},
            (set(users) - {"profile.4"}) | {"profile.11"})
        self.assertEqual(pool.tabs["profile.1"]["status"], "review")
        self.assertEqual(pool.tabs["profile.2"]["status"], "blocked")
        self.assertEqual(pool.tabs["profile.3"]["status"], "error")

    def test_safe_no_click_closes_failed_profile_but_keeps_ambiguous_click(self):
        from profile_actions import ActionTabPool
        context = FakeTabContext()
        pool = ActionTabPool(context)
        no_click = pool.open("missing.following")
        uncertain = pool.open("possibly.changed")
        pool.record("missing.following", "review", safe_no_click=True)
        pool.record("possibly.changed", "review")
        self.assertTrue(no_click.is_closed())
        self.assertFalse(uncertain.is_closed())
        self.assertIsNotNone(pool.open("next.untouched"))

    def test_prefetch_uses_existing_tab_instead_of_duplicate(self):
        from profile_actions import ActionTabPool
        context = FakeTabContext()
        pool = ActionTabPool(context)
        prepared = pool.open("already.loading")
        self.assertIs(pool.prepared("already.loading"), prepared)
        pool.tabs["already.loading"]["status"] = "prefetched"
        self.assertEqual(len(context.created), 1)
        self.assertEqual(pool.overview()[0]["status"], "prefetched")
        pool.record("already.loading", "review")
        self.assertFalse(prepared.is_closed())
        self.assertIs(pool.prepared("already.loading"), prepared)
        pool.record("already.loading", "ok")
        self.assertIsNone(pool.prepared("already.loading"))
        self.assertTrue(prepared.is_closed())

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

    def test_real_runner_prepares_ten_urls_before_first_action(self):
        """Reproduces owner's failure: one ambiguous action must not limit prefill to 3."""
        import types
        from unittest.mock import MagicMock

        class Tab:
            def __init__(self):
                self.url = "about:blank"
                self.visited = []
                self.closed = False
            def goto(self, url, **kwargs):
                self.url = url
                self.visited.append(url)
            def locator(self, *_):
                return types.SimpleNamespace(count=lambda: 0)
            def is_closed(self):
                return self.closed
            def close(self):
                self.closed = True

        class Browser:
            def __init__(self):
                self.pages = [Tab()]
            def new_page(self):
                page = Tab()
                self.pages.append(page)
                return page
            def close(self):
                for p in self.pages:
                    p.close()

        with TemporaryDirectory() as temporary:
            browser = Browser()
            browser.pages[0].url = "https://www.instagram.com/"
            robot = self._action(Path(temporary))
            robot.owner = "owner1"
            robot.account = "ig_account_1"
            robot.handle = "owner.name"
            robot.task = "unfollow"
            robot.targets = [f"test.{n}" for n in range(12)]
            robot.rest_minutes = 0
            robot.min_delay_seconds = 0
            seen = []
            def one_uncertain_click(*args, **kwargs):
                # All ten page URLs must already exist when the first action starts.
                seen.append([p.url for p in browser.pages[1:]])
                robot.stop_event.set()
                return "review", "Final state is ambiguous; no click can be replayed."
            fake_playwright = types.SimpleNamespace(
                chromium=types.SimpleNamespace(
                    launch_persistent_context=lambda **kwargs: browser))
            fake_context = MagicMock()
            fake_context.__enter__.return_value = fake_playwright
            with patch.dict(sys.modules, {
                    "playwright": types.ModuleType("playwright"),
                    "playwright.sync_api": types.SimpleNamespace(
                        sync_playwright=lambda: fake_context)}), \
                 patch("profile_actions.preserve_instagram_auth_page", return_value=True), \
                 patch("profile_actions.challenge_detected", return_value=False), \
                 patch("profile_actions.signed_in_handle", return_value="owner.name"), \
                 patch("profile_actions.wait_required", return_value=0), \
                 patch("profile_actions.batch_wait", return_value=0), \
                 patch("profile_actions.perform_visible_action", side_effect=one_uncertain_click):
                robot._run()
            self.assertEqual(len(seen), 1)
            self.assertEqual(len(seen[0]), 10)
            self.assertEqual(
                seen[0], ["https://www.instagram.com/test." + str(n) + "/"
                          for n in range(10)])
            self.assertEqual(robot._journal()["test.0"]["status"], "review")
            self.assertNotIn("test.1", robot._journal())
            self.assertTrue(all(page.closed for page in browser.pages))

    def test_already_not_following_is_completed_not_an_unfollow_or_issue(self):
        """Keep a separate confirmed-no-follow outcome and move to the next target."""
        from profile_actions import _atomic_json, ActionTabPool
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            robot=self._action(root)
            request=self._request(["already.gone","still.following"],task="unfollow")
            with patch("profile_actions.threading.Thread") as thread:
                thread.return_value.is_alive.return_value=False
                robot.start(request)
                _atomic_json(robot._base(),{
                    "already.gone":{"status":"already_not_following",
                        "message":"Already not following. No Unfollow clicked.", "issue":""}
                })
                state=robot.snapshot()
                self.assertEqual(state["successful"],0,
                    "Already gone must never inflate successful Unfollows")
                self.assertEqual(state["already_not_following"],1)
                self.assertEqual(state["processed"],1)
                self.assertEqual(state["remaining"],1)
                self.assertEqual(state["issues"],[])
                self.assertIn("already.gone",state["attempted_usernames"],
                    "A completed no-follow profile must not receive action replay")
                review=robot.batch_review(request)["batch"]
                self.assertEqual(review["action_results"]["already.gone"]["status"],
                                 "already_not_following")
                approved=robot.approve_batch({**request,"batch_id":review["id"],
                    "confirmation":"reviewed:"+review["id"]})
                self.assertIn("already.gone",approved["approved_usernames"])
                self.assertIn("still.following",approved["unresolved_usernames"])
        context=FakeTabContext()
        pool=ActionTabPool(context)
        page=pool.open("already.gone")
        pool.record("already.gone","already_not_following")
        self.assertTrue(page.is_closed())
        self.assertIsNotNone(pool.open("still.following"))

    def test_automatic_attempt_never_counts_as_owner_review_before_confirm(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            robot=self._action(root)
            request=self._request(["verified.one","uncertain.two"])
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value=False
                robot.start(request)
                _atomic_json(robot._base(),{
                    "verified.one":{"status":"ok","message":"Follow confirmed"},
                    "uncertain.two":{"status":"review","message":
                        "Final state ambiguous. Do not repeat this action."}
                })
                snapshot=robot.snapshot()
                self.assertEqual(snapshot["successful"],1)
                self.assertIsNone(snapshot["review_batch"]["approved_at"])
                fresh=self._action(root)
                pending=fresh.batch_review(request)["batch"]
                self.assertEqual(pending["targets"],request["targets"])
                self.assertEqual(pending["action_results"]["verified.one"]["status"],"ok")
                self.assertEqual(pending["action_results"]["uncertain.two"]["status"],"review")
                with self.assertRaisesRegex(ValueError, "unapproved batch exists"):
                    robot.start(self._request(["different.person"]))
                with self.assertRaisesRegex(ValueError,"exact unapproved batch"):
                    robot.recheck_batch({**request,"batch_id":"wrong",
                                         "confirmation":"recheck:wrong"})
                with self.assertRaisesRegex(ValueError,"explicit batch confirmation"):
                    robot.approve_batch({**request,"batch_id":pending["id"],
                                          "confirmation":"reviewed:wrong"})
                # A read-only recheck must not overwrite the original action journal.
                robot.active_batch_id=pending["id"]
                robot._save_recheck_result("uncertain.two","review","Still ambiguous; no click")
                robot._save_recheck_result("verified.one","ok","Follow still visible; no click")
                before=robot._journal()
                result=robot.approve_batch({**request,"batch_id":pending["id"],
                                            "confirmation":"reviewed:"+pending["id"]})
                self.assertEqual(result["approved_usernames"],["verified.one"])
                self.assertEqual(result["unresolved_usernames"],["uncertain.two"])
                self.assertEqual(robot._journal(),before)
                self.assertIsNone(fresh.batch_review(request)["batch"])
                robot.start(self._request(["different.person"]))

    def test_resume_pending_cohort_executes_only_untouched_without_new_batch(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as tmp:
            robot = self._action(Path(tmp))
            req = self._request(["already.ok","uncertain.click","no.click","untouched.one","untouched.two"],task="unfollow")
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                robot.start(req)
                batch = robot.batch_review(req)["batch"]
                _atomic_json(robot._base(), {
                    "already.ok": {"status":"ok","message":"Follow confirmed."},
                    "uncertain.click":{"status":"review","message":"Final state ambiguous after click."},
                    "no.click":{"status":"review","issue":"profile_load_timeout",
                      "message":"No relationship control found. Waiting timed out: Following. No action clicked."}})
                with self.assertRaisesRegex(ValueError,"unapproved batch exists"):
                    robot.start(self._request(["replacement.new"],task="unfollow"))
                with self.assertRaisesRegex(ValueError,"exact saved ID"):
                    robot.start({**req,"batch_id":"wrong"})
                swapped = self._request(list(reversed(req["targets"])),task="unfollow")
                with self.assertRaisesRegex(ValueError,"exact saved ID"):
                    robot.start({**swapped,"batch_id":batch["id"]})
                with self.assertRaisesRegex(ValueError,"Saved batch changed"):
                    robot.start({**req,"account":"other","batch_id":batch["id"]})
                prior = robot._journal()
                robot.start({**req,"batch_id":batch["id"]})
                self.assertTrue(robot.continuing_batch)
                self.assertFalse(robot.review_only)
                self.assertEqual(robot.active_batch_id,batch["id"])
                self.assertEqual(robot.targets,req["targets"])
                self.assertEqual(robot._journal(),prior)
                self.assertEqual(len(robot._review_batches(req["owner"],req["account"],req["task"])),1)
                robot.review_only=True
                robot.status="paused"
                with self.assertRaisesRegex(ValueError,"Read-only verification cannot resume"):
                    robot.start(req,resume=True)

    def test_readonly_recheck_reuses_same_unapproved_batch_and_scope(self):
        with TemporaryDirectory() as temporary:
            root=Path(temporary)
            robot=self._action(root)
            request=self._request(["profile.one","profile.two"])
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value=False
                robot.start(request)
                entry=robot.batch_review(request)["batch"]
                payload={**request,"batch_id":entry["id"],
                         "confirmation":"recheck:"+entry["id"]}
                robot.recheck_batch(payload)
                self.assertTrue(robot.review_only)
                self.assertEqual(robot.active_batch_id,entry["id"])
                self.assertEqual(robot.targets,request["targets"])
                self.assertEqual(robot.snapshot()["attempted_usernames"],[])
                other={**payload,"account":"different-account"}
                with self.assertRaisesRegex(ValueError,"exact unapproved batch"):
                    robot.recheck_batch(other)
                # Even a recheck that verifies a formerly ambiguous action
                # never mutates the original journal.
                robot._save_recheck_result("profile.one","ok","Read-only Follow confirmed.")
                approved=robot.approve_batch({**request,"batch_id":entry["id"],
                                               "confirmation":"reviewed:"+entry["id"]})
                self.assertEqual(approved["approved_usernames"],["profile.one"])
                self.assertEqual(approved["unresolved_usernames"],["profile.two"])

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
                with self.assertRaisesRegex(ValueError,"unapproved batch exists"):
                    robot.start(self._request(["fresh.81"]))
                current = robot.batch_review({**request,"task":"cancel"})["batch"]
                robot.approve_batch({**request,"task":"cancel", "batch_id":current["id"],
                                     "confirmation":"reviewed:"+current["id"]})
                with self.assertRaisesRegex(ValueError,"No untouched profiles remain"):
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
                b=robot.batch_review(self._request(["pending.old"]))["batch"]
                robot.approve_batch({**self._request(["pending.old"]), "batch_id":b["id"],
                                     "confirmation":"reviewed:"+b["id"]})
                robot.start(self._request(["pending.old"]))
                with self.assertRaisesRegex(ValueError,"unapproved batch exists"):
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
                request=self._request(["missing.old"],task="unfollow")
                cold.start(request)
                self.assertEqual(cold.targets, ["missing.old"])
                b=cold.batch_review(request)["batch"]
                cold.approve_batch({**request,"batch_id":b["id"],
                                    "confirmation":"reviewed:"+b["id"]})
                cold.start(self._request(["missing.new"],task="unfollow"))
                with self.assertRaisesRegex(ValueError, "unapproved batch exists"):
                    cold.start(self._request(["maybe.clicked"],task="unfollow"))

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
