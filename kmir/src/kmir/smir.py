from __future__ import annotations

import json
import logging
from collections import deque
from functools import cached_property
from typing import TYPE_CHECKING, NewType

from .alloc import AllocInfo
from .ty import ArrayT, EnumT, PtrT, RefT, StructT, TupleT, Ty, TypeMetadata, UnionT

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path
    from typing import Final

    from .alloc import AllocId


_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'
_DROP_IN_PLACE_PREFIXES: Final = ('std::ptr::drop_in_place::<', 'core::ptr::drop_in_place::<')


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
    def drop_function_tys(self) -> dict[Ty, Ty]:
        res: dict[Ty, Ty] = {}

        for sym, item in self.items.items():
            if sym not in self.function_symbols_reverse:
                continue

            mono_item = item['mono_item_kind'].get('MonoItemFn')
            if mono_item is None:
                continue

            if not mono_item['name'].startswith(_DROP_IN_PLACE_PREFIXES):
                continue

            body = mono_item.get('body')
            if body is None or body['arg_count'] < 1:
                continue

            arg_ty = Ty(body['locals'][1]['ty'])
            arg_type = self.types.get(arg_ty)
            if not isinstance(arg_type, (PtrT, RefT)):
                _LOGGER.debug(f'Skipping drop glue {sym}: unexpected argument type {arg_type}')
                continue

            pointee_ty = Ty(arg_type.pointee_type)
            fn_ty = Ty(self.function_symbols_reverse[sym][0])
            res[pointee_ty] = fn_ty

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
                raise ValueError('SMIRInfo.reduce_to() received an invalid start_symbol')

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
        """Determines which functions are called or referenced from others.

        This includes:
        1. Direct calls: functions used as the `func` operand in Call terminators
        2. Indirect calls: functions passed as arguments (ZeroSized constants) that may be
           called via function pointers (e.g., closures passed to higher-order functions)
        """
        result: dict[Ty, set[Ty]] = {}
        function_tys = set(self.function_symbols.keys())

        for sym, item in self.items.items():
            if not SMIRInfo._is_func(item):
                continue
            # skip functions not present in the `function_symbols_reverse` table
            if sym not in self.function_symbols_reverse:
                continue
            body = item['mono_item_kind']['MonoItemFn'].get('body')
            if body is None or 'blocks' not in body:
                # No MIR body means we cannot extract call edges; treat as having no outgoing edges.
                _LOGGER.debug(f'Skipping call edge extraction for {sym}: missing body')
                called_tys: set[Ty] = set()
            else:
                called_tys = set()
                for block in body['blocks']:
                    terminator = block['terminator']['kind']

                    if 'Call' in terminator:
                        call = terminator['Call']

                        # 1. Direct call: the function being called
                        func = call['func']
                        if 'Constant' in func:
                            called_tys.add(Ty(func['Constant']['const_']['ty']))

                        # 2. Indirect call: function pointers passed as arguments
                        #    These are ZeroSized constants whose ty is in the function table
                        for arg in call.get('args', []):
                            if 'Constant' in arg:
                                const_ = arg['Constant'].get('const_', {})
                                if const_.get('kind') == 'ZeroSized':
                                    ty = const_.get('ty')
                                    if isinstance(ty, int) and ty in function_tys:
                                        called_tys.add(Ty(ty))

                    if 'Drop' in terminator:
                        drop = terminator['Drop']
                        drop_ty = self._place_ty(body, drop['place'])
                        if drop_ty is None:
                            continue
                        drop_fn_ty = self.drop_function_tys.get(drop_ty)
                        if drop_fn_ty is not None:
                            called_tys.add(drop_fn_ty)

            for ty in self.function_symbols_reverse[sym]:
                result[Ty(ty)] = called_tys
        return result

    def _place_ty(self, body: dict, place: dict) -> Ty | None:
        local = place.get('local')
        if not isinstance(local, int):
            return None
        locals_ = body.get('locals', [])
        if not (0 <= local < len(locals_)):
            return None

        current_ty: Ty | None = Ty(locals_[local]['ty'])
        for projection in place.get('projection', []):
            assert current_ty is not None
            current_ty = self._projected_ty(current_ty, projection)
            if current_ty is None:
                return None

        return current_ty

    def _projected_ty(self, ty: Ty, projection: object) -> Ty | None:
        type_info = self.types.get(ty)
        if type_info is None:
            return None

        if projection == 'Deref':
            if isinstance(type_info, (PtrT, RefT)):
                return Ty(type_info.pointee_type)
            return None

        if not isinstance(projection, dict):
            return None

        if 'Field' in projection:
            index, field_ty = projection['Field']
            if isinstance(field_ty, int):
                return Ty(field_ty)

            if isinstance(type_info, (StructT, UnionT)):
                fields = type_info.fields
            elif isinstance(type_info, TupleT):
                fields = type_info.components
            elif isinstance(type_info, EnumT):
                # Field projection into enums is only well-defined after a downcast.
                return None
            else:
                return None

            if 0 <= index < len(fields):
                return Ty(fields[index])
            return None

        if 'Index' in projection and isinstance(type_info, ArrayT):
            return Ty(type_info.element_type)

        if 'ConstantIndex' in projection and isinstance(type_info, ArrayT):
            return Ty(type_info.element_type)

        if 'Subslice' in projection and isinstance(type_info, ArrayT):
            sub = projection['Subslice']
            from_idx = sub.get('from', 0)
            to_idx = sub.get('to', 0)
            from_end = sub.get('from_end', False)

            if from_end:
                # [from .. len-to]: result length depends on runtime size
                if type_info.length is not None:
                    result_len = type_info.length - from_idx - to_idx
                else:
                    result_len = None
            else:
                # [from .. to]: result length = to - from
                result_len = to_idx - from_idx

            # Search for an ArrayType with matching element type and length
            if result_len is not None:
                for candidate_ty, candidate_info in self.types.items():
                    if (
                        isinstance(candidate_info, ArrayT)
                        and candidate_info.element_type == type_info.element_type
                        and candidate_info.length == result_len
                    ):
                        return candidate_ty
            return ty

        if 'OpaqueCast' in projection or 'Subtype' in projection:
            key = 'OpaqueCast' if 'OpaqueCast' in projection else 'Subtype'
            cast_ty = projection[key]
            return Ty(cast_ty) if isinstance(cast_ty, int) else None

        if 'Downcast' in projection:
            return ty

        return None


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
