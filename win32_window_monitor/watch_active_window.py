"""Log window focus and appearance.

Written to try to debug some window popping up and stealing focus from my
Spelunky game for a split second.

Developed with 32-bit python on Windows 7. Might work in other environments,
but some of these APIs might not exist before Vista.

Much credit to Eric Blade for this:
https://mail.python.org/pipermail/python-win32/2009-July/009381.html
and David Heffernan:
http://stackoverflow.com/a/15898768/9585
"""

from .win32api import *

# using pywin32 for constants and ctypes for everything else seems a little
# indecisive, but whatevs.
import win32con

import sys
import ctypes
import ctypes.wintypes

# The types of events we want to listen for, and the names we'll use for
# them in the log output. Pick from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
EVENT_TYPES = {
    HookEvent.SYSTEM_FOREGROUND: "Foreground",
    HookEvent.OBJECT_FOCUS: "Focus",
    HookEvent.OBJECT_SHOW: "Show",
    HookEvent.SYSTEM_DIALOGSTART: "Dialog",
    HookEvent.SYSTEM_CAPTURESTART: "Capture",
    HookEvent.SYSTEM_MINIMIZEEND: "UnMinimize"
}

# store last event time for displaying time between events
last_time = 0


def log(msg):
    print(msg)


def win_event_hook_callback(win_event_hook_handle, event_id: int, hwnd: wintypes.HWND,
                            id_object: wintypes.LONG, id_child: wintypes.LONG,
                            event_thread_id: wintypes.DWORD,
                            event_time_ms: wintypes.DWORD):
    global last_time
    event_id = HookEvent(event_id)
    title = get_window_title(hwnd)

    process_id = get_hwnd_process_id(event_thread_id, hwnd)

    short_name = '?'
    if process_id:
        filename = get_process_filename(process_id)
        if filename:
            short_name = '\\'.join(filename.rsplit('\\', 2)[-2:])

    if hwnd:
        hwnd = hex(hwnd)
    elif id_object == win32con.OBJID_CURSOR:
        hwnd = '<Cursor>'

    elapsed_ms = event_time_ms - last_time if last_time else 0
    log(u"%s:%04.2f\t%-10s\t"
        u"W:%-8s\tP:%-8d\tT:%-8d\t"
        u"%s\t%s" % (
        event_time_ms, float(elapsed_ms) / 1000, EVENT_TYPES.get(event_id, hex(event_id)),
        hwnd, process_id or -1, event_thread_id or -1,
        short_name, title))

    last_time = event_time_ms


def main():
    ole32.CoInitialize(0)

    win_event_proc = WinEventProcType(win_event_hook_callback)

    event_hook_handles = [set_win_event_hook(win_event_proc, et) for et in EVENT_TYPES.keys()]

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    for hook_handle in event_hook_handles:
        user32.UnhookWinEvent(hook_handle)
    ole32.CoUninitialize()


if __name__ == '__main__':
    main()
