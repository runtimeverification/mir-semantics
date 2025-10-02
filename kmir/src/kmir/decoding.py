from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ty import IntTy, Ty, TypeMetadata, UintTy
    from .value import Value


def decode_value(data: bytes, type_info: TypeMetadata, types: dict[Ty, TypeMetadata]) -> Value:
    from .ty import Bool, Int, Uint

    match type_info:
        case Bool():
            return _decode_bool(data)
        case Uint(int_ty) | Int(int_ty):
            return _decode_int(data, int_ty)
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
