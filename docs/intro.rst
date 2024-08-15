sphinx-external-toc-strict
===========================

A sphinx extension that allows the documentation site-map
(a.k.a Table of Contents) to be defined external to the documentation files.

In normal Sphinx documentation, the documentation site-map is defined *via* a bottom-up approach - adding `toctree directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents>`_) within pages of the documentation.

This extension facilitates a **top-down** approach to defining the site-map structure, within a single YAML file.

.. image:: _static/toc-graphic.png
   :width: 600px
   :alt: "ToC graphic"

.. PYVERSIONS

* Python 3.9 through 3.12, and 3.13.0a3 and up.

**New in 1.2.x:**

create_site no overwrite and existing files informative message;
SiteMap.file_format ignore unknown use cases;

**New in 1.1.x:**

fork project; drop pyyaml support transition to strictyaml; use both markdown and restructuredtext;
code manual; semantic versioning; badges;

Forked
-------

sphinx-external-toc-strict is a fork of sphinx-external-toc

.. csv-table:: Comparison
   :header: "Matric", "TOC", "TOC-Strict"
   :widths: auto

   "yaml package", `pyyaml / yaml <https://hitchdev.com/strictyaml/why-not/>`_, `strictyaml / ruemel.yaml <https://hitchdev.com/strictyaml/why/>`_
   ".hidden.files.rst", "Yes", "No"
   "docs theme", `sphinx-book-theme <https://sphinx-book-theme.readthedocs.io/en/latest>`_, `alabaster <https://alabaster.readthedocs.io/en/latest/>`_
   "markdown support", "Yes", "Yes"
   "both", `No <https://github.com/executablebooks/sphinx-external-toc/#development-notes>`_, "Yes, root doc must be ``index.rst``"
   "dump yaml", "use yaml.dump", :py:func:`parsing_strictyaml.dump_yaml <sphinx_external_toc_strict.parsing_strictyaml.dump_yaml>`
   "static type checking", "patchy", "Yes (99%)"
   "coverage", "patchy", "maximium"
   "in-code manual", "No", "Yes"

The core APIs should be compatible. To avoid confusion, on the command
line, rather than ``sphinx-etoc``, use ``sphinx-etoc-strict``

The author of `sphinx-external-toc <https://pypi.org/project/sphinx_external_toc/>`_ is Chris Sewell

The author of `sphinx-external-toc-strict <https://pypi.org/project/sphinx-external-toc-strict/>`_ is Dave Faulkmore

Thank you for making Sphinx much better

Example ToC
------------

Allows for documents not specified in the ToC to be auto-excluded.

.. tableofcontents::
