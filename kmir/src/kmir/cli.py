import os
from argparse import ArgumentParser
from functools import cached_property

from pyk.cli.args import KCLIArgs
from pyk.cli.utils import dir_path, file_path

from .utils import arg_pair_of, node_id_like


def create_argument_parser() -> ArgumentParser:
    logging_args = ArgumentParser(add_help=False)
    logging_args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
    logging_args.add_argument('--debug', default=False, action='store_true', help='Debug output.')

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
        default=os.getenv('KMIR_LLVM_DIR'),
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    parse_subparser.add_argument(
        '--input',
        type=str,
        default='program',
        help='Input mode',
        choices=['program', 'binary', 'json', 'kast', 'kore'],
    )
    parse_subparser.add_argument(
        '--output',
        type=str,
        default='pretty',
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
        default=os.getenv('KMIR_LLVM_DIR'),
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    run_subparser.add_argument(
        '--output',
        type=str,
        default='pretty',
        help='Output mode',
        choices=['pretty', 'program', 'json', 'kore', 'latex', 'kast', 'binary', 'none'],
    )
    run_subparser.add_argument(
        '--bug-report',
        action='store_true',
        default=False,
        help='Generate a haskell-backend bug report for the execution',
    )
    run_subparser.add_argument(
        '--depth',
        default=None,
        type=int,
        help='Stop execution after `depth` rewrite steps',
    )

    # Prove
    prove_subparser = command_parser.add_parser(
        'prove', parents=[logging_args], help='Prove a MIR specification WARN: EXPERIMENTAL AND WORK IN PROGRESS'
    )
    prove_subparser.add_argument(
        'spec_file',
        type=file_path,
        help='Path to specification file',
    )
    prove_subparser.add_argument(
        '--definition-dir',
        default=os.getenv('KMIR_LLVM_DIR'),
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    prove_subparser.add_argument(
        '--haskell-dir',
        default=os.getenv('KMIR_HASKELL_DIR'),
        type=dir_path,
        help='Path to Haskell definition to use.',
    )
    prove_subparser.add_argument(
        '--bug-report',
        action='store_true',
        default=False,
        help='Generate a haskell-backend bug report for the execution',
    )
    prove_subparser.add_argument(
        '--depth',
        default=None,
        type=int,
        help='Stop execution after `depth` rewrite steps',
    )
    prove_subparser.add_argument(
        '--smt-timeout',
        type=int,
        default=200,
        help='Timeout in ms to use for SMT queries',
    )
    prove_subparser.add_argument(
        '--smt-retry-limit',
        type=int,
        default=4,
        help='Number of times to retry SMT queries with scaling timeouts.',
    )
    prove_subparser.add_argument(
        '--trace-rewrites',
        default=False,
        action='store_true',
        help='Log traces of all simplification and rewrite rule applications.',
    )
    prove_subparser.add_argument(
        '--save-directory',
        type=dir_path,
        default=None,
        help='Path to KCFG proofs directory, directory must already exist.',
    )
    prove_subparser.add_argument(
        '--reinit',
        action='store_true',
        default=False,
        help='Reinitialise a proof.',
    )
    prove_subparser.add_argument(
        '--use-booster',
        action='store_true',
        default=False,  # TODO: debug the booster backend, when it is as fast as legacy, change this to be True
        help='Use the booster backend instead of the haskell backend',
    )

    kmir_cli_args = KMIRCLIArgs()

    # KCFG show
    show_subparser = command_parser.add_parser(
        'show-kcfg',
        help='Display tree show of CFG',
        parents=[
            logging_args,
            kmir_cli_args.kcfg_show_args,
        ],
    )
    show_subparser.add_argument(
        'spec-file',
        type=file_path,
        help='Path to specification file',
    )
    show_subparser.add_argument(
        '--definition-dir',
        default=os.getenv('KMIR_LLVM_DIR'),
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    show_subparser.add_argument(
        '--haskell-dir',
        default=os.getenv('KMIR_HASKELL_DIR'),
        type=dir_path,
        help='Path to Haskell definition to use.',
    )
    show_subparser.add_argument(
        '--save-directory',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )

    # KCFG view
    view_subparser = command_parser.add_parser(
        'view-kcfg',
        help='Display tree view of CFG',
        parents=[logging_args],
    )
    view_subparser.add_argument(
        'spec-file',
        type=file_path,
        help='Path to specification file',
    )
    view_subparser.add_argument(
        '--definition-dir',
        default=os.getenv('KMIR_LLVM_DIR'),
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    view_subparser.add_argument(
        '--haskell-dir',
        default=os.getenv('KMIR_HASKELL_DIR'),
        type=dir_path,
        help='Path to Haskell definition to use.',
    )
    view_subparser.add_argument(
        '--save-directory',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )

    return parser


class KMIRCLIArgs(KCLIArgs):
    @cached_property
    def kcfg_show_args(self) -> ArgumentParser:
        args = ArgumentParser(add_help=False)
        args.add_argument(
            '--node',
            type=node_id_like,
            dest='nodes',
            default=[],
            action='append',
            help='List of nodes to display as well.',
        )
        args.add_argument(
            '--node-delta',
            type=arg_pair_of(node_id_like, node_id_like),
            dest='node_deltas',
            default=[],
            action='append',
            help='List of nodes to display delta for.',
        )
        args.add_argument(
            '--failure-information',
            dest='failure_info',
            default=False,
            action='store_true',
            help='Show failure summary for cfg',
        )
        args.add_argument(
            '--no-failure-information',
            dest='failure_info',
            action='store_false',
            help='Do not show failure summary for cfg',
        )
        args.add_argument('--to-module', default=False, action='store_true', help='Output edges as a K module.')
        args.add_argument('--pending', default=False, action='store_true', help='Also display pending nodes')
        args.add_argument('--failing', default=False, action='store_true', help='Also display failing nodes')
        args.add_argument(
            '--counterexample-information',
            dest='counterexample_info',
            default=False,
            action='store_true',
            help="Show models for failing nodes. Should be called with the '--failure-information' flag",
        )
        return args
