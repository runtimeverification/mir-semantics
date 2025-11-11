from __future__ import annotations

import logging
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.args import KCLIArgs
from pyk.cterm.show import CTermShow
from pyk.kast.pretty import PrettyPrinter
from pyk.proof.reachability import APRProof
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .build import HASKELL_DEF_DIR, LLVM_LIB_DIR
from .cargo import CargoProject
from .kmir import KMIR, KMIRAPRNodePrinter
from .linker import link
from .options import (
    InfoOpts,
    LinkOpts,
    ProveRSOpts,
    PruneOpts,
    RunOpts,
    SectionEdgeOpts,
    ShowOpts,
    ViewOpts,
)
from .smir import SMIRInfo, Ty
from .utils import render_leaf_k_cells, render_rules, render_statistics

if TYPE_CHECKING:
    from argparse import Namespace
    from collections.abc import Sequence
    from typing import Final

    from .options import KMirOpts

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def _kmir_run(opts: RunOpts) -> None:
    if opts.file:
        smir_info = SMIRInfo.from_file(Path(opts.file))
    else:
        cargo = CargoProject(Path.cwd())
        # multi-exec projects currently not supported
        if opts.bin:
            _LOGGER.warning(f'Requested to run {opts.bin} but multi-exec projects currently not supported')
        # target = opts.bin if opts.bin else cargo.default_target
        smir_info = cargo.smir_for_project(clean=False)

    def run(target_dir: Path):
        kmir = KMIR.from_kompiled_kore(smir_info, symbolic=opts.haskell_backend, target_dir=target_dir)
        result = kmir.run_smir(smir_info, start_symbol=opts.start_symbol, depth=opts.depth)
        print(kmir.kore_to_pretty(result))

    if opts.target_dir:
        run(target_dir=opts.target_dir)
    else:
        with tempfile.TemporaryDirectory() as target_dir:
            run(target_dir=Path(target_dir))


def _kmir_prove_rs(opts: ProveRSOpts) -> None:
    proof = KMIR.prove_rs(opts)
    print(str(proof.summary))
    if not proof.passed:
        sys.exit(1)


def _kmir_view(opts: ViewOpts) -> None:
    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)
    printer = PrettyPrinter(kmir.definition)
    omit_labels = ('<currentBody>',) if opts.omit_current_body else ()
    cterm_show = CTermShow(printer.print, omit_labels=omit_labels)
    opts.full_printer = False
    node_printer = KMIRAPRNodePrinter(cterm_show, proof, opts)
    viewer = APRProofViewer(proof, kmir, node_printer=node_printer, cterm_show=cterm_show)
    viewer.run()


def _kmir_show(opts: ShowOpts) -> None:
    from pyk.kast.pretty import PrettyPrinter

    from .kprint import KMIRPrettyPrinter

    kmir = KMIR(HASKELL_DEF_DIR, LLVM_LIB_DIR)
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)

    # Use custom KMIR printer by default, switch to standard printer if requested
    if opts.use_default_printer:
        printer = PrettyPrinter(kmir.definition)
        _LOGGER.info('Using standard PrettyPrinter')
    else:
        printer = KMIRPrettyPrinter(kmir.definition)
        _LOGGER.info('Using custom KMIRPrettyPrinter')

    all_omit_cells = list(opts.omit_cells or ())
    if opts.omit_current_body:
        all_omit_cells.append('<currentBody>')

    cterm_show = CTermShow(printer.print, omit_labels=tuple(all_omit_cells))
    node_printer = KMIRAPRNodePrinter(cterm_show, proof, opts)
    shower = APRProofShow(kmir.definition, node_printer=node_printer)
    shower.kcfg_show.pretty_printer = printer
    effective_node_deltas = tuple(sorted({*(opts.node_deltas or ()), *(opts.node_deltas_pro or ())}))
    effective_rule_edges = tuple(sorted({*(opts.rules or ()), *(opts.node_deltas_pro or ())}))

    _LOGGER.info(
        f'Showing {proof.id} with\n nodes: {opts.nodes},\n node_deltas: {effective_node_deltas},\n omit_cells: {tuple(all_omit_cells)}'
    )
    lines = shower.show(
        proof,
        nodes=opts.nodes or (),
        node_deltas=effective_node_deltas,
        omit_cells=tuple(all_omit_cells),
    )
    if opts.statistics:
        if lines and lines[-1] != '':
            lines.append('')
        lines.extend(render_statistics(proof))
    if effective_rule_edges:
        lines.append('# Rules: ')
        lines.extend(render_rules(proof, effective_rule_edges))
    if opts.leaves:
        if lines and lines[-1] != '':
            lines.append('')
        lines.extend(render_leaf_k_cells(proof, node_printer.cterm_show))

    print('\n'.join(lines))


