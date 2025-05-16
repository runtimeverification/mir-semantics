from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import cached_property, reduce
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from pathlib import Path

Ty = NewType('Ty', int)
AdtDef = NewType('AdtDef', int)


class SMIRInfo:
    _smir: dict

    def __init__(self, smir_json: dict) -> None:
        self._smir = smir_json

    @staticmethod
    def from_file(smir_json_file: Path) -> SMIRInfo:
        return SMIRInfo(json.loads(smir_json_file.read_text()))

    @cached_property
    def types(self) -> dict[Ty, TypeMetadata]:
        return {Ty(id): metadata_from_json(type) for id, type in self._smir['types']}

    @cached_property
    def adt_defs(self) -> dict[AdtDef, Ty]:
        res = {}
        for ty, typeinfo in self.types.items():
            match typeinfo:
                case StructT(adt_def=adt_def):
                    res[AdtDef(adt_def)] = ty
                case EnumT(adt_def=adt_def):
                    res[AdtDef(adt_def)] = ty
                case UnionT(adt_def=adt_def):
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


class IntTy(Enum):
    I8 = 1
    I16 = 2
    I32 = 4
    I64 = 8
    I128 = 16
    Isize = 8


class UintTy(Enum):
    U8 = 1
    U16 = 2
    U32 = 4
    U64 = 8
    U128 = 16
    Usize = 8


class FloatTy(Enum):
    F16 = 2
    F32 = 4
    F64 = 8
    F128 = 16


@dataclass
class TypeMetadata: ...


@dataclass
class PrimitiveType(TypeMetadata): ...


@dataclass
class Bool(PrimitiveType): ...


@dataclass
class Char(PrimitiveType): ...


@dataclass
class Str(PrimitiveType): ...


@dataclass
class Float(PrimitiveType):
    info: FloatTy


@dataclass
class Int(PrimitiveType):
    info: IntTy


@dataclass
class Uint(PrimitiveType):
    info: UintTy


def _primty_from_json(typeinfo: str | dict) -> PrimitiveType:
    if typeinfo == 'Bool':
        return Bool()
    elif typeinfo == 'Char':
        return Char()
    elif typeinfo == 'Str':
        return Str()

    assert isinstance(typeinfo, dict)
    if 'Uint' in typeinfo:
        return Uint(UintTy.__members__[typeinfo['Uint']])
    if 'Int' in typeinfo:
        return Int(IntTy.__members__[typeinfo['Int']])
    if 'Float' in typeinfo:
        return Float(FloatTy.__members__[typeinfo['Float']])
    return NotImplemented


@dataclass
class EnumT(TypeMetadata):
    name: str
    adt_def: int
    discriminants: dict


@dataclass
class StructT(TypeMetadata):
    name: str
    adt_def: int
    fields: list[Ty]


@dataclass
class UnionT(TypeMetadata):
    name: str
    adt_def: int


@dataclass
class ArrayT(TypeMetadata):
    element_type: Ty
    length: int | None


@dataclass
class PtrT(TypeMetadata):
    pointee_type: Ty


@dataclass
class RefT(TypeMetadata):
    pointee_type: Ty


@dataclass
class TupleT(TypeMetadata):
    components: list[Ty]


@dataclass
class FunT(TypeMetadata):
    type_str: str


def metadata_from_json(typeinfo: dict) -> TypeMetadata:
    if 'PrimitiveType' in typeinfo:
        return _primty_from_json(typeinfo['PrimitiveType'])
    elif 'EnumType' in typeinfo:
        info = typeinfo['EnumType']
        discriminants = dict(info['discriminants'])
        return EnumT(name=info['name'], adt_def=info['adt_def'], discriminants=discriminants)
    elif 'StructType' in typeinfo:
        return StructT(
            typeinfo['StructType']['name'], typeinfo['StructType']['adt_def'], typeinfo['StructType']['fields']
        )
    elif 'UnionType' in typeinfo:
        return UnionT(typeinfo['UnionType']['name'], typeinfo['UnionType']['adt_def'])
    elif 'ArrayType' in typeinfo:
        info = typeinfo['ArrayType']
        assert isinstance(info, list)
        length = None if info[1] is None else _decode(info[1]['kind']['Value'][1]['bytes'])
        return ArrayT(info[0], length)
    elif 'PtrType' in typeinfo:
        return PtrT(typeinfo['PtrType'])
    elif 'RefType' in typeinfo:
        return RefT(typeinfo['RefType'])
    elif 'TupleType' in typeinfo:
        return TupleT(typeinfo['TupleType']['types'])
    elif 'FunType' in typeinfo:
        return FunT(typeinfo['FunType'])

    return NotImplemented


def _decode(bytes: list[int]) -> int:
    # assume little-endian: reverse the bytes
    bytes.reverse()
    return reduce(lambda x, y: x * 256 + y, bytes)
