import sys
from dataclasses import (
    dataclass,
    fields,
)
from typing import Any

from ._compat import (
    DC_SLOTS,
    field,
)
from .api import (
    Document,
    SiteMap,
)
from .constants import (
    DEFAULT_ITEMS_KEY,
    DEFAULT_SUBTREES_KEY,
)

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

__all__: Final[tuple[str, str, str]]

@dataclass(**DC_SLOTS)
class FileFormat:
    toc_defaults: dict[str, Any] = field(default_factory=dict)
    subtrees_keys: Sequence[str] = ()
    items_keys: Sequence[str] = ()
    default_subtrees_key: str = DEFAULT_SUBTREES_KEY
    default_items_key: str = DEFAULT_ITEMS_KEY

    def get_subtrees_key(self, depth: int) -> str: ...
    def get_items_key(self, depth: int) -> str: ...

FILE_FORMATS: dict[str, FileFormat]

def create_toc_dict(
    site_map: SiteMap,
    *,
    skip_defaults: bool = True,
) -> dict[str, Any]: ...
def _parse_item_testable(
    site_map: SiteMap,
    item: Any,
    depth: int,
    file_format: FileFormat,
    skip_defaults: bool,
    parsed_docnames: set[str],
) -> dict[str, Any]: ...
def _docitem_to_dict(
    doc_item: Document,
    site_map: SiteMap,
    *,
    depth: int,
    file_format: FileFormat,
    skip_defaults: bool = True,
    is_root: bool = False,
    parsed_docnames: set[str] | None = None,
) -> dict[str, Any]: ...
