"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Query sphinx.ext.intersphinx inventories.

.. py:data:: __all__
   :type: tuple[str, str]
   :value: ("fake_node", "query_intersphinx")

   Module exports

.. seealso::

   Code affected by RefItem

   | strict_external_toc_strict.events.insert_toctrees
   | strict_external_toc_strict.parsing_shared._parse_item_testable
   | strict_external_toc_strict.parsing_strictyaml._parse_doc_item

   Sphinx extension testing
   `[top] <https://www.sphinx-doc.org/en/master/extdev/testing.html>`_
   `[configuration] <https://www.sphinx-doc.org/en/master/usage/configuration.html>`_
   `[testing top] <https://github.com/sphinx-doc/sphinx/tree/master/sphinx/testing>`_
   `[sphinx.testing.fixtures] <https://github.com/sphinx-doc/sphinx/blob/master/sphinx/testing/fixtures.py>`_
   `[sphinx conftest.py] <https://github.com/sphinx-doc/sphinx/blob/master/tests/conftest.py>`_

   `missing_reference <https://github.com/sphinx-doc/sphinx/blob/7487e764cbd45269ef8be9976af67ce8bd37b48f/sphinx/ext/intersphinx/_resolve.py#L253C5-L253C22>`_

   unittest which calls missing_reference
   `sphinx.ext.intersphinx pytest <https://github.com/sphinx-doc/sphinx/blob/0a162fa8da21154011a2c890bb82fd0ce96ebf16/tests/test_extensions/test_ext_intersphinx.py#L49>`_

"""

from docutils import nodes
from sphinx import addnodes
from sphinx.ext.intersphinx import missing_reference

__all__ = (
    "fake_node",
    "query_intersphinx",
)


def fake_node(domain, ref_type, target, content, **attrs):
    """To query all (local) sphinx.ext.intersphinx inventories.
    Create args needed by :py:func:`sphinx.ext.intersphinx.missing_reference`.

    docname is accessible

    Usage

    .. code-block:: text

       from sphinx_external_toc_strict.sphinx_node import fake_node
       from sphinx.ext.intersphinx import missing_reference

       node, contnode = fake_node('std', 'ref', "The-Julia-Domain", "The-Julia-Domain")
       rn = missing_reference(app, app.env, node, contnode)
       docname = rn.astext()
       url = rn.get("refuri")

    .. seealso::

       `Nodes <https://docutils.sourceforge.io/docutils/nodes.py>`_

    """
    # docutils.nodes.Inline, docutils.nodes.TextElement
    # Inline is another decorator (besides emphasis)
    contnode = nodes.emphasis(content, content)
    node = addnodes.pending_xref("")
    node["refdomain"] = domain
    node["reftype"] = ref_type
    node["reftarget"] = target

    node.attributes.update(attrs)
    node += contnode

    return node, contnode


def query_intersphinx(app, target, contents=None, domain="std", ref_type="ref"):
    """Query intersphinx to get docname and url

    An inventory std:label entry (from sphinx intersphinx data)

    .. code-block:: text

       The-Julia-Domain std:label -1 write_inventory/#$ The Julia Domain

    Assumes an inventory with this entry is registered with
    intersphinx_mapping in ``/docs/conf.py`` or ``pyproject.toml``

    :param app: Sphinx app instance
    :type app: sphinx.application.Sphinx
    :param target:

        intersphinx ref id. From example inventory entry, ref id is
        ``The-Julia-Domain``.

    :type target: str
    :param contents: Default None. If provided, overrides inventory entry docname
    :type contents: str | None
    :param domain: An intersphinx domain. e.g. ``py`` or ``std``.
    :type domain: str
    :param ref_type: An intersphinx ref type. e.g. ``meth`` or ``ref``.
    :type ref_type: str
    :returns: docname and url
    :rtype: tuple[str | None, str | None]

    .. seealso::

       `intersphinx_data <https://raw.githubusercontent.com/sphinx-doc/sphinx/refs/heads/master/tests/test_util/intersphinx_data.py>`_

    """
    if contents is None:
        display_title = target
    else:
        display_title = contents

    node, contnode = fake_node(domain, ref_type, target, display_title)
    rn = missing_reference(app, app.env, node, contnode)
    if rn is None:
        t_ret = ("", "")
    else:
        docname = rn.astext()
        url = rn.get("refuri")
        t_ret = (docname, url)

    return t_ret
