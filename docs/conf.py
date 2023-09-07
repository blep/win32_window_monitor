from sphinx.application import Sphinx
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

autodoc_default_options = {
    'exclude-members': 'FORCE_HEX_REPR',  # Exclude NamedInt.FORCE_HEX_REPR
    # TODO revist this, we want documented method to be in the doc
    #    'special-members': '__init_subclass__, __eq__, __hash__',
}

autodoc_default_flags = ['members']

def custom_autodoc_skip_filter(app: Sphinx, what: str, name: str, obj: object,
                               skip: bool, options: dict) -> bool:
    """
    Keeps default 'include' behavior the same, but also includes class members and attributes
    that have a specific docstring.

    Args:
        app: The Sphinx application.
        what: The type of object being documented.
        name: The name of the object.
        obj: The object being documented.
        skip: The current skip status.
        options: Additional options.

    Returns:
        bool: True to skip the member, False to include it in the documentation.
    """
    app.info(f"Skip={skip} for '{name}' based on custom filter.")
    if not skip:
        return False

    if what in ('method', 'attribute', 'property', 'descriptor', 'classmethod', 'staticmethod'):
        if hasattr(obj, '__doc__'):
            return False
            # parent_classes = obj.__objclass__.__bases__
            # if not any(getattr(parent, '__doc__', None) == obj.__doc__ for parent in parent_classes):
            #     return False

    return skip


def setup(app):
    app.connect('autodoc-skip-member', custom_autodoc_skip_filter)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']
