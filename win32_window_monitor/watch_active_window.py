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

from win32_window_monitor.win32api import *

# using pywin32 for constants and ctypes for everything else seems a little
# indecisive, but whatevs.
import win32con

import signal
import platform

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


class WindowEventLogger:
    def __init__(self):
        # store last event time for displaying time between events
        self.last_time = 0

    def on_event(self, win_event_hook_handle, event_id: int, hwnd: wintypes.HWND,
                 id_object: wintypes.LONG, id_child: wintypes.LONG,
                 event_thread_id: wintypes.DWORD,
                 event_time_ms: wintypes.DWORD):
        event_id = HookEvent(event_id)
        title = get_window_title(hwnd)

        process_id = get_hwnd_process_id(event_thread_id, hwnd)

        exe_short_name = '?'
        if process_id:
            filename = get_process_filename(process_id)
            if filename:
                exe_short_name = '\\'.join(filename.rsplit('\\', 2)[-2:])

        if hwnd:
            hwnd = hex(hwnd)
        elif id_object == win32con.OBJID_CURSOR:
            hwnd = '<Cursor>'

        elapsed_second = float(event_time_ms - self.last_time if self.last_time else 0) / 1000
        event_name = EVENT_TYPES.get(event_id, event_id.name)
        print("%s:%04.2f\t%-10s\t"
              "W:%-8s\tP:%-8d\tT:%-8d\t"
              "%s\t%s" % (
                  event_time_ms, elapsed_second, event_name,
                  hwnd, process_id or -1, event_thread_id or -1,
                  exe_short_name, title))

        self.last_time = event_time_ms


def main():
    with init_com():
        # Register hook callback for all relevant event types
        # Demonstrates that we can use a method as event hook callback without issue thanks
        # to ctypes.
        event_logger = WindowEventLogger()
        win_event_proc = WinEventProcType(event_logger.on_event)
        event_hook_handles = [set_win_event_hook(win_event_proc, et) for et in EVENT_TYPES.keys()]

        # Install signal handler to exit the application when CTRL+C or CTRL+Break is pressed
        def signal_handler(signum, frame):
            # Send WM_QUIT message to exit the message loop started below
            post_quit_message(0)

        if platform.system() == 'Windows':
            signal.signal(signal.SIGBREAK, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

        run_message_loop()

        for hook_handle in event_hook_handles:
            unhook_win_event(hook_handle)


if __name__ == '__main__':
    main()
