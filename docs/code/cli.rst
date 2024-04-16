Entrypoint functions
=====================

Command line functions

Usage

sphinx-etoc-strict [command] [options]

Help

sphinx-etoc-strict --help

sphinx-etoc-strict [command] --help

commands:

- create_site

- create_toc

- migrate_toc

- parse_toc

.. py:module:: sphinx_external_toc_strict.cli
   :platform: Unix
   :synopsis: Entrypoint functions

   .. py:function:: main

      Command-line for sphinx-external-toc-strict. Prints usage

   .. py:function:: parse_toc(toc_file: pathlib.Path) -> None
      Parse a ToC file to a site-map YAML

      :param toc_file: Absolute path to toc file. File name convention: ``_toc.yml``
      :type toc_file: pathlib.Path

   .. py:function:: create_site(toc_file: pathlib.Path, path: pathlib.Path, extension: str, overwrite: bool) -> None

      Create a project directory from a ToC file

     :param toc_file: Absolute path to toc file. File name convention: ``_toc.yml``
     :type toc_file: pathlib.Path
     :param path:

        root index file absolute path. Sphinx file stem convention:
        ``index``. Possible suffixes: ``.rst`` or ``.md``

     :type path: pathlib.Path
     :param extension:

        Default documentation file format extension. Either "rst" or "md"

     :type extension: str
     :param overwrite:

        Whether to overwrite docs/ folder tree. A default would be really
        nice here, ey?

     :type overwrite: bool

   .. py:function:: create_toc(site_dir: pathlib.Path, extension: str, index: str, skip_match: str, guess_titles: bool, file_format: str) -> None

      Create a ToC file from a project directory

     :param site_dir: Base folder documentation. Coding convention ``docs/`` or ``doc/``
     :type site_dir: pathlib.Path
     :param extension:

        Documentation file format extensions. Default both ".rst" or ".md". Take
        the opportunity to specify one rather than both

     :type extension: str
     :param index: File stem of root file. Coding convention is ``index``
     :type index: str
     :param skip_match:

        Default ``(".*",)``. Can provide option multiple times. Glob of
        relative path files to skip

     :type skip_match: str
     :param guess_titles:

        Default True. ``True`` to pull title from each document

     :type guess_titles: bool
     :param file_format:

        Supported use cases: ``default``, ``jb-book``, or ``jb-article``

     :type file_format: str

   .. py:function:: migrate_toc(toc_file: pathlib.Path, format: str, output: pathlib.Path) -> None

      Migrate a ToC from a previous revision

      :param toc_file: Table of contents file absolute path
      :type toc_file: pathlib.Path
      :param format: Ignored. Only possible value is ``jb-v0.10``
      :type format: str
      :param output: Output file absolute path
      :type output: pathlib.Path
