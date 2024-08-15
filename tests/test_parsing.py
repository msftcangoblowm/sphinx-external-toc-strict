import os
from pathlib import Path

import pytest

from sphinx_external_toc_strict.constants import use_cases
from sphinx_external_toc_strict.exceptions import MalformedError
from sphinx_external_toc_strict.parsing_shared import (
    FILE_FORMATS,
    _parse_item_testable,
    create_toc_dict,
)
from sphinx_external_toc_strict.parsing_strictyaml import (
    _scalar_affinity_map,
    affinity_val,
    dump_yaml,
    parse_toc_data,
    parse_toc_yaml,
)

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, data_regression):
    site_map = parse_toc_yaml(path)
    data_regression.check(site_map.as_json())


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_create_toc_dict(path: Path, data_regression):
    site_map = parse_toc_yaml(path)
    data = create_toc_dict(site_map)
    data_regression.check(data)


TOC_FILES_BAD = list(Path(__file__).parent.joinpath("_bad_toc_files").glob("*.yml"))
ERROR_MESSAGES = {
    # "bad_option_value.yml": "toctree validation @ '/': 'titlesonly'",
    "bad_option_value.yml": "Field value unexpected: .+",
    "bad_url.yml": "entry validation @ '/entries/0': 'url' must match regex",
    "doc_multiple_times.yml": "document file used multiple times: '.+'",  # .+ --> *
    # "doc_validation_fail.yml": "doc validation @ .+",  # .+ --> *
    "doc_validation_fail.yml": "Field value unexpected: .+",  # .+ --> *
    "empty.yml": "toc is not a mapping:",
    "file_and_glob_present.yml": "entry contains incompatible keys .* @ '/entries/0'",
    "list.yml": "toc is not a mapping:",
    "unknown_keys.yml": "Unknown keys found: .* @ '/'",
    "unknown_usecase.yml": "'format' key value not recognised: 'epub'",
    "empty_items.yml": "'entries' not a non-empty list @ '/'",
    "entry_not_a_mapping.yml": "entry not a mapping type @ '/entries/0'",
    "entry_unknown_link_type.yml": r"entry does not contain one of {'.+', '.+', '.+'} @ '/entries/0'",  # .+ --> *
    "item_then_subtrees_key.yml": "Both 'subtrees' and 'entries' found @ '/'",
    "items_in_glob.yml": "entry contains incompatible keys 'glob' and 'entries' @ '/entries/0'",
    "no_root.yml": "'root' key not found @ '/'",
    "unknown_keys_nested.yml": (
        "Unknown keys found: {'unknown'}, allow.* " "@ '/subtrees/0/entries/1/'"
    ),
    "empty_subtrees.yml": "'subtrees' not a non-empty list @ '/'",
    "items_in_url.yml": "entry contains incompatible keys 'url' and 'entries' @ '/entries/0'",
    "subtree_with_no_items.yml": "entry not a mapping containing 'entries' key @ '/subtrees/0/'",
}


@pytest.mark.parametrize(
    "path", TOC_FILES_BAD, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES_BAD]
)
def test_malformed_file_parse(path: Path):
    message = ERROR_MESSAGES[path.name]
    with pytest.raises(MalformedError, match=message):
        parse_toc_yaml(path)


testdata_parse_toc_yaml_bad_input = [
    None,
    1.12345,
]
ids_parse_toc_yaml_bad_input = [
    "data source None",
    "data source unsupported type",
]


@pytest.mark.parametrize(
    "path",
    testdata_parse_toc_yaml_bad_input,
    ids=ids_parse_toc_yaml_bad_input,
)
def test_parse_toc_yaml_bad_input(path):
    with pytest.raises(ValueError):
        parse_toc_yaml(path)


def test_parse_item_testable():
    """Cause a TypeError"""
    path = os.path.abspath(Path(__file__).parent.joinpath("_toc_files", "basic.yml"))
    site_map = parse_toc_yaml(path)
    # doc_item = site_map.root
    depth = 0
    file_format = FILE_FORMATS[site_map.file_format or "default"]
    skip_defaults = True
    parsed_docnames = set()
    with pytest.raises(TypeError):
        _parse_item_testable(
            site_map,
            0.12345,
            depth,
            file_format,
            skip_defaults,
            parsed_docnames,
        )


testdata_create_toc_dict_bad_file_format = (
    (
        Path(__file__).parent.joinpath("_toc_files", "basic.yml"),
        "Trevor",
    ),
)
ids_create_toc_dict_bad_file_format = ("invalid file format",)


@pytest.mark.parametrize(
    "path_toc, file_format",
    testdata_create_toc_dict_bad_file_format,
    ids=ids_create_toc_dict_bad_file_format,
)
def test_create_toc_dict_bad_file_format(path_toc, file_format):
    """site map with invalid file format (aka use case)"""
    # pytest --showlocals --log-level INFO -k "test_create_toc_dict_bad_file_format" tests
    # create site map with invalid file format (aka use case)
    assert file_format not in use_cases

    # prepare
    #    create a site_map with an unknown file format
    site_map = parse_toc_yaml(str(path_toc))
    site_map._file_format = file_format

    with pytest.raises(KeyError):
        create_toc_dict(site_map)

    # setter ignores invalid file formats
    ff_before = site_map.file_format
    site_map.file_format = "fdsadfdsfsafsadfasdf"
    ff_after = site_map.file_format
    assert ff_before == ff_after


testdata = [
    ("entires", {"file": "bob"}, None, {"file": "bob"}),
    ("entires", {"file": "bob"}, 1.12345, {"file": "bob"}),
    ("entires", {"file": "bob"}, _scalar_affinity_map, {"file": "bob"}),
]
ids = [
    "not scalar, mapping None",
    "not scalar, mapping unsupported type",
    "not scalar, mapping default mapping",
]


@pytest.mark.parametrize(
    "key, val, mapping, expected",
    testdata,
    ids=ids,
)
def test_affinity_val(key, val, mapping, expected):
    """Use type affinity and a mapping to coerse value data type"""
    val_out = affinity_val(key, val, mapping=mapping)
    assert val_out == expected


testdata_parse_toc_data = [
    ({"defaults": {"caption": 1.12345}}),
    ({"defaults": {"maxdepth": 1.12345}}),
    ({"defaults": {"maxdepth": 1}, "root": "intro", "meta": {"unknown": 1.12345}}),
]
ids_parse_toc_data = [
    "Field value unexpected",
    "maxdepth normally an int, received float",
    "meta unknown normally an int, received float",
]


@pytest.mark.parametrize(
    "data",
    testdata_parse_toc_data,
    ids=ids_parse_toc_data,
)
def test_parse_toc_data(data):
    with pytest.raises(MalformedError):
        parse_toc_data(data)


testdata_unsupported_type = (
    (None,),
    (1.1234,),
)
ids_unsupported_type = (
    "Forgot to check for None, huh?",
    "float unsupported type",
)


@pytest.mark.parametrize(
    "invalid",
    testdata_unsupported_type,
    ids=ids_unsupported_type,
)
def test_dump_yaml(invalid):
    """unsupported type --> ValueError"""
    with pytest.raises(ValueError):
        dump_yaml(invalid)
