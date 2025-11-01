import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

# Read version from pyproject.toml
try:
    import tomllib
except ImportError:
    # Python < 3.11
    import tomli as tomllib

project_root = Path(__file__).parent.parent
pyproject_path = project_root / "pyproject.toml"

with pyproject_path.open("rb") as f:
    pyproject_data = tomllib.load(f)
    version = pyproject_data["project"]["version"]
    release = version

project = "pytoon"
copyright = "2025, TOON Contributors"
author = "TOON Contributors"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

html_theme = "furo"
html_title = "pytoon Documentation"
html_short_title = "pytoon"
html_static_path = ["_static"]
html_show_sourcelink = True

html_theme_options = {
    "sidebar_hide_name": False,
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#1e40af",
    },
    "dark_css_variables": {
        "color-brand-primary": "#60a5fa",
        "color-brand-content": "#93c5fd",
    },
}

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_member_order = "bysource"

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

pygments_style = "sphinx"

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]
