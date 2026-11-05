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
   :value: collections.abc.Callable[[typing.Any, dc.Field[typing.Any], sphinx_external_toc_strict.util_dc.UnionAB], None]

   Reinventing the wheel. :pypi_org:`attrs` has built-in validators.
   Evidently dataclasses doesn't

"""

import dataclasses as dc
import re
from collections.abc import (
    Callable,
    Sequence,
)
from typing import (
    Any,
    TypeAlias,
    cast,
)

__all__ = (
    "DC_SLOTS",
    "UnionAB",
    "ValidatorType",
    "deep_iterable",
    "field",
    "findall",
    "instance_of",
    "is_dataclass_instance",
    "matches_re",
    "optional",
    "validate_fields",
)

DC_SLOTS = {"slots": True}


def is_dataclass_instance(obj):
    """Check if a dataclasses.dataclass instance.

    :param obj: an instance
    :type obj: object
    :rtype: bool
    """
    ret = not isinstance(obj, type) and dc.is_dataclass(obj)
    return ret


def field(**kwargs):
    """dataclasses have fields. When dynamically creating a dataclass
    the fields must also be dynamically created

    :param kwargs: keyword/value pairs dict passed to :py:func:`dataclasses.field`
    :type kwargs: typing.Any
    :returns: A dynamically created dataclasses field
    :rtype: typing.Any
    """
    if "validator" in kwargs:  # pragma: no branch
        kwargs.setdefault("metadata", {})["validator"] = kwargs.pop("validator")

    return dc.field(**kwargs)


field.__doc__ = dc.field.__doc__


def validate_fields(inst) -> None:
    """Validate the fields of a dataclass,
    according to `validator` functions set in the field metadata.

    This function should be called in the `__post_init__` of the dataclass.

    The validator function should take as input (inst, field, value) and
    raise an exception if the value is invalid.
    :param inst: A dataclasses decorated class instance
    :type inst: object
    """
    if is_dataclass_instance(inst):  # pragma: no branch
        for field in dc.fields(inst):
            if "validator" in field.metadata:  # pragma: no branch
                if isinstance(field.metadata["validator"], list):
                    for validator in field.metadata["validator"]:
                        validator(inst, field, getattr(inst, field.name))
                else:
                    field.metadata["validator"](inst, field, getattr(inst, field.name))


# https://github.com/python/mypy/issues/12155
UnionAB: TypeAlias = Any | Sequence[Any]
ValidatorType: TypeAlias = Callable[[Any, dc.Field[Any], UnionAB], None]


def instance_of(type_):
    """A validator that raises a :py:exc:`TypeError` if the initializer is called
    with a wrong type for this particular attribute (checks are performed using
    `isinstance` therefore it's also valid to pass a tuple of types).

    :param type_: The type to check for.
    :type type_: typing.Any | collections.abc.Sequence[typing.Any]
    :returns: Validator to check value is instance of type
    :rtype: :py:data:`~sphinx_external_toc_strict.util_dc.ValidatorType`
    """

    def _validator(inst: "Any", attr: "dc.Field[Any]", value: UnionAB) -> None:
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, type_):  # type: ignore[arg-type]  # pragma: no branch
            msg_exc = (
                f"'{attr.name}' must be {type_!r} (got {value!r} that "
                f"is a {value.__class__!r})."
            )
            raise TypeError(msg_exc)

    return cast("Callable[[Any, dc.Field[Any], Any | Sequence[Any]], None]", _validator)


def matches_re(regex, flags=0):
    r"""Create a validator fcn for checks against a regex

    When str and regex are a mismatch raises :py:exc:`ValueError`.

    :param regex: a regex string or precompiled pattern to match against
    :type regex: str | re.Pattern
    :param flags:

       Default 0. flags that will be passed to the underlying :py:mod:`re`
       function (default 0)

    :type flags: int
    :returns: An inline function to validate regex
    :rtype: :py:data:`~sphinx_external_toc_strict.util_dc.ValidatorType`
    :raises:

       - :py:exc:`ValueError` -- validator that raises ValueError when
         str arg passed to initializer doesn't match regex

       - :py:exc:`TypeError` -- flags can only be used with a string
         pattern; pass flags to re.compile() instead

    """
    if isinstance(regex, re.Pattern):
        if flags:  # pragma: no branch
            msg_warn = (
                "'flags' can only be used with a string pattern; "
                "pass flags to re.compile() instead"
            )
            raise TypeError(msg_warn)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    match_func = pattern.fullmatch

    def _validator(inst: "Any", attr: "dc.Field[Any]", value: str) -> None:
        """Validate iterable item.

        :param inst: object instance with attribute
        :type inst: typing.Any
        :param attr: A dataclass field
        :type attr: dataclasses.Field[typing.Any]
        :param value: Value to set attribute to
        :type value: sphinx_external_toc_strict.util_dc.UnionAB
        """
        if not match_func(value):  # pragma: no branch
            raise ValueError(
                f"'{attr.name}' must match regex {pattern!r} ({value!r} doesn't)"
            )

    return cast("Callable[[Any, dc.Field[Any], Any, Sequence[Any]], None]", _validator)


def optional(validator):
    """Morphs a validator into an optional (attribute) validator

    A validator that makes an attribute optional.  An optional attribute is one
    which can be set to ``None`` in addition to satisfying the requirements of
    the sub-validator.

    :param validator: An argument validator
    :type validator: collections.abc.Callable[[typing.Any, dataclasses.Field, typing.Any], None]
    :returns: An inline function optional (attribute) validator
    :rtype: collections.abc.Callable[[typing.Any, dataclasses.Field, typing.Any], None]
    """

    def _validator(inst: "Any", attr: "dc.Field[Any]", value: UnionAB) -> None:
        """Validate iterable item.

        :param inst: object instance with attribute
        :type inst: typing.Any
        :param attr: A dataclass field
        :type attr: dataclasses.Field[typing.Any]
        :param value: Value to set attribute to
        :type value: sphinx_external_toc_strict.util_dc.UnionAB
        """
        if value is None:  # pragma: no branch
            return

        validator(inst, attr, value)

    return cast("Callable[[Any, dc.Field[Any], Any, Sequence[Any]], None]", _validator)


def deep_iterable(
    member_validator,
    iterable_validator=None,
):
    """A validator that performs deep validation of an iterable.

    :param member_validator: Validator to apply to iterable members
    :type member_validator: :py:class:`sphinx_external_toc_strict.util_dc.ValidatorType`
    :param iterable_validator: Default None. Validator to apply to iterable itself
    :type iterable_validator: :py:class:`sphinx_external_toc_strict.util_dc.ValidatorType` | None
    :returns: Iterator which validates members
    :rtype: :py:class:`sphinx_external_toc_strict.util_dc.ValidatorType`
    """

    def _validator(inst: "Any", attr: "dc.Field[Any]", value: UnionAB) -> None:
        """Validate iterable item.

        :param inst: object instance with attribute
        :type inst: typing.Any
        :param attr: A dataclass field
        :type attr: dataclasses.Field[typing.Any]
        :param value: Value to set attribute to
        :type value: sphinx_external_toc_strict.util_dc.UnionAB
        """
        if iterable_validator is not None:  # pragma: no branch
            iterable_validator(inst, attr, value)

        for member in value:
            member_validator(inst, attr, member)

    return cast("Callable[[Any, dc.Field[Any], Any, Sequence[Any]], None]", _validator)


# Docutils compatibility


def findall(node):
    """findall replaces traverse in docutils v0.18

    Difference is that findall is an iterator

    Make findall available for all docutils versions

    :param node: A parent tree node
    :type node: docutils.nodes.Element
    :returns: Not sure about signature of node.traverse
    :rtype: collections.abc.Iterator[docutils.nodes.Element]
    """
    return getattr(node, "findall", node.traverse)
