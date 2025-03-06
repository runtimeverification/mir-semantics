from __future__ import annotations

import os
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CTerm, cterm_build_claim
from pyk.kast.inner import KApply, KSort, Subst
from pyk.kast.manip import split_config_from
from pyk.kast.outer import KFlatModule, KImport

from kmir.build import haskell_semantics, llvm_semantics
from kmir.convert_from_definition.__main__ import parse_mir_klist_json
from kmir.convert_from_definition.v2parser import parse_json

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyk.kast.inner import KToken


@dataclass
class KMirOpts: ...


@dataclass
class RunOpts(KMirOpts):
    input_files: list[Path]
    depth: int
    start_symbol: str
    start_crate: str
    haskell_backend: bool


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


def _kmir_run(opts: RunOpts) -> None:
    tools = haskell_semantics() if opts.haskell_backend else llvm_semantics()

    # TODO: Same as comment in convert_from_definition::__main__.py - args.sort might not be right
    results = [parse_json(tools.definition, input_file, 'Crate') for input_file in opts.input_files]

    failed = []
    passed: list[tuple[KApply | KToken, KSort]] = []

    for index, result in enumerate(results):
        if result is None:
            failed.append(opts.input_files[index])
        else:
            passed.append(result)

    if failed:
        for failure in failed:
            print(f'Parse error! In {failure}', file=sys.stderr)
        sys.exit(1)

    terms, _sort = parse_mir_klist_json(passed, KSort('Crate'))

    start_crate = extract_crate_name(opts.input_files[0]) if len(opts.input_files) == 1 else opts.start_crate

    run_result = tools.run_parsed(terms, opts.start_symbol, start_crate, opts.depth)

    print(tools.kprint.kore_to_pretty(run_result))


def extract_crate_name(file_path: Path) -> str:
    filename = os.path.basename(file_path)
    return filename.removesuffix('.smir.json')


def _kmir_gen_spec(opts: GenSpecOpts) -> None:
    tools = haskell_semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Crate')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result
    config = tools.make_init_config(kmir_kast, opts.start_symbol)
    config_with_cell_vars, _ = split_config_from(config)

    lhs = CTerm(config)
    new_k_cell = tools.kmir.Symbols.END_PROGRAM
    rhs = CTerm(Subst({'K_CELL': new_k_cell})(config_with_cell_vars))
    claim, _ = cterm_build_claim(opts.input_file.stem, lhs, rhs)

    output_file = opts.output_file
    if output_file is None:
        output_file = opts.input_file.with_suffix('.spec.json')

    spec_module = KFlatModule(
        opts.input_file.stem.upper().replace('.', '-').replace('_', '-'), (claim,), (KImport('KMIR'),)
    )

    output_file.write_text(spec_module.to_json())


def kmir(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case GenSpecOpts():
            _kmir_gen_spec(opts)
        case _:
            raise AssertionError()


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir')

    command_parser = parser.add_subparsers(dest='command', required=True)

    run_parser = command_parser.add_parser('run', help='run stable MIR programs')
    run_parser.add_argument('input_file', metavar='FILE', nargs='+', help='MIR program to run')
    run_parser.add_argument('--depth', type=int, metavar='DEPTH', help='Depth to execute')
    run_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )
    run_parser.add_argument(
        '--start-crate', type=str, metavar='START_CRATE', default='main', help='Crate name to begin execution from'
    )
    run_parser.add_argument('--haskell-backend', action='store_true', help='Run with the haskell backend')

    gen_spec_parser = command_parser.add_parser('gen-spec', help='Generate a k spec from a SMIR json')
    gen_spec_parser.add_argument('input_file', metavar='FILE', help='MIR program to generate a spec for')
    gen_spec_parser.add_argument('--output-file', metavar='FILE', help='Output file')
    gen_spec_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    return parser


def _parse_args(args: Sequence[str]) -> KMirOpts:
    ns = _arg_parser().parse_args(args)

    match ns.command:
        case 'run':
            return RunOpts(
                input_files=[Path(file).resolve() for file in ns.input_file],
                depth=ns.depth,
                start_symbol=ns.start_symbol,
                start_crate=ns.start_crate,
                haskell_backend=ns.haskell_backend,
            )
        case 'gen-spec':
            return GenSpecOpts(
                input_file=Path(ns.input_file).resolve(), output_file=ns.output_file, start_symbol=ns.start_symbol
            )
        case _:
            raise AssertionError()


def main() -> None:
    kmir(sys.argv[1:])
