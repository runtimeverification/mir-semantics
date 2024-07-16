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


def maybe_byte_from_dict(js: int | None) -> KApply:
    if js is None:
        return KApply('noByte', ())

    return KApply('someByte', (KToken(str(js), KSort('Int'))))


def bytes_from_dict(js: Sequence[int]) -> KApply:
    if len(js) == 0:
        return KApply('.maybeBytes', ())

    return KApply('maybeBytes', (maybe_byte_from_dict(js[0]), bytes_from_dict(js[1:])))


def provenance_map_entry_from_dict(js: Sequence[object]) -> KApply:
    match js:
        case [int(size), [int(_), int(allocid)]]:
            return KApply(
                'provenanceMapEntry',
                KToken(str(size), KSort('Int')),
                KApply('allocId', KToken(str(allocid), KSort('Int'))),
            )

    _unimplemented()


def provenance_map_entries_from_dict(js: Sequence[Sequence[object]]) -> KApply:
    if len(js) == 0:
        return KApply('.provenanceMapEntries')

    return KApply(
        'provenanceMapEntries', (provenance_map_entry_from_dict(js[0]), provenance_map_entries_from_dict(js[1:]))
    )


def provenance_map_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'ptrs': list(ptrs)}:
            return KApply('provenanceMap', provenance_map_entries_from_dict(ptrs))

    _raise_conversion_error('')


def align_from_dict(n: int) -> KApply:
    return KApply('align', (KToken(str(n), KSort('Int'))))


def allocation_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'bytes': list(bs), 'provenance': dict(provenance), 'align': int(align), 'mutability': str(mutability)}:
            return KApply(
                'allocation',
                (
                    bytes_from_dict(bs),
                    provenance_map_from_dict(provenance),
                    align_from_dict(align),
                    mutability_from_dict(mutability),
                ),
            )

    _raise_conversion_error('')


def constant_kind_from_dict(js: str | Mapping[str, object]) -> KApply:
    if isinstance(js, str):
        if js == 'ZeroSized':
            return KApply('constantKindZeroSized_TYPES_ConstantKind', ())
        else:
            _raise_conversion_error('')
    else:
        match js:
            case {'Allocated': dict(payload)}:
                return KApply(
                    'constantKindAllocated(_)_TYPES_ConstantKind_Allocation',
                    args=[allocation_from_dict(payload)],
                )

        _raise_conversion_error('')


def mirconstid_from_dict(n: int) -> KApply:
    return KApply('mirConstId(_)_TYPES_MirConstId_Int', (KToken(str(n), KSort('Int'))))


def mirconst_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'kind': str() | dict() as kind, 'ty': int(ty), 'id': int(id_)}:
            return KApply(
                'mirConst(_,_,_)_TYPES_MirConst_ConstantKind_Ty_MirConstId',
                (constant_kind_from_dict(kind), ty_from_dict(ty), mirconstid_from_dict(id_)),
            )

    _raise_conversion_error('')


def maybe_user_type_annotation_index_from_dict(js: Mapping[str, object] | None) -> KApply:
    if js is None:
        return KApply('noUserTypeAnnotationIndex_BODY_MaybeUserTypeAnnotationIndex', ())

    _unimplemented()


def const_operand_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'span': int(span), 'user_ty': dict() | None as user_ty, 'const_': dict(literal)}:
            return KApply(
                'constOperand(_,_,_)_BODY_ConstOperand_Span_MaybeUserTypeAnnotationIndex_MirConst',
                (
                    span_from_dict(span),
                    maybe_user_type_annotation_index_from_dict(user_ty),
                    mirconst_from_dict(literal),
                ),
            )

    _raise_conversion_error('')


