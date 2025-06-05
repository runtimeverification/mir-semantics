from __future__ import annotations

import logging
from math import ceil, log10
from typing import TYPE_CHECKING

from .smir import SMIRInfo

if TYPE_CHECKING:
    from typing import Final

_LOGGER: Final = logging.getLogger(__name__)


def link(smirs: list[SMIRInfo]) -> SMIRInfo:
    max_ty_range = max(map(ty_range, smirs))
    # round up to nearest power of 10
    offset = 10 ** (ceil(log10(max_ty_range)))

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
    }
    return SMIRInfo(result_dict)


def ty_range(smir: SMIRInfo) -> int:
    f_max = max([ty for ty, _ in smir.function_symbols.items()])
    ty_max = max([ty for ty, _ in smir.types.items()])
    return max(f_max, ty_max)


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

    # traverse item bodies and replace all `ty` fields
    for item in info._smir['items']:
        apply_offset_item(item['mono_item_kind'], offset)


def apply_offset_typeInfo(typeinfo: dict, offset: int) -> dict:
    # traverses type information, updating all `Ty`-valued fields and `adt_def` fields within
    # returns the updated (i.e., mutated) `typeinfo`` dictionary
    if 'StructType' in typeinfo:
        typeinfo['StructType']['fields'] = [x + offset for x in typeinfo['StructType']['fields']]
    elif 'ArrayType' in typeinfo:
        assert isinstance(typeinfo['ArrayType'], list)
        typeinfo['ArrayType'][0] = typeinfo['ArrayType'][0] + offset
    elif 'PtrType' in typeinfo:
        typeinfo['PtrType'] = typeinfo['PtrType'] + offset
    elif 'RefType' in typeinfo:
        typeinfo['RefType'] = typeinfo['RefType'] + offset
    elif 'TupleType' in typeinfo:
        typeinfo['TupleType']['types'] = [x + offset for x in typeinfo['TupleType']['types']]
    # noop cases
    # elif 'PrimitiveType' in typeinfo:
    # elif 'EnumType' in typeinfo:
    # elif 'UnionType' in typeinfo:
    # elif 'FunType' in typeinfo:

    # FIXME adt_def!

    return typeinfo


def apply_offset_item(item: dict, offset: int) -> None:
    # Operating on MonoItemFn (MonoItemStatic and GlobalAsm do not contain any `Ty`),
    # traverses the body of the function and adds `offset` to all `Ty` fields (mutastes)
    if 'MonoItemFn' in item and 'body' in item['MonoItemFn']:
        body = item['MonoItemFn']['body']
        for local in body['locals']:
            local['ty'] = local['ty'] + offset
        for block in body['blocks']:
            for stmt in block['statements']:
                apply_offset_stmt(stmt['kind'], offset)
            apply_offset_terminator(block['terminator']['kind'], offset)


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


def apply_offset_tyconst(tyconst: dict, offset: int) -> None:
    # Param
    # Bound
    if 'Unevaluated' in tyconst:
        # GenericArgs can recursively contain TyConst, or Ty
        for arg in tyconst['Unevaluated'][1]:
            if 'Type' in arg:
                arg['Type'] = arg['Type'] + offset
            elif 'Const' in arg:
                apply_offset_tyconst(arg['Const']['kind'], offset)
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
    # all statement kinds
    return None  # NotImplemented


############################# Testing only

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('smirs', nargs='+', metavar='SMIR_JSON', help='SMIR JSON files to link')
    parser.add_argument('--output', '-o', metavar='OUTPUT_FILE', help='Output file', default='out.smir.json')
    parser.add_argument('--log-level', '-l', metavar='LOGLEVEL', default='INFO')
    return parser.parse_args()


def run_linker() -> None:
    args = parse_args()

    logging.basicConfig(level=args.log_level.upper())

    smirs = [SMIRInfo.from_file(Path(f)) for f in args.smirs]

    result = link(smirs)

    result.dump(Path(args.output))
