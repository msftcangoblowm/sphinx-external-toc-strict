.. Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
.. For details: https://github.com/msftcangoblowm/sphinx-external-toc-strict/blob/master/NOTICE.txt

sphinx-external-toc-strict
===========================

A sphinx extension that allows the documentation site-map (a.k.a Table of Contents) to be defined external to the documentation files.

|  |last-commit| |codecov| |license|
|  |test-status| |quality-status| |docs|
|  |kit| |versions| |black|
|  |stars| |mastodon-msftcangoblowm|

In normal Sphinx documentation, the documentation site-map is defined
*via* a bottom-up approach - adding
`toctree directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents>`_
within pages of the documentation.

This extension facilitates a **top-down** approach to defining the
site-map structure, within a single YAML file.

.. image:: https://raw.githubusercontent.com/msftcangoblowm/sphinx-external-toc-strict/main/docs/_static/toc-graphic.png
   :alt: ToC graphic
   :width: 1770px
   :height: 908px

It also allows for documents not specified in the ToC to be auto-excluded.

.. PYVERSIONS

* Python 3.9 through 3.12, and 3.13.0a3 and up.

**New in 1.2.x:**

create_site no overwrite and existing files informative message;
SiteMap.file_format ignore unknown use cases;

**New in 1.1.x:**

fork project; drop pyyaml support transition to strictyaml; use both markdown and restructuredtext;
code manual; semantic versioning; badges;

This is a fork
---------------

sphinx-external-toc-strict is a fork of sphinx-external-toc

.. csv-table:: Comparison
   :header: "Matric", "TOC", "TOC-Strict"
   :widths: auto

   "yaml package", `pyyaml / yaml <https://hitchdev.com/strictyaml/why-not/>`_, `strictyaml / ruemel.yaml <https://hitchdev.com/strictyaml/why/>`_
   ".hidden.files.rst", "Yes", "No"
   "docs theme", `sphinx-book-theme <https://sphinx-book-theme.readthedocs.io/en/latest>`_, `alabaster <https://alabaster.readthedocs.io/en/latest/>`_
   "markdown support", "Yes", "Yes"
   "both", `No <https://github.com/executablebooks/sphinx-external-toc/#development-notes>`_, "Yes, root doc must be ``index.rst``"
   "dump yaml", "use yaml.dump", "[package].parsing_strictyaml.dump_yaml"
   "static type checking", "patchy", "Yes (99%)"
   "coverage", "patchy", "maximium"
   "in-code manual", "No", "Yes"

The core API should be compatible. To avoid confusion, on the command line, rather than ``sphinx-etoc``, use ``sphinx-etoc-strict``

The author of sphinx-external-toc `[source ToC] <https://pypi.org/project/sphinx_external_toc/>`_ is Chris Sewell

The author of sphinx-external-toc-strict `[source ToC-strict] <https://pypi.org/project/sphinx-external-toc-strict/>`_ is Dave Faulkmore

User Guide
------------

Sphinx Configuration
^^^^^^^^^^^^^^^^^^^^^

Add to your ``conf.py``:

.. code:: python

    source_suffix = [".md", ".rst"]
    extensions = ["sphinx_external_toc_strict", "myst-parser"]
    external_toc_path = "_toc.yml"  # optional, default: _toc.yml
    external_toc_exclude_missing = True

Or to your ``pyproject.toml``:

.. code:: text

   [tool.sphinx-pyproject]
   source_suffix = [".md", ".rst"]
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
   external_toc_path = "_toc.yml"  # optional, default: _toc.yml
   external_toc_exclude_missing = true
   myst_enable_extensions = ["colon_fence", "html_image"]


Note the ``external_toc_path`` is always read as a Unix path, and can
either be specified relative to the source directory (recommended) or
as an absolute path.

Basic Structure
^^^^^^^^^^^^^^^^

A minimal ToC defines the top level ``root`` key, for a single root document file:

.. code:: yaml

   root: intro

The value of the ``root`` key will be a path to a file, in Unix format
(folders split by ``/``), relative to the source directory, and can be
with or without the file extension.

.. note:: Configure root file

   This root file will be set as the
   `master_doc <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-master_doc>`_.

Document files can then have a ``subtrees`` key - denoting a list of
individual toctrees for that document - and in-turn each subtree should
have a ``entries`` key - denoting a list of children links, that are one of:

