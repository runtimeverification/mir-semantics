import logging
import sys
from argparse import Namespace
from pathlib import Path
from typing import Any, Final, Iterable, Optional

from pyk.proof import APRProof
from pyk.proof.reachability import APRFailureInfo
from pyk.utils import BugReport, check_dir_path, check_file_path

from . import VERSION
from .cli import create_argument_parser
from .kmir import KMIR
from .parse import parse
from .prove import get_claim_labels, prove, show_proof, view_proof
from .run import run
from .utils import NodeIdLike

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


def exec_version(**kwargs: Any) -> None:
    print(f'KMIR Version: {VERSION}')


def exec_parse(
    mir_file: Path,
    input: str,
    output: str,
    definition_dir: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    check_file_path(mir_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(definition_dir)

    kmir = KMIR(definition_dir)
    # _LOGGER.log( 'Call parser at {definition_dir}')
    parse(kmir, mir_file, output=output)
    # print(proc_res.stdout) if output != 'none' else None


def exec_run(
    mir_file: Path,
    output: str,
    definition_dir: Optional[Path] = None,
    depth: Optional[int] = None,
    bug_report: bool = False,
    # ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    # mir_file = Path(input_file)
    check_file_path(mir_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(definition_dir)

    if depth is not None:
        assert depth < 0, ValueError(f'Argument "depth" must be non-negative, got: {depth}')

    if bug_report:
        br = BugReport(mir_file.with_suffix('.bug_report.tar'))
        kmir = KMIR(definition_dir, bug_report=br)
    else:
        kmir = KMIR(definition_dir)

    run(kmir, mir_file, depth=depth, output=output)


def exec_prove(
    spec_file: Path,
    smt_timeout: int,
    smt_retry_limit: int,
    claim_list: bool = False,
    claim: Optional[str] = None,
    definition_dir: Optional[Path] = None,
    haskell_dir: Optional[Path] = None,
    use_booster: bool = True,
    bug_report: bool = False,
    save_directory: Optional[Path] = None,
    reinit: bool = False,
    depth: Optional[int] = None,
    trace_rewrites: bool = False,
    **kwargs: Any,
) -> None:
    # TODO: workers
    # TODO: md_selector doesn't work

    check_file_path(spec_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        # llvm_dir = Path(definition_dir)
        check_dir_path(definition_dir)

    if haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        # haskell_dir = Path(haskell_dir)
        check_dir_path(haskell_dir)

    # if the save_directory is not provided, the proofs are saved to the same directory of spec_file
    if save_directory is None:
        save_directory = spec_file.parent
    else:
        check_dir_path(save_directory)

    br = BugReport(spec_file.with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, haskell_dir=haskell_dir, use_booster=use_booster, bug_report=br)
    # We provide configuration of which backend to use in a KMIR object.
    # `use_booster` is by default True, where Booster Backend is always used unless turned off

    if claim_list:
        claim_labels = get_claim_labels(kmir, spec_file)
        print(*claim_labels, sep='\n')
        sys.exit(0)

    (passed, failed) = prove(
        kmir,
        spec_file,
        claim_label=claim,
        save_directory=save_directory,
        reinit=reinit,
        depth=depth,
        smt_timeout=smt_timeout,
        smt_retry_limit=smt_retry_limit,
        trace_rewrites=trace_rewrites,
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


def exec_show_proof(
    claim_label: str,
    proof_dir: Optional[Path] = None,
    definition_dir: Optional[Path] = None,
    haskell_dir: Optional[Path] = None,
    nodes: Iterable[NodeIdLike] = (),
    node_deltas: Iterable[tuple[NodeIdLike, NodeIdLike]] = (),
    failure_info: bool = False,
    to_module: bool = False,
    # minimize: bool = True,
    pending: bool = False,
    failing: bool = False,
    counterexample_info: bool = False,
    **kwargs: Any,
) -> None:
    if proof_dir is None:
        raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
    else:
        check_dir_path(proof_dir)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        check_dir_path(definition_dir)

    if haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        check_dir_path(haskell_dir)

    kmir = KMIR(definition_dir, haskell_dir=haskell_dir)

    show_output = show_proof(
        kmir,
        claim_label,
        proof_dir,
        nodes,
        node_deltas,
        to_module,
        failure_info,
        pending,
        failing,
        counterexample_info,
    )

    print(show_output)


def exec_view_proof(
    claim_label: str,
    proof_dir: Optional[Path] = None,
    definition_dir: Optional[Path] = None,
    haskell_dir: Optional[Path] = None,
    **kwargs: Any,
) -> None:
    # TODO: include dirs

    if proof_dir is None:
        raise RuntimeError('Proof directory is not specified, please provide the directory to all the proofs')
    else:
        check_dir_path(proof_dir)
    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        check_dir_path(definition_dir)
    if haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        check_dir_path(haskell_dir)

    kmir = KMIR(definition_dir, haskell_dir=haskell_dir)

    view_proof(
        kmir,
        claim_label,
        proof_dir,
    )


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


if __name__ == '__main__':
    main()
