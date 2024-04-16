Command-line
===============

This package comes with the ``sphinx-etoc-strict`` command-line program,
with some additional tools.

To see all options:

.. code-block:: shell

   sphinx-etoc-strict --help

.. code-block:: text

   Usage: sphinx-etoc-strict [OPTIONS] COMMAND [ARGS]...

     Command-line for sphinx-external-toc.

   Options:
     --version   Show the version and exit.
     -h, --help  Show this message and exit.

   Commands:
     from-project  Create a ToC file from a project directory.
     migrate    Migrate a ToC from a previous revision.
     parse      Parse a ToC file to a site-map YAML.
     to-project    Create a project directory from a ToC file.

For help for a specific command. e.g. from-project

.. code-block:: shell

   sphinx-etoc-strict from-project --help

.. code-block:: text

   Usage: sphinx-etoc from-project [OPTIONS] SITE_DIR

     Create a ToC file from a project directory.

   Options:
     -e, --extension TEXT         File extensions to consider as documents
                                  (use multiple times)  [default: .rst, .md]
     -i, --index TEXT             File name (without suffix) considered as the
                                  index file in a folder  [default: index]
     -s, --skip-match TEXT        File/Folder names which match will be
                                  ignored (use multiple times)  [default: .*]
     -t, --guess-titles           Guess titles of documents from path names
     -f, --file-format [default|jb-book|jb-article]
                                  The key-mappings to use.  [default: default]
     -h, --help                   Show this message and exit.

from-project
-------------

To build a (raw) ToC file from an existing site

.. code-block:: shell

   sphinx-etoc-strict from-project path/to/folder

Some rules used:

- Files/folders will be skipped if they match a pattern added by ``-s``
  (based on `fnmatch <https://docs.python.org/3/library/fnmatch.html>`_)
  Unix shell-style wildcards)

- Sub-folders with no content files inside will be skipped

- File and folder names will be sorted by
  `natural order <https://en.wikipedia.org/wiki/Natural_sort_order>`_

- If there is a file called `index` (or the name set by `-i`) in any
  folder, it will be treated as the index file, otherwise the first
  file by ordering will be used.

The command can also guess a ``title`` for each file, based on its path:

- The folder name is used for index files, otherwise the file name

- Words are split by ``_``

- The first "word" is removed if it is an integer

For example, for a project with files:

.. code-block:: text

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

.. code-block:: shell

   sphinx-etoc from-project path/to/folder -i index -s ".*" -e ".rst" -t

.. code-block:: yaml

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

to-project
-----------

To build a template project from only a ToC file:

.. code-block:: shell

   sphinx-etoc to-project -p path/to/site -e rst path/to/_toc.yml

Note, you can also add additional files in `meta`/`create_files` and
append text to the end of files with `meta`/`create_append`, e.g.

.. code-block:: shell

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
