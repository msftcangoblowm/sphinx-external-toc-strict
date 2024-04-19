Sphinx
=======

Configuration
--------------

Add to your ``conf.py``:

.. code-block:: python

    extensions = ["sphinx_external_toc_strict"]
    external_toc_path = "_toc.yml"  # optional, default: _toc.yml
    external_toc_exclude_missing = False  # optional, default: False

Or to your ``pyproject.toml``

.. code-block:: text

   [tool.sphinx-pyproject]
   source_suffix = [".md", ".rst"]
   external_toc_exclude_missing = true
   extensions = [
      "sphinx.ext.autodoc",
      "sphinx.ext.autosectionlabel",
      "sphinx.ext.todo",
      "sphinx.ext.doctest",
      "sphinx_paramlinks",
      "sphinx.ext.intersphinx",
      "sphinx.ext.extlinks",
      "sphinx_external_toc_strict",
      "myst_parser",
   ]
   myst_enable_extensions = ["colon_fence", "html_image"]

Note the ``external_toc_path`` is always read as a Unix path, and can
either be specified relative to the source directory (recommended) or
as an absolute path.

Basic Structure
-------------------

A minimal ToC defines the top level `root` key, for a single root document file:

.. code-block:: text

   root: intro

The value of the ``root`` key will be a path to a file, in Unix format
(folders split by ``/``), relative to the source directory, and can be
with or without the file extension.

.. note:: root file

   For a root file other than than index, modify the Sphinx conf key is

   `master_doc <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-master_doc>`_

   This can be set in ``conf.py`` **or** ``pyproject.toml`` under section
   ``[tool.sphinx-pyproject]``

   Incorrectly set master_doc value ramification,
   :code:`make pdf` fails to build pdf

Document files can then have a ``subtrees`` key - denoting a list of
individual toctrees for that document - and in-turn each subtree should
have a ``entries`` key - denoting a list of children links, that are
one of:

- ``file``: path to a single document file in Unix format,  with or
  without the file extension (as for `root`)

- ``glob``: path to one or more document files *via* Unix shell-style
  wildcards
  (similar to `fnmatch <https://docs.python.org/3/library/fnmatch.html>`_),
  but single stars don't match slashes.)

- ``url``: path for an external URL (starting e.g. ``http`` or ``https``)

.. important::

   Each document file can only occur once in the ToC!

This can proceed recursively to any depth.

.. code-block:: text

   root: intro
   subtrees:
   - entries:
     - file: doc1
       subtrees:
       - entries:
         - file: doc2
           subtrees:
           - entries:
             - file: doc3
     - url: https://example.com
     - glob: subfolder/other*

This is equivalent to having a single ``toctree`` directive in ``intro``,
containing ``doc1``, and a single ``toctree`` directive in ``doc1``, with
the ``:glob:`` flag and containing ``doc2``, ``https://example.com`` and ``subfolder/other*``.

As a shorthand, the ``entries`` key can be at the same level as the ``file``,
which denotes a document with a single subtree. For example, this file
is exactly equivalent to the one above:

.. code-block:: text

   root: intro
   entries:
   - file: doc1
     entries:
     - file: doc2
       entries:
       - file: doc3
   - url: https://example.com
   - glob: subfolder/other*

File and URL titles
--------------------

By default, the initial header within a ``file`` document will be used
as its title in generated Table of Contents. With the ``title`` key you
can set an alternative title for a document. and also for ``url``:

.. code-block:: text

   root: intro
   subtrees:
   - entries:
     - file: doc1
       title: Document 1 Title
     - url: https://example.com
       title: Example URL Title

ToC tree options
-----------------

Each subtree can be configured with a number of options (see also
`sphinx toctree options <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree>`_):

- ``caption`` (string): A title for the whole the subtree, e.g. shown
  above the subtree in ToCs

- ``hidden`` (boolean): Whether to show the ToC within (inline of) the
  document (default ``False``).
  By default it is appended to the end of the document, but see also the
  ``tableofcontents`` directive for positioning of the ToC.

