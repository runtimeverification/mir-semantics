from collections.abc import Iterable
from pathlib import Path
from typing import Any

from pyk.cterm import CTerm
from pyk.kast.inner import KApply, KInner, KSequence, KVariable
from pyk.kcfg.semantics import KCFGSemantics
from pyk.ktool.kprove import KProve
from pyk.prelude.k import K
from pyk.proof.show import APRProofShow
from pyk.proof.tui import APRProofViewer

from .utils import NodeIdLike, get_apr_proof_for_spec, legacy_explore, print_failure_info


class KMIRSemantics(KCFGSemantics):
    def is_terminal(self, cterm: CTerm) -> bool:
        k_cell = cterm.cell('K_CELL')
        # <k> #halt </k>
        if k_cell == halt():
            return True
        elif type(k_cell) is KSequence:
            # <k> . </k>
            if k_cell.arity == 0:
                return True
            # <k> #halt </k>
            elif k_cell.arity == 1 and k_cell[0] == halt():
                return True
            elif k_cell.arity == 2 and k_cell[0] == halt() and type(k_cell[1]) is KVariable and k_cell[1].sort == K:
                return True
        return False

    @staticmethod
    def terminal_rules() -> list[str]:
        terminal_rules = ['MIR.halt']

        # TODO: break every step and add to terminal rules. Semantics does not support this currently
        return terminal_rules

    @staticmethod
    def cut_point_rules() -> list[str]:
        return []

    def extract_branches(self, cterm: CTerm) -> list[KInner]:
        return []

    def same_loop(self, cterm1: CTerm, cterm2: CTerm) -> bool:
        return False

    def abstract_node(self, cterm: CTerm) -> CTerm:
        return cterm


# @staticmethod
def halt() -> KApply:
    return KApply('#halt_MIR_KItem')


def show_kcfg(
    llvm_dir: Path,
    haskell_dir: Path,
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

    # kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    kprove = KProve(haskell_dir, use_directory=save_directory)
    assert not kprove, ValueError('Cannot use KProve object when it is None')

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


def view_kcfg(
    definition_dir: Path,
    haskell_dir: Path,
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
    # kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory)

    kprove = KProve(haskell_dir, use_directory=save_directory)
    assert not kprove, ValueError('Cannot use KProve object when it is None')

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
