from __future__ import annotations

import json
from functools import cached_property
from typing import TYPE_CHECKING, NewType

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Any

Ty = NewType('Ty', int)
AdtDef = NewType('AdtDef', int)

# TODO: Named tuples w/ `from_dict` and helpers to create K terms


class SMIRInfo:
    _smir: dict

    def __init__(self, smir_json_file: Path) -> None:
        self._smir = json.loads(smir_json_file.read_text())

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
    def items(self) -> dict[str, dict]:
        return {_item['symbol_name']: _item for _item in self._smir['items']}

    @cached_property
    def function_arguments(self) -> dict[str, dict]:
        res = {}
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            arg_count = mono_item_fn['body']['arg_count']
            local_args = mono_item_fn['body']['locals'][1 : arg_count + 1]
            res[name] = local_args
        return res

    @cached_property
    def function_symbols(self) -> tuple[dict[Ty, str], dict[str, Ty]]:
        names = {}
        tys = {}
        for ty, sym in self._smir['functions']:
            names[Ty(ty)] = sym
            tys[sym] = Ty(ty)
        return (names, tys)

    @cached_property
    def function_tys(self) -> dict[str, Ty]:
        res = {}
        (_, fun_syms) = self.function_symbols
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            sym = item['symbol_name']
            if not sym in fun_syms:
                continue

            res[name] = fun_syms[sym]
        return res

    @staticmethod
    def _is_func(item: dict[str, dict]) -> bool:
        return 'MonoItemFn' in item['mono_item_kind']

    # TODO (does this go here?)
    # def ty_as_kast(self, ty: Ty) -> KInner
