"""Fail-closed cross-process admission for all real Instagram action jobs.

Public and Developer are separate Windows processes with distinct Chrome data
directories, but share the canonical action journal. In-process RLocks do not
protect either this journal or concurrent real relationship clicks. This lease
must be held across the entire worker, including owner review of open tabs.
"""
import hashlib
import os
from pathlib import Path
import sys


class ActionSessionBusy(ValueError):
    """Another local application is still performing/reviewing actions."""


class ActionLease:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.handle = None
        self._released = False

    def acquire(self):
        self.root.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
                kernel32.CreateSemaphoreW.argtypes = [
                    ctypes.c_void_p, ctypes.c_long, ctypes.c_long, ctypes.c_wchar_p]
                kernel32.CreateSemaphoreW.restype = ctypes.c_void_p
                kernel32.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
                kernel32.WaitForSingleObject.restype = ctypes.c_ulong
                kernel32.ReleaseSemaphore.argtypes = [
                    ctypes.c_void_p, ctypes.c_long, ctypes.c_void_p]
                kernel32.ReleaseSemaphore.restype = ctypes.c_bool
                kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
                kernel32.CloseHandle.restype = ctypes.c_bool
                digest = hashlib.sha256(
                    os.path.normcase(str(self.root)).encode("utf-8")).hexdigest()[:32]
                name = "Local\\MichelsLab_IGC_ActionJournal_" + digest
                handle = kernel32.CreateSemaphoreW(None, 1, 1, name)
                if not handle:
                    raise OSError("Cannot initialize shared Instagram action guard.")
                if kernel32.WaitForSingleObject(handle, 0) != 0:
                    kernel32.CloseHandle(handle)
                    raise ActionSessionBusy(
                        "Another public/Developer InstaCleaner action job is active. "
                        "Finish or pause that robot before starting a new batch.")
                self.handle = (kernel32, handle)
            else:
                import fcntl
                flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
                fd = os.open(self.root / ".instagram-action-admission.lock", flags, 0o600)
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    os.close(fd)
                    raise ActionSessionBusy(
                        "Another public/Developer InstaCleaner action job is active. "
                        "Finish or pause that robot before starting a new batch.")
                except BaseException:
                    os.close(fd)
                    raise
                self.handle = fd
        except ActionSessionBusy:
            raise
        except OSError as exc:
            raise ActionSessionBusy(
                "Cannot prove exclusive access to the Instagram action journal; "
                "no job started.") from exc
        return self

    def release(self):
        if self._released:
            return
        self._released = True
        if self.handle is None:
            return
        if sys.platform == "win32":
            kernel32, handle = self.handle
            kernel32.ReleaseSemaphore(handle, 1, None)
            kernel32.CloseHandle(handle)
        else:
            import fcntl
            fcntl.flock(self.handle, fcntl.LOCK_UN)
            os.close(self.handle)
        self.handle = None
