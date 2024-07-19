from __future__ import annotations

from typing import TYPE_CHECKING

from pyk.kast.att import Atts
from pyk.kast.outer import KTerminal, KNonTerminal
from pyk.kast.inner import KLabel, KApply, KSort

if TYPE_CHECKING:
    from pyk.kast.outer import KProduction, KDefinition
    from pyk.kast.inner import KInner
    from typing import Callable, Any


from kmir.build import semantics


def _sort_name_to_json(sort: str) -> str:
    return {
        'IntTy': 'Int',
    }.get(sort, sort)


def _is_mir_production(prod: KProduction) -> bool:
    group = prod.att.get(Atts.GROUP)
    return group is not None and group == 'mir'


def _mir_terminal(prod: KProduction) -> str | None:
    if _is_mir_production(prod) and len(prod.items) == 1 and isinstance(prod.items[0], KTerminal):
        return prod.items[0].value

    return None

def _mir_non_terminal(prod: KProduction) -> tuple[KSort, ...] | None:
    if _is_mir_production(prod) and not _mir_terminal(prod):
        return tuple(nt.sort for nt in prod.non_terminals)

    return None


def _build_parser(defn: KDefinition) -> Callable[[dict[Any, Any]], KInner]:
    terminal_table: dict[str, dict[str, KLabel]] = {}
    non_terminal_table: dict[tuple[KSort, ...], KLabel] = {}

    for prod in defn.productions:
        if term := _mir_terminal(prod):
            sort = _sort_name_to_json(prod.sort.name)
            if sort not in terminal_table:
                terminal_table[sort] = {}

            terminal_table[sort][term] = prod.klabel

        if non_terms := _mir_non_terminal(prod):
            non_terminal_table[non_terms] = prod.klabel

    def _parse(data: dict[Any, Any]) -> KInner:
        if len(data) != 1:
            raise RuntimeError

        sort, value = list(data.items())[0]

        if isinstance(value, str):
            if sort in terminal_table:
                if value in terminal_table[sort]:
                    label = terminal_table[sort][value]
                    return KApply(label=label)

        if isinstance(value, dict):
            arg = _parse(value)
            arg_sort = KSort('IntTy') # TODO: HARD CODED!
            label = non_terminal_table[(arg_sort,)] 
            return KApply(label=label, args=[arg])

        if isinstance(value, list):
            pass

        raise RuntimeError

    return _parse


def main() -> None:
    tools = semantics()
    defn = tools.definition

    parser = _build_parser(defn)

    data = {'RigidTy': {'Int': 'I32'}}
    kast = parser(data)
    print(tools.kprint.pretty_print(kast))
