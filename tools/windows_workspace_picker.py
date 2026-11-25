"""Native Windows workspace selector: two app windows, one login each.

The existing Chrome user-data directory is NEVER moved or deleted. A second
directory hosts a genuinely independent InstaCleaner login/storage profile.
This chooser does not authenticate Instagram and never probes browser cookies.
"""
from __future__ import annotations

from pathlib import Path
import sys

WORKSPACES = ("primary", "secondary")


def chrome_workspace_path(home: Path, workspace: str) -> Path:
    """Preserve the installed v120.80 Chrome profile path for the first window."""
    if workspace not in WORKSPACES:
        raise ValueError("Choose a supported InstaCleaner window.")
    return Path(home) / ("workspace-browser" if workspace == "primary"
                         else "workspace-browser-secondary")



def instagram_robot_session_path(home: Path, workspace: str) -> Path:
    """Preserve the ORIGINAL robot browser for window 1; isolate window 2.

    The canonical action/WAL directory stays common and remains independently
    scoped by owner/account. This path is ONLY the persistent Chrome session
    root; it must never be copied, migrated or deleted when opening a slot.
    """
    if workspace not in WORKSPACES:
        raise ValueError("Choose a supported InstaCleaner window.")
    return Path(home) / ("instagram-browser" if workspace == "primary"
                         else "instagram-browser-secondary")


def ui_document_path(home: Path, workspace: str, filename: str = "IG-Cleaner-Pro.html") -> Path:
    """Keep the original file:// origin for account 1; isolate account 2."""
    if workspace not in WORKSPACES:
        raise ValueError("Invalid InstaCleaner window identity.")
    if filename in ("", ".", "..") or "/" in filename or "\\" in filename:
        raise ValueError("Invalid UI filename.")
    return Path(home) / filename if workspace == "primary" else (
        Path(home) / "second-window" / filename)

def instance_mutex_name(workspace: str, *, developer: bool = False) -> str:
    if workspace not in WORKSPACES:
        raise ValueError("Invalid InstaCleaner window identity.")
    prefix = "Local\\MichelsLab_InstaCleanerPro_Developer" if developer else (
        "Local\\MichelsLab_InstaCleanerPro_Desktop")
    return prefix + ("_SecondWindow" if workspace == "secondary" else "")


def workspace_is_open(workspace: str, *, developer: bool = False) -> bool:
    """Read the existing named mutex without creating/reserving an app slot."""
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenMutexW.argtypes = [ctypes.c_uint32, ctypes.c_bool, ctypes.c_wchar_p]
    kernel32.OpenMutexW.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel32.CloseHandle.restype = ctypes.c_bool
    handle = kernel32.OpenMutexW(0x00100000, False,
                                instance_mutex_name(workspace, developer=developer))
    if handle:
        kernel32.CloseHandle(handle)
        return True
    error = ctypes.get_last_error()
    if error == 2:  # ERROR_FILE_NOT_FOUND: genuinely absent
        return False
    # Access denied or an unexpected probe failure is not evidence of a free slot.
    # The authoritative CreateMutexW gate still runs at actual launch.
    return True


