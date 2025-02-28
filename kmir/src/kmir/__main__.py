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
from pyk.proof.reachability import APRProof, APRProver

from kmir.build import HASKELL_DEF_DIR, LLVM_LIB_DIR, semantics
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
    proof_dir: Path | None
    include_labels: tuple[str, ...] | None
    exclude_labels: tuple[str, ...] | None

    def __init__(self, spec_file: Path, proof_dir: str | None, include_labels: str, exclude_labels: str) -> None:
        self.spec_file = spec_file
        if proof_dir is None:
            self.proof_dir = None
        else:
            self.proof_dir = Path(proof_dir).resolve()
        self.include_labels = tuple(include_labels.split(',')) if include_labels is not None else None
        self.exclude_labels = tuple(exclude_labels.split(',')) if exclude_labels is not None else None


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
        suffixes = ''.join(opts.input_file.suffixes)
        base = opts.input_file.name.removesuffix(suffixes)
        output_file = Path(f'{base}-spec.k')

    module_name = output_file.stem.upper().replace('_', '-')
    spec_module = KFlatModule(module_name, (claim,), (KImport('KMIR'),))

    output_file.write_text(tools.kprint.pretty_print(spec_module))


def _kmir_prove(opts: ProveOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
    claim_index = kmir.get_claim_index(opts.spec_file)
    labels = claim_index.labels(include=opts.include_labels, exclude=opts.exclude_labels)
    for label in labels:
        print(f'Proving {label}')
        claim = claim_index[label]
        proof = APRProof.from_claim(kmir.definition, claim, {}, proof_dir=opts.proof_dir)
        with kmir.kcfg_explore() as kcfg_explore:
            prover = APRProver(kcfg_explore)
            prover.advance_proof(proof)
        summary = proof.summary
        print(f'{summary}')


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
    prove_parser.add_argument('--proof-dir', metavar='DIR', help='Proof directory')
    prove_parser.add_argument(
        '--include-labels', metavar='LABELS', help='Comma separated list of claim labels to include'
    )
    prove_parser.add_argument(
        '--exclude-labels', metavar='LABELS', help='Comma separated list of claim labels to exclude'
    )

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
            return ProveOpts(
                spec_file=Path(ns.input_file).resolve(),
                proof_dir=ns.proof_dir,
                include_labels=ns.include_labels,
                exclude_labels=ns.exclude_labels,
            )
        case _:
            raise AssertionError()


def main() -> None:
    kmir(sys.argv[1:])
