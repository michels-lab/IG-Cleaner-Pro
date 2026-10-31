"""Two exact Instagram action workspaces with separate Chrome sessions.

Action workers are deliberately SERIALIZED by the canonical global action
WAL/OS lease. This is NOT a two-concurrent-unfollows feature. Each workspace
has its own persistent browser identity and ActionRobot state, while all
relationship evidence stays in the original canonical owner/account journals.
"""
from __future__ import annotations

import threading
from pathlib import Path

from dual_chrome_sessions import APP_OWNER, DualChromeSessions
from profile_actions import ActionRobot
from dual_action_coordinator import SharedGlobalActionCohort


class DualActionWorkspaces:
    def __init__(self, sessions: DualChromeSessions, collector, journal_root: Path,
                 legacy_actions: ActionRobot, *, offline_test_runner=None):
        # Internal OFFLINE test hook. Real Windows bridge never passes this
        # parameter: normal app workers remain globally SERIALIZED. When a
        # callback is supplied, it replaces the entire Instagram Playwright
        # _run() body. This is not a production concurrent-Unfollow switch.
        if offline_test_runner is not None and not callable(offline_test_runner):
            raise TypeError("Offline robot test runner must be a callable.")
        self.sessions = sessions
        self.collector = collector
        self.journal_root = Path(journal_root)
        self.legacy_actions = legacy_actions
        self._offline_test_runner = offline_test_runner
        self._offline_cohort = (
            SharedGlobalActionCohort(self.journal_root)
            if offline_test_runner is not None else None
        )
        self.lock = threading.RLock()
        self.owner = None
        self.workspaces = {}

    @staticmethod
    def _owner(data):
        if not isinstance(data, dict):
            raise ValueError("Choose a registered InstaCleaner owner and workspace.")
        owner = data.get("owner")
        if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
            raise ValueError("Sign in to InstaCleaner before managing action workspaces.")
        return owner

    @staticmethod
    def _alive(robot):
        return robot.worker is not None and robot.worker.is_alive()

    def configure(self, data):
        owner = self._owner(data)
        first = self.sessions._workspace(data.get("primary"))
        second = self.sessions._workspace(data.get("secondary"))
        if first[0] == second[0] or first[1] == second[1]:
            raise ValueError("Two action workspaces must have different accounts and handles.")
        if (data.get("read_only_consent") is not True
                or data.get("acknowledge_serial_actions") is not True
                or data.get("confirmation") != "dual-action-workspaces:" + first[0] + ":" + second[0]):
            raise ValueError(
                "Confirm both exact accounts and that relationship actions remain serialized.")
        with self.lock:
            if self.owner is not None and self.owner != owner:
                raise ValueError("Another InstaCleaner owner already configured action workspaces.")
            if self._alive(self.legacy_actions) or any(
                    self._alive(item["robot"]) for item in self.workspaces.values()):
                raise ValueError("Stop all active action workers before changing account assignments.")
            folders = [self.sessions.directory(owner, a) for a, _ in (first, second)]
            if folders[0].resolve() == folders[1].resolve():
                raise ValueError("Instagram Chrome profile collision: no workspaces configured.")
            # Never share ActionRobot's mutable owner/target/stop/worker state
            # across these accounts. Reuse only the canonical data directory
            # for existing WAL, protections and batch history.
            workspaces = {}
            for (account, handle), folder in zip((first, second), folders):
                robot = ActionRobot(
                    self.collector, self.journal_root, folder,
                    lease_factory=(self._offline_cohort.lease
                                   if self._offline_cohort is not None else None),
                )
                if self._offline_test_runner is not None:
                    # Completely replaces network-bound Playwright/click code,
                    # not just the final click. Only unit tests inject runner.
                    robot._run = (
                        lambda a=account, ev=robot.stop_event:
                        self._offline_test_runner(a, ev)
                    )
                workspaces[account] = {
                    "handle": handle, "chrome": folder, "robot": robot,
                }
            self.owner, self.workspaces = owner, workspaces
            return self._snapshot_locked()

    def _lane(self, owner, account):
        if owner != self.owner or account not in self.workspaces:
            raise ValueError("The selected Instagram action workspace belongs to another owner.")
        return self.workspaces[account]

    def start_one(self, data):
        owner = self._owner(data)
        account = data.get("account")
        action = data.get("action")
        if not isinstance(account, str) or not isinstance(action, dict):
            raise ValueError("Name the exact workspace and owner-approved action cohort.")
        task = action.get("task")
        if task not in ("unfollow", "cancel", "audit"):
            raise ValueError("Use the existing Unfollow, Cancel Pending or read-only Audit tasks.")
        if data.get("confirmation") != (
                "action-workspace-start:" + owner + ":" + account + ":" + task):
            raise ValueError("Approve the exact account and task before starting its Chrome robot.")
        with self.lock:
            lane = self._lane(owner, account)
            if (action.get("owner"), action.get("account"),
                    action.get("expected_handle")) != (owner, account, lane["handle"]):
                raise ValueError("Action owner, workspace and expected Instagram login must match.")
            if self._alive(self.legacy_actions):
                raise ValueError("The legacy Instagram action worker is active; no parallel actions.")
            if (self._offline_cohort is None
                    and any(self._alive(row["robot"]) for row in self.workspaces.values())):
                raise ValueError("Only one relationship-changing action worker can run at a time.")
            # The offline test harness may exercise both workers, but because
            # their _run bodies are replaced no Instagram mutation can occur.
            # The coordinator still holds the legacy global kernel lease
            # while either worker lives. Production never enters this branch.
            # ActionRobot performs its COMPLETE existing batch-size, protected
            # list, fresh-cohort, WAL and exact-target approval gates here.
            # This supervisor never invents/forwards a consent flag.
            return lane["robot"].start(action)

    def pause_one(self, data):
        owner = self._owner(data)
        account = data.get("account")
        if (not isinstance(account, str)
                or data.get("confirmation") != "action-workspace-pause:" + owner + ":" + account):
            raise ValueError("Confirm the exact Instagram workspace before stopping its worker.")
        with self.lock:
            lane = self._lane(owner, account)
            return lane["robot"].pause({"owner": owner, "account": account})

    def review_one(self, data):
        """Read the unresolved cohort from the EXACT owner/account/task WAL."""
        owner = self._owner(data)
        account, task = data.get("account"), data.get("task")
        if task not in ("unfollow", "cancel"):
            raise ValueError("Choose Unfollow or Cancel Pending for this workspace review.")
        with self.lock:
            lane = self._lane(owner, account)
            return lane["robot"].batch_review(
                {"owner": owner, "account": account, "task": task})

    def approve_one(self, data):
        """Owner-confirmed exact-scope batch approval; never promotes Review to OK."""
        owner = self._owner(data)
        account, task, batch_id = (data.get("account"), data.get("task"),
                                   data.get("batch_id"))
        if (not isinstance(account, str) or task not in ("unfollow", "cancel")
                or not isinstance(batch_id, str) or not 1 <= len(batch_id) <= 128
                or data.get("confirmation") != (
                    "action-workspace-approve:" + owner + ":" + account + ":" + task + ":" + batch_id)):
            raise ValueError("Confirm the exact account, task and original saved batch before approval.")
        with self.lock:
            lane = self._lane(owner, account)
            if self._alive(self.legacy_actions) or any(
                    self._alive(item["robot"]) for item in self.workspaces.values()):
                raise ValueError("Pause all relationship action workers before approving a saved batch.")
            # The canonical ActionRobot already refuses any untouched target,
            # corrupt WAL, stale cohort and unconfirmed click. It explicitly
            # keeps uncertain actions unresolved, even after read-only scans.
            return lane["robot"].approve_batch({
                "owner": owner, "account": account, "task": task,
                "batch_id": batch_id, "confirmation": "reviewed:" + batch_id,
            })

    def open_review_one(self, data):
        """Manually open a previously inspected target in its own Chrome profile."""
        owner = self._owner(data)
        account, task, username = data.get("account"), data.get("task"), data.get("username")
        if task not in ("unfollow", "cancel"):
            raise ValueError("Choose Unfollow or Cancel Pending review.")
        from profile_counts_robot import valid_username
        if (not isinstance(account, str) or not isinstance(username, str)
                or username != valid_username(username)
                or data.get("confirmation") != (
                    "action-workspace-review:" + owner + ":" + account + ":" + username)):
            raise ValueError("Confirm the exact account and saved profile for manual review.")
        with self.lock:
            lane = self._lane(owner, account)
            robot = lane["robot"]
            if self._alive(robot):
                raise ValueError("Pause this action worker before manually reopening its profiles.")
            with robot.lock:
                # Independently read exact scoped evidence even on app restart.
                from profile_actions import _read_json
                saved = _read_json(robot._base_for(owner, account, task), {})
                visited = _read_json(robot._target_visits_file_for(owner, account, task), {})
                if username not in saved and username not in visited:
                    raise ValueError("This target was never inspected in this account's saved history.")
            # Opens the bound hashed Chrome directory; no relationship click.
            return robot.open_profile(
                {"owner": owner, "account": account, "task": task, "username": username})

    def status(self, owner):
        if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
            raise ValueError("Invalid InstaCleaner owner.")
        with self.lock:
            if self.owner is not None and owner != self.owner:
                raise ValueError("Cannot inspect another owner's Instagram action workspaces.")
            return self._snapshot_locked()

    def _snapshot_locked(self):
        lanes = []
        for account, item in self.workspaces.items():
            r = item["robot"]
            # Never include Chrome session paths, tokens or browser cookies.
            state = r.snapshot()
            lanes.append({
                "account": account, "expected_handle": item["handle"],
                "state": state["status"], "message": state["message"],
                "running": state["running"], "task": state["task"],
                "current_profile": state["current_profile"],
                "processed": state["processed"], "pending": state["pending"],
                "issues": state["issue_count"],
                "review_batch_open": state["review_batch"] is not None,
            })
        return {
            "owner": self.owner, "two_workspaces": len(lanes) == 2,
            "distinct_action_chrome_profiles": len(lanes) == 2,
            "mode": ("offline_two_worker_integration_test_no_instagram"
                     if self._offline_cohort is not None else
                     "independent_chrome_sessions_serialized_actions"),
            "parallel_mutations_enabled": False,
            "requires_separate_batch_confirmation": True,
            "lanes": lanes,
        }

    def shutdown(self):
        with self.lock:
            workers = [item["robot"] for item in self.workspaces.values()]
            for robot in workers:
                robot.stop_event.set()
        # Always join outside the manager lock; a worker must be able to
        # close Chrome and release its WAL before the native process exits.
        for robot in workers:
            if self._alive(robot):
                robot.worker.join(timeout=60)
