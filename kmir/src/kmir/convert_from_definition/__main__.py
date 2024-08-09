import argparse
import json
import sys

from kmir.build import semantics

from .v2parser import Parser


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('json', metavar='JSON', help='JSON data to convert')
    parser.add_argument('sort', metavar='SORT', help='Expected Sort name for the parsed term', default='pgm')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tools = semantics()
    p = Parser(tools.definition)

    result = p.parse_mir_json(json.loads(args.json), args.sort)
    if result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    term, _ = result
    print(tools.krun.pretty_print(term))
