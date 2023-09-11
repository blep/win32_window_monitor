# win32_window_monitor

Monitor global window [events](https://learn.microsoft.com/en-us/windows/win32/winauto/event-constants)
on Windows O.S. using the [SetWinEventHook](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook) 
WIN32 SDK API:

- Reports the event's window HWND, PID (process identifier) and executable path to a python callback.

- Provides helper functions to easily retrieve the PID and executable path from
  the callback parameters.

## Use cases

- Tracks the focused window and its process
- Tracks windows that capture the mouse or keyboard input
- Tracks which process is causing your fullscreen game to lose focus (Kevin Turner's initial motivation for his gist)
- ... (there are lots of UI Automation related events that could be useful)

Since the standard HWND and PID are readily available, you can utilize
existing Python modules to interact with either the window or the process.

## log_focused_window script to log focus related events

`main.py` shows how to use the API to produce the example output below. After
installing the `win32-window-monitor` package, the script `log_focused_window` is installed (in 
`venv\Scripts\log_focused_window.exe`, which is added to the `PATH` when activating the venv).

```bat
pip install win32-window-monitor
log_focused_window
```

which produces the following output:

```text
101307546:0.00  Capture         W:0x1014c       P:7440          T:7592          Windows\explorer.exe    Running applications
101307687:0.14  Foreground      W:0x903ce       P:2508          T:1988          net\firefox.exe blep/win32_window_monitor: Monitor change of the focused window on Windows O.S.. Reports the focused window HWND, pid and executable to a Python callback. — Mozilla Firefox
101307687:0.00  Focus           W:0x903ce       P:2508          T:1988          net\firefox.exe blep/win32_window_monitor: Monitor change of the focused window on Windows O.S.. Reports the focused window HWND, pid and executable to a Python callback. — Mozilla Firefox
101312015:4.33  Show            W:0xc080c       P:7440          T:7592          Windows\explorer.exe
101312015:0.00  Show            W:0x10150       P:7440          T:7592          Windows\explorer.exe
101312031:0.02  Show            W:0x1065e       P:12428         T:11660         Notion\Notion.exe       Chrome Legacy Window
101312312:0.28  Capture         W:0x1014c       P:7440          T:7592          Windows\explorer.exe    Running applications
101312468:0.16  Foreground      W:0x20642       P:12428         T:11660         Notion\Notion.exe       Python: automated CI/Release/doc/Wheel
101312484:0.02  Focus           W:0x20642       P:12428         T:11660         Notion\Notion.exe       Python: automated CI/Release/doc/Wheel
101312484:0.00  Show            W:0x20642       P:12428         T:11660         Notion\Notion.exe       Python: automated CI/Release/doc/Wheel
101314312:1.83  Capture         W:0x1014c       P:7440          T:7592          Windows\explorer.exe    Running applications
101314421:0.11  Foreground      W:0x440820      P:16088         T:7192          System32\conhost.exe    C:\Windows\System32\cmd.exe - python  -m win32_window_monitor.main
101314437:0.02  Focus           W:0x440820      P:16088         T:7192          System32\conhost.exe    C:\Windows\System32\cmd.exe - python  -m win32_window_monitor.main
```

Columns content
----------------

- event time_ms : elapsed seconds since last event
- event
- W: HWND, the window handle
- P: process ID
- T: thread ID
- short process path
- window title

Actions made to produce those events
------------------------------------

- Bring Firefox window to focus by clicking on it in the Taskbar. Events with
`explorer.exe` are interactions with the Taskbar.
- Bring Notion app to focus by clicking on it in the Taskbar.
- Bring back cmd.exe to focus by clicking on it in the Taskbar.


## Usage example

IMPORTANT: to track the current foreground window, you need at least HookEvent.SYSTEM_FOREGROUND and
HookEvent.SYSTEM_MINIMIZEEND (SYSTEM_FOREGROUND for is not sent when restoring a minimized window).

```python
# win32_window_monitor/main_usage_example.py
from win32_window_monitor import *
from ctypes import wintypes


def on_event(win_event_hook_handle: HWINEVENTHOOK, event_id: int, hwnd: wintypes.HWND,
             id_object: wintypes.LONG, id_child: wintypes.LONG,
             event_thread_id: wintypes.DWORD,
             event_time_ms: wintypes.DWORD):
    # Called from the thread running the Windows message loop.
    # HookEvent provides a nice str, and unlike enum.Enum accepts any integer value.
    event_id = HookEvent(event_id)
    title = get_window_title(hwnd)
    process_id = get_hwnd_process_id(event_thread_id, hwnd)
    exe_path = get_process_filename(process_id) if process_id else '?'
    print(f'{event_time_ms} {event_id} P{process_id} {exe_path} {title}')


def main():
    # - init_com(): Initialize Windows COM (CoInitialize)
    # - post_quit_message_on_break_signal: Signal handlers to exit the
    # application when CTRL+C or CTRL+Break are pressed.
    with init_com(), post_quit_message_on_break_signal():
        # We must keep the event_hook_handle alive. Failure to do that may
        # cause a crash as the "trampoline" function generated by ctypes for
        # the event hook would be deleted.
        event_hook_handle = set_win_event_hook(on_event, HookEvent.SYSTEM_FOREGROUND)

        # Run the Windows message loop until the WM_QUIT message is received
        # (sent by signal handlers above). If you have a graphic UI (TkInter, Qt...), it is
        # likely that your application already has a Windows message loop that
        # should be used instead.
        run_message_loop()

        unhook_win_event(event_hook_handle)


if __name__ == '__main__':
    main()
```

## Acknowledgments

This project core is heavily based on the work of others:

- Kevin Turner: [GIST](https://gist.github.com/keturn/6695625) providing an excellent starting base for this project.
- Eric Blade: [getting process name from window handle](https://mail.python.org/pipermail/python-win32/2009-July/009381.html)
- David Heffernan: [using WIN32 SetWinEventHook with ctypes](https://stackoverflow.com/questions/15849564/how-to-use-winapi-setwineventhook-in-python/15898768#15898768-
