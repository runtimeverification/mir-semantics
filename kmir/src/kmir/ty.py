from dataclasses import dataclass
from enum import Enum
from functools import reduce
from typing import NewType

Ty = NewType('Ty', int)


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
    discriminants: list[int]


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
        discriminants = list(info['discriminants'])
        return EnumT(name=info['name'], adt_def=info['adt_def'], discriminants=discriminants)
    elif 'StructType' in typeinfo:
        return StructT(
            typeinfo['StructType']['name'], typeinfo['StructType']['adt_def'], typeinfo['StructType']['fields']
        )
    elif 'UnionType' in typeinfo:
        return UnionT(typeinfo['UnionType']['name'], typeinfo['UnionType']['adt_def'])
    elif 'ArrayType' in typeinfo:
        info = typeinfo['ArrayType']
        length = None if info['size'] is None else _decode(info['size']['kind']['Value'][1]['bytes'])
        return ArrayT(info['elem_type'], length)
    elif 'PtrType' in typeinfo:
        return PtrT(typeinfo['PtrType']['pointee_type'])
    elif 'RefType' in typeinfo:
        return RefT(typeinfo['RefType']['pointee_type'])
    elif 'TupleType' in typeinfo:
        return TupleT(typeinfo['TupleType']['types'])
    elif 'FunType' in typeinfo:
        return FunT(typeinfo['FunType'])

    return NotImplemented


def _decode(bytes: list[int]) -> int:
    # assume little-endian: reverse the bytes
    bs = bytes.copy()
    bs.reverse()
    return reduce(lambda x, y: x * 256 + y, bs)
