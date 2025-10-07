from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple

from pyk.kast.inner import KApply
from pyk.kast.prelude.bytes import bytesToken
from pyk.kast.prelude.kint import intToken

from .alloc import Allocation, AllocInfo, Memory, ProvenanceMap
from .ty import ArrayT, Bool, EnumT, Int, IntTy, Uint
from .value import AggregateValue, BoolValue, IntValue, RangeValue, Value

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyk.kast import KInner

    from .alloc import AllocId
    from .ty import Ty, TypeMetadata, UintTy


@dataclass
class UnableToDecodeValue(Value):
    data: bytes
    type_info: TypeMetadata

    def to_kast(self) -> KInner:
        return KApply(
            'Evaluation::UnableToDecodeValue',
            bytesToken(self.data),
            KApply('TypeInfo::VoidType'),  # TODO: TypeInfo -> KAST transformation
        )


@dataclass
class UnableToDecodeAlloc(Value):
    data: bytes
    ty: Ty

    def to_kast(self) -> KInner:
        return KApply(
            'Evaluation::UnableToDecodeAlloc',
            bytesToken(self.data),
            KApply('ty', intToken(self.ty)),
            KApply('ProvenanceMapEntries::empty'),  # TODO
        )


class ProvenanceMapEntry(NamedTuple):
    offset: int
    alloc_id: AllocId


def decode_alloc_or_unable(alloc_info: AllocInfo, types: Mapping[Ty, TypeMetadata]) -> Value:
    match alloc_info:
        case AllocInfo(
            ty=ty,
            global_alloc=Memory(
                allocation=Allocation(
                    bytez=bytez,
                    provenance=ProvenanceMap(
                        ptrs=ptrs,
                    ),
                ),
            ),
        ):
            data = bytes(n or 0 for n in bytez)

            if not ptrs:  # TODO generalize to lists with at most one entry
                type_info = types[ty]
                return decode_value_or_unable(data=data, type_info=type_info, types=types)

            return UnableToDecodeAlloc(data=data, ty=ty)
        case _:
            raise AssertionError('Unhandled case')


def decode_value_or_unable(data: bytes, type_info: TypeMetadata, types: Mapping[Ty, TypeMetadata]) -> Value:
    try:
        return decode_value(data=data, type_info=type_info, types=types)
    except ValueError:
        return UnableToDecodeValue(data=data, type_info=type_info)


def decode_value(data: bytes, type_info: TypeMetadata, types: Mapping[Ty, TypeMetadata]) -> Value:
    match type_info:
        case Bool():
            return _decode_bool(data)
        case Uint(int_ty) | Int(int_ty):
            return _decode_int(data, int_ty)
        case ArrayT(elem_ty, length):
            return _decode_array(data, elem_ty, length, types)
        case EnumT(discriminants=discriminants, fields=fields):
            return _decode_enum(data, discriminants, fields)
        case _:
            raise ValueError(f'Unsupported type: {type_info}')


def _decode_bool(data: bytes) -> Value:
    match data:
        case b'\x00':
            return BoolValue(False)
        case b'\x01':
            return BoolValue(True)
        case _:
            raise ValueError(f'Cannot decode as Bool: {data!r}')


def _decode_int(data: bytes, int_ty: IntTy | UintTy) -> Value:
    nbytes = int_ty.value
    if len(data) != nbytes:
        raise ValueError(f'Expected (u)int of length {nbytes}, got: {data!r}')

    signed = isinstance(int_ty, IntTy)

    return IntValue(
        value=int.from_bytes(data, byteorder='little', signed=signed),
        nbits=nbytes * 8,
        signed=signed,
    )


def _decode_array(
    data: bytes,
    elem_ty: Ty,
    length: int | None,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    try:
        elem_info = types[elem_ty]
    except KeyError as err:
        raise ValueError(f'Unknown element type: {elem_ty}') from err

    elem_nbytes = elem_info.nbytes(types)

    elems = []
    while data:
        elem_data = data[:elem_nbytes]
        data = data[elem_nbytes:]
        elem = decode_value(elem_data, elem_info, types)
        elems.append(elem)

    if length is not None and len(elems) != length:
        raise ValueError(f'Expected {length} elements, got: {len(elems)}')

    return RangeValue(elems)


def _decode_enum(
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
) -> Value:
    # The only supported case for now is when there are no fields
    if any(tys for tys in fields):
        raise ValueError('TODO - implement this case')

    tag = int.from_bytes(data, byteorder='little', signed=False)
    try:
        variant_idx = discriminants.index(tag)
    except ValueError as err:
        raise ValueError(f'Tag not found: {tag}') from err

    return AggregateValue(variant_idx, ())