def operand_from_dict(js: Mapping[str, object]) -> KApply:
    if len(js) != 1:
        _raise_conversion_error('')

    match js:
        case {'Constant': dict(constant)}:
            return KApply('operandConstant', (const_operand_from_dict(constant)))
        case {'Copy': dict(place)}:
            return KApply('operandCopy', (place_from_dict(place)))
        case {'Move': dict(place)}:
            return KApply('operandMove', (place_from_dict(place)))
        case _:
            _unimplemented()


def operands_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_Operands_Operand_Operands"}_Operands', ())

    return KApply('___BODY_Operands_Operand_Operands', (operand_from_dict(js[0]), operands_from_dict(js[1:])))


def local_from_dict(n: int) -> KApply:
    return KApply('local(_)_BODY_Local_Int', (KToken(str(n), KSort('Int'))))


def projection_elems_from_dict(js: Sequence[Any]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_ProjectionElems_ProjectionElem_ProjectionElems"}_ProjectionElems', ())

    _unimplemented()  # TODO: define projection_elem and apply as to other list sorts_from_dict


def place_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'local': int(local), 'projection': list(projection)}:
            return KApply(
                'place(_,_)_BODY_Place_Local_ProjectionElems',
                (local_from_dict(local), projection_elems_from_dict(projection)),
            )

    _raise_conversion_error('')


def maybe_basicblock_idx_from_dict(js: int | None) -> KApply:
    if js is None:
        return KApply('noBasicBlockIdx_BODY_MaybeBasicBlockIdx', ())

    _unimplemented()


def unwind_action_from_dict(js: str) -> KApply:
    if js == 'Continue':
        return KApply('unwindActionContinue_BODY_UnwindAction', ())
    if js == 'Unreachable':
        return KApply('unwindActionUnreachable_BODY_UnwindAction', ())

    _unimplemented()


def terminator_kind_from_dict(js: str | Mapping[str, object]) -> KApply:
    if isinstance(js, str):
        if js == 'Return':
            return KApply('terminatorKindReturn', ())
        _unimplemented()
    else:
        if len(js) != 1:
            _raise_conversion_error('')
        match js:
            case {'Call': dict(call)}:
                return KApply(
                    'terminatorKindCall',
                    (
                        operand_from_dict(call['func']),
                        operands_from_dict(call['args']),
                        place_from_dict(call['destination']),
                        maybe_basicblock_idx_from_dict(call['target']),
                        unwind_action_from_dict(call['unwind']),
                    ),
                )
            case _:
                _unimplemented()


def terminator_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'kind': str() | dict() as kind, 'span': int(span)}:
            return KApply(
                'terminator(_,_)_BODY_Terminator_TerminatorKind_Span',
                (terminator_kind_from_dict(kind), span_from_dict(span)),
            )

    _raise_conversion_error('')


def statement_kind_from_dict(js: str | Mapping[str, object]) -> KApply:
    if isinstance(js, str):
        _unimplemented()
    else:
        match js:
            case {'Assign': dict()}:
                _unimplemented()
            case {'StorageLive': int(local)}:
                return KApply('statementKindStorageLive', (local_from_dict(local)))
            case {'StorageDead': int(local)}:
                return KApply('statementKindStorageLive', (local_from_dict(local)))
            case _:
                _unimplemented()


def statement_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'kind': str() | dict() as kind, 'span': int(span)}:
            return KApply(
                'statement(_,_)_BODY_Serminator_StatementKind_Span',
                (statement_kind_from_dict(kind), span_from_dict(span)),
            )
    _raise_conversion_error('')


def statements_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_Statements_Statement_Statements"}_Statements', ())

    return KApply('___BODY_Statements_Statement_Statements', (statement_from_dict(js[0]), statements_from_dict(js[1:])))


def basicblock_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'statements': list(statements), 'terminator': dict(terminator)}:
            return KApply(
                'basicBlock(_,_)_BODY_BasicBlock_Statements_Terminator',
                (statements_from_dict(statements), terminator_from_dict(terminator)),
            )

    _raise_conversion_error('')


