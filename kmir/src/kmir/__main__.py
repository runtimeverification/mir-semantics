import logging
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, Final

from pyk.cli.utils import dir_path, file_path
from pyk.kast.outer import KApply, KClaim, KRewrite
from pyk.kcfg import KCFG
from pyk.ktool.kprint import KAstInput, KAstOutput
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRunOutput
from pyk.proof import APRProof
from pyk.proof.equality import EqualityProof
from pyk.proof.proof import Proof
from pyk.utils import BugReport

from .kmir import KMIR
from .utils import ensure_ksequence_on_k_cell, kmir_prove, legacy_explore, print_failure_info

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def main() -> None:
    parser = create_argument_parser()
    args = parser.parse_args()
    logging.basicConfig(level=_loglevel(args), format=_LOG_FORMAT)

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
    depth: int | None = None,
    bug_report: bool = False,
    ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    krun_output = KRunOutput[output.upper()]
    br = BugReport(Path(input_file).with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, None, bug_report=br)

    try:
        proc_res = kmir.run_program(input_file, output=krun_output, depth=depth)
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


def exec_prove(
    definition_dir: str,
    haskell_dir: str,
    spec_file: str,
    bug_report: bool = False,
    save_directory: Path | None = None,
    reinit: bool = False,
    depth: int | None = None,
    smt_timeout: int | None = None,
    smt_retry_limit: int | None = None,
    trace_rewrites: bool = False,
    **kwargs: Any,
) -> None:
    # TODO: workers
    # TODO: md_selector doesn't work
    spec_file_path = Path(spec_file)

    br = BugReport(spec_file_path.with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory, bug_report=br)

    kprove: KProve
    if kmir.kprove is None:
        raise ValueError('Cannot use KProve object when it is None')
    else:
        kprove = kmir.kprove

    _LOGGER.info('Extracting claims from file')
    claims = kprove.get_claims(Path(spec_file))
    if not claims:
        raise ValueError(f'No claims found in file {spec_file}')

    def is_functional(claim: KClaim) -> bool:
        claim_lhs = claim.body
        if type(claim_lhs) is KRewrite:
            claim_lhs = claim_lhs.lhs
        return not (type(claim_lhs) is KApply and claim_lhs.label.name == '<generatedTop>')

    def _init_and_run_proof(claim: KClaim) -> tuple[bool, list[str] | None]:
        with legacy_explore(
            kprove,
            id=claim.label,
            bug_report=br,
            smt_timeout=smt_timeout,
            smt_retry_limit=smt_retry_limit,
            trace_rewrites=trace_rewrites,
        ) as kcfg_explore:
            # TODO: simplfy_init
            proof_problem: Proof
            if is_functional(claim):
                if (
                    save_directory is not None
                    and not reinit
                    and EqualityProof.proof_exists(claim.label, save_directory)
                ):
                    proof_problem = EqualityProof.read_proof_data(save_directory, claim.label)
                else:
                    proof_problem = EqualityProof.from_claim(claim, kprove.definition, proof_dir=save_directory)
            else:
                if save_directory is not None and not reinit and APRProof.proof_exists(claim.label, save_directory):
                    proof_problem = APRProof.read_proof_data(save_directory, claim.label)

                else:
                    _LOGGER.info(f'Converting claim to KCFG: {claim.label}')
                    kcfg, init_node_id, target_node_id = KCFG.from_claim(kprove.definition, claim)

                    new_init = ensure_ksequence_on_k_cell(kcfg.node(init_node_id).cterm)
                    new_target = ensure_ksequence_on_k_cell(kcfg.node(target_node_id).cterm)

                    _LOGGER.info(f'Computing definedness constraint for initial node: {claim.label}')
                    new_init = kcfg_explore.cterm_assume_defined(new_init)

                    kcfg.replace_node(init_node_id, new_init)
                    kcfg.replace_node(target_node_id, new_target)

                    # Unsure if terminal should be empty
                    proof_problem = APRProof(
                        claim.label, kcfg, [], init_node_id, target_node_id, {}, proof_dir=save_directory
                    )

            passed = kmir_prove(
                kprove,
                proof_problem,
                kcfg_explore,
                max_depth=depth,
            )
            failure_log = None
            if not passed:
                failure_log = print_failure_info(proof_problem, kcfg_explore)

            return passed, failure_log

    results: list[tuple[bool, list[str] | None]] = []
    for claim in claims:
        results.append(_init_and_run_proof(claim))

    failed = 0
    for claim, r in zip(claims, results, strict=True):
        passed, failure_log = r
        if passed:
            print(f'PROOF PASSED: {claim.label}')
        else:
            failed += 1
            print(f'PROOF FAILED: {claim.label}')
            if failure_log is not None:
                for line in failure_log:
                    print(line)

    if failed:
        sys.exit(failed)


def create_argument_parser() -> ArgumentParser:
    logging_args = ArgumentParser(add_help=False)
    logging_args.add_argument('--verbose', '-v', default=False, action='store_true', help='Verbose output.')
    logging_args.add_argument('--debug', default=False, action='store_true', help='Debug output.')

    parser = ArgumentParser(prog='kmir', description='KMIR command line tool')

    command_parser = parser.add_subparsers(dest='command', required=True, help='Command to execute')

    # Init (See flake.nix)
    # This command is not needed unless it is for the flake, so we should hide it from users
    if 'init' in sys.argv:
        init_subparser = command_parser.add_parser('init', parents=[logging_args])
        init_subparser.add_argument(
            'llvm_dir',
            type=dir_path,
            help='Path to the llvm definition',
        )

    # Parse
    parse_subparser = command_parser.add_parser('parse', parents=[logging_args], help='Parse a MIR file')
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
    run_subparser = command_parser.add_parser('run', parents=[logging_args], help='Run a MIR program')
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
        '--definition-dir',
        dest='definition_dir',
        type=dir_path,
        help='Path to LLVM definition to use.',
    )
    prove_subparser.add_argument(
        '--haskell-dir',
        dest='haskell_dir',
        type=dir_path,
        help='Path to Haskell definition to use.',
    )
    prove_subparser.add_argument(
        '--spec-file',
        dest='spec_file',
        type=file_path,
        help='Path to specification file',
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
        dest='smt_timeout',
        type=int,
        default=125,
        help='Timeout in ms to use for SMT queries',
    )
    prove_subparser.add_argument(
        '--smt-retry-limit',
        dest='smt_retry_limit',
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
        dest='save_directory',
        type=dir_path,
        help='Path to KCFG proofs directory, directory must already exist.',
    )
    prove_subparser.add_argument(
        '--reinit',
        action='store_true',
        default=False,
        help='Reinit a proof.S',
    )

    return parser


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == '__main__':
    main()
