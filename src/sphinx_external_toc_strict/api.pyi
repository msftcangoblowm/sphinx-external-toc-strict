from collections.abc import (
    Iterable,
    Iterator,
    MutableMapping,
    Sequence,
)
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Self,
    Union,
)

from sphinx.application import Sphinx

from .constants import URL_PATTERN
from .util_dc import (
    DC_SLOTS,
    deep_iterable,
    field,
    instance_of,
    matches_re,
    optional,
)

class FileItem(str):
    def render(
        self,
        site_map: SiteMap,
    ) -> Iterator[tuple[str, str]]: ...

class GlobItem(str):
    def render(
        self,
        all_docnames: Iterable[str],
    ) -> Iterator[tuple[str, str]]: ...

@dataclass(**DC_SLOTS)
class UrlItem:
    url: str = field(validator=[instance_of(str), matches_re(URL_PATTERN)])
    title: str | None = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self) -> None: ...
    def render(self) -> Iterator[tuple[str, str]]: ...

@dataclass(**DC_SLOTS)
class RefItem:
    ref_id: str = field(validator=[instance_of(str)])
    title: str | None = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self) -> None: ...
    def render(self, app: Sphinx) -> Iterator[tuple[str, str]]: ...

@dataclass(**DC_SLOTS)
class TocTree:
    items: list[GlobItem | FileItem | UrlItem] = field(
        validator=deep_iterable(
            instance_of((GlobItem, FileItem, UrlItem)), instance_of(list)
        )
    )
    caption: str | None = field(
        default=None, kw_only=True, validator=optional(instance_of(str))
    )
    hidden: bool = field(default=True, kw_only=True, validator=instance_of(bool))
    maxdepth: int = field(default=-1, kw_only=True, validator=instance_of(int))
    numbered: bool | int = field(
        default=False, kw_only=True, validator=instance_of((bool, int))
    )
    reversed: bool = field(default=False, kw_only=True, validator=instance_of(bool))
    titlesonly: bool = field(default=False, kw_only=True, validator=instance_of(bool))

    def __post_init__(self) -> None: ...
    def files(self) -> list[str]: ...
    def globs(self) -> list[str]: ...

    __match_args__: tuple[str, ...] = ("items",)

@dataclass(**DC_SLOTS)
class Document:
    docname: str = field(validator=instance_of(str))
    subtrees: list[TocTree] = field(
        default_factory=list,
        validator=deep_iterable(instance_of(TocTree), instance_of(list)),
    )
    title: str | None = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self) -> None: ...
    def child_files(self) -> list[str]: ...
    def child_globs(self) -> list[str]: ...

class SiteMap(MutableMapping[str, Union[Document, Any]]):
    __slots__ = ("_root", "_docs", "_meta", "_file_format")
    _root: Document
    _docs: dict[str, Document]
    _meta: dict[str, Any]
    _file_format: str | None

    def __init__(
        self,
        root: Document,
        meta: dict[str, Any] | None = None,
        file_format: str | None = None,
    ) -> None: ...
    @property
    def root(self) -> Document: ...
    @property
    def meta(self) -> dict[str, Any]: ...
    @property
    def file_format(self) -> str | None: ...
    @file_format.setter
    def file_format(self, val: str | None) -> None: ...
    def globs(self) -> set[str]: ...
    def match_globs(self, posix_no_suffix: str) -> bool: ...
    def new_excluded(
        self,
        srcdir: str | Path,
        cfg_source_suffix: Sequence[str],
        cfg_exclude_patterns: Sequence[str],
    ) -> Sequence[str]: ...
    def __getitem__(self, docname: str) -> Document: ...
    def __setitem__(self, docname: str, item: Document) -> None: ...
    def __delitem__(self, docname: str) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    @staticmethod
    def _replace_items(d: dict[str, Any]) -> dict[str, Any]: ...
    def as_json(self) -> dict[str, Any]: ...
    def get_changed(self, previous: Self) -> set[str]: ...
