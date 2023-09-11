import sphinx_rtd_theme
import os
import sys
import typing

sys.path.insert(0, os.path.abspath('..'))

# Fix enum doc: `SYSTEM_FOREGROUND = 0x0003` instead of `SYSTEM_FOREGROUND = HookEvent.SYSTEM_FOREGROUND`
# See NamedInt.FORCE_HEX_STR
os.environ['SPHINX_NAMED_INT_FORCE_HEX_REPR'] = 'ON'


# Mock types to enable doc generation on Linux and provide type name that the developer use.
class MockWithDocName(typing.NewType):
    """Mock ctypes package as readthedocs.org only provides Linux machine for build, and ctypes.windll is not available.

    This also fix ctypes.wintypes.HANDLE being documented as ctypes.c_void_p, and similar for DWORD...
    """

    def __getattr__(self, name):
        if name not in self.__dict__:
            value = MockWithDocName(self.__name__ + '.' + name, typing.Any)
            setattr(self, name, value)
            return value
        return super().__getattribute__(name)

    def __repr__(self):
        return self.__name__


def win_func_type(restype, *argtypes):
    return typing.Callable[argtypes, restype]


import ctypes

ctypes.wintypes = MockWithDocName('wintypes', typing.Any)
ctypes.windll = MockWithDocName('windll', typing.Any)
ctypes.WINFUNCTYPE = win_func_type

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'win32-window-monitor'
copyright = '2023, Baptiste Lepilleur'
author = 'Baptiste Lepilleur'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "myst_parser",
]

# TODO check the napoleon extension which allow more compact/readable docstring:
# https://sphinxcontrib-napoleon.readthedocs.io/en/latest/


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# ensure that __all__ is not ignored
autosummary_imported_members = True

autodoc_default_options = {
    'exclude-members': 'FORCE_HEX_REPR',  # Exclude NamedInt.FORCE_HEX_REPR
    # TODO revist this, we want documented method to be in the doc
    #    'special-members': '__init_subclass__, __eq__, __hash__',
}

autodoc_default_flags = ['members']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
