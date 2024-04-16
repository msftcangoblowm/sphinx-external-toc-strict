"""
dataclasses dynamically construct tools and Validators

Compatibility for using dataclasses instead of attrs.

**But** a dynamic dataclasses.dataclasses with dynamic
dataclasses.Field **cannot** be static type checked!

dataclasses.Field is for internal use only and is not a type

dataclasses.dataclass is not a valid type. Create a Protocol?

.. py:data:: UnionAB
   :type: typing.TypeAlias
   :value: typing.Union[typing.Any, collections.abc.Sequence[typing.Any]]

   :py:func:`isinstance` accepts a type or a tuple of types

.. py:data:: ValidatorType
   :type: typing.TypeAlias
   :value: Callable[[Any, dc.Field[Any], UnionAB], None]

   Reinventing the wheel. :pypi_org:`attrs` has built-in validators.
   Evidently dataclasses doesn't

"""

from __future__ import annotations

import dataclasses as dc
import re
import sys
from typing import (
    Any,
    Callable,
    Pattern,
    Protocol,
    Union,
    cast,
    runtime_checkable,
)

from docutils.nodes import Element

if sys.version_info >= (3, 9):  # pragma: no cover
    from collections.abc import Sequence
else:  # pragma: no cover
    from typing import Sequence

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias

# Use dataclasses slots True for reduced memory usage and performance gain
if sys.version_info >= (3, 10):  # pragma: no cover
    DC_SLOTS: dict[str, bool] = {"slots": True}
else:  # pragma: no cover
    DC_SLOTS: dict[str, bool] = {}


# https://stackoverflow.com/questions/54668000/type-hint-for-an-instance-of-a-non-specific-dataclass
@runtime_checkable
@dc.dataclass
class DataclassProtocol(Protocol):
    pass


def field(**kwargs: Any) -> Any:
    """dataclasses have fields. When dynamically creating a dataclass
    the fields must also be dynamically created

    :param kwargs: keyword/value pairs dict passed to :py:func:`dataclasses.field`
    :type kwargs: typing.Any
    :returns: A dynamically created dataclasses field
    :rtype: typing.Any
    """
    if sys.version_info < (3, 10):
        kwargs.pop("kw_only", None)
    else:  # pragma: no cover
        pass

    if "validator" in kwargs:
        kwargs.setdefault("metadata", {})["validator"] = kwargs.pop("validator")
    else:  # pragma: no cover
        pass

    return dc.field(**kwargs)


field.__doc__ = dc.field.__doc__


def validate_fields(inst: DataclassProtocol) -> None:
    """Validate the fields of a dataclass,
    according to `validator` functions set in the field metadata.

    This function should be called in the `__post_init__` of the dataclass.

    The validator function should take as input (inst, field, value) and
    raise an exception if the value is invalid.
    :param inst: A dataclasses decorated class instance
    :type inst: DataclassProtocol
    """
    for field in dc.fields(inst):
        if "validator" not in field.metadata:
            continue
        if isinstance(field.metadata["validator"], list):
            for validator in field.metadata["validator"]:
                validator(inst, field, getattr(inst, field.name))
        else:
            field.metadata["validator"](inst, field, getattr(inst, field.name))


# https://github.com/python/mypy/issues/12155
UnionAB: TypeAlias = Union[Any, Sequence[Any]]
ValidatorType: TypeAlias = Callable[[Any, dc.Field[Any], UnionAB], None]


def instance_of(type_: UnionAB) -> ValidatorType:
    """
    A validator that raises a `TypeError` if the initializer is called
    with a wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    :param type_: The type to check for.
    :type type_: typing.Any | collections.abc.Sequence[typing.Any]
    :returns: Validator to check value is instance of type
    :rtype: :py:data:`~sphinx_external_toc_strict._compat.ValidatorType`
    """

    def _validator(inst: Any, attr: dc.Field[Any], value: UnionAB) -> None:
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, type_):  # type: ignore[arg-type]
            msg_exc = (
                f"'{attr.name}' must be {type_!r} (got {value!r} that "
                f"is a {value.__class__!r})."
            )
            raise TypeError(msg_exc)

    return cast(
        Callable[[Any, dc.Field[Any], Union[Any, Sequence[Any]]], None], _validator
    )


