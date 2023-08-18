from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from pyk.cli.utils import dir_path, file_path
from pyk.ktool.kprint import KAstInput, KAstOutput
from pyk.ktool.krun import KRunOutput
from pyk.utils import BugReport

from .kmir import KMIR


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(**vars(args))


def exec_init(llvm_dir: str, **kwargs: Any) -> KMIR:
    return KMIR(llvm_dir, llvm_dir)


def exec_parse(
    input_file: str,
    definition_dir: str | None = None,
    input: str = 'program',
    output: str = 'kore',
    **kwargs: Any,
) -> None:
    kast_input = KAstInput[input.upper()]
    kast_output = KAstOutput[output.upper()]

    kmir = KMIR(definition_dir, None)
    proc_res = kmir.parse_program_raw(input_file, input=kast_input, output=kast_output)

    if output != KAstOutput.NONE:
        print(proc_res.stdout)


def exec_run(
    input_file: str,
    definition_dir: str | None = None,
    output: str = 'none',
    max_depth: int | None = None,
    bug_report: bool = False,
    ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    krun_output = KRunOutput[output.upper()]
    br = BugReport(Path(input_file).with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, None, bug_report=br)

    try:
        proc_res = kmir.run_program(input_file, output=krun_output, depth=max_depth)
        if output != KAstOutput.NONE:
            print(proc_res.stdout)
    except RuntimeError as err:
        if ignore_return_code:
            msg, stdout, stderr = err.args
            print(stdout)
            print(stderr)
            print(msg)
        else:
            msg, stdout, stderr = err.args
            print(stdout)
            print(stderr)
            print(msg)
            exit(1)


def create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(prog='kmir', description='KMIR command line tool')
    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # Init
    init_subparser = command_parser.add_parser('init', help='Initialises a KMIR object')
    init_subparser.add_argument(
        'llvm_dir',
        type=dir_path,
        help='Path to the llvm definition',
    )

    # Parse
    parse_subparser = command_parser.add_parser('parse', help='Parse a MIR file')
    parse_subparser.add_argument(
        'input_file',
        type=file_path,
        help='Path to .mir file',
    )
    parse_subparser.add_argument(
        '--definition-dir',
        default=None,
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
        default='kore',
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
        default=None,
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
    run_subparser.add_argument(
        '--bug-report',
        action='store_true',
        default=False,
        help='Generate a haskell-backend bug report for the execution',
    )
    run_subparser.add_argument(
        '--max-depth',
        default=None,
        type=int,
        help='Stop execution after `max-depth` rewrite steps',
    )

    return parser


if __name__ == '__main__':
    main()
