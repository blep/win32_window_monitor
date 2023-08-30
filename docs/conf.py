import sphinx_rtd_theme
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# Fix enum doc: `SYSTEM_FOREGROUND = 0x0003` instead of `SYSTEM_FOREGROUND = HookEvent.SYSTEM_FOREGROUND`
# See NamedInt.FORCE_HEX_STR
os.environ['SPHINX_NAMED_INT_FORCE_HEX_REPR'] = 'ON'

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
