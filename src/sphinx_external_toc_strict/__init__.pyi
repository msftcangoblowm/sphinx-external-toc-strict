from __future__ import annotations

import sys

from sphinx.application import Sphinx

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import Final
else:  # pragma: no cover
    from typing_extensions import Final

def setup(app: Sphinx) -> dict[str, str | bool]: ...
