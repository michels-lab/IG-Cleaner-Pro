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


def instance_mutex_name(workspace: str, *, developer: bool = False) -> str:
    if workspace not in WORKSPACES:
        raise ValueError("Invalid InstaCleaner window identity.")
    prefix = "Local\\\\MichelsLab_InstaCleanerPro_Developer" if developer else (
        "Local\\\\MichelsLab_InstaCleanerPro_Desktop")
    return prefix + ("_SecondWindow" if workspace == "secondary" else "")


def select_workspace() -> str | None:
    """Use a labeled Windows task dialog rather than ambiguous Yes/No buttons.

    Cancel returns None and does not touch user data or start the browser.
    Launching the program again displays the same chooser for another window.
    """
    if sys.platform != "win32":
        raise RuntimeError("The native Windows account chooser requires Windows.")

    import ctypes
    from ctypes import wintypes

    class TaskDialogButton(ctypes.Structure):
        _fields_ = [("nButtonID", ctypes.c_int), ("pszButtonText", wintypes.LPCWSTR)]

    class TaskDialogConfig(ctypes.Structure):
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

    buttons = (TaskDialogButton * 2)(
        TaskDialogButton(101, "Cuenta principal\\nConserva tu sesión anterior"),
        TaskDialogButton(102, "Segunda cuenta\\nAbre una sesión totalmente independiente"),
    )
    config = TaskDialogConfig()
    config.cbSize = ctypes.sizeof(TaskDialogConfig)
    # TDF_USE_COMMAND_LINKS and TDF_ALLOW_DIALOG_CANCELLATION
    config.dwFlags = 0x0010 | 0x0008
    # TDCBF_CANCEL_BUTTON
    config.dwCommonButtons = 0x0008
    config.pszWindowTitle = "Instagram Cleaner Pro"
    config.pszMainInstruction = "¿Con qué cuenta quieres trabajar?"
    config.pszContent = (
        "Cada cuenta tiene su propia ventana, inicio de sesión y datos de navegador. "
        "Para abrir ambas, ejecuta InstaCleaner otra vez y elige la otra cuenta."
    )
    config.cButtons = 2
    config.pButtons = buttons
    config.nDefaultButton = 101
    config.cxWidth = 260
    selected = ctypes.c_int(0)
    call = ctypes.WinDLL("comctl32", use_last_error=True).TaskDialogIndirect
    call.argtypes = [ctypes.POINTER(TaskDialogConfig), ctypes.POINTER(ctypes.c_int),
                     ctypes.c_void_p, ctypes.c_void_p]
    call.restype = ctypes.c_long
    result = call(ctypes.byref(config), ctypes.byref(selected), None, None)
    if result < 0:
        raise RuntimeError("No se pudo abrir el selector de cuentas de Windows.")
    return {101: "primary", 102: "secondary"}.get(selected.value)
