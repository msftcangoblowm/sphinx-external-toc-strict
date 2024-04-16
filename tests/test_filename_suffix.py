import pytest

from sphinx_external_toc_strict.filename_suffix import (
    _strip_suffix_natural,
    _strip_suffix_or,
    strip_suffix,
)

testdata_strip_suffix = [
    ("file.tar.gz", (), "file.tar.gz"),
    ("file.tar.gz", (".tar.gz"), "file"),
    ("file.tar.gz", ("tar",), "file.tar.gz"),
    ("file.tar.gz", ("gz",), "file.tar"),
    ("file.tar.gz", ("zip", "xz", "rar", "txt", "ai"), "file.tar.gz"),
    ("file", ("file",), "file"),
    ("file.tar.gz", (".md.gz"), "file.tar"),
    ("file.tar.gz", "asdf.md.gz", "file.tar"),
    ("file.gz", ".md.gz", "file"),
]
ids_strip_suffix = [
    "no suffixes provided. Nothing to strip from file name",
    "strip tar.gz",
    "cannot strip tar from tar.gz",
    "can strip gz from tar.gz",
    "lots of non-match suffixes",
    "file stem is not a suffix",
    "weak knees, quit while ahead",
    "str suffixes provided with a stem",
    "ran out of chips",
]


@pytest.mark.parametrize(
    "file_name, suffixes, expected",
    testdata_strip_suffix,
    ids=ids_strip_suffix,
)
def test_strip_suffix(file_name, suffixes, expected):
    """From file name no suffixes provided to strip"""
    out = strip_suffix(file_name, suffixes)
    assert out == expected


testdata_strip_suffix_natural = [
    ("file.tar.gz", (".tar.gz",)),
    (
        "file.tar.gz",
        [
            ".tar.gz",
        ],
    ),
    ("file.tar.gz", 1.1234),
]
ids_strip_suffix_natural = [
    "suffix is of type tuple, expects str",
    "suffix is of type list, expects str",
    "suffix is of type float, expects str",
]


@pytest.mark.parametrize(
    "name, suffixes",
    testdata_strip_suffix_natural,
    ids=ids_strip_suffix_natural,
)
def test_strip_suffix_natural(name, suffixes):
    """do_not_cross_streams"""
    with pytest.raises(AssertionError):
        _strip_suffix_natural(name, suffixes)


testdata_strip_suffix_or = [
    (
        "file.tar.gz",
        ".tar.gz",
    ),
    ("file.tar.gz", (".tar.gz",)),
    ("file.tar.gz", 1.1234),
]
ids_strip_suffix_or = [
    "suffix is of type str, expects list",
    "suffix is of type tuple, expects list",
    "suffix is of type float, expects list",
]


@pytest.mark.parametrize(
    "name, suffixes",
    testdata_strip_suffix_or,
    ids=ids_strip_suffix_or,
)
def test_strip_suffix_or(name, suffixes):
    """do_not_cross_streams"""
    with pytest.raises(AssertionError):
        _strip_suffix_or(name, suffixes)


def test_strip_suffix_errors():
    name = "bob"
    suffixes = 1.1234
    with pytest.raises(ValueError):
        strip_suffix(name, suffixes)

    suffixes = (".tar.gz",)  # tuple, not a list
    strip_suffix(name, suffixes)
    assert name == "bob"
