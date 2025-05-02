from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, NewType

from kmir.kast import bool_var, int_var

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path
    from typing import Any

    from pyk.kast.inner import KInner

Ty = NewType('Ty', int)
AdtDef = NewType('AdtDef', int)

# TODO: Named tuples w/ `from_dict` and helpers to create K terms


class SMIRInfo:
    _smir: dict

    def __init__(self, smir_json: dict) -> None:
        self._smir = smir_json

    @staticmethod
    def from_file(smir_json_file: Path) -> SMIRInfo:
        return SMIRInfo(json.loads(smir_json_file.read_text()))

    @cached_property
    def types(self) -> dict[Ty, Any]:
        res = {}
        for id, type in self._smir['types']:
            res[Ty(id)] = type
        return res

    @cached_property
    def adt_defs(self) -> dict[AdtDef, Ty]:
        res = {}
        for ty, typeinfo in self.types.items():
            if 'StructType' in typeinfo:
                adt_def = typeinfo['StructType']['adt_def']
                res[AdtDef(adt_def)] = ty
            if 'EnumType' in typeinfo:
                adt_def = typeinfo['EnumType']['adt_def']
                res[AdtDef(adt_def)] = ty
        return res

    @cached_property
    def items(self) -> dict[str, dict]:
        return {_item['symbol_name']: _item for _item in self._smir['items']}

    @cached_property
    def function_arguments(self) -> dict[str, list[dict]]:
        res = {}
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            arg_count = mono_item_fn['body']['arg_count']
            local_args = mono_item_fn['body']['locals'][1 : arg_count + 1]
            res[name] = local_args
        return res

    @cached_property
    def function_symbols(self) -> dict[int, dict]:
        return {ty: sym for ty, sym, *_ in self._smir['functions'] if type(ty) is int}

    @cached_property
    def function_symbols_reverse(self) -> dict[str, int]:
        return {sym['NormalSym']: ty for ty, sym in self.function_symbols.items() if 'NormalSym' in sym}

    @cached_property
    def function_tys(self) -> dict[str, int]:
        fun_syms = self.function_symbols_reverse

        res = {'main': -1}
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            sym = item['symbol_name']
            if not sym in fun_syms:
                continue

            res[name] = fun_syms[sym]
        return res

    @staticmethod
    def _is_func(item: dict[str, dict]) -> bool:
        return 'MonoItemFn' in item['mono_item_kind']

    def var_from_ty(self, ty: Ty, varname: str) -> tuple[KInner, Iterable[KInner]]:
        typeinfo = self.types[ty]
        type_metadata = _metadata_from_json(typeinfo)
        match type_metadata:
            case Int(info):
                width = info.value
                return int_var(varname, width, True)
            case Uint(info):
                width = info.value
                return int_var(varname, width, False)
            case Bool():
                return bool_var(varname)
            case _:
                return NotImplemented


class IntTy(Enum):
    I8 = 1
    I16 = 2
    I32 = 4
    I64 = 8
    Isize = 8


class UintTy(Enum):
    U8 = 1
    U16 = 2
    U32 = 4
    U64 = 8
    Usize = 8


@dataclass
class TypeMetadata: ...


@dataclass
class RigidTy(TypeMetadata): ...


@dataclass
class Bool(RigidTy): ...


@dataclass
class Int(RigidTy):
    info: IntTy


@dataclass
class Uint(RigidTy):
    info: UintTy


def _rigidty_from_json(typeinfo: str | dict) -> RigidTy:
    if typeinfo == 'Bool':
        return Bool()

    assert isinstance(typeinfo, dict)
    if 'UInt' in typeinfo:
        return Uint(UintTy.__members__[typeinfo['UInt']])
    if 'Int' in typeinfo:
        return Int(IntTy.__members__[typeinfo['Int']])
    return NotImplemented


def _metadata_from_json(typeinfo: dict) -> TypeMetadata:
    if 'PrimitiveType' in typeinfo:
        return _rigidty_from_json(typeinfo['PrimitiveType'])
    return NotImplemented
