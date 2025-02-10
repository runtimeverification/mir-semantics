from __future__ import annotations

import json
from collections.abc import Sequence
from functools import cached_property
from typing import TYPE_CHECKING

from pyk.kast.att import Atts
from pyk.kast.inner import KApply, KSort, KToken
from pyk.kast.outer import KTerminal

if TYPE_CHECKING:
    from pathlib import Path

    from pyk.kast.outer import KDefinition, KProduction

# Expected json
JSON = dict | str | int | bool | Sequence | None
ParseResult = tuple[KApply | KToken, KSort] | None


def parse_json(definition: KDefinition, json_file: Path, sort: str) -> ParseResult:
    p = Parser(definition)

    with open(json_file, 'r') as f:
        json_data = json.load(f)

    result = p.parse_mir_json(json_data, sort)

    return result


# Return true if a production has been annotated with a mir* group
def _is_mir_production(prod: KProduction) -> bool:
    group = prod.att.get(Atts.GROUP)
    return group is not None and group.startswith('mir')


# If a production has a symbol, return its symbol. Otherwise, return its klabel
# Used when we do not need to identify a production by its symbol, we simply
# intend to construct a KApply using the returned label.
# Therefore, the label's format is of no concequence.
def _get_label(prod: KProduction) -> str:
    symbol = prod.att.get(Atts.SYMBOL)
    if symbol is not None:
        return symbol
    label = prod.klabel
    assert label
    return label.name


# Return a production's symbol, asserting that it has one.
# Used when we need to be able to automatically construct a symbol for the
# production we intend to use (enumerations and terminals). Therefore, we
# provide symbols in the MIR semantics constructed from information that is
# available here to reconstruct the symbols.
def _get_symbol(prod: KProduction) -> str:
    symbol = prod.att.get(Atts.SYMBOL)
    assert symbol
    return symbol


# Return the group that a mir production belongs in as a string
def _get_group(prod: KProduction) -> str:
    group = prod.att.get(Atts.GROUP)
    assert group
    return group


# Parse a mir production's group information.
# Return a tuple (mir production's type, list of field names)
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


# Return true if the mir production's group includes field names.
def _has_named_fields(group_info: str) -> bool:
    return '---' in group_info


def _is_mir_terminal(prod: KProduction) -> bool:
    return _is_mir_production(prod) and len(prod.items) == 1 and isinstance(prod.items[0], KTerminal)


# Return the symbol sort::value for a terminal of Sort name sort, and value
# value.
def _terminal_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


# Return the symbol sort::value for a mir-enum production of Sort name sort
# with value value. The value is expected to be the name of an enumerator for
# the corresponding Sort, as shown in json.
def _enum_symbol(sort: str, value: str) -> str:
    return f'{sort}::{value}'


# Return the symbols sort::apend, sort::empty for a list of Sort name sort.
def _list_symbols(sort: str) -> tuple[str, str]:
    return (f'{sort}::append', f'{sort}::empty')


# Given a list Sort, return the element sort.
def _element_sort(sort: KSort) -> KSort:
    name = sort.name
    if name.endswith('ies'):  # Bodies, Entries, ...
        return KSort(name[:-3] + 'y')
    elif (  # -es for words ending in 's', 'ch', 'sh', 'ss', 'x' or 'z'
        name.endswith('ses')
        or name.endswith('ches')
        or name.endswith('shes')
        or name.endswith('sses')
        or name.endswith('xes')
        or name.endswith('zes')
    ):
        return KSort(name[:-2])
    elif name.endswith('Indices'):
        return KSort(name[:-7] + 'Index')
    # If the name is not lsted above, we assume it has a regular plural form.
    # Simply remove trailing 's' to get the singular for element sort name.
    assert name.endswith('s')
    return KSort(name[:-1])


