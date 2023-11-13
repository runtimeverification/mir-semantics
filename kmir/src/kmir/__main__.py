import logging
import sys
from argparse import Namespace
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Final

from pyk.kast.outer import KApply, KClaim, KRewrite
from pyk.kcfg import KCFG
from pyk.ktool.kprint import KAstInput, KAstOutput
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRunOutput
from pyk.proof import APRProof
from pyk.proof.equality import EqualityProof
from pyk.proof.proof import Proof
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer
from pyk.utils import BugReport

from .cli import create_argument_parser
from .kmir import KMIR, KMIRSemantics
from .utils import (
    NodeIdLike,
    ensure_ksequence_on_k_cell,
    get_apr_proof_for_spec,
    kmir_prove,
    legacy_explore,
    print_failure_info,
)

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
    print(
        'WARN: "init" was seen in args, this calls an internal function. If a file is named "init", it must be renamed'
    )
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
    if spec_file is None:
        raise ValueError('A spec file must be provided')

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
            kcfg_semantics=KMIRSemantics,  # type: ignore
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


def exec_show_kcfg(
    definition_dir: str,
    haskell_dir: str,
    spec_file: Path,
    save_directory: Path | None = None,
    claim_labels: Iterable[str] | None = None,
    exclude_claim_labels: Iterable[str] = (),
    spec_module: str | None = None,
    md_selector: str | None = None,
    nodes: Iterable[NodeIdLike] = (),
    node_deltas: Iterable[tuple[NodeIdLike, NodeIdLike]] = (),
    to_module: bool = False,
    minimize: bool = True,
    failure_info: bool = False,
    sort_collections: bool = False,
    pending: bool = False,
    failing: bool = False,
    **kwargs: Any,
) -> None:
    # TODO: include dirs

    if spec_file is None:
        raise ValueError('A spec file must be provided')

    kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    kprove: KProve
    if kmir.kprove is None:
        raise ValueError('Cannot use KProve object when it is None')
    else:
        kprove = kmir.kprove

    proof = get_apr_proof_for_spec(
        kprove,
        spec_file,
        save_directory=save_directory,
        spec_module_name=spec_module,
        # include_dirs=include_dirs,
        md_selector=md_selector,
        claim_labels=claim_labels,
        exclude_claim_labels=exclude_claim_labels,
    )

    if pending:
        nodes = list(nodes) + [node.id for node in proof.pending]
    if failing:
        nodes = list(nodes) + [node.id for node in proof.failing]

    # TODO: Create NodePrinter ???
    proof_show = APRProofShow(kprove)

    res_lines = proof_show.show(
        proof,
        nodes=nodes,
        node_deltas=node_deltas,
        to_module=to_module,
        minimize=minimize,
        sort_collections=sort_collections,
    )

    if failure_info:
        with legacy_explore(kprove, id=proof.id) as kcfg_explore:
            res_lines += print_failure_info(proof, kcfg_explore)

    print('\n'.join(res_lines))


def exec_view_kcfg(
    definition_dir: str,
    haskell_dir: str,
    spec_file: Path,
    save_directory: Path | None = None,
    claim_labels: Iterable[str] | None = None,
    exclude_claim_labels: Iterable[str] = (),
    spec_module: str | None = None,
    md_selector: str | None = None,
    **kwargs: Any,
) -> None:
    # TODO: include dirs

    if spec_file is None:
        raise ValueError('A spec file must be provided')
    kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    kprove: KProve
    if kmir.kprove is None:
        raise ValueError('Cannot use KProve object when it is None')
    else:
        kprove = kmir.kprove

    proof = get_apr_proof_for_spec(
        kprove,
        spec_file,
        save_directory=save_directory,
        spec_module_name=spec_module,
        md_selector=md_selector,
        claim_labels=claim_labels,
        exclude_claim_labels=exclude_claim_labels,
    )

    # TODO: NodePrinter ???
    proof_view = APRProofViewer(proof, kprove)

    proof_view.run()


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == '__main__':
    main()