def select_workspace(*, developer: bool = False, _smoke_cancel: bool = False) -> str | None:
    """Use a labeled Windows task dialog rather than ambiguous Yes/No buttons.

    Cancel returns None and does not touch user data or start the browser.
    Launching the program again displays the same chooser for another window.
    """
    if sys.platform != "win32":
        raise RuntimeError("The native Windows account chooser requires Windows.")

    import ctypes
    from ctypes import wintypes

    class TaskDialogButton(ctypes.Structure):
        _pack_ = 1  # commctrl.h uses byte-packed task-dialog structures.
        _fields_ = [("nButtonID", ctypes.c_int), ("pszButtonText", wintypes.LPCWSTR)]

    class TaskDialogConfig(ctypes.Structure):
        _pack_ = 1
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("hwndParent", wintypes.HWND),
            ("hInstance", wintypes.HINSTANCE),
            ("dwFlags", wintypes.UINT),
            ("dwCommonButtons", wintypes.UINT),
            ("pszWindowTitle", wintypes.LPCWSTR),
            ("pszMainIcon", ctypes.c_void_p),
            ("pszMainInstruction", wintypes.LPCWSTR),
            ("pszContent", wintypes.LPCWSTR),
            ("cButtons", wintypes.UINT),
            ("pButtons", ctypes.POINTER(TaskDialogButton)),
            ("nDefaultButton", ctypes.c_int),
            ("cRadioButtons", wintypes.UINT),
            ("pRadioButtons", ctypes.c_void_p),
            ("nDefaultRadioButton", ctypes.c_int),
            ("pszVerificationText", wintypes.LPCWSTR),
            ("pszExpandedInformation", wintypes.LPCWSTR),
            ("pszExpandedControlText", wintypes.LPCWSTR),
            ("pszCollapsedControlText", wintypes.LPCWSTR),
            ("pszFooterIcon", ctypes.c_void_p),
            ("pszFooter", wintypes.LPCWSTR),
            ("pfCallback", ctypes.c_void_p),
            ("lpCallbackData", ctypes.c_ssize_t),
            ("cxWidth", wintypes.UINT),
        ]

    labels = {
        "primary": (101, "Primary account\nKeep your existing session"),
        "secondary": (102, "Second account\nOpen its independent session"),
    }
    free = [slot for slot in WORKSPACES
            if not workspace_is_open(slot, developer=developer)]
    busy = [slot for slot in WORKSPACES if slot not in free]
    buttons = (TaskDialogButton * len(free))(
        *(TaskDialogButton(*labels[slot]) for slot in free)
    )
    config = TaskDialogConfig()
    config.cbSize = ctypes.sizeof(TaskDialogConfig)
    # TDF_USE_COMMAND_LINKS and TDF_ALLOW_DIALOG_CANCELLATION
    config.dwFlags = 0x0010 | 0x0008
    config.dwCommonButtons = 0x0008  # Cancel
    config.pszWindowTitle = "Instagram Cleaner Pro"
    config.pszMainInstruction = ("Which account window do you want to open?"
                                if free else "Both account windows are already open")
    status = " ".join(
        ("Primary account" if slot == "primary" else "Second account") +
        ": already open or unavailable." for slot in busy
    )
    config.pszContent = (
        "Each window has its own sign-in and browser data. "
        + (status + " " if status else "")
        + ("Choose an available window, or cancel without changing anything."
           if free else "Use an existing window or close one before launching again.")
    )
    config.cButtons = len(free)
    config.pButtons = buttons if free else None
    config.nDefaultButton = labels[free[0]][0] if free else 2
    config.cxWidth = 260
    selected = ctypes.c_int(0)
    callback = None
    if _smoke_cancel:
        # Installed-binary CI only: exercise the real Win32 dialog and dismiss
        # it through its own Cancel command, without starting either workspace.
        post = ctypes.WinDLL("user32", use_last_error=True).PostMessageW
        post.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
        post.restype = wintypes.BOOL
        callback_type = ctypes.WINFUNCTYPE(ctypes.c_int32, wintypes.HWND,
                                            wintypes.UINT, ctypes.c_size_t,
                                            ctypes.c_ssize_t, ctypes.c_ssize_t)

        @callback_type
        def callback(hwnd, notification, *_args):
            if notification in (0, 4):  # TDN_CREATED / TDN_TIMER
                post(hwnd, 0x0400 + 102, 2, 0)  # TDM_CLICK_BUTTON / IDCANCEL
            return 0

        config.dwFlags |= 0x0800  # TDF_CALLBACK_TIMER
        config.pfCallback = ctypes.cast(callback, ctypes.c_void_p)
    try:
        call = ctypes.WinDLL("comctl32", use_last_error=True).TaskDialogIndirect
        call.argtypes = [ctypes.POINTER(TaskDialogConfig), ctypes.POINTER(ctypes.c_int),
                         ctypes.c_void_p, ctypes.c_void_p]
        call.restype = ctypes.c_int32  # HRESULT is signed 32-bit.
        result = call(ctypes.byref(config), ctypes.byref(selected), None, None)
    except (OSError, AttributeError):
        if _smoke_cancel:
            raise
        return fallback_workspace_dialog(free)
    if result != 0:
        if _smoke_cancel:
            raise RuntimeError(f'Native account chooser failed: HRESULT 0x{result & 0xffffffff:08X}')
        # A missing common-controls activation context or rejected ABI must
        # never make the installed app impossible to start. Preserve explicit
        # owner choice and Cancel; never silently pick a different account.
        return fallback_workspace_dialog(free)
    if _smoke_cancel and selected.value != 2:
        raise RuntimeError('Native account chooser did not return Cancel.')
    return next((slot for slot in free if labels[slot][0] == selected.value), None)

def fallback_workspace_dialog(free: list[str]) -> str | None:
    """Universal Win32 recovery when comctl32 TaskDialogIndirect fails."""
    import ctypes
    from ctypes import wintypes

    message_box = ctypes.WinDLL("user32", use_last_error=True).MessageBoxW
    message_box.argtypes = [wintypes.HWND, wintypes.LPCWSTR,
                            wintypes.LPCWSTR, wintypes.UINT]
    message_box.restype = ctypes.c_int
    title = "Insta Cleaner Pro"
    if not free:
        message_box(None, "Both account windows are already open or unavailable.",
                    title, 0x40)
        return None
    if len(free) == 1:
        name = "Primary account" if free[0] == "primary" else "Second account"
        result = message_box(None, "Open " + name + "?\n\nOK = Open; Cancel = Exit.",
                             title, 0x01 | 0x40 | 0x100)
        return free[0] if result == 1 else None
    result = message_box(
        None, "Choose your independent account window:\n\n"
              "Yes = Primary account (existing session)\n"
              "No = Second account (separate session)\n"
              "Cancel = Exit without changes.",
        title, 0x03 | 0x40 | 0x200)
    return {6: "primary", 7: "secondary"}.get(result)
