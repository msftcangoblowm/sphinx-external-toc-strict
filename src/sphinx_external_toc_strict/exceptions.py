"""
.. moduleauthor:: Dave Faulkmore <https://mastodon.social/@msftcangoblowme>

Seperate out exceptions

.. py:data:: __all__
   :type: tuple[str]
   :value: ("MalformedError",)

   Module exports

"""

__all__ = ("MalformedError",)


class MalformedError(Exception):
    """Raised if the `_toc.yml` file is malformed."""
