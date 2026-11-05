import dataclasses as dc
import re
from collections.abc import (
    Callable,
    Sequence,
)
from typing import (
    Any,
    TypeAlias,
    TypeGuard,
)

from docutils.nodes import Element

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

DC_SLOTS: dict[str, bool]
UnionAB: TypeAlias = Any | Sequence[Any]
ValidatorType: TypeAlias = Callable[[Any, dc.Field[Any], UnionAB], None]

def deep_iterable(
    member_validator: ValidatorType,
    iterable_validator: ValidatorType | None = None,
) -> ValidatorType: ...
def field(**kwargs: Any) -> Any: ...
def findall(node: Element) -> Any: ...
def instance_of(type_: UnionAB) -> ValidatorType: ...
def is_dataclass_instance(obj: object) -> TypeGuard[object]: ...
def matches_re(regex: str | re.Pattern[str], flags: int = 0) -> ValidatorType: ...
def optional(validator: ValidatorType) -> ValidatorType: ...
def validate_fields(inst: object) -> None: ...
