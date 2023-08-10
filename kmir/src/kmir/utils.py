import logging
from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Final

from pyk.cterm import CTerm
from pyk.kast.inner import KInner, Subst
from pyk.kast.manip import set_cell
from pyk.kast.outer import KSequence
from pyk.kcfg import KCFG, KCFGExplore
from pyk.kcfg.semantics import KCFGSemantics
from pyk.kore.rpc import KoreClient, KoreExecLogFormat, kore_server
from pyk.ktool.kprint import KPrint
from pyk.ktool.kprove import KProve
from pyk.proof import APRBMCProof, APRBMCProver, APRProof, APRProver
from pyk.proof.equality import EqualityProof, EqualityProver
from pyk.proof.proof import Proof, ProofStatus
from pyk.utils import BugReport

_LOGGER: Final = logging.getLogger(__name__)


def kmir_prove(
    kprove: KProve,
    proof: Proof,
    kcfg_explore: KCFGExplore,
    max_depth: int | None = 1000,
    max_iterations: int | None = None,
    extract_branches: Callable[[CTerm], Iterable[KInner]] | None = None,
    abstract_node: Callable[[CTerm], CTerm] | None = None,
) -> bool:
    proof = proof
    terminal_rules: Iterable[str] = []  # TODO terminal rules
    cut_point_rules: Iterable[str] = []
    prover: APRBMCProver | APRProver | EqualityProver
    if type(proof) is APRBMCProof:
        prover = APRBMCProver(proof, kcfg_explore)
    elif type(proof) is APRProof:
        prover = APRProver(proof, kcfg_explore)
    elif type(proof) is EqualityProof:
        prover = EqualityProver(kcfg_explore=kcfg_explore, proof=proof)
    else:
        raise ValueError(f'Do not know how to build prover for proof: {proof}')
    try:
        if type(prover) is APRBMCProver or type(prover) is APRProver:
            prover.advance_proof(
                max_iterations=max_iterations,
                execute_depth=max_depth,
                terminal_rules=terminal_rules,
                cut_point_rules=cut_point_rules,
            )
            assert isinstance(proof, APRProof)
            failure_nodes = proof.failing
            if len(failure_nodes) == 0:
                _LOGGER.info(f'Proof passed: {proof.id}')
                return True
            else:
                _LOGGER.error(f'Proof failed: {proof.id}')
                return False
        elif type(prover) is EqualityProver:
            prover.advance_proof()
            if prover.proof.status == ProofStatus.PASSED:
                _LOGGER.info(f'Proof passed: {prover.proof.id}')
                return True
            if prover.proof.status == ProofStatus.FAILED:
                _LOGGER.error(f'Proof failed: {prover.proof.id}')
                if type(proof) is EqualityProof:
                    _LOGGER.info(proof.pretty(kprove))
                return False
            if prover.proof.status == ProofStatus.PENDING:
                _LOGGER.info(f'Proof pending: {prover.proof.id}')
                return False
        return False

    except Exception as e:
        _LOGGER.error(f'Proof crashed: {proof.id}\n{e}')
        return False
    failure_nodes = proof.pending + proof.failing
    if len(failure_nodes) == 0:
        _LOGGER.info(f'Proof passed: {proof.id}')
        return True
    else:
        _LOGGER.error(f'Proof failed: {proof.id}')
        return False


@contextmanager
def legacy_explore(
    kprint: KPrint,
    *,
    kcfg_semantics: KCFGSemantics | None = None,
    id: str | None = None,
    port: int | None = None,
    kore_rpc_command: str | Iterable[str] | None = None,
    llvm_definition_dir: Path | None = None,
    smt_timeout: int | None = None,
    smt_retry_limit: int | None = None,
    bug_report: BugReport | None = None,
    haskell_log_format: KoreExecLogFormat = KoreExecLogFormat.ONELINE,
    haskell_log_entries: Iterable[str] = (),
    log_axioms_file: Path | None = None,
    trace_rewrites: bool = False,
) -> Iterator[KCFGExplore]:
    # Old way of handling KCFGExplore, to be removed
    with kore_server(
        definition_dir=kprint.definition_dir,
        llvm_definition_dir=llvm_definition_dir,
        module_name=kprint.main_module,
        port=port,
        command=kore_rpc_command,
        bug_report=bug_report,
        smt_timeout=smt_timeout,
        smt_retry_limit=smt_retry_limit,
        haskell_log_format=haskell_log_format,
        haskell_log_entries=haskell_log_entries,
        log_axioms_file=log_axioms_file,
    ) as server:
        with KoreClient('localhost', server.port, bug_report=bug_report) as client:
            yield KCFGExplore(
                kprint=kprint,
                kore_client=client,
                kcfg_semantics=kcfg_semantics,
                id=id,
                trace_rewrites=trace_rewrites,
            )


def ensure_ksequence_on_k_cell(cterm: CTerm) -> CTerm:
    k_cell = cterm.cell('K_CELL')
    if type(k_cell) is not KSequence:
        _LOGGER.info('Introducing artificial KSequence on <k> cell.')
        return CTerm.from_kast(set_cell(cterm.kast, 'K_CELL', KSequence([k_cell])))
    return cterm


def print_failure_info(proof: Proof, kcfg_explore: KCFGExplore, counterexample_info: bool = False) -> list[str]:
    if type(proof) is APRProof or type(proof) is APRBMCProof:
        target = proof.kcfg.node(proof.target)

        res_lines: list[str] = []

        num_pending = len(proof.pending)
        num_failing = len(proof.failing)
        res_lines.append(
            f'{num_pending + num_failing} Failure nodes. ({num_pending} pending and {num_failing} failing)'
        )
        if num_pending > 0:
            res_lines.append('')
            res_lines.append('Pending nodes:')
            for node in proof.pending:
                res_lines.append('')
                res_lines.append(f'ID: {node.id}:')
        if num_failing > 0:
            res_lines.append('')
            res_lines.append('Failing nodes:')
            for node in proof.failing:
                res_lines.append('')
                res_lines.append(f'  Node id: {str(node.id)}')

                simplified_node, _ = kcfg_explore.cterm_simplify(node.cterm)
                simplified_target, _ = kcfg_explore.cterm_simplify(target.cterm)

                node_cterm = CTerm.from_kast(simplified_node)
                target_cterm = CTerm.from_kast(simplified_target)

                res_lines.append('  Failure reason:')
                _, reason = kcfg_explore.implication_failure_reason(node_cterm, target_cterm)
                res_lines += [f'    {line}' for line in reason.split('\n')]

                res_lines.append('  Path condition:')
                res_lines += [f'    {kcfg_explore.kprint.pretty_print(proof.path_constraints(node.id))}']
                if counterexample_info:
                    res_lines.extend(print_model(node, kcfg_explore))

        res_lines.append('')
        res_lines.append(
            'Join the Runtime Verification Discord server for support: https://discord.com/invite/CurfmXNtbN'
        )

        return res_lines
    elif type(proof) is EqualityProof:
        return ['EqualityProof failed.']
    else:
        raise ValueError('Unknown proof type.')


def print_model(node: KCFG.Node, kcfg_explore: KCFGExplore) -> list[str]:
    res_lines: list[str] = []
    result_subst = kcfg_explore.cterm_get_model(node.cterm)
    if type(result_subst) is Subst:
        res_lines.append('  Model:')
        for var, term in result_subst.to_dict().items():
            term_kast = KInner.from_dict(term)
            res_lines.append(f'    {var} = {kcfg_explore.kprint.pretty_print(term_kast)}')
    else:
        res_lines.append('  Failed to generate a model.')

    return res_lines