def _kmir_prune(opts: PruneOpts) -> None:
    proof = APRProof.read_proof_data(opts.proof_dir, opts.id)
    pruned_nodes = proof.prune(opts.node_id)
    print(f'Pruned nodes: {pruned_nodes}')
    proof.write_proof_data()


def _kmir_section_edge(opts: SectionEdgeOpts) -> None:
    # Proof dir is checked to be some in arg parsing for instructive errors
    assert opts.proof_dir is not None

    if not APRProof.proof_data_exists(opts.id, opts.proof_dir):
        raise ValueError(f'Proof id {opts.id} not found in proof dir {opts.proof_dir}')

    target_path = opts.proof_dir / opts.id

    _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {opts.id}')
    apr_proof = APRProof.read_proof_data(opts.proof_dir, opts.id)

    smir_info = SMIRInfo.from_file(target_path / 'smir.json')

    kmir = KMIR.from_kompiled_kore(smir_info, symbolic=True, bug_report=opts.bug_report, target_dir=target_path)

    source_id, target_id = opts.edge
    _LOGGER.info(f'Attempting to add {opts.sections} sections from node {source_id} to node {target_id}')

    with kmir.kcfg_explore(apr_proof.id) as kcfg_explore:
        node_ids = kcfg_explore.section_edge(
            apr_proof.kcfg,
            source_id=int(source_id),
            target_id=int(target_id),
            logs=apr_proof.logs,
            sections=opts.sections,
        )
        _LOGGER.info(f'Added nodes on edge {(source_id, target_id)}: {node_ids}')

    apr_proof.write_proof_data()


def _kmir_info(opts: InfoOpts) -> None:
    smir_info = SMIRInfo.from_file(opts.smir_file)

    if opts.types:
        print(f'\nTypes requested: {opts.types}')
        chosen_types = [Ty(type_id) for type_id in opts.types]
        for type_id in chosen_types:
            print(f'Type {type_id}: {smir_info.unref_type(type_id)}')


def _kmir_link(opts: LinkOpts) -> None:
    result = link([SMIRInfo.from_file(f) for f in opts.smir_files])
    result.dump(opts.output_file)


