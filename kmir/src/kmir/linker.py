from __future__ import annotations

import logging
from math import ceil, log10
from typing import TYPE_CHECKING

from .smir import SMIRInfo

if TYPE_CHECKING:
    from typing import Final

_LOGGER: Final = logging.getLogger(__name__)


def link(smirs: list[SMIRInfo]) -> SMIRInfo:
    max_id_range = max(map(id_range, smirs))
    # round up to nearest power of 10
    offset = 10 ** (ceil(log10(max_id_range)))

    _LOGGER.info(f'Maximum type ID (offset) is {offset}, linking {len(smirs)} smir.json files')

    for smir, offset in zip(smirs, [offset * i for i in range(len(smirs))], strict=True):
        _LOGGER.debug(f'Offset {offset} for smir {smir._smir["name"]}')
        apply_offset(smir, offset)

    result_dict = {
        'name': ','.join([smir._smir['name'] for smir in smirs]),
        'crate_id': 0,  # HACK
        'allocs': [a for smir in smirs for a in smir._smir['allocs']],
        'functions': [f for smir in smirs for f in smir._smir['functions']],
        'items': [i for smir in smirs for i in smir._smir['items']],
        'types': [t for smir in smirs for t in smir._smir['types']],
        'spans': [s for smir in smirs for s in smir._smir['spans']],
        'machine': smirs[0]._smir['machine'],
        # debug and uneval_constants are omitted in the linked output
    }
    return SMIRInfo(result_dict)


def id_range(smir: SMIRInfo) -> int:
    f_max = max([0] + list(smir.function_symbols.keys()))
    ty_max = max([0] + list(smir.types.keys()))
    span_range = max([0] + list(smir.spans.keys()))
    return max(f_max, ty_max, span_range)


def apply_offset(info: SMIRInfo, offset: int) -> None:
    # mutates the dictionary inside the SMIRInfo
    # all fields containing a `Ty` are updated, adding the given offset
    dic = info._smir
    ts = dic['types']

    _LOGGER.debug(f'Applying offset {offset} to smir {dic["name"]}, with {len(ts)} types')

    info._smir['functions'] = [(ty + offset, sym) for ty, sym in info._smir['functions']]
    info._smir['types'] = [
        (ty + offset, apply_offset_typeInfo(typeInfo, offset)) for ty, typeInfo in info._smir['types']
    ]
    info._smir['spans'] = [(i + offset, span) for i, span in info._smir['spans']]

    # TODO adjust all alloc IDs (incl. alloc provenance)
    # TODO then adjust alloc references during item traversal

    # traverse item bodies and replace all `ty` fields
    for item in info._smir['items']:
        apply_offset_item(item['mono_item_kind'], offset)


def apply_offset_typeInfo(typeinfo: dict, offset: int) -> dict:
    # traverses type information, updating all `Ty`-valued fields and `adt_def` fields within
    # returns the updated (i.e., mutated) `typeinfo`` dictionary
    # 'PrimitiveType' in typeinfo:
    if 'EnumType' in typeinfo:
        typeinfo['EnumType']['adt_def'] = typeinfo['EnumType']['adt_def'] + offset
    elif 'StructType' in typeinfo:
        typeinfo['StructType']['fields'] = [x + offset for x in typeinfo['StructType']['fields']]
        typeinfo['StructType']['adt_def'] = typeinfo['StructType']['adt_def'] + offset
    elif 'UnionType' in typeinfo:
        typeinfo['UnionType']['adt_def'] = typeinfo['UnionType']['adt_def'] + offset
    elif 'ArrayType' in typeinfo:
        assert isinstance(typeinfo['ArrayType'], list)
        typeinfo['ArrayType'][0] = typeinfo['ArrayType'][0] + offset
    elif 'PtrType' in typeinfo:
        typeinfo['PtrType'] = typeinfo['PtrType'] + offset
    elif 'RefType' in typeinfo:
        typeinfo['RefType'] = typeinfo['RefType'] + offset
    elif 'TupleType' in typeinfo:
        typeinfo['TupleType']['types'] = [x + offset for x in typeinfo['TupleType']['types']]
    # 'FunType' in typeinfo:

    return typeinfo


