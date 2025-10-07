from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.prelude.collections import list_of
from pyk.kast.prelude.kbool import boolToken
from pyk.kast.prelude.kint import intToken

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Final

    from pyk.kast import KInner

    from .alloc import AllocId


class Value(ABC):
    @abstractmethod
    def to_kast(self) -> KInner: ...


@dataclass
class BoolValue(Value):
    value: bool

    def to_kast(self) -> KInner:
        return KApply('Value::BoolVal', boolToken(self.value))


@dataclass
class IntValue(Value):
    value: int
    nbits: int
    signed: bool

    def to_kast(self) -> KInner:
        return KApply(
            'Value::Integer',
            intToken(self.value),
            intToken(self.nbits),
            boolToken(self.signed),
        )


@dataclass
class RangeValue(Value):
    elems: tuple[Value, ...]

    def __init__(self, elems: Iterable[Value]):
        self.elems = tuple(elems)

    def to_kast(self) -> KInner:
        return KApply('Value::Range', list_of(elem.to_kast() for elem in self.elems))


@dataclass
class AggregateValue(Value):
    variant_idx: int
    fields: tuple[Value, ...]

    def __init__(self, variant_idx: int, fields: Iterable[Value]):
        self.variant_idx = variant_idx
        self.fields = tuple(fields)

    def to_kast(self) -> KInner:
        return KApply(
            'Value::Aggregate',
            KApply('variantIdx', intToken(self.variant_idx)),
            list_of(field.to_kast() for field in self.fields),
        )


@dataclass
class AllocRefValue(Value):
    alloc_id: AllocId
    # projection_elems: tuple[ProjectionElem, ...]
    metadata: Metadata

    def to_kast(self) -> KInner:
        return KApply(
            'Value::AllocRef',
            KApply('allocId', intToken(self.alloc_id)),
            KApply('ProjectionElems::empty'),  # TODO
            self.metadata.to_kast(),
        )


class Metadata(ABC):
    @abstractmethod
    def to_kast(self) -> KInner: ...


@dataclass
class NoMetadata(Metadata):
    def to_kast(self) -> KInner:
        return KApply('noMetadata')


NO_METADATA: Final = NoMetadata()


@dataclass
class StaticSize(Metadata):
    size: int

    def to_kast(self) -> KInner:
        return KApply('staticSize', intToken(self.size))


@dataclass
class DynamicSize(Metadata):
    size: int

    def to_kast(self) -> KInner:
        return KApply('dynamicSize', intToken(self.size))
