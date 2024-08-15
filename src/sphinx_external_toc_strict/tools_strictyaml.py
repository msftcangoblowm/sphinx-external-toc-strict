from __future__ import annotations

import re
import shutil
import sys
from fnmatch import fnmatch
from itertools import chain
from pathlib import (
    Path,
    PurePosixPath,
)
from typing import Any

from .api import (
    Document,
    FileItem,
    SiteMap,
    TocTree,
)
from .constants import (
    DEFAULT_ITEMS_KEY,
    DEFAULT_SUBTREES_KEY,
)
from .exceptions import MalformedError
from .filename_suffix import strip_suffix
from .parsing_shared import create_toc_dict
from .parsing_strictyaml import (
    load_yaml,
    parse_toc_data,
    parse_toc_yaml,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import (
        Mapping,
        Sequence,
    )
else:  # pragma: no cover
    from typing import (
        Mapping,
        Sequence,
    )


def _default_affinity(additional_files, default_ext):
    """Check create_files, if a file extension (e.g. ".md") is specified, use
    that. Would override sphinx environment, ``default_ext``. This
    annoyingly non-dynamic option is set within config file.

    [tool.sphinx-pyproject] source_suffix = ".rst"

    Rather than fix the setting, be able to override it on the fly

    :param additional_files: Files specified in yaml meta section --> ``create_files``
    :type additional_files: collections.abc.Sequence[str]
    :param default_ext: **A** default ext specified in config option, ``source_suffix``
    :type default_ext: str
    :returns: By looking thru the create_files, the file extension is actually used
    :rtype: str
    :meta private:
    """
    md_count = 0
    rst_count = 0
    default_affinity = default_ext
    for file_name in additional_files:
        file_suffix = Path(file_name).suffix

        if file_suffix == ".md":
            md_count += 1
        else:  # pragma: no cover
            pass

        if file_suffix == ".rst":
            rst_count += 1
        else:  # pragma: no cover
            pass

    # ignore index.rst cuz it's unavoidable
    if rst_count >= 1:
        rst_count -= 1

    if md_count != 0 and md_count > rst_count:
        default_affinity = ".md"
    elif rst_count != 0 and rst_count > md_count:
        default_affinity = ".rst"
    else:  # pragma: no cover
        # index.rst is ignored and still equal ... inconclusive; default_affinity
        pass

    return default_affinity


def create_site_from_toc(
    toc_path,
    *,
    root_path=None,
    default_ext=".rst",
    encoding="utf8",
    overwrite=False,
    toc_name="_toc.yml",
):
    """Create the files defined in the external toc file.

    Additional files can also be created by defining them in
    `meta`/`create_files` of the toc. Text can also be appended to files, by
    defining them in `meta`/`create_append` (as a mapping from files to text).

    :param toc_path: path to ToC file
    :type toc_path: pathlib.Path | str
    :param root_path: the root directory, or use ToC file directory
    :type root_path: pathlib.Path | str | None
    :param default_ext: default file extension to use
    :type default_ext: str | None
    :param encoding: encoding for writing files
    :type encoding:  str | None
    :param overwrite: overwrite existing files (otherwise raise ``IOError``)
    :type overwrite: bool | None
    :param toc_name: copy ToC file to root with this name
    :type toc_name: str | None
    :returns: Site map
    :rtype: sphinx_external_toc_strict.api.SiteMap
    :raises:

       - :py:exc:`IOError` -- Path already exists

    """
    assert default_ext in {".rst", ".md"}
    site_map = parse_toc_yaml(toc_path)

    root_path = Path(toc_path).parent if root_path is None else Path(root_path)
    root_path.mkdir(parents=True, exist_ok=True)

    # retrieve and validate meta variables
    additional_files = site_map.meta.get("create_files", [])

    # check create_files, if a file extension specified. If so, use that not default_ext
    default_affinity = _default_affinity(additional_files, default_ext)

    assert isinstance(additional_files, Sequence), "'create_files' should be a list"
    append_text = site_map.meta.get("create_append", {})
    assert isinstance(append_text, Mapping), "'create_append' should be a mapping"

    # copy toc file to root
    if toc_name and not root_path.joinpath(toc_name).exists():
        shutil.copyfile(toc_path, root_path.joinpath(toc_name))

    # create files
    for docname in chain(site_map, additional_files):
        # create document
        filename = docname
        is_unknown_ext = not any(docname.endswith(ext) for ext in {".rst", ".md"})
        if is_unknown_ext is True:
            # filename += default_ext
            filename += default_affinity
        else:  # pragma: no cover
            pass

        docpath = root_path.joinpath(PurePosixPath(filename))
        if docpath.exists() and not overwrite:
            raise IOError(f"Path already exists: {docpath}")
        docpath.parent.mkdir(parents=True, exist_ok=True)

        content = []

        # add heading based on file type
        heading = f"Heading: {filename}"
        if filename.endswith(".rst"):
            content = [heading, "=" * len(heading), ""]
        elif filename.endswith(".md"):
            content = ["# " + heading, ""]
        else:  # pragma: no cover
            pass

        # append extra text
        extra_lines = append_text.get(docname, "").splitlines()
        if extra_lines:
            content.extend(extra_lines + [""])

        # note \n works when writing for all platforms:
        # https://docs.python.org/3/library/os.html#os.linesep
        docpath.write_text("\n".join(content), encoding=encoding)

    return site_map


def site_map_guess_titles(
    site_map,
    index,
    is_guess=False,
):
    """In _toc.yml if titles in files, option can take titles from file names

    :param site_map: site map. Later converted into toc
    :type site_map: SiteMap
    :param index: File stem of root file. Coding convention is ``index``
    :type index: str
    :param is_guess: Default False. True to take titles from file names
    :type is_guess: typing.Any | None
    """
    # ensure bool
    if is_guess is None or not isinstance(is_guess, bool):
        is_modify_titles = False
    else:
        is_modify_titles = is_guess

    root_docname = site_map.root.docname
    docnames = [
        docname
        for docname in site_map
        if docname != root_docname and is_modify_titles is True
    ]
    for docname in docnames:
        # Take titles from file names
        filepath = PurePosixPath(docname)
        # use the folder name for index files
        name = filepath.parent.name if filepath.name == index else filepath.name
        # split into words
        words = name.split("_")
        # remove first word if is an integer
        words = words[1:] if words and all(c.isdigit() for c in words[0]) else words
        site_map[docname].title = " ".join(words).capitalize()


def create_site_map_from_path(
    root_path,
    *,
    suffixes=(".rst", ".md"),
    default_index="index",
    ignore_matches=(".*",),
    file_format=None,
):
    """Create the site-map from a folder structure.

    Files and folders are sorted in
    `natural order <https://en.wikipedia.org/wiki/Natural_sort_order>`_:

    :param root_path: Path to root file
    :type root_path: pathlib.Path | str
    :param suffixes: file suffixes to consider as documents
    :type suffixes: collections.abc.Sequence[str]
    :param default_index:

       file name (without suffix) considered as the index file for a
       folder, if not found then the first file is taken as the index

    :type default_index: str
    :param ignore_matches:

       file/folder names which match one of these will be ignored,
       uses fnmatch Unix shell-style wildcards, defaults to ignoring
       hidden files (starting with a dot)

    :type ignore_matches: collections.abc.Sequence[str]
    :param file_format: Default None. File format if specified
    :type file_format: str | None
    :returns: Site map created from folder tree starting at ``root_path``
    :rtype: SiteMap
    :raises:

       - :py:exc:`NotADirectoryError` -- root folder is not a folder
       - :py:exc:`FileNotFoundError` -- Path does not contain a root file

    """
    root_path = Path(root_path)
    # assess root. raises NotADirectoryError
    root_index, root_files, root_folders = _assess_folder(
        root_path, suffixes, default_index, ignore_matches
    )

    is_no_index = root_index is None or root_index != default_index
    if is_no_index:
        msg_err = f"path does not contain a root file: {root_path}"
        raise FileNotFoundError(msg_err)
    else:  # pragma: no cover
        pass

    # create root item and child folders
    root_item, indexed_folders = _doc_item_from_path(
        root_path,
        root_path,
        root_index,
        root_files,
        root_folders,
        suffixes,
        default_index,
        ignore_matches,
    )

    # create base site-map
    site_map = SiteMap(root=root_item, file_format=file_format)
    # we add all files to the site map, even if they don't have descendants
    # so we may later change their title
    for root_file in root_files:
        site_map[root_file] = Document(root_file)

    # while there are subfolders add them to the site-map
    while indexed_folders:
        (
            sub_path,
            child_index,
            child_files,
            child_folders,
        ) = indexed_folders.pop(0)
        for child_file in child_files:
            child_docname = (sub_path / child_file).relative_to(root_path).as_posix()
            assert child_docname not in site_map
            site_map[child_docname] = Document(child_docname)
        doc_item, new_indexed_folders = _doc_item_from_path(
            root_path,
            sub_path,
            child_index,
            child_files,
            child_folders,
            suffixes,
            default_index,
            ignore_matches,
        )
        assert doc_item.docname not in site_map
        site_map[doc_item.docname] = doc_item
        indexed_folders += new_indexed_folders

    return site_map


def _doc_item_from_path(
    root,
    folder,
    index_docname,
    other_docnames,
    folder_names,
    suffixes,
    default_index,
    ignore_matches,
):
    """Return the ``Document`` and children folders that contain an index.

    :param root: Path of root file
    :type root: pathlib.Path
    :param folder: Path of folder
    :type folder: pathlib.Path
    :param index_docname: docname of this node
    :type index_docname: str
    :param other_docnames: list of docnames of direct children
    :type other_docnames: collections.abc.Sequence[str]
    :param folder_names: folder names of direct children
    :type folder_names: collections.abc.Sequence[str]
    :param suffixes: suffixes to strip from file names
    :type suffixes: collections.abc.Sequence[str]
    :param default_index: root file name without suffix
    :type default_index: str
    :param ignore_matches: index names to ignore
    :type ignore_matches: collections.abc.Sequence[str]
    :returns:

       tuple containing: Document, list of sub_folder, child_index,
       child_files, child_folders

    :rtype: tuple[Document, list[tuple[pathlib.Path, str, collections.abc.Sequence[str], collections.abc.Sequence[str]]]]
    :meta private:
    """
    file_items = [
        FileItem((folder / name).relative_to(root).as_posix())
        for name in other_docnames
    ]

    # get folders with sub-indexes
    indexed_folders = []
    index_items = []
    for folder_name in folder_names:
        sub_folder = folder / folder_name
        # raises NotADirectoryError if root folder is not a folder
        child_index, child_files, child_folders = _assess_folder(
            sub_folder, suffixes, default_index, ignore_matches
        )
        if not child_index:
            # TODO handle folders with no files, but files in sub-folders
            continue
        indexed_folders.append((sub_folder, child_index, child_files, child_folders))
        index_items.append(
            FileItem((sub_folder / child_index).relative_to(root).as_posix())
        )

    doc_item = Document(
        docname=(folder / index_docname).relative_to(root).as_posix(),
        subtrees=(
            [TocTree(items=file_items + index_items)]  # type: ignore[arg-type]
            if (file_items or index_items)
            else []
        ),
    )
    return doc_item, indexed_folders


def natural_sort(iterable):
    """Natural sort an iterable.

    :param iterable: A list of str
    :type iterable: Iterable[str]
    :returns: Sorted, in ascending order, list
    :rtype: list[str]

    .. seealso::

       `Natural sort order <https://en.wikipedia.org/wiki/Natural_sort_order>`_

    """

    def _convert(text: str) -> int | str:
        return int(text) if text.isdigit() else text.lower()

    def _alphanum_key(key: str) -> list[int | str]:
        return [_convert(c) for c in re.split("([0-9]+)", key)]

    return sorted(iterable, key=_alphanum_key)


def _assess_folder(
    folder,
    suffixes,
    default_index,
    ignore_matches,
):
    """Assess the folder for ToC items. Strips suffixes from file names and
    sorts file/folder names by natural order.

    :param folder: A folder of ToC items
    :type folder: pathlib.Path
    :param suffixes: file name suffixes to strip from file names
    :type suffixes: collections.abc.Sequence[str]
    :param default_index: Default file stem of root document
    :type default_index: str
    :param ignore_matches: list of glob patterns of files to ignore
    :type ignore_matches: collections.abc.Sequence[str]
    :returns: (index file name, other file names, folders)
    :rtype: tuple[str | None, collections.abc.Sequence[str], collections.abc.Sequence[str]]
    :raises:

       - :py:exc:`NotADirectoryError` -- path must be a directory

    :meta private:
    """
    if not folder.is_dir():
        raise NotADirectoryError(f"path must be a directory: {folder}")

    # conversion to a set is to remove duplicates, e.g. doc.rst and doc.md
    sub_files = natural_sort(
        list(
            set(
                [
                    strip_suffix(path.name, suffixes)
                    for path in folder.iterdir()
                    if path.is_file()
                    and any(path.name.endswith(suffix) for suffix in suffixes)
                    and (not any(fnmatch(path.name, pat) for pat in ignore_matches))
                ]
            )
        )
    )
    sub_folders = natural_sort(
        [
            path.name
            for path in folder.iterdir()
            if path.is_dir()
            if (not any(fnmatch(path.name, pat) for pat in ignore_matches))
        ]
    )

    if not sub_files:
        return (None, sub_files, sub_folders)

    # get the index file for this folder
    try:
        index = sub_files.index(default_index)
    except ValueError:
        index = 0
    index_file = sub_files.pop(index)

    return (index_file, sub_files, sub_folders)


def migrate_jupyter_book(toc):
    """Migrate a jupyter-book v0.10.2 toc

    :param toc: Absolute path to toc yml file or toc map or list of toc map
    :type toc: pathlib.Path | dict[str, typing.Any] | list[dict[str, typing.Any]]
    :returns: toc dict
    :rtype: dict[str, typing.Any]
    :raises:

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- First
         list item is not a dict

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- First
         list item contains both 'chapters' and 'sections' keys

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- First
         list item '{key}' is not a list

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- top-level
         contains mixed 'part' and 'file' keys

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- ToC
         is not a list or dict

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- no
         top-level 'file' key found

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- There
         is more than one top-level key

       - :py:exc:`~sphinx_external_toc_strict.exceptions.MalformedError` -- Error
         parsing migrated output

    """

    if isinstance(toc, Path):
        path_toc = toc
        yml = load_yaml(path_toc, encoding="utf8")
        toc = yml.data

    # convert list to dict
    if isinstance(toc, list):
        toc_updated = toc[0]
        if not isinstance(toc_updated, dict):
            raise MalformedError("First list item is not a dict")
        if len(toc) > 1:
            first_items: list[dict[str, Any]] = []
            top_items_key = "sections"  # this is the default top-level key
            # The first set of pages will be called *either* sections or chapters
            if "sections" in toc_updated and "chapters" in toc_updated:
                raise MalformedError(
                    "First list item contains both 'chapters' and 'sections' keys"
                )
            for key in ("sections", "chapters"):
                if key in toc_updated:
                    top_items_key = key
                    items = toc_updated.pop(key)
                    if not isinstance(items, Sequence):
                        raise MalformedError(f"First list item '{key}' is not a list")
                    first_items += items

            # add list items after to same level
            first_items += toc[1:]

            # check for part keys (and also chapter which was deprecated)
            contains_part = any(
                ("part" in item or "chapter" in item) for item in first_items
            )
            contains_file = any("file" in item for item in first_items)
            if contains_part and contains_file:
                raise MalformedError("top-level contains mixed 'part' and 'file' keys")

            toc_updated["parts" if contains_part else top_items_key] = first_items

        toc = toc_updated
    elif not isinstance(toc, dict):
        raise MalformedError("ToC is not a list or dict")

    # convert first `file` to `root`
    if "file" not in toc:
        raise MalformedError("no top-level 'file' key found")
    toc["root"] = toc.pop("file")

    # setting `titlesonly` True is now part of the file format
    # toc["defaults"] = {"titlesonly": True}

    # we should now have a dict with either a 'parts', 'chapters', or 'sections' key
    top_level_keys = {"parts", "chapters", "sections"}.intersection(toc.keys())
    if len(top_level_keys) > 1:
        raise MalformedError(
            f"There is more than one top-level key: {top_level_keys!r}"
        )
    # from the top-level key we can now derive the file-format (for key-mappings)
    file_format = {
        "": "jb-book",
        "parts": "jb-book",
        "chapters": "jb-book",
        "sections": "jb-article",
    }["" if not top_level_keys else list(top_level_keys)[0]]

    # change all parts to DEFAULT_SUBTREES_KEY
    # change all chapters to DEFAULT_ITEMS_KEY
    # change all part/chapter to caption
    dicts = [toc]
    while dicts:
        dct = dicts.pop(0)
        if "chapters" in dct and "sections" in dct:
            raise MalformedError(f"both 'chapters' and 'sections' in same dict: {dct}")
        if "parts" in dct:
            dct[DEFAULT_SUBTREES_KEY] = dct.pop("parts")
        if "sections" in dct:
            dct[DEFAULT_ITEMS_KEY] = dct.pop("sections")
        if "chapters" in dct:
            dct[DEFAULT_ITEMS_KEY] = dct.pop("chapters")
        for key in ("part", "chapter"):
            if key in dct:
                dct["caption"] = dct.pop(key)

        # add nested dicts
        for val in dct.values():
            for item in val if isinstance(val, Sequence) else [val]:
                if isinstance(item, dict):
                    dicts.append(item)

    # if `numbered` at top level, move to options or copy to each subtree
    if "numbered" in toc:
        key = "numbered"
        val_raw = toc.pop("numbered")
        numbered = val_raw
        if DEFAULT_ITEMS_KEY in toc:
            toc["options"] = {key: numbered}
        for subtree in toc.get(DEFAULT_SUBTREES_KEY, []):
            if key not in subtree:
                subtree[key] = numbered

    # now convert to a site map, so we can validate
    try:
        site_map = parse_toc_data(toc)
    except MalformedError as err:
        msg_err = f"Error parsing migrated output: {err}"
        raise MalformedError(msg_err) from err
    # change the file format and convert back to a dict
    site_map.file_format = file_format
    return create_toc_dict(site_map, skip_defaults=True)
