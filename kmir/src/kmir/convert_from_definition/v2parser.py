from __future__ import annotations

from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING

from pyk.kast.att import Atts
from pyk.kast.inner import KApply, KSort, KToken
from pyk.kast.outer import KTerminal

if TYPE_CHECKING:
    from pyk.kast.outer import KDefinition, KProduction


JSON = dict[object, object] | str | int | bool | Sequence[object]
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


def _extract_mir_group_info(group_info: str) -> tuple[str, Sequence[str]]:
    # --- separates the field names from the mir instruction kind
    # --  separates the individual field names
    # -   is a symbol for _
    tokens = group_info.split('---')
    l = len(tokens)
    assert l == 1 or l == 2
    if l == 1:
        return (tokens[0], [])
    field_name_tokens = tokens[1].split('--')
    field_names = [s.replace('-', '_') for s in field_name_tokens]
    return (tokens[0], field_names)


def _is_mir_terminal(prod: KProduction) -> bool:
    return _is_mir_production(prod) and len(prod.items) == 1 and isinstance(prod.items[0], KTerminal)


def _terminal_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


def _enum_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


def _list_symbols(sort: str) -> tuple[str, str]:
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

    def _mir_productions_for_sort(self, sort: KSort) -> tuple[KProduction, ...]:
        return tuple(p for p in self._mir_productions if p.sort == sort)

    def _mir_production_for_symbol(self, sort: KSort, symbol: str) -> KProduction:
        prods = [p for p in self._mir_productions_for_sort(sort) if _get_symbol(p) == symbol]
        assert len(prods) == 1
        return prods[0]

    def parse_mir_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert prod in self._mir_productions

        group = _get_group(prod)
        kind, _ = _extract_mir_group_info(group)
        match kind:
            case 'mir':
                if prod in self._mir_terminals:
                    return self._parse_mir_terminal_json(json, prod)
                else:
                    assert prod in self._mir_non_terminals
                    return self._parse_mir_nonterminal_json(json, prod)
            case 'mir-enum':
                return self._parse_mir_enum_json(json, prod.sort)
            case 'mir-list':
                return self._parse_mir_list_json(json, prod.sort)
            case 'mir-option' | 'mir-option-string' | 'mir-option-int' | 'mir-option-bool':
                return self._parse_mir_option_json(json, prod.sort)
            case 'mir-string':
                return self._parse_mir_string_json(json, prod)
            case 'mir-int':
                return self._parse_mir_int_json(json, prod)
            case 'mir-bool':
                return self._parse_mir_bool_json(json, prod)
            case _:
                raise AssertionError()

    def _parse_mir_terminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, str)
        sort = prod.sort
        symbol = _terminal_symbol(sort.name, json)
        expected_symbol = _get_symbol(prod)
        assert symbol == expected_symbol
        return KApply(symbol), sort

    def _parse_mir_nonterminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, dict) or isinstance(json, Sequence)

        group = _get_group(prod)
        _, field_names = _extract_mir_group_info(group)
        symbol = _get_symbol(prod)
        sort = prod.sort
        args = []
        arg_count = 0
        for arg_sort in prod.argument_sorts:
            arg_json = None
            if isinstance(json, dict):
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
            assert isinstance(arg_json, JSON)
            arg_parse_result = self.parse_mir_json(arg_json, arg_prods[0])
            assert isinstance(arg_parse_result, tuple)
            arg_kapply, arg_ksort = arg_parse_result
            assert arg_kapply
            assert arg_ksort
            args.append(arg_kapply)
        return KApply(symbol, args), sort

    def _parse_mir_enum_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, dict)
        keys = list(json.keys())
        assert len(keys) == 1
        key = keys[0]
        assert isinstance(key, str)
        symbol = _enum_symbol(sort.name, key)
        json_value = json[key]
        assert isinstance(json_value, JSON)
        return self.parse_mir_json(json_value, self._mir_production_for_symbol(sort, symbol))

    def _parse_mir_list_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, Sequence)
        append_symbol, empty_symbol = _list_symbols(sort.name)
        element_sort = _element_sort(sort)
        element_prods = self._mir_productions_for_sort(element_sort)
        assert len(element_prods) > 0
        list_kapply = KApply(empty_symbol, ())
        for element in json:
            assert isinstance(element, JSON)
            element_parse_result = self.parse_mir_json(element, element_prods[0])
            assert isinstance(element_parse_result, tuple)
            element_kapply, _ = element_parse_result
            list_kapply = KApply(append_symbol, (element_kapply, list_kapply))
        return list_kapply, sort

    def _parse_mir_option_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert (
            json is None
            or isinstance(json, dict)
            or isinstance(json, Sequence)
            or isinstance(json, str)
            or isinstance(json, int)
            or isinstance(json, bool)
        )
        prods = self._mir_productions_for_sort(sort)
        assert len(prods) == 2
        if json is None:
            tprod = prods[0] if prods[0] in self._mir_terminals else prods[1]
            tsymbol = _get_symbol(tprod)
            return KApply(tsymbol, ()), sort
        ntprod = prods[0] if prods[0] not in self._mir_terminals else prods[1]
        ntsymbol = _get_symbol(ntprod)
        group = _get_group(ntprod)
        kind, _ = _extract_mir_group_info(group)
        match kind:
            case 'mir-option-string':
                assert isinstance(json, str)
                return KApply(ntsymbol, (KToken('\"' + json + '\"', KSort('String')))), sort
            case 'mir-option-int':
                assert isinstance(json, int)
                return KApply(ntsymbol, (KToken(str(json), KSort('Int')))), sort
            case 'mir-option-bool':
                assert isinstance(json, bool)
                return KApply(ntsymbol, (KToken(str(json), KSort('Bool')))), sort
            case 'mir-option':
                arg_sorts = ntprod.argument_sorts
                assert len(arg_sorts) == 1
                arg_sort = arg_sorts[0]
                arg_prods = self._mir_productions_for_sort(arg_sort)
                assert len(arg_prods) > 0
                arg_parse_result = self.parse_mir_json(json, arg_prods[0])
                assert isinstance(arg_parse_result, tuple)
                arg_kapply, _ = arg_parse_result
                return KApply(ntsymbol, (arg_kapply)), sort
            case _:
                raise AssertionError()

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
