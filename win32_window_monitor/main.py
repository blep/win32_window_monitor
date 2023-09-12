"""Log window focus and appearance using set_win_event_hook().
"""

from win32_window_monitor import *
from ctypes import wintypes

# The types of events we want to listen for, and the names we'll use for
# them in the log output. Pick from
# http://msdn.microsoft.com/en-us/library/windows/desktop/dd318066(v=vs.85).aspx
EVENT_TYPES = {
    HookEvent.SYSTEM_FOREGROUND: "Foreground",  # The foreground window has changed.
    HookEvent.OBJECT_FOCUS: "Focus",  # An object has received the keyboard focus.
    HookEvent.OBJECT_SHOW: "Show",  # A hidden object is shown.
    HookEvent.SYSTEM_DIALOGSTART: "Dialog",  # A dialog box has been displayed.
    HookEvent.SYSTEM_CAPTURESTART: "Capture",  # A window has received mouse capture.
    HookEvent.SYSTEM_MINIMIZEEND: "UnMinimize"  # A window object is about to be restored.
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
        elif id_object == ObjectId.CURSOR:
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
    with init_com(), post_quit_message_on_break_signal():
        # Register hook callback for all relevant event types
        # Demonstrates that we can use a method as event hook callback without issue thanks
        # to ctypes.
        event_logger = WindowEventLogger()
        event_hook_handles = [set_win_event_hook(event_logger.on_event, et) for et in EVENT_TYPES.keys()]

        # Run Windows message loop until WM_QUIT message is received (send by signal handlers above).
        # If you have a graphic UI, it is likely that your application already has a Windows message
        # loop that should be used instead.
        run_message_loop()

        for hook_handle in event_hook_handles:
            hook_handle.unhook()


if __name__ == '__main__':
    main()
