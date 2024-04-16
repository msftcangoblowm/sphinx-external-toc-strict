"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

The yaml files structure is too dynamic. Constructing
a strictyaml schema for the entire YAML file is a fool's errand!

Instead, limit the scope of strictyaml influence to:

- parse the entire YAML as if all fields are :py:class:`strictyaml.Str`

- Have a key value pair, mapping of scalar key name --> stricyyaml validator class.
  e.g. ``titleonly`` --> :py:class:`strictyaml.Bool`. Then handle all scalar
  values thru this affinity mapping

The undocumented top-level key, ``meta``, contains mysterious key/value pairs.

Discover which ``meta`` keys are used, see this ``tests/_bad_toc_files``
and ``tests/_toc_files`` folders

.. py:data:: __all__
   :type: tuple[str, str, str, str, str]
   :value: ("parse_toc_yaml", "parse_toc_data", "affinity_val", \
   "load_yaml", "dump_yaml")

   Modules exports

.. py:data:: _scalar_affinity_map
   :type: types.MappingProxyType[str, strictyaml.validators.Validator]

   Read-only mapping. Use as strictyaml schema with
   :py:func:`strictyaml.load` to fix the scalar value's type

   key: field key

   value: strictyaml scalar Validator

"""

from __future__ import annotations

import io
import sys
from collections.abc import Mapping
from pathlib import (
    Path,
    PurePath,
)
from types import MappingProxyType
from typing import Any

import strictyaml as s

from .api import (
    Document,
    FileItem,
    GlobItem,
    SiteMap,
    TocTree,
    UrlItem,
)
from .constants import (
    FILE_FORMAT_KEY,
    FILE_KEY,
    GLOB_KEY,
    ROOT_KEY,
    TOCTREE_OPTIONS,
    URL_KEY,
)
from .exceptions import MalformedError
from .parsing_shared import (
    FILE_FORMATS,
    create_toc_dict,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

__all__ = ("parse_toc_yaml", "parse_toc_data", "affinity_val", "load_yaml", "dump_yaml")

_scalar_affinity_map = MappingProxyType(
    {
        "root": s.Str(),
        "format": s.Str(),
        "file": s.Str(),
        "url": s.Str(),  # regex url?
        "title": s.Str(),
        "glob": s.Str(),
        "caption": s.Str(),
        "hidden": s.Bool(),
        "maxdepth": s.Int(),
        "numbered": s.Int() | s.Bool(),
        "reversed": s.Bool(),
        "titlesonly": s.Bool(),
        "exclude_missing": s.Bool(),  # meta; test_parsing/test_create_toc_dict_exclude_missing_.yml
        "unknown": s.Int(),  # meta; _bad_toc_files/unknown_keys_nested.yml
        "create_files": s.Seq(s.Str()),  # meta; Sequence[str]
        "regress": s.Str(),  # meta; str
    },
)


def affinity_val(
    key,
    val,
    mapping=_scalar_affinity_map,
):
    """yaml file initially parsed treating every scalar as a str. Have
    strictyaml fix the scalar to the correct data type

    .. warning::

       :py:mod:`strictyaml` long shadow hangs heavy over the village,
       infested with spies, hiding in plain sight.

       The witch hunter screams, `Reveal yourself and be judged. Tonight
       all that is hidden shall be revealed.`

    :param key: field key used in yaml file
    :type key: str
    :param val:

       str value. Need to fix the type by knowing each field's type affinity

    :type val: str
    :param mapping: Key is field key. Value is a strictyaml scalar Validator
    :type mapping: types.MappingProxyType
    :returns: Value with strictyaml fixed type
    :rtype: str | int | bool
    :raises:

       - :py:exc:`strictyaml.YAMLValidationError` -- Field value unexpected data type

    """
    """Space where key val user input validation would normally be.
    By default, strictyaml treat both as strictyaml.Str"""
    pass

    """This package has its mapping. Be open minded, other packages
    most likely face the same exact issue. Allow them to change which
    mapping is used. Hint: functools.partial is your friend"""
    if mapping is None or (
        mapping is not None and not isinstance(mapping, MappingProxyType)
    ):
        mapping = _scalar_affinity_map
    else:  # pragma: no cover
        pass

    is_uninteresting = key not in mapping.keys()
    if is_uninteresting:
        # a scalar str it began, a scalar str it shall remain!
        ret = val
    else:
        str_yaml = f"{val}"
        schema = mapping[key]
        try:
            yml = s.dirty_load(str_yaml, schema, allow_flow_style=True)
        except s.YAMLValidationError:
            """strictyaml.exceptions.YAMLValidationError: when expecting an integer
            E       found an arbitrary number
            E         in "<unicode string>", line 1, column 1:
            E           '1.12345'
            E            ^ (line: 1)
            """
            raise
        else:
            ret = yml.data

    return ret


def load_yaml(path, encoding="utf8"):
    """Using strictyaml dirty load converts all values into str,
    preventing most yaml shenanegans.

    Uses schema :py:class:`strictyaml.Any`. Which converts all scalars into str!

    The yaml file itself is a wall of complexity. To avoid that
    complexity, the parser does it's job, but is aware that every value's scalar
    non-str data type is wrong.

    To fix this side effect. Scalar key/value pair is compared against a Mapping.
    key --> strictyaml Validator. Scalar Validator is treated as a
    strictyaml schema. Value treated as yaml; loaded by strictyaml
    with the correct scalar schema.

    :param path: absolute path to yaml file
    :type path: str | pathlib.Path
    :param encoding: Default "utf8". Provide encoding if other than "utf8"
    :param emcoding: str | None
    :returns:

       YAML class instance. Which has useful attribute,
       :py:attr:`~strictyaml.YAML.data` and method,
       :py:meth:`~strictyaml.YAML.as_yaml`

    :rtype: strictyaml.YAML
    """
    str_yaml = Path(path).read_text(encoding=encoding)
    return s.dirty_load(str_yaml, allow_flow_style=True)


def dump_yaml(site_map):
    """Dump sitemap into yaml

    To prepare a site map call,
    :py:meth:`sphinx_external_toc_strict.parsing_strictyaml.parse_toc_yaml`

    site map gets converted into a dict. :pypi_org:`ruamel.yaml`
    dumps the dict as yaml

    :param site_map: convert site map into a dict.  then dumps the dict into yaml str
    :type site_map: sphinx_external_toc_strict.api.SiteMap | dict[str, typing.Any]
    :returns: yaml
    :rtype: str
    :raises:

       - :py:exc:`ValueError` -- Unsupported type expecting
         :py:func:`~sphinx_external_toc_strict.api.SiteMap` or
         :py:func:`~sphinx_external_toc_strict.parsing_shared.create_toc_dict`

    """
    if issubclass(type(site_map), SiteMap):
        data = create_toc_dict(site_map)
    elif isinstance(site_map, dict):
        # sphinx_external_toc_strict.parsing_shared.create_toc_dict call output
        data = site_map
    else:
        msg_exc = (
            "Expecting SiteMap or dict output of"
            f"parsing_shared.create_toc_dict got {type(site_map)}"
        )
        raise ValueError(msg_exc)

    with io.StringIO() as f:
        yaml = s.ruamel.YAML()
        yaml.dump(data, f)
        ret = f.getvalue()

    return ret


def parse_toc_yaml(path, encoding="utf8"):
    """Parse the ToC file

    :param path: `_toc.yml` file path
    :type path: str | pathlib.Path | strictyaml.YAML
    :param encoding: `_toc.yml` file character encoding
    :type encoding: str | None
    :return: parsed site map
    :rtype: sphinx_external_toc_strict.api.SiteMap
    :raises:

       - :py:exc:`ValueError` -- unsupported type expecting a
         :py:class:`pathlib.Path` or :py:class:`strictyaml.YAML`

    """
    msg_exc = f"Expecting a Path or strictyaml.YAML got {type(path)}"
    is_pathlike = path is not None and (
        isinstance(path, str) or issubclass(type(path), PurePath)
    )
    if path is not None:
        if is_pathlike:
            yml = load_yaml(path)
        elif isinstance(path, s.YAML):
            yml = path
        else:
            raise ValueError(msg_exc)
    else:
        raise ValueError(msg_exc)

    sm = parse_toc_data(yml.data)

    return sm


def parse_toc_data(data):
    """Parse a dictionary of the ToC

    :param data: ToC data dictionary
    :type data: dict[str, typing.Any]
    :return: parsed site map
    :rtype: sphinx_external_toc_strict.api.SiteMap
    """
    if not isinstance(data, Mapping):
        raise MalformedError(f"toc is not a mapping: {type(data)}")

    try:
        file_format = FILE_FORMATS[data.get(FILE_FORMAT_KEY, "default")]
    except KeyError:
        raise MalformedError(
            f"'{FILE_FORMAT_KEY}' key value not recognised: "
            f"'{data.get(FILE_FORMAT_KEY, 'default')}'"
        )

    defaults: dict[str, Any] = {**file_format.toc_defaults}
    d_faults = data.get("defaults", {})
    for key_inner, val_inner in d_faults.items():
        try:
            defaults[key_inner] = affinity_val(key_inner, val_inner)
        except s.YAMLValidationError as exc:
            exc_arg = exc.args[0] if exc.args else ""
            msg_exc = (
                f"Field value unexpected: {key_inner}: {val_inner} \n" f"{exc_arg}"
            )
            raise MalformedError(msg_exc)

    doc_item, docs_list = _parse_doc_item(
        data, defaults, "/", depth=0, is_root=True, file_format=file_format
    )

    d_meta = data.get("meta")
    if d_meta is not None and isinstance(d_meta, Mapping):
        for k, v in d_meta.items():
            try:
                v_2 = affinity_val(k, v)
            except s.YAMLValidationError as exc:
                exc_arg = exc.args[0] if exc.args else ""
                msg_exc = f"Field value unexpected: {k}: {v} \n" f"{exc_arg}"
                raise MalformedError(msg_exc)
            else:
                # Type changed?
                if v_2 is not v:
                    d_meta[k] = v_2

    site_map = SiteMap(
        root=doc_item,
        meta=d_meta,
        file_format=data.get(FILE_FORMAT_KEY),
    )

    _parse_docs_list(docs_list, site_map, defaults, depth=1, file_format=file_format)

    return site_map


def _parse_doc_item(
    data,
    defaults,
    path,
    *,
    depth,
    file_format,
    is_root=False,
):
    """Parse a single doc item

    :param data: doc item dictionary
    :type data: dict[str, typing.Any]
    :param defaults: doc item defaults dictionary
    :type defaults: dict[str, typing.Any]
    :param path: doc item file path
    :type path: str
    :param depth: recursive depth (starts at 0)
    :type depth: int
    :param file_format: doc item file format
    :type file_format: FileFormat
    :param is_root: Default False. Whether this is the root item
    :type is_root: bool
    :return: parsed doc item
    :rtype: tuple[sphinx_external_toc_strict.api.Document, collections.abc.Sequence[tuple[str, dict[str, typing.Any]]]]
    :raises:

       - :py:exc:`MalformedError` -- invalid doc item

    :meta private:
    """
    file_key = ROOT_KEY if is_root else FILE_KEY
    if file_key not in data.keys():
        raise MalformedError(f"'{file_key}' key not found @ '{path}'")

    subtrees_key = file_format.get_subtrees_key(depth)
    items_key = file_format.get_items_key(depth)

    # check no unknown keys present
    allowed_keys = {
        file_key,
        "title",
        "options",
        subtrees_key,
        items_key,
        # top-level only
        FILE_FORMAT_KEY,
        "defaults",
        "meta",
    }
    if not allowed_keys.issuperset(data.keys()):
        unknown_keys = set(data.keys()).difference(allowed_keys)
        raise MalformedError(
            f"Unknown keys found: {unknown_keys!r}, allowed: {allowed_keys!r} @ '{path}'"
        )

    shorthand_used = False
    if items_key in data:
        # this is a shorthand for defining a single subtree
        if subtrees_key in data:
            raise MalformedError(
                f"Both '{subtrees_key}' and '{items_key}' found @ '{path}'"
            )
        subtrees_data = [{items_key: data[items_key], **data.get("options", {})}]
        shorthand_used = True
    elif subtrees_key in data:
        subtrees_data = data[subtrees_key]
        if not (isinstance(subtrees_data, Sequence) and subtrees_data):
            raise MalformedError(f"'{subtrees_key}' not a non-empty list @ '{path}'")
        path = f"{path}{subtrees_key}/"
    else:
        subtrees_data = []

    _known_link_keys = {FILE_KEY, GLOB_KEY, URL_KEY}

    toctrees = []
    for toc_idx, toc_data in enumerate(subtrees_data):
        toc_path = path if shorthand_used else f"{path}{toc_idx}/"

        if not (isinstance(toc_data, Mapping) and items_key in toc_data):
            raise MalformedError(
                f"entry not a mapping containing '{items_key}' key @ '{toc_path}'"
            )

        items_data = toc_data[items_key]

        if not (isinstance(items_data, Sequence) and items_data):
            raise MalformedError(f"'{items_key}' not a non-empty list @ '{toc_path}'")

        # generate items list
        items: list[GlobItem | FileItem | UrlItem] = []
        for item_idx, item_data in enumerate(items_data):
            if not isinstance(item_data, Mapping):
                raise MalformedError(
                    f"entry not a mapping type @ '{toc_path}{items_key}/{item_idx}'"
                )

            link_keys = _known_link_keys.intersection(item_data)

            # validation checks
            if not link_keys:
                raise MalformedError(
                    f"entry does not contain one of "
                    f"{_known_link_keys!r} @ '{toc_path}{items_key}/{item_idx}'"
                )
            if not len(link_keys) == 1:
                raise MalformedError(
                    f"entry contains incompatible keys "
                    f"{link_keys!r} @ '{toc_path}{items_key}/{item_idx}'"
                )
            for item_key in (GLOB_KEY, URL_KEY):
                for other_key in (subtrees_key, items_key):
                    if link_keys == {item_key} and other_key in item_data:
                        raise MalformedError(
                            f"entry contains incompatible keys "
                            f"'{item_key}' and '{other_key}' @ '{toc_path}{items_key}/{item_idx}'"
                        )

            try:
                if link_keys == {FILE_KEY}:
                    items.append(FileItem(item_data[FILE_KEY]))
                elif link_keys == {GLOB_KEY}:
                    items.append(GlobItem(item_data[GLOB_KEY]))
                elif link_keys == {URL_KEY}:
                    items.append(UrlItem(item_data[URL_KEY], item_data.get("title")))
                else:  # pragma: no cover unknown link key already handled
                    pass
            except (ValueError, TypeError) as exc:
                exc_arg = exc.args[0] if exc.args else ""
                raise MalformedError(
                    f"entry validation @ '{toc_path}{items_key}/{item_idx}': {exc_arg}"
                ) from exc

        # generate toc key-word arguments
        """
        keywords = {k: toc_data[k] for k in TOCTREE_OPTIONS if k in toc_data}
        for key in defaults:
            if key not in keywords.keys():
                keywords[key] = defaults[key]
            else:  # pragma: no cover key already in dict
                pass
        """
        d_keywords = {}
        for k in TOCTREE_OPTIONS:
            if k in toc_data:
                try:
                    v = toc_data[k]
                    v_2 = affinity_val(k, v)
                except s.YAMLValidationError as exc:
                    exc_arg = exc.args[0] if exc.args else ""
                    msg_exc = f"Field value unexpected: {k}: {v} \n" f"{exc_arg}"
                    raise MalformedError(msg_exc)
                else:
                    d_keywords[k] = v_2

        for key in defaults:
            if key not in d_keywords.keys():
                d_keywords[key] = defaults[key]
            else:  # pragma: no cover key already in dict
                pass

        try:
            # toc_item = TocTree(items=items, **keywords)
            toc_item = TocTree(items=items, **d_keywords)
        except (ValueError, TypeError) as exc:
            exc_arg = exc.args[0] if exc.args else ""
            raise MalformedError(
                f"toctree validation @ '{toc_path}': {exc_arg}"
            ) from exc
        toctrees.append(toc_item)

    try:
        doc_item = Document(
            docname=data[file_key], title=data.get("title"), subtrees=toctrees
        )
    except (ValueError, TypeError) as exc:
        exc_arg = exc.args[0] if exc.args else ""
        raise MalformedError(f"doc validation @ '{path}': {exc_arg}") from exc

    # list of docs that need to be parsed recursively (and path)
    """docs_to_be_parsed_list = [
        (
            f"{path}/{items_key}/{ii}/"
            if shorthand_used
            else f"{path}{ti}/{items_key}/{ii}/",
            item_data,
        )
        for ti, toc_data in enumerate(subtrees_data)
        for ii, item_data in enumerate(toc_data[items_key])
        if FILE_KEY in item_data
    ]
    """
    docs_to_be_parsed_list = []
    for ti, toc_data in enumerate(subtrees_data):
        for ii, item_data in enumerate(toc_data[items_key]):
            if FILE_KEY in item_data:
                str_path = (
                    f"{path}/{items_key}/{ii}/"
                    if shorthand_used
                    else f"{path}{ti}/{items_key}/{ii}/"
                )
                t_pair = (str_path, item_data)
                docs_to_be_parsed_list.append(t_pair)

    return (
        doc_item,
        docs_to_be_parsed_list,
    )


def _parse_docs_list(
    docs_list,
    site_map,
    defaults,
    *,
    depth,
    file_format,
):
    """Parse a list of docs

    :param docs_list: sequence of doc items
    :type docs_list: collections.abc.Sequence[tuple[str, dict[str, typing.Any]]]
    :param site_map: site map
    :type site_map: sphinx_external_toc_strict.SiteMap
    :param defaults: default doc item values
    :type defaults: dict[str, typing.Any]
    :param depth: recursive depth (starts at 0)
    :type depth: int
    :param file_format: doc item file format
    :type file_format: FileFormat
    :raises:

       - :py:exc:`MalformedError` -- doc file used multiple times

    :meta private:
    """
    for child_path, doc_data in docs_list:
        docname = doc_data[FILE_KEY]
        if docname in site_map:
            raise MalformedError(f"document file used multiple times: '{docname}'")
        child_item, child_docs_list = _parse_doc_item(
            doc_data,
            defaults,
            child_path,
            depth=depth,
            file_format=file_format,
        )
        site_map[docname] = child_item

        _parse_docs_list(
            child_docs_list,
            site_map,
            defaults,
            depth=depth + 1,
            file_format=file_format,
        )
