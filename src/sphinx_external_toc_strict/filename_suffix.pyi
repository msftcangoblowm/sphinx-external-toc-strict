from __future__ import annotations

import sys

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

__all__: Final[tuple[str, str]]

def stem_natural(name: str) -> str: ...
def _strip_suffix_natural(name: str, suffixes: str) -> str: ...
def _strip_suffix_or(name: str, suffixes: list[str]) -> str: ...
def strip_suffix(name: str, suffixes: str | Sequence[str]) -> str: ...
