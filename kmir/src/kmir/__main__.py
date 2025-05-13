from __future__ import annotations

import logging
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.args import KCLIArgs
from pyk.kast.inner import KApply
from pyk.kast.outer import KFlatModule, KImport
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .build import HASKELL_DEF_DIR, LLVM_DEF_DIR, LLVM_LIB_DIR
from .cargo import CargoProject
from .kmir import KMIR, KMIRAPRNodePrinter
from .options import GenSpecOpts, ProveRawOpts, ProveRSOpts, PruneOpts, RunOpts, ShowOpts, ViewOpts
from .parse.parser import parse_json
from .smir import SMIRInfo

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Sequence
    from typing import Final

    from .options import KMirOpts

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def _kmir_run(opts: RunOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR) if opts.haskell_backend else KMIR(LLVM_DEF_DIR)

    smir_file: Path
    if opts.file:
        smir_file = Path(opts.file).resolve()
    else:
        cargo = CargoProject(Path.cwd())
        target = opts.bin if opts.bin else cargo.default_target
        smir_file = cargo.smir_for(target)

    parse_result = parse_json(kmir.definition, smir_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)
    kmir_kast, _ = parse_result

    if opts.haskell_backend:
        smir_json = SMIRInfo.from_file(smir_file)
        assert type(kmir_kast) is KApply

        result = kmir.run_call(kmir_kast, smir_json, opts.start_symbol, opts.depth)
    else:
        result = kmir.run_parsed(kmir_kast, opts.start_symbol, opts.depth)

    print(kmir.kore_to_pretty(result))


def _kmir_prove_rs(opts: ProveRSOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR, bug_report=opts.bug_report)
    proof = kmir.prove_rs(opts)
    print(str(proof.summary))
    if not proof.passed:
        sys.exit(1)


def _kmir_gen_spec(opts: GenSpecOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)

    parse_result = parse_json(kmir.definition, opts.input_file, 'Pgm')
    if parse_result is None:
        print('Parse error!', file=sys.stderr)
        sys.exit(1)

    kmir_kast, _ = parse_result
    apr_proof = kmir.apr_proof_from_kast(
        str(opts.input_file.stem.replace('_', '-')),
        kmir_kast,
        SMIRInfo.from_file(opts.input_file),
        start_symbol=opts.start_symbol,
        sort='KmirCell',
    )
    claim = apr_proof.as_claim()

    output_file = opts.output_file
    if output_file is None:
        suffixes = ''.join(opts.input_file.suffixes)
        base = opts.input_file.name.removesuffix(suffixes)
        output_file = Path(f'{base}-spec.k')

    module_name = output_file.stem.upper().replace('_', '-')
    spec_module = KFlatModule(module_name, (claim,), (KImport('KMIR'),))

    output_file.write_text(kmir.pretty_print(spec_module))


def _kmir_prove_raw(opts: ProveRawOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR, bug_report=opts.bug_report)
    claim_index = kmir.get_claim_index(opts.spec_file)
    labels = claim_index.labels(include=opts.include_labels, exclude=opts.exclude_labels)
    for label in labels:
        print(f'Proving {label}')
        claim = claim_index[label]
        if not opts.reload and opts.proof_dir is not None and APRProof.proof_data_exists(label, opts.proof_dir):
            _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
            proof = APRProof.read_proof_data(opts.proof_dir, label)
        else:
            _LOGGER.info(f'Constructing initial proof: {label}')
            proof = APRProof.from_claim(kmir.definition, claim, {}, proof_dir=opts.proof_dir)
        with kmir.kcfg_explore(label) as kcfg_explore:
            prover = APRProver(kcfg_explore, execute_depth=opts.max_depth)
            prover.advance_proof(proof, max_iterations=opts.max_iterations)
        summary = proof.summary
        print(f'{summary}')


def _kmir_view(opts: ViewOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)
    smir_info = None
    if opts.smir_info is not None:
        smir_info = SMIRInfo.from_file(opts.smir_info)
    node_printer = KMIRAPRNodePrinter(kmir, proof, smir_info=smir_info, full_printer=False)
    viewer = APRProofViewer(proof, kmir, node_printer=node_printer)
    viewer.run()


def _kmir_show(opts: ShowOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)
    smir_info = None
    if opts.smir_info is not None:
        smir_info = SMIRInfo.from_file(opts.smir_info)
    node_printer = KMIRAPRNodePrinter(kmir, proof, smir_info=smir_info, full_printer=opts.full_printer)
    shower = APRProofShow(kmir, node_printer=node_printer)
    lines = shower.show(proof)
    print('\n'.join(lines))


def _kmir_prune(opts: PruneOpts) -> None:
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)
    pruned_nodes = proof.prune(opts.node_id)
    print(f'Pruned nodes: {pruned_nodes}')
    proof.write_proof_data()


def kmir(args: Sequence[str]) -> None:
    ns = _arg_parser().parse_args(args)
    opts = _parse_args(ns)
    logging.basicConfig(level=_loglevel(ns), format=_LOG_FORMAT)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case GenSpecOpts():
            _kmir_gen_spec(opts)
        case ProveRawOpts():
            _kmir_prove_raw(opts)
        case ViewOpts():
            _kmir_view(opts)
        case ShowOpts():
            _kmir_show(opts)
        case PruneOpts():
            _kmir_prune(opts)
        case ProveRSOpts():
            _kmir_prove_rs(opts)
        case _:
            raise AssertionError()


