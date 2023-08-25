import ctypes
from ctypes import wintypes
# using pywin32 for constants and ctypes for everything else seems a little
# indecisive, but whatevs.
import win32con

import logging
from typing import Optional

user32 = ctypes.windll.user32
ole32 = ctypes.windll.ole32
kernel32 = ctypes.windll.kernel32

WinEventProcType = ctypes.WINFUNCTYPE(
    None,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.HWND,
    wintypes.LONG,
    wintypes.LONG,
    wintypes.DWORD,
    wintypes.DWORD
)

HWINEVENTHOOK = wintypes.HANDLE

# limited information would be sufficient, but our platform doesn't have it.
PROCESS_FLAG = getattr(win32con, 'PROCESS_QUERY_LIMITED_INFORMATION',
                       win32con.PROCESS_QUERY_INFORMATION)

THREAD_FLAG = getattr(win32con, 'THREAD_QUERY_LIMITED_INFORMATION',
                      win32con.THREAD_QUERY_INFORMATION)


def get_process_filename(process_id: int, log_error=True) -> Optional[str]:
    """Returns the full process path for the given process_id, or None on error."""
    handle_process = kernel32.OpenProcess(PROCESS_FLAG, 0, process_id)
    if not handle_process:
        if log_error:
            logging.error("OpenProcess(%s) failed: %s", process_id, ctypes.WinError())
        return None

    try:
        filename_buffer = wintypes.DWORD(4096)
        filename = ctypes.create_unicode_buffer(filename_buffer.value)
        kernel32.QueryFullProcessImageNameW(handle_process, 0, ctypes.byref(filename),
                                            ctypes.byref(filename_buffer))

        return filename.value
    finally:
        kernel32.CloseHandle(handle_process)


def get_hwnd_process_id(event_thread_id: int, hwnd: wintypes.HWND, log_error=True) -> Optional[int]:
    """Returns the processId of the given window handle in the given thread, or None on error."""
    if not hwnd and not event_thread_id:
        return None

    # It's possible to have a window we can get a PID out of when the thread
    # isn't accessible, but it's also possible to get called with no window,
    # so we have two approaches.
    errors = []
    errors_args = []
    thread_handle = kernel32.OpenThread(THREAD_FLAG, 0, event_thread_id)
    process_id = None
    if thread_handle:
        try:
            process_id = kernel32.GetProcessIdOfThread(thread_handle)
            if process_id:
                return process_id
            else:
                errors.append("GetProcessIdOfThread(%s): %s")
                errors_args.extend([thread_handle, ctypes.WinError()])
        finally:
            kernel32.CloseHandle(thread_handle)

    if hwnd:
        process_id_value = wintypes.DWORD()
        thread_id = user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id_value))
        if thread_id != event_thread_id:
            errors.append('Window thread != event thread? %s != %s')
            errors_args.extend([thread_id, event_thread_id])
        if process_id_value:
            process_id = process_id_value.value
        else:
            errors.append('GetWindowThreadProcessID(%s): %s')
            errors_args.extend([hwnd, ctypes.WinError()])

    if not process_id and log_error:
        error_detail = '; '.join(errors)
        logging.error("Couldn't get process id from either hwnd=%s or thread id=%s: " + error_detail,
                      hwnd, event_thread_id, *errors_args)
    return process_id


def get_window_title(hwnd: wintypes.HWND) -> str:
    """Returns the window title of the given window handle, or an empty string on error."""
    length = user32.GetWindowTextLengthW(hwnd)
    title = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, title, length + 1)
    return title.value


SetWinEventHook = user32.SetWinEventHook
SetWinEventHook.argtypes = [
    wintypes.DWORD,  # eventMin
    wintypes.DWORD,  # eventMax
    wintypes.HMODULE,  # hmodWinEventProc
    WinEventProcType,  # pfnWinEventProc
    wintypes.DWORD,  # idProcess
    wintypes.DWORD,  # idThread
    wintypes.DWORD  # dwFlags
]
SetWinEventHook.restype = HWINEVENTHOOK


def set_win_event_hook(win_event_proc: WinEventProcType, event_type: int) -> HWINEVENTHOOK:
    """Set a global event hook for the given event_type.

    Throws an OSError exception on failure created by ctypes.WinError().

    :param win_event_proc: callback called when an event occurs.
    :param event_type: event id to hook. See https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants
    :return: registered event hook handle.
    """
    win_event_hook_handle = SetWinEventHook(
        event_type, event_type, 0, win_event_proc, 0, 0, win32con.WINEVENT_OUTOFCONTEXT)
    if not win_event_hook_handle:
        raise ctypes.WinError()
    return win_event_hook_handle


def unhook_win_event(win_event_hook_handle: HWINEVENTHOOK) -> bool:
    """Removes the hook set by set_win_event_hook()."""
    UnhookWinEvent = user32.UnhookWinEvent
    UnhookWinEvent.argtypes = [HWINEVENTHOOK]
    UnhookWinEvent.restype = wintypes.BOOL
    return UnhookWinEvent(win_event_hook_handle) != 0