def basicblocks_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_BasicBlocks_BasicBlock_BasicBlocks"}_BasicBlocks', ())

    return KApply(
        '___BODY_BasicBlocks_BasicBlock_BasicBlocks', (basicblock_from_dict(js[0]), basicblocks_from_dict(js[1:]))
    )


def ty_from_dict(n: int) -> KApply:
    return KApply('ty', (KToken(str(n), KSort('Int'))))


def mutability_from_dict(s: str) -> KApply:
    return KApply(f'mutability{s.capitalize()}_BODY_Mutability', ())


def localdecl_from_dict(js: Mapping[str, object]) -> KInner:
    match js:
        case {'ty': int(ty), 'span': int(span), 'mutability': str(mutability)}:
            return KApply(
                'localDecl(_,_,_)_BODY_LocalDecl_Ty_Span_Mutability',
                (ty_from_dict(ty), span_from_dict(span), mutability_from_dict(mutability)),
            )

    _raise_conversion_error('')


def localdecls_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.List{"___BODY_LocalDecls_LocalDecl_LocalDecls"}_LocalDecls', ())

    return KApply('___BODY_LocalDecls_LocalDecl_LocalDecls', (localdecl_from_dict(js[0]), localdecls_from_dict(js[1:])))


def arg_count_from_dict(n: int) -> KToken:
    return KToken(str(n), KSort('Int'))


def var_debug_infos_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    # Ignore var_debug_info for now
    return KApply('.List{"___BODY_VarDebugInfos_VarDebugInfo_VarDebugInfos"}_VarDebugInfos', ())


def maybe_local_from_dict(js: int | Mapping[str, object] | None) -> KApply:
    match js:
        case None:
            return KApply('noLocal_BODY_MaybeLocal', ())
        case _:
            _unimplemented()


def span_from_dict(n: int) -> KApply:
    return KApply('span(_)_TYPES_Span_Int', (KToken(str(n), KSort('Int'))))


def global_alloc_from_dict(js: tuple[int, Mapping[str, object]]) -> KApply:
    match js:
        case [int(n), {'Memory': dict(allocation)}]:
            return KApply(
                'globalAllocEntry',
                (KToken(str(n), KSort('Int')), KApply('globalAllocMemory', (allocation_from_dict(allocation)))),
            )
        case [int(n), {'Static': int(s)}]:
            return KApply(
                'globalAllocEntry',
                (KToken(str(n), KSort('Int')), KApply('globalAllocStatic', (KToken(str(s), KSort('Int'))))),
            )
        case _:
            _unimplemented()


def global_allocs_from_dict(js: Sequence[tuple[int, Mapping[str, object]]]) -> KApply:
    if len(js) == 0:
        return KApply('.globalAllocsMap')

    return KApply('globalAllocsMap', (global_alloc_from_dict(js[0]), global_allocs_from_dict(js[1:])))


def body_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {
            'blocks': list(blocks),
            'locals': list(locals),
            'arg_count': int(arg_count),
            'var_debug_info': list(var_debug_infos),
            'spread_arg': int(_) | None as spread_arg,
            'span': int(span),
        }:
            return KApply(
                'body(_,_,_,_,_,_)_BODY_Body_BasicBlocks_LocalDecls_Int_VarDebugInfos_MaybeLocal_Span',
                (
                    basicblocks_from_dict(blocks),
                    localdecls_from_dict(locals),
                    arg_count_from_dict(arg_count),
                    var_debug_infos_from_dict(var_debug_infos),
                    maybe_local_from_dict(spread_arg),
                    span_from_dict(span),
                ),
            )

    _raise_conversion_error('')


def defid_from_dict(n: int) -> KApply:
    #    return KApply('defId', (KApply('opaque', (KToken('\"' + str(n) + '\"', KSort('String'))))))
    return KApply('defId', (KToken('\"' + str(n) + '\"', KSort('String'))))


