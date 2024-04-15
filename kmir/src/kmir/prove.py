import logging
import os
from pathlib import Path
from typing import Any, Final

from pyk.cli.args import LoggingOptions
from pyk.proof import APRProof
from pyk.proof.proof import Proof
from pyk.proof.reachability import APRFailureInfo
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .cli import KCFGShowProofOptions
from .kmir import KMIR

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


def get_claim_labels(kmir: KMIR, spec_file: Path) -> list[str]:
    _LOGGER.info(f'Extracting claim labels from spec file {spec_file}')

    if kmir.prover:
        kmir_prover = kmir.prover
    else:
        raise ValueError('The prover object in kmir is not initialised.')

    flat_module_list = kmir_prover.mir_prove.get_claim_modules(spec_file=spec_file)

    all_claims = {c.label: c for m in flat_module_list.modules for c in m.claims}

    return list(all_claims.keys())


class ProveOptions(LoggingOptions):
    spec_file: Path
    definition_dir: Path | None
    haskell_dir: Path | None
    claim_list: bool
    claim: str | None
    bug_report: bool
    depth: int | None
    smt_timeout: int
    smt_retry_limit: int
    trace_rewrites: bool
    save_directory: Path | None
    reinit: bool
    use_booster: bool

    @staticmethod
    def default() -> dict[str, Any]:
        llvm_dir_str = os.getenv('KMIR_LLVM_DIR')
        llvm_dir = Path(llvm_dir_str) if llvm_dir_str is not None else None
        haskell_dir_str = os.getenv('KMIR_HASKELL_DIR')
        haskell_dir = Path(haskell_dir_str) if haskell_dir_str is not None else None

        return {
            'definition_dir': llvm_dir,
            'haskell_dir': haskell_dir,
            'claim_list': False,
            'claim': None,
            'bug_report': False,
            'depth': None,
            'smt_timeout': 200,
            'smt_retry_limit': 4,
            'trace_rewrites': False,
            'save_directory': None,
            'reinit': False,
            'use_booster': False,  # TODO: debug the booster backend, when it is as fast as legacy, change this to be True
        }


def prove(
    kmir: KMIR,
    options: ProveOptions,
) -> tuple[list[Proof], list[Proof]]:
    _LOGGER.info('Extracting claims from file')

    if kmir.prover:
        kmir_prover = kmir.prover
    else:
        raise ValueError('The prover object in kmir is not initialised.')

    claims = kmir_prover.get_all_claims(options.spec_file, options.claim)
    assert claims, ValueError(f'No claims found in file {options.spec_file}')

    passing: list[Proof] = []
    failing: list[Proof] = []
    for claim in claims:
        # start an rpc session with KoreServer
        server = kmir_prover.set_kore_server(smt_timeout=options.smt_timeout, smt_retry_limit=options.smt_retry_limit)

        with kmir_prover.rpc_session(server, claim.label, options.trace_rewrites) as session:
            proof = kmir_prover.initialise_a_proof(
                claim, session, save_directory=options.save_directory, reinit=options.reinit
            )
            res = kmir.prove_driver(proof, session, max_depth=options.depth)

            _, passed = res
            if passed == 'failed':
                failing.append(proof)
            else:
                passing.append(proof)
    return (passing, failing)


class ShowProofOptions(LoggingOptions, KCFGShowProofOptions):
    claim_label: str
    proof_dir: Path | None
    definition_dir: Path | None
    haskell_dir: Path | None

    @staticmethod
    def default() -> dict[str, Any]:
        llvm_dir_str = os.getenv('KMIR_LLVM_DIR')
        llvm_dir = Path(llvm_dir_str) if llvm_dir_str is not None else None
        haskell_dir_str = os.getenv('KMIR_HASKELL_DIR')
        haskell_dir = Path(haskell_dir_str) if haskell_dir_str is not None else None

        return {
            'proof_dir': None,
            'definition_dir': llvm_dir,
            'haskell_dir': haskell_dir,
        }


def show_proof(
    kmir: KMIR,
    options: ShowProofOptions,
) -> str:
    prover = kmir.prover

    if prover is None:
        raise ValueError(
            'The prover objectof KMIR is not initialized, provide path to the haskell definition directory'
        )
    else:
        kprove = prover.mir_prove
    # better error message with instructions to fix

    if options.proof_dir is None:
        raise ValueError('Proof directory not specified. Must specify with --proof-dir.')

    proof = Proof.read_proof_data(options.proof_dir, options.claim_label)
    # TODO: Create NodePrinter ???

    res_lines: list[str] = []

    if isinstance(proof, APRProof):
        kmir_show = APRProofShow(kprove)
        nodes = list(options.nodes)
        if options.pending:
            nodes += [node.id for node in proof.pending]
        if options.failing:
            nodes += [node.id for node in proof.failing]

        res_lines += kmir_show.show(
            proof,
            nodes=nodes,
            node_deltas=options.node_deltas,
            to_module=options.to_module,
            # minimize=minimize,
            # sort_collections=sort_collections,
        )

        if options.failure_info:
            with prover.rpc_session(prover.set_kore_server(), options.claim_label) as kcfg_explore:
                failures = APRFailureInfo.from_proof(proof, kcfg_explore, options.counterexample_info)
                res_lines += failures.print()
    else:  # TODO: implement the other proof types
        raise ValueError('Proof type not supported yet.')

    return '\n'.join(res_lines)


class ViewProofOptions(LoggingOptions):
    claim_label: str
    proof_dir: Path | None
    definition_dir: Path | None
    haskell_dir: Path | None

    @staticmethod
    def default() -> dict[str, Any]:
        llvm_dir_str = os.getenv('KMIR_LLVM_DIR')
        llvm_dir = Path(llvm_dir_str) if llvm_dir_str is not None else None
        haskell_dir_str = os.getenv('KMIR_HASKELL_DIR')
        haskell_dir = Path(haskell_dir_str) if haskell_dir_str is not None else None

        return {
            'proof_dir': None,
            'definition_dir': llvm_dir,
            'haskell_dir': haskell_dir,
        }


def view_proof(kmir: KMIR, options: ViewProofOptions) -> None:
    # TODO: include dirs

    prover = kmir.prover

    if prover is None:
        raise ValueError(
            'The prover objectof KMIR is not initialized, provide path to the haskell definition directory'
        )
    else:
        kprove = prover.mir_prove

    if options.proof_dir is None:
        raise ValueError('Proof directory not specified. Must specify with --proof-dir.')

    proof = Proof.read_proof_data(options.proof_dir, options.claim_label)

    if isinstance(proof, APRProof):
        # TODO: NodePrinter ???
        kmir_view = APRProofViewer(proof, kprove)
        kmir_view.run()
    else:
        raise ValueError('Proof type not supported yet.')
