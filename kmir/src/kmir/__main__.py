from __future__ import annotations

import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CTerm, cterm_build_claim
from pyk.kast.inner import Subst
from pyk.kast.manip import split_config_from
from pyk.kast.outer import KFlatModule, KImport

from kmir.build import semantics
from kmir.convert_from_definition.v2parser import parse_json
from kmir.kmir import KMIR

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class KMirOpts: ...


@dataclass
class RunOpts(KMirOpts):
    input_file: Path
    depth: int
    start_symbol: str


@dataclass
class GenSpecOpts(KMirOpts):
    input_file: Path
    output_file: Path | None
    start_symbol: str

    def __init__(self, input_file: Path, output_file: str | None, start_symbol: str) -> None:
        self.input_file = input_file
        if output_file is None:
            self.output_file = None
        else:
            self.output_file = Path(output_file).resolve()
        self.start_symbol = start_symbol


@dataclass
class ProveOpts(KMirOpts):
    spec_file: Path


def _kmir_run(opts: RunOpts) -> None:
    tools = semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result

    result = tools.run_parsed(kmir_kast, opts.start_symbol, opts.depth)

    print(tools.kprint.kore_to_pretty(result))


def _kmir_gen_spec(opts: GenSpecOpts) -> None:
    tools = semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result
    config = tools.make_init_config(kmir_kast, opts.start_symbol)
    config_with_cell_vars, _ = split_config_from(config)

    lhs = CTerm(config)
    new_k_cell = KMIR.Symbols.END_PROGRAM
    rhs = CTerm(Subst({'K_CELL': new_k_cell})(config_with_cell_vars))
    claim, _ = cterm_build_claim(opts.input_file.stem, lhs, rhs)

    output_file = opts.output_file
    if output_file is None:
        output_file = opts.input_file.with_suffix('.spec.json')

    spec_module = KFlatModule(
        opts.input_file.stem.upper().replace('.', '-').replace('_', '-'), (claim,), (KImport('KMIR'),)
    )

    output_file.write_text(spec_module.to_json())


def _kmir_prove(opts: ProveOpts) -> None:
    print(f'proving {opts.spec_file}')


def kmir(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case GenSpecOpts():
            _kmir_gen_spec(opts)
        case ProveOpts():
            _kmir_prove(opts)
        case _:
            raise AssertionError()


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir')

    command_parser = parser.add_subparsers(dest='command', required=True)

    run_parser = command_parser.add_parser('run', help='run stable MIR programs')
    run_parser.add_argument('input_file', metavar='FILE', help='MIR program to run')
    run_parser.add_argument('--depth', type=int, metavar='DEPTH', help='Depth to execute')
    run_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    gen_spec_parser = command_parser.add_parser('gen-spec', help='Generate a k spec from a SMIR json')
    gen_spec_parser.add_argument('input_file', metavar='FILE', help='MIR program to generate a spec for')
    gen_spec_parser.add_argument('--output-file', metavar='FILE', help='Output file')
    gen_spec_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    prove_parser = command_parser.add_parser('prove', help='Run the prover on a spec')
    prove_parser.add_argument('input_file', metavar='FILE', help='File with the json spec module')

    return parser


def _parse_args(args: Sequence[str]) -> KMirOpts:
    ns = _arg_parser().parse_args(args)

    match ns.command:
        case 'run':
            return RunOpts(input_file=Path(ns.input_file).resolve(), depth=ns.depth, start_symbol=ns.start_symbol)
        case 'gen-spec':
            return GenSpecOpts(
                input_file=Path(ns.input_file).resolve(), output_file=ns.output_file, start_symbol=ns.start_symbol
            )
        case 'prove':
            return ProveOpts(spec_file=Path(ns.input_file).resolve())
        case _:
            raise AssertionError()


def main() -> None:
    kmir(sys.argv[1:])
