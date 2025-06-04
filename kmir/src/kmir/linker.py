from __future__ import annotations

import logging
from itertools import chain
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
        'allocs': [ a for smir in smirs for a in smir._smir['allocs']],
        'functions': [f for smir in smirs for f in smir._smir['functions']],
        'items': [ i for smir in smirs for i in smir._smir['items']],
        'types': [t for smir in smirs for t in smir._smir['types']],
    }
    return SMIRInfo(result_dict)


def ty_range(smir: SMIRInfo) -> int:
    f_max = max([ty for ty, _ in smir.function_symbols.items()])
    ty_max = max([ty for ty, _ in smir.types.items()])
    return max(f_max, ty_max)


def apply_offset(info: SMIRInfo, offset: int) -> None:
    # mutates the dictionary inside the SMIRInfo
    dic = info._smir
    ts = dic['types']

    _LOGGER.debug(f'Applying offset {offset} to smir {dic["name"]}, with {len(ts)} types')


    info._smir['functions'] = [(ty + offset, sym) for ty, sym in info._smir['functions']]
    info._smir['types'] = [(ty + offset, apply_offset_typeInfo(typeInfo, offset)) for ty, typeInfo in info._smir['types']]

    # FIXME traverse item bodies and replace all `ty` fields

def apply_offset_typeInfo(typeinfo: dict, offset: int) -> dict:
    # traverse type information
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
    return typeinfo


############################# Testing only

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('smirs', nargs='+', metavar='SMIR_JSON', help='SMIR JSON files to link')
    parser.add_argument('--output', '-o', metavar='OUTPUT_FILE', help='Output file', default='out.smir.json')
    parser.add_argument('--log-level', '-l', metavar='LOGLEVEL', default='INFO')
    return parser.parse_args()


# def main() -> None:
#     kmir = KMIR(LLVM_DEF_DIR)


#     result = parse_json(kmir.definition, Path(args.json), args.sort)
def run_linker() -> None:
    args = parse_args()

    logging.basicConfig(level=args.log_level.upper())

    smirs = [SMIRInfo.from_file(Path(f)) for f in args.smirs]

    result = link(smirs)

    result.dump(Path(args.output))
