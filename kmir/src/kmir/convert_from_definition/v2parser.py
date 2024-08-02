from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING

from pyk.kast.att import Atts
from pyk.kast.inner import KApply, KToken, KSort
from pyk.kast.outer import KTerminal

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.kast.outer import KDefinition, KProduction


JSON = dict[object, object] | str | int | Sequence[object]
ParseResult = tuple[KApply, KSort] | None


def _is_mir_production(prod: KProduction) -> bool:
    group = prod.att.get(Atts.GROUP)
    symbol = prod.att.get(Atts.SYMBOL)
    return group is not None and group.startswith('mir') and symbol is not None


def _get_symbol(prod: KProduction) -> str:
    symbol = prod.att.get(Atts.SYMBOL)
    assert symbol
    return symbol


def _get_group(prod: KProduction) -> str:
    group = prod.att.get(Atts.GROUP)
    assert group
    return group

def _extract_mir_group_info(group_info: str) -> tuple(str, Sequence[str])
    # --- separates the field names from the mir instruction kind
    # --  separates the individual field names
    # -   is a symbol for _
    tokens = group_info.split("---")
    l = len(tokens)
    assert l == 1 or l == 2
    if l == 1:
        return (tokens[0], [])
    if l == 2:
        field_name_tokens = tokens[1].split("--")
        field_names = [ s.replace("-", "_") for s in field_name_tokens ]
        return (tokens[0], field_names)

def _is_mir_terminal(prod: KProduction) -> bool:
    return _is_mir_production(prod) and len(prod.items) == 1 and isinstance(prod.items[0], KTerminal)


def _terminal_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


def _enum_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'
    

def _list_symbols(sort: str) -> Tuple[str, str]:
    return (f'{sort}::append', f'{sort}::empty')
    

def _element_sort(sort: KSort) -> KSort:
    name = sort.name
    element_name = {
        'Bodies': 'Body',
    }.get(name)
    if element_name:
        return KSort(element_name)
    assert name.endswith('s')
    return KSort(name[:-1])



class Parser:
    __definition: KDefinition

    def __init__(
        self,
        defn: KDefinition,
    ):
        self.__definition = defn

    def _mir_productions_for_sort(self, sort: KSort) -> Tuple[KProduction, ...]
        return (p for p in self._mir_productions if p.sort == sort)


    def _mir_production_for_symbol(self, sort: KSort, symbol: str) -> KProduction
        prods = [p for p in self._mir_productions_for_sort(sort) if _get_symbol(p) == symbol]
        assert len(prods) == 1
        return prods[0]


    def parse_mir_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert prod in _mir_productions

        group = _get_group(prod)
        kind, _ = _extract_mir_group_info(group)
        match kind:
            case 'mir':
                if prod in _mir_terminals:
                    return self._parse_mir_terminal_json(json, prod)
                else:
                    assert prod in _mir_non_terminals
                    return self._parse_mir_nonterminal_json(json, prod)
            case 'mir-enum':
                return self._parse_mir_enum_json(json, prod.sort)
            case 'mir-list':
                return self._parse_mir_list_json(json, prod.sort)
            case 'mir-string':
                return self._parse_mir_string_json(json, prod)
            case 'mir-int':
                return self._parse_mir_int_json(json, prod)
            case 'mir-bool':
                return self._parse_mir_bool_json(json, prod)
            case _:
               assert False


    def _parse_mir_terminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        if not isinstance(json, str):
            return None
        sort = prod.sort
        symbol = _terminal_symbol(sort.name, json)
        expected_symbol = _get_symbol(prod)
        if symbol != expected_symbol:
            return None
        return KApply(symbol), sort


    def _parse_mir_nonterminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, dict[object, object]) or isinstance(json, Sequence[object])

        group = _get_group(prod)
        _, field_names = _extract_mir_group_info(group)
        symbol = _get_symbol(prod)
        sort = prod.sort
        args = []
        arg_count = 0
        for arg_sort in prod.argument_sorts:
            arg_json = None
            if isinstance(json, dict[object, object]):
                assert arg_count < len(field_names)
                key = field_names[arg_count]
                assert key in json
                arg_json = json[key]
                arg_count += 1
            else:
                arg_json = json[arg_count]
                arg_count += 1
            arg_prods = self._mir_productions_for_sort(arg_sort)
            assert len(arg_prods) > 0
            arg_kapply, arg_ksort =  self.parse_mir_json(arg_json, arg_prods[0])
            assert arg_kapply
            assert arg_ksort
            args.append(arg_kapply)
        return KApply(symbol, args), sort


    def _parse_mir_enum_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, dict[object, object])
        keys = list(json.keys())
        assert len(keys) == 1
        key = keys[0]
        symbol = _enum_symbol(sort.name, key)
        return self._parse_mir_json(json[key], self._mir_production_for_symbol(sort, symbol))


    def _parse_mir_list_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, Sequence[object])
        append_symbol, empty_symbol = _list_symbols(sort.name)
        element_sort = _element_sort(prod.sort)
        element_prods = self._mir_productions_for_sort(element_sort)
        assert len(element_prods) > 0
        list_kapply = KApply(empty_symbol, ())
        for element in json:
            element_kapply, _ =  self.parse_mir_json(element, element_prods[0])
            list_kapply = KApply(append_symbol, (element_kapply, list_kapply))
        return list_kapply, sort


    def _parse_mir_string_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, str)
        sort = prod.sort
        symbol = _get_symbol(prod)
        return KApply(symbol, (KToken('\"' + json + '\"', KSort('String')))), sort


    def _parse_mir_int_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, int)
        sort = prod.sort
        symbol = _get_symbol(prod)
        return KApply(symbol, (KToken(str(json), KSort('Int')))), sort


    def _parse_mir_bool_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, bool)
        sort = prod.sort
        symbol = _get_symbol(prod)
        return KApply(symbol, (KToken(str(json), KSort('Bool')))), sort


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

