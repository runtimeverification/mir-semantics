from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast import KInner


class Value(ABC):
    @abstractmethod
    def to_kast(self) -> KInner: ...


@dataclass
class BoolValue(Value):
    value: bool

    def to_kast(self):
        from pyk.kast.prelude.kbool import boolToken

        return KApply('Value::BoolVal', boolToken(self.value))


@dataclass
class IntValue(Value):
    value: int
    nbits: int
    signed: bool

    def to_kast(self):
        from pyk.kast.prelude.kbool import boolToken
        from pyk.kast.prelude.kint import intToken

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

    def to_kast(self):
        from pyk.kast.prelude.collections import list_of

        return KApply('Value::Range', list_of(elem.to_kast() for elem in self.elems))