- ``file``: path to a single document file in Unix format,  with or without the file extension (as for ``root``)
- ``glob``: path to one or more document files *via* Unix shell-style wildcards (similar to `fnmatch <https://docs.python.org/3/library/fnmatch.html>`_, but single stars don't match slashes.)
- ``url``: path for an external URL (starting e.g. ``http`` or ``https``)

.. important::

   Each document file can only occur once in the ToC!

This can proceed recursively to any depth.

.. code:: yaml

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

This is equivalent to having a single ``toctree`` directive in
``intro``, containing ``doc1``, and a single ``toctree`` directive in
``doc1``, with the ``glob:`` flag and containing ``doc2``,
``https://example.com`` and ``subfolder/other*``.

As a shorthand, the ``entries`` key can be at the same level as the
``file``, which denotes a document with a single subtree.

For example, this file is exactly equivalent to the one above:

.. code:: yaml

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
^^^^^^^^^^^^^^^^^^^^

By default, the initial header within a ``file`` document will be used
as its title in generated Table of Contents. With the ``title`` key you
can set an alternative title for a document. and also for ``url``:

.. code:: yaml

   root: intro
   subtrees:
   - entries:
     - file: doc1
       title: Document 1 Title
     - url: https://example.com
       title: Example URL Title

ToC tree options
^^^^^^^^^^^^^^^^^

Each subtree can be configured with a number of options (see also
`sphinx toctree options <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-toctree>`_):

- ``caption`` (string): A title for the whole the subtree, e.g. shown above the subtree in ToCs
- ``hidden`` (boolean): Whether to show the ToC within (inline of) the document (default ``False``).
  By default it is appended to the end of the document, but see also the `tableofcontents` directive for positioning of the ToC.
- ``maxdepth`` (integer): A maximum nesting depth to use when showing the ToC within the document (default -1, meaning infinite).
- ``numbered`` (boolean or integer): Automatically add numbers to all documents within a subtree (default ``False``).
  If set to `True`, all sub-trees will also be numbered based on nesting (e.g. with ``1.1`` or ``1.1.1``),
  or if set to an integer then the numbering will only be applied to that depth.
- ``reversed`` (boolean): If `True` then the entries in the subtree will be listed in reverse order (default ``False``).
  This can be useful when using `glob` entries.
- ``titlesonly`` (boolean): If `True` then only the first heading in the document will be shown in the ToC, not other headings of the same level (default ``False``).

These options can be set at the level of the subtree:

.. code:: yaml

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

or, if you are using the shorthand for a single subtree, set options under an ``options`` key:

.. code:: yaml

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

You can also use the top-level ``defaults`` key, to set default options for all subtrees:

.. code:: yaml

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

.. warning:: numbered

   ``numbered`` should not generally be used as a default, since numbering
   cannot be changed by nested subtrees, and sphinx will log a warning.

.. note:: title numbering

   By default, title numbering restarts for each subtree.
   If you want want this numbering to be continuous, check-out the
   `sphinx-multitoc-numbering extension <https://github.com/executablebooks/sphinx-multitoc-numbering>`_.

Using different key-mappings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For certain use-cases, it is helpful to map the ``subtrees``/``entries``
keys to mirror e.g. an output
`LaTeX structure <https://www.overleaf.com/learn/latex/sections_and_chapters>`_.

The ``format`` key can be used to provide such mappings (and also initial defaults).
Currently available:

- ``jb-article``:
  - Maps ``entries`` -> ``sections``
  - Sets the default of `titlesonly` to ``true``
- ``jb-book``:
  - Maps the top-level ``subtrees`` to ``parts``
  - Maps the top-level ``entries`` to ``chapters``
  - Maps other levels of ``entries`` to ``sections``
  - Sets the default of ``titlesonly`` to ``true``

For example:

.. code:: yaml

   defaults:
     titlesonly: true
   root: index
   subtrees:
   - entries:
     - file: doc1
       entries:
       - file: doc2

is equivalent to:

.. code:: yaml

   format: jb-book
   root: index
   parts:
   - chapters:
     - file: doc1
       sections:
       - file: doc2

.. important:: key names changes

   These change in key names do not change the output site-map structure

Add a ToC to a page's content
------------------------------

By default, the ``toctree`` generated per document (one per subtree) are
appended to the end of the document and hidden (then, for example, most
HTML themes show them in a side-bar).

But if you would like them to be visible at a certain place within the document body, you may do so by using the ``tableofcontents`` directive:

ReStructuredText:

.. code:: text

   .. tableofcontents::


MyST Markdown:

.. code:: text

   ```{tableofcontents}
   ```

Currently, only one ``tableofcontents`` should be used per page (all
``toctree`` will be added here), and only if it is a page with
child/descendant documents.

Note, this will override the ``hidden`` option set for a subtree.

Excluding files not in ToC
---------------------------

By default, Sphinx will build all document files, regardless of whether
they are specified in the Table of Contents, if they:

1. Have a file extension relating to a loaded parser (e.g. ``.rst`` or ``.md``)

2. Do not match a pattern in
   `exclude_patterns <https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns>`_

To automatically add any document files that do not match a ``file`` or
``glob`` in the ToC to the ``exclude_patterns`` list, add to your ``conf.py``:

.. code:: python

    external_toc_exclude_missing = True

Note that, for performance, files that are in *hidden folders* (e.g.
in ``.tox`` or ``.venv``) will not be added to ``exclude_patterns`` even
if they are not specified in the ToC. You should exclude these folders explicitly.

.. important:: incompatible with orphan files

   This feature is currently incompatible with `orphan files <https://www.sphinx-doc.org/en/master/usage/restructuredtext/field-lists.html#metadata>`_.

Command-line
-------------

This package comes with the ``sphinx-etoc-strict`` command-line program,
with some additional tools.

To see all options:

.. code: shell

   sphinx-etoc-strict --help

.. code:: text

   Usage: sphinx-etoc-strict [OPTIONS] COMMAND [ARGS]...

     Command-line for sphinx-external-toc-strict.

   Options:
     --version   Show the version and exit.
     -h, --help  Show this message and exit.

   Commands:
     from-project  Create a ToC file from a project directory.
     migrate    Migrate a ToC from a previous revision.
     parse      Parse a ToC file to a site-map YAML.
     to-project    Create a project directory from a ToC file.

To build a template project from only a ToC file:

.. code: shell

   sphinx-etoc-strict to-project -p path/to/site -e rst path/to/_toc.yml

Note, you can also add additional files in ``meta``/``create_files`` and append text to the end of files with ``meta``/``create_append``, e.g.

.. code:: yaml

   root: intro
   entries:
   - glob: doc*
   meta:
     create_append:
       intro: |
         This is some
         appended text
     create_files:
     - doc1
     - doc2
     - doc3

To build a ToC file from an existing site:

.. code: shell

   sphinx-etoc-strict from-project path/to/folder

Some rules used:

- Files/folders will be skipped if they match a pattern added by ``-s`` (based on `[fnmatch docs] <https://docs.python.org/3/library/fnmatch.html>`_ Unix shell-style wildcards)
- Sub-folders with no content files inside will be skipped
- File and folder names will be sorted by `natural order <https://en.wikipedia.org/wiki/Natural_sort_order>`_
- If there is a file called ``index`` (or the name set by ``-i``) in any folder, it will be treated as the index file, otherwise the first file by ordering will be used.

The command can also guess a ``title`` for each file, based on its path:

- The folder name is used for index files, otherwise the file name
- Words are split by ``_``
- The first "word" is removed if it is an integer

For example, for a project with files:

.. code:: text

   index.rst
   1_a_title.rst
   11_another_title.rst
   .hidden_file.rst
   .hidden_folder/index.rst
   1_a_subfolder/index.rst
   2_another_subfolder/index.rst
   2_another_subfolder/other.rst
   3_subfolder/1_no_index.rst
   3_subfolder/2_no_index.rst
   14_subfolder/index.rst
   14_subfolder/subsubfolder/index.rst
   14_subfolder/subsubfolder/other.rst

will create the ToC:

.. code: shell

   sphinx-etoc-strict from-project path/to/folder -i index -s ".*" -e ".rst" -t

.. code:: text

   root: index
   entries:
   - file: 1_a_title
     title: A title
   - file: 11_another_title
     title: Another title
   - file: 1_a_subfolder/index
     title: A subfolder
   - file: 2_another_subfolder/index
     title: Another subfolder
     entries:
     - file: 2_another_subfolder/other
       title: Other
   - file: 3_subfolder/1_no_index
     title: No index
     entries:
     - file: 3_subfolder/2_no_index
       title: No index
   - file: 14_subfolder/index
     title: Subfolder
     entries:
     - file: 14_subfolder/subsubfolder/index
       title: Subsubfolder
       entries:
       - file: 14_subfolder/subsubfolder/other
         title: Other

.. note:: hidden files are unsupported

   On a filesystem, somewhere within your home directory, hidden files
   are meant for config files. Documents are not hidden files!

   The file stem and file suffix handling has improved dramatically.

   But a hidden file, like ``.hidden_file.rst``, and ``.tar.gz`` looks
   similar. Both have no file stem

   Either can have markdown support or hidden file support, not both.
   Fate chose markdown support; that's the way the dice rolled


API
----

The ToC file is parsed to a ``SiteMap``, which is a ``MutableMapping``
subclass, with keys representing docnames mapping to a ``Document`` that
stores information on the toctrees it should contain:

.. code:: python

    from sphinx_external_toc.parsing_strict import parse_toc_yaml, dump_yaml

    path = "path/to/_toc.yml"
    site_map = parse_toc_yaml(path)
    dump_yaml(site_map)

Would produce e.g.

.. code:: yaml

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

Development Notes
------------------

Questions / TODOs:

- Add additional top-level keys, e.g. ``appendices`` (see `sphinx#2502 <https://github.com/sphinx-doc/sphinx/issues/2502>`_) and ``bibliography``
- Integrate `sphinx-multitoc-numbering <https://github.com/executablebooks/sphinx-multitoc-numbering>`_ into this extension? (or upstream PR)
- document suppressing warnings
- test against orphan file
- `sphinx-book-theme#304 <https://github.com/executablebooks/sphinx-book-theme/pull/304>`_
- CLI command to generate toc from existing documentation ``toctrees`` (and then remove toctree directives)
- test rebuild on toc changes (and document how rebuilds are controlled when toc changes)
- some jupyter-book issues point to potential changes in numbering, based on where the ``toctree`` is in the document.
  So could look into placing it e.g. under the first heading/title

.. |last-commit| image:: https://img.shields.io/github/last-commit/msftcangoblowm/sphinx-external-toc-strict/main
    :target: https://github.com/msftcangoblowm/sphinx-external-toc-strict/pulse
    :alt: last commit to gauge activity
.. |test-status| image:: https://github.com/msftcangoblowm/sphinx-external-toc-strict/actions/workflows/testsuite.yml/badge.svg?branch=main&event=push
    :target: https://github.com/msftcangoblowm/sphinx-external-toc-strict/actions/workflows/testsuite.yml
    :alt: Test suite status
.. |quality-status| image:: https://github.com/msftcangoblowm/sphinx-external-toc-strict/actions/workflows/quality.yml/badge.svg?branch=main&event=push
    :target: https://github.com/msftcangoblowm/sphinx-external-toc-strict/actions/workflows/quality.yml
    :alt: Quality check status
.. |docs| image:: https://readthedocs.org/projects/sphinx-external-toc-strict/badge/?version=latest&style=flat
    :target: https://sphinx-external-toc-strict.readthedocs.io/
    :alt: Documentation
.. |kit| image:: https://img.shields.io/pypi/v/sphinx-external-toc-strict
    :target: https://pypi.org/project/sphinx-external-toc-strict/
    :alt: PyPI status
.. |versions| image:: https://img.shields.io/pypi/pyversions/sphinx-external-toc-strict.svg?logo=python&logoColor=FBE072
    :target: https://pypi.org/project/sphinx-external-toc-strict/
    :alt: Python versions supported
.. |license| image:: https://img.shields.io/github/license/msftcangoblowm/sphinx-external-toc-strict
    :target: https://pypi.org/project/sphinx-external-toc-strict/blob/master/LICENSE.txt
    :alt: License
.. |stars| image:: https://img.shields.io/github/stars/msftcangoblowm/sphinx-external-toc-strict.svg?logo=github
    :target: https://github.com/msftcangoblowm/sphinx-external-toc-strict/stargazers
    :alt: GitHub stars
.. |mastodon-msftcangoblowm| image:: https://img.shields.io/mastodon/follow/112019041247183249
    :target: https://mastodon.social/@msftcangoblowme
    :alt: msftcangoblowme on Mastodon
.. |codecov| image:: https://codecov.io/gh/msftcangoblowm/sphinx-external-toc-strict/branch/main/graph/badge.svg?token=HCBC74IABR
    :target: https://codecov.io/gh/msftcangoblowm/sphinx-external-toc-strict
    :alt: sphinx-external-toc-strict coverage percentage
.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
