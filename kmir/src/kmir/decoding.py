from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply
from pyk.kast.prelude.string import stringToken

from .alloc import Allocation, AllocInfo, Function, Memory, ProvenanceEntry, ProvenanceMap, Static, VTable
from .ty import (
    ArbitraryFields,
    ArrayT,
    BoolT,
    EnumT,
    Initialized,
    IntegerLength,
    IntT,
    IntTy,
    Multiple,
    Pointer,
    PrimitiveInt,
    PtrT,
    RefT,
    Single,
    StrT,
    StructT,
    TupleT,
    UintT,
    WrappingRange,
)
from .value import (
    NO_SIZE,
    AggregateValue,
    AllocRefValue,
    BoolValue,
    DynamicSize,
    IntValue,
    Metadata,
    RangeValue,
    StaticSize,
    StrValue,
    Value,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyk.kast import KInner

    from .ty import FieldsShape, LayoutShape, MachineSize, Scalar, TagEncoding, Ty, TypeMetadata, UintTy
    from .value import MetadataSize


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
        case AllocInfo(
            ty=_,
            # `Static` currently only carries `def_id`; we ignore it here.
            global_alloc=Static(),
        ):
            # Static global alloc does not carry raw bytes here; leave as unable-to-decode placeholder
            return UnableToDecodeValue('Static global allocation not decoded')
        case AllocInfo(
            ty=_,
            global_alloc=Function(
                instance=_,
            ),
        ):
            # Function alloc currently not decoded to a runtime value
            return UnableToDecodeValue('Function global allocation not decoded')
        case AllocInfo(
            ty=_,
            # `VTable` carries `ty` and optional `binder`; we ignore both here.
            global_alloc=VTable(),
        ):
            # VTable alloc currently not decoded to a runtime value
            return UnableToDecodeValue('VTable global allocation not decoded')
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

                metadata_size = _metadata_size(pointee_type_info)

                if len(data) == 8:
                    # single slim pointer (assumes usize == u64)
                    return AllocRefValue(
                        alloc_id=alloc_id,
                        metadata=Metadata(
                            size=metadata_size,
                            pointer_offset=0,
                            origin_size=metadata_size,
                        ),
                    )

                if len(data) == 16 and metadata_size == DynamicSize(1):
                    # sufficient data to decode dynamic size (assumes usize == u64)
                    # expect fat pointer
                    actual_size = DynamicSize(int.from_bytes(data[8:16], byteorder='little', signed=False))
                    return AllocRefValue(
                        alloc_id=alloc_id,
                        metadata=Metadata(
                            size=actual_size,
                            pointer_offset=0,
                            origin_size=actual_size,
                        ),
                    )

    return UnableToDecodeValue(f'Unable to decode alloc: {data!r}, of type: {type_info}')


def _pointee_ty(type_info: TypeMetadata) -> Ty | None:
    match type_info:
        case PtrT(ty) | RefT(ty):
            return ty
        case _:
            return None


def _metadata_size(type_info: TypeMetadata) -> MetadataSize:
    match type_info:
        case ArrayT(length=None):
            return DynamicSize(1)  # 1 is a placeholder, the actual size is inferred from the slice data
        case ArrayT(length=int() as length):
            return StaticSize(length)
        case _:
            return NO_SIZE


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
        case StructT(fields=fields, layout=layout):
            return _decode_struct(data=data, fields=fields, layout=layout, types=types)
        case TupleT(components=components):
            return _decode_tuple(data=data, component_tys=components, types=types)
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


def _decode_struct(
    *,
    data: bytes,
    fields: list[Ty],
    layout: LayoutShape | None,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    if not layout:
        raise ValueError('Struct layout not provided')

    offsets = _extract_offsets(layout.fields)

    match layout.variants:
        case Single(index=0):
            pass
        case _:
            raise ValueError(f'Unexpected layout variants in struct: {layout.variants}')

    field_values = _decode_fields(data=data, tys=fields, offsets=offsets, types=types)
    return AggregateValue(0, field_values)


def _decode_tuple(
    *,
    data: bytes,
    component_tys: list[Ty],
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    if not component_tys:
        if data:
            raise ValueError(f'Zero-sized tuple expected empty data, got: {data!r}')
        return AggregateValue(0, [])

    raise ValueError('Tuple decoding with components is not implemented yet')


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

    offsets = _extract_offsets(layout.fields)

    match layout.variants:
        case Single(index):
            return _decode_enum_single(
                data=data,
                discriminants=discriminants,
                fields=fields,
                offsets=offsets,
                # ---
                index=index,
                # ---
                types=types,
            )
        case Multiple(
            tag=tag,
            tag_encoding=tag_encoding,
            tag_field=tag_field,
            variants=variants,
        ):
            return _decode_enum_multiple(
                data=data,
                discriminants=discriminants,
                fields=fields,
                offsets=offsets,
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


def _extract_offsets(fields_shape: FieldsShape) -> list[MachineSize]:
    match fields_shape:
        case ArbitraryFields(offsets=offsets):
            return offsets
        case _:
            raise ValueError(f'Unsupported fields shape: {fields_shape}')


def _decode_enum_single(
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    offsets: list[MachineSize],
    index: int,
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    assert index == 0, 'Assumed index to always be 0 for Single(index)'

    assert len(fields) == 1, 'Expected a single list of field types for single-variant enum'
    tys = fields[0]

    assert len(discriminants) == 1, 'Expected a single discriminant for single-variant enum'

    field_values = _decode_fields(data=data, tys=tys, offsets=offsets, types=types)
    return AggregateValue(0, field_values)


def _decode_enum_multiple(
    *,
    data: bytes,
    discriminants: list[int],
    fields: list[list[Ty]],
    offsets: list[MachineSize],
    # ---
    tag: Scalar,
    tag_encoding: TagEncoding,
    tag_field: int,
    variant_layouts: list[LayoutShape],
    # ---
    types: Mapping[Ty, TypeMetadata],
) -> Value:
    assert len(offsets) == 1, 'Assumed offsets to only contain the tag offset'
    assert tag_field == 0, 'Assumed tag field to be zero accordingly'
    tag_offset = offsets[tag_field]
    tag_value, width = _extract_tag(data=data, tag_offset=tag_offset, tag=tag)
    discriminant = tag_encoding.decode(tag_value, width=width)

    try:
        variant_idx = discriminants.index(discriminant)
    except ValueError as err:
        raise ValueError(f'Discriminant not found: {discriminant}') from err

    tys = fields[variant_idx]

    variant_layout = variant_layouts[variant_idx]
    field_offsets = _extract_offsets(variant_layout.fields)
    assert isinstance(variant_layout.variants, Single)

    field_values = _decode_fields(data=data, tys=tys, offsets=field_offsets, types=types)
    return AggregateValue(variant_idx, field_values)


def _decode_fields(
    *,
    data: bytes,
    tys: list[Ty],
    offsets: list[MachineSize],
    types: Mapping[Ty, TypeMetadata],
) -> list[Value]:
    res: list[Value] = []
    for ty, offset in zip(tys, offsets, strict=True):
        type_info = types[ty]
        size_in_bytes = type_info.nbytes(types)
        field_data = data[offset.in_bytes : offset.in_bytes + size_in_bytes]
        value = decode_value(field_data, type_info, types)
        res.append(value)
    return res


def _extract_tag(*, data: bytes, tag_offset: MachineSize, tag: Scalar) -> tuple[int, IntegerLength]:
    match tag:
        case Initialized(
            value=PrimitiveInt(
                length=length,
                signed=False,
            ),
            valid_range=_,
        ):
            tag_data = data[tag_offset.in_bytes : tag_offset.in_bytes + length.value]
            tag_value = int.from_bytes(tag_data, byteorder='little', signed=False)
            return tag_value, length
        # special case: niche-encoded optional pointer, None == 0x00000000
        case Initialized(value=Pointer(), valid_range=WrappingRange(start=1, end=0)) if (
            data == b'\x00\x00\x00\x00\x00\x00\x00\x00'
        ):
            return 0, IntegerLength.I64
        case _:
            raise ValueError(f'Unsupported tag: {tag}')
