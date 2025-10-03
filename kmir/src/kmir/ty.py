from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from typing import Any, Final


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


def _cannot_parse_as(name: str, data: Any) -> ValueError:
    return ValueError(f'Cannot parse as {name}: {data}')


class TypeMetadata(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> TypeMetadata:
        if data == 'VoidType':
            return VOID_T

        ((variant, _),) = data.items()

        if not variant.endswith('Type'):
            raise ValueError(f'Unknown TypeMetadata variant: {variant}')

        cls_name = variant[:-3]  # 'FooType' -> 'FooT'
        try:
            cls = globals()[cls_name]
        except KeyError as err:
            raise _cannot_parse_as('TypeMetadata', data) from err

        return cls.from_raw(data)


class PrimitiveT(TypeMetadata, ABC):
    @staticmethod
    def from_raw(data: Any) -> PrimitiveT:
        match data['PrimitiveType']:
            case 'Bool':
                return Bool()
            case 'Char':
                return Char()
            case 'Str':
                return Str()
            case {'Uint': uint_ty}:
                return Uint(UintTy[uint_ty])
            case {'Int': int_ty}:
                return Int(IntTy[int_ty])
            case {'Float': float_ty}:
                return Float(FloatTy[float_ty])
            case _:
                raise _cannot_parse_as('PrimitiveType', data)


@dataclass
class Bool(PrimitiveT): ...


@dataclass
class Char(PrimitiveT): ...


@dataclass
class Str(PrimitiveT): ...


@dataclass
class Float(PrimitiveT):
    info: FloatTy


@dataclass
class Int(PrimitiveT):
    info: IntTy


@dataclass
class Uint(PrimitiveT):
    info: UintTy


@dataclass
class EnumT(TypeMetadata):
    name: str
    adt_def: int
    discriminants: list[int]

    @staticmethod
    def from_raw(data: Any) -> EnumT:
        match data:
            case {
                'EnumType': {
                    'name': name,
                    'adt_def': adt_def,
                    'discriminants': discriminants,
                }
            }:
                return EnumT(
                    name=name,
                    adt_def=adt_def,
                    discriminants=list(discriminants),
                )
            case _:
                raise _cannot_parse_as('EnumT', data)


@dataclass
class StructT(TypeMetadata):
    name: str
    adt_def: int
    fields: list[Ty]

    @staticmethod
    def from_raw(data: Any) -> StructT:
        match data:
            case {
                'StructType': {
                    'name': name,
                    'adt_def': adt_def,
                    'fields': fields,
                }
            }:
                return StructT(
                    name=name,
                    adt_def=adt_def,
                    fields=list(fields),
                )
            case _:
                raise _cannot_parse_as('StructT', data)


@dataclass
class UnionT(TypeMetadata):
    name: str
    adt_def: int

    @staticmethod
    def from_raw(data: Any) -> UnionT:
        match data:
            case {
                'UnionType': {
                    'name': name,
                    'adt_def': adt_def,
                }
            }:
                return UnionT(
                    name=name,
                    adt_def=adt_def,
                )
            case _:
                raise _cannot_parse_as('UnionT', data)


@dataclass
class ArrayT(TypeMetadata):
    element_type: Ty
    length: int | None

    @staticmethod
    def from_raw(data: Any) -> ArrayT:
        match data:
            case {
                'ArrayType': {
                    'elem_type': element_type,
                    'size': size,
                }
            }:
                length: int | None
                if size is None:
                    length = None
                else:
                    bs = bytes(size['kind']['Value'][1]['bytes'])
                    length = int.from_bytes(bs, byteorder='little', signed=False)

                return ArrayT(
                    element_type=element_type,
                    length=length,
                )
            case _:
                raise _cannot_parse_as('ArrayT', data)


@dataclass
class PtrT(TypeMetadata):
    pointee_type: Ty

    @staticmethod
    def from_raw(data: Any) -> PtrT:
        match data:
            case {
                'PtrType': {
                    'pointee_type': int() as pointee_type,
                }
            }:
                return PtrT(Ty(pointee_type))
            case _:
                raise _cannot_parse_as('PtrT', data)


@dataclass
class RefT(TypeMetadata):
    pointee_type: Ty

    @staticmethod
    def from_raw(data: Any) -> RefT:
        match data:
            case {
                'RefType': {
                    'pointee_type': pointee_type,
                }
            }:
                return RefT(Ty(pointee_type))
            case _:
                raise _cannot_parse_as('RefT', data)


@dataclass
class TupleT(TypeMetadata):
    components: list[Ty]

    @staticmethod
    def from_raw(data: Any) -> TupleT:
        match data:
            case {
                'TupleType': {
                    'types': types,
                }
            }:
                return TupleT(list(types))
            case _:
                raise _cannot_parse_as('TupleT', data)


@dataclass
class FunT(TypeMetadata):
    type_str: str

    @staticmethod
    def from_raw(data: Any) -> FunT:
        match data:
            case {'FunType': type_str}:
                return FunT(type_str)
            case _:
                raise _cannot_parse_as('FunT', data)


@dataclass
class VoidT(TypeMetadata): ...


VOID_T: Final = VoidT()
