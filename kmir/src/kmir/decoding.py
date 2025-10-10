from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.prelude.string import stringToken

from .alloc import Allocation, AllocInfo, Memory, ProvenanceEntry, ProvenanceMap
from .ty import (
    ArbitraryFields,
    ArrayT,
    BoolT,
    EnumT,
    IntT,
    IntTy,
    Multiple,
    PrimitiveFields,
    PtrT,
    RefT,
    Single,
    StrT,
    UintT,
)
from .value import (
    NO_METADATA,
    AggregateValue,
    AllocRefValue,
    BoolValue,
    DynamicSize,
    IntValue,
    RangeValue,
    StaticSize,
    StrValue,
    Value,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyk.kast import KInner

    from .ty import LayoutShape, MachineSize, Scalar, TagEncoding, Ty, TypeMetadata, UintTy, VariantsShape
    from .value import Metadata


@dataclass
class UnableToDecodeValue(Value):
    msg: str

    def to_kast(self) -> KInner:
        return KApply(
            'Evaluation::UnableToDecodePy',
            stringToken(self.msg),
        )


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
            return _decode_memory_alloc_or_unable(data=data, ptrs=ptrs, ty=ty, types=types)
        case _:
            raise AssertionError('Unhandled case')


def _decode_memory_alloc_or_unable(
    data: bytes,
    ptrs: list[ProvenanceEntry],
    ty: Ty,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    try:
        type_info = types[ty]
    except KeyError:
        return UnableToDecodeValue(f'Unknown type: {ty}')

    match ptrs:
        case []:
            return decode_value_or_unable(data=data, type_info=type_info, types=types)

        case [ProvenanceEntry(0, alloc_id)]:
            if (pointee_ty := _pointee_ty(type_info)) is not None:  # ensures this is a reference type
                try:
                    pointee_type_info = types[pointee_ty]
                except KeyError:
                    return UnableToDecodeValue(f'Unknown pointee type: {pointee_ty}')

                metadata = _metadata(pointee_type_info)

                if len(data) == 8:
                    # single slim pointer (assumes usize == u64)
                    return AllocRefValue(alloc_id=alloc_id, metadata=metadata)

                if len(data) == 16 and metadata == DynamicSize(1):
                    # sufficient data to decode dynamic size (assumes usize == u64)
                    # expect fat pointer
                    return AllocRefValue(
                        alloc_id=alloc_id,
                        metadata=DynamicSize(int.from_bytes(data[8:16], byteorder='little', signed=False)),
                    )

    return UnableToDecodeValue(f'Unable to decode alloc: {data!r}, of type: {type_info}')


def _pointee_ty(type_info: TypeMetadata) -> Ty | None:
    match type_info:
        case PtrT(ty) | RefT(ty):
            return ty
        case _:
            return None


def _metadata(type_info: TypeMetadata) -> Metadata:
    match type_info:
        case ArrayT(length=None):
            return DynamicSize(1)  # 1 is a placeholder, the actual size is inferred from the slice data
        case ArrayT(length=int() as length):
            return StaticSize(length)
        case _:
            return NO_METADATA


def decode_value_or_unable(data: bytes, type_info: TypeMetadata, types: Mapping[Ty, TypeMetadata]) -> Value:
    try:
        return decode_value(data=data, type_info=type_info, types=types)
    except ValueError as err:
        return UnableToDecodeValue(f'Unable to decode value: {data!r}, of type: {type_info}: {err}')


def decode_value(data: bytes, type_info: TypeMetadata, types: Mapping[Ty, TypeMetadata]) -> Value:
    match type_info:
        case BoolT():
            return _decode_bool(data)
        case StrT():
            return _decode_str(data)
        case UintT(int_ty) | IntT(int_ty):
            return _decode_int(data, int_ty)
        case ArrayT(elem_ty, length):
            return _decode_array(data, elem_ty, length, types)
        case EnumT(
            discriminants=discriminants,
            fields=fields,
            layout=layout,
        ):
            return _decode_enum(
                data=data,
                discriminants=discriminants,
                fields=fields,
                layout=layout,
                types=types,
            )
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


def _decode_str(data: bytes) -> Value:
    return StrValue(data.decode('utf-8'))


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
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    layout: LayoutShape | None,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    if not layout:
        raise ValueError('Enum layout not provided')

    match layout.fields:
        case PrimitiveFields():
            raise ValueError('TODO: support decoding for FieldsShape::Primitive')
        case ArbitraryFields(offsets=offsets):
            return _decode_enum_arbitrary(
                data=data,
                discriminants=discriminants,
                fields=fields,
                layout_offsets=offsets,
                layout_variants=layout.variants,
                types=types,
            )
        case _:
            raise AssertionError('Undhandle case')


def _decode_enum_arbitrary(
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    layout_offsets: list[MachineSize],
    layout_variants: VariantsShape,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    match layout_variants:
        case Single(index):
            return _decode_enum_arbitrary_single(
                data=data,
                discriminants=discriminants,
                fields=fields,
                layout_offsets=layout_offsets,
                # ---
                tag_index=index,
                # ---
                types=types,
            )
        case Multiple(
            tag=tag,
            tag_encoding=tag_encoding,
            tag_field=tag_field,
            variants=variants,
        ):
            return _decode_enum_arbitrary_multiple(
                data=data,
                discriminants=discriminants,
                fields=fields,
                layout_offsets=layout_offsets,
                # ---
                tag=tag,
                tag_encoding=tag_encoding,
                tag_field=tag_field,
                variant_layouts=variants,
                # ---
                types=types,
            )
        case _:
            raise AssertionError('Undhandled case')


def _decode_enum_arbitrary_single(
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    layout_offsets: list[MachineSize],
    tag_index: int,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    assert len(fields) == 1, 'Expected a single list of field types for single-variant enum'
    tys = fields[0]

    assert len(discriminants) == 1, 'Expected a single discriminant for single-variant enum'
    discriminant = discriminants[0]
    assert tag_index == discriminant, 'Assumed tag_index to be the same as the discriminant'

    field_values: list[Value] = []

    assert len(tys) == len(layout_offsets), 'Expected as many field offsets as field types'
    for ty, offset in zip(tys, layout_offsets, strict=True):
        field_type_info = types[ty]
        field_nbytes = field_type_info.nbytes(types)
        field_data = data[offset.in_bytes : offset.in_bytes + field_nbytes]
        field_value = decode_value(field_data, field_type_info, types)
        field_values.append(field_value)

    return AggregateValue(0, field_values)


def _decode_enum_arbitrary_multiple(
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    layout_offsets: list[MachineSize],
    # ---
    tag: Scalar,
    tag_encoding: TagEncoding,
    tag_field: int,
    variant_layouts: list[LayoutShape],
    # ---
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    # The only supported case for now is when there are no fields
    if any(tys for tys in fields):
        raise ValueError('TODO - implement this case')

    tag_value = int.from_bytes(data, byteorder='little', signed=False)
    try:
        variant_idx = discriminants.index(tag_value)
    except ValueError as err:
        raise ValueError(f'Tag not found: {tag_value}') from err

    return AggregateValue(variant_idx, ())
