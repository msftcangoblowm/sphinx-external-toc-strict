"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Separate out exceptions

"""

__all__ = ("MalformedError",)


class MalformedError(Exception):
    """Raised if the `_toc.yml` file is malformed."""
