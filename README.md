# WIN32 Window Monitor

Report changes of the focused window on Windows O.S. to a Python callback with 
window HWND, pid and executable to a Python callback.

Example:

TODO

TODO:
- uses psutil to retrieve executable full path.
- need to hook another event type: https://stackoverflow.com/questions/30999516/how-to-use-setwineventhook-function-to-get-active-window-changed-message
EVENT_SYSTEM_MINIMIZEEND is sent when a window is restored 
https://github.com/bryphe/node-process-windows/issues/1
- You may also need EVENT_SYSTEM_MINIMIZESTART and EVENT_SYSTEM_MINIMIZEEND
- Arg, found someone that did it in Python using ctypes (somehow did not manage to find it initialy):
  https://gist.github.com/keturn/6695625

# Building this project

## Building the Cython extension

https://cython.readthedocs.io/en/latest/src/quickstart/build.html
https://shwina.github.io/cython-testing/

To build `_win32_window_monitor.pyx` extension:
```bash
python  setup.py build_ext --inplace
````

The easiest way to integrate in PyCharm, is to create an stand-alone 
Run Configuration for Python script, named `Compile Cython`, 
executing the script `setup.py` with parameters `build_ext --inplace`
in the project root directory.

Creates the Run Configuration that execute Python module `win32_window_monitor.main`
with "Modify Options > Before Launch > Add before Launch" > Run Configuration > `Compile Cython`
that we created above.

This will ensure that the extension is recompiled when 
modified before running main.

# Releasing

python setup.py sdist bdist_wheel
twine upload dist/*