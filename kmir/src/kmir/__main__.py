import logging
import sys
from argparse import Namespace
from typing import Any, Final, Iterable

from pyk.cli.args import LoggingOptions
from pyk.proof import APRProof
from pyk.proof.reachability import APRFailureInfo
from pyk.utils import BugReport, check_dir_path, check_file_path

from . import VERSION
from .cli import create_argument_parser
from .kmir import KMIR
from .parse import ParseOptions, parse
from .prove import ProveOptions, ShowProofOptions, ViewProofOptions, get_claim_labels, prove, show_proof, view_proof
from .run import RunOptions, run

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()
    logging.basicConfig(level=_loglevel(args), format=_LOG_FORMAT)

    stripped_args = {
        key: val for (key, val) in vars(args).items() if val is not None and not (isinstance(val, Iterable) and not val)
    }
    options = generate_options(stripped_args)

    executor_name = 'exec_' + args.command.lower().replace('-', '_')
    if executor_name not in globals():
        raise AssertionError(f'Unimplemented command: {args.command}')

    execute = globals()[executor_name]
    execute(options)


def generate_options(args: dict[str, Any]) -> LoggingOptions:
    command = args['command']
    match command:
        case 'version':
            return VersionOptions(args)
        case 'parse':
            return ParseOptions(args)
        case 'run':
            return RunOptions(args)
        case 'prove':
            return ProveOptions(args)
        case 'show-proof':
            return ShowProofOptions(args)
        case 'view-proof':
            return ViewProofOptions(args)
        case _:
            raise ValueError(f'Unrecognized command: {command}')


class VersionOptions(LoggingOptions): ...


def exec_version(options: VersionOptions) -> None:
    print(f'KMIR Version: {VERSION}')


def exec_parse(options: ParseOptions) -> None:
    check_file_path(options.mir_file)

    if options.definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(options.definition_dir)

    kmir = KMIR(options.definition_dir)
    # _LOGGER.log( 'Call parser at {definition_dir}')
    parse(kmir, options)
    # print(proc_res.stdout) if output != 'none' else None


def exec_run(options: RunOptions) -> None:
    # mir_file = Path(input_file)
    check_file_path(options.mir_file)

    if options.definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(options.definition_dir)

    if options.depth is not None:
        assert options.depth < 0, ValueError(f'Argument "depth" must be non-negative, got: {options.depth}')

    if options.bug_report:
        br = BugReport(options.mir_file.with_suffix('.bug_report.tar'))
        kmir = KMIR(options.definition_dir, bug_report=br)
    else:
        kmir = KMIR(options.definition_dir)

    run(kmir, options)


def exec_prove(options: ProveOptions) -> None:
    # TODO: workers
    # TODO: md_selector doesn't work

    check_file_path(options.spec_file)

    if options.definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(options.definition_dir)

    if options.haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        # haskell_dir = Path(haskell_dir)
        check_dir_path(options.haskell_dir)

    # if the save_directory is not provided, the proofs are saved to the same directory of spec_file
    save_directory = options.save_directory
    if save_directory is None:
        save_directory = options.spec_file.parent
    else:
        check_dir_path(save_directory)

    br = BugReport(options.spec_file.with_suffix('.bug_report.tar')) if options.bug_report else None
    kmir = KMIR(options.definition_dir, haskell_dir=options.haskell_dir, use_booster=options.use_booster, bug_report=br)
    # We provide configuration of which backend to use in a KMIR object.
    # `use_booster` is by default True, where Booster Backend is always used unless turned off

    if options.claim_list:
        claim_labels = get_claim_labels(kmir, options.spec_file)
        print(*claim_labels, sep='\n')
        sys.exit(0)

    (passed, failed) = prove(
        kmir,
        options,
    )

    for proof in passed:
        print(f'PROOF PASSED: {proof.id}')

    for proof in failed:
        print(f'PROOF FAILED: {proof.id}')
        if isinstance(proof, APRProof) and isinstance(proof.failure_info, APRFailureInfo):
            failure_info = '\n'.join(proof.failure_info.print())
            print(f'{failure_info}')

    total_claims = len(passed) + len(failed)
    plural = '' if total_claims == 1 else 's'
    print(f'Prover run on {total_claims} claim{plural}: {len(passed)} passed, {len(failed)} failed')

    if len(failed) != 0:
        sys.exit(1)


def exec_show_proof(options: ShowProofOptions) -> None:
    if options.proof_dir is None:
        raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
    else:
        check_dir_path(options.proof_dir)

    if options.definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        check_dir_path(options.definition_dir)

    if options.haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        check_dir_path(options.haskell_dir)

    kmir = KMIR(options.definition_dir, haskell_dir=options.haskell_dir)

    show_output = show_proof(
        kmir,
        options,
    )

    print(show_output)


def exec_view_proof(options: ViewProofOptions) -> None:
    # TODO: include dirs

    if options.proof_dir is None:
        raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
    else:
        check_dir_path(options.proof_dir)
    if options.definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        check_dir_path(options.definition_dir)
    if options.haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        check_dir_path(options.haskell_dir)

    kmir = KMIR(options.definition_dir, haskell_dir=options.haskell_dir)

    view_proof(
        kmir,
        options,
    )


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == '__main__':
    main()
