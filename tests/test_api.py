"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

..

Unittest of api module

Unit test -- Module

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.api' -m pytest \
   --showlocals tests/test_api.py && coverage report \
   --data-file=.coverage --include="**/api.py"

"""

from contextlib import nullcontext as does_not_raise

import pytest

from sphinx_external_toc_strict.api import (
    Document,
    FileItem,
    GlobItem,
    SiteMap,
    TocTree,
    UrlItem,
)

testdata_urlitem_validation = (
    (
        "https://blahblahblah.com/whatever.html",
        "this is my title",
        does_not_raise(),
    ),
    (
        "https://blahblahblah.com/whatever.html",
        None,
        does_not_raise(),
    ),
    (
        "not a url",
        None,
        pytest.raises(ValueError),
    ),
    (
        0.2345,
        None,
        pytest.raises(TypeError),
    ),
)
ids_urlitem_validation = (
    "with title",
    "without title",
    "not a url",
    "url not a str",
)


@pytest.mark.parametrize(
    "url, title, expectation",
    testdata_urlitem_validation,
    ids=ids_urlitem_validation,
)
def test_urlitem_validation(url, title, expectation):
    """Test UrlItem validation."""
    # pytest --showlocals --log-level INFO -k "test_urlitem_validation" tests
    with expectation:
        actual = UrlItem(url, title)
    if isinstance(expectation, does_not_raise):
        assert isinstance(actual, UrlItem)


testdata_globitem_validation = (
    (
        ["a_a_a", "a_a_b", "a_b_a", "a_b_c"],
        "a_b_*",
        ["a_b_a", "a_b_c"],
    ),
)
ids_globitem_validation = ("Get pattern a_b_wildcard",)


@pytest.mark.parametrize(
    "all_docnames, patname, docnames_expected",
    testdata_globitem_validation,
    ids=ids_globitem_validation,
)
def test_globitem_validation(all_docnames, patname, docnames_expected):
    """Test GlobItem. ``all_docnames`` must be type list."""
    # pytest --showlocals --log-level INFO -k "test_globitem_validation" tests
    item = GlobItem(patname)
    assert patname == str(item)
    gen = item.render(all_docnames)
    t_pairs = list(gen)
    docnames_actual = [docname for _, docname in t_pairs]
    assert docnames_actual == docnames_expected


def test_sitemap_get_changed_identical():
    """Test for identical sitemaps."""
    root1 = Document("root")
    root1.subtrees = [TocTree([])]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([])]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == set()


def test_sitemap_get_changed_root():
    """Test for sitemaps with changed root."""
    doc1 = Document("doc1")
    doc2 = Document("doc2")
    sitemap1 = SiteMap(doc1)
    sitemap1["doc2"] = doc2
    sitemap2 = SiteMap(doc2)
    sitemap1["doc1"] = doc1
    assert sitemap1.get_changed(sitemap2) == {"doc1"}


def test_sitemap_get_changed_title():
    """Test for sitemaps with changed title."""
    root1 = Document("root")
    root1.title = "a"
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.title = "b"
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees():
    """Test for sitemaps with changed subtrees."""
    root1 = Document("root")
    root1.subtrees = [TocTree([])]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([FileItem("a")])]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees_numbered():
    """Test for sitemaps with changed numbered option."""
    root1 = Document("root")
    root1.subtrees = [TocTree([], numbered=False)]
    sitemap1 = SiteMap(root1)
    root2 = Document("root")
    root2.subtrees = [TocTree([], numbered=True)]
    sitemap2 = SiteMap(root2)
    assert sitemap1.get_changed(sitemap2) == {"root"}
