import re
import sys
from pathlib import Path

from packaging.version import parse
from sphinx_pyproject import SphinxConfig

from sphinx_external_toc_strict.constants import __version__ as proj_version
from sphinx_external_toc_strict.pep518_read import find_project_root

path_docs = Path(__file__).parent
path_package_base = path_docs.parent
sys.path.insert(0, str(path_package_base))  # Needed ??

# pyproject.toml search algo. Credit/Source: https://pypi.org/project/black/
srcs = (path_package_base,)
t_root = find_project_root(srcs)

config = SphinxConfig(
    # Path(__file__).parent.parent.joinpath("pyproject.toml"),
    t_root[0] / "pyproject.toml",
    globalns=globals(),
    config_overrides={"version": proj_version},  # dynamic version setuptools_scm
)

# This project is a fork from "Sphinx External ToC"
proj_project = config.name
proj_description = config.description
proj_authors = config.author

slug = re.sub(r"\W+", "-", proj_project.lower())
proj_master_doc = config.get("master_doc")

# Original author Chris Sewell <chrisj_sewell@hotmail.com>
# copyright = "2021, Executable Book Project"

# @@@ editable
copyright = "2023–2024, Dave Faulkmore"
# The short X.Y.Z version.
version = "1.2.0"
# The full version, including alpha/beta/rc tags.
release = "1.2.0"
# The date of release, in "monthname day, year" format.
release_date = "August 15, 2024"
# @@@ end

v = parse(release)
version_short = f"{v.major}.{v.minor}"
# version_xyz = f"{v.major}.{v.minor}.{v.micro}"
version_xyz = version
project = f"{proj_project} {version}"

###############
# Dynamic
###############
rst_epilog = """
.. |project_name| replace:: {slug}
.. |package-equals-release| replace:: sphinx_external_toc_strict=={release}
""".format(
    release=release, slug=slug
)

html_theme_options = {
    "description": proj_description,
    "show_relbars": True,
    "logo_name": False,
    "logo": "sphinx-external-toc-strict-logo.svg",
    "show_powered_by": False,
}

latex_documents = [
    (
        proj_master_doc,
        f"{slug}.tex",
        f"{proj_project} Documentation",
        proj_authors,
        "manual",  # manual, howto, jreport (Japanese)
        True,
    )
]
man_pages = [
    (
        proj_master_doc,
        slug,
        f"{proj_project} Documentation",
        [proj_authors],
        1,
    )
]
texinfo_documents = [
    (
        proj_master_doc,
        slug,
        f"{proj_project} Documentation",
        proj_authors,
        slug,
        proj_description,
        "Miscellaneous",
    )
]

#################
# Static
#################
ADDITIONAL_PREAMBLE = r"""
\DeclareUnicodeCharacter{20BF}{\'k}
"""

latex_elements = {
    "sphinxsetup": "verbatimforcewraps",
    "extraclassoptions": "openany,oneside",
    "preamble": ADDITIONAL_PREAMBLE,
}

html_sidebars = {
    "**": [
        "about.html",
        "searchbox.html",
        "navigation.html",
        "relations.html",
    ],
}

intersphinx_mapping = {
    "python": (  # source https://docs.python.org/3/objects.inv
        "https://docs.python.org/3",
        ("objects-python.inv", "objects-python.txt"),
    ),
    "strictyaml-docs": (  # source logging-strict
        "https://hitchdev.com/strictyaml",
        ("objects-strictyaml-docs.inv", "objects-strictyaml-docs.txt"),
    ),
    "strictyaml-source": (  # source logging-strict
        "https://github.com/crdoconnor/strictyaml",
        ("objects-strictyaml-source.inv", "objects-strictyaml-source.txt"),
    ),
    "docutils-source": (
        "https://docutils.sourceforge.io",
        ("objects-docutils-source.inv", "objects-docutils-source.txt"),
    ),
    "sphinx-docs": (  # Alternative? https://www.sphinx-doc.org/objects.inv
        "https://www.sphinx-doc.org/en/master",
        ("objects-sphinx-docs.inv", "objects-sphinx-docs.txt"),
    ),
    "toc-strict": (
        "https://sphinx-external-toc-strict.readthedocs.io/en/latest",
        ("objects-toc-strict.inv", "objects-toc-strict.txt"),
    ),
    "objects-black": (  # source logging-strict
        "https://github.com/psf/black",
        ("objects-black.inv", "objects-black.txt"),
    ),
}
intersphinx_disabled_reftypes = ["std:doc"]

extlinks = {
    "pypi_org": (  # url to: aiologger
        "https://pypi.org/project/%s",
        "%s",
    ),
}

# spoof user agent to prevent broken links
# curl -A "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0" --head "https://github.com/python/cpython/blob/3.12/Lib/unittest/case.py#L193"
linkcheck_request_headers = {
    "https://github.com/": {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    },
    "https://docs.github.com/": {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
    },
}

# Ignore unfixable WARNINGS
# in pyproject.toml --> nitpicky = true
# in conf.py --> nitpicky = True
nitpick_ignore = [
    ("py:class", "ValidatorType"),
]
