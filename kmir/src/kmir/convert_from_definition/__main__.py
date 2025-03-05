from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KSort

if TYPE_CHECKING:
    from pyk.kast.inner import KToken

from kmir.build import llvm_semantics

from .v2parser import parse_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'json', metavar='JSON', nargs='+', help='JSON data to convert, add multiple files for cross-crate'
    )
    parser.add_argument('sort', metavar='SORT', help='Expected Sort name for the parsed term', default='Crate')
    return parser.parse_args()


# This is essentially just a duplicate of `Parser` method `_parse_mir_klist_json`
def parse_mir_klist_json(crates: list[tuple[KApply | KToken, KSort]], sort: KSort) -> tuple[KApply, KSort]:
    append_symbol = '_List_'
    empty_symbol = '.List'
    list_item_symbol = 'ListItem'
    list_kapply = KApply(empty_symbol, ())
    first_iter = True
    for element_kapply, _ in crates:
        element_list_item = KApply(list_item_symbol, (element_kapply))
        if first_iter:
            list_kapply = element_list_item
            first_iter = False
        else:
            list_kapply = KApply(append_symbol, (list_kapply, element_list_item))
    return list_kapply, sort


def main() -> None:
    args = parse_args()
    tools = llvm_semantics()

    # TODO: args.sort might not be right
    results = [parse_json(tools.definition, Path(json), args.sort) for json in args.json]

    failed = []
    passed: list[tuple[KApply | KToken, KSort]] = []

    for index, result in enumerate(results):
        if result is None:
            failed.append(args.json[index])
        else:
            passed.append(result)

    if failed:
        for failure in failed:
            print(f'Parse error! In {failure}', file=sys.stderr)
        sys.exit(1)

    terms, _sort = parse_mir_klist_json(passed, KSort('Crate'))

    print(tools.krun.pretty_print(terms))