def apply_offset_item(item: dict, offset: int) -> None:
    # Operating on MonoItemFn (MonoItemStatic and GlobalAsm do not contain any `Ty`),
    # * traverses function body to add `offset` to all `Ty` and `span` fields (mutastes)
    # * traverses function locals and debug information to add `offset` to all `span` fields
    if 'MonoItemFn' in item and 'body' in item['MonoItemFn']:
        body = item['MonoItemFn']['body']
        for local in body['locals']:
            local['ty'] = local['ty'] + offset
            local['span'] = local['span'] + offset
        for block in body['blocks']:
            for stmt in block['statements']:
                apply_offset_stmt(stmt['kind'], offset)
                stmt['span'] = stmt['span'] + offset
            apply_offset_terminator(block['terminator']['kind'], offset)
            block['terminator']['span'] = block['terminator']['span'] + offset
        # adjust span in var_debug_info, each item's source_info.span
        for thing in body['var_debug_info']:
            thing['source_info']['span'] += offset
            if 'Constant' in thing['value']:
                apply_offset_operand({'Constant': thing['value']}, offset)
            if 'composite' in thing and thing['composite'] is not None:
                thing['composite']['ty'] += offset
                for proj in thing['composite']['projection']:
                    apply_offset_proj(proj, offset)


def apply_offset_terminator(term: dict, offset: int) -> None:
    # traverses and updates operands and places (projections) within the terminator
    # Noop for the commented cases
    # - Goto
    if 'SwitchInt' in term:
        apply_offset_operand(term['SwitchInt']['discr'], offset)
    # - Resume
    # - Abort
    # - Unreachable
    elif 'Drop' in term:
        apply_offset_place(term['Drop']['place'], offset)
    elif 'Call' in term:
        apply_offset_operand(term['Call']['func'], offset)
        for arg in term['Call']['args']:
            apply_offset_operand(arg, offset)
        apply_offset_place(term['Call']['destination'], offset)
    elif 'Assert' in term:
        apply_offset_operand(term['Assert']['cond'], offset)
    # - InlineAsm


def apply_offset_operand(op: dict, offset: int) -> None:
    if 'Copy' in op:
        apply_offset_place(op['Copy'], offset)
    elif 'Move' in op:
        apply_offset_place(op['Move'], offset)
    elif 'Constant' in op:
        op['Constant']['const_']['ty'] = op['Constant']['const_']['ty'] + offset
        if 'Ty' in op['Constant']['const_']['kind']:
            apply_offset_tyconst(op['Constant']['const_']['kind']['Ty']['kind'], offset)
        op['Constant']['span'] = op['Constant']['span'] + offset


def apply_offset_tyconst(tyconst: dict, offset: int) -> None:
    # Param
    # Bound
    if 'Unevaluated' in tyconst:
        for arg in tyconst['Unevaluated'][1]:
            apply_offset_gen_arg(arg, offset)
    elif 'Value' in tyconst:
        tyconst['Value'][0] = tyconst['Value'][0] + offset
    elif 'ZSTValue' in tyconst:
        tyconst['ZSTValue'] = tyconst['ZSTValue'] + offset


def apply_offset_place(place: dict, offset: int) -> None:
    # applies offset to all projection elements
    for proj in place['projection']:
        apply_offset_proj(proj, offset)


def apply_offset_proj(proj: dict, offset: int) -> None:
    # Deref
    if 'Field' in proj:
        proj['Field'][1] = proj['Field'][1] + offset
    # Index
    # ConstantIndex
    # Subslice
    # Downcast
    elif 'OpaqueCast' in proj:
        proj['OpaqueCast'] = proj['OpaqueCast'] + offset
    elif 'Subtype' in proj:
        proj['Subtype'] = proj['Subtype'] + offset


