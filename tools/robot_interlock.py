"""Fail-closed cross-process admission for all real Instagram action jobs.

Public and Developer are separate Windows processes with distinct Chrome data
directories but one canonical action journal. The kernel releases this file
lock when a process crashes; no stale owner PID or named semaphore counter can
silently deadlock future runs. A running worker holds it through owner review.
"""
import os
from pathlib import Path
import sys


class ActionSessionBusy(ValueError):
    """Another local application is still performing/reviewing actions."""


class ActionLease:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.handle = None

    def acquire(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / ".instagram-action-admission.lock"
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
