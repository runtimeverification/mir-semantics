from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KVariable
from pyk.kast.prelude.kint import leInt
from pyk.kast.prelude.utils import token

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast.inner import KInner

    from .smir import SMIRInfo


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
    term = KApply('Value::BoolVal', (var,))
    return term, ()


def mk_call_terminator(target: int, arg_count: int) -> KInner:
    operands = [
        KApply(
            'Operand::Copy',
            (KApply('place', (KApply('local', (token(i + 1),)), KApply('ProjectionElems::empty', ()))),),
        )
        for i in range(arg_count)
    ]

    # args = foldr(Operands::append, Operands::empty, operands)
    args = KApply('Operands::empty', ())
    for op in reversed(operands):
        args = KApply(
            'Operands::append',
            (
                op,
                args,
            ),
        )

    return KApply(
        '#execTerminator(_)_KMIR-CONTROL-FLOW_KItem_Terminator',
        (
            KApply(
                'terminator(_,_)_BODY_Terminator_TerminatorKind_Span',
                (
                    KApply(
                        'TerminatorKind::Call',
                        (
                            KApply(
                                'Operand::Constant',
                                (
                                    KApply(
                                        'constOperand(_,_,_)_BODY_ConstOperand_Span_MaybeUserTypeAnnotationIndex_MirConst',
                                        (
                                            KApply('span', token(0)),
                                            KApply('noUserTypeAnnotationIndex_BODY_MaybeUserTypeAnnotationIndex', ()),
                                            KApply(
                                                'mirConst(_,_,_)_TYPES_MirConst_ConstantKind_Ty_MirConstId',
                                                (
                                                    KApply('ConstantKind::ZeroSized', ()),
                                                    KApply('ty', (token(target),)),
                                                    KApply('mirConstId(_)_TYPES_MirConstId_Int', (token(0),)),
                                                ),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                            args,
                            KApply(
                                'place',
                                (
                                    KApply('local', (token(0),)),
                                    KApply('ProjectionElems::empty', ()),
                                ),
                            ),
                            KApply('noBasicBlockIdx_BODY_MaybeBasicBlockIdx', ()),
                            KApply('UnwindAction::Continue', ()),
                        ),
                    ),
                    KApply('span', token(0)),
                ),
            ),
        ),
    )


def symbolic_locals(smir_info: SMIRInfo, local_types: list[dict]) -> tuple[list[KInner], list[KInner]]:
    locals, constraints = ArgGenerator(smir_info).run(local_types)
    local0 = KApply('newLocal', (KApply('ty', (token(0),)), KApply('Mutability::Not', ())))
    return ([local0] + locals, constraints)


class ArgGenerator:
    smir_info: SMIRInfo
    locals: list[KInner]
    pointees: list[KInner]
    constraints: list[KInner]
    counter: int
    ref_offset: int

    if TYPE_CHECKING:
        from .smir import Ty

    def __init__(self, smir_info: SMIRInfo) -> None:
        self.smir_info = smir_info
        self.locals = []
        self.pointees = []
        self.constraints = []
        self.counter = 1
        self.ref_offset = 0

    def run(self, local_types: list[dict]) -> tuple[list[KInner], list[KInner]]:
        self.ref_offset = len(local_types) + 1
        for ty in [t['ty'] for t in local_types]:
            self._add_local(ty)
        return (self.locals + self.pointees, self.constraints)

    def _add_local(self, ty: Ty) -> None:
        match self.smir_info.types.get(ty):
            case _:
                new = KApply(
                    'typedValue', (self._fresh_var('ARG'), KApply('ty', (token(ty),)), KApply('Mutability::Not', ()))
                )
                self.locals.append(new)

    def _fresh_var(self, prefix: str) -> KInner:
        name = prefix + str(self.counter)
        self.counter += 1
        return KVariable(name)
