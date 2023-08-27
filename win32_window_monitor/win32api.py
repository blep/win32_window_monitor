import contextlib
import ctypes
import logging
import signal
from ctypes import wintypes
from typing import Optional
from typing import Union

from .ids import HookEvent

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

# Relevant Windows SDK constant

THREAD_QUERY_LIMITED_INFORMATION = 2048
PROCESS_QUERY_LIMITED_INFORMATION = 4096
WINEVENT_OUTOFCONTEXT = 0
WINEVENT_SKIPOWNTHREAD = 1
WINEVENT_SKIPOWNPROCESS = 2
WINEVENT_INCONTEXT = 4

# Could fallback on PROCESS_QUERY_INFORMATION and THREAD_QUERY_INFORMATION for xP
PROCESS_FLAG = PROCESS_QUERY_LIMITED_INFORMATION
THREAD_FLAG = THREAD_QUERY_LIMITED_INFORMATION


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


def get_hwnd_process_id(event_thread_id: wintypes.DWORD, hwnd: wintypes.HWND, log_error=True) -> Optional[int]:
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


def set_win_event_hook(win_event_proc: WinEventProcType, event_type: Union[int, HookEvent]) -> HWINEVENTHOOK:
    """Set a global event hook for the given event_type.

    Throws an OSError exception on failure created by ctypes.WinError().

    See https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook for detail.

    :param win_event_proc: callback called when an event occurs.
    :param event_type: event id to hook. See https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants
    :return: registered event hook handle.
    """
    win_event_hook_handle = SetWinEventHook(
        event_type, int(event_type), 0, win_event_proc, 0, 0, WINEVENT_OUTOFCONTEXT)
    if not win_event_hook_handle:
        raise ctypes.WinError()
    return win_event_hook_handle


UnhookWinEvent = user32.UnhookWinEvent
UnhookWinEvent.argtypes = [HWINEVENTHOOK]
UnhookWinEvent.restype = wintypes.BOOL


def unhook_win_event(win_event_hook_handle: HWINEVENTHOOK) -> bool:
    """Removes the hook set by set_win_event_hook()."""
    return UnhookWinEvent(win_event_hook_handle) != 0


@contextlib.contextmanager
def init_com():
    ole32.CoInitialize(0)
    try:
        yield
    finally:
        ole32.CoUninitialize()


def run_message_loop():
    """
    Runs WIN32 message loop (user32.GetMessageW) until WM_QUIT is received.
    :return:
    """
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)


PostQuitMessage = user32.PostQuitMessage
PostQuitMessage.argtypes = [ctypes.c_int]
PostQuitMessage.restype = None


def post_quit_message(exit_code: int = 0):
    PostQuitMessage(exit_code)


@contextlib.contextmanager
def post_quit_message_on_break_signal():
    """Install signal handler to exit the application when CTRL+C or CTRL+Break is pressed.

    Exiting the application is done by sending the WM_QUIT message (via post_quit_message),
    which causes the Windows message loop of run_message_loop() that receives it to exit.

    This is a contextmanager for use with the with statement.
    """
    def signal_handler_post_quit_message(signum, stack_frame):
        post_quit_message()

    old_break_handler = signal.getsignal(signal.SIGBREAK)
    signal.signal(signal.SIGBREAK, signal_handler_post_quit_message)
    old_int_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal_handler_post_quit_message)

    yield

    # Restore the old signal handlers on exit
    signal.signal(signal.SIGINT, old_int_handler)
    signal.signal(signal.SIGBREAK, old_break_handler)
