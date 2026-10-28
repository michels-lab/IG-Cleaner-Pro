"""Read-only eligibility audit for two separately owned Instagram action cohorts.

This is intentionally *not* a dual-action executor. We have no proof that
two concurrent relationship-changing workers have owner-scoped WAL, browser
identity and recovery isolation. Never turn a preflight result into consent.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from dual_chrome_sessions import APP_OWNER, DualChromeSessions
from profile_actions import (
    ActionRobot, _read_json, _invalid_saved_action_record, valid_username,
)


class DualActionPreflight:
    """Classify two exact cohorts using the SAME journals as the live robot."""

    def __init__(self, sessions: DualChromeSessions, actions: ActionRobot):
        self.sessions = sessions
        self.actions = actions

    def _validate(self, data):
        if not isinstance(data, dict):
            raise ValueError("Select two Instagram action cohorts for read-only inspection.")
        owner = data.get("owner")
        if not isinstance(owner, str) or not APP_OWNER.fullmatch(owner):
            raise ValueError("Sign in to InstaCleaner before inspecting saved actions.")
        primary, secondary = data.get("primary"), data.get("secondary")
        for lane in (primary, secondary):
            if not isinstance(lane, dict):
                raise ValueError("Provide a separate cohort for each Instagram workspace.")
        left = self.sessions._workspace(primary)
        right = self.sessions._workspace(secondary)
        if left[0] == right[0] or left[1] == right[1]:
            raise ValueError("Two action cohorts require distinct Instagram accounts.")
        if (data.get("read_only_consent") is not True
                or data.get("confirmation") != "dual-action-preflight:" + left[0] + ":" + right[0]):
            raise ValueError("Confirm both exact workspaces for inspection only.")
        for lane in (primary, secondary):
            if lane.get("task") not in ("unfollow", "cancel"):
                raise ValueError("Choose Unfollow or Cancel Pending for each action cohort.")
            names = lane.get("targets")
            if not isinstance(names, list) or not 1 <= len(names) <= 1000:
                raise ValueError("Each account needs 1–1,000 named target profiles.")
            if any(not isinstance(user, str) or not valid_username(user)
                   or user != valid_username(user) for user in names):
                raise ValueError("Targets must be canonical exact Instagram usernames.")
            if len(names) != len(set(names)):
                raise ValueError("Duplicate targets require inspection; no silent deduplication.")
        return owner, ((left, primary), (right, secondary))

    def _inspect_one(self, owner, scope, lane):
        (account, handle), task, targets = scope, lane["task"], lane["targets"]
        robot = self.actions
        # Use the original owner/account/task-scoped files. Never create an
        # independent journal that could later permit a duplicate Unfollow.
        journal = _read_json(robot._base_for(owner, account, task), {})
        visits = _read_json(robot._target_visits_file_for(owner, account, task), {})
        protected = _read_json(robot._protection_file_for(owner, account), [])
        batches = robot._review_batches(owner, account, task)
        if (any(not isinstance(user, str) or valid_username(user) != user
                or _invalid_saved_action_record(rec)
                for user, rec in journal.items())
                or any(not isinstance(user, str) or valid_username(user) != user
                       or not isinstance(rec, dict) for user, rec in visits.items())
                or any(not isinstance(user, str) or valid_username(user) != user
                       for user in protected)
                or any(not isinstance(entry, dict) for entry in batches)):
            raise ValueError(
                "Saved action history or protected-list evidence is malformed. "
                "Do not start or replan robot actions; inspect the original records.")
        pending = next((entry for entry in reversed(batches)
                        if not entry.get("approved_at") and not entry.get("deferred_at")), None)
        protected_set = set(protected)
        inspected = set(visits) | set(journal)
        selected = []
        counts = {"untouched": 0, "protected": 0, "previously_inspected": 0,
                  "uncertain_action": 0, "pending_cohort": 0}
        for username in targets:
            if username in protected_set:
                state = "protected"
            elif username in journal and (
                    journal[username].get("click_intent") is not None
                    or journal[username].get("issue") == "interrupted_action_uncertain"):
                state = "uncertain_action"
            elif username in inspected:
                state = "previously_inspected"
            elif pending is not None:
                # No new batch while a previous exact cohort is unresolved.
                state = "pending_cohort"
            else:
                state = "untouched"
            counts[state] += 1
            selected.append({"username": username, "offline_evidence": state})
        return {
            "account": account, "expected_handle": handle, "task": task,
            "selected_count": len(targets),
            "evidence_counts": counts,
            "targets": selected,
            "unresolved_saved_cohort": pending is not None,
            "saved_cohort_id": str(pending.get("id") or "") if pending else "",
            "offline_untouched_only": counts["untouched"] == len(targets),
            "actions_enabled": False,
            "missing_verification": [
                "fresh_exact_owner_browser_session",
                "current_target_relationship",
                "separate_exact_cohort_action_consent",
                "independent_mutation_WAL_and_cross_process_admission",
            ],
        }

    def inspect(self, data):
        owner, lanes = self._validate(data)
        with self.actions.lock:
            if (self.actions.worker is not None and self.actions.worker.is_alive()):
                raise ValueError(
                    "An Instagram action worker is running. Pause it before "
                    "using an offline journal snapshot for dual-account planning.")
            results = [self._inspect_one(owner, scope, lane) for scope, lane in lanes]
        return {
            "status": "read_only_snapshot",
            "owner": owner,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "actions_enabled": False,
            "can_launch_parallel_unfollow": False,
            "mode": "two_account_offline_action_eligibility_only",
            "warning": ("This is saved local evidence, NOT a live Instagram account check "
                        "or permission to Unfollow/Cancel. Existing action robots "
                        "remain serialized."),
            "lanes": results,
        }
