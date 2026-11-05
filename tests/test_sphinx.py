"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test module sphinx_external_toc_strict.tools_strictyaml

Without coverage

.. code-block:: shell

   pytest -s --showlocals -vv "tests/test_sphinx.py"

With coverage

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.tools_strictyaml' -m pytest \
   --showlocals tests/test_sphinx.py && coverage report \
   --data-file=.coverage --include="**/tools_strictyaml.py"

"""

import logging
import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from sphinx import version_info as sphinx_version_info
from sphinx.ext.intersphinx import load_mappings
from sphinx.ext.intersphinx import setup as intersphinx_setup
from sphinx.ext.intersphinx import validate_intersphinx_mapping
from sphinx.testing.util import SphinxTestApp

from sphinx_external_toc_strict.constants import g_app_name
from sphinx_external_toc_strict.tools_strictyaml import create_site_from_toc

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import (
        Any,
        Self,
    )

    from sphinx.testing.fixtures import (
        SharedResult,
        _app_params,
    )

    from .typing_sphinx import MakeApp

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))
TOC_FILES_WARN = list(
    Path(__file__).parent.joinpath("_warning_toc_files").glob("*.yml")
)

CONF_CONTENT = (
    f"""extensions = ["sphinx_external_toc_strict", "myst_parser", "sphinx.ext.intersphinx"]{os.linesep}"""
    """external_toc_path = "_toc.yml\""""
)


class SphinxBuild:
    """Class to help build toctree

    :ivar app: sphinx test app instance
    :vartype app: sphinx.testing.util.SphinxTestApp
    :ivar src: path to a ``_toc.yml``
    :vartype src: pathlib.Path
    """

    def __init__(self, app: "SphinxTestApp", src: "Path") -> None:
        """Class constructor."""
        self.app = app
        self.src = src

    def build(self, assert_pass=True) -> "Self":
        """Build toctree.

        :param assert_pass: Default True. True to assert no warnings occurred
        :type assert_pass: bool
        :returns: Sphinx test app instance
        :rtype: typing.Self
        """
        self.app.build()
        if assert_pass:
            assert self.warnings == "", self.status
        return self

    @property
    def status(self) -> str:
        """Status str from text stream.

        :returns: status message
        :rtype: str
        """
        return self.app._status.getvalue()

    @property
    def warnings(self) -> str:
        """Get Sphinx warning messages.

        :returns: warning messages as a str
        :rtype: str
        """
        return self.app._warning.getvalue()

    @property
    def outdir(self) -> "Path":
        """Output folder of Sphinx logs?

        :returns: Output folder absolute path
        :rtype: pathlib.Path
        """
        return Path(self.app.outdir)


@pytest.fixture()
def sphinx_build_factory(make_app: "MakeApp") -> "Callable[[Path, Any], SphinxBuild]":
    """``pytest.fixture`` which has Sphinx build a toctree.

    :param src_path: Path to ``_toc.yml`` test file
    :type src_path: pathlib.Path
    :param kwargs: Pass on keyword args
    :type kwargs: typing.Any
    :returns: A SphinxBuild instance
    :rtype: tests.test_sphinx.SphinxBuild
    """

    def _func(src_path: "Path", **kwargs: "Any") -> SphinxBuild:
        """Get path and build toctree from ``_toc.yml``."""
        # For compatibility with multiple versions of sphinx, convert pathlib.Path to
        # sphinx.testing.path.path here.
        if sphinx_version_info >= (7, 2):
            app_srcdir = src_path
        else:
            from sphinx.testing.path import path

            app_srcdir = path(os.fspath(src_path))

        app = make_app(srcdir=app_srcdir, **kwargs)
        return SphinxBuild(app, src_path)

    yield _func


