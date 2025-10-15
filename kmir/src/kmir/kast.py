from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

from pyk.kast.inner import KApply, KVariable, build_cons
from pyk.kast.prelude.collections import list_of
from pyk.kast.prelude.kint import eqInt, leInt
from pyk.kast.prelude.ml import mlEqualsTrue
from pyk.kast.prelude.utils import token

from .ty import ArrayT, Bool, EnumT, Int, PtrT, RefT, StructT, TupleT, Uint, UnionT

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast.inner import KInner

    from .smir import SMIRInfo

_LOGGER: Final = logging.getLogger(__name__)


def int_var(var: KVariable, num_bytes: int, signed: bool) -> tuple[KInner, Iterable[KInner]]:
    bit_width = num_bytes * 8
    var_max = ((1 << (bit_width - 1)) if signed else (1 << bit_width)) - 1
    var_min = -(1 << (bit_width - 1)) if signed else 0
    constraints = (mlEqualsTrue(leInt(var, token(var_max))), mlEqualsTrue(leInt(token(var_min), var)))
    term = KApply('Value::Integer', (var, token(bit_width), token(signed)))
    return term, constraints


def bool_var(var: KVariable) -> tuple[KInner, Iterable[KInner]]:
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

    args = build_cons(KApply('Operands::empty', ()), 'Operands::append', operands)

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


def _typed_value(value: KInner, ty: int, mutable: bool) -> KInner:
    return KApply(
        'typedValue',
        (value, KApply('ty', (token(ty),)), KApply('Mutability::Mut' if mutable else 'Mutability::Not', ())),
    )


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
        for ty, mut in [(t['ty'], t['mutability']) for t in local_types]:
            self._add_local(ty, mut == 'Mut')
        return (self.locals + self.pointees, self.constraints)

    def _add_local(self, ty: Ty, mutable: bool) -> None:
        value, constraints, _ = self._symbolic_value(ty, mutable)

        self.locals.append(_typed_value(value, ty, mutable))
        self.constraints += constraints

    def _fresh_var(self, prefix: str) -> KVariable:
        name = prefix + str(self.counter)
        self.counter += 1
        return KVariable(name)

    def _symbolic_value(self, ty: Ty, mutable: bool) -> tuple[KInner, Iterable[KInner], KInner | None]:
        # returns: symbolic value of given type, related constraints, related pointer metadata
        match self.smir_info.types.get(ty):
            case Int(info):
                val, constraints = int_var(self._fresh_var('ARG_INT'), info.value, True)
                return val, constraints, None

            case Uint(info):
                val, constraints = int_var(self._fresh_var('ARG_UINT'), info.value, False)
                return val, constraints, None

            case Bool():
                val, constraints = bool_var(self._fresh_var('ARG_BOOL'))
                return val, constraints, None

            case EnumT(_, _, discriminants):
                variant_var = self._fresh_var('ARG_VARIDX')
                # constraints for variant index being in range
                max_variant = len(discriminants)
                idx_range = [
                    mlEqualsTrue(leInt(token(0), variant_var)),
                    mlEqualsTrue(leInt(variant_var, token(max_variant))),
                ]
                args = self._fresh_var('ENUM_ARGS')
                return KApply('Value::Aggregate', (KApply('variantIdx', (variant_var,)), args)), idx_range, None

            case StructT(_, _, fields):
                field_vars: list[KInner] = []
                field_constraints: list[KInner] = []
                for _ty in fields:
                    new_var, new_constraints, _ = self._symbolic_value(_ty, mutable)
                    field_vars.append(new_var)
                    field_constraints += new_constraints
                return (
                    KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), list_of(field_vars))),
                    field_constraints,
                    None,
                )

            case UnionT():
                args = self._fresh_var('ARG_UNION')
                return KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), args)), [], None

            case ArrayT(_, None):
                elems = self._fresh_var('ARG_ARRAY')
                l = self._fresh_var('ARG_ARRAY_LEN')
                return (
                    KApply('Value::Range', (elems,)),
                    [mlEqualsTrue(eqInt(KApply('sizeList', (elems,)), l))],
                    KApply('dynamicSize', (l,)),
                )

            case ArrayT(element_type, size) if size is not None:
                elem_vars: list[KInner] = []
                elem_constraints: list[KInner] = []
                for _ in range(size):
                    new_var, new_constraints, _ = self._symbolic_value(element_type, mutable)
                    elem_vars.append(new_var)
                    elem_constraints += new_constraints
                return (
                    KApply('Value::Range', (list_of(elem_vars),)),
                    elem_constraints,
                    KApply('staticSize', (token(size),)),
                )

            case TupleT(components):
                elem_vars = []
                elem_constraints = []
                for _ty in components:
                    new_var, new_constraints, _ = self._symbolic_value(_ty, mutable)
                    elem_vars.append(new_var)
                    elem_constraints += new_constraints
                return (
                    KApply('Value::Aggregate', (KApply('variantIdx', (token(0),)), list_of(elem_vars))),
                    elem_constraints,
                    None,
                )

            case RefT(pointee_ty):
                pointee_var, pointee_constraints, metadata = self._symbolic_value(pointee_ty, mutable)
                ref = self.ref_offset
                self.ref_offset += 1
                self.pointees.append(_typed_value(pointee_var, pointee_ty, mutable))
                return (
                    KApply(
                        'Value::Reference',
                        (
                            token(0), # Stack OFFSET field
                            KApply('place', (KApply('local', (token(ref),)), KApply('ProjectionElems::empty', ()))),
                            KApply('Mutability::Mut', ()) if mutable else KApply('Mutability::Not', ()),
                            metadata if metadata is not None else KApply('noMetadata', ()),
                            token(0),  # PTR_OFFSET field
                        ),
                    ),
                    pointee_constraints,
                    None,
                )
            case PtrT(pointee_ty):
                pointee_var, pointee_constraints, metadata = self._symbolic_value(pointee_ty, mutable)
                ref = self.ref_offset
                self.ref_offset += 1
                self.pointees.append(_typed_value(pointee_var, pointee_ty, mutable))
                return (
                    KApply(
                        'Value::PtrLocal',
                        (
                            token(0),
                            KApply('place', (KApply('local', (token(ref),)), KApply('ProjectionElems::empty', ()))),
                            KApply('Mutability::Mut', ()) if mutable else KApply('Mutability::Not', ()),
                            KApply('PtrEmulation', (metadata if metadata is not None else KApply('noMetadata', ()), token(0), KApply('Value::NoOrigin', ()))),
                        ),
                    ),
                    pointee_constraints,
                    None,
                )
            case other:
                _LOGGER.warning(f'Missing type information ({other}) for type {ty}')
                # missing type information, but can assert that this is a value
                var = self._fresh_var('ARG')
                return var, [mlEqualsTrue(KApply('isValue', (var,)))], None