def apply_offset_stmt(stmt: dict, offset: int) -> None:
    if 'Assign' in stmt:
        apply_offset_place(stmt['Assign'][0], offset)
        apply_offset_rvalue(stmt['Assign'][1], offset)
    elif 'FakeRead' in stmt:
        apply_offset_place(stmt['FakeRead'][1], offset)
    elif 'SetDiscriminant' in stmt:
        apply_offset_place(stmt['SetDiscriminant'][0], offset)
    elif 'Deinit' in stmt:
        apply_offset_place(stmt['Deinit'], offset)
    # StorageLive
    # StorageDead
    elif 'Retag' in stmt:
        apply_offset_place(stmt['Retag'], offset)
    elif 'PlaceMention' in stmt:
        apply_offset_place(stmt['PlaceMention'], offset)
    elif 'AscribeUserType' in stmt:
        apply_offset_place(stmt['AscribeUserType']['place'], offset)
        for proj in stmt['AscribeUserType']['projections']:
            apply_offset_proj(proj, offset)
    # Coverage
    # Intrinsic
    # ConstEvalCounter
    # Nop


def apply_offset_rvalue(rval: dict, offset: int) -> None:
    if 'AddressOf' in rval:
        apply_offset_place(rval['AddressOf'][1], offset)
    elif 'Aggregate' in rval:
        # handle AggregateKind
        if 'Array' in rval['Aggregate'][0]:
            rval['Aggregate'][0]['Array'] = rval['Aggregate'][0]['Array'] + offset  # ty field
        # Tuple
        elif 'Adt' in rval['Aggregate'][0]:
            rval['Aggregate'][0]['Adt'][0] = rval['Aggregate'][0]['Adt'][0] + offset  # AdtDef field
            # GenericArgs can recursively contain TyConst, or Ty
            for arg in rval['Aggregate'][0]['Adt'][2]:
                apply_offset_gen_arg(arg, offset)
            # usertype annotation and field idx not used, unchanged for now
        elif 'Closure' in rval['Aggregate'][0]:
            for arg in rval['Aggregate'][0]['Closure'][1]:
                apply_offset_gen_arg(arg, offset)
        elif 'Coroutine' in rval['Aggregate'][0]:
            for arg in rval['Aggregate'][0]['Coroutine'][1]:
                apply_offset_gen_arg(arg, offset)
        elif 'RawPtr' in rval['Aggregate'][0]:
            rval['Aggregate'][0]['RawPtr'][0] = rval['Aggregate'][0]['RawPtr'][0] + offset  # ty field
        for op in rval['Aggregate'][1]:
            apply_offset_operand(op, offset)
    elif 'BinaryOp' in rval:
        apply_offset_operand(rval['BinaryOp'][1], offset)
        apply_offset_operand(rval['BinaryOp'][2], offset)
    elif 'Cast' in rval:
        apply_offset_operand(rval['Cast'][1], offset)
        rval['Cast'][2] = rval['Cast'][2] + offset
    elif 'CheckedBinaryOp' in rval:
        apply_offset_operand(rval['CheckedBinaryOp'][1], offset)
        apply_offset_operand(rval['CheckedBinaryOp'][2], offset)
    elif 'CopyForDeref' in rval:
        apply_offset_place(rval['CopyForDeref'], offset)
    elif 'Discriminant' in rval:
        apply_offset_place(rval['Discriminant'], offset)
    elif 'Len' in rval:
        apply_offset_place(rval['Len'], offset)
    elif 'Ref' in rval:
        apply_offset_place(rval['Ref'][2], offset)
    elif 'Repeat' in rval:
        apply_offset_operand(rval['Repeat'][0], offset)
        apply_offset_tyconst(rval['Repeat'][1]['kind'], offset)
    elif 'ShallowInitBox' in rval:
        apply_offset_operand(rval['ShallowInitBox'][0], offset)
        rval['ShallowInitBox'][1] = rval['ShallowInitBox'][1] + offset
    # ThreadLocalRef
    elif 'NullaryOp' in rval:
        rval['NullaryOp'][1] = rval['NullaryOp'][1] + offset
    elif 'UnaryOp' in rval:
        apply_offset_operand(rval['UnaryOp'][1], offset)
    elif 'Use' in rval:
        apply_offset_operand(rval['Use'], offset)


def apply_offset_gen_arg(arg: dict, offset: int) -> None:
    # GenericArg may contain a Ty or a TyConst
    if 'Type' in arg:
        arg['Type'] = arg['Type'] + offset
    elif 'Const' in arg:
        apply_offset_tyconst(arg['Const']['kind'], offset)
