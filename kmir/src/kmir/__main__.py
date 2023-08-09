import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from pyk.cli.utils import dir_path, file_path
from pyk.kast.outer import KApply, KClaim, KRewrite
from pyk.kcfg import KCFG
from pyk.ktool.kprint import KAstInput, KAstOutput
from pyk.ktool.kprove import KProve, KProveOutput
from pyk.ktool.krun import KRunOutput
from pyk.proof import APRProof
from pyk.proof.equality import EqualityProof
from pyk.proof.proof import Proof
from pyk.utils import BugReport

from .kmir import KMIR
from .utils import ensure_ksequence_on_k_cell, kmir_prove, legacy_explore, print_failure_info


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
    output: str = 'kore',
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
    depth: int | None = None,
    bug_report: bool = False,
    ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    krun_output = KRunOutput[output.upper()]
    br = BugReport(Path(input_file).with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, definition_dir, bug_report=br)

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
    output: str = 'none',
    bug_report: bool = False,
    use_kprove_object: bool = False,
    depth: int | None = None,
    smt_timeout: int | None = None,
    smt_retry_limit: int | None = None,
    trace_rewrites: bool = False,
    **kwargs: Any,
) -> None:
    # TODO: workers
    kprove_output = KProveOutput[output.upper()]
    spec_file_path = Path(spec_file)
    br = BugReport(spec_file_path.with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, haskell_dir, bug_report=br)

    if use_kprove_object:
        kprove: KProve
        if kmir.kprove is None:
            raise ValueError('Cannot use KProve object when it is None')
        else:
            kprove = kmir.kprove

        print('Extracting claims from file', flush=True)
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
                # TODO: save directory
                # TODO: LOGGER
                # TODO: simplfy_init
                proof_problem: Proof
                if is_functional(claim):
                    proof_problem = EqualityProof.from_claim(claim, kprove.definition)
                else:
                    print(f'Converting claim to KCFG: {claim.label}', flush=True)
                    kcfg, init_node_id, target_node_id = KCFG.from_claim(kprove.definition, claim)

                    new_init = ensure_ksequence_on_k_cell(kcfg.node(init_node_id).cterm)
                    new_target = ensure_ksequence_on_k_cell(kcfg.node(target_node_id).cterm)

                    print(f'Computing definedness constraint for initial node: {claim.label}', flush=True)
                    new_init = kcfg_explore.cterm_assume_defined(new_init)  # Fails

                    kcfg.replace_node(init_node_id, new_init)
                    kcfg.replace_node(target_node_id, new_target)

                    proof_problem = APRProof(claim.label, kcfg, init_node_id, target_node_id, {})  # Fails

                passed = kmir_prove(
                    kprove,
                    proof_problem,
                    kcfg_explore,
                    max_depth=depth,
                )
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

    else:
        print('Proving program with _kprove', flush=True)
        proc_res = kmir.prove_program(spec_file_path, kompiled_dir=Path(haskell_dir), output=kprove_output, depth=depth)
        print('Completed proving', flush=True)
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
    prove_subparser = command_parser.add_parser('prove', help='Prove a MIR specification')
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
        '--output',
        dest='output',
        type=str,
        default='kast',
        help='Output mode',
        choices=['pretty', 'program', 'KAST', 'binary', 'json', 'latex', 'kore', 'none'],
        required=False,
    )
    prove_subparser.add_argument(
        '--use-kprove-object',
        action='store_true',
        default=False,
        help='FOR DEVELOPMENT ONLY. To use _kprove directly or use KProve object',
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

    return parser


if __name__ == '__main__':
    main()
