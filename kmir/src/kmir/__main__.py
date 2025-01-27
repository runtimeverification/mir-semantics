from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kast.inner import KSort, Subst

from kmir.build import semantics
from kmir.convert_from_definition.v2parser import parse_json

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class KMirOpts: ...


@dataclass
class RunOpts(KMirOpts):
    input_file: Path


def _kmir_run(opts: RunOpts) -> None:
    tools = semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result

    subst = Subst({'$PGM': kmir_kast})
    init_config = subst.apply(tools.definition.init_config(KSort('GeneratedTopCell')))
    init_kore = tools.krun.kast_to_kore(init_config, KSort('GeneratedTopCell'))
    result = tools.krun.run_pattern(init_kore)

    print(tools.kprint.kore_to_pretty(result))


def kmir(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case _:
            raise AssertionError()


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir')

    command_parser = parser.add_subparsers(dest='command', required=True)

    run_parser = command_parser.add_parser('run', help='run stable MIR programs')
    run_parser.add_argument('input_file', metavar='FILE', help='MIR program to run')

    return parser


def _parse_args(args: Sequence[str]) -> KMirOpts:
    ns = _arg_parser().parse_args(args)

    match ns.command:
        case 'run':
            return RunOpts(input_file=Path(ns.input_file).resolve())
        case _:
            raise AssertionError()


def main() -> None:
    kmir(sys.argv[1:])
