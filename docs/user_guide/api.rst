API
====

The ToC file is parsed to a ``SiteMap``, which is a
:py:class:`~collections.abc.MutableMapping` subclass, with keys representing
docnames mapping to a ``Document`` that stores information on the toctrees
it should contain:

.. code-block:: python

    from sphinx_external_toc_strict.parsing_strictyaml import parse_toc_yaml, dump_yaml

    path = "path/to/_toc.yml"
    site_map = parse_toc_yaml(path)
    dump_yaml(site_map)

Would produce e.g.

.. code-block:: yaml

   root: intro
   documents:
     doc1:
       docname: doc1
       subtrees: []
       title: null
     intro:
       docname: intro
       subtrees:
       - caption: Subtree Caption
         numbered: true
         reversed: false
         items:
         - doc1
         titlesonly: true
       title: null
   meta: {}
