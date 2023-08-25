import platform
import sys
import time
from threading import Thread
from queue import Queue

if platform.system() != "Windows":
    print("Unsupported platform!")
    sys.exit(0)

from ._win32_window_monitor import WindowFocusListener


def main():
    event_queue = Queue()
    listener = WindowFocusListener(event_queue)
    listener.start()
    listener_thread = Thread(target=listener.run, args=(), daemon=True)
    listener_thread.start()

    try:
        while True:
            window_event = event_queue.get()
            hwnd, pid, title = window_event.hwnd, window_event.pid, window_event.title
            print(f'Window event: hwnd={hwnd}, pid={pid}, title={title}')

            # process = psutil.Process(pid)
            # exe_path = process.exe
    finally:
        listener.stop()


if __name__ == "__main__":
    main()
