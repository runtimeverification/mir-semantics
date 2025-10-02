from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply

if TYPE_CHECKING:
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
