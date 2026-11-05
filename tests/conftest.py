"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

sphinx-external-toc-strict pytest conftest.py
"""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.fr import FileRegression
from tests.test_util.intersphinx_data import INVENTORY_V2

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from tests.typing_sphinx import MakeApp

# from tests.test_util.sphinx_conftest import pytest_plugins  # noqa: F401
pytest_plugins = ("sphinx.testing.fixtures",)


@pytest.fixture()
def file_regression(file_regression: "FileRegression") -> FileRegression:
    """Comparison files will need updating.

    .. seealso::

       Awaiting resolution of `pytest-regressions#32 <https://github.com/ESSS/pytest-regressions/issues/32>`_

    """
    return FileRegression(file_regression)


@pytest.fixture(scope="session")
def rootdir() -> "Path":
    """``tests/roots`` contains subfolders with naming
    pattern ``/test-[site folder tree]``. These contain a Sphinx ``docs/``
    folder tree.

    :returns: tests roots base folder. Which contains lots of subfolders
    :rtype: pathlib.Path
    """
    return Path(__file__).parent.resolve() / "roots"


@pytest.fixture(scope="function", autouse=False)
def docs_dir(tmp_path: "Path") -> "Path":
    """Acts as a Sphinx ``docs/`` folder. Not within a package base
    folder

    :returns: ``docs`` folder
    :rtype: pathlib.Path
    """
    path_dir = tmp_path / "docs"
    path_dir.mkdir(exist_ok=True)
    return path_dir


@pytest.fixture()
def inventory_v2() -> "Callable[[MakeApp, str], Path]":
    """Writes sphinx standard inventory_v2 file.
    Destination is Sphinx app instance srcdir.

    This inventory contains only one entry we're interested in.
    :param inv_file_name: Inventory file name. e.g. ``objects-test.inv``
    :type inv_file_name: str
    :returns: inventory file destination path
    :rtype: pathlib.Path
    """

    def _func(app: "MakeApp", inv_file_name: str) -> "Path":
        """Write the inventory file to destination site."""
        inv_file = app.srcdir / inv_file_name
        inv_file.write_bytes(INVENTORY_V2)

        return inv_file

    return _func


@pytest.fixture()
def augment_intersphinx_mapping() -> "Callable[[MakeApp, dict[str, Any]], None]":
    """Fixture to adjust the ``app.config`` rather than editing a
    Sphinx config (python) file.

    :param mapping: intersphinx_mapping dict
    :type mapping: dict[str, typing.Any]
    """

    def _func(app: "MakeApp", mapping: "dict[str, Any]") -> None:
        """Make small alterations to Sphinx ``app.config``.
        The ``conf.py``, shouldn't be edited. Instead adjusts
        ``app.config``. Changes are not persistent. ``conf.py``
        is unchanged.
        """
        # copy *mapping* so that normalization does not alter it
        app.config.intersphinx_mapping = mapping.copy()
        app.config.intersphinx_cache_limit = 0
        app.config.intersphinx_disabled_reftypes = []
        return None

    return _func
