"""Two exact Instagram action workspaces with separate persistent Chrome sessions.

Serial by DEFAULT. Two concurrent action workers are possible ONLY after
an exact owner-initiated configuration and additional owner/account/task
confirmation per batch. Both workers share one legacy GLOBAL OS lease for
the entire cohort and take distinct scoped Chrome/WAL locks. Existing public
and Developer installations cannot bypass the global file admission.
"""
from __future__ import annotations

import hashlib
import threading
from pathlib import Path

from dual_chrome_sessions import APP_OWNER, DualChromeSessions
from profile_actions import ActionRobot, _atomic_json, _read_json
from dual_action_coordinator import SharedGlobalActionCohort
from robot_interlock import ScopedActionLease


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
        self._live_cohort = None
        self._parallel_enabled = False
        self.lock = threading.RLock()
        self.owner = None
        self.workspaces = {}
        self._restored_from_disk = False

    def _binding_file(self, owner):
        """Private metadata next to isolated browser data, outside exported robot WAL.

        Only owner/workspace/expected Instagram handle are stored. No cookies,
        credentials, approvals, target lists or background action state.
        """
        digest = hashlib.sha256(owner.encode("utf-8")).hexdigest()[:32]
        return self.sessions.root.parent / "linked-action-workspaces-v1" / (digest + ".json")

    def _build_lanes(self, owner, first, second, parallel):
        """Build two idle ActionRobot instances; NEVER launch Playwright."""
        folders = [self.sessions.directory(owner, a) for a, _ in (first, second)]
        if folders[0].resolve() == folders[1].resolve():
            raise ValueError("Instagram Chrome profile collision: no workspaces configured.")
        # Both robots retain the original owner/account/task-scoped canonical
        # WAL. Only the explicit current-session parallel consent installs a
        # two-worker cohort; restored bindings always use serial OS leases.
        live_cohort = SharedGlobalActionCohort(self.journal_root) if parallel else None
        cohort = self._offline_cohort or live_cohort
        workspaces = {}
        for (account, handle), folder in zip((first, second), folders):
            robot = ActionRobot(
                self.collector, self.journal_root, folder,
                lease_factory=(cohort.lease if cohort is not None else None),
            )
            if self._offline_test_runner is not None:
                robot._run = (
                    lambda a=account, ev=robot.stop_event:
                    self._offline_test_runner(a, ev)
                )
            workspaces[account] = {
                "handle": handle, "chrome": folder, "robot": robot,
            }
        return live_cohort, workspaces

    def _restore_saved_locked(self, owner):
        """Read-only rebind on native restart; cannot resurrect a worker/consent."""
        path = self._binding_file(owner)
        if not path.exists():
            return
        saved = _read_json(path, {})
        if saved.get("version") != 1 or saved.get("owner") != owner or (
                set(saved) != {"version", "owner", "primary", "secondary"}):
            raise ValueError("Saved two-account bindings are invalid. No robots were started.")
        try:
            first = self.sessions._workspace(saved["primary"])
            second = self.sessions._workspace(saved["secondary"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Saved Instagram account bindings are invalid. No robots were started.") from exc
        if first[0] == second[0] or first[1] == second[1]:
            raise ValueError("Saved Chrome profiles overlap. No robots were started.")
        live_cohort, workspaces = self._build_lanes(owner, first, second, False)
        self._live_cohort = live_cohort
        self._parallel_enabled = False
        self.owner, self.workspaces = owner, workspaces
        self._restored_from_disk = True

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
        parallel = data.get("parallel_actions_consent") is True
        if data.get("parallel_actions_consent") not in (None, False, True):
            raise ValueError("Choose a valid explicit concurrent-action mode.")
        if data.get("read_only_consent") is not True:
            raise ValueError("Confirm both exact accounts before configuring Chrome.")
        if parallel:
            if (data.get("acknowledge_parallel_actions") is not True
                    or data.get("acknowledge_serial_actions") is True
                    or data.get("confirmation") !=
                    "dual-action-workspaces-parallel:" + first[0] + ":" + second[0]):
                raise ValueError(
                    "Confirm TWO concurrent action robots for these exact accounts. "
                    "Each batch also needs separate explicit owner approval.")
        elif (data.get("acknowledge_serial_actions") is not True
                or data.get("acknowledge_parallel_actions") is True
                or data.get("confirmation") !=
                "dual-action-workspaces:" + first[0] + ":" + second[0]):
            raise ValueError(
                "Confirm both exact accounts and the default serialized action mode.")
        with self.lock:
            if self.owner is not None and self.owner != owner:
                raise ValueError("Another InstaCleaner owner already configured action workspaces.")
            if self._alive(self.legacy_actions) or any(
                    self._alive(item["robot"]) for item in self.workspaces.values()):
                raise ValueError("Stop all active action workers before changing account assignments.")
            live_cohort, workspaces = self._build_lanes(owner, first, second, parallel)
            # Persist only the owner-confirmed *identity bindings*. Never
            # persist parallel-action approval, the original job, login
            # cookies, token, targets or the robot's running flag. Commit
            # metadata atomically BEFORE replacing in-memory assignments.
            _atomic_json(self._binding_file(owner), {
                "version": 1, "owner": owner,
                "primary": {"account": first[0], "expected_handle": first[1]},
                "secondary": {"account": second[0], "expected_handle": second[1]},
            })
            self._live_cohort = live_cohort
            self._parallel_enabled = parallel
            self.owner, self.workspaces = owner, workspaces
            self._restored_from_disk = False
            return self._snapshot_locked()

    def _lane(self, owner, account):
        if owner != self.owner or account not in self.workspaces:
            raise ValueError("The selected Instagram action workspace belongs to another owner.")
        return self.workspaces[account]

    def preflight_new_one(self, data):
        """Read-only exact-account new-cohort eligibility from canonical WAL.

        Never converts observed historical state into current Instagram
        relationship evidence or owner permission. The start path independently
        revalidates everything under its exclusive OS lease.
        """
        owner = self._owner(data)
        account, task, targets = (data.get("account"), data.get("task"),
                                  data.get("targets"))
        from profile_counts_robot import valid_username
        from dual_action_preflight import DualActionPreflight
        if (not isinstance(account, str) or task not in ("unfollow", "cancel")
                or data.get("confirmation") != (
                    "action-workspace-preflight:" + owner + ":" + account + ":" + task)
                or not isinstance(targets, list) or not 1 <= len(targets) <= 1000
                or any(not isinstance(name, str) or valid_username(name) != name
                       for name in targets) or len(set(targets)) != len(targets)):
            raise ValueError("Read-only preflight requires exact owner, task and 1-1000 unique usernames.")
        with self.lock:
            lane = self._lane(owner, account)
            if data.get("expected_handle") != lane["handle"]:
                raise ValueError("The selected Instagram account handle changed. No targets were inspected.")
            if (self._alive(self.legacy_actions)
                    or self._alive(lane["robot"])
                    or (not self._parallel_enabled and self._offline_cohort is None
                        and any(self._alive(row["robot"]) for row in self.workspaces.values()))):
                raise ValueError("Pause the existing action robot before checking a new cohort.")
            inspection = DualActionPreflight(self.sessions, self.legacy_actions)
            # Classifies one cohort using the same journal/protection/visit
            # evidence and precise scope already proven by the dual preflight.
            result = inspection._inspect_one(
                owner, (account, lane["handle"]),
                {"task": task, "targets": targets})
            return {
                **result, "owner": owner, "read_only": True,
                "actions_enabled": False, "can_launch_parallel_unfollow": False,
                "warning": "Local saved-history check only. Current Instagram "
                           "relationship and login must be verified separately.",
            }

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
            if self._parallel_enabled and self._offline_cohort is None:
                if data.get("parallel_action_confirmation") != (
                        "parallel-action-workspace-start:" + owner + ":" + account + ":" + task):
                    raise ValueError(
                        "Confirm concurrent-action permission for this exact account and task.")
            if (not self._parallel_enabled and self._offline_cohort is None
                    and any(self._alive(row["robot"]) for row in self.workspaces.values())):
                raise ValueError("Only one relationship-changing action worker can run at a time.")
            # A parallel configuration still uses independent ActionRobot
            # instances and the original per-account WAL. A single cohort
            # holds the LEGACY GLOBAL kernel lock until the LAST active worker
            # exits. The worker itself performs ALL existing protected,
            # target identity, Click-WAL, rate and login checks.
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

    def cancel_batch_one(self, data):
        """Cancel one original saved cohort; never mistake it for Cancel Pending.

        The idle after-restart route uses the same canonical account WAL under
        a kernel lease. Parallel mode shares its already-held legacy GLOBAL
        lock with the still-running sibling action robot, without stopping B.
        """
        owner = self._owner(data)
        account, task, batch_id = (data.get("account"), data.get("task"),
                                   data.get("batch_id"))
        if (not isinstance(account, str) or task not in ("unfollow", "cancel")
                or not isinstance(batch_id, str) or not 1 <= len(batch_id) <= 128
                or data.get("confirmation") != (
                    "action-workspace-cancel:" + owner + ":" + account + ":" +
                    task + ":" + batch_id)):
            raise ValueError("Confirm the exact owner, account, task and saved batch to cancel.")
        with self.lock:
            lane = self._lane(owner, account)
            robot = lane["robot"]
            request = {"owner": owner, "account": account, "task": task,
                       "batch_id": batch_id, "confirmation": "cancel-batch:" + batch_id}
            if self._alive(robot):
                if (robot.owner, robot.account, robot.task) != (owner, account, task):
                    raise ValueError("A different task is running in this action lane; no batch cancelled.")
                return robot.cancel_current_batch(request)
            # Do not mutate idle WAL unless the OS guarantees the same scope
            # is not owned by a different public/Developer InstaCleaner.
            cohort = self._offline_cohort or self._live_cohort
            lease = (cohort.lease(self.journal_root, owner, account)
                     if cohort is not None else
                     ScopedActionLease(self.journal_root, owner, account))
            # ScopedActionLease intentionally exposes acquire()/release()
            # rather than __enter__/__exit__. Both cohort and legacy leases
            # are released even if the disk archive fails.
            lease.acquire()
            try:
                return robot.cancel_saved_batch(request)
            finally:
                lease.release()

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

    def archived_one(self, data):
        """Inspect cancelled/deferred saved waves for one selected account/task.

        A read-only history viewer is not batch approval, resumption or an
        Instagram relationship action. Never return targets, cookies or Chrome
        paths; the existing ActionRobot exposes only bounded safe summaries.
        """
        owner = self._owner(data)
        account, task = data.get("account"), data.get("task")
        if (not isinstance(account, str) or task not in ("unfollow", "cancel")
                or data.get("confirmation") !=
                "action-workspace-archive:" + owner + ":" + account + ":" + task):
            raise ValueError("Confirm the exact account and task to inspect archived batches.")
        with self.lock:
            lane = self._lane(owner, account)
            return lane["robot"].deferred_batch_history(
                {"owner": owner, "account": account, "task": task})

    def archived_detail_one(self, data):
        """Read one archived cohort without rerunning or approving anything."""
        owner = self._owner(data)
        account, task, batch_id = (
            data.get("account"), data.get("task"), data.get("batch_id"))
        if (not isinstance(account, str) or task not in ("unfollow", "cancel")
                or not isinstance(batch_id, str) or not 1 <= len(batch_id) <= 128
                or data.get("confirmation") !=
                "action-workspace-archive-detail:" + owner + ":" + account +
                ":" + task + ":" + batch_id):
            raise ValueError("Confirm exact Instagram account, task and archived batch.")
        with self.lock:
            lane = self._lane(owner, account)
            return lane["robot"].deferred_batch_details({
                "owner": owner, "account": account,
                "task": task, "batch_id": batch_id})

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
            if self.owner is None:
                self._restore_saved_locked(owner)
            if self.owner is not None and owner != self.owner:
                raise ValueError("Cannot inspect another owner's Instagram action workspaces.")
            return self._snapshot_locked()

    def _saved_cohort_summaries(self, owner, account, robot):
        """Redacted read-only unfinished Unfollow/Cancel cohorts after restart.

        The robot's in-memory task is blank after Windows is relaunched even
        when the ORIGINAL approved cohort is durable. Never infer a new
        action, successful click or login from historical WAL.
        """
        from profile_counts_robot import valid_username
        rows = []
        for task in ("unfollow", "cancel"):
            try:
                # A missing/incomplete saved batch cannot hide a damaged
                # canonical action WAL. Check each task's own file even when
                # _pending_review() would return None without reading it.
                # This is read-only and never changes the original evidence.
                _read_json(robot._base_for(owner, account, task), {})
                result = robot.batch_review({
                    "owner": owner, "account": account, "task": task})
                batch = result.get("batch")
                if batch is None:
                    continue
                names = batch.get("targets")
                batch_id = batch.get("id")
                if (not isinstance(batch_id, str) or not 1 <= len(batch_id) <= 128
                        or not isinstance(names, list) or not 1 <= len(names) <= 1000
                        or any(not isinstance(name, str) or valid_username(name) != name
                               for name in names) or len(set(names)) != len(names)):
                    raise ValueError("Invalid original saved target cohort.")
                original = batch.get("original_targets")
                original_count = (len(original)
                                  if isinstance(original, list) and original
                                  and len(original) <= 1000 and
                                  all(isinstance(x, str) and valid_username(x) == x
                                      for x in original) else len(names))
                outcomes = batch.get("action_results")
                if not isinstance(outcomes, dict):
                    raise ValueError("Saved action outcomes are not verifiable.")
                pending = confirmed = no_click = warnings = unavailable = 0
                for username in names:
                    item = outcomes.get(username)
                    if not isinstance(item, dict):
                        warnings += 1
                    elif item.get("status") == "pending":
                        pending += 1
                    elif item.get("status") == "ok":
                        # Validated terminal OK often retains its original
                        # click_intent WAL with outcome_recorded=true. This is
                        # real confirmed evidence, not an unresolved warning.
                        # ActionRobot.batch_review already downgrades invalid
                        # or unresolved "ok" WAL to review before reaching us.
                        confirmed += 1
                    elif item.get("possible_click") is True:
                        # A genuinely unresolved click still takes precedence
                        # over read-only "already" or unavailable observations.
                        warnings += 1
                    elif item.get("status") in (
                            "already_not_following", "already_not_requested"):
                        no_click += 1
                    elif item.get("status") == "profile_unavailable":
                        unavailable += 1
                    else:
                        warnings += 1
                rows.append({
                    "task": task, "batch_id": batch_id,
                    "original_total": original_count,
                    "current_total": len(names),
                    "untouched": pending,
                    "confirmed_clicks": confirmed,
                    "already_resolved_no_click": no_click,
                    "warnings": warnings,
                    "unavailable_no_click": unavailable,
                    "requires_explicit_resume": True,
                    "source": "saved_local_action_journal",
                })
            except (TypeError, KeyError, ValueError, OSError):
                # A damaged local file is not proof of an empty saved wave.
                # Show an explicit read failure without exposing usernames
                # or silently claiming the account has nothing outstanding.
                rows.append({"task": task, "unverifiable": True,
                             "requires_manual_review": True,
                             "source": "saved_local_action_journal"})
        return rows

    def _snapshot_locked(self):
        lanes = []
        for account, item in self.workspaces.items():
            r = item["robot"]
            # Never include Chrome session paths, tokens or browser cookies.
            # An already-bound worker reads its owner/account/task action WAL
            # in snapshot(), BEFORE _saved_cohort_summaries can protect its
            # archived-batch reads. A torn or wrong-type WAL for lane A must
            # not crash the entire Windows status route and hide healthy B.
            # Never repair, approve or truncate uncertain original evidence.
            try:
                state = r.snapshot()
            except (ValueError, OSError, TypeError, KeyError):
                state = {
                    "status": "blocked",
                    "message": (
                        "Saved action journal or related account evidence is "
                        "unreadable; original files are preserved. Review this "
                        "Instagram account before starting another action."
                    ),
                    "running": self._alive(r),
                    "task": r.task if r.task in ("unfollow", "cancel", "audit") else None,
                    "current_profile": None,
                    # Unknown is never zero or a confirmed relationship click.
                    "processed": None, "pending": None, "issue_count": None,
                    "total": None, "successful": None,
                    "already_not_following": None,
                    "already_not_requested": None,
                    "batch_size": None, "review_batch": None,
                    "owner_profile_visits": None,
                    "owner_sibling_proofs": None,
                }
            lanes.append({
                "account": account, "expected_handle": item["handle"],
                "state": state["status"], "message": state["message"],
                "running": state["running"], "task": state["task"],
                "current_profile": state["current_profile"],
                "processed": state["processed"], "pending": state["pending"],
                "issues": state["issue_count"],
                # Raw worker counters: actions really confirmed vs outcomes that
                # were already resolved without any relationship-changing click.
                # Missing historical values stay UNKNOWN, never fabricated 0.
                "total": state.get("total"),
                "successful": state.get("successful"),
                "already_not_following": state.get("already_not_following"),
                "already_not_requested": state.get("already_not_requested"),
                "batch_size": state.get("batch_size"),
                "batch_id": (state.get("review_batch") or {}).get("id")
                    if isinstance(state.get("review_batch"), dict) else None,
                # Read-only, redacted diagnostics: distinct from target visits
                # and NEVER counted as Instagram relationship mutations.
                "owner_profile_visits": state["owner_profile_visits"],
                "owner_sibling_proofs": state["owner_sibling_proofs"],
                "review_batch_open": state["review_batch"] is not None,
                # After a native restart the in-memory worker/task is blank.
                # Show both persisted cohorts without rebinding or replaying
                # an account, Chrome tab, action job or owner consent.
                "saved_batches": (
                    self._saved_cohort_summaries(self.owner, account, r)
                    if self.owner and not state["running"] else []),
            })
        return {
            "owner": self.owner, "two_workspaces": len(lanes) == 2,
            "distinct_action_chrome_profiles": len(lanes) == 2,
            "mode": ("offline_two_worker_integration_test_no_instagram"
                     if self._offline_cohort is not None else
                     "explicit_owner_authorized_two_account_actions"
                     if self._parallel_enabled else
                     "independent_chrome_sessions_serialized_actions"),
            "parallel_mutations_enabled": self._parallel_enabled,
            "bindings_restored_from_disk": self._restored_from_disk,
            "legacy_global_lease_held": (
                self._live_cohort.status()["legacy_global_lease_held"]
                if self._live_cohort is not None else False
            ),
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
