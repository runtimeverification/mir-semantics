import argparse
import sys
from pathlib import Path

from kmir.build import semantics

from .v2parser import parse_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('json', metavar='JSON', help='JSON data to convert')
    parser.add_argument('sort', metavar='SORT', help='Expected Sort name for the parsed term', default='pgm')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tools = semantics()

    result = parse_json(tools.definition, Path(args.json), args.sort)

    if result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    term, _ = result
    print(tools.krun.pretty_print(term))
