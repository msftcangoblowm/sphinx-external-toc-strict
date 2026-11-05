"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

sphinx fixtures typing

"""

from collections.abc import Callable
from typing import TypeAlias

from sphinx.testing.util import SphinxTestApp

__all__ = ("MakeApp",)

MakeApp: TypeAlias = Callable[..., SphinxTestApp]
