from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING, NamedTuple, NewType

from .ty import Ty

if TYPE_CHECKING:
    from typing import Any, Final


_LOGGER: Final = logging.getLogger(__name__)


AllocId = NewType('AllocId', int)
DefId = NewType('DefId', int)
InstanceDef = NewType('InstanceDef', int)


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
            case {'Function': _}:
                return Function.from_dict(dct)
            case {'VTable': _}:
                return VTable.from_dict(dct)
            case {'Static': _}:
                return Static.from_dict(dct)
            case {'Memory': _}:
                return Memory.from_dict(dct)
            case _:
                raise ValueError(f'Unsupported or invalid GlobalAlloc data: {dct}')


@dataclass
class Function(GlobalAlloc):
    instance: Instance

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Function:
        return Function(
            instance=Instance.from_dict(dct['Function']),
        )


@dataclass
class Instance:
    kind: InstanceKind
    deff: InstanceDef

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Instance:
        return Instance(
            kind=InstanceKind.from_dict(dct['kind']),
            deff=InstanceDef(dct['def']),
        )


class InstanceKind(ABC):  # noqa: B024
    @staticmethod
    def from_dict(obj: Any) -> InstanceKind:
        match obj:
            case 'Item':
                return Item()
            case 'Intrinsic':
                return Intrinsic()
            case {'Virtual': _}:
                return Virtual.from_dict(obj)
            case 'Shim':
                return Shim()
            case _:
                raise ValueError(f'Invalid InstanceKind data: {obj}')


@dataclass
class Item(InstanceKind): ...


@dataclass
class Intrinsic(InstanceKind): ...


@dataclass
class Virtual(InstanceKind):
    idx: int

    @staticmethod
    def from_dict(obj: Any) -> Virtual:
        match obj:
            case {'Virtual': {'idx': idx}}:
                return Virtual(idx=idx)
            case _:
                raise ValueError(f'Invalid Virtual data: {obj}')


@dataclass
class Shim(InstanceKind): ...


@dataclass
class VTable(GlobalAlloc):
    ty: Ty
    binder: ExistentialTraitRefBinder | None

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> VTable:
        return VTable(
            ty=Ty(dct['VTable'][0]),
            binder=ExistentialTraitRefBinder.from_dict(dct['VTable'][1]) if dct['VTable'][1] is not None else None,
        )


@dataclass
class ExistentialTraitRefBinder:
    value: ExistentialTraitRef
    bound_vars: list[BoundVariableKind]

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> ExistentialTraitRefBinder:
        return ExistentialTraitRefBinder(
            value=ExistentialTraitRef.from_dict(dct['value']),
            bound_vars=[BoundVariableKind.from_dict(var) for var in dct['bound_vars']],
        )


@dataclass
class ExistentialTraitRef:
    def_id: DefId
    generic_args: list[GenericArgKind]

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> ExistentialTraitRef:
        return ExistentialTraitRef(
            def_id=DefId(dct['def_id']),
            generic_args=[GenericArgKind.from_dict(arg) for arg in dct['generic_args']],
        )


@dataclass
class BoundVariableKind(ABC):  # noqa: B024
    @staticmethod
    def from_dict(dct: Any) -> BoundVariableKind:
        match dct:
            case {'Ty': _}:
                return BVTy.from_dict(dct)
            case {'Region': _}:
                return BVRegion.from_dict(dct)
            case 'Const':
                return BVConst()
            case _:
                raise ValueError(f'Invalid BoundBariableKind data: {dct}')


@dataclass
class BVTy(BoundVariableKind):
    kind: BoundTyKind

    @staticmethod
    def from_dict(dct: Any) -> BVTy:
        return BVTy(kind=BoundTyKind.from_dict(dct['Ty']))


class BoundTyKind(ABC):  # noqa: B024
    @staticmethod
    def from_dict(dct: Any) -> BoundTyKind:
        match dct:
            case 'Anon':
                return BTAnon()
            case {'Param': _}:
                return BTParam.from_dict(dct)
            case _:
                raise ValueError(f'Invalid BoundTyKind data: {dct}')


@dataclass
class BTAnon(BoundTyKind): ...


@dataclass
class BTParam(BoundTyKind):
    def_id: DefId
    name: str

    @staticmethod
    def from_dict(dct: Any) -> BTParam:
        return BTParam(
            def_id=DefId(dct['Param'][0]),
            name=str(dct['Param'][1]),
        )


@dataclass
class BVRegion(BoundVariableKind):
    kind: BoundRegionKind

    @staticmethod
    def from_dict(dct: Any) -> BVRegion:
        return BVRegion(kind=BoundRegionKind.from_dict(dct['Region']))


class BoundRegionKind(ABC):  # noqa: B024
    @staticmethod
    def from_dict(dct: Any) -> BoundRegionKind:
        match dct:
            case 'BrAnon':
                return BRAnon()
            case {'BrNamed': _}:
                return BRNamed.from_dict(dct)
            case 'BrEnv':
                return BREnv()
            case _:
                raise ValueError(f'Invalid BoundRegionKind data: {dct}')


@dataclass
class BRAnon(BoundRegionKind): ...


@dataclass
class BRNamed(BoundRegionKind):
    def_id: DefId
    name: str

    @staticmethod
    def from_dict(dct: Any) -> BRNamed:
        return BRNamed(
            def_id=DefId(dct['BrNamed'][0]),
            name=str(dct['BrNamed'][1]),
        )


@dataclass
class BREnv(BoundRegionKind): ...


@dataclass
class BVConst(BoundVariableKind): ...


@dataclass
class GenericArgKind:
    @staticmethod
    def from_dict(dct: dict[str, Any]) -> GenericArgKind:
        _LOGGER.warning(f'Unparsed GenericArgKind data encountered: {dct}')
        return GenericArgKind()


@dataclass
class Static(GlobalAlloc):
    def_id: DefId

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Static:
        return Static(
            def_id=DefId(dct['Static']),
        )


@dataclass
class Memory(GlobalAlloc):
    allocation: Allocation

    @staticmethod
    def from_dict(dct: dict[str, Any]) -> Memory:
        return Memory(
            allocation=Allocation.from_dict(dct['Memory']),
        )


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
