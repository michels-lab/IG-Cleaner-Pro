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

    def test_finished_cohort_releases_unused_prefetched_tabs_not_uncertain_actions(self):
        from profile_actions import ActionTabPool
        pool=ActionTabPool(FakeTabContext())
        staged=[pool.open("staged."+str(i)) for i in range(8)]
        for i in range(8):
            pool.tabs["staged."+str(i)]["status"]="prefetched"
        uncertain=pool.open("maybe.clicked")
        pool.record("maybe.clicked","review")
        blocked=pool.open("manual.challenge")
        pool.record("manual.challenge","blocked")
        pool.close_unacted_prefetches()
        self.assertTrue(all(page.is_closed() for page in staged),
                        "Eight untouched prefetched tabs must not hold robot in review loop")
        self.assertFalse(uncertain.is_closed(),"Potential relationship action remains visible")
        self.assertFalse(blocked.is_closed(),"Account challenge remains for human attention")
        self.assertEqual({row["username"] for row in pool.overview()},
                         {"maybe.clicked","manual.challenge"})

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


def _read_json_for_test(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ActionBatchHistoryTests(unittest.TestCase):
    def setUp(self):
        # These history-only tests deliberately replace threading.Thread with
        # a mock whose start() NEVER invokes the worker's finally block.
        # Mock the OS admission lease here; actual Windows/Linux process
        # locking and release are validated in test_robot_interlock.py.
        lease_patcher = patch("profile_actions.ActionLease")
        lease_patcher.start()
        self.addCleanup(lease_patcher.stop)

    def _action(self, root):
        collector=Collector(root/"counts",root/"chrome")
        return ActionRobot(collector,root/"actions",root/"chrome")

    def _request(self, users, task="cancel"):
        return dict(owner="owner1",account="ig_account_1",expected_handle="owner.name",
                    task=task, targets=users,batch_size=len(users),
                    gap_seconds=10,rest_minutes=0,protected=[],
                    followers_evidence=task=="unfollow",
                    confirmation=f"{task}:{len(users)}")

    def test_public_robot_find_owner_across_tabs_no_conflicting_identity(self):
        from unittest.mock import Mock
        from profile_actions import _find_verified_owner_tab

        def tab(url, closed=False):
            page = Mock()
            page.url = url
            page.is_closed.return_value = closed
            return page

        login = tab("https://www.instagram.com/accounts/login/")
        owner = tab("https://www.instagram.com/owner.name/")
        outsider = tab("https://not-instagram.example/fake/")
        closed = tab("https://www.instagram.com/closed.owner/", closed=True)
        insecure = tab("http://www.instagram.com/insecure/")
        mismatch = tab("https://www.instagram.com/other.owner/")

        def signed(page):
            return {
                owner: "OWNER.Name",
                mismatch: "other.owner",
                outsider: "other.owner",
                closed: "other.owner",
                insecure: "other.owner",
            }.get(page)

        with patch("profile_actions.signed_in_handle", side_effect=signed) as identity:
            found, wrong = _find_verified_owner_tab(
                [login, outsider, closed, insecure, owner], "owner.name")
            self.assertIs(found, owner)
            self.assertIsNone(wrong)
            self.assertEqual(identity.call_count, 2, "Only HTTPS Instagram tabs observed")
            identity.reset_mock()
            found, wrong = _find_verified_owner_tab(
                [login, owner, mismatch], "owner.name")
            self.assertIsNone(found)
            self.assertEqual(wrong, "other.owner")
            identity.reset_mock()
            found, wrong = _find_verified_owner_tab([login], "owner.name")
            self.assertIsNone(found)
            self.assertIsNone(wrong)
        for page in (login, owner, outsider, closed, insecure, mismatch):
            page.goto.assert_not_called()
            page.locator.assert_not_called()
            page.click.assert_not_called()

    def test_public_robot_manual_login_does_not_wait_forever_or_fake_actions(self):
        """No Developer Edition: normal Windows robot times out with honest status."""
        import contextlib
        from types import ModuleType
        from unittest.mock import Mock

        from profile_actions import _same_instagram_owner
        self.assertTrue(_same_instagram_owner("OWNER.Name", "owner.name"))
        self.assertTrue(_same_instagram_owner("owner.name", "OWNER.NAME"))
        self.assertFalse(_same_instagram_owner("other.owner", "owner.name"))
        self.assertFalse(_same_instagram_owner(None, "owner.name"))
        self.assertFalse(_same_instagram_owner("", "owner.name"))

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            robot = self._action(root)
            robot.owner, robot.account = "owner1", "ig_account_1"
            robot.handle, robot.task = "owner.name", "unfollow"
            robot.targets = ["test.profile"]
            page = Mock()
            page.url = "https://www.instagram.com/accounts/login/"
            page.is_closed.return_value = False
            browser = Mock()
            browser.pages = [page]
            pw = Mock()
            pw.chromium.launch_persistent_context.return_value = browser
            fake = ModuleType("playwright.sync_api")
            fake.sync_playwright = lambda: contextlib.nullcontext(pw)
            with patch.dict(sys.modules, {"playwright.sync_api": fake}), \
                 patch("profile_actions.preserve_instagram_auth_page",
                       return_value=True), \
                 patch("profile_actions.challenge_detected",
                       return_value=False), \
                 patch("profile_actions.signed_in_handle",
                       return_value=None), \
                 patch("profile_actions.time.monotonic",
                       side_effect=[0, 250]):
                robot._run()
            self.assertEqual(robot.status, "blocked")
            self.assertIn("within four minutes", robot.message)
            self.assertIn("no profiles were unfollowed or cancelled",
                          robot.message)
            browser.close.assert_called_once()
            self.assertFalse(robot._base().exists(),
                             "Login failure cannot create an action journal")
            page.goto.assert_not_called()

    def test_public_robot_rejects_different_owner_without_click_or_journal(self):
        import contextlib
        from types import ModuleType
        from unittest.mock import Mock
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            robot=self._action(root)
            robot.owner,robot.account="owner1","ig_account_1"
            robot.handle,robot.task="owner.name","cancel"
            robot.targets=["sample.target"]
            page=Mock()
            page.url="https://www.instagram.com/accounts/login/"
            page.is_closed.return_value=False
            browser=Mock()
            browser.pages=[page]
            pw=Mock()
            pw.chromium.launch_persistent_context.return_value=browser
            fake=ModuleType("playwright.sync_api")
            fake.sync_playwright=lambda:contextlib.nullcontext(pw)
            with patch.dict(sys.modules,{"playwright.sync_api":fake}), \
                 patch("profile_actions.preserve_instagram_auth_page",
                       return_value=True), \
                 patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",
                       return_value="other.owner"):
                robot._run()
            self.assertEqual(robot.status,"blocked")
            self.assertIn("other.owner",robot.message)
            self.assertFalse(robot._base().exists())
            browser.close.assert_called_once()

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
            def bring_to_front(self):
                self.was_focused = True
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
            robot.tab_flow = "ten_tabs"  # legacy mode remains explicit
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
            self.assertTrue(browser.pages[1].was_focused,
                            "The first Instagram target tab must receive focus before its action")
            self.assertEqual(len(seen[0]), 10)
            self.assertEqual(
                seen[0], ["https://www.instagram.com/test." + str(n) + "/"
                          for n in range(10)])
            self.assertEqual(robot._journal()["test.0"]["status"], "review")
            self.assertNotIn("test.1", robot._journal())
            self.assertTrue(all(page.closed for page in browser.pages))

    def test_real_runner_sequential_opens_only_current_before_first_action(self):
        """Sequential: an unprocessed future target must never be opened."""
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
            def bring_to_front(self):
                self.was_focused = True
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
                # Future targets must not open before the first action is processed.
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
            self.assertTrue(browser.pages[1].was_focused,
                            "The first Instagram target tab must receive focus before its action")
            self.assertEqual(len(seen[0]), 1)
            self.assertEqual(
                seen[0], ["https://www.instagram.com/test." + str(n) + "/"
                          for n in range(1)])
            self.assertEqual(robot._journal()["test.0"]["status"], "review")
            self.assertNotIn("test.1", robot._journal())
            self.assertTrue(all(page.closed for page in browser.pages))

    def test_armed_click_with_familiar_missing_profile_issue_stops_wave(self):
        """No second profile may receive an action after an uncertain first click.

        Real worker control flow, local fake Chromium pages and durable journal;
        this fixture never connects to Instagram.
        """
        import types
        from unittest.mock import MagicMock
        from profile_actions import ActionTabPool

        class Tab:
            def __init__(self):
                self.url, self.closed = "about:blank", False
            def goto(self, url, **kwargs):
                self.url = url
            def bring_to_front(self):
                pass
            def locator(self, *_):
                return types.SimpleNamespace(count=lambda: 0)
            def is_closed(self):
                return self.closed
            def close(self):
                self.closed = True

        class Browser:
            def __init__(self):
                self.pages = [Tab()]
                self.pages[0].url = "https://www.instagram.com/"
            def new_page(self):
                page = Tab()
                self.pages.append(page)
                return page
            def close(self):
                for page in self.pages:
                    page.close()

        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            robot.owner, robot.account = "owner1", "ig_account_1"
            robot.handle, robot.task = "owner.name", "unfollow"
            robot.targets = ["uncertain.first", "must.not.click", "third.unacted"]
            robot.active_batch_id = "approved-click-barrier"
            robot.rest_minutes, robot.min_delay_seconds = 0, 0
            browser = Browser()
            calls = []

            def ambiguous_after_possible_click(page, username, *args, **kwargs):
                calls.append(username)
                if username == "uncertain.first":
                    kwargs["on_pre_click"]("relationship_control")
                    return "review", "The profile does not show Following."
                robot.stop_event.set()
                return "ok", "Action confirmed: Follow."

            # The original worker intentionally holds ambiguous tabs open
            # for owner review. End that final wait, without influencing the
            # earlier decision whether to click a SECOND account.
            real_close = ActionTabPool.close_unacted_prefetches
            def complete_fixture(pool):
                real_close(pool)
                robot.stop_event.set()

            fake_pw = types.SimpleNamespace(chromium=types.SimpleNamespace(
                launch_persistent_context=lambda **kwargs: browser))
            fake_ctx = MagicMock()
            fake_ctx.__enter__.return_value = fake_pw
            with patch.dict(sys.modules, {
                    "playwright": types.ModuleType("playwright"),
                    "playwright.sync_api": types.SimpleNamespace(
                        sync_playwright=lambda: fake_ctx)}), \
                 patch("profile_actions.preserve_instagram_auth_page",return_value=True), \
                 patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"), \
                 patch("profile_actions.wait_required",return_value=0), \
                 patch("profile_actions.batch_wait",return_value=0), \
                 patch("profile_actions.ActionTabPool.close_unacted_prefetches",
                       autospec=True,side_effect=complete_fixture), \
                 patch("profile_actions.perform_visible_action",
                       side_effect=ambiguous_after_possible_click):
                robot._run()
            self.assertEqual(calls, ["uncertain.first"],
                             "A durable possible-click must stop this ten-tab wave")
            journal = robot._journal()
            self.assertEqual(journal["uncertain.first"]["status"], "review")
            self.assertEqual(journal["uncertain.first"]["issue"], "missing_profile_info")
            self.assertEqual(journal["uncertain.first"]["click_intent"]["phase"],
                             "relationship_control")
            self.assertFalse("must.not.click" in journal)
            self.assertFalse("third.unacted" in journal)
            self.assertTrue(all(tab.closed for tab in browser.pages))

    def test_forty_profiles_run_as_four_complete_ten_tab_waves(self):
        """Real _run state machine: 10 prepared -> ordered verify/close -> next 10."""
        from unittest.mock import MagicMock
        import types
        import sys
        from unittest.mock import patch

        class Tab:
            def __init__(self):
                self.url, self.closed, self.focused = "about:blank", False, False
            def goto(self, url, **kwargs):
                self.url = url
            def locator(self, *_):
                return types.SimpleNamespace(count=lambda: 0)
            def is_closed(self):
                return self.closed
            def close(self):
                self.closed = True
            def bring_to_front(self):
                self.focused = True

        class Browser:
            def __init__(self):
                self.pages = [Tab()]
                self.pages[0].url = "https://www.instagram.com/"
            def new_page(self):
                page = Tab()
                self.pages.append(page)
                return page
            def close(self):
                for page in self.pages:
                    page.close()

        with TemporaryDirectory() as temporary:
            browser = Browser()
            robot = self._action(Path(temporary))
            robot.owner, robot.account = "owner1", "ig_account_1"
            robot.handle, robot.task = "owner.name", "unfollow"
            robot.targets = ["wave." + str(i) for i in range(40)]
            robot.tab_flow = "ten_tabs"  # four complete explicit legacy waves
            robot.rest_minutes, robot.min_delay_seconds = 0, 0
            observations = []
            def real_verified_action(page, username, *_args, **_kwargs):
                self.assertTrue(page.focused, "Current target tab must have focus")
                live=[p.url for p in browser.pages[1:] if not p.is_closed()]
                observations.append((username, live))
                self.assertIn("https://www.instagram.com/"+username+"/", live)
                return "ok", "Action confirmed: visible Follow after Unfollow."
            fake_playwright = types.SimpleNamespace(chromium=types.SimpleNamespace(
                launch_persistent_context=lambda **kwargs: browser))
            fake_context = MagicMock()
            fake_context.__enter__.return_value = fake_playwright
            with patch.dict(sys.modules, {
                   "playwright": types.ModuleType("playwright"),
                   "playwright.sync_api": types.SimpleNamespace(
                       sync_playwright=lambda: fake_context)}), \
                 patch("profile_actions.preserve_instagram_auth_page",return_value=True), \
                 patch("profile_actions.challenge_detected",return_value=False), \
                 patch("profile_actions.signed_in_handle",return_value="owner.name"), \
                 patch("profile_actions.wait_required",return_value=0), \
                 patch("profile_actions.batch_wait",return_value=0), \
                 patch("profile_actions.perform_visible_action",side_effect=real_verified_action):
                robot._run()
            self.assertEqual(len(observations),40)
            for batch in range(4):
                names=["wave."+str(i) for i in range(batch*10,(batch+1)*10)]
                expected=["https://www.instagram.com/"+name+"/" for name in names]
                for step in range(10):
                    user,live=observations[batch*10+step]
                    self.assertEqual(user,names[step])
                    self.assertEqual(live,expected[step:],
                        "Only the current ten tabs may remain open, never next-wave prefetch")
            self.assertEqual(robot.snapshot()["successful"],40)
            self.assertTrue(all(p.closed for p in browser.pages))

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
                # The first result does not permit closing out the untouched
                # second target; the exact saved cohort must remain resumable.
                with self.assertRaisesRegex(ValueError, "untouched profiles"):
                    robot.approve_batch({**request,"batch_id":review["id"],
                        "confirmation":"reviewed:"+review["id"]})
                self.assertIsNotNone(robot.batch_review(request)["batch"])
                _atomic_json(robot._base(), {
                    **robot._journal(),
                    "still.following":{"status":"review",
                        "message":"Ambiguous previous action; do not retry."}
                })
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

    def test_cancel_paused_batch_preserves_all_click_evidence_and_unlocks_new_task(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            old = self._request(["already.ok", "possible.click", "untouched.one"],
                                task="cancel")
            with patch("profile_actions.threading.Thread") as thread:
                thread.return_value.is_alive.return_value = False
                robot.start(old)
                batch = robot.batch_review(old)["batch"]
                journal = {
                    "already.ok": {"status": "ok", "at": "2026-10-23T08:20:00Z",
                                   "message": "Verified no active request"},
                    "possible.click": {"status": "review", "issue": "interrupted_action_uncertain",
                                       "at": "2026-10-23T08:21:00Z",
                                       "click_intent": {"batch_id": batch["id"], "task": "cancel",
                                                        "phase": "request_cancel",
                                                        "written_at": "2026-10-23T08:20:59Z",
                                                        "requires_manual_review": True},
                                       "message": "Click may have been sent"}
                }
                _atomic_json(robot._base(), journal)
                original = robot._base().read_bytes()
                cancel = {**old, "batch_id": batch["id"],
                          "confirmation": "cancel-batch:" + batch["id"]}
                with self.assertRaisesRegex(ValueError, "Confirm the exact saved cohort"):
                    robot.cancel_current_batch({**cancel, "confirmation": "wrong"})
                with self.assertRaisesRegex(ValueError, "active owner"):
                    robot.cancel_current_batch({**cancel, "account": "other.account"})
                result = robot.cancel_current_batch(cancel)
                self.assertEqual(result["status"], "cancelled")
                self.assertFalse(result["cancel_requested"])
                self.assertIsNone(robot.batch_review(old)["batch"])
                self.assertEqual(robot._base().read_bytes(), original,
                                 "Cancelling must never edit the action journal")
                saved = robot._review_batches(old["owner"], old["account"], old["task"])[-1]
                self.assertEqual(saved["deferred_reason"], "owner_cancelled")
                self.assertEqual(saved["deferred_action_recorded"], 2)
                self.assertEqual(saved["deferred_untouched"], 1)
                self.assertFalse(saved["marked_reviewed"])
                self.assertIn("possible.click",
                              robot.attempted_history(old)["attempted_usernames"])
                # The cancelled task no longer monopolizes the normal robot.
                next_job = self._request(["fresh.person"], task="unfollow")
                started = robot.start(next_job)
                self.assertEqual(started["task"], "unfollow")

    def test_cancel_during_cooldown_sets_stop_before_archival(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as tmp:
            robot = self._action(Path(tmp))
            request = self._request(["possible.click", "waiting.two"], task="unfollow")
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = True
                robot.start(request)
                batch = robot.batch_review(request)["batch"]
                _atomic_json(robot._base(), {
                    "possible.click": {"status": "review",
                      "issue": "interrupted_action_uncertain",
                      "at": "2026-10-23T08:21:00Z",
                      "message": "Maybe changed"}
                })
                original = robot._base().read_bytes()
                response = robot.cancel_current_batch({
                    **request, "batch_id": batch["id"],
                    "confirmation": "cancel-batch:" + batch["id"]})
                self.assertEqual(response["status"], "cancelling")
                self.assertTrue(response["running"])
                self.assertTrue(robot.stop_event.is_set())
                self.assertIsNotNone(robot.batch_review(request)["batch"],
                                     "Never archive an in-flight write prematurely")
                with self.assertRaisesRegex(ValueError, "Owner stopped"):
                    robot._persist_action_click_intent(
                        robot._journal(), robot._base(), "waiting.two",
                        "unfollow_graphql")
                # Simulate completion of the worker/browser cleanup callback.
                with robot.lock:
                    robot._finish_owner_cancel_locked()
                worker.return_value.is_alive.return_value = False
                self.assertEqual(robot.snapshot()["status"], "cancelled")
                self.assertIsNone(robot.batch_review(request)["batch"])
                self.assertEqual(robot._base().read_bytes(), original)

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
                robot._save_recheck_result("profile.two","review","Read-only check still uncertain.")
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
                # Historical filtering is independent of batch approval; mark
                # the initial member as attempted before closing the cohort.
                _atomic_json(robot._base(), {**robot._journal(),
                    "a.one":{"status":"review","message":"Prior uncertain result."}})
                robot.approve_batch({**request,"task":"cancel", "batch_id":current["id"],
                                     "confirmation":"reviewed:"+current["id"]})
                with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
                    robot.start(self._request(["target.79"]))
                robot.start(self._request(["fresh.81"]))
                self.assertEqual(robot.targets,["fresh.81"])

    def test_new_cohort_never_reopens_any_previous_journal_target(self):
        """Previously visited is different from successfully unfollowed."""
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            scope = self._request(["fresh.one"], task="unfollow")
            source = robot._base_for(scope["owner"], scope["account"], scope["task"])
            original = {
                "confirmed.unfollow": {"status": "ok",
                                       "message": "Action confirmed: Follow."},
                "already.gone": {"status": "already_not_following"},
                "no.click": {"status": "review", "issue": "profile_load_timeout",
                             "message": __import__("profile_actions").MISSING_RELATIONSHIP_CONTROL +
                                 " Waiting timed out: Following. No action clicked."},
                "possibly.clicked": {"status": "review",
                                     "message": "Final verification uncertain."},
            }
            _atomic_json(source, original)
            history = robot.attempted_history(scope)
            self.assertEqual(history["visited_usernames"], sorted(original))
            self.assertNotIn("no.click", history["attempted_usernames"],
                             "Old attempted-only filter caused repeat visits")
            fresh = self._action(Path(temporary))
            self.assertEqual(fresh.attempted_history(scope)["visited_usernames"], sorted(original))
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                for username in original:
                    with self.subTest(username=username), self.assertRaisesRegex(
                            ValueError, "previously opened/reviewed"):
                        fresh.start(self._request([username], task="unfollow"))
                self.assertFalse(worker.called, "No Chrome job must start for old targets")
                self.assertEqual(_read_json_for_test(source), original)
                fresh.start(scope)
                self.assertEqual(fresh.targets, ["fresh.one"])

    def test_new_cohort_blocks_crashed_navigation_without_false_unfollow(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            robot = self._action(root)
            robot.owner, robot.account = "owner1", "ig_account_1"
            robot.task, robot.active_batch_id = "unfollow", "previous-cohort"
            robot._reserve_target_visit("opened.but.not.actioned")
            path = robot._target_visits_file_for(robot.owner, robot.account, robot.task)
            marks = _read_json_for_test(path)
            self.assertEqual(marks["opened.but.not.actioned"]["state"],
                "target_navigation_reserved_not_action_confirmed")
            self.assertFalse(robot._base().exists(),
                             "Target visit must never impersonate a relationship result")
            scope = self._request(["opened.but.not.actioned"], task="unfollow")
            history = self._action(root).attempted_history(scope)
            self.assertEqual(history["visited_usernames"], ["opened.but.not.actioned"])
            self.assertEqual(history["attempted_usernames"], [])
            with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
                self._action(root).start(scope)
            self.assertFalse(robot._base().exists())
            # Malformed visit evidence fails closed instead of losing exclusions.
            path.write_text("{not JSON", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Corrupted robot activity journal"):
                self._action(root).attempted_history(scope)
            with self.assertRaisesRegex(ValueError, "Corrupted robot activity journal"):
                self._action(root).start(scope)

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
                # New cohorts exclude old inspected profiles even when no click.
                # The original saved cohort can still continue its exact approved
                # set or use explicit read-only recheck.
                with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
                    robot.start(self._request(["pending.old"]))
                with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
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
                # New cohorts exclude all inspected profiles, including
                # previously harmless no-click observations. Continue is only
                # allowed on the original saved, still-open cohort.
                for user in ("missing.old", "missing.new",
                             "missing.diagnostic", "maybe.clicked"):
                    with self.subTest(user=user), self.assertRaisesRegex(
                            ValueError, "previously opened/reviewed"):
                        cold.start(self._request([user], task="unfollow"))
                worker.assert_not_called()

    def test_new_forty_after_saved_ten_preserves_all_history_and_never_autoclicks(self):
        """Real owner case: 10 saved / 40 desired / 5 attempted / no Chrome start."""
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            original = [f"saved.{i:02d}" for i in range(10)]
            payload = self._request(original, task="cancel")
            with patch("profile_actions.threading.Thread") as thread:
                thread.return_value.is_alive.return_value = False
                robot.start(payload)
                before = robot.batch_review(payload)["batch"]
                self.assertEqual(len(before["targets"]), 10)
                journal = {original[0]: {
                    "status": "review",
                    "message": "An uncertain Request click; never replay.",
                    "click_intent": {"phase": "relationship_control",
                                     "outcome_recorded": False}},
                    original[1]: {"status": "ok", "message": "Confirmed existing action"},
                    original[2]: {"status": "blocked", "message":
                                   "Instagram session verification failed before the first click. No action performed."},
                    original[3]: {"status": "review", "message":
                                   "Layout was not verifiable; click may have occurred.",
                                   "click_intent": {"phase": "relationship_control"}},
                    original[4]: {"status": "already_not_requested",
                                   "message": "Follow verified; no Cancel Request clicked"}}
                _atomic_json(robot._base(), journal)
                preserved = robot._base().read_bytes()
                result = robot.set_aside_incomplete_batch({
                    **payload, "batch_id": before["id"], "desired_batch_size": 40,
                    "confirmation": "new-batch:" + before["id"] + ":40"
                })
                self.assertEqual(result["status"], "saved_cohort_set_aside_for_new_batch")
                self.assertEqual(result["saved_size"], 10)
                self.assertEqual(result["requested_new_size"], 40)
                self.assertFalse(result["marked_reviewed"])
                self.assertEqual(result["approved_usernames"], [])
                self.assertIn(original[2], result["reusable_usernames"])
                self.assertIn(original[5], result["reusable_usernames"])
                self.assertNotIn(original[0], result["reusable_usernames"])
                self.assertNotIn(original[3], result["reusable_usernames"])
                self.assertNotIn(original[4], result["reusable_usernames"])
                self.assertEqual(preserved, robot._base().read_bytes(),
                    "Set aside must not modify or overwrite possible-click journal bytes")
                self.assertIsNone(robot.batch_review(payload)["batch"])
                archived = robot._review_batches("owner1", "ig_account_1", "cancel")
                match = next(x for x in archived if x["id"] == before["id"])
                self.assertEqual(match["targets"], original)
                self.assertEqual(match["requested_next_batch_size"], 40)
                self.assertEqual(match["deferred_reason"], "owner_new_batch_explicit")
                self.assertFalse(match["marked_reviewed"])
                self.assertFalse(bool(match.get("approved_at")))
                with self.assertRaisesRegex(ValueError, "Saved cohort changed"):
                    robot.set_aside_incomplete_batch({
                        **payload, "batch_id": before["id"], "desired_batch_size": 40,
                        "confirmation": "new-batch:" + before["id"] + ":40"})
                # A fresh 40-person batch can now be PREPARED, but no worker
                # action is run by this handoff; old clicked usernames absent.
                safe = result["reusable_usernames"]
                # Saved-cohort handoff preserves historically no-click records,
                # but a completely NEW automatic cohort must NOT reopen them.
                with self.assertRaisesRegex(ValueError, "previously opened/reviewed"):
                    robot.start(self._request(safe[:1], task="cancel"))
                never_opened = [u for u in safe if u not in journal]
                additions = [f"new.{i:02d}" for i in range(40-len(never_opened))]
                next_request = self._request(never_opened + additions, task="cancel")
                robot.start(next_request)
                targets = robot.batch_review(next_request)["batch"]["targets"]
                self.assertEqual(len(targets), 40)
                self.assertFalse(set(targets) & set(journal),
                    "No inspected/no-click or ambiguous old target can enter new cohort")

    def test_new_batch_rejects_unapproved_owner_size_and_running_workers(self):
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            payload = self._request(["old.one","old.two"], task="cancel")
            with patch("profile_actions.threading.Thread") as thread:
                thread.return_value.is_alive.return_value = False
                robot.start(payload)
                saved = robot.batch_review(payload)["batch"]
                request = {**payload, "batch_id": saved["id"],
                           "desired_batch_size": 40,
                           "confirmation": "new-batch:" + saved["id"] + ":40"}
                with self.assertRaisesRegex(ValueError, "exact saved batch"):
                    robot.set_aside_incomplete_batch({**request,
                        "confirmation": "new-batch:wrong-batch:40"})
                with self.assertRaisesRegex(ValueError, "workspace"):
                    robot.set_aside_incomplete_batch({**request,
                        "account": "somebody-else"})
                robot.worker.is_alive.return_value = True
                with self.assertRaisesRegex(ValueError, "Chrome robots"):
                    robot.set_aside_incomplete_batch(request)
                robot.worker.is_alive.return_value = False
                self.assertEqual(robot.batch_review(payload)["batch"]["targets"],
                                 ["old.one","old.two"])

    def test_replan_only_truly_absent_or_proven_preclick_and_preserves_evidence(self):
        """A saved malformed entry cannot be recycled into an approved 10->2 wave."""
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            targets = [
                "bad.type", "null.value", "empty.record", "missing.status",
                "null.intent", "uncertain.clicked", "safe.no.click",
                "fresh.one", "fresh.two", "fresh.three",
            ]
            request = self._request(targets, task="unfollow")
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                robot.start(request)
                batch = robot.batch_review(request)["batch"]
                before = {
                    "bad.type": 123,
                    "null.value": None,
                    "empty.record": {},
                    "missing.status": {"message": "no status or phase"},
                    "null.intent": {"status": "blocked",
                                    "message": "Instagram session verification failed before the first click. No action performed.",
                                    "click_intent": None},
                    "uncertain.clicked": {"status": "review",
                                          "click_intent": {"phase": "relationship_control",
                                                           "outcome_recorded": False}},
                    "safe.no.click": {"status": "blocked",
                                      "message": "Instagram session verification failed before the first click. No action performed."},
                }
                _atomic_json(robot._base(), before)
                saved = robot._base().read_bytes()
                # Before resizing, original saved cohort remains inspectable,
                # including corrupt entries, without interpreting them as idle.
                unsafe_view = robot.batch_review(request)["batch"]
                self.assertEqual(
                    unsafe_view["action_results"]["bad.type"]["status"], "review")
                self.assertFalse(
                    unsafe_view["action_results"]["bad.type"]["safe_no_click"])
                self.assertIn("unrecognized evidence",
                              unsafe_view["action_results"]["null.intent"]["message"])
                payload = {**request, "batch_id": batch["id"],
                           "desired_batch_size": 2,
                           "confirmation": "replan-size:" + batch["id"] + ":2"}
                result = robot.replan_incomplete_batch(payload)
                self.assertEqual(result["active_size"], 2)
                self.assertEqual(result["reusable_after_active"], 2)
                self.assertEqual(result["action_recorded"], 6)
                replanned = robot.batch_review(request)["batch"]
                self.assertEqual(replanned["targets"],
                                 ["safe.no.click", "fresh.one"])
                self.assertEqual(replanned["carryover_targets"],
                                 ["fresh.two", "fresh.three"])
                self.assertEqual(replanned["original_targets"], targets)
                self.assertIsNone(replanned["approved_at"])
                self.assertEqual(saved, robot._base().read_bytes())
                self.assertEqual(result["marked_reviewed"], False)
                # A stale 10-profile request cannot replace the newly
                # replanned two-profile active cohort; original evidence lives
                # in the unchanged journal and original_targets snapshot.
                with self.assertRaisesRegex(ValueError, "unapproved batch exists"):
                    robot.start({**request, "batch_id": batch["id"]})

    def test_malformed_terminal_must_not_be_approved_as_reviewed(self):
        from profile_actions import _atomic_json
        with TemporaryDirectory() as temporary:
            robot = self._action(Path(temporary))
            request = self._request(["bad.terminal", "valid.terminal"], task="unfollow")
            with patch("profile_actions.threading.Thread") as worker:
                worker.return_value.is_alive.return_value = False
                robot.start(request)
                batch = robot.batch_review(request)["batch"]
                _atomic_json(robot._base(), {
                    "bad.terminal": {"status": "ok", "click_intent": None},
                    "valid.terminal": {"status": "already_not_following",
                                      "message": "Exact Follow, no click"},
                })
                with self.assertRaisesRegex(ValueError, "Invalid saved action evidence"):
                    robot.approve_batch({
                        **request, "batch_id": batch["id"],
                        "confirmation": "reviewed:" + batch["id"],
                    })
                after = robot.batch_review(request)["batch"]
                self.assertIsNone(after["approved_at"])
                self.assertEqual(after["action_results"]["bad.terminal"]["status"], "review")
                self.assertFalse(after["action_results"]["bad.terminal"]["safe_no_click"])

    def test_missing_following_uses_readonly_structured_diagnosis_no_action(self):
        from unittest.mock import Mock
        from profile_actions import perform_visible_action, _preclick_no_action
        from profile_actions import MISSING_RELATIONSHIP_CONTROL

        page = Mock()
        page.url = "https://www.instagram.com/test.target/"
        page.locator.return_value.count.return_value = 0
        page.locator.return_value.first.count.return_value = 1
        page.locator.return_value.first.is_visible.return_value = True
        page.locator.return_value.first.inner_text.return_value = "Profile test.target"
        pre_click = Mock()
        guards = (
            patch("profile_actions.challenge_detected", return_value=False),
            patch("profile_actions._wait_for_target_profile_shell", return_value=True),
            patch("profile_actions._verified_action_owner", return_value=True),
            patch("profile_actions._wait_for_profile_relationship_control", return_value=None),
            patch("profile_actions._profile_relationship_control", return_value=None),
            patch("profile_actions._relationship_layout_note",
                  return_value=" Profile layout: exact target yes, control no."),
            patch("profile_actions._follow_state", return_value=None),
        )
        from contextlib import ExitStack
        with ExitStack() as stack:
            for guard in guards:
                stack.enter_context(guard)
            lookup = stack.enter_context(patch(
                "ig_structured_probe.inspect_structured_following",
                return_value="FOLLOWING_STRUCTURED"))
            result, details = perform_visible_action(
                page, "test.target", "unfollow", "owner.name",
                can_act=lambda name: name == "test.target",
                preloaded=True, use_reference_transport=False, on_pre_click=pre_click)
            self.assertEqual(result, "review")
            self.assertIn(MISSING_RELATIONSHIP_CONTROL, details)
            self.assertIn("Structured lookup:", details)
            self.assertIn("No action clicked", details)
            self.assertTrue(_preclick_no_action({
                "status": "review", "issue": "profile_load_timeout",
                "message": details}))
            lookup.assert_called_once_with(page, "test.target",
                                           owner_verified=True)
            pre_click.assert_not_called()
            page.goto.assert_not_called()

            lookup.reset_mock(return_value=True)
            lookup.return_value = "STRUCTURED_SESSION_REQUIRED"
            result, details = perform_visible_action(
                page, "test.target", "unfollow", "owner.name",
                preloaded=True, use_reference_transport=False, on_pre_click=pre_click)
            self.assertEqual(result, "review")
            self.assertIn("not exposed", details)
            pre_click.assert_not_called()

            lookup.reset_mock(return_value=True)
            lookup.return_value = "STRUCTURED_RATE_LIMITED"
            result, details = perform_visible_action(
                page, "test.target", "unfollow", "owner.name",
                preloaded=True, use_reference_transport=False, on_pre_click=pre_click)
            self.assertEqual(result, "blocked")
            self.assertIn("403/429", details)
            pre_click.assert_not_called()

            lookup.reset_mock(return_value=True)
            result, details = perform_visible_action(
                page, "test.target", "cancel", "owner.name",
                preloaded=True, use_reference_transport=False, on_pre_click=pre_click)
            self.assertEqual(result, "review")
            lookup.assert_not_called()
            pre_click.assert_not_called()

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
