"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Unittest of api module

With coverage

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.api' -m pytest \
   --showlocals tests/test_api.py && coverage report \
   --data-file=.coverage --include="**/api.py"

"""

from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING

import pytest

from sphinx_external_toc_strict.api import (
    Document,
    FileItem,
    GlobItem,
    SiteMap,
    TocTree,
    UrlItem,
)

if TYPE_CHECKING:
    from .typing_only import DOES_NOT_OR_DOES


@pytest.mark.parametrize(
    "url, title, expectation",
    (
        pytest.param(
            "https://blahblahblah.com/whatever.html",
            "this is my title",
            does_not_raise(),
            id="with-title",
        ),
        pytest.param(
            "https://blahblahblah.com/whatever.html",
            None,
            does_not_raise(),
            id="without-title",
        ),
        pytest.param(
            "not a url",
            None,
            pytest.raises(ValueError),
            id="not-a-url",
        ),
        pytest.param(
            0.2345,
            None,
            pytest.raises(TypeError),
            id="url-not-a-str",
        ),
    ),
)
def test_urlitem_validation(
    url: "str | float",
    title: "str | None",
    expectation: "DOES_NOT_OR_DOES",
) -> None:
    """Test UrlItem validation."""
    # pytest --showlocals --log-level INFO -k "test_urlitem_validation" tests
    with expectation:
        actual = UrlItem(
            url,  # type: ignore[arg-type]
            title,
        )
    if isinstance(expectation, does_not_raise):
        assert isinstance(actual, UrlItem)


@pytest.mark.parametrize(
    "all_docnames, patname, docnames_expected",
    (
        pytest.param(
            ["a_a_a", "a_a_b", "a_b_a", "a_b_c"],
            "a_b_*",
            ["a_b_a", "a_b_c"],
            id="get-pattern-a_b_wildcard",
        ),
    ),
)
def test_globitem_validation(
    all_docnames: list[str],
    patname: str,
    docnames_expected: list[str],
) -> None:
    """Test GlobItem. ``all_docnames`` must be type list."""
    # pytest --showlocals --log-level INFO -k "test_globitem_validation" tests
    item = GlobItem(patname)
    assert patname == str(item)
    gen = item.render(all_docnames)
    t_pairs = list(gen)
    docnames_actual = [docname for _, docname in t_pairs]
    assert docnames_actual == docnames_expected


def test_sitemap_get_changed_identical() -> None:
    """Test for identical sitemaps."""
    root_0 = Document("root")
    root_1 = Document("root")

    root_0.subtrees = [TocTree([])]
    root_1.subtrees = [TocTree([])]

    sitemap_0 = SiteMap(root_0)
    sitemap_1 = SiteMap(root_1)

    # verify -- empty set
    assert sitemap_0.get_changed(sitemap_1) == set()


def test_sitemap_get_changed_root() -> None:
    """Test for sitemaps with changed root."""
    doc1 = Document("doc1")
    doc2 = Document("doc2")

    sitemap1 = SiteMap(doc1)
    sitemap2 = SiteMap(doc2)

    sitemap1["doc2"] = doc2
    sitemap1["doc1"] = doc1

    # verify
    assert sitemap1.get_changed(sitemap2) == {"doc1"}


def test_sitemap_get_changed_title() -> None:
    """Test for sitemaps with changed title."""
    root1 = Document("root")
    root1.title = "a"
    sitemap1 = SiteMap(root1)

    root2 = Document("root")
    root2.title = "b"
    sitemap2 = SiteMap(root2)

    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees() -> None:
    """Test for sitemaps with changed subtrees."""
    root1 = Document("root")
    root1.subtrees = [TocTree([])]
    sitemap1 = SiteMap(root1)

    root2 = Document("root")
    root2.subtrees = [TocTree([FileItem("a")])]
    sitemap2 = SiteMap(root2)

    assert sitemap1.get_changed(sitemap2) == {"root"}


def test_sitemap_get_changed_subtrees_numbered() -> None:
    """Test for sitemaps with changed numbered option."""
    root1 = Document("root")
    root1.subtrees = [TocTree([], numbered=False)]
    sitemap1 = SiteMap(root1)

    root2 = Document("root")
    root2.subtrees = [TocTree([], numbered=True)]
    sitemap2 = SiteMap(root2)

    assert sitemap1.get_changed(sitemap2) == {"root"}