@pytest.mark.parametrize(
    "path_toc", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
@pytest.mark.sphinx("html", testroot="skeleton", freshenv=True)
def test_success(
    path_toc: "Path",
    caplog: pytest.LogCaptureFixture,
    sphinx_build_factory: "Callable[[Path, Any], SphinxBuild]",
    # file_regression,
    app_params: "_app_params",
    test_params: "dict[str, Any]",
    shared_result: "SharedResult",
    make_app: "MakeApp",
    inventory_v2: "Callable[[MakeApp, str], Path]",
    augment_intersphinx_mapping: "Callable[[MakeApp, dict[str, Any]], None]",
) -> None:
    """Test successful builds."""
    # python -X dev -m pytest --showlocals --log-level INFO -k "test_success" tests
    # python -m pytest --showlocals tests/test_sphinx.py::test_success[basic_titles]
    # python -m pytest --showlocals tests/test_sphinx.py::test_success[glob_md]
    # sphinx-build -aE -b html . _build/html

    caplog.set_level(logging.INFO, logger="root")
    # prepare
    #    https://github.com/sphinx-doc/sphinx/blob/abb3ead01a76093f0d48068743c6fce7dc6d57c0/sphinx/testing/fixtures.py#L145
    from types import SimpleNamespace

    # Should copy tree --> srcdir
    args, kwargs = app_params
    srcdir = kwargs["srcdir"]

    ns = SimpleNamespace()
    ns.app = SimpleNamespace()
    ns.app.srcdir = kwargs["srcdir"]

    #    inventory --> srcdir
    #    sphinx INVENTORY_V2. Required toc using ``ref`` key (aka RefItem)
    inv_file_name = "objects-test.inv"
    inv_file = inventory_v2(ns.app, inv_file_name)
    assert inv_file.exists() and inv_file.is_file()

    #    generate document files --> srcdir
    site_map = create_site_from_toc(path_toc, root_path=srcdir, overwrite=True)

    app_ = make_app(*args, **kwargs)

    #    config -- master_doc
    master_doc = Path(site_map.root.docname).stem
    app_.config.master_doc = master_doc

    # intersphinx -- setup
    extensions = ["sphinx_external_toc_strict", "myst_parser", "sphinx.ext.intersphinx"]
    app_.config.extensions.extend(extensions)
    intersphinx_setup(app_)

    #    conf.py -- augment
    #        - intersphinx_mapping
    augment_intersphinx_mapping(
        app_,
        {
            "test": ("https://docs.python.org/3", inv_file_name),
        },
    )

    #        - toc file name
    app_.config.external_toc_path = "_toc.yml"

    #        - external_toc_exclude_missing
    if site_map.meta.get("exclude_missing") is True:
        app_.config.external_toc_exclude_missing = True

    #    load the inventory and check if it's done correctly
    validate_intersphinx_mapping(app_, app_.config)
    load_mappings(app_)

    app_.build()

    shutil.rmtree(srcdir, ignore_errors=True)

    # if test_params['shared_result']:
    #     shared_result.store(test_params['shared_result'], app_)

    # optionally check the doctree of a file. regress holds root doc file stem
    """
    if "regress" in site_map.meta:
        doctree = app_.env.get_doctree(site_map.meta["regress"])
        doctree["source"] = site_map.meta["regress"]
        file_regression.check(doctree.pformat(), extension=".xml", encoding="utf8")
    """
    pass


@pytest.mark.parametrize(
    "relpath_toc",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            id="localize-basic",
        ),
    ),
)
def test_gettext(
    relpath_toc: "Path",
    tmp_path: "Path",
    request: pytest.FixtureRequest,
    sphinx_build_factory: "Callable[[Path, Any], SphinxBuild]",
) -> None:
    """Test the gettext builder runs correctly."""
    # python -m pytest -s -vv --showlocals -k test_gettext tests/
    abspath_tests_dir = request.path.parent
    abspath_toc = abspath_tests_dir.joinpath(relpath_toc).resolve()

    src_dir = tmp_path / "srcdir"
    # write document files
    create_site_from_toc(abspath_toc, root_path=src_dir, toc_name=None)
    # write conf.py
    content = (
        f"""extensions = ["{g_app_name}"]{os.linesep}"""
        f"external_toc_path = {abspath_toc.as_posix()!r}"
    )
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir, buildername="gettext")
    builder.build()


@pytest.mark.parametrize(
    "path", TOC_FILES_WARN, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES_WARN]
)
def test_warning(
    path: "Path",
    docs_dir: "Path",
    sphinx_build_factory: "Callable[[Path, Any], SphinxBuild]",
) -> None:
    """Test create_site_from_toc generating warnings."""
    # pytest --showlocals --log-level INFO -k "test_warning" tests
    # write document files
    sitemap = create_site_from_toc(path, root_path=docs_dir)
    # write conf.py
    docs_dir.joinpath("conf.py").write_text(CONF_CONTENT, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(docs_dir)
    builder.build(assert_pass=False)
    expected_warning = sitemap.meta["expected_warning"]
    warnings = [warns for warns in builder.warnings]  # noqa: F841

    assert expected_warning in builder.warnings


@pytest.mark.parametrize(
    "relpath_toc",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            id="abspath-basic",
        ),
    ),
)
def test_absolute_path(
    relpath_toc: "Path",
    tmp_path: "Path",
    request: pytest.FixtureRequest,
    sphinx_build_factory: "Callable[[Path, Any], SphinxBuild]",
) -> None:
    """Test if `external_toc_path` is supplied as an absolute path."""
    abspath_tests_dir = request.path.parent
    abspath_toc = abspath_tests_dir.joinpath(relpath_toc).resolve()

    src_dir = tmp_path / "srcdir"
    # write document files
    create_site_from_toc(abspath_toc, root_path=src_dir, toc_name=None)
    # write conf.py
    content = (
        f"""extensions = ["{g_app_name}"]{os.linesep}"""
        f"external_toc_path = {abspath_toc.as_posix()!r}"
    )
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()


def test_file_extensions(
    tmp_path: "Path",
    sphinx_build_factory: "Callable[[Path, Any], SphinxBuild]",
) -> None:
    """Test for tocs containing docnames with file extensions."""
    src_dir = tmp_path / "srcdir"
    src_dir.mkdir(exist_ok=True)
    # write documents
    src_dir.joinpath("intro.rst").write_text("Head\n====\n", encoding="utf8")
    src_dir.joinpath("markdown.rst").write_text("Head\n====\n", encoding="utf8")
    src_dir.joinpath("notebooks.rst").write_text("Head\n====\n", encoding="utf8")
    # write toc
    toc_path = tmp_path / "toc.yml"
    toc_path.write_text(
        """
format: jb-book
root: intro.rst
chapters:
- file: markdown.rst
  sections:
  - file: notebooks.rst
    """,
        encoding="utf8",
    )
    # write conf.py
    content = f"""
extensions = ["{g_app_name}"]
external_toc_path = {Path(os.path.abspath(toc_path)).as_posix()!r}

"""
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()
