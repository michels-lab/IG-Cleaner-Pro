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


class DualActionWorkspaces:
    def __init__(self, sessions: DualChromeSessions, collector, journal_root: Path,
                 legacy_actions: ActionRobot):
        self.sessions = sessions
        self.collector = collector
        self.journal_root = Path(journal_root)
        self.legacy_actions = legacy_actions
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
                workspaces[account] = {
                    "handle": handle, "chrome": folder,
                    "robot": ActionRobot(self.collector, self.journal_root, folder),
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
            if any(self._alive(row["robot"]) for row in self.workspaces.values()):
                raise ValueError("Only one relationship-changing action worker can run at a time.")
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
            "mode": "independent_chrome_sessions_serialized_actions",
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
