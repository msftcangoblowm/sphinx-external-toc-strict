"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Without coverage

.. code-block:: shell

   pytest -s --showlocals -vv "tests/test_parsing.py"

With coverage

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.parsing_strictyaml' -m pytest \
   --showlocals tests/test_parsing.py && coverage report \
   --data-file=.coverage --include="**/parsing_strictyaml.py"

"""

from pathlib import Path
from typing import TYPE_CHECKING

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

if TYPE_CHECKING:
    import types
    from typing import Any

    import strictyaml as s

    from .fr import FileRegression
    from .typing_only import DOES_NOT_OR_DOES

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: "Path", data_regression: "FileRegression") -> None:
    """Test parse_toc_yaml with good files."""
    site_map = parse_toc_yaml(path)
    data_regression.check(site_map.as_json())


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_create_toc_dict(path: "Path", data_regression: "FileRegression") -> None:
    """Test create_toc_dict with good files."""
    site_map = parse_toc_yaml(path)
    data = create_toc_dict(site_map)
    data_regression.check(data)


TOC_FILES_BAD = list(Path(__file__).parent.joinpath("_bad_toc_files").glob("*.yml"))
ERROR_MESSAGES = {
    # "bad_option_value.yml": "toctree validation @ '/': 'titlesonly'",
    "bad_option_value.yml": "Field value unexpected: .+",
    "bad_url.yml": "entry validation @ '/entries/0': 'url' must match regex",
    "doc_multiple_times.yml": "Document file used multiple times: '.+'",  # .+ --> *
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
def test_malformed_file_parse(path: "Path") -> None:
    """Test parse_toc_yaml with bad files."""
    message = ERROR_MESSAGES[path.name]
    with pytest.raises(MalformedError, match=message):
        parse_toc_yaml(path)


@pytest.mark.parametrize(
    "path, expectation",
    (
        pytest.param(
            None,
            pytest.raises(ValueError),
            id="data-source-None",
        ),
        pytest.param(
            1.12345,
            pytest.raises(ValueError),
            id="data-source-unsupported-type",
        ),
    ),
)
def test_parse_toc_yaml_bad_input(
    path: "float | None",
    expectation: "DOES_NOT_OR_DOES",
) -> None:
    """Test parse_toc_yaml."""
    with expectation:
        parse_toc_yaml(
            path,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "relpath_toc_yaml, depth, skip_defaults, expectation",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            0,
            True,
            pytest.raises(TypeError),
            id="basic-toc-yaml",
        ),
    ),
)
def test_parse_item_testable(
    relpath_toc_yaml: "Path",
    depth: int,
    skip_defaults: bool,
    expectation: "DOES_NOT_OR_DOES",
    request: pytest.FixtureRequest,
) -> None:
    """Cause a TypeError"""
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml = abspath_tests_dir.joinpath(relpath_toc_yaml)
    toc_yaml_abspath = abspath_toc_yaml.as_posix()

    site_map = parse_toc_yaml(toc_yaml_abspath)
    # doc_item = site_map.root
    file_format = FILE_FORMATS[site_map.file_format or "default"]
    parsed_docnames = set()
    with expectation:
        _parse_item_testable(
            site_map,
            0.12345,
            depth,
            file_format,
            skip_defaults,
            parsed_docnames,
        )


@pytest.mark.parametrize(
    "relpath_toc_yaml, file_format",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            "Trevor",
            id="invalid-file-format",
        ),
    ),
)
def test_create_toc_dict_bad_file_format(
    relpath_toc_yaml: "Path",
    file_format: str,
    request: pytest.FixtureRequest,
) -> None:
    """site map with invalid file format (aka use case)"""
    # pytest --showlocals --log-level INFO -k "test_create_toc_dict_bad_file_format" tests
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml = abspath_tests_dir.joinpath(relpath_toc_yaml)
    toc_yaml_abspath = abspath_toc_yaml.as_posix()

    # create site map with invalid file format (aka use case)
    assert file_format not in use_cases

    # prepare
    #    create a site_map with an unknown file format
    site_map = parse_toc_yaml(toc_yaml_abspath)
    site_map._file_format = file_format

    with pytest.raises(KeyError):
        create_toc_dict(site_map)

    # setter ignores invalid file formats
    ff_before = site_map.file_format
    site_map.file_format = "fdsadfdsfsafsadfasdf"
    ff_after = site_map.file_format
    assert ff_before == ff_after


@pytest.mark.parametrize(
    "key, val, mapping, expected",
    (
        pytest.param(
            "entries",
            {"file": "bob"},
            None,
            {"file": "bob"},
            id="not-scalar-mapping-None",
        ),
        pytest.param(
            "entries",
            {"file": "bob"},
            1.12345,
            {"file": "bob"},
            id="not-scalar-mapping-unsupported-type",
        ),
        pytest.param(
            "entries",
            {"file": "bob"},
            _scalar_affinity_map,
            {"file": "bob"},
            id="not-scalar-mapping-default-mapping",
        ),
    ),
)
def test_affinity_val(
    key: str,
    val: dict[str, str],
    mapping: "types.MappingProxyType[str, s.validators.Validator] | float | None",
    expected: dict[str, str],
) -> None:
    """Use type affinity and a mapping to coerce value data type"""
    # pytest --showlocals --log-level INFO -k "test_affinity_val" tests
    val_out = affinity_val(
        key,
        val,
        mapping=mapping,  # type: ignore[arg-type]
    )
    assert val_out == expected


@pytest.mark.parametrize(
    "data, expectation",
    (
        pytest.param(
            {"defaults": {"caption": 1.12345}},
            pytest.raises(MalformedError),
            id="Field-value-unexpected",
        ),
        pytest.param(
            {"defaults": {"maxdepth": 1.12345}},
            pytest.raises(MalformedError),
            id="maxdepth=normally-an-int-received-float",
        ),
        pytest.param(
            {
                "defaults": {"maxdepth": 1},
                "root": "intro",
                "meta": {"unknown": 1.12345},
            },
            pytest.raises(MalformedError),
            id="meta-unknown-normally-an-int-received-float",
        ),
    ),
)
def test_parse_toc_data(
    data: "dict[str, Any]", expectation: "DOES_NOT_OR_DOES"
) -> None:
    """Test parse_toc_data."""
    # pytest --showlocals --log-level INFO -k "test_parse_toc_data" tests
    with expectation:
        parse_toc_data(data)


@pytest.mark.parametrize(
    "invalid, expectation",
    (
        pytest.param(
            None,
            pytest.raises(ValueError),
            id="Forgot-to-check-for-None-huh",
        ),
        pytest.param(
            1.1234,
            pytest.raises(ValueError),
            id="float-unsupported-type",
        ),
    ),
)
def test_dump_yaml(
    invalid: "float | None",
    expectation: "DOES_NOT_OR_DOES",
) -> None:
    """Unsupported type --> ValueError"""
    with expectation:
        dump_yaml(invalid)
