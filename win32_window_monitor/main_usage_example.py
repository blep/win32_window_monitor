"""Usage example included in README.md.
"""

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
