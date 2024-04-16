sphinx-external-toc-strict
===========================

A sphinx extension that allows the documentation site-map
(a.k.a Table of Contents) to be defined external to the documentation files.
As used by `Jupyter Book <https://jupyterbook.org>`_!

In normal Sphinx documentation, the documentation site-map is defined *via* a bottom-up approach - adding `toctree directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents>`_) within pages of the documentation.

This extension facilitates a **top-down** approach to defining the site-map structure, within a single YAML file.

.. image:: _static/toc-graphic.png
   :width: 600px
   :alt: "ToC graphic"

Example ToC
------------

Allows for documents not specified in the ToC to be auto-excluded.

.. tableofcontents::


Forked
-------

sphinx-external-toc-strict is a fork of 
`sphinx-external-toc <https://github.com/executablebooks/sphinx-external-toc>`_

Chris Sewell is the brilliant author of sphinx-external-toc

Thank you for making Sphinx much better

