from __future__ import annotations

import json
import logging
from collections import deque
from functools import cached_property
from typing import TYPE_CHECKING, NewType

from .alloc import AllocInfo
from .ty import EnumT, RefT, StructT, Ty, TypeMetadata, UnionT

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path
    from typing import Final

    from .alloc import AllocId


_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


AdtDef = NewType('AdtDef', int)


class SMIRInfo:
    _smir: dict

    def __init__(self, smir_json: dict) -> None:
        self._smir = smir_json

    @staticmethod
    def from_file(smir_json_file: Path) -> SMIRInfo:
        return SMIRInfo(json.loads(smir_json_file.read_text()))

    def dump(self, smir_json_file: Path) -> None:
        smir_json_file.write_text(json.dumps(self._smir))

    @cached_property
    def name(self) -> str:
        return self._smir['name']

    @cached_property
    def digest(self) -> str:
        import hashlib

        hash_object = hashlib.sha256(str(self._smir).encode('UTF-8'))
        return hash_object.hexdigest()

    @cached_property
    def allocs(self) -> dict[AllocId, AllocInfo]:
        return {
            alloc_info.alloc_id: alloc_info for alloc_info in (AllocInfo.from_dict(dct) for dct in self._smir['allocs'])
        }

    @cached_property
    def types(self) -> dict[Ty, TypeMetadata]:
        return {Ty(id): TypeMetadata.from_raw(type) for id, type in self._smir['types']}

    def unref_type(self, ty: Ty) -> TypeMetadata | None:
        """Recursively resolve type until reaching a non-reference type."""
        if ty not in self.types:
            _LOGGER.warning(f'Type {ty} not found in types')
            return None
        type_info = self.types[ty]
        while isinstance(type_info, RefT):
            if Ty(type_info.pointee_type) not in self.types:
                _LOGGER.info(f'Pointee type {Ty(type_info.pointee_type)} not found in types for reference type {ty}')
                return type_info
            type_info = self.types[Ty(type_info.pointee_type)]
        return type_info

    @cached_property
    def unref_types(self) -> dict[Ty, TypeMetadata | None]:
        """Returns a dictionary of all types and their unreferenced versions."""
        return {ty: self.unref_type(ty) for ty in self.types.keys()}

    @cached_property
    def adt_defs(self) -> dict[AdtDef, Ty]:
        res = {}
        for ty, typeinfo in self.types.items():
            match typeinfo:
                case StructT(adt_def=adt_def):
                    res[AdtDef(adt_def)] = ty
                case EnumT(adt_def=adt_def):
                    res[AdtDef(adt_def)] = ty
                case UnionT(adt_def=adt_def):
                    res[AdtDef(adt_def)] = ty
        return res

    @cached_property
    def items(self) -> dict[str, dict]:
        return {_item['symbol_name']: _item for _item in self._smir['items']}

    @cached_property
    def main_symbol(self) -> str | None:
        mains = [
            sym
            for sym, item in self.items.items()
            if 'MonoItemFn' in item['mono_item_kind']
            if item['mono_item_kind']['MonoItemFn']['name'] == 'main'
        ]
        return mains[0] if mains else None

    @cached_property
    def function_arguments(self) -> dict[str, list[dict]]:
        res = {}
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            body = mono_item_fn.get('body')
            if body is None:
                # Functions without a MIR body (e.g., externs/const shims) have no arguments to inspect.
                # Skip adding entries for them; callers should not rely on args for such symbols.
                _LOGGER.debug(f'Skipping function_arguments for {name}: missing body')
                continue

            arg_count = body['arg_count']
            local_args = body['locals'][1 : arg_count + 1]
            res[name] = local_args
        return res

    @cached_property
    def function_symbols(self) -> dict[int, dict]:
        fnc_symbols = {ty: sym for ty, sym, *_ in self._smir['functions'] if type(ty) is int}
        # by convention, Ty -1 is used for 'main' if it exists
        fnc_symbols[-1] = {'NormalSym': self.main_symbol}

        # function items not present in the SMIR lookup table are added with negative Ty ID
        missing = [name for name in self.items.keys() if {'NormalSym': name} not in fnc_symbols.values()]

        fake_ty = -2
        for name in missing:
            fnc_symbols[fake_ty] = {'NormalSym': name}
            fake_ty -= 1

        return fnc_symbols

    @cached_property
    def function_symbols_reverse(self) -> dict[str, list[int]]:
        # must retain any duplicates, therefore returning a list of Ty instead of a single one
        tys_for_name: dict[str, list[int]] = {}
        for ty, sym in self.function_symbols.items():
            if 'NormalSym' in sym:
                tys_for_name.setdefault(sym['NormalSym'], []).append(ty)
            elif 'IntrinsicSym' in sym:
                tys_for_name.setdefault(sym['IntrinsicSym'], []).append(ty)
            # Skip other symbol types like NoOpSym for now
        return tys_for_name

    @cached_property
    def function_tys(self) -> dict[str, int]:
        fun_syms = self.function_symbols_reverse

        res = {}
        for item in self._smir['items']:
            if not SMIRInfo._is_func(item):
                _LOGGER.warning(f'Not a function: {item}')
                continue

            mono_item_fn = item['mono_item_kind']['MonoItemFn']
            name = mono_item_fn['name']
            sym = item['symbol_name']
            if not sym in fun_syms:
                _LOGGER.warning(f'Could not find sym in fun_syms: {sym}')
                continue

            # by construction of function_symbols_reverse, it must return at least a singleton
            res[name] = fun_syms[sym][0]
        return res

    @cached_property
    def spans(self) -> dict[int, tuple[Path, int, int, int, int]]:
        return {id: (p, sr, sc, er, ec) for id, [p, sr, sc, er, ec] in self._smir['spans']}

    @staticmethod
    def _is_func(item: dict[str, dict]) -> bool:
        return 'MonoItemFn' in item['mono_item_kind']

    def reduce_to(self, start_symbols: str | Sequence[str]) -> SMIRInfo:
        # returns a new SMIRInfo with all _items_ removed that are not reachable from the named function(s)
        match start_symbols:
            case str(symbol):
                start_tys = [Ty(self.function_tys[symbol])]
            case [*symbols] if symbols and all(isinstance(sym, str) for sym in symbols):
                start_tys = [Ty(self.function_tys[sym]) for sym in symbols]
            case _:
                raise ValueError("SMIRInfo.reduce_to() received an invalid start_symbol")

        _LOGGER.debug(f'Reducing items, starting at {start_tys}. Call Edges {self.call_edges}')

        reachable = compute_closure(start_tys, self.call_edges)

        _LOGGER.debug(f'Reducing to reachable Tys {reachable}')

        new_smir = self._smir.copy()  # shallow copy, but we can overwrite the `items`

        # filter the new symbols to avoid key errors
        new_syms = [self.function_symbols[ty] for ty in reachable]
        new_syms_ = [sym['NormalSym'] for sym in new_syms if 'NormalSym' in sym]
        new_smir['items'] = [self.items[sym] for sym in new_syms_ if sym in self.items]

        return SMIRInfo(new_smir)

    @cached_property
    def call_edges(self) -> dict[Ty, set[Ty]]:
        # determines which functions are _called_ from others, by symbol name
        result = {}
        for sym, item in self.items.items():
            if not SMIRInfo._is_func(item):
                continue
            # skip functions not present in the `function_symbols_reverse` table
            if not sym in self.function_symbols_reverse:
                continue
            body = item['mono_item_kind']['MonoItemFn'].get('body')
            if body is None or 'blocks' not in body:
                # No MIR body means we cannot extract call edges; treat as having no outgoing edges.
                _LOGGER.debug(f'Skipping call edge extraction for {sym}: missing body')
                called_tys: set[Ty] = set()
            else:
                called_funs = [
                    b['terminator']['kind']['Call']['func'] for b in body['blocks'] if 'Call' in b['terminator']['kind']
                ]
                called_tys = {Ty(op['Constant']['const_']['ty']) for op in called_funs if 'Constant' in op}
            # TODO also add any constant operands used as arguments whose ty refer to a function
            # the semantics currently does not support this, see issue #488 and stable-mir-json issue #55
            for ty in self.function_symbols_reverse[sym]:
                result[Ty(ty)] = called_tys
        return result


def compute_closure(start_nodes: Sequence[Ty], edges: dict[Ty, set[Ty]]) -> set[Ty]:
    work = deque(start_nodes)
    reached = set()
    finished = False
    while not finished:
        try:
            next = work.popleft()
        except IndexError:
            # queue empty, we are done
            finished = True
        if not next in reached:
            reached.add(next)
            # tolerate missing edge entries in edges
            if next in edges:
                work.extend(edges[next])
    return reached
