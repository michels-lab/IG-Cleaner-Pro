"""Fail-closed cross-process admission for all real Instagram action jobs.

Public and Developer are separate Windows processes with distinct Chrome data
directories but one canonical action journal. The kernel releases this file
lock when a process crashes; no stale owner PID or named semaphore counter can
silently deadlock future runs. A running worker holds it through owner review.
"""
import hashlib
import os
from pathlib import Path
import sys


class ActionSessionBusy(ValueError):
    """Another local application is still performing/reviewing actions."""


class ActionLease:
    def __init__(self, root: Path, *, lock_name=".instagram-action-admission.lock"):
        self.root = Path(root).resolve()
        # Only internal, known-safe lock basenames may be used. No paths or usernames.
        if (not isinstance(lock_name, str) or not lock_name.startswith(".instagram-action-")
                or not lock_name.endswith(".lock") or "/" in lock_name or chr(92) in lock_name
                or ".." in lock_name):
            raise ValueError("Invalid Instagram action lease name.")
        self.lock_name = lock_name
        self.handle = None

    def acquire(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / self.lock_name
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        if sys.platform == "win32":
            flags |= os.O_BINARY
        try:
            fd = os.open(path, flags, 0o600)
        except OSError as exc:
            raise ActionSessionBusy(
                "Cannot establish exclusive access to the Instagram action journal; "
                "no job started.") from exc
        try:
            if sys.platform == "win32":
                import msvcrt
                # A Win32 byte-range file lock is bound to the open handle.
                # Closing/crashing releases it automatically. Unlike a named
                # semaphore, it cannot remain at zero after an app crash.
                if not os.fstat(fd).st_size:
                    os.write(fd, b"\0")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise ActionSessionBusy(
                "Another public/Developer InstaCleaner action job may be active, "
                "or the journal cannot be locked. Finish/pause the other robot "
                "before starting another batch.") from exc
        except BaseException:
            os.close(fd)
            raise
        self.handle = fd
        return self

    def release(self):
        fd = self.handle
        if fd is None:
            return
        self.handle = None
        try:
            if sys.platform == "win32":
                import msvcrt
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


class ScopedActionLease:
    """Two-level action lease, backwards-compatible with older installed apps.

    The legacy GLOBAL lease is deliberately held first and kept until the
    complete action worker finishes. The new opaque per-owner/workspace lease
    adds collision protection for future independent workers; it does NOT
    enable concurrent Unfollow or Cancel Pending today.

    A future move to simultaneous mutation must first prove that no old
    global-lease app can run concurrently, and explicitly migrate publisher
    admission, WAL journaling, recovery and Chrome identity before lifting
    the global barrier. Never enable it just because the scope lock exists.
    """

    def __init__(self, root: Path, owner: str, account: str):
        if (not isinstance(owner, str) or not 1 <= len(owner) <= 200
                or not isinstance(account, str) or not 1 <= len(account) <= 120):
            raise ValueError("An exact InstaCleaner owner and workspace are required.")
        name_digest = hashlib.sha256(
            (owner + chr(0) + account).encode("utf-8")).hexdigest()[:32]
        self.global_lease = ActionLease(root)
        self.workspace_lease = ActionLease(
            root, lock_name=".instagram-action-" + name_digest + ".lock")
        self.acquired = False

    def acquire(self):
        if self.acquired:
            raise ActionSessionBusy("This action lease is already active.")
        # GLOBAL always first; avoid deadlocks and stay compatible with
        # already installed versions that only know the global OS lock.
        self.global_lease.acquire()
        try:
            self.workspace_lease.acquire()
        except BaseException:
            self.global_lease.release()
            raise
        self.acquired = True
        return self

    def release(self):
        if not self.acquired:
            return
        self.acquired = False
        try:
            self.workspace_lease.release()
        finally:
            self.global_lease.release()
