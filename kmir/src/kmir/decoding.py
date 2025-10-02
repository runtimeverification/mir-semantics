from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ty import IntTy, Ty, TypeMetadata, UintTy
    from .value import Value


def decode_value(data: bytes, type_info: TypeMetadata, types: dict[Ty, TypeMetadata]) -> Value:
    from .ty import ArrayT, Bool, Int, Uint

    match type_info:
        case Bool():
            return _decode_bool(data)
        case Uint(int_ty) | Int(int_ty):
            return _decode_int(data, int_ty)
        case ArrayT(elem_ty, length):
            return _decode_array(data, elem_ty, length, types)
        case _:
            raise ValueError(f'Unsupported type: {type_info}')


def _decode_bool(data: bytes) -> Value:
    from .value import BoolValue

    match data:
        case b'\x00':
            return BoolValue(False)
        case b'\x01':
            return BoolValue(True)
        case _:
            raise ValueError(f'Cannot decode as Bool: {data!r}')


def _decode_int(data: bytes, int_ty: IntTy | UintTy) -> Value:
    from .ty import IntTy
    from .value import IntValue

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
    types: dict[Ty, TypeMetadata],
) -> Value:
    from .value import RangeValue

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
