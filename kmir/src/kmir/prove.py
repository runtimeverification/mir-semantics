import logging
import sys
from pathlib import Path
from typing import Final, Iterable

from pyk.cterm import CTerm
from pyk.kast.outer import KApply, KClaim, KRewrite
from pyk.kcfg import KCFG
from pyk.ktool.kprove import KProve
from pyk.proof import APRProof
from pyk.proof.equality import EqualityProof
from pyk.proof.proof import Proof
from pyk.utils import BugReport

from .kmir_cfg import KMIRSemantics
from .utils import ensure_ksequence_on_k_cell, kmir_prove, legacy_explore, print_failure_info

_LOGGER: Final = logging.getLogger(__name__)


def prove(
    llvm_dir: Path,
    haskell_dir: Path,
    spec_file: Path,
    *,
    use_booster: bool = False,
    bug_report: BugReport | None = None,
    save_directory: Path | None = None,
    reinit: bool = False,
    depth: int | None = None,
    smt_timeout: int | None = None,
    smt_retry_limit: int | None = None,
    trace_rewrites: bool = False,
    kore_rpc_command: str | Iterable[str] | None = None,
) -> None:
    # kmir = KMIR(definition_dir, haskell_dir, use_directory=save_directory, bug_report=br)
    kprove = KProve(haskell_dir, use_directory=save_directory)

    assert not kprove, ValueError('Cannot use KProve object when it is None')

    _LOGGER.info('Extracting claims from file')
    claims = kprove.get_claims(spec_file)

    assert not claims, ValueError(f'No claims found in file {spec_file}')

    if kore_rpc_command is None:
        kore_rpc_command = ('kore-rpc-booster',) if use_booster else ('kore-rpc',)
    elif isinstance(kore_rpc_command, str):
        kore_rpc_command = kore_rpc_command.split()

    def is_functional(claim: KClaim) -> bool:
        claim_lhs = claim.body
        if type(claim_lhs) is KRewrite:
            claim_lhs = claim_lhs.lhs
        return not (type(claim_lhs) is KApply and claim_lhs.label.name == '<generatedTop>')

    def _init_and_run_proof(claim: KClaim) -> tuple[bool, list[str] | None]:
        with legacy_explore(
            kprove,
            kcfg_semantics=KMIRSemantics(),
            id=claim.label,
            llvm_definition_dir=llvm_dir if use_booster else None,
            bug_report=bug_report,
            kore_rpc_command=kore_rpc_command,
            smt_timeout=smt_timeout,
            smt_retry_limit=smt_retry_limit,
            trace_rewrites=trace_rewrites,
        ) as kcfg_explore:
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

                    _LOGGER.info(f'Simplifying initial and target node: {claim.label}')
                    new_init, _ = kcfg_explore.cterm_simplify(new_init)
                    new_target, _ = kcfg_explore.cterm_simplify(new_target)
                    if CTerm._is_bottom(new_init.kast):
                        raise ValueError('Simplifying initial node led to #Bottom, are you sure your LHS is defined?')
                    if CTerm._is_top(new_target.kast):
                        raise ValueError('Simplifying target node led to #Bottom, are you sure your RHS is defined?')

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
