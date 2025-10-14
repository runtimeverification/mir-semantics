from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, NamedTuple, NewType

if TYPE_CHECKING:
    from collections.abc import Mapping
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

    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        raise ValueError(f'Method nbytes() is unsupported for type: {self}')


class PrimitiveT(TypeMetadata, ABC):
    @staticmethod
    def from_raw(data: Any) -> PrimitiveT:
        match data['PrimitiveType']:
            case 'Bool':
                return BoolT()
            case 'Char':
                return CharT()
            case 'Str':
                return StrT()
            case {'Uint': uint_ty}:
                return UintT(UintTy[uint_ty])
            case {'Int': int_ty}:
                return IntT(IntTy[int_ty])
            case {'Float': float_ty}:
                return FloatT(FloatTy[float_ty])
            case _:
                raise _cannot_parse_as('PrimitiveT', data)


@dataclass
class BoolT(PrimitiveT):
    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        return 1


@dataclass
class CharT(PrimitiveT): ...


@dataclass
class StrT(PrimitiveT): ...


@dataclass
class FloatT(PrimitiveT):
    info: FloatTy


@dataclass
class IntT(PrimitiveT):
    info: IntTy

    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        return self.info.value


@dataclass
class UintT(PrimitiveT):
    info: UintTy

    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        return self.info.value


@dataclass
class EnumT(TypeMetadata):
    name: str
    adt_def: int
    discriminants: list[int]
    fields: list[list[Ty]]
    layout: LayoutShape | None

    @staticmethod
    def from_raw(data: Any) -> EnumT:
        match data:
            case {
                'EnumType': {
                    'name': name,
                    'adt_def': adt_def,
                    'discriminants': discriminants,
                    'fields': fields,
                    'layout': layout,
                }
            }:
                return EnumT(
                    name=name,
                    adt_def=adt_def,
                    discriminants=list(discriminants),
                    fields=[list(tys) for tys in fields],
                    layout=LayoutShape.from_raw(layout),
                )
            case _:
                raise _cannot_parse_as('EnumT', data)

    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        match self.layout:
            case None:
                raise ValueError(f'Cannot determine size, layout is missing for: {self}')
            case LayoutShape(size=size):
                return size.in_bytes


@dataclass
class LayoutShape:
    fields: FieldsShape
    variants: VariantsShape
    abi: ValueAbi
    abi_align: int
    size: MachineSize

    @staticmethod
    def from_raw(data: Any) -> LayoutShape:
        match data:
            case {
                'fields': fields,
                'variants': variants,
                'abi': abi,
                'abi_align': abi_align,
                'size': size,
            }:
                return LayoutShape(
                    fields=FieldsShape.from_raw(fields),
                    variants=VariantsShape.from_raw(variants),
                    abi=ValueAbi.from_raw(abi),
                    abi_align=int(abi_align),
                    size=MachineSize.from_raw(size),
                )
            case _:
                raise _cannot_parse_as('LayoutShape', data)