def kmir(args: Sequence[str]) -> None:
    ns = _arg_parser().parse_args(args)
    opts = _parse_args(ns)
    logging.basicConfig(level=_loglevel(ns), format=_LOG_FORMAT)
    match opts:
        case RunOpts():
            _kmir_run(opts)
        case InfoOpts():
            _kmir_info(opts)
        case ViewOpts():
            _kmir_view(opts)
        case ShowOpts():
            _kmir_show(opts)
        case PruneOpts():
            _kmir_prune(opts)
        case SectionEdgeOpts():
            _kmir_section_edge(opts)
        case ProveRSOpts():
            _kmir_prove_rs(opts)
        case LinkOpts():
            _kmir_link(opts)
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
    run_parser.add_argument('--target-dir', type=Path, metavar='TARGET_DIR', help='SMIR kompilation target directory')
    run_parser.add_argument('--depth', type=int, metavar='DEPTH', help='Depth to execute')
    run_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )
    run_parser.add_argument('--haskell-backend', action='store_true', help='Run with the haskell backend')

    info_parser = command_parser.add_parser(
        'info', help='Show information about a SMIR JSON file', parents=[kcli_args.logging_args]
    )
    info_parser.add_argument('smir_file', metavar='FILE', help='SMIR JSON file to analyze')
    info_parser.add_argument('--types', metavar='TYPES', help='Comma separated list of type IDs to show details for')

    prove_args = ArgumentParser(add_help=False)
    prove_args.add_argument('--proof-dir', metavar='DIR', help='Proof directory')
    prove_args.add_argument('--bug-report', metavar='PATH', help='path to optional bug report')
    prove_args.add_argument('--max-depth', metavar='DEPTH', type=int, help='max steps to take between nodes in kcfg')
    prove_args.add_argument(
        '--max-iterations', metavar='ITERATIONS', type=int, help='max number of proof iterations to take'
    )
    prove_args.add_argument('--reload', action='store_true', help='Force restarting proof')
    prove_args.add_argument(
        '--break-on-calls', dest='break_on_calls', action='store_true', help='Break on all function and intrinsic calls'
    )
    prove_args.add_argument(
        '--break-on-function-calls',
        dest='break_on_function_calls',
        action='store_true',
        help='Break on function calls (not intrinsics)',
    )
    prove_args.add_argument(
        '--break-on-intrinsic-calls',
        dest='break_on_intrinsic_calls',
        action='store_true',
        help='Break on intrinsic calls (not other functions)',
    )
    prove_args.add_argument(
        '--break-on-thunk', dest='break_on_thunk', action='store_true', help='Break on thunk evaluation'
    )
    prove_args.add_argument(
        '--terminate-on-thunk',
        dest='terminate_on_thunk',
        action='store_true',
        help='Terminate proof when reaching a thunk',
    )
    prove_args.add_argument(
        '--break-every-statement',
        dest='break_every_statement',
        action='store_true',
        help='Break on every MIR Statement execution',
    )
    prove_args.add_argument(
        '--break-on-terminator-goto',
        dest='break_on_terminator_goto',
        action='store_true',
        help='Break on Goto terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-switch-int',
        dest='break_on_terminator_switch_int',
        action='store_true',
        help='Break on SwitchInt terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-return',
        dest='break_on_terminator_return',
        action='store_true',
        help='Break on Return terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-call',
        dest='break_on_terminator_call',
        action='store_true',
        help='Break on Call terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-assert',
        dest='break_on_terminator_assert',
        action='store_true',
        help='Break on Assert terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-drop',
        dest='break_on_terminator_drop',
        action='store_true',
        help='Break on Drop terminator',
    )
    prove_args.add_argument(
        '--break-on-terminator-unreachable',
        dest='break_on_terminator_unreachable',
        action='store_true',
        help='Break on Unreachable terminator',
    )
    prove_args.add_argument(
        '--break-every-terminator',
        dest='break_every_terminator',
        action='store_true',
        help='Break on every MIR terminator execution',
    )
    prove_args.add_argument(
        '--break-every-step',
        dest='break_every_step',
        action='store_true',
        help='Break on every MIR step (statements and terminators)',
    )

    proof_args = ArgumentParser(add_help=False)
    proof_args.add_argument('id', metavar='PROOF_ID', help='The id of the proof to view')
    proof_args.add_argument('--proof-dir', metavar='DIR', help='Proof directory')

    display_args = ArgumentParser(add_help=False)
    display_args.add_argument(
        '--full-printer',
        dest='full_printer',
        action='store_true',
        default=False,
        help='Display the full node in output.',
    )
    display_args.add_argument(
        '--smir-info',
        dest='smir_info',
        type=Path,
        default=None,
        help='Path to SMIR JSON file to improve debug messaging.',
    )
    display_args.add_argument(
        '--no-omit-current-body',
        dest='omit_current_body',
        default=True,
        action='store_false',
        help='Display the <currentBody> cell completely.',
    )

    show_parser = command_parser.add_parser(
        'show', help='Show proof information', parents=[kcli_args.logging_args, proof_args, display_args]
    )
    show_parser.add_argument('--nodes', metavar='NODES', help='Comma separated list of node IDs to show')
    show_parser.add_argument(
        '--node-deltas', metavar='DELTAS', help='Comma separated list of node deltas in format "source:target"'
    )
    show_parser.add_argument(
        '--node-deltas-pro', metavar='DELTAS', help='Extra node deltas (printed after main output)'
    )
    show_parser.add_argument(
        '--omit-cells', metavar='CELLS', help='Comma separated list of cell names to omit from output'
    )
    show_parser.add_argument(
        '--no-omit-static-info',
        dest='omit_static_info',
        action='store_false',
        default=True,
        help='Display static information cells (functions, start-symbol, types, adt-to-ty)',
    )
    show_parser.add_argument(
        '--use-default-printer',
        dest='use_default_printer',
        action='store_true',
        default=False,
        help='Use standard PrettyPrinter instead of custom KMIR printer',
    )
    show_parser.add_argument(
        '--statistics',
        action='store_true',
        help='Display aggregate statistics about the proof graph',
    )
    show_parser.add_argument(
        '--leaves',
        action='store_true',
        help='Print the <k> cell for each leaf node in the proof graph',
    )

    show_parser.add_argument('--rules', metavar='EDGES', help='Comma separated list of edges in format "source:target"')

    command_parser.add_parser(
        'view', help='View proof information', parents=[kcli_args.logging_args, proof_args, display_args]
    )

    prune_parser = command_parser.add_parser(
        'prune', help='Prune a proof from a given node', parents=[kcli_args.logging_args, proof_args]
    )
    prune_parser.add_argument('node_id', metavar='NODE', type=int, help='The node to prune')

    section_edge_parser = command_parser.add_parser(
        'section-edge', help='Break an edge into sections', parents=[kcli_args.logging_args, proof_args]
    )
    section_edge_parser.add_argument(
        'edge', type=lambda s: tuple(s.split(',')), help='Edge to section in CFG (format: `source,target`)'
    )
    section_edge_parser.add_argument(
        '--sections', type=int, default=2, help='Number of sections to make from edge (>= 2, default: 2)'
    )

    prove_rs_parser = command_parser.add_parser(
        'prove-rs', help='Prove a rust program', parents=[kcli_args.logging_args, prove_args]
    )
    prove_rs_parser.add_argument(
        'rs_file', type=Path, metavar='FILE', help='Rust file with the spec function (e.g. main)'
    )
    prove_rs_parser.add_argument(
        '--save-smir', action='store_true', help='Do not delete the intermediate generated SMIR JSON file.'
    )
    prove_rs_parser.add_argument('--smir', action='store_true', help='Treat the input file as a smir json.')
    prove_rs_parser.add_argument(
        '--start-symbol', type=str, metavar='SYMBOL', default='main', help='Symbol name to begin execution from'
    )

    link_parser = command_parser.add_parser(
        'link', help='Link together 2 or more SMIR JSON files', parents=[kcli_args.logging_args]
    )
    link_parser.add_argument('smir_files', nargs='+', metavar='SMIR_JSON', help='SMIR JSON files to link')
    link_parser.add_argument(
        '--output-file', '-o', metavar='FILE', help='Output file', default='linker_output.smir.json'
    )

    return parser


