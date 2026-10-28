"""Exclusive OS lease per isolated Chrome robot profile, not per InstaCleaner app.

Two different Instagram workspaces can be supervised concurrently. Two Windows
processes must never attach a Playwright robot to the *same* Chrome profile.
The kernel releases these locks on process exit/crash. These leases do not
authorize any Instagram action or replace the action journal WAL admission.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys


class ChromeLaneBusy(ValueError):
    """A separate worker already owns this Chrome session, or locking failed."""


class ChromeLaneLease:
    """A nonblocking per-Chrome-directory lease held for the entire worker run."""

    def __init__(self, session_dir):
        self.session_dir = Path(session_dir).resolve()
        self.handle = None

    def acquire(self):
        if self.handle is not None:
            raise ChromeLaneBusy("This Chrome lane already holds its session lease.")
        # Keep lease metadata OUTSIDE Chrome's user-data and exported robot logs.
        root = self.session_dir.parent / ".igc-robot-lane-leases"
        try:
            root.mkdir(parents=True, exist_ok=True)
            flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
            if sys.platform == "win32":
                flags |= os.O_BINARY
            fd = os.open(root / (self.session_dir.name + ".lock"), flags, 0o600)
        except OSError as exc:
            raise ChromeLaneBusy("Cannot reserve an exclusive Chrome robot session. No job started.") from exc
        try:
            if sys.platform == "win32":
                import msvcrt
                if not os.fstat(fd).st_size:
                    os.write(fd, b"\0")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise ChromeLaneBusy(
                "Another InstaCleaner robot already owns this Chrome session, "
                "or the session cannot be locked. Stop that lane first; no actions were performed."
            ) from exc
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

    def __enter__(self):
        return self.acquire()

    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.release()
