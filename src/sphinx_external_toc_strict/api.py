"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Defines the `SiteMap` object, for storing the parsed ToC

In yaml can include the top level field, ``meta``.

.. csv-table:: meta tricks
   :header: "field", "typr", "desc"
   :widths: auto

   "create_files", "list[str]", "In Sphinx doc tree, create empty file. Normally just the file stem. If both .rst and .md docs are present include entire file name"
   "create_append", "file_stem[.md|.rst]: | '[text]'", "In Sphinx doc tree, create with provided contents. In unittest yml this is tricky. Use single quote, without newlines, rather than | or double quotes. Escape double quotes and single whitespace"
   "regress", "str", "During building html phase, the root doc stem. No file extension"
   "exclude_missing", "bool", "Rather than fail, continue if a present file is not included into the ToC"

Outside of unittest yml, tricks

Append :code:`.. tableofcontents::` directive (or markdown equivalent) to
existing ``index.rst`` file

.. code-block:: text

   meta:
     create_append:
       index: '

       .. tableofcontents::

       '

Whitespace is significant. The empty lines must not include whitespace.

Even if using markdown, the root index file **must be** ``index.rst``

"""

from __future__ import annotations

import sys
from dataclasses import (
    asdict,
    dataclass,
)
from typing import (
    Any,
    Union,
)

from ._compat import (
    DC_SLOTS,
    deep_iterable,
    field,
    instance_of,
    matches_re,
    optional,
    validate_fields,
)
from .constants import (
    URL_PATTERN,
    use_cases,
)

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping


class FileItem(str):
    """A document path in a toctree list.

    This should be in POSIX format (folders split by ``/``), relative to the
    source directory, and can be with or without an extension.
    """


class GlobItem(str):
    """A document glob in a toctree list."""


@dataclass(**DC_SLOTS)
class UrlItem:
    """A URL in a toctree
    :ivar url: URL str
    :vartype url: str
    :ivar title: Title shown rather than the raw URL
    :vartype title: sre | None
    .. note: url pattern

       regex should match sphinx.util.url_re

    """

    url: str = field(validator=[instance_of(str), matches_re(URL_PATTERN)])
    title: str | None = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self):
        validate_fields(self)


@dataclass(**DC_SLOTS)
class TocTree:
    """An individual toctree within a document

    :ivar items: List of one ToC level's items: glob, file, or url
    :vartype items: list[sphinx_external_toc_strict.api.GlobItem | sphinx_external_toc_strict.api.FileItem | sphinx_external_toc_strict.api.UrlItem]
    :ivar caption: Default None. This ToC level's caption
    :vartype caption: str | None
    :ivar hidden: Default True. Whether to show the ToC within (inline of) the document
    :vartype hidden:  bool
    :ivar maxdepth:

       Default ``-1`` means infinite. A maximum nesting depth to use
       when showing the ToC within the document
    :vartype maxdepth: int
    :ivar numbered:

       Default False. Automatically add numbers to all documents within a subtree

    :vartype numbered: bool | int
    :ivar reversed:

       If ``True`` entries in the subtree will be listed in reverse
       order. Useful along with ``glob``

    :vartype reversed: bool
    :ivar titleonly:

       Default ``False``. If ``True`` then only the first heading in
       the document will be shown in the ToC, not other headings of
       the same level

    :vartype titleonly: bool
    """

    # TODO validate uniqueness of docnames (at least one item)
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

    def __post_init__(self):
        validate_fields(self)

    def files(self):
        """Returns a list of file items included in this ToC tree

        :return: file items
        :rtype: list[str]
        """
        return [str(item) for item in self.items if isinstance(item, FileItem)]

    def globs(self):
        """Get list of glob items included in this ToC tree

        :return: glob items
        :rtype: list[str]
        """
        return [str(item) for item in self.items if isinstance(item, GlobItem)]


@dataclass(**DC_SLOTS)
class Document:
    """A document in the site map

    :ivar docname:

       Normally file stem. If both .rst and .md are used, then file name

    :vartype docname: str
    :ivar subtrees: Flat structure of all subtrees
    :vartype subtrees: list[TocTree]
    :ivar title: In yaml, can provide a title. Otherwise pulled from the document
    :vartype title: str | None

    .. todo:: Validate docname uniqueness

       Validate uniqueness of docnames across all parts (and none
       should be the docname)

    """

    docname: str = field(validator=instance_of(str))
    subtrees: list[TocTree] = field(
        default_factory=list,
        validator=deep_iterable(instance_of(TocTree), instance_of(list)),
    )
    title: str | None = field(default=None, validator=optional(instance_of(str)))

    def __post_init__(self) -> None:
        validate_fields(self)

    def child_files(self):
        """Return all children files.

        :return: child files
        :rtype: list[str]
        """
        return [name for tree in self.subtrees for name in tree.files()]

    def child_globs(self):
        """Return all children globs.

        :return: child globs
        :rtype: list[str]
        """
        return [name for tree in self.subtrees for name in tree.globs()]


class SiteMap(MutableMapping[str, Union[Document, Any]]):
    """A mapping of documents to their toctrees (or None if terminal)

    :ivar root: Document root
    :vartype root: sphinx_external_toc_strict.api.Document
    :ivar meta:

       YAML tricks, used mainly in yml used by unittests. Known tricks:
       create_files, create_append, regress, exclude_missing

    :vartype meta: dict[str, typing.Any] | None
    :ivar file_format: Supported formats / use cases
    :vartype file_format: str | None
    """

    def __init__(
        self,
        root: Document,
        meta: dict[str, Any] | None = None,
        file_format: str | None = None,
    ) -> None:
        self._docs: dict[str, Document] = {}
        self[root.docname] = root
        self._root: Document = root
        self._meta: dict[str, Any] = meta or {}
        # bypasses property setter. Could be unsupported or mistaken file format
        self._file_format = file_format

    @property
    def root(self):
        """Return the root document of the ToC tree.

        :return: root document
        :rtype: sphinx_external_toc_strict.api.Document
        """
        return self._root

    @property
    def meta(self):
        """Return the site-map metadata.

        :return: metadata dictionary
        :rtype: dict[str, typing.Any]
        """
        return self._meta

    @property
    def file_format(self):
        """Get the format of the file.

        :return: output file format
        :rtype: str | None

        .. seealso::

           file formats (aka use cases)

           :py:data:`sphinx_external_toc_strict.constants.use_cases`

        """
        return self._file_format

    @file_format.setter
    def file_format(self, val):
        """Set the format of the file

        :param value: file format
        :type value: str | None

        .. seealso::

           file formats (aka use cases)

           :py:data:`sphinx_external_toc_strict.constants.use_cases`

        """
        is_valid = val is not None and val in use_cases
        if is_valid:
            self._file_format = val
        else:  # pragma: no cover
            # do nothing
            pass

    def globs(self):
        """All globs present across all toctrees

        :returns: set of all globs present across all toctrees
        :rtype: set[str]
        """
        return {glob for item in self._docs.values() for glob in item.child_globs()}

    def __getitem__(self, docname):
        """Enable retrieving a document by name using the indexing operator.

        :param docname: document name
        :type docname: str
        :return: document instance
        :rtype: sphinx_external_toc_strict.api.Document
        """
        return self._docs[docname]

    def __setitem__(self, docname, item):
        """Enable setting a document by name using the indexing operator.

        :param docname: document name
        :type docname: str
        :param item: document instance
        :type item: sphinx_external_toc_strict.api.Document
        """
        assert item.docname == docname
        self._docs[docname] = item

    def __delitem__(self, docname):
        """Enable removing a document by name.

        :param docname: document name
        :type docname: str
        """
        assert docname != self._root.docname, "cannot delete root doc item"
        del self._docs[docname]

    def __iter__(self):
        """Enable iterating the names of the documents the site map is composed
        of.

        :returns: document name
        :rtype: collections.abc.Iterator[str]
        """
        for docname in self._docs:
            yield docname

    def __len__(self):
        """Enable using Python's built-in `len()` function to return the number
        of documents contained in a site map.

        :return: number of documents in this site map
        :rtype: int
        """
        return len(self._docs)

    @staticmethod
    def _replace_items(d):
        """Helper which replaces Mapping and Sequence to json equivalents

        :param d: dict to convert to json
        :type d: dict[str, typing.Any]
        :returns: dict suitable to convert into json
        :rtype: dict[str, typing.Any]
        """
        for k, v in d.items():
            if isinstance(v, dict):
                d[k] = SiteMap._replace_items(v)
            elif isinstance(v, (list, tuple)):
                d[k] = [
                    (
                        SiteMap._replace_items(i)
                        if isinstance(i, dict)
                        else (str(i) if isinstance(i, str) else i)
                    )
                    for i in v
                ]
            elif isinstance(v, str):
                d[k] = str(v)
        return d

    def as_json(self):
        """Return JSON serialized site-map representation

        :returns: json dict
        :rtype: dict[str, typing.Any]
        """
        doc_dict = {
            k: asdict(self._docs[k]) if self._docs[k] else self._docs[k]
            for k in sorted(self._docs)
        }

        doc_dict = SiteMap._replace_items(doc_dict)
        data = {
            "root": self.root.docname,
            "documents": doc_dict,
            "meta": self.meta,
        }
        if self.file_format:
            data["file_format"] = self.file_format
        else:  # pragma: no cover
            pass

        return data

    def get_changed(self, previous):
        """Compare this sitemap to another and return a list of changed documents

        :param previous: SiteMap to compare against
        :type previous: sphinx_external_toc_strict.api.SiteMap
        :returns: set[str]
        :rtype: set[str]

        .. note:: For Sphinx

           File extensions should be removed to get docnames. When
           mixing .rst and .md, the file extensions are necessary

        """
        changed_docs = set()
        # check if the root document has changed
        if self.root != previous.root:
            changed_docs.add(self.root.docname)
        for name, doc in self._docs.items():
            if name not in previous:
                changed_docs.add(name)
                continue
            prev_doc = previous[name]
            if prev_doc != doc:
                changed_docs.add(name)
        return changed_docs
