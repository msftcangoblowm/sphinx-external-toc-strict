"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Unittest for entrypoint, cli

.. code-block:: shell

   pytest --showlocals --log-level INFO tests/test_tools.py
   pytest --showlocals --cov="drain_swamp" --cov-report=term-missing tests/test_tools.py

"""

import sys
from pathlib import Path

import pytest

from sphinx_external_toc_strict.parsing_strictyaml import parse_toc_data
from sphinx_external_toc_strict.tools_strictyaml import (
    _assess_folder,
    _default_affinity,
    create_site_from_toc,
    create_site_map_from_path,
    migrate_jupyter_book,
    site_map_guess_titles,
)

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))
JB_TOC_FILES = list(
    Path(__file__).parent.joinpath("_jb_migrate_toc_files").glob("*.yml")
)


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, tmp_path: Path, data_regression):
    site_path = tmp_path.joinpath("site")
    create_site_from_toc(path, root_path=site_path)
    file_list = [p.relative_to(site_path).as_posix() for p in site_path.glob("**/*")]
    data_regression.check(sorted(file_list))


TOC_PICK_ONE = list(
    (Path(__file__).parent.joinpath("_toc_files", "glob.yml"),),
)


@pytest.mark.parametrize(
    "path", TOC_PICK_ONE, ids=[path.name.rsplit(".", 1)[0] for path in TOC_PICK_ONE]
)
def test_file_to_sitemap_file_already_exists(path: Path, tmp_path: Path):
    """Monkey throws file into cogworks. So file already exists"""
    site_path = tmp_path.joinpath("site")
    site_path.mkdir(parents=True, exist_ok=True)
    site_path.joinpath("doc1.rst").touch()

    with pytest.raises(IOError):
        create_site_from_toc(path, root_path=site_path)


def test_create_site_map_from_path(tmp_path: Path, data_regression):
    # pytest --showlocals --log-level INFO -k "test_create_site_map_from_path" tests
    # prepare
    #    will create root file (index.rst) later
    files = [
        "index.rst",
        "1_other.rst",
        "11_other.rst",
        ".hidden_file.rst",
        ".hidden_folder/index.rst",
        "subfolder1/index.rst",
        "subfolder2/index.rst",
        "subfolder2/other.rst",
        "subfolder3/no_index1.rst",
        "subfolder3/no_index2.rst",
        "subfolder14/index.rst",
        "subfolder14/subsubfolder/index.rst",
        "subfolder14/subsubfolder/other.rst",
    ]

    for posix in files:
        path_f = tmp_path.joinpath(*posix.split("/"))
        path_f.parent.mkdir(parents=True, exist_ok=True)
        path_f.touch()

    # act
    #    remove root file
    path_root_file = tmp_path.joinpath("index.rst")
    path_root_file.unlink()

    with pytest.raises(FileNotFoundError):
        create_site_map_from_path(tmp_path)

    # prepare
    #    add root file
    path_root_file.touch()

    # act
    site_map = create_site_map_from_path(tmp_path)

    #    from doc file names' don't guess title
    invalids = (
        None,
        0.1234,
    )
    index = "index"
    for invalid in invalids:
        site_map_guess_titles(site_map, index, is_guess=invalid)

    # verify the file is unchanged against previous run
    data_regression.check(site_map.as_json())
    # data = create_toc_dict(site_map)
    # data_regression.check(data)


@pytest.mark.parametrize(
    "path", JB_TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in JB_TOC_FILES]
)
def test_migrate_jb(path, data_regression):
    toc = migrate_jupyter_book(Path(path))
    data_regression.check(toc)
    # check it is a valid toc
    parse_toc_data(toc)


@pytest.mark.skipif(sys.platform != "linux", reason="path is to a known linux file")
def test_assess_folder_expecting_folder():
    """Expecting a folder, got a file"""
    folder = Path("/etc/shells")
    suffixes = (".sh",)
    default_index = "index"
    ignore_matches = (".*",)
    with pytest.raises(NotADirectoryError):
        _assess_folder(folder, suffixes, default_index, ignore_matches)


testdata_default_affinity = (
    (("intro.rst", "doc1.md", "doc2.md", "doc3.md"), ".txt", ".md"),
    (("intro.rst", "doc1.md", "doc2.rst", "doc3.rst"), ".txt", ".rst"),
    (("intro.rst", "doc1.md", "doc3.rst"), ".txt", ".txt"),
)
ids_default_affinity = (
    "majority markdown files",
    "majority restructuredtext files",
    "equal so inconclusive; go with default",
)


@pytest.mark.parametrize(
    "additional_files, default_ext, expected",
    testdata_default_affinity,
    ids=ids_default_affinity,
)
def test_default_affinity(additional_files, default_ext, expected):
    actual_affinity = _default_affinity(additional_files, default_ext)
    assert actual_affinity == expected
