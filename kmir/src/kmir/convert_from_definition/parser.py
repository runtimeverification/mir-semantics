from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from pyk.kast.att import Atts
from pyk.kast.inner import KApply, KSort
from pyk.kast.outer import KTerminal

if TYPE_CHECKING:
    from pyk.kast.outer import KDefinition, KProduction


JSON = dict[object, object]
ParseResult = tuple[KApply, KSort] | None


def _is_mir_production(prod: KProduction) -> bool:
    group = prod.att.get(Atts.GROUP)
    symbol = prod.att.get(Atts.SYMBOL)
    return group is not None and group == 'mir' and symbol is not None


def _get_symbol(prod: KProduction) -> str:
    symbol = prod.att.get(Atts.SYMBOL)
    assert symbol
    return symbol


def _is_mir_terminal(prod: KProduction) -> bool:
    return _is_mir_production(prod) and len(prod.items) == 1 and isinstance(prod.items[0], KTerminal)


def _json_terminal(json: JSON) -> tuple[str, str] | None:
    if len(json) != 1:
        return None

    (k, v), *_ = list(json.items())
    if not isinstance(k, str) or not isinstance(v, str):
        return None

    return (k, v)


def _json_non_terminal(json: JSON) -> tuple[str, object] | None:
    if len(json) != 1:
        return None

    (k, v), *_ = list(json.items())
    if not isinstance(k, str):
        return None

    return (k, v)


def _terminal_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


def _sort_name_from_json(sort: str) -> str:
    return {
        'Int': 'IntTy',
        'Uint': 'UintTy',
        'Float': 'FloatTy',
    }.get(sort, sort)


def _non_terminal_sorts(prod: KProduction) -> tuple[KSort, ...]:
    return (prod.sort,) + tuple(nt.sort for nt in prod.non_terminals)


class Parser:
    __definition: KDefinition

    def __init__(
        self,
        defn: KDefinition,
    ):
        self.__definition = defn

    def parse_mir_json(self, json: JSON) -> ParseResult:
        maybe_terminal = self._parse_terminal(json)
        if maybe_terminal is not None:
            return maybe_terminal

        maybe_non_terminal = self._parse_non_terminal(json)
        if maybe_non_terminal is not None:
            return maybe_non_terminal

        return self._parse_other(json)

    def _parse_terminal(self, json: JSON) -> ParseResult:
        maybe_terminal = _json_terminal(json)
        if maybe_terminal is None:
            return None

        sort, value = maybe_terminal
        sort = _sort_name_from_json(sort)

        symbol = _terminal_symbol(sort, value)
        if symbol not in self._mir_terminal_symbols:
            return None

        return KApply(symbol), KSort(sort)

    def _parse_non_terminal(self, json: JSON) -> ParseResult:
        maybe_non_terminal = _json_non_terminal(json)
        if maybe_non_terminal is None:
            return None

        sort, sub_object = maybe_non_terminal
        sort = _sort_name_from_json(sort)

        if not isinstance(sub_object, dict):
            return None

        # TODO: this will need a different entrypoint when you have N > 1
        # children; it'll do for now
        maybe_child = self.parse_mir_json(sub_object)
        if maybe_child is None:
            return None

        child_value, child_sort = maybe_child
        if (child_sort,) not in self._mir_non_terminal_symbols:
            return None

        symbol = self._mir_non_terminal_symbols[(child_sort,)]

        return KApply(symbol, args=(child_value,)), KSort(sort)

    def _parse_other(self, json: JSON) -> ParseResult:
        return None

    @cached_property
    def _mir_productions(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self.__definition.productions if _is_mir_production(prod))

    @cached_property
    def _mir_terminals(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self._mir_productions if _is_mir_terminal(prod))

    @cached_property
    def _mir_non_terminals(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self._mir_productions if not _is_mir_terminal(prod))

    @cached_property
    def _mir_terminal_symbols(self) -> set[str]:
        return {_get_symbol(prod) for prod in self._mir_terminals}

    @cached_property
    def _mir_non_terminal_symbols(self) -> dict[tuple[KSort, ...], str]:
        return {tuple(_non_terminal_sorts(p)): _get_symbol(p) for p in self._mir_non_terminals}
