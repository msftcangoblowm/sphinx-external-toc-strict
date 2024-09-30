"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

sphinx-external-toc-strict pytest conftest.py
"""

import re
from pathlib import Path
from typing import Any

import pytest

from tests.test_util.intersphinx_data import INVENTORY_V2
from tests.test_util.sphinx_conftest import pytest_plugins  # noqa: F401


class FileRegression:
    """Compare previous runs files.

    :ivar file_regression: file to compare against?
    :vartype file_regression: typing.Self

    .. todo:: when Sphinx<=6 is dropped

       Remove line starting with re.escape(" translation_progress=

    .. todo:: when Sphinx<7.2 is dropped

       Remove line starting with original_url=

    """

    ignores = (
        # Remove when support for Sphinx<=6 is dropped,
        re.escape(" translation_progress=\"{'total': 0, 'translated': 0}\""),
        # Remove when support for Sphinx<7.2 is dropped,
        r"original_uri=\"[^\"]*\"\s",
    )

    def __init__(self, file_regression: "FileRegression") -> None:
        """FileRegression constructor."""
        self.file_regression = file_regression

    def check(self, data: str, **kwargs: dict[str, Any]) -> str:
        """Check previous run against current run file.

        :param data: file contents
        :type data: str
        :param kwargs: keyword options are passed thru
        :type kwargs: dict[str, typing.Any]
        :returns: diff of file contents?
        :rtype: str
        """
        return self.file_regression.check(self._strip_ignores(data), **kwargs)

    def _strip_ignores(self, data: str) -> str:
        """Helper to strip ignores from data.

        :param data: file contents w/o ignore statements
        :type data: str
        :returns: sanitized file contents
        :rtype: str
        """
        cls = type(self)
        for ig in cls.ignores:
            data = re.sub(ig, "", data)
        return data


@pytest.fixture()
def file_regression(file_regression: "FileRegression") -> FileRegression:
    """Comparison files will need updating.

    .. seealso::

       Awaiting resolution of `pytest-regressions#32 <https://github.com/ESSS/pytest-regressions/issues/32>`_

    """
    return FileRegression(file_regression)


@pytest.fixture(scope="session")
def rootdir() -> Path:
    """``tests/roots`` contains subfolders with naming
    pattern ``/test-[site folder tree]``. These contain a Sphinx ``docs/``
    folder tree.

    :returns: tests roots base folder. Which contains lots of subfolders
    :rtype: pathlib.Path
    """
    return Path(__file__).parent.resolve() / "roots"


@pytest.fixture(scope="function", autouse=False)
def docs_dir(tmp_path):
    """Acts as a Sphinx ``docs/`` folder. Not within a package base
    folder

    :returns: ``docs`` folder
    :rtype: pathlib.Path
    """
    path_dir = tmp_path / "docs"
    path_dir.mkdir(exist_ok=True)
    return path_dir


@pytest.fixture()
def inventory_v2():
    """Writes sphinx standard inventory_v2 file.
    Destination is Sphinx app instance srcdir.

    This inventory contains only one entry we're interested in.
    :param inv_file_name: Inventory file name. e.g. ``objects-test.inv``
    :type inv_file_name: str
    :returns: inventory file destination path
    :rtype: pathlib.Path
    """

    def _func(app, inv_file_name):
        """Write the inventory file to destination site."""
        inv_file = app.srcdir / inv_file_name
        inv_file.write_bytes(INVENTORY_V2)

        return inv_file

    return _func


@pytest.fixture()
def augment_intersphinx_mapping():
    """Fixture to adjust the ``app.config`` rather than editting a
    Sphinx config (python) file.

    :param mapping: intersphinx_mapping dict
    :type mapping: dict[str, typing.Any]
    """

    def _func(app, mapping):
        """Make small alterations to Sphinx ``app.config``.
        The ``conf.py``, shouldn't be editted. Instead adjusts
        ``app.config``. Changes are not persistant. ``conf.py``
        is unchanged.
        """
        # copy *mapping* so that normalization does not alter it
        app.config.intersphinx_mapping = mapping.copy()
        app.config.intersphinx_cache_limit = 0
        app.config.intersphinx_disabled_reftypes = []
        return None

    return _func