def item_kind_from_dict(js: str) -> KApply:
    if js == 'Fn':
        return KApply('itemKindFn', ())
    if js == 'Static':
        return KApply('itemKindStatic', ())
    if js == 'Const':
        return KApply('itemKindConst', ())

    _unimplemented()


def maybe_item_kind_from_dict(js: str) -> KApply:
    if js == 'Fn':
        return KApply('someItemKind', KApply('itemKindFn', ()))
    if js == 'Static':
        return KApply('someItemKind', KApply('itemKindStatic', ()))
    if js == 'Const':
        return KApply('someItemKind', KApply('itemKindConst', ()))
    if js == '':
        return KApply('noItemKind', ())

    _unimplemented()


def instance_kind_from_dict(js: str) -> KApply:
    if js == 'Item':
        return KApply('instanceKindItem', ())
    _unimplemented()


def bodies_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.bodies')

    return KApply('bodies', (body_from_dict(js[0]), bodies_from_dict(js[1:])))


def string_from_dict(js: str) -> KToken:
    return KToken('\"' + js + '\"', KSort('String'))


def mono_item_fn_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {
            'name': str(name),
            'id': int(id),
            'instance_kind': str(instance_kind),
            'item_kind': str(item_kind),
            'body': [dict(body), None],
            'promoted': list(promoted),
        }:
            return KApply(
                'monoItemFn',
                (
                    string_from_dict(name),
                    defid_from_dict(id),
                    instance_kind_from_dict(instance_kind),
                    maybe_item_kind_from_dict(item_kind),
                    body_from_dict(body),
                    bodies_from_dict(promoted),
                ),
            )

    _raise_conversion_error('')


def mono_item_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {'MonoItemFn': dict(payload)}:
            return mono_item_fn_from_dict(payload)
        case {'MonoItemStatic': dict()}:
            _unimplemented()
        case {'MonoItemGlobalAsm': dict()}:
            _unimplemented()
    _raise_conversion_error('')


def mono_item_wrapper_from_dict(js: Mapping[str, object]) -> KApply:
    match js:
        case {
            'symbol_name': str(name),
            'mono_item_kind': dict(mono_item),
            'details': str(_) | None,
        }:
            return KApply(
                'monoItemWrapper',
                (
                    string_from_dict(name),
                    mono_item_from_dict(mono_item),
                ),
            )

    _raise_conversion_error('')


def mono_items_from_dict(js: Sequence[Mapping[str, object]]) -> KApply:
    if len(js) == 0:
        return KApply('.monoItems')

    return KApply('monoItems', (mono_item_wrapper_from_dict(js[0]), mono_items_from_dict(js[1:])))


def function_map_entry_from_dict(js: tuple[int, str]) -> KApply:
    match js:
        case [int(n), str(s)]:
            return KApply(
                'functionMapEntry',
                (KToken(str(n), KSort('Int')), string_from_dict(s)),
            )
    _raise_conversion_error('')


def functions_map_from_dict(js: Sequence[tuple[int, str]]) -> KApply:
    if len(js) == 0:
        return KApply('.functionsMap')

    return KApply('functionsMap', (function_map_entry_from_dict(js[0]), functions_map_from_dict(js[1:])))


def types_map_from_dict(js: Sequence[tuple[int, Mapping[str, object]]]) -> KApply:
    # We ignore the types map for now
    return KApply('.tysMap', ())


def from_dict(js: Mapping[str, object]) -> KInner:
    match js:
        case {
            'name': str(name),
            'items': list(items),
            'crate_functions': list(crate_functions),
            'allocs': list(allocs),
            'types': list(types),
        }:
            return KApply(
                'pgm',
                (
                    string_from_dict(name),
                    mono_items_from_dict(items),
                    functions_map_from_dict(crate_functions),
                    global_allocs_from_dict(allocs),
                    types_map_from_dict(types),
                ),
            )

    _raise_conversion_error('')
