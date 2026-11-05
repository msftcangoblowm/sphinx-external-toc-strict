"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Avoids creating a Sphinx app or docutils.nodes.Element

Without coverage

.. code-block:: shell

   pytest -s --showlocals -vv "tests/test_events_create_warning.py"

"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from docutils.nodes import system_message

from sphinx_external_toc_strict.events import create_warning

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.fixture()
def make_app() -> "Callable[[], MagicMock]":
    """Avoid creating an actual Sphinx app"""

    def fcn_(suppress_warnings: list[str] = []) -> "MagicMock":
        """implementation"""
        app = MagicMock()
        app.config.suppress_warnings = suppress_warnings
        return app

    return fcn_


@pytest.fixture()
def make_doctree() -> "Callable[[], MagicMock]":
    """Avoid creating an actual doctree"""

    def fcn_(msg_node: "system_message") -> "MagicMock":
        """implementation"""
        doctree = MagicMock()
        doctree.reporter.warning.return_value = msg_node
        return doctree

    return fcn_


def test_create_warning_returns_node(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """happy path: warning is created and returned"""
    app = make_app()
    node = system_message("hello [etoc.ref]", level=2)
    doctree = make_doctree(node)

    result = create_warning(app, doctree, "ref", "hello")

    assert result is node
    doctree.reporter.warning.assert_called_once_with("hello [etoc.ref]")


def test_create_warning_suppressed_by_type(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """suppressed: returns None, reporter never called"""
    # suppresses all etoc.*
    app = make_app(suppress_warnings=["etoc"])
    doctree = make_doctree(system_message("", level=2))

    result = create_warning(app, doctree, "ref", "hello")

    assert result is None
    doctree.reporter.warning.assert_not_called()


def test_create_warning_suppressed_by_subtype(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """suppress etoc.ref"""
    app = make_app(suppress_warnings=["etoc.ref"])
    doctree = make_doctree(system_message("", level=2))

    result = create_warning(app, doctree, "ref", "hello")
    assert result is None


def test_create_warning_passes_line(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """line kwarg is forwarded when provided"""
    app = make_app()
    node = system_message("", level=2)
    doctree = make_doctree(node)

    create_warning(app, doctree, "ref", "hello", line=42)

    doctree.reporter.warning.assert_called_once_with("hello [etoc.ref]", line=42)


def test_create_warning_no_line_kwarg(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """line omitted when None"""
    app = make_app()
    node = system_message("", level=2)
    doctree = make_doctree(node)

    # line defaults to None
    create_warning(app, doctree, "ref", "hello")

    doctree.reporter.warning.assert_called_once_with("hello [etoc.ref]")


def test_create_warning_appends_to_node(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """append_to receives the node"""
    app = make_app()
    node = system_message("msg [etoc.toctree]", level=2)
    doctree = make_doctree(node)
    container = MagicMock()

    result = create_warning(app, doctree, "toctree", "msg", append_to=container)

    assert result is node
    container.append.assert_called_once_with(node)


def test_create_warning_custom_wtype(
    make_app: "Callable[[], MagicMock]",
    make_doctree: "Callable[[], MagicMock]",
) -> None:
    """custom wtype appears in the formatted message"""
    app = make_app()
    node = system_message("", level=2)
    doctree = make_doctree(node)

    create_warning(app, doctree, "glob", "bad glob", wtype="myext")

    doctree.reporter.warning.assert_called_once_with("bad glob [myext.glob]")
