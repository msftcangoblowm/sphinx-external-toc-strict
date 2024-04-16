"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Shared objects, such as: data, functions, and classes

.. py:data:: __all__
   :type: tuple[str, str, str]
   :value: ("FileFormat", "create_toc_dict", "FILE_FORMATS")

   Module exports

.. py:data:: FILE_FORMATS
   :type: dict[str, FileFormat]

   Differences between file formats (use cases). subtree, entries,
   default item. And settings: ``titleonly``

"""

import copy
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
    FileItem,
    GlobItem,
    TocTree,
    UrlItem,
)
from .constants import (
    DEFAULT_ITEMS_KEY,
    DEFAULT_SUBTREES_KEY,
    FILE_FORMAT_KEY,
    FILE_KEY,
    GLOB_KEY,
    ROOT_KEY,
    TOCTREE_OPTIONS,
    URL_KEY,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

__all__ = (
    "FileFormat",
    "create_toc_dict",
    "FILE_FORMATS",
)


@dataclass(**DC_SLOTS)
class FileFormat:
    """Mapping of keys for subtrees and items, dependant on depth in the ToC

    .. note:: Hey devs!

       :py:mod:`dataclasses` turns attributes --> instance variables. aka
       into class constructor parameters

    :ivar toc_defaults:

       Each FileFormat may have specific defaults. e.g. "jb-book" and
       "jb-article" have default, ``{"titleonly": True}``

    :vartype: dict[str, typing.Any]
    :ivar subtrees_keys:

       tuple of subtrees' index key

    :vartype: Sequence[str]
    :ivar items_keys: tuple of items' index key
    :vartype: Sequence[str]
    :ivar default_subtrees_key:

       Default "subtrees". Defaults key for subtrees. Other usecases would override

    :vartype: str
    :ivar default_items_key:

       Default "entries". Default key for entries. Other usecases would override

    :vartype: str
    """

    toc_defaults: dict[str, Any] = field(default_factory=dict)
    subtrees_keys: Sequence[str] = ()
    items_keys: Sequence[str] = ()
    default_subtrees_key: str = DEFAULT_SUBTREES_KEY
    default_items_key: str = DEFAULT_ITEMS_KEY

    def get_subtrees_key(self, depth):
        """Get the subtrees key name for this depth in the ToC.

        :param depth: recursive depth (starts at 0)
        :type depth: int
        :return: subtrees key name
        :rtype: str
        """
        try:
            return self.subtrees_keys[depth]
        except IndexError:
            return self.default_subtrees_key

    def get_items_key(self, depth):
        """Get the items key name for this depth in the ToC.

        :param depth: recursive depth (starts at 0)
        :type depth: int
        :return: items key name
        :rtype: str
        """
        try:
            return self.items_keys[depth]
        except IndexError:
            return self.default_items_key


FILE_FORMATS = {
    "default": FileFormat(),
    "jb-book": FileFormat(
        subtrees_keys=("parts",),
        items_keys=("chapters",),
        default_items_key="sections",
        toc_defaults={"titlesonly": True},
    ),
    "jb-article": FileFormat(
        default_items_key="sections",
        toc_defaults={"titlesonly": True},
    ),
}


def create_toc_dict(site_map, *, skip_defaults=True):
    """Create the ToC dictionary from a site-map.

    :param site_map: site map
    :type site_map: sphinx_external_toc_strict.api.SiteMap
    :param skip_defaults:

       Default True. Do not add key/values for values that are already the default

    :type skip_defaults: bool
    :return: ToC dictionary
    :rtype: dict[str, typing.Any]
    :raises:

       - :py:exc:`KeyError` -- File format not recognised. Format that
         have support: default, jb-book, jp-article

    """
    try:
        file_format = FILE_FORMATS[site_map.file_format or "default"]
    except KeyError:
        raise KeyError(f"File format not recognised @ '{site_map.file_format}'")
    data = _docitem_to_dict(
        site_map.root,
        site_map,
        depth=0,
        skip_defaults=skip_defaults,
        is_root=True,
        file_format=file_format,
    )
    if site_map.meta:
        data["meta"] = site_map.meta.copy()
    if site_map.file_format and site_map.file_format != "default":
        # ensure it is the first key
        data = {FILE_FORMAT_KEY: site_map.file_format, **data}
    return data


def _parse_item_testable(
    site_map,
    item,
    depth,
    file_format,
    skip_defaults,
    parsed_docnames,
):
    """Parse one item: FileItem, GlobItem, or UrlItem

    Was inline fcn, _parse_item, within _docitem_to_dict

    :param site_map: site map
    :type site_map: SiteMap
    :param item: Should be a FileItem, GlobItem, or UrlItem, but assuming nothing
    :type item: typing.Any
    :param depth: Within document, nesting depth
    :type depth: int
    :param file_format: doc item file format
    :type file_format: FileFormat
    :param skip_defaults: do not add key/values for values that are already the default
    :type skip_defaults: bool
    :param parsed_docnames:

       parsed document names cache used to prevent infinite recursion

    :type parsed_docnames: set[str]
    :returns:

       dict containing key/value pair. For URLItem, also contains ``title`` / ``value``

    :rtype: dict[str, typing.Any]
    :raises:

       - :py:exc:`TypeError` -- unsupported type excepted FileItem, GlobItem, or URLItem

    :meta private:
    """
    if isinstance(item, FileItem):
        if item in site_map:
            d_ret = _docitem_to_dict(
                site_map[item],
                site_map,
                depth=depth + 1,
                file_format=file_format,
                skip_defaults=skip_defaults,
                parsed_docnames=parsed_docnames,
            )
        else:  # pragma: no cover FileItem MUST be within a Mapping
            d_ret = {FILE_KEY: str(item)}
    elif isinstance(item, GlobItem):
        d_ret = {GLOB_KEY: str(item)}
    elif isinstance(item, UrlItem):
        if item.title is not None:
            d_ret = {URL_KEY: item.url, "title": item.title}
        else:
            d_ret = {URL_KEY: item.url}
    else:
        raise TypeError(item)

    return d_ret


def _docitem_to_dict(
    doc_item,
    site_map,
    *,
    depth,
    file_format,
    skip_defaults=True,
    is_root=False,
    parsed_docnames=None,
):
    """Create ToC dictionary from a `Document` and a `SiteMap`.

    :param doc_item: Document instance
    :type doc_item: sphinx_external_toc_strict.api.Document
    :param site_map: site map
    :type site_map: sphinx_external_toc_strict.api.SiteMap
    :param depth: recursive depth (starts at 0)
    :type depth: int
    :param file_format: doc item file format
    :type file_format: FileFormat
    :param skip_defaults:

       Default True. Do not add key/values for values that are already the default

    :type skip_defaults: bool
    :param is_root: whether this is the root item, defaults to False
    :type is_root: bool
    :param parsed_docnames:

       parsed document names cache used to prevent infinite recursion

    :type parsed_docnames: set[str] | None
    :return: parsed ToC dictionary
    :rtype: dict[str, typing.Any]
    :raises:

       - :py:exc:`RecursionError` -- Site map recursion
       - :py:exc:`TypeError` -- invalid ToC item

    :meta private:
    """
    file_key = ROOT_KEY if is_root else FILE_KEY
    subtrees_key = file_format.get_subtrees_key(depth)
    items_key = file_format.get_items_key(depth)

    # protect against infinite recursion
    parsed_docnames = parsed_docnames or set()
    if doc_item.docname in parsed_docnames:
        raise RecursionError(f"{doc_item.docname!r} in site-map multiple times")
    parsed_docnames.add(doc_item.docname)

    data: dict[str, Any] = {}

    data[file_key] = doc_item.docname
    if doc_item.title is not None:
        data["title"] = doc_item.title

    if not doc_item.subtrees:
        return data

    data[subtrees_key] = []
    # TODO handle default_factory
    _defaults = {f.name: f.default for f in fields(TocTree)}
    for toctree in doc_item.subtrees:
        # only add these keys if their value is not the default
        toctree_data = {
            key: getattr(toctree, key)
            for key in TOCTREE_OPTIONS
            if (not skip_defaults) or getattr(toctree, key) != _defaults[key]
        }
        # toctree_data[items_key] = [_parse_item(s) for s in toctree.items]
        lst_tmp = []
        for s in toctree.items:
            lst_tmp.append(
                _parse_item_testable(
                    site_map,
                    s,
                    depth,
                    file_format,
                    skip_defaults,
                    parsed_docnames,
                ),
            )
        toctree_data[items_key] = copy.deepcopy(lst_tmp)
        data[subtrees_key].append(toctree_data)

    # apply shorthand if possible (one toctree in subtrees)
    if len(data[subtrees_key]) == 1 and items_key in data[subtrees_key][0]:
        old_toctree_data = data.pop(subtrees_key)[0]
        # move options to options key
        if len(old_toctree_data) > 1:
            data["options"] = {
                k: v for k, v in old_toctree_data.items() if k != items_key
            }
        data[items_key] = old_toctree_data[items_key]

    return data
