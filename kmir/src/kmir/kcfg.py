from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pyk.proof import APRProof  # , EqualityProof, APRBMCProof
from pyk.proof.proof import Proof
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .kmir import KMIR
from .utils import NodeIdLike


def show_kcfg(
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
) -> None:
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

    if isinstance(proof, APRProof):
        kmir_show = APRProofShow(kprove)
        if pending:
            nodes = list(nodes) + [node.id for node in proof.pending]
        if failing:
            nodes = list(nodes) + [node.id for node in proof.failing]

        res_lines = kmir_show.show(
            proof,
            nodes=nodes,
            node_deltas=node_deltas,
            to_module=to_module,
            # minimize=minimize,
            # sort_collections=sort_collections,
        )

    # if failure_info:
    # with prover.rpc_session(prover.set_kore_server(), claim_label) as kcfg_explore:
    #        proof.failure_info.print()
    # TODO: print counterexample
    else:  # TODO: implement the other proof types
        raise ValueError('Proof type not supported yet.')

    print('\n'.join(res_lines))


def view_kcfg(
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
