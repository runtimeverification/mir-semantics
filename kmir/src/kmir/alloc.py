from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple, NewType

from .ty import Ty

if TYPE_CHECKING:
    from typing import Any


AllocId = NewType('AllocId', int)


@dataclass
class AllocInfo:
    alloc_id: AllocId
    ty: Ty
    global_alloc: GlobalAlloc

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> AllocInfo:
        return AllocInfo(
            alloc_id=AllocId(dct['alloc_id']),
            ty=Ty(dct['ty']),
            global_alloc=GlobalAlloc.from_dict(dct['global_alloc']),
        )


class GlobalAlloc(ABC):  # noqa: B024
    @staticmethod
    def from_dict(dct: dict[str, Any]) -> GlobalAlloc:
        match dct:
            case {'Memory': _}:
                return Memory.from_dict(dct)
            case {'Static': alloc_id}:
                return Static.from_dict(dct)
            case {'Function': _}:
                return Function.from_dict(dct)
            case {'VTable': _}:
                return VTable.from_dict(dct)
            case _:
                raise ValueError(f'Unsupported or invalid GlobalAlloc data: {dct}')


@dataclass
class Memory(GlobalAlloc):
    allocation: Allocation

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Memory:
        return Memory(
            allocation=Allocation.from_dict(dct['Memory']),
        )


@dataclass
class Static(GlobalAlloc):
    alloc_id: AllocId

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Static:
        return Static(
            alloc_id=AllocId(dct['Static']),
        )


@dataclass
class Function(GlobalAlloc):
    instance: dict[str, Any]

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Function:
        # Pass through instance payload as-is; KMIR currently does not execute via function allocs
        return Function(instance=dict(dct['Function']))


@dataclass
class VTable(GlobalAlloc):
    data: Any

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> VTable:
        # Preserve raw representation; currently not interpreted by KMIR
        return VTable(data=dct['VTable'])


@dataclass
class Allocation:
    bytez: list[int | None]  # field 'bytes'
    provenance: ProvenanceMap
    align: int
    mutable: bool  # field 'mutability'

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Allocation:
        return Allocation(
            bytez=list(dct['bytes']),
            provenance=ProvenanceMap.from_dict(dct['provenance']),
            align=int(dct['align']),
            mutable={
                'Not': False,
                'Mut': True,
            }[dct['mutability']],
        )


@dataclass
class ProvenanceMap:
    ptrs: list[ProvenanceEntry]

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> ProvenanceMap:
        return ProvenanceMap(
            ptrs=[
                ProvenanceEntry(
                    offset=int(size),
                    alloc_id=AllocId(prov),
                )
                for size, prov in dct['ptrs']
            ],
        )


class ProvenanceEntry(NamedTuple):
    offset: int
    alloc_id: AllocId
