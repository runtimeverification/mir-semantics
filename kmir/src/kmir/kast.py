from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KVariable
from pyk.kast.prelude.kint import leInt
from pyk.kast.prelude.utils import token

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast.inner import KInner


def int_var(varname: str, num_bytes: int, signed: bool) -> tuple[KInner, Iterable[KInner]]:
    var = KVariable(varname, 'Int')
    bit_width = num_bytes * 8
    var_max = ((1 << (bit_width - 1)) if signed else (1 << bit_width)) - 1
    var_min = -(1 << (bit_width - 1)) if signed else 0
    constraints = (leInt(var, token(var_max)), leInt(token(var_min), var))
    term = KApply('Value::Integer', (var, token(bit_width), token(signed)))
    return term, constraints


def bool_var(varname: str) -> tuple[KInner, Iterable[KInner]]:
    var = KVariable(varname, 'Bool')
    term = KApply('Value::Bool', (var,))
    return term, ()
