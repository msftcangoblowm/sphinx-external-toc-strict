import types
from collections.abc import Sequence
from dataclasses import (
    dataclass,
    fields,
)
from pathlib import Path
from typing import Any

import strictyaml as s

from .api import (
    Document,
    SiteMap,
)
from .constants import (
    DEFAULT_ITEMS_KEY,
    DEFAULT_SUBTREES_KEY,
)
from .parsing_shared import FileFormat
from .util_dc import (
    DC_SLOTS,
    field,
)

__all__ = ("parse_toc_yaml", "parse_toc_data", "affinity_val", "load_yaml", "dump_yaml")

def affinity_val(
    key: str,
    val: str,
    mapping: types.MappingProxyType[str, s.Validator] = ...,
) -> str | int | bool: ...
def dump_yaml(site_map: SiteMap | dict[str, Any]) -> str: ...
def load_yaml(path: str | Path, encoding: str = "utf8") -> s.YAML: ...
def parse_toc_yaml(path: str | Path | s.YAML, encoding: str = "utf8") -> SiteMap: ...
def parse_toc_data(data: dict[str, Any]) -> SiteMap: ...
def _parse_doc_item(
    data: dict[str, Any],
    defaults: dict[str, Any],
    path: str,
    *,
    depth: int,
    file_format: FileFormat,
    is_root: bool = False,
) -> tuple[Document, Sequence[tuple[str, dict[str, Any]]]]: ...
def _parse_docs_list(
    docs_list: Sequence[tuple[str, dict[str, Any]]],
    site_map: SiteMap,
    defaults: dict[str, Any],
    *,
    depth: int,
    file_format: FileFormat,
) -> None: ...
