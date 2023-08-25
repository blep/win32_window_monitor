# win32_window_monitor
Monitor change of the focused window on Windows Operating System.

Reports the focused window HWND, pid and executable path.

# Acknowledgment

This project core is heavily based on the work of others:

- Kevin Turner: [GIST](https://gist.github.com/keturn/6695625) providing an excellent starting base for this project.
- Eric Blade: [getting process name from window handle](https://mail.python.org/pipermail/python-win32/2009-July/009381.html)  
- David Heffernan: [using WIN32 SetWinEventHook with ctypes](https://stackoverflow.com/questions/15849564/how-to-use-winapi-setwineventhook-in-python/15898768#15898768- David Heffernan: [using WIN32 SetWinEventHook with ctypes](https://stackoverflow.com/questions/15849564/how-to-use-winapi-setwineventhook-in-python/15898768#15898768)