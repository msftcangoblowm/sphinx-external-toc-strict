"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Test querying std:doc and std:label --> std:ref

Unit test -- Module

.. code-block:: shell

   python -m coverage run --source='strict_external_toc_strict.sphinx_node' -m pytest \
   --showlocals tests/test_refitem.py && coverage report \
   --data-file=.coverage --include="**/sphinx_node.py"

"""

from contextlib import nullcontext as does_not_raise
from typing import TYPE_CHECKING

import pytest
from sphinx.ext.intersphinx import load_mappings
from sphinx.ext.intersphinx import setup as intersphinx_setup
from sphinx.ext.intersphinx import validate_intersphinx_mapping

from sphinx_external_toc_strict.api import RefItem
from sphinx_external_toc_strict.sphinx_node import query_intersphinx
from tests.test_util.intersphinx_data import INVENTORY_V2

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path
    from typing import Any

    from sphinx.application import Sphinx

    from tests.typing_only import DOES_NOT_OR_DOES
    from tests.typing_sphinx import MakeApp


def set_config(app: "Sphinx", mapping: "dict[str, Any]") -> None:
    """Setup intersphinx_mapping and intersphinx_disabled_reftypes.
    Initialize intersphinx first.

    :param app:

       Sphinx app instance. To get the app with the least fuss,
       Do not load sphinx_external_toc_strict or intersphinx.
       Additional Sphinx extensions initialize later.

    :type app: pytest.Fixture
    :param mapping: intersphinx_mapping dict
    :type mapping: dict[str, typing.Any]
    """
    # copy *mapping* so that normalization does not alter it
    app.config.intersphinx_mapping = mapping.copy()
    app.config.intersphinx_cache_limit = 0
    app.config.intersphinx_disabled_reftypes = []


@pytest.fixture
def load_inv(
    app: "Sphinx",
    inventory_v2: "Callable[[MakeApp, str], Path]",
    augment_intersphinx_mapping: "Callable[[MakeApp, dict[str, Any]], None]",
) -> "Callable[[str | None, str | None, str | None], None]":
    """Must be called by a test marked with ``pytest.mark.sphinx``.

    For querying only, not running sphinx build.

    :param inv_file_name:

       Default "objects-test.inv". inventory file name. Not setup to load more than one.

    :type inv_file_name: str
    :param intersphinx_inv_id:

       intersphinx_mapping inventory identifier. Used with
       ``:external:[id acting as a domain]:[ref id]`` lookup syntax.

    :type intersphinx_inv_id: str
    :param uri: base url
    :type uri: str
    """

    def _func(
        inv_file_name: "str | None" = "objects-test.inv",
        intersphinx_inv_id: "str | None" = "python",
        uri: "str | None" = "https://docs.python.org/3",
    ) -> None:
        """After initializing Sphinx app. Initialize:
        intersphinx, intersphinx_mapping and load an inventory"""
        intersphinx_setup(app)

        #    inventory
        inv_file = inventory_v2(app, inv_file_name)
        assert inv_file.exists() and inv_file.is_file()

        #    in addition to conf.py, add runtime config settings
        augment_intersphinx_mapping(
            app,
            {
                intersphinx_inv_id: (uri, str(inv_file)),
            },
        )

        #    load the inventory and check if it's done correctly
        validate_intersphinx_mapping(app, app.config)
        load_mappings(app)
        # inv = app.env.intersphinx_inventory
        pass

    return _func


@pytest.mark.sphinx("html", testroot="root", freshenv=True)
@pytest.mark.parametrize(
    "inventory_contents, domain, ref_type, ref_id, t_out",
    (
        pytest.param(
            INVENTORY_V2,
            "std",
            "ref",
            "The-Julia-Domain",
            (
                "The Julia Domain",
                "https://docs.python.org/3/write_inventory/#The-Julia-Domain",
            ),
            id="Query-sphinx.ext.intersphinx-INVENTORY_V2",
        ),
        pytest.param(
            INVENTORY_V2,
            "std",
            "ref",
            "nonexistent",
            ("", ""),
            id="nonexistent-ref",
        ),
    ),
)
def test_querying_inv(
    inventory_contents: bytes,
    domain: str,
    ref_type: str,
    ref_id: str,
    t_out: tuple[str, str],
    app: "Sphinx",
    load_inv: "Callable[[str | None, str | None, str | None], None]",
) -> None:
    """Test querying an inventory. No _toc.yml file yet."""
    # python -X dev -m pytest --showlocals --log-level INFO -k "test_querying_inv" tests

    # srcdir = app.srcdir
    # outdir = app.outdir
    load_inv()

    # Act
    #    no context data
    t_query_result = query_intersphinx(app, ref_id, domain=domain, ref_type=ref_type)
    assert isinstance(t_query_result, tuple)
    assert t_query_result == t_out

    docname, url = t_query_result
    assert isinstance(docname, str)
    assert isinstance(url, str)

    #    provide a contents
    #    Does not change the title. Maybe changes how it's rendered in the toc?!
    title_new = f"Buy this {ref_id}!"
    t_query_result = query_intersphinx(
        app,
        ref_id,
        contents=title_new,
        domain=domain,
        ref_type=ref_type,
    )
    assert isinstance(t_query_result, tuple)
    assert t_query_result == t_out


@pytest.mark.sphinx("html", testroot="root", freshenv=True)
@pytest.mark.parametrize(
    "ref_id, title, expectation, expected_title",
    (
        pytest.param(
            "The-Julia-Domain",
            "this is my title",
            does_not_raise(),
            "this is my title",
            id="with-title",
        ),
        pytest.param(
            "The-Julia-Domain",
            None,
            does_not_raise(),
            "The Julia Domain",
            id="without-title",
        ),
        pytest.param(
            "not-a-ref",
            None,
            does_not_raise(),
            "",
            id="not-a-ref.-Only-intersphinx-knows",
        ),
        pytest.param(
            0.2345,
            None,
            pytest.raises(TypeError),
            "",
            id="ref-not-a-str",
        ),
    ),
)
def test_refitem_validation(
    ref_id: "str | float",
    title: "str | None",
    expectation: "DOES_NOT_OR_DOES",
    expected_title: str,
    app: "Sphinx",
    load_inv: "Callable[[str | None, str | None, str | None], None]",
) -> None:
    """Test RefItem validation."""
    # pytest --showlocals --log-level INFO -k "test_refitem_validation" tests
    url_expected = f"https://docs.python.org/3/write_inventory/#{ref_id}"

    load_inv()
    with expectation:
        item = RefItem(
            ref_id,  # type: ignore[arg-type]
            title,
        )
    if isinstance(expectation, does_not_raise):
        assert isinstance(item, RefItem)

        gen = item.render(app)
        t_actual = next(gen)
        assert isinstance(t_actual, tuple)
        title_actual, url_actual = t_actual
        assert title_actual == expected_title
        is_ref_not_found = len(url_actual) == 0
        if is_ref_not_found:
            # no such ref id in inventory
            assert url_actual == ""
        else:
            # inventory entry found
            assert url_actual == url_expected