def matches_re(regex: str | Pattern[str], flags: int = 0) -> ValidatorType:
    r"""Create a validator fcn for checks against a regex

    When str and regex are a mismatch raises :py:exc:`ValueError`.

    :param regex: a regex string or precompiled pattern to match against
    :type regex: str | re.Pattern
    :param flags:

       Default 0. flags that will be passed to the underlying :py:mod:`re`
       function (default 0)

    :type flags: int
    :returns: An inline function to validate regex
    :rtype: :py:data:`~sphinx_external_toc_strict._compat.ValidatorType`
    :raises:

       - :py:exc:`ValueError` -- validator that raises ValueError when
         str arg passed to initializer doesn't match regex

       - :py:exc:`TypeError` -- flags can only be used with a string
         pattern; pass flags to re.compile() instead

    """
    fullmatch = getattr(re, "fullmatch", None)

    if isinstance(regex, Pattern):
        if flags:
            raise TypeError(
                "'flags' can only be used with a string pattern; "
                "pass flags to re.compile() instead"
            )
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if fullmatch:
        match_func = pattern.fullmatch
    else:  # Python 2 fullmatch emulation (https://bugs.python.org/issue16203)
        pattern = re.compile(r"(?:{})\Z".format(pattern.pattern), pattern.flags)
        match_func = pattern.match

    def _validator(inst: Any, attr: dc.Field[Any], value: str) -> None:
        if not match_func(value):
            raise ValueError(
                f"'{attr.name}' must match regex {pattern!r} ({value!r} doesn't)"
            )

    return cast(
        Callable[[Any, dc.Field[Any], Union[Any, Sequence[Any]]], None], _validator
    )


def optional(validator: ValidatorType) -> ValidatorType:
    """Morphs a validator into an optional (attribute) validator

    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to ``None`` in addition to satisfying the requirements of
    the sub-validator.

    :param validator: An argument validator
    :type validator: collections.abc.Callable[[typing.Any, dataclasses.Field, typing.Any], None]
    :returns: An inline function optional (attribute) validator
    :rtype: collections.abc.Callable[[typing.Any, dataclasses.Field, typing.Any], None]
    """

    def _validator(inst: Any, attr: dc.Field[Any], value: UnionAB) -> None:
        if value is None:
            return

        validator(inst, attr, value)

    return cast(
        Callable[[Any, dc.Field[Any], Union[Any, Sequence[Any]]], None], _validator
    )


def deep_iterable(
    member_validator: ValidatorType, iterable_validator: ValidatorType | None = None
) -> ValidatorType:
    """A validator that performs deep validation of an iterable.

    :param member_validator: Validator to apply to iterable members
    :type member_validator: :py:class:`sphinx_external_toc_strict._compat.ValidatorType`
    :param iterable_validator: Default None. Validator to apply to iterable itself
    :type iterable_validator: :py:class:`sphinx_external_toc_strict._compat.ValidatorType` | None
    :returns: Iterator which validates members
    :rtype: :py:class:`sphinx_external_toc_strict._compat.ValidatorType`
    """

    def _validator(inst: Any, attr: dc.Field[Any], value: UnionAB) -> None:
        if iterable_validator is not None:
            iterable_validator(inst, attr, value)

        for member in value:
            member_validator(inst, attr, member)

    return cast(
        Callable[[Any, dc.Field[Any], Union[Any, Sequence[Any]]], None], _validator
    )


# Docutils compatibility


def findall(node: Element) -> Any:
    """findall replaces traverse in docutils v0.18

    Difference is that findall is an iterator

    Make findall available for all docutils versions

    :param node: A parent tree node
    :type node: docutils.nodes.Element
    :returns: Not sure about signature of node.traverse
    :rtype: Iterator[docutils.nodes.Element]
    """
    return getattr(node, "findall", node.traverse)
