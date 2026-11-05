"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Without coverage

.. code-block:: shell

   pytest -s --showlocals -vv "tests/test_events_parse_toc_to_env.py"

"""

import shutil
from contextlib import nullcontext as does_not_raise
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import (
    MagicMock,
    patch,
)

import pytest
from sphinx.errors import ExtensionError

from sphinx_external_toc_strict.constants import g_app_name
from sphinx_external_toc_strict.events import (
    ensure_index_file,
    parse_toc_to_env,
)
from sphinx_external_toc_strict.filename_suffix import stem_natural

# from logging_strict.tech_niques.context_locals import get_locals_dynamic

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Sequence,
    )
    from typing import Any

    from tests.typing_only import DOES_NOT_OR_DOES


class FakeConfig(dict):
    """Supports config[key] and config.attr = value."""

    def __setattr__(self, name: str, value: "Any") -> None:
        """Set dict key/value pair

        :type name: str
        :type value: typing.Any
        """
        self[name] = value

    def __getattr__(self, name: str) -> "Any":
        """Get dict value by name

        :type name: str
        """
        try:
            ret = self[name]
        except KeyError:
            raise AttributeError(name)
        return ret


@pytest.fixture
def app() -> "Callable[[Path], MagicMock]":
    """Get working Sphinx app Mock"""

    def fcn_(abspath_dir: "Path") -> MagicMock:
        """Avoid hardcoding app.srcdir"""
        mock = MagicMock()
        mock.srcdir = str(abspath_dir)  # must be a real path for Path()
        # relative; resolved against srcdir
        mock.config = FakeConfig()
        return mock

    return fcn_


@pytest.fixture
def config() -> FakeConfig:
    """dict wrapper"""
    cfg = FakeConfig(
        master_doc="intro",
        source_suffix={".rst": "restructuredtext"},
        exclude_patterns=[],
        external_toc_exclude_missing=False,
    )
    return cfg


@pytest.mark.parametrize(
    "relpath_toc_yaml_f",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            id="ToC-basic",
        ),
    ),
)
def test_parse_toc_to_env_success(
    relpath_toc_yaml_f: "Path",
    tmp_path: "Path",
    request: pytest.FixtureRequest,
    app: MagicMock,
    config: FakeConfig,
) -> None:
    """verify master_doc after reading config"""
    # python -m pytest -s -vv --showlocals -k test_parse_toc_to_env_success tests/
    # prepare -- source YAML ToC
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml_f = abspath_tests_dir.joinpath(relpath_toc_yaml_f)
    app.srcdir = abspath_toc_yaml_f.parent
    toc_yaml_f = abspath_toc_yaml_f.name

    # override default app.config
    config["external_toc_path"] = toc_yaml_f
    app.config = config

    parse_toc_to_env(app, config)
    # master_doc updated (was already "index" so no change, but the assignment happened)

    assert app.config["master_doc"] == "intro"


@pytest.mark.parametrize(
    "toc_yaml_file_name, expectation",
    (
        pytest.param(
            "nope.yml",
            pytest.raises(ExtensionError, match="does not exist"),
            id="nonexistent-file",
        ),
    ),
)
def test_parse_toc_to_env_missing_file(
    toc_yaml_file_name: str,
    expectation: "DOES_NOT_OR_DOES",
    tmp_path: "Path",
    app: MagicMock,
    config: FakeConfig,
) -> None:
    """missing ToC file"""
    # override default app.config
    config["external_toc_path"] = toc_yaml_file_name
    app.config = config
    app.srcdir = str(tmp_path)

    with expectation:
        parse_toc_to_env(app, config)


def test_parse_toc_to_env_is_directory(
    app: MagicMock,
    config: FakeConfig,
    tmp_path: "Path",
) -> None:
    """Test 'is not a file' branch"""
    # python -m pytest -s -vv --showlocals -k test_parse_toc_to_env_is_directory tests/
    # override default app.config
    config["external_toc_path"] = "adir"
    app.config = config
    abspath_dir_dest = tmp_path / "adir"
    app.srcdir = str(abspath_dir_dest)

    (tmp_path / "adir").mkdir(parents=True, exist_ok=True)
    regex_missing_folder = r"\[etoc\] `external_toc_path` does not exist: .*"
    with pytest.raises(ExtensionError, match=regex_missing_folder):
        parse_toc_to_env(app, config)


@pytest.mark.parametrize(
    "relpath_toc_yaml_f",
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            id="ToC-basic",
        ),
    ),
)
def test_parse_toc_to_env_changes_master_doc(
    relpath_toc_yaml_f: "Path",
    app: MagicMock,
    config: FakeConfig,
    tmp_path: "Path",
    request: pytest.FixtureRequest,
) -> None:
    """Change master_doc"""
    # Make the YAML root docname differ from current master_doc
    # python -m pytest -s -vv --showlocals -k test_parse_toc_to_env_changes_master_doc tests/
    #
    # prepare -- source YAML ToC
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml_f = abspath_tests_dir.joinpath(relpath_toc_yaml_f)
    app.srcdir = abspath_toc_yaml_f.parent
    toc_yaml_f = abspath_toc_yaml_f.name

    config["external_toc_path"] = toc_yaml_f
    app.config = config

    abspath_f_src = Path(app.srcdir) / config["external_toc_path"]
    src_contents = abspath_f_src.read_text()
    src_contents = src_contents.replace("root: intro", "root: myroot")
    abspath_f_dest = tmp_path / config["external_toc_path"]
    abspath_f_dest.write_text(src_contents)
    app.srcdir = tmp_path

    config["master_doc"] = "intro"  # will be changed to "myroot"
    parse_toc_to_env(app, config)
    assert config["master_doc"] == "myroot"


@pytest.mark.parametrize(
    (
        "relpath_toc_yaml_f, files, extras, source_suffix, "
        "external_toc_exclude_missing, expectation"
    ),
    (
        pytest.param(
            Path("_toc_files").joinpath("basic.yml"),
            ("extra.rst", "doc1.rst", "doc2.rst", "doc3.rst", "subfolder/doc4.rst"),
            ("extra.rst",),
            (".md", ".rst"),
            True,
            does_not_raise(),
            id="ToC-basic",
        ),
        pytest.param(
            Path("_bad_toc_files").joinpath("doc_validation_fail.yml"),
            ("extra.rst", "doc1.rst"),
            ("extra.rst",),
            (".md", ".rst"),
            True,
            pytest.raises(ExtensionError),
            id="ToC-validation-fail",
        ),
    ),
)
def test_parse_toc_to_env_exclude_missing(
    relpath_toc_yaml_f: "Path",
    files: "Sequence[str]",
    extras: "Sequence[str]",
    source_suffix: "Sequence[str]",
    external_toc_exclude_missing: bool,
    expectation: "DOES_NOT_OR_DOES",
    app: MagicMock,
    config: FakeConfig,
    tmp_path: "Path",
    request: pytest.FixtureRequest,
) -> None:
    """extra .rst file not in ToC"""
    # python -m pytest -s -vv --showlocals -k test_parse_toc_to_env_exclude_missing tests/
    #
    # prepare -- source YAML ToC
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml_f = abspath_tests_dir.joinpath(relpath_toc_yaml_f)
    app.srcdir = abspath_toc_yaml_f.parent
    toc_yaml_f = abspath_toc_yaml_f.name

    # prepare -- config would normally originate from pyproject.toml
    config["external_toc_path"] = toc_yaml_f
    config["source_suffix"] = source_suffix
    config["external_toc_exclude_missing"] = external_toc_exclude_missing
    app.config = config

    # prepare -- copy to tmp folder
    abspath_f_src = Path(app.srcdir) / toc_yaml_f
    shutil.copy2(abspath_f_src.as_posix(), tmp_path.as_posix())

    # prepare -- create rst files which appear in ToC
    #    Add an extra .rst file; not in the ToC
    for f in files:
        abspath_f = tmp_path.joinpath(f)
        abspath_f.parent.mkdir(parents=True, exist_ok=True)
        abspath_f.write_text("hello")

    # prepare -- effort spent preparing tmp folder. Be ashame not to use it
    app.srcdir = str(tmp_path)

    # act
    with expectation:
        parse_toc_to_env(app, config)
    if isinstance(expectation, does_not_raise):
        # verify -- excluded documents
        for str_extra in extras:
            assert str_extra in config["exclude_patterns"]


@pytest.mark.parametrize(
    (
        "builder_name, exception, relpath_toc_yaml_f, files, source_suffix, "
        "external_toc_exclude_missing"
    ),
    (
        pytest.param(
            "dirhtml",
            TypeError("a message"),
            Path("_toc_files").joinpath("basic.yml"),
            ("extra.rst", "doc1.rst", "doc2.rst", "doc3.rst", "subfolder/doc4.rst"),
            (".md", ".rst"),
            True,
            id="do-nothing",
        ),
        pytest.param(
            "dirhtml",
            None,
            Path("_toc_files").joinpath("basic.yml"),
            ("extra.rst", "doc1.rst", "doc2.rst", "doc3.rst", "subfolder/doc4.rst"),
            (".md", ".rst"),
            True,
            id="ToC-basic",
        ),
    ),
)
def test_events_ensure_index_file(
    builder_name: str,
    exception: Exception | None,
    relpath_toc_yaml_f: "Path",
    files: "Sequence[str]",
    source_suffix: "Sequence[str]",
    external_toc_exclude_missing: bool,
    tmp_path: "Path",
    request: pytest.FixtureRequest,
    app: MagicMock,
    config: FakeConfig,
) -> None:
    """use fake app"""
    # python -m pytest -s -vv --showlocals -k test_events_ensure_index_file tests/
    # python -m pytest -s -vv --showlocals "tests/test_events_parse_toc_to_env.py::test_events_ensure_index_file[ToC-basic]"
    #
    # prepare -- source YAML ToC
    abspath_tests_dir = request.path.parent
    abspath_toc_yaml_f = abspath_tests_dir.joinpath(relpath_toc_yaml_f)
    app.srcdir = abspath_toc_yaml_f.parent
    toc_yaml_f = abspath_toc_yaml_f.name

    # prepare -- config would normally originate from pyproject.toml
    config["external_toc_path"] = toc_yaml_f
    config["source_suffix"] = source_suffix
    config["external_toc_exclude_missing"] = external_toc_exclude_missing
    app.config = config

    # prepare -- copy to tmp folder
    abspath_f_src = Path(app.srcdir) / toc_yaml_f
    shutil.copy2(abspath_f_src.as_posix(), tmp_path.as_posix())

    # prepare -- create rst files which appear in ToC
    #    Add an extra .rst file; not in the ToC
    for f in files:
        abspath_f = tmp_path.joinpath(f)
        abspath_f.parent.mkdir(parents=True, exist_ok=True)
        abspath_f.write_text("hello")

    # prepare -- effort spent preparing tmp folder. Be ashame not to use it
    app.srcdir = str(tmp_path)
    app.outdir = str(tmp_path)

    # additional settings
    if builder_name == "dirhtml":
        root_name = stem_natural(app.config.master_doc)
        redirect_url = f"{root_name}/index.html"
        tmp_path.joinpath(redirect_url).parent.mkdir(parents=True, exist_ok=True)
        tmp_path.joinpath(redirect_url).write_text("hello")

    #    default setting
    # app.config.master_doc = "intro"
    app.builder = MagicMock()
    app.builder.format = "html"
    app.builder.name = builder_name
    assert app.builder.name == builder_name
    assert app.builder.format == "html"

    """
    args = (app, exception)
    kwargs = {}
    t_ret = get_locals_dynamic(ensure_index_file, *args, **kwargs)
    """

    with patch(f"{g_app_name}.events.logger.info", lambda x: None):
        ensure_index_file(app, exception)
