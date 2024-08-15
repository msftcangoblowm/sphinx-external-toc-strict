from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .api import (
    Document,
    SiteMap,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import (
        Iterable,
        Sequence,
    )
else:  # pragma: no cover
    from typing import (
        Iterable,
        Sequence,
    )

def _default_affinity(additional_files: Sequence[str], default_ext: str) -> str: ...
def create_site_from_toc(
    toc_path: str | Path,
    *,
    root_path: Path | str | None = None,
    default_ext: str | None = ".rst",
    encoding: str | None = "utf8",
    overwrite: bool | None = False,
    toc_name: str | None = "_toc.yml",
) -> SiteMap: ...
def site_map_guess_titles(
    site_map: SiteMap,
    index: str,
    is_guess: Any | None = False,
) -> None: ...
def create_site_map_from_path(
    root_path: Path | str,
    *,
    suffixes: Sequence[str] = (".rst", ".md"),
    default_index: str = "index",
    ignore_matches: Sequence[str] = (".*",),
    file_format: str | None = None,
) -> SiteMap: ...
def _doc_item_from_path(
    root: Path,
    folder: Path,
    index_docname: str,
    other_docnames: Sequence[str],
    folder_names: Sequence[str],
    suffixes: Sequence[str],
    default_index: str,
    ignore_matches: Sequence[str],
) -> tuple[Document, list[tuple[Path, str, Sequence[str], Sequence[str]]]]: ...
def natural_sort(iterable: Iterable[str]) -> list[str]: ...
def _assess_folder(
    folder: Path,
    suffixes: Sequence[str],
    default_index: str,
    ignore_matches: Sequence[str],
) -> tuple[str | None, Sequence[str], Sequence[str]]: ...
def migrate_jupyter_book(
    toc: Path | dict[str, Any] | list[dict[str, Any]],
) -> dict[str, Any]: ...
