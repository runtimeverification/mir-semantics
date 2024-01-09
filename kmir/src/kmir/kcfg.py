from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pyk.kcfg.show import KCFGShow
from pyk.proof.proof import Proof

from .kmir import KMIR
from .utils import NodeIdLike


def show_kcfg(
    kmir: KMIR,
    # spec_file: Path,
    claim_label: str,
    save_directory: Path,
    # exclude_claim_labels: Iterable[str] = (),
    # spec_module: str | None = None,
    # md_selector: str | None = None,
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
    prover = kmir.prover

    if prover is None:
        raise ValueError(
            'The prover objectof KMIR is not initialized, provide path to the haskell definition directory'
        )
    else:
        kprove = prover.mir_prove
    # better error message with instructions to fix

    """ proof = get_apr_proof_for_spec(  # read directly from the proof directory
        kprove,
        spec_file,
        save_directory=save_directory,
        spec_module_name=spec_module,
        # include_dirs=include_dirs,
        md_selector=md_selector,
        claim_labels=claim_labels,
        exclude_claim_labels=exclude_claim_labels,
    ) """
    proof = Proof.read_proof_data(save_directory, claim_label)

    if pending:
        nodes = list(nodes) + [node.id for node in proof.pending]
    if failing:
        nodes = list(nodes) + [node.id for node in proof.failing]

    # TODO: Create NodePrinter ???
    proof_show = KCFGShow(kprove)

    res_lines = proof_show.show(
        proof.kcfg,
        nodes=nodes,
        node_deltas=node_deltas,
        to_module=to_module,
        minimize=minimize,
        sort_collections=sort_collections,
    )

    # TODO： print failure_info
    """if failure_info:
        with legacy_explore(kprove, id=proof.id) as kcfg_explore:
            res_lines += print_failure_info(proof, kcfg_explore) """

    print('\n'.join(res_lines))


""" def view_kcfg(
    kmir: KMIR,
    claim_label: str,
    #spec_file: Path,
    save_directory: Path,
    #exclude_claim_labels: Iterable[str] = (),
    #spec_module: str | None = None,
    #md_selector: str | None = None,
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

    proof = APRProof.read_proof_data(save_directory, claim_label)

    # TODO: NodePrinter ???
    proof_view = APRProofViewer(proof, kprove)

    proof_view.run() """
