"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

file name suffix handling module.

With coverage

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.filename_suffix' -m pytest \
   --showlocals tests/test_filename_suffix.py && coverage report \
   --data-file=.coverage --include="**/filename_suffix.py"

"""

from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING

import pytest

from sphinx_external_toc_strict.filename_suffix import (
    _strip_suffix_natural,
    _strip_suffix_or,
    strip_suffix,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Sequence,
    )

    from tests.typing_only import DOES_NOT_OR_DOES


@pytest.mark.parametrize(
    "fcn, name, suffixes, expectation",
    (
        pytest.param(
            _strip_suffix_natural,
            "file.tar.gz",
            (".tar.gz",),
            pytest.raises(AssertionError),
            id="suffix-is-of-type-tuple-expects-str",
        ),
        pytest.param(
            _strip_suffix_natural,
            "file.tar.gz",
            [
                ".tar.gz",
            ],
            pytest.raises(AssertionError),
            id="suffix-is-of-type-list-expects-str",
        ),
        pytest.param(
            _strip_suffix_natural,
            "file.tar.gz",
            1.1234,
            pytest.raises(AssertionError),
            id="suffix-is-of-type-float-expects-str",
        ),
        pytest.param(
            _strip_suffix_or,
            "file.tar.gz",
            ".tar.gz",
            pytest.raises(AssertionError),
            id="suffix-is-of-type-str-expects-list",
        ),
        pytest.param(
            _strip_suffix_or,
            "file.tar.gz",
            (".tar.gz",),
            pytest.raises(AssertionError),
            id="suffix-is-of-type-tuple-expects-list",
        ),
        pytest.param(
            _strip_suffix_or,
            "file.tar.gz",
            1.1234,
            pytest.raises(AssertionError),
            id="suffix-is-of-type-float-expects-list",
        ),
        pytest.param(
            strip_suffix,
            "bob",
            1.1234,
            pytest.raises(ValueError),
            id="cause-a-ValueError",
        ),
    ),
)
def test_strip_expectation_fail(
    fcn: "Callable[[str, str], str] | Callable[[str, list[str]], str]",
    name: str,
    suffixes: "Sequence[str] | float",
    expectation: "DOES_NOT_OR_DOES",
) -> None:
    """streams crossed"""
    # pytest --showlocals --log-level INFO -k "test_strip_expectation_fail" tests
    with expectation:
        fcn(
            name,
            suffixes,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "fcn, name, suffixes, expectation, expected",
    (
        pytest.param(
            strip_suffix,
            "bob",
            (".tar.gz",),
            does_not_raise(),
            "bob",
            id="Does-no-harm-if-file-name-doesnt-have-any-suffixes",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            (),
            does_not_raise(),
            "file.tar.gz",
            id="no-suffixes-provided.-Nothing-to-strip-from-file-name",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            (".tar.gz"),  # is this supposed to be a tuple. It's a str!
            does_not_raise(),
            "file",
            id="strip-tar.gz",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            ("tar",),
            does_not_raise(),
            "file.tar.gz",
            id="cannot-strip-tar-from-tar.gz",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            ("gz",),
            does_not_raise(),
            "file.tar",
            id="can-strip-gz-from=tar.gz",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            ("zip", "xz", "rar", "txt", "ai"),
            does_not_raise(),
            "file.tar.gz",
            id="lots-of-non-match-suffixes",
        ),
        pytest.param(
            strip_suffix,
            "file",
            ("file",),
            does_not_raise(),
            "file",
            id="file-stem-is-not-a-suffix",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            (".md.gz"),  # is this supposed to be a tuple. It's a str!
            does_not_raise(),
            "file.tar",
            id="weak-knees,-quit-while-ahead",
        ),
        pytest.param(
            strip_suffix,
            "file.tar.gz",
            "asdf.md.gz",
            does_not_raise(),
            "file.tar",
            id="str-suffixes-provided-with-a-stem",
        ),
        pytest.param(
            strip_suffix,
            "file.gz",
            ".md.gz",
            does_not_raise(),
            "file",
            id="ran-out-of-chips",
        ),
    ),
)
def test_strip_expectation_success(
    fcn: "Callable[[str, Sequence[str]], str]",
    name: str,
    suffixes: "Sequence[str] | str | float",
    expectation: "DOES_NOT_OR_DOES",
    expected: "str | None",
) -> None:
    """Test strip_suffix."""
    # pytest --showlocals --log-level INFO -k "test_strip_expectation_success" tests
    with expectation:
        actual = fcn(
            name,
            suffixes,  # type: ignore[arg-type]
        )
    if isinstance(expectation, does_not_raise):
        assert expected == actual