- ``maxdepth`` (integer): A maximum nesting depth to use when showing
  the ToC within the document (default -1, meaning infinite).

- ``numbered`` (boolean or integer): Automatically add numbers to all
  documents within a subtree (default ``False``).
  If set to ``True``, all sub-trees will also be numbered based on
  nesting (e.g. with ``1.1`` or ``1.1.1``), or if set to an integer then
  the numbering will only be applied to that depth.

- ``reversed`` (boolean): If ``True`` then the entries in the subtree
  will be listed in reverse order (default `False`).
  This can be useful when using ``glob`` entries.

- ``titlesonly`` (boolean): If ``True`` then only the first heading in
  the document will be shown in the ToC, not other headings of the same
  level (default ``False``).

These options can be set at the level of the subtree:

.. code-block:: text

   root: intro
   subtrees:
   - caption: Subtree Caption
     hidden: False
     maxdepth: 1
     numbered: True
     reversed: False
     titlesonly: True
     entries:
     - file: doc1
       subtrees:
       - titlesonly: True
         entries:
         - file: doc2

or, if you are using the shorthand for a single subtree, set options under
an ``options`` key:

.. code-block:: text

   root: intro
   options:
     caption: Subtree Caption
     hidden: False
     maxdepth: 1
     numbered: True
     reversed: False
     titlesonly: True
   entries:
   - file: doc1
     options:
       titlesonly: True
     entries:
     - file: doc2

You can also use the top-level ``defaults`` key, to set default options
for all subtrees:

.. code-block:: text

   root: intro
   defaults:
     titlesonly: True
   options:
     caption: Subtree Caption
     hidden: False
     maxdepth: 1
     numbered: True
     reversed: False
   entries:
   - file: doc1
     entries:
     - file: doc2

.. note:: title numbering

   By default, title numbering restarts for each subtree. For continuous numbering,
   there is the unmaintained sphinx extension,
   `sphinx-multitoc-numbering <https://github.com/executablebooks/sphinx-multitoc-numbering>`_.

   Tried it, didn't do the job! For now, ignore *numbered* option and
   the non-functional sphinx extension

.. warning:: ``numbered`` not as a default

   Since numbering cannot be changed by nested subtrees; sphinx will
   log a warning

Using different key-mappings
-----------------------------

For certain use-cases, it is helpful to map the ``subtrees``/``entries`` keys
to mirror e.g. an output `LaTeX structure <https://www.overleaf.com/learn/latex/Sections_and_chapters>`_.

The ``format`` key can be used to provide such mappings (and also initial defaults).
Currently available:

- ``jb-article``:
  - Maps ``entries`` -> ``sections``
  - Sets the default of ``titlesonly`` to ``true``

- ``jb-book``:
  - Maps the top-level ``subtrees`` to ``parts``
  - Maps the top-level ``entries`` to ``chapters``
  - Maps other levels of ``entries`` to ``sections``
  - Sets the default of ``titlesonly`` to ``true``

For example:

.. code-block:: text

   defaults:
     titlesonly: true
   root: index
   subtrees:
   - entries:
     - file: doc1
       entries:
       - file: doc2

is equivalent to:

.. code-block:: text

   format: jb-book
   root: index
   parts:
   - chapters:
     - file: doc1
       sections:
       - file: doc2

.. important::

   These change in key names do not change the output site-map structure

Excluding files not in ToC
---------------------------

By default, Sphinx will build all document files, regardless of whether
they are specified in the Table of Contents, if they:

1. Have a file extension relating to a loaded parser (e.g. ``.rst`` or ``.md``)

2. Do not match a pattern in `exclude_patterns <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns>`_


To automatically add any document files that do not match a ``file``
or ``glob`` in the ToC to the ``exclude_patterns`` list, add to your ``conf.py``:

.. code-block:: python

    external_toc_exclude_missing = True

Note that, for performance, files that are in *hidden folders*
(e.g. in ``.tox`` or ``.venv``) will not be added to ``exclude_patterns``
even if they are not specified in the ToC. You should exclude these folders explicitly.

.. important::

   This feature is not currently compatible with
   `orphan files <https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#metadata>`_.
