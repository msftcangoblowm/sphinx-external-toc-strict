"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Given a file name, not a file path, strip suffixes

Very confusing

If a Sequence (".md", ".rst"), this is OR logic, strip suffix from end of file name

If a str, e.g. ".tar", a smarter algo is required.

.. py:data: __all__
   :type: tuple[str, str]
   :value: ("strip_suffix", "stem_natural")

   module exports

"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    cast,
)

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence


__all__ = ("strip_suffix", "stem_natural")


def stem_natural(name):
    """Similiar to Path.stem, but removes all suffixes and doesn't fail
    if there is no stem

    :param name: file name, not file path
    :type name: str
    :returns: file stem without any suffixes
    :rtype: str
    """
    # Split file name into parts. Not a file path
    try:
        # Does name contain any suffixes?
        name.index(".")
    except ValueError:
        # name does not contain any suffixes. Nothing to strip
        ret = name
    else:
        ret = name[: name.index(".")]

    return ret


def _strip_suffix_natural(name, suffixes):
    """Strip suffixes from file name

    - Do not confuse a stem and a suffix

    :param name: file name
    :type name: str
    :param suffixes: **strictly** str only. e.g. ".tar.gz" or "" or ".rm"
    :type suffixes: str
    :returns: file name stripped out suffix
    :rtype: str
    :raises:

        - :py:exc:`AssertionError` -- this algo is for one string only

    :meta private:
    """
    if TYPE_CHECKING:
        l_suffixes: list[str]

    if not isinstance(suffixes, str):
        raise AssertionError("this algo is for one string only")

    stem = stem_natural(name)

    """pathlib.Path.suffixes bug: Without a stem,
    :py:attr:`pathlib.Path.suffixes` gives wrong result"""
    if suffixes.startswith("."):
        placeholder = "asdf"
        l_suffixes = Path(f"{placeholder}{suffixes}").suffixes
    else:
        # suffixes given with a stem ... duh
        l_suffixes = Path(suffixes).suffixes

    # in-place reverse user supplied suffixes
    # [".tar", ".gz"] --> [".gz", ".tar"]
    l_suffixes.reverse()

    lst_suffixes = Path(name).suffixes

    for idx_loop, suffix in enumerate(l_suffixes):
        is_no_remaining = len(lst_suffixes) == 0

        if is_no_remaining:
            # Ran out of chips. Awwwwwh!
            break
        else:
            if lst_suffixes[-1] == suffix:
                lst_suffixes.pop()
            else:
                # Weak nerves. Only continue if on perfect winning streak
                break
    ret_suffixes = "".join(lst_suffixes)

    ret = f"{stem}{ret_suffixes}"

    return ret


def _strip_suffix_or(name, suffixes):
    """OR logic algo. Do not break apart suffix str

    - Do not confuse a stem and a suffix

    :param name: file name
    :type name: str
    :param suffixes: Strictly list[str]. Or logic compare complete str
    :type suffixes: list[str]
    :returns: file name stripped out suffix
    :rtype: str
    :raises:

        - :py:exc:`AssertionError` -- this algo is for one list[str] only

    :meta private:
    """
    if not isinstance(suffixes, list):
        raise AssertionError("this algo is list[str] only")

    # Check suffixes preceded with a dot
    # tar.gz --> .tar.gz
    for idx, suffix in enumerate(suffixes):
        if not suffix.startswith("."):
            suffixes[idx] = f".{suffix}"

    stem = stem_natural(name)

    lst_suffixes = Path(name).suffixes
    str_suffixes = "".join(lst_suffixes)

    if len(str_suffixes) == 0:
        ret = name
    else:
        ret = f"{stem}{str_suffixes}"
        for token in suffixes:
            if str_suffixes.endswith(token):
                str_suffixes = str_suffixes[: -len(token)]
                ret = f"{stem}{str_suffixes}"
                break

    return ret


def strip_suffix(name, suffixes):
    """Strip suffixes from file name

    - Do not confuse a stem and a suffix

    :param name: file name
    :type name: str
    :param suffixes: Strictly Sequence[str]
    :type suffixes: str | collections.abc.Sequence[str]
    :returns: file name stripped out suffix
    :rtype: str
    :raises:

       - :py:exc:`ValueError` -- Unsupported type expecting a str or a Sequence[str]

    """
    msg_exc = (
        f"Unsupported type expecting a str or a Sequence[str] got {type(suffixes)}"
    )

    if isinstance(suffixes, str):
        return _strip_suffix_natural(name, suffixes)

    if not isinstance(suffixes, Sequence):
        raise ValueError(msg_exc)

    if isinstance(suffixes, tuple):
        suffixes_a = list(suffixes)
    else:  # pragma: no cover
        suffixes_a = cast(list[str], suffixes)

    return _strip_suffix_or(name, suffixes_a)