class Parser:
    __definition: KDefinition

    def __init__(
        self,
        defn: KDefinition,
    ):
        self.__definition = defn

    # Return all mir productions for Sort sort
    def _mir_productions_for_sort(self, sort: KSort) -> tuple[KProduction, ...]:
        return tuple(p for p in self._mir_productions if p.sort == sort)

    # Return the mir production with Sort sort name and label symbol.
    # Note: the symbol is (and should be) unique, and would be enough to
    # uniquely identify the production. This functions is written this way to
    # limit the search only to relevant productions of the correct Sort,
    # aiming for optimization (cache?) in the future.
    def _mir_production_for_symbol(self, sort: KSort, symbol: str) -> KProduction:
        prods = [p for p in self._mir_productions_for_sort(sort) if _get_label(p) == symbol]
        assert len(prods) > 0, f"No production for `{symbol}' in sort `{sort.name}'"
        assert len(prods) == 1, f"Expected a single production for `{symbol}' as sort `{sort.name}'"
        return prods[0]

    # Parse the provided json term, with expected Sort name sort.
    # This is the parser's interface,
    def parse_mir_json(self, json: JSON, sort: str) -> ParseResult:
        return self._parse_mir_json(json, KSort(sort))

    # Parser's top level internal method,
    # Parse the provided json term, with expected Sort sort.
    def _parse_mir_json(self, json: JSON, sort: KSort) -> ParseResult:
        # Identify a single production of Sort sort.
        # It shouldn't matter how we pick one. If there are more than one
        # (e.g., optione, enums), the particular case can handle finding the
        # correct rule to apply. In the other cases there should only be one
        # production anyway, which is asserted as needed.
        prods = self._mir_productions_for_sort(sort)
        assert len(prods) > 0, f"Don't know how to parse sort `{sort.name}'"
        prod = prods[0]
        assert prod in self._mir_productions

        # Get the mir production's group information. Then, based on the
        # production's type, call the appropriate underlying method.
        group = _get_group(prod)
        kind, _ = _extract_mir_group_info(group)
        match kind:
            case 'mir':
                assert len(prods) == 1
                if prod in self._mir_terminals:
                    return self._parse_mir_terminal_json(json, prod)
                else:
                    assert prod in self._mir_non_terminals
                    return self._parse_mir_nonterminal_json(json, prod)
            case 'mir-enum':
                return self._parse_mir_enum_json(json, sort)
            case s if s.startswith('mir-klist'):
                element_sort_name = s.split('-')[-1]
                return self._parse_mir_klist_json(json, KSort(element_sort_name))
            case 'mir-list':
                return self._parse_mir_list_json(json, sort)
            case 'mir-option' | 'mir-option-string' | 'mir-option-int' | 'mir-option-bool':
                return self._parse_mir_option_json(json, sort)
            case 'mir-string':
                assert len(prods) == 1
                return self._parse_mir_string_json(json, prod)
            case 'mir-int':
                assert len(prods) == 1
                return self._parse_mir_int_json(json, prod)
            case 'mir-bool':
                assert len(prods) == 1
                return self._parse_mir_bool_json(json, prod)
            case 'mir-bytes':
                assert len(prods) == 1
                return self._parse_mir_bytes_json(json, prod)
            case _:
                raise AssertionError()

    # Parser's internal method,
    # Parse the provided terminal using the provided production.
    def _parse_mir_terminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, str)
        sort = prod.sort
        symbol = _terminal_symbol(sort.name, json)
        expected_symbol = _get_symbol(prod)
        # Sanity check: We check that the provided production's symbol and the
        # automatically contructed one match.
        assert symbol == expected_symbol
        return KApply(symbol), sort

    # Parser's internal method,
    # Parse the provided non terminal using the provided production.
    def _parse_mir_nonterminal_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, dict) or isinstance(json, Sequence)

        # We use the provided production to
        # - find the field names of the arguments in json, if any
        # - find the sorts of the arguments
        # - find the sort
        group = _get_group(prod)
        _, field_names = _extract_mir_group_info(group)
        symbol = _get_label(prod)
        sort = prod.sort
        # Collect the parse results of the production arguments in args
        args = []
        arg_count = 0
        for arg_sort in prod.argument_sorts:
            arg_json = None
            if isinstance(json, dict):
                # Search for the corresponding field name in json, and find
                # the associated value
                assert arg_count < len(field_names)
                key = field_names[arg_count]
                assert key in json
                arg_json = json[key]
                arg_count += 1
            else:
                # Grab the next json value
                arg_json = json[arg_count]
                arg_count += 1
            assert isinstance(arg_json, JSON)
            arg_parse_result = self._parse_mir_json(arg_json, arg_sort)
            assert isinstance(arg_parse_result, tuple)
            arg_kapply, arg_ksort = arg_parse_result
            assert arg_kapply
            assert arg_ksort
            args.append(arg_kapply)
        return KApply(symbol, args), sort

    # Parser's internal method,
    # Parse the provided json as a enum using expected Sort sort.
    def _parse_mir_enum_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, dict) or isinstance(json, str)
        if isinstance(json, dict):
            # In case of an enumeration a a dictionary, the key is the name of
            # the enumerator. Find the name, and use it to construct the symbol
            # of the associated production.
            # The associated production will be non terminal (otherwise the
            # enumeration would have been printed as a string)
            keys = list(json.keys())
            assert len(keys) == 1
            key = keys[0]
            assert isinstance(key, str)
            symbol = _enum_symbol(sort.name, key)
            json_value = json[key]
            assert isinstance(json_value, JSON)
            prod = self._mir_production_for_symbol(sort, symbol)
            assert prod in self._mir_non_terminals, f'{prod} not in mir_non_terminals'
            # Check for single-argument enums with non named argument. In this
            # case, the argument needs to be changed to a list, so that its
            # structure is not cosidered a part of the current enumeration.
            if not _has_named_fields(_get_group(prod)) and len(prod.argument_sorts) == 1:
                # str is a Sequence, therefore the extra check
                assert isinstance(json_value, str) or not isinstance(json_value, Sequence)
                json_value = [json_value]
            return self._parse_mir_nonterminal_json(json_value, prod)
        else:
            # Enum has been printed as string due to optimization.
            # Handle as a terminal.
            symbol = _enum_symbol(sort.name, json)
            prod = self._mir_production_for_symbol(sort, symbol)
            assert prod in self._mir_terminals
            return self._parse_mir_terminal_json(json, prod)

    # Parser's internal method,
    # Parse the provided json as a list using expected Sort sort.
    def _parse_mir_list_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, Sequence)
        append_symbol, empty_symbol = _list_symbols(sort.name)
        element_sort = _element_sort(sort)
        list_kapply = KApply(empty_symbol, ())
        for element in reversed(json):
            assert isinstance(element, JSON)
            element_parse_result = self._parse_mir_json(element, element_sort)
            assert isinstance(element_parse_result, tuple)
            element_kapply, _ = element_parse_result
            list_kapply = KApply(append_symbol, (element_kapply, list_kapply))
        return list_kapply, sort

    # Parser's internal method,
    # Parse the provided json as a K list using expected Sort sort for the list elements.
    def _parse_mir_klist_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert isinstance(json, Sequence)
        append_symbol = '_List_'
        empty_symbol = '.List'
        list_item_symbol = 'ListItem'
        list_kapply = KApply(empty_symbol, ())
        first_iter = True
        for element in json:
            assert isinstance(element, JSON)
            element_parse_result = self._parse_mir_json(element, sort)
            assert isinstance(element_parse_result, tuple)
            element_kapply, _ = element_parse_result
            element_list_item = KApply(list_item_symbol, (element_kapply))
            if first_iter:
                list_kapply = element_list_item
                first_iter = False
            else:
                list_kapply = KApply(append_symbol, (list_kapply, element_list_item))
        return list_kapply, sort

    # Parser's internal method,
    # Parse the provided json as an option using expected Sort sort.
    def _parse_mir_option_json(self, json: JSON, sort: KSort) -> ParseResult:
        assert (
            json is None
            or isinstance(json, dict)
            or isinstance(json, Sequence)
            or isinstance(json, str)
            or isinstance(json, int)
            or isinstance(json, bool)
        )
        # Get both productions for the option - exactly two should exist.
        prods = self._mir_productions_for_sort(sort)
        assert len(prods) == 2
        if json is None:
            # Use the terminal production for None
            tprod = prods[0] if prods[0] in self._mir_terminals else prods[1]
            tsymbol = _get_label(tprod)
            return KApply(tsymbol, ()), sort
        # Use the non terminal production otherwise
        ntprod = prods[0] if prods[0] not in self._mir_terminals else prods[1]
        ntsymbol = _get_label(ntprod)
        group = _get_group(ntprod)
        kind, _ = _extract_mir_group_info(group)
        match kind:
            case 'mir-option-string':
                # Apply the non terminal production to the generated token
                assert isinstance(json, str)
                return KApply(ntsymbol, (KToken('\"' + json + '\"', KSort('String')))), sort
            case 'mir-option-int':
                # Apply the non terminal production to the generated token
                assert isinstance(json, int)
                return KApply(ntsymbol, (KToken(str(json), KSort('Int')))), sort
            case 'mir-option-bool':
                # Apply the non terminal production to the generated token
                assert isinstance(json, bool)
                return KApply(ntsymbol, (KToken(str(json), KSort('Bool')))), sort
            case 'mir-option':
                # Parse the argument and then apply the non terminal production
                arg_sorts = ntprod.argument_sorts
                assert len(arg_sorts) == 1
                arg_sort = arg_sorts[0]
                arg_parse_result = self._parse_mir_json(json, arg_sort)
                assert isinstance(arg_parse_result, tuple)
                arg_kapply, _ = arg_parse_result
                return KApply(ntsymbol, (arg_kapply)), sort
            case _:
                raise AssertionError()

    # Parser's internal method,
    # Parse the provided json as a string using the provided production.
    def _parse_mir_string_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, str)
        sort = prod.sort
        symbol = _get_label(prod)
        # Special handling of MIRString: return the string token instead.
        if symbol == 'MIRString::String':
            return KToken('\"' + json + '\"', KSort('String')), KSort('String')
        # Apply the production to the generated string token
        return KApply(symbol, (KToken('\"' + json + '\"', KSort('String')))), sort

    # Parser's internal method,
    # Parse the provided json as an int using the provided production.
    def _parse_mir_int_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, int)
        sort = prod.sort
        symbol = _get_label(prod)
        # Special handling of MIRInt: return the int token instead.
        if symbol == 'MIRInt::Int':
            return KToken(str(json), KSort('Int')), KSort('Int')
        # Apply the production to the generated int token
        return KApply(symbol, (KToken(str(json), KSort('Int')))), sort

    # Parser's internal method,
    # Parse the provided json as a bool using the provided production.
    def _parse_mir_bool_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, bool)
        sort = prod.sort
        symbol = _get_label(prod)
        # Special handling of MIRBool: return the bool token instead.
        if symbol == 'MIRBool::Bool':
            return KToken(str(json), KSort('Bool')), KSort('Bool')
        # Apply the production to the generated bool token
        return KApply(symbol, (KToken(str(json), KSort('Bool')))), sort

    # parse a sequence of ints into a byte array
    def _parse_mir_bytes_json(self, json: JSON, prod: KProduction) -> ParseResult:
        assert isinstance(json, Sequence)

        if not json: # empty sequence, the assertion below would fail
            bytes = ""
        else:
            for i in json:
                # null values are allowed and taken to mean \x00
                assert (isinstance(i, int) or i is None)
            import string
            if all( chr(i) in string.printable for i in json):
                # if all elements are ascii printable, use simple characters
                bytes = ''.join([chr(i) for i in json])
            else:
                # otherwise convert to hexadecimal representation \xCA\xFE otherwise
                bytes = ''.join( [ f'\\x{i:02x}' if i is not None else f'\\x00' for i in json ] )
        symbol = _get_label(prod)
        if symbol == 'MIRBytes::Bytes':
            return KToken('b"' + str(bytes) + '"', KSort('Bytes')), KSort('Bytes')
        else:
            sort = prod.sort
            return KApply(symbol, (KToken('b"' + str(bytes) + '"', KSort('Bytes')), sort))

    @cached_property
    def _mir_productions(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self.__definition.productions if _is_mir_production(prod))

    @cached_property
    def _mir_terminals(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self._mir_productions if _is_mir_terminal(prod))

    @cached_property
    def _mir_non_terminals(self) -> tuple[KProduction, ...]:
        return tuple(prod for prod in self._mir_productions if not _is_mir_terminal(prod))
