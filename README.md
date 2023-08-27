# win32_window_monitor

Monitor change of the focused window on Windows Operating System.

Reports the focused window HWND, pid and executable path to a python callback
registered
using [SetWinEventHook](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook).

Provides helpers function to easily retrieve process id and path from the
callback parameters.

# Example

The main.py shows how to use the API to produce the example output below. After
installing the `win32-window-monitor` package, the script `log_focused_window` is installed.

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

Columns content:

- event time_ms : elapsed second since last event
- event
- W: HWND, the window handle
- P: process id
- T: thread id
- short process path
- window title

Action made to produce this event:
- Bring Firefox window to focus by click on it in the Taskbar. Events with `explorer.exe` are interactions with the Taskbar.
- Bring Notion app to focus by click on it in the Taskbar.
- Bring back cmd.exe to focus by click on it in the Taskbar.

# Usage example

IMPORTANT: you need more than just SYSTEM_FOREGROUND to capture all
events that bring a window to the foreground. SYSTEM_FOREGROUND for
example is not generated when restoring a minimized window.

```python
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
    # - init_com(): initialize Windows COM (CoInitialize)
    # - post_quit_message_on_break_signal: signal handlers to exit the
    # application when CTRL+C or CTRL+Break is pressed.
    with init_com(), post_quit_message_on_break_signal():
        # Converts the callback to the ctype function type, and register it.
        win_event_proc = WinEventProcType(on_event)
        event_hook_handle = set_win_event_hook(win_event_proc, HookEvent.SYSTEM_FOREGROUND)

        # Run Windows message loop until WM_QUIT message is received (send by signal handlers above).
        # If you have a graphic UI, it is likely that your application already has a Windows message
        # loop that should be used instead.
        run_message_loop()

        unhook_win_event(event_hook_handle)

if __name__ == '__main__':
    main()
```

# Acknowledgment

This project core is heavily based on the work of others:

- Kevin Turner: [GIST](https://gist.github.com/keturn/6695625) providing an excellent starting base for this project.
- Eric
  Blade: [getting process name from window handle](https://mail.python.org/pipermail/python-win32/2009-July/009381.html)
- David
  Heffernan: [using WIN32 SetWinEventHook with ctypes](https://stackoverflow.com/questions/15849564/how-to-use-winapi-setwineventhook-in-python/15898768#15898768-
  David
  Heffernan: [using WIN32 SetWinEventHook with ctypes](https://stackoverflow.com/questions/15849564/how-to-use-winapi-setwineventhook-in-python/15898768#15898768)