"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Seperate constants out so independent of any dependencies

.. py:data:: URL_PATTERN
   :type: str

   regex used to parse URLs

.. py:data:: DEFAULT_SUBTREES_KEY
   :type: str
   :value: "subtrees"

   Default subtrees key. Is overrided for jb-book and jb-article

.. py:data:: DEFAULT_ITEMS_KEY
   :type: str
   :value: "entries"

   Items can contain: ``- file:``, ``- url:``, or ``- glob:`` item

.. py:data:: FILE_FORMAT_KEY
   :type: str
   :value: "format"

   file format / use case key

.. py:data:: ROOT_KEY
   :type: str
   :value: "root"

   key for root document

.. py:data:: FILE_KEY
   :type: str
   :value: "file"

   Default file key

.. py:data:: GLOB_KEY
   :type: str
   :value: "glob"

   Default url key
.. py:data:: URL_KEY
   :type: str
   :value: "url"

   Default url key

.. py:data:: TOCTREE_OPTIONS
   :type: tuple[str, ...]
   :value: ("caption", "hidden", "maxdepth", "numbered", "reversed", "titlesonly")

   Possible options' key

.. py:data:: use_cases
   :type: tuple[str, ...]

   All supported file formats / uses cases

.. py:data:: __all__
   :type: tuple[str, str, str, str, str, str, str, str, str, str, str, str, str]
   :value: ("g_app_name", "__version_app", "__url__", "URL_PATTERN", \
   "DEFAULT_SUBTREES_KEY", "DEFAULT_ITEMS_KEY", "FILE_FORMAT_KEY", \
   "ROOT_KEY", "FILE_KEY", "GLOB_KEY", "URL_KEY", "TOCTREE_OPTIONS", \
   "use_cases")


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
    "URL_KEY",
    "TOCTREE_OPTIONS",
    "use_cases",
)

g_app_name = "sphinx_external_toc_strict"

# Pattern used to match URL items.
# regex should match sphinx.util.url_re
URL_PATTERN = r".+://.*"

DEFAULT_SUBTREES_KEY = "subtrees"
DEFAULT_ITEMS_KEY = "entries"
FILE_FORMAT_KEY = "format"
ROOT_KEY = "root"
FILE_KEY = "file"
GLOB_KEY = "glob"
URL_KEY = "url"

TOCTREE_OPTIONS = (
    "caption",
    "hidden",
    "maxdepth",
    "numbered",
    "reversed",
    "titlesonly",
)

use_cases = ("default", "jb-book", "jb-article")

# Removes epoch and local. Fixes version
__version_app = sanitize_tag(__version__)
__url__ = readthedocs_url(g_app_name, ver_=__version__)
