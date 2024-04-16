import sys

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

__all__: Final[tuple[str, str, str, str, str, str, str, str, str, str, str, str, str]]

g_app_name: Final[str]

URL_PATTERN: Final[str]

DEFAULT_SUBTREES_KEY: Final[str]
DEFAULT_ITEMS_KEY: Final[str]
FILE_FORMAT_KEY: Final[str]
ROOT_KEY: Final[str]
FILE_KEY: Final[str]
GLOB_KEY: Final[str]
URL_KEY: Final[str]
TOCTREE_OPTIONS: Final[Sequence[str]]

use_cases: Final[tuple[str, ...]]

__version_app: Final[str]
__url__: Final[str]
