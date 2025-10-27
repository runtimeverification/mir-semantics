from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.prelude.collections import list_of
from pyk.kast.prelude.kbool import boolToken
from pyk.kast.prelude.kint import intToken
from pyk.kast.prelude.string import stringToken

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
class StrValue(Value):
    value: str

    def to_kast(self) -> KInner:
        return KApply(
            'Value::StringVal',
            stringToken(self.value),
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


@dataclass
class Metadata:
    size: MetadataSize
    pointer_offset: int
    origin_size: MetadataSize

    def to_kast(self) -> KInner:
        return KApply(
            'Metadata',
            self.size.to_kast(),
            intToken(self.pointer_offset),
            self.origin_size.to_kast(),
        )


class MetadataSize(ABC):
    @abstractmethod
    def to_kast(self) -> KInner: ...


@dataclass
class NoSize(MetadataSize):
    def to_kast(self) -> KInner:
        return KApply('noMetadataSize')


NO_SIZE: Final = NoSize()


@dataclass
class StaticSize(MetadataSize):
    size: int

    def to_kast(self) -> KInner:
        return KApply('staticSize', intToken(self.size))


@dataclass
class DynamicSize(MetadataSize):
    size: int

    def to_kast(self) -> KInner:
        return KApply('dynamicSize', intToken(self.size))
