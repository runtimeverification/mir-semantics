from argparse import ArgumentParser
from subprocess import CalledProcessError
from typing import Any

from pyk.cli_utils import dir_path, file_path
from pyk.ktool.kprint import KAstInput, KAstOutput
from pyk.ktool.krun import KRunOutput

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
    **kwargs: Any,
) -> None:
    kast_input = KAstInput[input.upper()]
    kast_output = KAstOutput[output.upper()]

    kmir = KMIR(definition_dir, definition_dir)
    proc_res = kmir.parse_program_raw(input_file, input=kast_input, output=kast_output)

    if output != KAstOutput.NONE:
        print(proc_res.stdout)


def exec_run(
    input_file: str,
    definition_dir: str,
    output: str = 'none',
    ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    krun_output = KRunOutput[output.upper()]

    kmir = KMIR(definition_dir, definition_dir)

    try:
        proc_res = kmir.run_program(input_file, output=krun_output)
        if output != KAstOutput.NONE:
            print(proc_res.stdout)
    except RuntimeError as err:
        if ignore_return_code:
            msg, stdout, stderr = err.args
            print(stdout)
            print(stderr)
            print(msg)
        else:
            raise


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

    # Run
    run_subparser = command_parser.add_parser('run', help='Run a MIR program')
    run_subparser.add_argument(
        'input_file',
        type=file_path,
        help='Path to .mir file',
    )
    run_subparser.add_argument(
        '--definition-dir',
        dest='definition_dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    run_subparser.add_argument(
        '--output',
        dest='output',
        type=str,
        default='kast',
        help='Output mode',
        choices=['pretty', 'program', 'json', 'kore', 'kast', 'none'],
        required=False,
    )
    run_subparser.add_argument(
        '--ignore-return-code',
        action='store_true',
        default=False,
        help='Ignore return code of krun, alwasys return 0 (use for debugging only)',
    )

    return parser


if __name__ == '__main__':
    main()
