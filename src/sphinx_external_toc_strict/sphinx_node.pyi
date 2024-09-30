from typing import Any

import sphinx

# Inline Elements
# class emphasis(Inline, TextElement): pass
from docutils.nodes import (
    Node,
    TextElement,
)
from sphinx.application import Sphinx

__all__ = (
    "fake_node",
    "query_intersphinx",
)

def fake_node(
    domain: str,
    ref_type: str,
    target: str,
    content: str,
    **attrs: dict[str, Any],
) -> tuple[Node, TextElement]: ...
def query_intersphinx(
    app: Sphinx,
    target: str,
    contents: str | None = None,
    domain: str | None = ...,
    ref_type: str | None = ...,
) -> tuple[str | None, str | None]: ...
