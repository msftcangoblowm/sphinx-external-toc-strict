from __future__ import annotations

from typing import Any

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.transforms import SphinxTransform
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective

logger: logging.SphinxLoggerAdapter

def create_warning(
    app: Sphinx,
    doctree: nodes.document,
    category: str,
    message: str,
    *,
    line: int | None = None,
    append_to: nodes.Element | None = None,
    wtype: str = "etoc",
) -> nodes.system_message | None: ...
def remove_suffix(docname: str, suffixes: list[str]) -> str: ...
def parse_toc_to_env(app: Sphinx, config: Config) -> None: ...
def add_changed_toctrees(
    app: Sphinx,
    env: BuildEnvironment,
    added: set[str],
    changed: set[str],
    removed: set[str],
) -> set[str]: ...

class TableOfContentsNode(nodes.Element):  # type: ignore[misc]
    def __init__(self, **attributes: Any) -> None: ...

class TableofContents(SphinxDirective):  # type: ignore
    def run(self) -> list[TableOfContentsNode]: ...

def insert_toctrees(app: Sphinx, doctree: nodes.document) -> None: ...

class InsertToctrees(SphinxTransform):  # type: ignore
    default_priority = 100
    def apply(self, **kwargs: Any) -> None: ...

def ensure_index_file(app: Sphinx, exception: Exception | None) -> None: ...