def _parse_args(ns: Namespace) -> KMirOpts:
    match ns.command:
        case 'run':
            return RunOpts(
                bin=ns.bin,
                file=ns.file,
                target_dir=ns.target_dir,
                depth=ns.depth,
                start_symbol=ns.start_symbol,
                haskell_backend=ns.haskell_backend,
            )
        case 'info':
            return InfoOpts(smir_file=Path(ns.smir_file), types=ns.types)
        case 'show':
            return ShowOpts(
                proof_dir=Path(ns.proof_dir),
                id=ns.id,
                full_printer=ns.full_printer,
                smir_info=Path(ns.smir_info) if ns.smir_info else None,
                omit_current_body=ns.omit_current_body,
                nodes=ns.nodes,
                node_deltas=ns.node_deltas,
                node_deltas_pro=ns.node_deltas_pro,
                rules=ns.rules,
                omit_cells=ns.omit_cells,
                omit_static_info=ns.omit_static_info,
                use_default_printer=ns.use_default_printer,
                statistics=ns.statistics,
                leaves=ns.leaves,
            )
        case 'view':
            proof_dir = Path(ns.proof_dir)
            return ViewOpts(
                proof_dir,
                ns.id,
                full_printer=ns.full_printer,
                smir_info=ns.smir_info,
                omit_current_body=ns.omit_current_body,
            )
        case 'prune':
            proof_dir = Path(ns.proof_dir)
            return PruneOpts(proof_dir, ns.id, ns.node_id)
        case 'section-edge':
            if ns.proof_dir is None:
                raise ValueError('Must pass --proof-dir to section-edge command')
            proof_dir = Path(ns.proof_dir)
            return SectionEdgeOpts(proof_dir, ns.id, ns.edge, ns.sections)
        case 'prove-rs':
            return ProveRSOpts(
                rs_file=Path(ns.rs_file),
                proof_dir=ns.proof_dir,
                bug_report=ns.bug_report,
                max_depth=ns.max_depth,
                max_iterations=ns.max_iterations,
                reload=ns.reload,
                save_smir=ns.save_smir,
                smir=ns.smir,
                start_symbol=ns.start_symbol,
                break_on_calls=ns.break_on_calls,
                break_on_function_calls=ns.break_on_function_calls,
                break_on_intrinsic_calls=ns.break_on_intrinsic_calls,
                break_on_thunk=ns.break_on_thunk,
                break_every_statement=ns.break_every_statement,
                break_on_terminator_goto=ns.break_on_terminator_goto,
                break_on_terminator_switch_int=ns.break_on_terminator_switch_int,
                break_on_terminator_return=ns.break_on_terminator_return,
                break_on_terminator_call=ns.break_on_terminator_call,
                break_on_terminator_assert=ns.break_on_terminator_assert,
                break_on_terminator_drop=ns.break_on_terminator_drop,
                break_on_terminator_unreachable=ns.break_on_terminator_unreachable,
                break_every_terminator=ns.break_every_terminator,
                break_every_step=ns.break_every_step,
                terminate_on_thunk=ns.terminate_on_thunk,
            )
        case 'link':
            return LinkOpts(
                smir_files=ns.smir_files,
                output_file=ns.output_file,
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
