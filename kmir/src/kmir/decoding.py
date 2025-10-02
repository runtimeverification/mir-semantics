from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .ty import Ty, TypeMetadata
    from .value import Value


def decode_value(data: bytes, type_info: TypeMetadata, types: dict[Ty, TypeMetadata]) -> Value:
    from .ty import Bool

    match type_info:
        case Bool():
            return _decode_bool(data)
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
