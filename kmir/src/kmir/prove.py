import logging
from pathlib import Path
from typing import Any, Final, Iterable, Optional

from pyk.proof import APRProof
from pyk.proof.proof import Proof
from pyk.proof.reachability import APRFailureInfo
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .kmir import KMIR
from .utils import NodeIdLike

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


def prove(
    kmir: KMIR,
    spec_file: Path,
    *,
    claim_label: Optional[str] = None,
    save_directory: Optional[Path] = None,
    reinit: bool = False,
    depth: Optional[int] = None,
    smt_timeout: Optional[int] = None,
    smt_retry_limit: Optional[int] = None,
    trace_rewrites: bool = False,
) -> tuple[list[Proof], list[Proof]]:
    _LOGGER.info('Extracting claims from file')

    if kmir.prover:
        kmir_prover = kmir.prover
    else:
        raise ValueError('The prover object in kmir is not initialised.')

    claims = kmir_prover.get_all_claims(spec_file, claim_label)
    assert claims, ValueError(f'No claims found in file {spec_file}')

    passing: list[Proof] = []
    failing: list[Proof] = []
    for claim in claims:
        # start an rpc session with KoreServer
        server = kmir_prover.set_kore_server(smt_timeout=smt_timeout, smt_retry_limit=smt_retry_limit)

        with kmir_prover.rpc_session(server, claim.label, trace_rewrites) as session:
            proof = kmir_prover.initialise_a_proof(claim, session, save_directory=save_directory, reinit=reinit)
            res = kmir.prove_driver(proof, session, max_depth=depth)

            _, passed = res
            if passed == 'failed':
                failing.append(proof)
            else:
                passing.append(proof)
    return (passing, failing)


def show_proof(
    kmir: KMIR,
    claim_label: str,
    proof_dir: Path,
    nodes: Iterable[NodeIdLike] = (),
    node_deltas: Iterable[tuple[NodeIdLike, NodeIdLike]] = (),
    to_module: bool = False,
    # minimize: bool = True,
    failure_info: bool = False,
    # sort_collections: bool = False,
    pending: bool = False,
    failing: bool = False,
    counterexample_info: bool = False,
    **kwargs: Any,
) -> str:
    prover = kmir.prover

    if prover is None:
        raise ValueError(
            'The prover objectof KMIR is not initialized, provide path to the haskell definition directory'
        )
    else:
        kprove = prover.mir_prove
    # better error message with instructions to fix

    proof = Proof.read_proof_data(proof_dir, claim_label)
    # TODO: Create NodePrinter ???

    res_lines: list[str] = []

    if isinstance(proof, APRProof):
        kmir_show = APRProofShow(kprove)
        if pending:
            nodes = list(nodes) + [node.id for node in proof.pending]
        if failing:
            nodes = list(nodes) + [node.id for node in proof.failing]

        res_lines += kmir_show.show(
            proof,
            nodes=nodes,
            node_deltas=node_deltas,
            to_module=to_module,
            # minimize=minimize,
            # sort_collections=sort_collections,
        )

        if failure_info:
            with prover.rpc_session(prover.set_kore_server(), claim_label) as kcfg_explore:
                failures = APRFailureInfo.from_proof(proof, kcfg_explore, counterexample_info)
                res_lines += failures.print()
    else:  # TODO: implement the other proof types
        raise ValueError('Proof type not supported yet.')

    return '\n'.join(res_lines)


def view_proof(
    kmir: KMIR,
    claim_label: str,
    proof_dir: Path,
    **kwargs: Any,
) -> None:
    # TODO: include dirs

    prover = kmir.prover

    if prover is None:
        raise ValueError(
            'The prover objectof KMIR is not initialized, provide path to the haskell definition directory'
        )
    else:
        kprove = prover.mir_prove

    proof = Proof.read_proof_data(proof_dir, claim_label)

    if isinstance(proof, APRProof):
        # TODO: NodePrinter ???
        kmir_view = APRProofViewer(proof, kprove)
        kmir_view.run()
    else:
        raise ValueError('Proof type not supported yet.')
