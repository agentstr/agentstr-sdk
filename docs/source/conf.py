# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import datetime

# -- Project information -----------------------------------------------------
project = "Agentstr SDK"
copyright = f"{datetime.datetime.now().year}, Agentstr. All rights reserved."
author = "Agentstr"

# -- General configuration ---------------------------------------------------
from pathlib import Path

# Get the project root dir, which is the parent dir of this
sys.path.insert(0, os.path.abspath("../.."))

# Package info
package_name = "agentstr"
package_path = Path("../../src") / package_name

# Add package to path
sys.path.insert(0, str(package_path.parent))

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.autodoc_pydantic",
    "sphinx_click",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "exclude-members": "__weakref__",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_title = "Agentstr Docs"
html_static_path = ["_static"]
# Use the same favicon for all pages
html_favicon = "_static/favicon.ico"
html_theme_options = {
    "light_logo": "favicon.ico",
    "dark_logo": "favicon.ico",
    "sidebar_hide_name": False, 
}

# Add custom CSS
html_css_files = [
    "custom.css",
]

# -- Autodoc configuration ---------------------------------------------------
def maybe_skip_member(app, what, name, obj, skip, options):
    if name in ["__weakref__", "__doc__", "__module__"]:
        return True
    return skip

def setup(app):
    app.connect("autodoc-skip-member", maybe_skip_member)
