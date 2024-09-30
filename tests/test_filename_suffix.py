"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

file name suffix handling module.

Unit test -- Module

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.filename_suffix' -m pytest \
   --showlocals tests/test_filename_suffix.py && coverage report \
   --data-file=.coverage --include="**/filename_suffix.py"

"""

from contextlib import nullcontext as does_not_raise

import pytest

from sphinx_external_toc_strict.filename_suffix import (
    _strip_suffix_natural,
    _strip_suffix_or,
    strip_suffix,
)

testdata_strip_suffix_natural = [
    (
        "file.tar.gz",
        (".tar.gz",),
        pytest.raises(AssertionError),
    ),
    (
        "file.tar.gz",
        [
            ".tar.gz",
        ],
        pytest.raises(AssertionError),
    ),
    (
        "file.tar.gz",
        1.1234,
        pytest.raises(AssertionError),
    ),
]
ids_strip_suffix_natural = [
    "suffix is of type tuple, expects str",
    "suffix is of type list, expects str",
    "suffix is of type float, expects str",
]


@pytest.mark.parametrize(
    "name, suffixes, expectation",
    testdata_strip_suffix_natural,
    ids=ids_strip_suffix_natural,
)
def test_strip_suffix_natural(name, suffixes, expectation):
    """do_not_cross_streams"""
    with expectation:
        _strip_suffix_natural(name, suffixes)


testdata_strip_suffix_or = [
    (
        "file.tar.gz",
        ".tar.gz",
        pytest.raises(AssertionError),
    ),
    ("file.tar.gz", (".tar.gz",), pytest.raises(AssertionError)),
    ("file.tar.gz", 1.1234, pytest.raises(AssertionError)),
]
ids_strip_suffix_or = [
    "suffix is of type str, expects list",
    "suffix is of type tuple, expects list",
    "suffix is of type float, expects list",
]


@pytest.mark.parametrize(
    "name, suffixes, expectation",
    testdata_strip_suffix_or,
    ids=ids_strip_suffix_or,
)
def test_strip_suffix_or(name, suffixes, expectation):
    """Test strip_suffix_or. Exceptions."""
    # pytest --showlocals --log-level INFO -k "test_strip_suffix_or" tests
    with expectation:
        _strip_suffix_or(name, suffixes)


testdata_strip_suffix_errors = (
    (
        "bob",
        1.1234,
        pytest.raises(ValueError),
        None,
    ),
    (
        "bob",
        (".tar.gz",),
        does_not_raise(),
        "bob",
    ),
    ("file.tar.gz", (), does_not_raise(), "file.tar.gz"),
    ("file.tar.gz", (".tar.gz"), does_not_raise(), "file"),
    ("file.tar.gz", ("tar",), does_not_raise(), "file.tar.gz"),
    ("file.tar.gz", ("gz",), does_not_raise(), "file.tar"),
    ("file.tar.gz", ("zip", "xz", "rar", "txt", "ai"), does_not_raise(), "file.tar.gz"),
    ("file", ("file",), does_not_raise(), "file"),
    ("file.tar.gz", (".md.gz"), does_not_raise(), "file.tar"),
    ("file.tar.gz", "asdf.md.gz", does_not_raise(), "file.tar"),
    ("file.gz", ".md.gz", does_not_raise(), "file"),
)
ids_strip_suffix_errors = (
    "Cause a ValueError",
    "Does no harm if file name doesn't have any suffixes",
    "no suffixes provided. Nothing to strip from file name",
    "strip tar.gz",
    "cannot strip tar from tar.gz",
    "can strip gz from tar.gz",
    "lots of non-match suffixes",
    "file stem is not a suffix",
    "weak knees, quit while ahead",
    "str suffixes provided with a stem",
    "ran out of chips",
)


@pytest.mark.parametrize(
    "name, suffixes, expectation, expected",
    testdata_strip_suffix_errors,
    ids=ids_strip_suffix_errors,
)
def test_strip_suffix_errors(name, suffixes, expectation, expected):
    """Test strip_suffix."""
    # pytest --showlocals --log-level INFO -k "test_strip_suffix_errors" tests
    with expectation:
        actual = strip_suffix(name, suffixes)
    if isinstance(expectation, does_not_raise):
        assert expected == actual