def _arg_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir')

    command_parser = parser.add_subparsers(dest='command', required=True)
    kcli_args = KCLIArgs()

    run_parser = command_parser.add_parser('run', help='run stable MIR programs', parents=[kcli_args.logging_args])
    run_target_selection = run_parser.add_mutually_exclusive_group()
    run_target_selection.add_argument('--bin', metavar='TARGET', help='Target to run')
    run_target_selection.add_argument('--file', metavar='SMIR', help='SMIR json file to execute')
    run_parser.add_argument('--depth', type=int, metavar='DEPTH', help='Depth to execute')
    run_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )
    run_parser.add_argument('--haskell-backend', action='store_true', help='Run with the haskell backend')

    gen_spec_parser = command_parser.add_parser(
        'gen-spec', help='Generate a k spec from a SMIR json', parents=[kcli_args.logging_args]
    )
    gen_spec_parser.add_argument('input_file', metavar='FILE', help='MIR program to generate a spec for')
    gen_spec_parser.add_argument('--output-file', metavar='FILE', help='Output file')
    gen_spec_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    prove_args = ArgumentParser(add_help=False)
    prove_args.add_argument('--proof-dir', metavar='DIR', help='Proof directory')
    prove_args.add_argument('--bug-report', metavar='PATH', help='path to optional bug report')
    prove_args.add_argument('--max-depth', metavar='DEPTH', type=int, help='max steps to take between nodes in kcfg')
    prove_args.add_argument(
        '--max-iterations', metavar='ITERATIONS', type=int, help='max number of proof iterations to take'
    )
    prove_args.add_argument('--reload', action='store_true', help='Force restarting proof')

    proof_args = ArgumentParser(add_help=False)
    proof_args.add_argument('id', metavar='PROOF_ID', help='The id of the proof to view')
    proof_args.add_argument('--proof-dir', metavar='DIR', help='Proof directory')

    prove_raw_parser = command_parser.add_parser(
        'prove', help='Utilities for working with proofs over SMIR', parents=[kcli_args.logging_args, prove_args]
    )
    prove_raw_parser.add_argument('input_file', metavar='FILE', help='K File with the spec module')
    prove_raw_parser.add_argument(
        '--include-labels', metavar='LABELS', help='Comma separated list of claim labels to include'
    )
    prove_raw_parser.add_argument(
        '--exclude-labels', metavar='LABELS', help='Comma separated list of claim labels to exclude'
    )

    display_args = ArgumentParser(add_help=False)
    display_args.add_argument(
        '--no-full-printer',
        dest='full_printer',
        action='store_false',
        default=True,
        help='Do not display the full node in output.',
    )
    display_args.add_argument(
        '--smir-info',
        dest='smir_info',
        type=Path,
        default=None,
        help='Path to SMIR JSON file to improve debug messaging.',
    )

    command_parser.add_parser(
        'show', help='Show a saved proof', parents=[kcli_args.logging_args, proof_args, display_args]
    )

    command_parser.add_parser(
        'view', help='View a saved proof', parents=[kcli_args.logging_args, proof_args, display_args]
    )

    prune_parser = command_parser.add_parser(
        'prune', help='Prune a proof from a given node', parents=[kcli_args.logging_args, proof_args]
    )
    prune_parser.add_argument('node_id', metavar='NODE', type=int, help='The node to prune')

    prove_rs_parser = command_parser.add_parser(
        'prove-rs', help='Prove a rust program', parents=[kcli_args.logging_args, prove_args]
    )
    prove_rs_parser.add_argument(
        'rs_file', type=Path, metavar='FILE', help='Rust file with the spec function (e.g. main)'
    )
    prove_rs_parser.add_argument(
        '--save-smir', action='store_true', help='Do not delete the intermediate generated SMIR JSON file.'
    )
    prove_rs_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    return parser


def _parse_args(ns: Namespace) -> KMirOpts:
    match ns.command:
        case 'run':
            return RunOpts(
                bin=ns.bin,
                file=ns.file,
                depth=ns.depth,
                start_symbol=ns.start_symbol,
                haskell_backend=ns.haskell_backend,
            )
        case 'gen-spec':
            return GenSpecOpts(
                input_file=Path(ns.input_file).resolve(), output_file=ns.output_file, start_symbol=ns.start_symbol
            )
        case 'prove':
            proof_dir = Path(ns.proof_dir).resolve()
            return ProveRawOpts(
                spec_file=Path(ns.input_file).resolve(),
                proof_dir=ns.proof_dir,
                include_labels=ns.include_labels,
                exclude_labels=ns.exclude_labels,
                bug_report=ns.bug_report,
                max_depth=ns.max_depth,
                reload=ns.reload,
                max_iterations=ns.max_iterations,
            )
        case 'view':
            proof_dir = Path(ns.proof_dir).resolve()
            return ViewOpts(proof_dir, ns.id, full_printer=ns.full_printer, smir_info=ns.smir_info)
        case 'prune':
            proof_dir = Path(ns.proof_dir).resolve()
            return PruneOpts(proof_dir, ns.id, ns.node_id)
        case 'show':
            proof_dir = Path(ns.proof_dir).resolve()
            return ShowOpts(proof_dir, ns.id, full_printer=ns.full_printer, smir_info=ns.smir_info)
        case 'prove-rs':
            return ProveRSOpts(
                rs_file=Path(ns.rs_file).resolve(),
                proof_dir=ns.proof_dir,
                bug_report=ns.bug_report,
                max_depth=ns.max_depth,
                max_iterations=ns.max_iterations,
                reload=ns.reload,
                save_smir=ns.save_smir,
                start_symbol=ns.start_symbol,
            )
        case _:
            raise AssertionError()


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG
    if args.verbose:
        return logging.INFO
    return logging.WARNING


def main() -> None:
    sys.setrecursionlimit(10000000)
    kmir(sys.argv[1:])
