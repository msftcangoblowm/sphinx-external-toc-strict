"""Portion of the Sphinx ``test-root`` conf.py file.

Initializes some Sphinx extensions which don't require post configuration.

.. seealso::

   `[source] <https://github.com/sphinx-doc/sphinx/blob/master/tests/roots/test-root/conf.py>`_

"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().resolve()))

extensions = [
    # "sphinx.ext.intersphinx",
    # "sphinx_external_toc_strict",
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
]
project = "Sphinx <Tests>"
copyright = "1234-6789, copyright text credits"
version = "0.6"
release = "0.6alpha1"
exclude_patterns = ["_build", "**/excluded.*"]
pygments_style = "sphinx"

templates_path = ["_templates"]
source_suffix = {
    ".txt": "restructuredtext",
}
