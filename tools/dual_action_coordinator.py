"""Crash-safe shared GLOBAL admission for two independently scoped action leases.

An explicit coordinator MAY hold one legacy global OS lock for TWO distinct
owner/account workers in the SAME Windows process. Older installed public or
Developer binaries still see the legacy global lock as BUSY for the ENTIRE
cohort. Releasing worker A cannot unlock the global lease while B is running.

This is an internal safety primitive, NOT a relationship-changing robot or
a launch of concurrent Unfollows. No app endpoint uses it until the complete
multi-worker action WAL, Chrome login and owner-confirmation contract is tested.
"""
from __future__ import annotations

import threading
from pathlib import Path

from robot_interlock import ActionLease, ActionSessionBusy, ScopedActionLease


class SharedGlobalActionCohort:
    """Kernel-held global WAL lease, reference-counted to distinct scoped jobs."""

    def __init__(self, journal_root, *, maximum_workers=2):
        if type(maximum_workers) is not int or maximum_workers != 2:
            raise ValueError("The audited multi-worker coordinator supports exactly two scopes.")
        self.root = Path(journal_root).resolve()
        self.lock = threading.RLock()
        self.global_lease = None
        self.scopes = {}
        self.active_owner = None
        self.maximum_workers = maximum_workers

    def lease(self, root, owner, account):
        if Path(root).resolve() != self.root:
            raise ValueError("The action WAL root must be the same canonical journal directory.")
        prototype = ScopedActionLease(self.root, owner, account)
        return _CohortScope(self, (owner, account), prototype.workspace_lease)

    def _acquire(self, key, scope):
        with self.lock:
            if key in self.scopes:
                raise ActionSessionBusy("This Instagram owner/account action scope is already active.")
            if self.active_owner is not None and self.active_owner != key[0]:
                raise ActionSessionBusy("Both concurrent Instagram workspaces must belong to the same app owner.")
            if len(self.scopes) >= self.maximum_workers:
                raise ActionSessionBusy("No more than two Instagram action scopes may run.")
            created_global = False
            if self.global_lease is None:
                # Older installations ALWAYS acquire exactly this filename,
                # so they remain excluded while either new worker is active.
                global_lease = ActionLease(self.root)
                global_lease.acquire()
                self.global_lease = global_lease
                created_global = True
            try:
                scope.acquire()
            except BaseException:
                # If worker B cannot reserve its Chrome/account WAL, A still
                # owns the legacy global lock. If A does not exist, free it.
                if created_global and not self.scopes:
                    self.global_lease.release()
                    self.global_lease = None
                raise
            self.scopes[key] = scope
            self.active_owner = key[0]

    def _release(self, key, scope):
        with self.lock:
            if self.scopes.get(key) is not scope:
                return
            # Never release the global lock until ALL scoped workers have
            # released their cross-process account leases.
            try:
                scope.release()
            finally:
                del self.scopes[key]
                if not self.scopes:
                    try:
                        self.global_lease.release()
                    finally:
                        self.global_lease = None
                        self.active_owner = None

    def status(self):
        with self.lock:
            return {
                "legacy_global_lease_held": self.global_lease is not None,
                "active_scopes": len(self.scopes),
                # Do not expose real owner/account names in diagnostics.
                "maximum_workers": self.maximum_workers,
                "parallel_mutations_enabled": False,
                "mode": "coordinator_only_not_wired_to_action_robot",
            }

    def assert_idle(self):
        with self.lock:
            if self.scopes or self.global_lease is not None:
                raise ActionSessionBusy("Wait until all action workers finish.")

    def close(self):
        """Fail-closed if workers still hold WAL; never unlock active actions."""
        self.assert_idle()


class _CohortScope:
    def __init__(self, cohort, key, workspace_lease):
        self.cohort, self.key, self.workspace_lease = cohort, key, workspace_lease
        self.acquired = False

    def acquire(self):
        if self.acquired:
            raise ActionSessionBusy("This action worker already has its scoped lease.")
        self.cohort._acquire(self.key, self.workspace_lease)
        self.acquired = True
        return self

    def release(self):
        if not self.acquired:
            return
        self.acquired = False
        self.cohort._release(self.key, self.workspace_lease)

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *_):
        self.release()
