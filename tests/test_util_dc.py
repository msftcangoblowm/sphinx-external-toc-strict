"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

``util_dc`` module was renamed from ``_compat``.

With coverage

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.util_dc' -m pytest \
   --showlocals tests/test_util_dc.py && coverage report \
   --data-file=.coverage --include="**/util_dc.py"

"""

import re
from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING

import pytest

from sphinx_external_toc_strict.util_dc import matches_re

if TYPE_CHECKING:
    from tests.typing_only import DOES_NOT_OR_DOES


@pytest.mark.parametrize(
    "pattern, flags, expectation",
    (
        pytest.param(
            re.compile(r"[A-za-z0-9]*"), 0, does_not_raise(), id="re.Pattern-base-case"
        ),
        pytest.param(
            re.compile(r"[A-za-z0-9]*"),
            1,
            pytest.raises(TypeError),
            id="re.Pattern-unexpected-flag",
        ),
    ),
)
def test_util_dc_matches_re(
    pattern: "re.Pattern[str] | str",
    flags: int,
    expectation: "DOES_NOT_OR_DOES",
) -> None:
    """matches_re tolerates both str and re.Pattern[str]"""
    # pytest --showlocals --log-level INFO -k "test_util_dc_matches_re" tests
    # remove py2 support which lacks re.fullmatch; do not continue to emulate it.
    assert hasattr(re, "fullmatch")
    with expectation:
        matches_re(pattern, flags)
    if isinstance(expectation, does_not_raise):
        pass
