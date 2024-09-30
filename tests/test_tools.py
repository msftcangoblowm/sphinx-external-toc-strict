"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Unittest for parsing and tools

Unit test -- Module

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.tools_strictyaml' -m pytest \
   --showlocals tests/test_tools.py && coverage report \
   --data-file=.coverage --include="**/tools_strictyaml.py"

"""

import copy
import sys
from contextlib import nullcontext as does_not_raise
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
    """Test create_site_from_toc."""
    site_path = tmp_path.joinpath("site")
    create_site_from_toc(path, root_path=site_path)
    file_list = [p.relative_to(site_path).as_posix() for p in site_path.glob("**/*")]
    data_regression.check(sorted(file_list))


testdata_file_to_sitemap_file_already_exists = (
    (
        Path(__file__).parent.joinpath("_toc_files", "glob.yml"),
        ("doc1.rst",),
        pytest.raises(OSError),
    ),
    (
        Path(__file__).parent.joinpath("_toc_files", "glob_md_extras.yml"),
        ("conf.py",),
        pytest.raises(OSError),
    ),
)
ids_file_to_sitemap_file_already_exists = (
    "Complains file already exists",
    "Complains non-document file already exists",
)


@pytest.mark.parametrize(
    "path_toc, touch_these_files, expectation",
    testdata_file_to_sitemap_file_already_exists,
    ids=ids_file_to_sitemap_file_already_exists,
)
def test_file_to_sitemap_file_already_exists(
    path_toc,
    touch_these_files,
    expectation,
    tmp_path,
    docs_dir,
):
    """Monkey throws file into cogworks. So file already exists."""
    # pytest --showlocals --log-level INFO -k "test_file_to_sitemap_file_already_exists" tests
    # prepare
    for file_name in touch_these_files:
        docs_dir.joinpath(file_name).touch()

    # act and verify
    with expectation:
        create_site_from_toc(path_toc, root_path=docs_dir)


testdata_site_map_files = [
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
testdata_create_site_map_from_path = (
    (
        copy.deepcopy(testdata_site_map_files),
        10,
        3,
    ),
)
ids_create_site_map_from_path = ("files with two unsupported hidden",)


@pytest.mark.parametrize(
    "files, docs_valid_count, index_and_hidden_count",
    testdata_create_site_map_from_path,
    ids=ids_create_site_map_from_path,
)
def test_create_site_map_from_path(
    files,
    docs_valid_count,
    index_and_hidden_count,
    tmp_path,
    data_regression,
):
    """Test create_site_map_from_path."""
    # pytest --showlocals --log-level INFO -k "test_create_site_map_from_path" tests
    # prepare
    #    will create root file (index.rst) later

    # prepare
    #    folders and empty files
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
    #    restore index.rst (root file)
    path_root_file.touch()

    # act
    site_map = create_site_map_from_path(tmp_path)

    # verify doc count
    docs = site_map._docs.values()
    files_expected_count = len(files)
    files_actual_count = 0
    files_actual_all = []
    for doc in docs:
        files_actual = doc.child_files()
        files_actual_count += len(files_actual)
        files_actual_all.extend(files_actual)

    assert files_expected_count == (docs_valid_count + index_and_hidden_count)
    assert files_actual_count == docs_valid_count

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


testdata_document_delitem = (
    (
        copy.deepcopy(testdata_site_map_files),
        "__delitem__",
        "subfolder14/index.rst",
        pytest.raises(KeyError),
    ),
    (
        copy.deepcopy(testdata_site_map_files),
        "__delitem__",
        "index",
        pytest.raises(AssertionError),
    ),
    (
        copy.deepcopy(testdata_site_map_files),
        "__delitem__",
        "subfolder14/index",
        does_not_raise(),
    ),
)
ids_document_delitem = (
    "no such document cuz has suffix .rst",
    "cannot delete root document",
    "branch index document",
)


@pytest.mark.parametrize(
    "files, method_name, doc_name, expectation",
    testdata_document_delitem,
    ids=ids_document_delitem,
)
def test_document_delitem(files, method_name, doc_name, expectation, tmp_path):
    """api.Document methods"""
    # pytest --showlocals --log-level INFO -k "test_document_delitem" tests
    # prepare
    #    folders and empty files
    for posix in files:
        path_f = tmp_path.joinpath(*posix.split("/"))
        path_f.parent.mkdir(parents=True, exist_ok=True)
        path_f.touch()

    #    SiteMap instance
    site_map = create_site_map_from_path(tmp_path)

    # len(site_map)
    hidden_docs_count = 2
    actual_count = len(site_map)
    expected_count = len(testdata_site_map_files) - hidden_docs_count
    assert actual_count == expected_count

    # get doc count
    docs = site_map._docs.values()
    files_before_count = 0
    for doc in docs:
        files_before = doc.child_files()
        files_before_count += len(files_before)

    # act
    #    del item
    meth = getattr(site_map, method_name)
    with expectation:
        meth(doc_name)
    if isinstance(expectation, does_not_raise):
        # verify
        docs = site_map._docs.values()
        files_after_count = 0
        for doc in docs:
            files_after = doc.child_files()
            files_after_count += len(files_after)

        assert files_after_count == (files_before_count - 1)


@pytest.mark.parametrize(
    "path", JB_TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in JB_TOC_FILES]
)
def test_migrate_jb(path, data_regression):
    """Test migrate jupyter book."""
    toc = migrate_jupyter_book(Path(path))
    data_regression.check(toc)
    # check it is a valid toc
    parse_toc_data(toc)


testdata_assess_folder_expecting_folder = (
    (
        Path("/etc/shells"),
        (".sh",),
        "index",
        (".*",),
        pytest.raises(NotADirectoryError),
    ),
)
ids_assess_folder_expecting_folder = ("Expecting a folder, got a file",)


@pytest.mark.skipif(sys.platform != "linux", reason="path is to a known linux file")
@pytest.mark.parametrize(
    "path_dir, suffixes, default_index, ignore_matches, expectation",
    testdata_assess_folder_expecting_folder,
    ids=ids_assess_folder_expecting_folder,
)
def test_assess_folder_expecting_folder(
    path_dir,
    suffixes,
    default_index,
    ignore_matches,
    expectation,
):
    """Test _assess_folder."""
    # pytest --showlocals --log-level INFO -k "test_assess_folder_expecting_folder" tests
    with expectation:
        _assess_folder(path_dir, suffixes, default_index, ignore_matches)


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
    """Test _default_affinity."""
    actual_affinity = _default_affinity(additional_files, default_ext)
    assert actual_affinity == expected


testdata_sitemap_as_json = (
    (
        Path(__file__).parent.joinpath(
            "_jb_migrate_toc_files",
            "jb_docs_toc.yml",
        ),
        "jb-book",
    ),
)
ids_sitemap_as_json = ("use case jupyter_book",)


@pytest.mark.parametrize(
    "path_toc, use_case",
    testdata_sitemap_as_json,
    ids=ids_sitemap_as_json,
)
def test_sitemap_as_json(path_toc, use_case, tmp_path):
    """Render SiteMap as json for non-default use cases."""
    # pytest --showlocals --log-level INFO -k "test_sitemap_as_json" tests

    # prepare
    #    toc --> site_map
    d_toc = migrate_jupyter_book(path_toc)
    site_map = parse_toc_data(d_toc)

    # verify
    #    migrate_jupyter_book calls site_map.file_format setter
    assert site_map.file_format == use_case
    # act
    site_map.as_json()


testdata_sitemap_globs = (
    (
        Path(__file__).parent.joinpath("_toc_files", "glob_md.yml"),
        2,
        (
            "intro",
            "README",
            "conf.py",
            "doc1",
            "doc2",
            "doc3",
        ),
        4,
    ),
)
ids_sitemap_globs = ("two globs",)


@pytest.mark.parametrize(
    "path_toc, expected_glob_count, docs_wo_suffix, expected_match_count",
    testdata_sitemap_globs,
    ids=ids_sitemap_globs,
)
def test_sitemap_globs(
    path_toc,
    expected_glob_count,
    docs_wo_suffix,
    expected_match_count,
    docs_dir,
):
    """Inspect globs in a toc."""
    # pytest --showlocals --log-level INFO -k "test_sitemap_globs" tests
    site_map = create_site_from_toc(path_toc, root_path=docs_dir)
    set_globs = site_map.globs()
    actual_glob_count = len(set_globs)
    assert actual_glob_count == expected_glob_count

    actual_matches = 0
    for file_relpath in docs_wo_suffix:
        if site_map.match_globs(file_relpath):
            actual_matches += 1
    assert actual_matches == expected_match_count


testdata_new_excluded = (
    (
        Path(__file__).parent.joinpath("_toc_files", "glob_md_extras.yml"),
        [".md", ".rst"],
        ["doc2"],
        1,
    ),
)
ids_new_excluded = ("exclude_patterns are actually ignored",)


@pytest.mark.parametrize(
    "path_toc, source_suffix, exclude_patterns, expected_excluded_count",
    testdata_new_excluded,
    ids=ids_new_excluded,
)
def test_new_excluded(
    path_toc,
    source_suffix,
    exclude_patterns,
    expected_excluded_count,
    docs_dir,
):
    """Files to exclude from site."""
    # pytest --showlocals --log-level INFO -k "test_new_excluded" tests
    site_map = create_site_from_toc(path_toc, root_path=docs_dir)
    additional_files = site_map.meta.get("create_files", [])
    assert len(additional_files) != 0
    new_excluded = site_map.new_excluded(docs_dir, source_suffix, exclude_patterns)
    actual_excluded_count = len(new_excluded)
    assert actual_excluded_count == expected_excluded_count
