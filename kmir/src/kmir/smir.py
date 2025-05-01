from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, NewType

from kmir.rust.cargo import cargo_get_smir_json

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

Ty = NewType('Ty', int)
AdtDef = NewType('AdtDef', int)

# TODO: Named tuples w/ `from_dict` and helpers to create K terms


class SMIRInfo:
    _smir: dict

    def __init__(self, rs_file: Path) -> None:
        self._smir = cargo_get_smir_json(rs_file)

    @cached_property
    def types(self) -> dict[Ty, Any]:
        res = {}
        for id, type in self._smir['types']:
            res[Ty(id)] = type
        return res

    @cached_property
    def adt_defs(self) -> dict[AdtDef, Ty]:
        res = {}
        for ty, typeinfo in self.types.items():
            if 'StructType' in typeinfo:
                adt_def = typeinfo['StructType']['adt_def']
                res[AdtDef(adt_def)] = ty
            if 'EnumType' in typeinfo:
                adt_def = typeinfo['EnumType']['adt_def']
                res[AdtDef(adt_def)] = ty
        return res

    @cached_property
    def function_arguments(self) -> dict[str, dict]:
        res = {}
        for item in self._smir['items']:
            is_func = 'MonoItemFn' in item['mono_item_kind']
            if not is_func:
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            arg_count = mono_item_fn['body']['arg_count']
            local_args = mono_item_fn['body']['locals'][1 : arg_count + 1]
            res[name] = local_args
        return res

    # TODO (does this go here?)
    # def ty_as_kast(self, ty: Ty) -> KInner
