"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Unittest for entrypoint, cli

.. code-block:: shell

   pytest --showlocals --log-level INFO tests/test_cli.py
   pytest --showlocals --cov="drain_swamp" --cov-report=term-missing tests/test_cli.py

"""

from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

import pytest
from click.testing import CliRunner

from sphinx_external_toc_strict.cli import (
    create_site,
    create_toc,
    main,
    migrate_toc,
    parse_toc,
)
from sphinx_external_toc_strict.constants import __version_app

if TYPE_CHECKING:
    from click.testing import Result


@pytest.fixture()
def invoke_cli():
    """Run CLI and do standard checks

    :param command: cli function being tested
    :type command: collections.abc.Callable[[typing.Any], typing.Any]
    :param args: args to cli function being tested
    :type args: collections.abc.Sequence[str]
    :param assert_exit: Default True. If True AssertionError when error encountered
    ]type assert_exit: bool | None

    .. seealso::

       `click.testing.Result <https://click.palletsprojects.com/en/8.1.x/api/#click.testing.Result>`_

    """

    def _func(command, args: list[str], assert_exit: bool | None = True) -> Result:
        runner = CliRunner()
        result = runner.invoke(command, args)
        is_assert_exit = (
            assert_exit is not None
            and isinstance(assert_exit, bool)
            and assert_exit is True
        )
        if is_assert_exit and result.exit_code != 0:
            exc_type, exc, tb = result.exc_info
            lst_tb = traceback.format_tb(tb)
            str_tb = "".join(lst_tb)
            err_msg = f"{exc_type}: {exc.args[0]}\n" f"{str_tb}\n"
            assert result.exit_code == 0, err_msg
        return result

    yield _func


@pytest.fixture()
def is_ok():
    """Check non-empty str

    :param val: object to check
    :type val: typing.Any
    :returns: True if a non-empty str otherwise False
    :rtype: bool
    """

    def _func(val: Any) -> bool:
        return val is not None and isinstance(val, str) and len(val.strip()) != 0

    yield _func


def test_main(invoke_cli, is_ok):
    """Invoke sphinx-toc-strict --version and --help"""
    # pytest --showlocals --log-level INFO -k "test_main" tests
    result = invoke_cli(main, ["--version"])
    assert __version_app in result.output

    result = invoke_cli(main, ["--help"])

    assert is_ok(result.output) is True


testdata_parse_toc = (
    (
        Path(__file__).parent.joinpath("_toc_files", "basic.yml"),
        "intro",
    ),
)
ids_parse_toc = ("parse basic toc with root intro rather than index",)


@pytest.mark.parametrize(
    "path_toc, toc_root_file_stem",
    testdata_parse_toc,
    ids=ids_parse_toc,
)
def test_parse_toc(path_toc, toc_root_file_stem, invoke_cli, is_ok):
    """parses yaml, creates a sitemap, dumps the site map to a str"""
    # pytest --showlocals --log-level INFO -k "test_parse_toc" tests
    toc_path = str(path_toc)
    result = invoke_cli(parse_toc, [toc_path])

    assert is_ok(result.output) is True
    assert toc_root_file_stem in result.output


def test_create_toc(tmp_path, invoke_cli, file_regression):
    """create project files

    Support for hidden files was dropped. ``.hidden_file.rst``, for
    example, is sorta equivalent to ``.tar.gz``. Both lack a file stem
    """
    # pytest --showlocals --log-level INFO -k "test_create_toc" tests
    dir_tmp_path = str(tmp_path)
    # prepare
    hidden_file_0 = ".hidden_file.rst"
    hidden_file_1 = ".hidden_folder/index.rst"
    files = [
        "index.rst",
        "1_a_title.rst",
        "11_another_title.rst",
        hidden_file_0,
        hidden_file_1,
        "1_a_subfolder/index.rst",
        "2_another_subfolder/index.rst",
        "2_another_subfolder/other.rst",
        "3_subfolder/1_no_index.rst",
        "3_subfolder/2_no_index.rst",
        "14_subfolder/index.rst",
        "14_subfolder/subsubfolder/index.rst",
        "14_subfolder/subsubfolder/other.rst",
    ]
    for posix in files:
        path = tmp_path.joinpath(*posix.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()

    # act
    """to toc_yml str appends title first letter capitalized.

    Without ``-t`` would take the titles from within these files. Which
    are empty, so that wouldn't go well
    """
    result = invoke_cli(create_toc, [dir_tmp_path, "--guess-titles"])

    str_toc_yml = result.output.rstrip()

    # verify
    #    Prove hidden files not in sitemap
    assert hidden_file_0 not in str_toc_yml
    assert hidden_file_1 not in str_toc_yml

    file_regression.check(str_toc_yml)


testdata_create_site_cli = (
    (
        Path(__file__).parent.joinpath("_toc_files", "exclude_missing.yml"),
        "intro",
        "rst",
    ),
)
ids_create_site_cli = ("intro instead of index",)


@pytest.mark.parametrize(
    "path_toc_yml, root, extension",
    testdata_create_site_cli,
    ids=ids_create_site_cli,
)
def test_create_site_cli_existing_files(
    path_toc_yml, root, extension, tmp_path, invoke_cli
):
    """From toc yml, creates site in tmp folder. In tmp folder, confirm files created"""
    # pytest --showlocals --log-level INFO -k "test_create_site_cli_existing_files" tests
    toc_file_path = os.path.abspath(path_toc_yml)

    #    already existing file
    path_f = tmp_path.joinpath(f"doc1.{extension}")
    path_f.touch()

    cmd = [
        toc_file_path,
        "--path",
        os.path.abspath(tmp_path),
        "--extension",
        extension,
    ]

    # act
    #    file aleady exists and overwrite not allowed
    result = invoke_cli(create_site, cmd)
    out = result.output.rstrip()
    # verify
    assert "SUCCESS!" not in out


@pytest.mark.parametrize(
    "path_toc_yml, root, extension",
    testdata_create_site_cli,
    ids=ids_create_site_cli,
)
def test_create_site_cli_normal(path_toc_yml, root, extension, tmp_path, invoke_cli):
    # pytest --showlocals --log-level INFO -k "test_create_site_cli_normal" tests
    # prepare
    #    doc1.rst file is created. When shown the toc would exclude doc1.rst
    expected_files = (
        "_toc.yml",
        f"{root}.rst",
        f"doc1.{extension}",
        f"doc2.{extension}",
        f"subfolder/other1.{extension}",
    )
    toc_file_path = os.path.abspath(path_toc_yml)

    cmd = [
        toc_file_path,
        "--path",
        os.path.abspath(tmp_path),
        "--extension",
        extension,
    ]

    # act
    result = invoke_cli(create_site, cmd)
    out = result.output.rstrip()
    # verify
    assert "SUCCESS!" in out

    #    Walk tmp_path folder tree contents
    lst_path_files = list(tmp_path.glob("**/*"))

    #    Convert absolute Path -> relative Path --> str
    #    build list[str]
    actual_paths = []
    for p_file in lst_path_files:
        p_relative_path = p_file.relative_to(tmp_path)
        actual_paths.append(str(p_relative_path))

    #    Confirm lists have same contents: expected_files == files
    for str_path_expected in expected_files:
        assert str_path_expected in actual_paths


testdata_migrate_toc = (
    (
        Path(__file__).parent.joinpath("_jb_migrate_toc_files", "simple_list.yml"),
        "index",
    ),
)
ids_migrate_toc = ("",)


@pytest.mark.parametrize(
    "path_toc_yml, root",
    testdata_migrate_toc,
    ids=ids_migrate_toc,
)
def test_migrate_toc(path_toc_yml, root, tmp_path, invoke_cli):
    """Migrate toc. Output to stdout or saves to file. Compare both"""
    # pytest --showlocals --log-level INFO -k "test_migrate_toc" tests
    toc_yml_path = str(path_toc_yml)

    # act
    result = invoke_cli(migrate_toc, [toc_yml_path])
    toc_yml_0 = result.output  # two newlines
    # verify
    assert f"root: {root}" in toc_yml_0

    # act
    path_site = tmp_path.joinpath("site")
    path_site.mkdir(parents=True, exist_ok=True)
    path_out = path_site.joinpath("_toc.yml")

    #    Saves to output file, site/_toc.yml
    result = invoke_cli(migrate_toc, [toc_yml_path, "--output", str(path_out)])
    out = result.output.rstrip()

    # verify
    assert out == f"Written to: {str(path_out)}"
    assert path_out.exists() is True
    toc_yml_1 = path_out.read_text()  # one newline
    # rstrip both cuz left side has two newlines. Right has one newline
    assert toc_yml_0.rstrip() == toc_yml_1.rstrip()
