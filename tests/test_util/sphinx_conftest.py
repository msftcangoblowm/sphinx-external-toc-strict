"""Taken some of Sphinx own ``conftest.py``. This is later imported."""

from __future__ import annotations

import gettext
import os
import sys
from types import SimpleNamespace
from typing import TYPE_CHECKING

import docutils
import pytest
import sphinx
import sphinx.locale
import sphinx.pycode
from sphinx.testing.util import _clean_up_global_state

if TYPE_CHECKING:
    from collections.abc import Iterator


def _init_console(
    locale_dir: str | None = sphinx.locale._LOCALE_DIR,
    catalog: str = "sphinx",
) -> tuple[gettext.NullTranslations, bool]:
    """Monkeypatch ``init_console`` to skip its action.

    Some tests rely on warning messages in English. We don't want
    CLI tests to bleed over those tests and make their warnings
    translated.
    """
    return gettext.NullTranslations(), False


sphinx.locale.init_console = _init_console

# https://github.com/sphinx-doc/sphinx/blob/master/sphinx/testing/fixtures.py
pytest_plugins = ["sphinx.testing.fixtures"]

# Exclude 'roots' dirs for pytest test collector
collect_ignore = ["roots"]

os.environ["SPHINX_AUTODOC_RELOAD_MODULES"] = "1"


def pytest_report_header(config: pytest.Config) -> str:
    """Display sphinx and docutils versions and tmp folder.

    :param config: pytest config instance
    :type config: pytest.Config
    :returns: header to print
    :rtype: str
    """
    header = f"libraries: Sphinx-{sphinx.__display_version__}, docutils-{docutils.__version__}"
    if hasattr(config, "_tmp_path_factory"):
        header += f"\nbase tmp_path: {config._tmp_path_factory.getbasetemp()}"
    return header


@pytest.fixture(autouse=True)
def _cleanup_docutils() -> Iterator[None]:
    """After test, restore changes to ``sys.path``

    :returns: Iterator containing one entry, None.
    :rtype: collections.abc.Iterator[None]
    """
    saved_path = sys.path
    yield  # run the test
    sys.path[:] = saved_path

    _clean_up_global_state()


@pytest.fixture
def _http_teapot(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Short-circuit HTTP requests.

    Windows takes too long to fail on connections, hence this fixture.
    """
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/418
    response = SimpleNamespace(status_code=418)

    def _request(*args, **kwargs):
        """Echo a request back as the response."""
        return response

    with monkeypatch.context() as m:
        m.setattr("sphinx.util.requests._Session.request", _request)
        yield
