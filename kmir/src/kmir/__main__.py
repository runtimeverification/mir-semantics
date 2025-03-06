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
from pyk.proof.tui import APRProofViewer

from kmir.build import HASKELL_DEF_DIR, LLVM_LIB_DIR, haskell_semantics, llvm_semantics
from kmir.convert_from_definition.v2parser import parse_json
from kmir.kmir import KMIR, KMIRAPRNodePrinter

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class KMirOpts: ...


@dataclass
class RunOpts(KMirOpts):
    input_file: Path
    depth: int
    start_symbol: str
    haskell_backend: bool


@dataclass
class GenSpecOpts(KMirOpts):
    input_file: Path
    output_file: Path | None
    start_symbol: str

    def __init__(self, input_file: Path, output_file: Path | str | None, start_symbol: str) -> None:
        self.input_file = input_file
        if output_file is None:
            self.output_file = None
        else:
            self.output_file = Path(output_file).resolve()
        self.start_symbol = start_symbol


@dataclass
class ProveRunOpts(KMirOpts):
    spec_file: Path
    proof_dir: Path | None
    include_labels: tuple[str, ...] | None
    exclude_labels: tuple[str, ...] | None
    bug_report: Path | None

    def __init__(
        self,
        spec_file: Path,
        proof_dir: Path | str | None,
        include_labels: str | None,
        exclude_labels: str | None,
        bug_report: Path | None = None,
    ) -> None:
        self.spec_file = spec_file
        self.proof_dir = Path(proof_dir).resolve() if proof_dir is not None else None
        self.include_labels = tuple(include_labels.split(',')) if include_labels is not None else None
        self.exclude_labels = tuple(exclude_labels.split(',')) if exclude_labels is not None else None
        self.bug_report = bug_report


@dataclass
class ProveViewOpts(KMirOpts):
    spec_file: Path
    proof_dir: Path | None
    id: str


def _kmir_run(opts: RunOpts) -> None:
    tools = haskell_semantics() if opts.haskell_backend else llvm_semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result

    result = tools.run_parsed(kmir_kast, opts.start_symbol, opts.depth)

    print(tools.kprint.kore_to_pretty(result))


def _kmir_gen_spec(opts: GenSpecOpts) -> None:
    tools = haskell_semantics()

    parse_result = parse_json(tools.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result
    config = tools.make_init_config(kmir_kast, opts.start_symbol, 'KmirCell')
    config_with_cell_vars, _ = split_config_from(config)

    lhs = CTerm(config)
    new_k_cell = KMIR.Symbols.END_PROGRAM
    rhs = CTerm(Subst({'K_CELL': new_k_cell})(config_with_cell_vars))
    claim, _ = cterm_build_claim(opts.input_file.stem.replace('_', '-'), lhs, rhs)

    output_file = opts.output_file
    if output_file is None:
        suffixes = ''.join(opts.input_file.suffixes)
        base = opts.input_file.name.removesuffix(suffixes)
        output_file = Path(f'{base}-spec.k')

    module_name = output_file.stem.upper().replace('_', '-')
    spec_module = KFlatModule(module_name, (claim,), (KImport('KMIR'),))

    output_file.write_text(tools.kprint.pretty_print(spec_module))


def _kmir_prove_run(opts: ProveRunOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR, bug_report=opts.bug_report)
    claim_index = kmir.get_claim_index(opts.spec_file)
    labels = claim_index.labels(include=opts.include_labels, exclude=opts.exclude_labels)
    for label in labels:
        print(f'Proving {label}')
        claim = claim_index[label]
        proof = APRProof.from_claim(kmir.definition, claim, {}, proof_dir=opts.proof_dir)
        with kmir.kcfg_explore(label) as kcfg_explore:
            prover = APRProver(kcfg_explore)
            prover.advance_proof(proof)
        summary = proof.summary
        print(f'{summary}')


def _kmir_prove_view(opts: ProveViewOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)

    claim_index = kmir.get_claim_index(opts.spec_file)
    labels = claim_index.labels(include=[opts.id])
    claim = claim_index[labels[0]]

    proof = APRProof.from_claim(kmir.definition, claim, {}, proof_dir=opts.proof_dir)

    node_printer = KMIRAPRNodePrinter(kmir, proof)

    viewer = APRProofViewer(proof, kmir, node_printer=node_printer)

    viewer.run()


def kmir(args: Sequence[str]) -> None:
    opts = _parse_args(args)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case GenSpecOpts():
            _kmir_gen_spec(opts)
        case ProveRunOpts():
            _kmir_prove_run(opts)
        case ProveViewOpts():
            _kmir_prove_view(opts)
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
    run_parser.add_argument('--haskell-backend', action='store_true', help='Run with the haskell backend')

    gen_spec_parser = command_parser.add_parser('gen-spec', help='Generate a k spec from a SMIR json')
    gen_spec_parser.add_argument('input_file', metavar='FILE', help='MIR program to generate a spec for')
    gen_spec_parser.add_argument('--output-file', metavar='FILE', help='Output file')
    gen_spec_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    prove_parser = command_parser.add_parser('prove', help='Utilities for working with proofs over SMIR')
    prove_command_parser = prove_parser.add_subparsers(dest='prove_command', required=True)

    prove_run_parser = prove_command_parser.add_parser('run', help='Run the prover on a spec')
    prove_run_parser.add_argument('input_file', metavar='FILE', help='K File with the spec module')
    prove_run_parser.add_argument('--proof-dir', metavar='DIR', help='Proof directory')
    prove_run_parser.add_argument(
        '--include-labels', metavar='LABELS', help='Comma separated list of claim labels to include'
    )
    prove_run_parser.add_argument(
        '--exclude-labels', metavar='LABELS', help='Comma separated list of claim labels to exclude'
    )
    prove_run_parser.add_argument('--bug-report', metavar='PATH', help='path to optional bug report')

    prove_view_parser = prove_command_parser.add_parser('view', help='View a saved proof')
    prove_view_parser.add_argument('input_file', metavar='SPEC_FILE', help='K File with the spec module')
    prove_view_parser.add_argument('id', metavar='PROOF_ID', help='The id of the proof to view')
    prove_view_parser.add_argument('--proof-dir', metavar='PROOF_DIR', help='Proofs folder that can contain the proof')

    return parser


def _parse_args(args: Sequence[str]) -> KMirOpts:
    ns = _arg_parser().parse_args(args)

    match ns.command:
        case 'run':
            return RunOpts(
                input_file=Path(ns.input_file).resolve(),
                depth=ns.depth,
                start_symbol=ns.start_symbol,
                haskell_backend=ns.haskell_backend,
            )
        case 'gen-spec':
            return GenSpecOpts(
                input_file=Path(ns.input_file).resolve(), output_file=ns.output_file, start_symbol=ns.start_symbol
            )
        case 'prove':
            match ns.prove_command:
                case 'run':
                    return ProveRunOpts(
                        spec_file=Path(ns.input_file).resolve(),
                        proof_dir=ns.proof_dir,
                        include_labels=ns.include_labels,
                        exclude_labels=ns.exclude_labels,
                        bug_report=ns.bug_report,
                    )
                case 'view':
                    proof_dir = Path(ns.proof_dir).resolve() if ns.proof_dir is not None else None
                    return ProveViewOpts(Path(ns.input_file).resolve(), proof_dir, ns.id)
                case _:
                    raise AssertionError()
        case _:
            raise AssertionError()


def main() -> None:
    kmir(sys.argv[1:])
