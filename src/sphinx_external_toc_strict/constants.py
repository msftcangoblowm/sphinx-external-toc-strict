"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Separate constants out so independent of any dependencies

"""

from ._version import __version__
from .version_semantic import (
    readthedocs_url,
    sanitize_tag,
)

__all__ = (
    "g_app_name",
    "__version_app",
    "__url__",
    "URL_PATTERN",
    "DEFAULT_SUBTREES_KEY",
    "DEFAULT_ITEMS_KEY",
    "FILE_FORMAT_KEY",
    "ROOT_KEY",
    "FILE_KEY",
    "GLOB_KEY",
    "REF_KEY",
    "URL_KEY",
    "TOCTREE_OPTIONS",
    "use_cases",
)

#: str: package name underscores not hyphens
g_app_name = "sphinx_external_toc_strict"

# Pattern used to match URL items.
# regex should match sphinx.util.url_re
#: str: regex used to parse URLs
URL_PATTERN = r".+://.*"

#: str: Default subtrees key. Overridden for jb-book and jb-article
DEFAULT_SUBTREES_KEY = "subtrees"
#: str: Items can contain: ``- file:``, ``- url:``, or ``- glob:`` item
DEFAULT_ITEMS_KEY = "entries"
#: str: file format / use case key
FILE_FORMAT_KEY = "format"
#: str: key for root document
ROOT_KEY = "root"
#: str: Default file key
FILE_KEY = "file"
#: str: Default url key
GLOB_KEY = "glob"
#: str: Default intersphinx reference id lookup key
REF_KEY = "ref"
#: str: Default url key
URL_KEY = "url"

#: tuple[str, ...]: Possible options' key
TOCTREE_OPTIONS = (
    "caption",
    "hidden",
    "maxdepth",
    "numbered",
    "reversed",
    "titlesonly",
)

#: tuple[str, ...]: All supported file formats / uses cases
use_cases = ("default", "jb-book", "jb-article")

# Removes epoch and local. Fixes version
__version_app = sanitize_tag(__version__)
__url__ = readthedocs_url(g_app_name, ver_=__version__)
