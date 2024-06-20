from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, NoReturn
    from collections.abc import Sequence, Mapping
    from pyk.kast.inner import KInner

from pyk.kast.inner import KApply, KSort, KToken


def _raise_conversion_error(msg: str) -> NoReturn:
    raise AssertionError(msg)


def _unimplemented() -> NoReturn:
    raise NotImplementedError()


def from_json_maybe_byte(js: int | None) -> KApply:
    if js is None:
        return KApply('noByte_BODY_MaybeByte', ())

    return KApply('someByte(_)_TYPES_MaybeByte_Int', (KToken(str(js), KSort('Int'))))


def from_json_bytes(js: Sequence[int]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___TYPES_Bytes_MaybeByte_Bytes"}_Bytes', ())

    return KApply('___TYPES_Bytes_MaybeByte_Bytes', (from_json_maybe_byte(js[0]), from_json_bytes(js[1:])))


def from_json_provenance_map(js: Mapping[str, Any]) -> KApply:
    return KApply('DraftProvenanceMap', ())


def from_json_align(n: int) -> KApply:
    return KApply('align(_)_TYPES_Align_Int', (KToken(str(n), KSort('Int'))))


def from_json_allocation(js: Mapping[str, Any]) -> KApply:
    return KApply(
        'allocation(_,_,_,_)_TYPES_Allocation_Bytes_ProvenanceMap_Align_Mutability',
        (
            from_json_bytes(js['bytes']),
            from_json_provenance_map(js['provenance']),
            from_json_align(js['align']),
            from_json_mutability(js['mutability']),
        ),
    )


def from_json_constant_kind(js: str | Mapping[str, Any]) -> KApply:
    if isinstance(js, str):
        if js == 'ZeroSized':
            return KApply('constantKindZeroSized_TYPES_ConstantKind', ())
        else:
            _raise_conversion_error('')
    else:
        match js:
            case {'Allocated': payload}:
                return KApply(
                    'constantKindAllocated(_)_TYPES_ConstantKind_Allocation',
                    (payload),
                )

        _raise_conversion_error('')


def from_json_constid(n: int) -> KApply:
    return KApply('constId(_)_TYPES_ConstId_Int', (KToken(str(n), KSort('Int'))))


def from_json_const(js: Mapping[str, Any]) -> KApply:
    return KApply(
        'const(_,_,_)_TYPES_Const_ConstantKind_Ty_ConstId',
        (from_json_constant_kind(js['kind']), from_json_ty(js['ty']), from_json_constid(js['id'])),
    )


def from_json_maybe_user_type_annotation_index(js: Mapping[str, object] | None) -> KApply:
    if js is None:
        return KApply('noUserTypeAnnotationIndex_BODY_MaybeUserTypeAnnotationIndex', ())

    _unimplemented()


def from_json_constant(js: Mapping[str, Any]) -> KApply:
    match js:
        case {'span': int(span), 'user_ty': dict() | None as user_ty, 'literal': dict(literal)}:
            return KApply(
                'constant(_,_,_)_BODY_Constant_Span_MaybeUserTypeAnnotationIndex_Const',
                (
                    from_json_span(span),
                    from_json_maybe_user_type_annotation_index(user_ty),
                    from_json_const(literal),
                ),
            )

    _raise_conversion_error('')


def from_json_operand(js: Mapping[str, Any]) -> KApply:
    if len(js) != 1:
        _raise_conversion_error('')

    match js:
        case {'Constant': constant}:
            return KApply('operandConstant(_)_BODY_Operand_Constant', (from_json_constant(constant)))
        case _:
            _unimplemented()


def from_json_operands(js: Sequence[Mapping[str, Any]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_Operands_Operand_Operands"}_Operands', ())

    return KApply('___BODY_Operands_Operand_Operands', (from_json_operand(js[0]), from_json_operands(js[1:])))


def from_json_local(n: int) -> KApply:
    return KApply('ilocal(_)_BODY_Local_Int', (KToken(str(n), KSort('Int'))))


def from_json_projection_elems(js: Sequence[Any]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_ProjectionElems_ProjectionElem_ProjectionElems"}_ProjectionElems', ())

    _unimplemented()  # TODO: define from_json_projection_elem and apply as to other list sorts


def from_json_place(js: Mapping[str, Any]) -> KApply:
    return KApply(
        'iplace(_,_)_BODY_Place_Local_ProjectionElems',
        (from_json_local(js['local']), from_json_projection_elems(js['projection'])),
    )


def from_json_maybe_basicblock_idx(js: int | None) -> KApply:
    if js is None:
        return KApply('noBasicBlockIdx_BODY_MaybeBasicBlockIdx', ())

    _unimplemented()


def from_json_unwind_action(js: str) -> KApply:
    if js == 'Continue':
        return KApply('unwindActionContinue_BODY_UnwindAction', ())

    _unimplemented()


def from_json_terminator_kind(js: Mapping[str, Any]) -> KApply:
    if len(js) != 1:
        _raise_conversion_error('')

    match js:
        case {'Call': call}:
            return KApply(
                'terminatorKindCall(_,_,_,_,_)_BODY_TerminatorKindCall_Operand_Operands_Place_MaybeBasicBlockIdx_UnwindAction',
                (
                    from_json_operand(call['func']),
                    from_json_operands(call['args']),
                    from_json_place(call['destination']),
                    from_json_maybe_basicblock_idx(call['target']),
                    from_json_unwind_action(call['unwind']),
                ),
            )

        case _:
            _unimplemented()


def from_json_terminator(js: Mapping[str, Any]) -> KApply:
    return KApply(
        'terminator(_,_)_BODY_Terminator_TerminatorKind_Span',
        (from_json_terminator_kind(js['kind']), from_json_span(js['span'])),
    )


def from_json_statement(js: Mapping[str, Any]) -> KApply:
    _unimplemented()


def from_json_statements(js: Sequence[Mapping[str, Any]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_Statements_Statement_Statements"}_Statements', ())

    return KApply('___BODY_Statements_Statement_Statements', (from_json_statement(js[0]), from_json_statements(js[1:])))


def from_json_basicblock(js: Mapping[str, Any]) -> KApply:
    return KApply(
        'basicBlock(_,_)_BODY_BasicBlock_Statements_Terminator',
        (from_json_statements(js['statements']), from_json_terminator(js['terminator'])),
    )


def from_json_basicblocks(js: Sequence[Mapping[str, Any]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_BasicBlocks_BasicBlock_BasicBlocks"}_BasicBlocks', ())

    return KApply(
        '___BODY_BasicBlocks_BasicBlock_BasicBlocks', (from_json_basicblock(js[0]), from_json_basicblocks(js[1:]))
    )


def from_json_ty(js: Mapping[str, Any]) -> KApply:
    return KApply('ty(_)_TYPES_Ty_Int', (KToken(str(js['id']), KSort('Int'))))


def from_json_mutability(s: str) -> KApply:
    return KApply(f'mutability{s.capitalize()}_BODY_Mutability', ())


def from_json_localdecl(js: Mapping[str, Any]) -> KInner:
    return KApply(
        'localDecl(_,_,_)_BODY_LocalDecl_Ty_Span_Mutability',
        (from_json_ty(js['ty']), from_json_span(js['span']), from_json_mutability(js['mutability'])),
    )


def from_json_localdecls(js: Sequence[Mapping[str, Any]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_LocalDecls_LocalDecl_LocalDecls"}_LocalDecls', ())

    return KApply('___BODY_LocalDecls_LocalDecl_LocalDecls', (from_json_localdecl(js[0]), from_json_localdecls(js[1:])))


def from_json_arg_count(n: int) -> KToken:
    return KToken(str(n), KSort('Int'))


def from_json_var_debug_info(js: Mapping[str, Any]) -> KInner:
    _unimplemented()


def from_json_var_debug_infos(js: Sequence[Mapping[str, Any]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_VarDebugInfos_VarDebugInfo_VarDebugInfos"}_VarDebugInfos', ())

    return KApply(
        '___BODY_VarDebugInfos_VarDebugInfo_VarDebugInfos',
        (from_json_var_debug_info(js[0]), from_json_var_debug_infos(js[1:])),
    )


def from_json_maybe_local(js: int | Mapping[str, Any] | None) -> KApply:
    match js:
        case None:
            return KApply('noLocal_BODY_MaybeLocal', ())
        case _:
            _unimplemented()


def from_json_span(n: int) -> KApply:
    return KApply('span(_)_TYPES_Span_Int', (KToken(str(n), KSort('Int'))))


def from_json(js: Mapping[str, Any]) -> KInner:
    match js:
        case {'body': v}:
            assert len(v) == 2
            assert v[1] == None
            body = v[0]
            blocks = from_json_basicblocks(body['blocks'])
            locals = from_json_localdecls(body['locals'])
            arg_count = from_json_arg_count(body['arg_count'])
            var_debug_infos = from_json_var_debug_infos(body['var_debug_info'])
            spread_arg = from_json_maybe_local(body['spread_arg'])
            span = from_json_span(body['span'])
            return KApply(
                'body(_,_,_,_,_,_)_BODY_Body_BasicBlocks_LocalDecls_Int_VarDebugInfos_MaybeLocal_Span',
                (blocks, locals, arg_count, var_debug_infos, spread_arg, span),
            )
        case _:
            return KToken('Catchall', 'Catchall')
