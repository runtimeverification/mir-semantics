import logging
from argparse import Namespace
from pathlib import Path
from typing import Any, Final, Optional

from pyk.utils import BugReport, check_dir_path, check_file_path

from . import VERSION
from .cli import create_argument_parser
from .kmir import KMIR
from .parse import parse
from .prove import prove
from .run import run

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
    input_file: str,
    input: str,
    output: str,
    definition_dir: Optional[str] = None,
    **kwargs: Any,
) -> None:
    mir_file = Path(input_file)
    check_file_path(mir_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        llvm_dir = Path(definition_dir)
        check_dir_path(llvm_dir)

    kmir = KMIR(llvm_dir)
    # _LOGGER.log( 'Call parser at {llvm_dir}')
    parse(kmir, mir_file, output=output)
    # print(proc_res.stdout) if output != 'none' else None


def exec_run(
    input_file: str,
    output: str,
    definition_dir: Optional[str] = None,
    depth: Optional[int] = None,
    bug_report: bool = False,
    # ignore_return_code: bool = False,
    **kwargs: Any,
) -> None:
    mir_file = Path(input_file)
    check_file_path(mir_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        llvm_dir = Path(definition_dir)
        check_dir_path(llvm_dir)

    if depth is not None:
        assert depth < 0, ValueError(f'Argument "depth" must be non-negative, got: {depth}')

    if bug_report:
        # br = BugReport(mir_file.with_suffix('.bug_report.tar'))
        kmir = KMIR(llvm_dir)
    else:
        kmir = KMIR(llvm_dir)

    run(kmir, mir_file, depth=depth, output=output)


def exec_prove(
    spec_file: str,
    *,
    smt_timeout: int,
    smt_retry_limit: int,
    definition_dir: Optional[str] = None,
    haskell_dir: Optional[str] = None,
    use_booster: bool = True,
    bug_report: bool = False,
    save_directory: Optional[str] = None,
    reinit: bool = False,
    depth: Optional[int] = None,
    trace_rewrites: bool = False,
    **kwargs: Any,
) -> None:
    # TODO: workers
    # TODO: md_selector doesn't work
    if spec_file is None:
        raise RuntimeError("A specification file must be provided")
    else: 
        spec_file = Path(spec_file)
        check_file_path(spec_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        llvm_dir = Path(definition_dir)
        check_dir_path(llvm_dir)

    if haskell_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        haskell_dir = Path(haskell_dir)
        check_dir_path(haskell_dir)

    if save_directory is None:
        raise RuntimeError('Cannot find the save directory, please specify a valid directory')
    else:
        use_directory = Path(save_directory)
        check_dir_path(use_directory)

    br = BugReport(spec_file.with_suffix('.bug_report.tar')) if bug_report else None
    kmir = KMIR(definition_dir, haskell_dir=haskell_dir, use_booster=use_booster, bug_report=br)
    # We provide configuration of which backend to use in a KMIR object.
    # `use_booster` is by default True, where Booster Backend is always used unless turned off

    prove(
        kmir,
        spec_file,
        save_directory=use_directory,
        reinit=reinit,
        depth=depth,
        smt_timeout=smt_timeout,
        smt_retry_limit=smt_retry_limit,
        trace_rewrites=trace_rewrites,
        # kore_rpc_command=kore_rpc_command,
    )


"""
def exec_show_kcfg(
    definition_dir: str,
    symbolic_dir: str,
    input_file: Path,
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

    spec_file = Path(input_file)
    check_file_path(spec_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        llvm_dir = Path(definition_dir)
        check_dir_path(llvm_dir)

    if symbolic_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        haskell_dir = Path(symbolic_dir)
        check_dir_path(haskell_dir)

    if save_directory is None:
        raise RuntimeError('Cannot find the save directory, please specify a valid directory')
    else:
        use_directory = Path(save_directory)
        check_dir_path(use_directory)

    # kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    show_kcfg(
        llvm_dir,
        haskell_dir,
        spec_file,
        use_directory,
        claim_labels,
        exclude_claim_labels,
        spec_module,
        md_selector,
        nodes,
        node_deltas,
        to_module,
        minimize,
        failure_info,
        sort_collections,
        pending,
        failing,
    )


def exec_view_kcfg(
    definition_dir: str,
    symbolic_dir: str,
    input_file: Path,
    save_directory: Path | None = None,
    claim_labels: Iterable[str] | None = None,
    exclude_claim_labels: Iterable[str] = (),
    spec_module: str | None = None,
    md_selector: str | None = None,
    **kwargs: Any,
) -> None:
    # TODO: include dirs

    spec_file = Path(input_file)
    check_file_path(spec_file)

    if definition_dir is None:
        raise RuntimeError('Cannot find KMIR LLVM definition, please specify --definition-dir, or KMIR_LLVM_DIR')
    else:
        llvm_dir = Path(definition_dir)
        check_dir_path(llvm_dir)

    if symbolic_dir is None:
        raise RuntimeError('Cannot find KMIR Haskell definition, please specify --haskell-dir, or KMIR_HASKELL_DIR')
    else:
        haskell_dir = Path(symbolic_dir)
        check_dir_path(haskell_dir)

    if save_directory is None:
        raise RuntimeError('Cannot find the save directory, please specify a valid directory')
    else:
        use_directory = Path(save_directory)
        check_dir_path(use_directory)
    # kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    view_kcfg(
        llvm_dir,
        haskell_dir,
        spec_file,
        use_directory,
        claim_labels,
        exclude_claim_labels,
        spec_module,
        md_selector,
    )
"""


def _loglevel(args: Namespace) -> int:
    if args.debug:
        return logging.DEBUG

    if args.verbose:
        return logging.INFO

    return logging.WARNING


"""
if __name__ == '__main__':
    main()
 """
