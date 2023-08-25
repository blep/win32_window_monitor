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
eventTypes = {
    win32con.EVENT_SYSTEM_FOREGROUND: "Foreground",
    win32con.EVENT_OBJECT_FOCUS: "Focus",
    win32con.EVENT_OBJECT_SHOW: "Show",
    win32con.EVENT_SYSTEM_DIALOGSTART: "Dialog",
    win32con.EVENT_SYSTEM_CAPTURESTART: "Capture",
    win32con.EVENT_SYSTEM_MINIMIZEEND: "UnMinimize"
}

# store last event time for displaying time between events
lastTime = 0


def log(msg):
    print(msg)


def logError(msg):
    sys.stdout.write(msg + '\n')


def callback(win_event_hook_handle, event_id: int, hwnd, id_object, id_child, event_thread_id,
             event_time_ms):
    global lastTime
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

    log(u"%s:%04.2f\t%-10s\t"
        u"W:%-8s\tP:%-8d\tT:%-8d\t"
        u"%s\t%s" % (
            event_time_ms, float(event_time_ms - lastTime) / 1000, eventTypes.get(event_id, hex(event_id)),
            hwnd, process_id or -1, event_thread_id or -1,
            short_name, title))

    lastTime = event_time_ms


def main():
    ole32.CoInitialize(0)

    win_event_proc = WinEventProcType(callback)

    event_hook_handles = [set_win_event_hook(win_event_proc, et) for et in eventTypes.keys()]

    msg = ctypes.wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
        user32.TranslateMessageW(msg)
        user32.DispatchMessageW(msg)

    for hook_handle in event_hook_handles:
        user32.UnhookWinEvent(hook_handle)
    ole32.CoUninitialize()


if __name__ == '__main__':
    main()
