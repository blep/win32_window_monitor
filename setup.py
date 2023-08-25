from setuptools import setup, Extension
from Cython.Build import cythonize
import sys

# Only build the extension on Windows
if sys.platform == 'win32':
    extension = Extension(
        name="win32_window_monitor._win32_window_monitor",
        sources=["win32_window_monitor/_win32_window_monitor.pyx"],
        libraries=["user32", "ole32"],
        extra_compile_args=[], extra_link_args=[])
    extensions = cythonize([extension],
                           compiler_directives={'language_level': "3"}
                           )
else:
    extensions = []

setup(
    name="win32_window_monitor",
    ext_modules=extensions,
    zip_safe=False
)