class FieldsShape(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> FieldsShape:
        match data:
            case 'Primitive':
                return PrimitiveFields()
            case {
                'Arbitrary': {
                    'offsets': offsets,
                },
            }:
                return ArbitraryFields(
                    offsets=[MachineSize.from_raw(offset) for offset in offsets],
                )
            case _:
                raise _cannot_parse_as('FieldsShape', data)


@dataclass
class PrimitiveFields(FieldsShape): ...


@dataclass
class ArbitraryFields(FieldsShape):
    offsets: list[MachineSize]


class VariantsShape(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> VariantsShape:
        match data:
            case {
                'Single': {
                    'index': index,
                },
            }:
                return Single(index=index)
            case {
                'Multiple': {
                    'tag': tag,
                    'tag_encoding': tag_encoding,
                    'tag_field': tag_field,
                    'variants': variants,
                },
            }:
                return Multiple(
                    tag=Scalar.from_raw(tag),
                    tag_encoding=TagEncoding.from_raw(tag_encoding),
                    tag_field=int(tag_field),
                    variants=[LayoutShape.from_raw(variant) for variant in variants],
                )
            case _:
                raise _cannot_parse_as('FieldsShape', data)


@dataclass
class Single(VariantsShape):
    index: int


@dataclass
class Multiple(VariantsShape):
    tag: Scalar
    tag_encoding: TagEncoding
    tag_field: int
    variants: list[LayoutShape]


@dataclass
class ValueAbi:
    @staticmethod
    def from_raw(data: Any) -> ValueAbi:
        return ValueAbi()


@dataclass
class MachineSize:
    num_bits: int

    @staticmethod
    def from_raw(data: Any) -> MachineSize:
        match data:
            case {
                'num_bits': num_bits,
            }:
                return MachineSize(num_bits=num_bits)
            case _:
                raise _cannot_parse_as('MachineSize', data)

    @cached_property
    def in_bytes(self) -> int:
        if self.num_bits % 8 != 0:
            raise ValueError('Expected an even number of bytes, got: {self.num_bits} bits')
        return self.num_bits // 8


class Scalar(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> Scalar:
        match data:
            case {
                'Initialized': {
                    'value': value,
                    'valid_range': valid_range,
                },
            }:
                return Initialized(
                    value=Primitive.from_raw(value),
                    valid_range=WrappingRange.from_raw(valid_range),
                )
            case {
                'Union': {
                    'value': value,
                },
            }:
                return Union(
                    value=Primitive.from_raw(value),
                )
            case _:
                raise _cannot_parse_as('Scalar', data)


@dataclass
class Initialized(Scalar):
    value: Primitive
    valid_range: WrappingRange


@dataclass
class Union(Scalar):
    value: Primitive


class Primitive(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> Primitive:
        match data:
            case {
                'Int': {
                    'length': length,
                    'signed': signed,
                },
            }:
                return PrimitiveInt(
                    length=IntegerLength[str(length)],
                    signed=bool(signed),
                )
            case {'Float': _}:
                return Float()
            case {'Pointer': _}:
                return Pointer()
            case _:
                raise _cannot_parse_as('Primitive', data)


@dataclass
class PrimitiveInt(Primitive):
    length: IntegerLength
    signed: bool


class IntegerLength(Enum):
    I8 = 1
    I16 = 2
    I32 = 4
    I64 = 8
    I128 = 16

    def wrapping_sub(self, x: int, y: int) -> int:
        bit_width = 8 * self.value
        mask = (1 << bit_width) - 1
        return (x - y) & mask


@dataclass
class Float(Primitive): ...


@dataclass
class Pointer(Primitive): ...


class TagEncoding(ABC):  # noqa: B024
    @staticmethod
    def from_raw(data: Any) -> TagEncoding:
        match data:
            case 'Direct':
                return Direct()
            case {
                'Niche': {
                    'untagged_variant': untagged_variant,
                    'niche_variants': niche_variants,
                    'niche_start': niche_start,
                },
            }:
                return Niche(
                    untagged_variant=int(untagged_variant),
                    niche_variants=RangeInclusive.from_raw(niche_variants),
                    niche_start=int(niche_start),
                )
            case _:
                raise _cannot_parse_as('TagEncoding', data)

    @abstractmethod
    def decode(self, tag: int, *, width: IntegerLength) -> int: ...


@dataclass
class Direct(TagEncoding):
    def decode(self, tag: int, *, width: IntegerLength) -> int:
        # The tag directly stores the discriminant.
        return tag


@dataclass
class Niche(TagEncoding):
    untagged_variant: int
    niche_variants: RangeInclusive
    niche_start: int

    def decode(self, tag: int, *, width: IntegerLength) -> int:
        # For this encoding, the discriminant and variant index of each variant coincide.
        # To recover the variant index i from tag:
        # i = tag.wrapping_sub(niche_start) + niche_variants.start
        # If i ends up outside niche_variants, the tag must have encoded the untagged_variant.
        i = width.wrapping_sub(tag, self.niche_start) + self.niche_variants.start
        if not i in self.niche_variants:
            return self.untagged_variant
        return i


class RangeInclusive(NamedTuple):
    start: int
    end: int

    @staticmethod
    def from_raw(data: Any) -> RangeInclusive:
        match data:
            case {
                'start': start,
                'end': end,
            }:
                return RangeInclusive(
                    start=int(start),
                    end=int(end),
                )
            case _:
                raise _cannot_parse_as('RangeInclusive', data)

    def __contains__(self, x: object) -> bool:
        if isinstance(x, int):
            return self.start <= x <= self.end
        raise TypeError('Method RangeInclusive.__contains__ is only supported for int, got: {x}')


class WrappingRange(NamedTuple):
    start: int
    end: int

    @staticmethod
    def from_raw(data: Any) -> WrappingRange:
        match data:
            case {
                'start': start,
                'end': end,
            }:
                return WrappingRange(
                    start=int(start),
                    end=int(end),
                )
            case _:
                raise _cannot_parse_as('WrappingRange', data)


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

    def nbytes(self, types: Mapping[Ty, TypeMetadata]) -> int:
        if self.length is None:
            raise ValueError(f'Method nbytes() is unsupported for array of unknown length: {self}')

        try:
            elem_info = types[self.element_type]
        except KeyError as err:
            raise ValueError(f'Unknown element type: {self.element_type}') from err

        return elem_info.nbytes(types) * self.length


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
