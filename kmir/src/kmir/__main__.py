from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional

from pyk.cli_utils import dir_path, file_path
from pyk.ktool.kprint import KAstInput, KAstOutput

from .kmir import KMIR


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(**vars(args))


def exec_parse(
    input_file: str,
    definition_dir: str,
    input: str = 'program',
    output: str = 'kast',
    mir_parser: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    kast_input = KAstInput[input.upper()]
    kast_output = KAstOutput[output.upper()]

    if not mir_parser:
        mir_parser = Path(definition_dir) / 'parser_Mir_MIR-SYNTAX'

    kmir = KMIR(definition_dir, definition_dir, mir_parser)
    proc_res = kmir.parse_program_raw(input_file, input=kast_input, output=kast_output)

    if output != KAstOutput.NONE:
        print(proc_res.stdout)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir', description='KMIR command line tool')
    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # Parse
    parse_subparser = command_parser.add_parser('parse', help='Parse a MIR file')
    parse_subparser.add_argument(
        'input_file',
        type=file_path,
        help='Path to .mir file',
    )
    parse_subparser.add_argument(
        '--definition-dir',
        dest='definition_dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    parse_subparser.add_argument(
        '--input',
        dest='input',
        type=str,
        default='program',
        help='Input mode',
        choices=['program', 'binary', 'json', 'kast', 'kore'],
        required=False,
    )
    parse_subparser.add_argument(
        '--output',
        dest='output',
        type=str,
        default='kast',
        help='Output mode',
        choices=['pretty', 'program', 'json', 'kore', 'kast', 'none'],
        required=False,
    )

    return parser


if __name__ == '__main__':
    main()
