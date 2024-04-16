import sys

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

__all__: Final[tuple[str]]

class MalformedError(Exception): ...
