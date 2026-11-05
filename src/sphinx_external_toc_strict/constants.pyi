from collections.abc import Sequence
from typing import Final

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

g_app_name: Final[str]

URL_PATTERN: Final[str]

DEFAULT_SUBTREES_KEY: Final[str]
DEFAULT_ITEMS_KEY: Final[str]
FILE_FORMAT_KEY: Final[str]
ROOT_KEY: Final[str]
FILE_KEY: Final[str]
GLOB_KEY: Final[str]
REF_KEY: Final[str]
URL_KEY: Final[str]
TOCTREE_OPTIONS: Final[Sequence[str]]

use_cases: Final[tuple[str, ...]]

__version_app: Final[str]
__url__: Final[str]
