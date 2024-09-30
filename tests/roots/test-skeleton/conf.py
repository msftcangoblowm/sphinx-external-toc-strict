"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Choose minimal sphinx extensions. source_suffix is both markdown and rst.

.. seealso::

   `[source] <https://github.com/sphinx-doc/sphinx/blob/master/tests/roots/test-root/conf.py>`_

"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().resolve()))

extensions = [
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
source_suffix = [".md", ".rst"]
