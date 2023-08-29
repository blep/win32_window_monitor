.. win32-window-monitor documentation master file, created by
   sphinx-quickstart on Sun Aug 27 11:12:24 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

win32-window-monitor
====================

Monitor change of the focused window on Windows Operating System:

- Reports the focused window HWND, pid and executable path to a python callback
  registered using `SetWinEventHook <https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwineventhook>`_.

- Provides helpers function to easily retrieve process id and path from the
  callback parameters.

Example
=======

The main.py shows how to use the API to produce the example output below. After
installing the ``win32-window-monitor`` package, the script ``log_focused_window``
is installed.

.. code-block:: batch

   pip install win32-window-monitor
   log_focused_window

which produces the following output:

.. code-block:: text

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

Columns content:

- event time_ms : elapsed second since last event
- event
- W: HWND, the window handle
- P: process id
- T: thread id
- short process path
- window title

Actions made to produce this event:
- Bring Firefox window to focus by click on it in the Taskbar. Events with `explorer.exe` are interactions with the Taskbar.
- Bring Notion app to focus by click on it in the Taskbar.
- Bring back cmd.exe to focus by click on it in the Taskbar.

Usage example
=============

IMPORTANT: you need more than just SYSTEM_FOREGROUND to capture all
events that bring a window to the foreground. SYSTEM_FOREGROUND for
example is not generated when restoring a minimized window.

.. literalinclude:: ../win32_window_monitor/main_usage_example.py



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api

.. include ../README.md


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
