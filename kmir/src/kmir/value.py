from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.prelude.bytes import bytesToken
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
        if len(self.elems) > 0 and all(isinstance(e, IntValue) and not e.signed for e in self.elems):
            int_vals = [e for e in self.elems if isinstance(e, IntValue)]
            bit_width = int_vals[0].nbits
            if (
                bit_width % 8 == 0
                and all(e.nbits == bit_width for e in int_vals)
                and all(0 <= e.value and e.value < 2**bit_width for e in int_vals)
            ):
                byte_width = int(bit_width / 8)
                fmts = {1: '<B', 2: '<H', 4: '<I', 8: '<Q'}
                if byte_width in fmts:
                    b_val = b''.join(struct.pack(fmts[byte_width], e.value) for e in int_vals)
                    return KApply(
                        'Value::RangeInteger',
                        intToken(len(int_vals)),
                        intToken(bit_width),
                        boolToken(False),
                        bytesToken(b_val),
                    )
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
