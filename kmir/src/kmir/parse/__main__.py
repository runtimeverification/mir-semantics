import argparse
import sys
from pathlib import Path

from ..build import LLVM_DEF_DIR
from ..kmir import KMIR
from .parser import parse_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('json', metavar='JSON', help='JSON data to convert')
    parser.add_argument('sort', metavar='SORT', help='Expected Sort name for the parsed term', default='pgm')
    return parser.parse_args()


def main() -> None:
    sys.setrecursionlimit(10000000)
    args = parse_args()
    kmir = KMIR(LLVM_DEF_DIR)

    result = parse_json(kmir.definition, Path(args.json), args.sort)

    if result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    term, _ = result
    print(kmir.pretty_print(term))
