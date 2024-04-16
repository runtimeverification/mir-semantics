from argparse import ArgumentParser
from functools import cached_property
from typing import Any

from pyk.cli.args import KCLIArgs, Options
from pyk.cli.utils import dir_path, file_path

from .utils import NodeIdLike, arg_pair_of, node_id_like


def create_argument_parser() -> ArgumentParser:
    logging_args = ArgumentParser(add_help=False)
    logging_args.add_argument('--verbose', '-v', default=None, action='store_true', help='Verbose output.')
    logging_args.add_argument('--debug', default=None, action='store_true', help='Debug output.')

    parser = ArgumentParser(prog='kmir', description='KMIR command line tool')

    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # Version
    command_parser.add_parser('version', parents=[logging_args], help='Display KMIR version')

    # Parse
    parse_subparser = command_parser.add_parser('parse', parents=[logging_args], help='Parse a MIR file')
    parse_subparser.add_argument(
        'mir_file',
        type=file_path,
        help='Path to .mir file',
    )
    parse_subparser.add_argument(
        '--definition-dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    parse_subparser.add_argument(
        '--input',
        type=str,
        help='Input mode',
        choices=['program', 'binary', 'json', 'kast', 'kore'],
    )
    parse_subparser.add_argument(
        '--output',
        type=str,
        help='Output mode',
        choices=['pretty', 'program', 'json', 'kore', 'kast', 'binary', 'latex', 'none'],
    )

    # Run
    run_subparser = command_parser.add_parser('run', parents=[logging_args], help='Run a MIR program')
    run_subparser.add_argument(
        'mir_file',
        type=file_path,
        help='Path to .mir file',
    )
    run_subparser.add_argument(
        '--definition-dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    run_subparser.add_argument(
        '--output',
        type=str,
        help='Output mode',
        choices=['pretty', 'program', 'json', 'kore', 'latex', 'kast', 'binary', 'none'],
    )
    run_subparser.add_argument(
        '--bug-report',
        action='store_true',
        default=None,
        help='Generate a haskell-backend bug report for the execution',
    )
    run_subparser.add_argument(
        '--depth',
        type=int,
        help='Stop execution after `depth` rewrite steps',
    )

    # Prove
    prove_subparser = command_parser.add_parser(
        'prove',
        parents=[logging_args],
        help='Prove a MIR specification, by default, it proves all the claims. Use `--claim` option to prove a selected claim.',
    )
    prove_subparser.add_argument(
        'spec_file',
        type=file_path,
        help='Path to specification file',
    )
    prove_subparser.add_argument(
        '--definition-dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    prove_subparser.add_argument(
        '--haskell-dir',
        type=dir_path,
        help='Path to Haskell definition to use.',
    )
    prove_subparser.add_argument(
        '--claim-list',
        default=None,
        action='store_true',
        help='Print a list of claims in the specificatoin file',
    )
    prove_subparser.add_argument(
        '--claim',
        type=str,
        help='Provide the claim label for proving a single claim',
    )
    prove_subparser.add_argument(
        '--bug-report',
        action='store_true',
        default=None,
        help='Generate a haskell-backend bug report for the execution',
    )
    prove_subparser.add_argument(
        '--depth',
        type=int,
        help='Stop execution after `depth` rewrite steps',
    )
    prove_subparser.add_argument(
        '--smt-timeout',
        type=int,
        help='Timeout in ms to use for SMT queries',
    )
    prove_subparser.add_argument(
        '--smt-retry-limit',
        type=int,
        help='Number of times to retry SMT queries with scaling timeouts.',
    )
    prove_subparser.add_argument(
        '--trace-rewrites',
        default=None,
        action='store_true',
        help='Log traces of all simplification and rewrite rule applications.',
    )
    prove_subparser.add_argument(
        '--save-directory',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )
    prove_subparser.add_argument(
        '--reinit',
        action='store_true',
        default=None,
        help='Reinitialise a proof.',
    )
    prove_subparser.add_argument(
        '--use-booster',
        action='store_true',
        default=None,
        help='Use the booster backend instead of the haskell backend',
    )

    kmir_cli_args = KMIRCLIArgs()

    # Proof show
    show_subparser = command_parser.add_parser(
        'show-proof',
        help='Display tree view of a proof in KCFG',
        parents=[
            logging_args,
            kmir_cli_args.kcfg_show_proof,
        ],
    )
    show_subparser.add_argument('claim_label', type=str, help='Provide the claim label for showing the proof')
    show_subparser.add_argument(
        '--proof-dir',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )
    show_subparser.add_argument(
        '--definition-dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    show_subparser.add_argument(
        '--haskell-dir',
        type=dir_path,
        help='Path to Haskell definition to use.',
    )

    # KCFG view
    view_subparser = command_parser.add_parser(
        'view-proof',
        help='Display the interative proof tree',
        parents=[logging_args],
    )
    view_subparser.add_argument('claim_label', type=str, help='Provide the claim label for showing the proof')
    view_subparser.add_argument(
        '--proof-dir',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )
    view_subparser.add_argument(
        '--definition-dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    view_subparser.add_argument(
        '--haskell-dir',
        type=dir_path,
        help='Path to Haskell definition to use.',
    )

    return parser


class KCFGShowProofOptions(Options):
    nodes: list[NodeIdLike]
    node_deltas: list[tuple[NodeIdLike, NodeIdLike]]
    failure_info: bool
    to_module: bool
    pending: bool
    failing: bool
    counterexample_info: bool

    @staticmethod
    def default() -> dict[str, Any]:
        return {
            'nodes': [],
            'node_deltas': [],
            'failure_info': False,
            'to_module': False,
            'pending': False,
            'failing': False,
            'counterexample_info': False,
        }


class KMIRCLIArgs(KCLIArgs):
    @cached_property
    def kcfg_show_proof(self) -> ArgumentParser:
        args = ArgumentParser(add_help=False)
        args.add_argument(
            '--nodes',
            type=node_id_like,
            dest='nodes',
            default=[],
            action='append',
            help='List of nodes to display as well.',
        )
        args.add_argument(
            '--node-deltas',
            type=arg_pair_of(node_id_like, node_id_like),
            dest='node_deltas',
            default=[],
            action='append',
            help='List of nodes to display delta for.',
        )
        args.add_argument(
            '--failure-information',
            dest='failure_info',
            default=None,
            action='store_true',
            help='Falg to show failure summary for cfg, by default, false.',
        )
        args.add_argument('--to-module', default=None, action='store_true', help='Output edges as a K module.')
        args.add_argument('--pending', default=None, action='store_true', help='Also display pending nodes')
        args.add_argument('--failing', default=None, action='store_true', help='Also display failing nodes')
        args.add_argument(
            '--counterexample-information',
            dest='counterexample_info',
            default=None,
            action='store_true',
            help="Show models for failing nodes. Should be called with the '--failure-information' flag",
        )
        return args
