from argparse import ArgumentParser
from typing import Any

from pyk.cli.args import Options

from .utils import NodeIdLike, arg_pair_of, node_id_like


def create_argument_parser() -> ArgumentParser:
    logging_args = ArgumentParser(add_help=False)
    logging_args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
    logging_args.add_argument('--debug', default=False, action='store_true', help='Debug output.')

    parser = ArgumentParser(prog='kmir', description='KMIR command line tool')

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

    @staticmethod
    def update_args(parser: ArgumentParser) -> None:
        parser.add_argument(
            '--nodes',
            type=node_id_like,
            dest='nodes',
            action='append',
            help='List of nodes to display as well.',
        )
        parser.add_argument(
            '--node-deltas',
            type=arg_pair_of(node_id_like, node_id_like),
            dest='node_deltas',
            action='append',
            help='List of nodes to display delta for.',
        )
        parser.add_argument(
            '--failure-information',
            dest='failure_info',
            action='store_true',
            help='Falg to show failure summary for cfg, by default, false.',
        )
        parser.add_argument('--to-module', action='store_true', help='Output edges as a K module.')
        parser.add_argument('--pending', action='store_true', help='Also display pending nodes')
        parser.add_argument('--failing', action='store_true', help='Also display failing nodes')
        parser.add_argument(
            '--counterexample-information',
            dest='counterexample_info',
            action='store_true',
            help="Show models for failing nodes. Should be called with the '--failure-information' flag",
        )
