"""Compositional Symbolic Execution (CSE) for KMIR.

Summary rules are K rewrite rules that match function calls by name and
rewrite them to the function's effect, following the same pattern as
p-token cheatcodes.  Rules are injected via ``add-module`` and applied
by the backend automatically — no ``custom_step`` needed for reuse.

Requires the slotStore refactor (PR #1059).
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CTerm
from pyk.kast.inner import KApply, KRewrite, KSequence, KSort, KToken, KVariable, Subst
from pyk.kast.att import Atts as AttKeys
from pyk.kast.att import AttEntry, KAtt
from pyk.kast.outer import KFlatModule, KImport, KRule
from pyk.kast.prelude.ml import mlAnd, mlEqualsTrue
from pyk.proof.reachability import APRProof

from .kast import SymbolicMode, make_call_config
from .kmir import KMIR, KMIRSemantics

if TYPE_CHECKING:
    from collections.abc import Mapping

    from pyk.cterm import CTerm
    from pyk.kast.inner import KInner
    from pyk.kcfg import KCFG

    from .options import ProveOpts
    from .smir import SMIRInfo, Ty

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class CoverPath:
    """One execution path through a callee, extracted from a cover node."""

    node_id: int
    constraints: tuple[KInner, ...]
    return_value: KInner | None
    slot_reads: dict[int, KInner]  # slot_handle -> value (read-only)
    slot_diffs: dict[int, tuple[KInner, KInner]]  # slot_handle -> (old, new)


@dataclass
class CalleeSummary:
    """Summary for one callee function: a set of K rules."""

    name: str
    rules: list[KRule] = field(default_factory=list)
    module: KFlatModule | None = None
    prove_time: float = 0.0
    num_covers: int = 0
    num_stuck: int = 0


@dataclass
class CSEResult:
    """Result of a full CSE prove run."""

    final_proof: APRProof | None = None
    callee_summaries: dict[str, CalleeSummary] = field(default_factory=dict)
    summary_modules: list[KFlatModule] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 1: Callee Proof
# ---------------------------------------------------------------------------


def prove_callee(
    kmir: KMIR,
    smir_info: SMIRInfo,
    callee_name: str,
    *,
    proof_dir: Path | None = None,
    max_iterations: int = 1000,
    max_depth: int = 10000,
    init_subst: dict[str, KInner] | None = None,
) -> APRProof:
    """Prove a callee function to completion (standalone, no caller context).

    Args:
        init_subst: Optional substitution to apply to the init cterm's config.
            Use this to pre-condition the symbolic state, e.g. replacing raw
            Aggregate slots with domain-specific sorts like PAccountMint.
    """
    from ._prove import _prove_sequential

    proof_id = f'cse-callee.{_sanitize_name(callee_name)}'
    proof = _make_callee_proof(kmir, smir_info, callee_name, proof_id, proof_dir=proof_dir, init_subst=init_subst)

    from .options import ProveOpts

    opts = ProveOpts(
        rs_file=Path('/dev/null'),  # not used by _prove_sequential
        max_iterations=max_iterations,
        max_depth=max_depth,
    )
    _prove_sequential(
        kmir,
        proof,
        opts=opts,
        label=f'cse-callee-{callee_name}',
        cut_point_rules=[],  # no cut-points for callee proofs
    )
    return proof


def _make_callee_proof(
    kmir: KMIR,
    smir_info: SMIRInfo,
    callee_name: str,
    proof_id: str,
    *,
    proof_dir: Path | None = None,
    init_subst: dict[str, KInner] | None = None,
) -> APRProof:
    """Create an APRProof for a standalone callee function."""
    from pyk.kast.manip import abstract_term_safely, set_cell, split_config_from

    lhs_config, constraints = make_call_config(
        kmir.definition,
        smir_info=smir_info,
        start_symbol=callee_name,
        mode=SymbolicMode(),
    )

    # Apply optional substitution to pre-condition the symbolic state
    if init_subst:
        for cell_name, value in init_subst.items():
            lhs_config = set_cell(lhs_config, cell_name, value)

    lhs = CTerm(lhs_config, constraints)

    var_config, var_subst = split_config_from(lhs_config)
    _rhs_subst: dict[str, KInner] = {
        v_name: abstract_term_safely(KVariable('_'), base_name=v_name) for v_name in var_subst
    }
    _rhs_subst['K_CELL'] = KSequence([KMIR.Symbols.END_PROGRAM])
    rhs = CTerm(Subst(_rhs_subst)(var_config))

    from pyk.kcfg import KCFG

    kcfg = KCFG()
    init_node = kcfg.create_node(lhs)
    target_node = kcfg.create_node(rhs)
    return APRProof(proof_id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)


# ---------------------------------------------------------------------------
# Phase 2: Summary Rule Generation
# ---------------------------------------------------------------------------


def extract_cover_paths(proof: APRProof) -> list[CoverPath]:
    """Extract execution paths from callee proof cover nodes."""
    kcfg = proof.kcfg
    init_node = kcfg.node(proof.init)
    paths: list[CoverPath] = []

    for cover in kcfg.covers():
        if cover.target.id != proof.target:
            continue
        source_node = cover.source
        # Collect path constraints by walking from init to this cover
        path_constraints = _collect_path_constraints(kcfg, proof.init, source_node.id)

        # Extract return value from RETVAL_CELL
        retval = _extract_return_value(source_node.cterm)

        # Diff slotStore between init and cover
        init_store = _extract_slot_store(init_node.cterm)
        cover_store = _extract_slot_store(source_node.cterm)
        slot_reads, slot_diffs = _diff_slot_stores(init_store, cover_store)

        paths.append(
            CoverPath(
                node_id=source_node.id,
                constraints=tuple(path_constraints),
                return_value=retval,
                slot_reads=slot_reads,
                slot_diffs=slot_diffs,
            )
        )
    return paths


def _collect_path_constraints(kcfg: KCFG, init_id: int, target_id: int) -> list[KInner]:
    """Walk KCFG from init to target, collecting split constraints."""
    # Use BFS to find path
    parent: dict[int, int] = {}
    split_constraints: dict[int, KInner] = {}
    visited = {init_id}
    queue = [init_id]

    while queue:
        node_id = queue.pop(0)
        if node_id == target_id:
            break

        # Check edges
        for edge in kcfg.edges(source_id=node_id):
            child = edge.target.id
            if child not in visited:
                visited.add(child)
                parent[child] = node_id
                queue.append(child)

        # Check splits
        for split in kcfg.splits(source_id=node_id):
            for child_id, csubst in split.splits.items():
                if child_id not in visited:
                    visited.add(child_id)
                    parent[child_id] = node_id
                    # Extract constraint from CSubst
                    if csubst.constraints:
                        split_constraints[child_id] = mlAnd(list(csubst.constraints))
                    queue.append(child_id)

        # Check covers (target might be reached through a cover)
        for cover in kcfg.covers(source_id=node_id):
            child = cover.target.id
            if child not in visited:
                visited.add(child)
                parent[child] = node_id
                queue.append(child)

    # Trace back from target to init, collecting constraints
    constraints: list[KInner] = []
    node = target_id
    while node in parent:
        if node in split_constraints:
            constraints.append(split_constraints[node])
        node = parent[node]

    return list(reversed(constraints))


def _extract_return_value(cterm: CTerm) -> KInner | None:
    """Extract the return value from RETVAL_CELL."""
    try:
        retval_cell = cterm.cell('RETVAL_CELL')
        # retval_cell is return(VAL) with full label name return(_)_KMIR-CONFIGURATION_RetVal_Value
        if isinstance(retval_cell, KApply) and 'return' in retval_cell.label.name:
            return retval_cell.args[0]
    except Exception:
        pass
    return None


def _extract_slot_store(cterm: CTerm) -> KInner:
    """Extract the <slotStore> cell from a cterm."""
    return cterm.cell('SLOTSTORE_CELL')


def _diff_slot_stores(
    init_store: KInner, cover_store: KInner
) -> tuple[dict[int, KInner], dict[int, tuple[KInner, KInner]]]:
    """Diff two slotStore maps. Returns (read_only_slots, modified_slots)."""
    # For now, return empty diffs — we'll refine this when handling side effects
    # The initial implementation targets pure functions (no slotStore modification)
    return {}, {}


def generate_summary_rules(
    callee_name: str,
    cover_paths: list[CoverPath],
    init_cterm: CTerm,
) -> list[KRule]:
    """Generate K rewrite rules from callee cover paths."""
    rules: list[KRule] = []

    for idx, path in enumerate(cover_paths):
        rule = _build_summary_rule(callee_name, path, idx, init_cterm)
        if rule is not None:
            rules.append(rule)

    return rules


_EXEC_TERMINATOR_CALL = '#execTerminatorCall(_,_,_,_,_,_,_)_KMIR-CONTROL-FLOW_KItem_Ty_MonoItemKind_Operands_Place_MaybeBasicBlockIdx_UnwindAction_Span'
_SET_LOCAL_VALUE = '#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation'
_CONTINUE_AT = '#continueAt(_)_KMIR-CONTROL-FLOW_KItem_MaybeBasicBlockIdx'
_GET_FUNCTION_NAME = 'getFunctionName(_)_KMIR-CONTROL-FLOW_String_MonoItemKind'
_EQ_STRING = '_==String__STRING-COMMON_Bool_String_String'


def _build_summary_rule(
    callee_name: str,
    path: CoverPath,
    path_idx: int,
    init_cterm: CTerm,
) -> KRule | None:
    """Build one K rule for a single execution path.

    Uses cterm_build_rule to construct a properly-structured rule from
    init CTerm (at function call) → final CTerm (after return).
    The init CTerm's K_CELL is #execTerminatorCall(...) and the final
    CTerm's K_CELL is #setLocalValue(DEST, RET) ~> #continueAt(TARGET).
    """
    from pyk.cterm.cterm import cterm_build_rule

    if path.return_value is None:
        _LOGGER.warning(f'CSE: no return value for {callee_name} path {path_idx}, skipping')
        return None

    # Variables for the rule
    func_var = KVariable('CSE_FUNC')
    dest_var = KVariable('CSE_DEST')
    target_var = KVariable('CSE_TARGET')
    cont_var = KVariable('CSE_CONT')

    # Build init CTerm: same as init_cterm but with K_CELL = #execTerminatorCall ~> CONT
    lhs_k = KSequence([
        KApply(_EXEC_TERMINATOR_CALL, [
            KVariable('CSE_TY'), func_var, KVariable('CSE_ARGS'),
            dest_var, target_var, KVariable('CSE_UNWIND'), KVariable('CSE_SPAN'),
        ]),
        cont_var,
    ])

    # Build final CTerm: same config but K_CELL = #setLocalValue(DEST, RET) ~> #continueAt(TARGET)
    rhs_k = KSequence([
        KApply(_SET_LOCAL_VALUE, [dest_var, path.return_value]),
        KApply(_CONTINUE_AT, [target_var]),
    ])

    # Use the init_cterm config as the base, replace K_CELL
    from pyk.kast.manip import set_cell

    init_config = set_cell(init_cterm.config, 'K_CELL', lhs_k)
    final_config = set_cell(init_cterm.config, 'K_CELL', rhs_k)

    # Build requires: getFunctionName(FUNC) ==String "callee_name" andBool path constraints
    func_name_check = KApply(_EQ_STRING, [
        KApply(_GET_FUNCTION_NAME, [func_var]),
        KToken(f'"{callee_name}"', KSort('String')),
    ])

    constraints: list[KInner] = [mlEqualsTrue(func_name_check)]
    constraints.extend(path.constraints)

    init_cterm_rule = CTerm(init_config, tuple(constraints))
    final_cterm_rule = CTerm(final_config)

    rule_label = f'cse-summary-{_sanitize_name(callee_name)}-path-{path_idx}'

    rule, _subst = cterm_build_rule(
        rule_label,
        init_cterm_rule,
        final_cterm_rule,
        priority=30,
    )
    return rule


def _sanitize_name(name: str) -> str:
    """Sanitize function name for use as K identifiers (module names, rule labels)."""
    import re

    result = name.replace('::', '-').replace('<', '').replace('>', '').replace(' ', '').replace('_', '-')
    result = re.sub(r'[^a-zA-Z0-9-]', '', result)
    # Kore identifiers must start with a letter
    if result and not result[0].isalpha():
        result = 'cse' + result
    return result


def build_summary_module(callee_name: str, rules: list[KRule]) -> KFlatModule:
    """Wrap summary rules in a KFlatModule for add-module injection."""
    module_name = f'CSE-SUMMARY-{_sanitize_name(callee_name).upper()}'
    return KFlatModule(module_name, sentences=rules, imports=[KImport('KMIR')])


# ---------------------------------------------------------------------------
# Phase 3: Pipeline Orchestration
# ---------------------------------------------------------------------------


def cse_prove(
    opts: ProveOpts,
    *,
    summary_dir: Path | None = None,
    callee_names: list[str] | None = None,
) -> CSEResult:
    """Full CSE pipeline: prove callees, generate summaries, prove caller with summaries."""
    from .kompile import kompile_smir
    from .smir import SMIRInfo

    result = CSEResult()
    t_start = time.time()

    # Load SMIR
    smir_path = opts.rs_file
    smir_info = SMIRInfo.load(smir_path)

    # Kompile
    kmir = kompile_smir(smir_path, smir_info, proof_dir=opts.proof_dir)

    # Determine callees to summarize
    if callee_names is None:
        callee_names = _find_summary_worthy_callees(smir_info, opts.start_symbol or 'main')

    _LOGGER.info(f'CSE: {len(callee_names)} callees to summarize')

    # Phase 1+2: For each callee, prove and generate summary
    for callee_name in callee_names:
        summary = _prove_and_summarize_callee(
            kmir, smir_info, callee_name,
            proof_dir=opts.proof_dir,
        )
        result.callee_summaries[callee_name] = summary
        if summary.module is not None:
            result.summary_modules.append(summary.module)
            _LOGGER.info(
                f'CSE: {callee_name}: {summary.num_covers} covers, '
                f'{len(summary.rules)} rules, {summary.prove_time:.1f}s'
            )
        else:
            _LOGGER.warning(f'CSE: {callee_name}: no summary generated')

    # Phase 3: Prove caller with summary modules
    _LOGGER.info(f'CSE: proving caller with {len(result.summary_modules)} summary modules')
    result.final_proof = _prove_with_summaries(
        kmir, smir_info, opts, result.summary_modules,
    )

    elapsed = time.time() - t_start
    status = 'PASSED' if result.final_proof and result.final_proof.passed else 'FAILED'
    _LOGGER.info(f'CSE: {status} in {elapsed:.1f}s')
    return result


def _prove_and_summarize_callee(
    kmir: KMIR,
    smir_info: SMIRInfo,
    callee_name: str,
    *,
    proof_dir: Path | None = None,
    init_subst: dict[str, KInner] | None = None,
    dep_modules: list[KFlatModule] | None = None,
) -> CalleeSummary:
    """Prove a callee and generate summary rules.

    Args:
        init_subst: Optional substitution for PAccount pre-conditioning.
        dep_modules: Summary modules of sub-callees to inject via add-module
            during the callee proof (multi-level composition).
    """
    summary = CalleeSummary(name=callee_name)
    t0 = time.time()

    if dep_modules:
        # Multi-level: prove callee with sub-callee summaries injected
        try:
            proof = _prove_callee_with_deps(
                kmir, smir_info, callee_name,
                dep_modules=dep_modules,
                init_subst=init_subst,
                proof_dir=proof_dir,
            )
        except Exception as e:
            _LOGGER.warning(f'CSE: callee proof failed for {callee_name}: {e}')
            return summary
    else:
        try:
            proof = prove_callee(kmir, smir_info, callee_name, proof_dir=proof_dir, init_subst=init_subst)
        except Exception as e:
            _LOGGER.warning(f'CSE: callee proof failed for {callee_name}: {e}')
            return summary

    summary.prove_time = time.time() - t0
    summary.num_covers = len([c for c in proof.kcfg.covers() if c.target.id == proof.target])
    summary.num_stuck = len([n for n in proof.kcfg.leaves if proof.kcfg.is_stuck(n.id)])

    if summary.num_covers == 0:
        _LOGGER.warning(f'CSE: callee {callee_name} has 0 covers, skipping summary')
        return summary

    if summary.num_stuck > 0:
        _LOGGER.warning(f'CSE: callee {callee_name} has {summary.num_stuck} stuck nodes')

    # Extract cover paths and generate rules
    init_cterm = proof.kcfg.node(proof.init).cterm
    cover_paths = extract_cover_paths(proof)
    summary.rules = generate_summary_rules(callee_name, cover_paths, init_cterm)

    if summary.rules:
        summary.module = build_summary_module(callee_name, summary.rules)

    return summary


def _prove_callee_with_deps(
    kmir: KMIR,
    smir_info: SMIRInfo,
    callee_name: str,
    *,
    dep_modules: list[KFlatModule],
    init_subst: dict[str, KInner] | None = None,
    proof_dir: Path | None = None,
    max_iterations: int = 1000,
    max_depth: int = 10000,
) -> APRProof:
    """Prove a callee with dependency summary modules injected (multi-level)."""
    from pyk.cterm import cterm_symbolic
    from pyk.kcfg.explore import KCFGExplore
    from pyk.proof.reachability import APRProver

    proof_id = f'cse-callee.{_sanitize_name(callee_name)}'
    proof = _make_callee_proof(kmir, smir_info, callee_name, proof_id, proof_dir=proof_dir, init_subst=init_subst)

    with cterm_symbolic(
        kmir.definition,
        kmir.definition_dir,
        llvm_definition_dir=kmir.llvm_library_dir,
        bug_report=kmir.bug_report,
        simplify_each=30,
    ) as cts:
        for mod in dep_modules:
            cts.add_module(mod, name_as_id=True)
        kcfg_explore = KCFGExplore(cts, kcfg_semantics=KMIRSemantics())
        prover = APRProver(kcfg_explore, execute_depth=max_depth)
        prover.advance_proof(proof, max_iterations=max_iterations)

    return proof


def _prove_with_summaries(
    kmir: KMIR,
    smir_info: SMIRInfo,
    opts: ProveOpts,
    summary_modules: list[KFlatModule],
) -> APRProof:
    """Prove the main target with summary modules injected via add-module."""
    from pyk.cterm import cterm_symbolic
    from pyk.kcfg.explore import KCFGExplore
    from pyk.proof.reachability import APRProver

    from ._prove import apr_proof_from_smir

    start_symbol = opts.start_symbol or 'main'
    proof_id = f'cse-reuse.{start_symbol}'
    proof = apr_proof_from_smir(kmir, proof_id, smir_info, start_symbol=start_symbol, proof_dir=opts.proof_dir)

    with cterm_symbolic(
        kmir.definition,
        kmir.definition_dir,
        llvm_definition_dir=kmir.llvm_library_dir,
        bug_report=kmir.bug_report,
        simplify_each=30,
    ) as cts:
        # Inject summary modules
        for module in summary_modules:
            module_name = cts.add_module(module, name_as_id=True)
            _LOGGER.info(f'CSE: added summary module {module_name}')

        kcfg_explore = KCFGExplore(cts, kcfg_semantics=KMIRSemantics())
        prover = APRProver(kcfg_explore, execute_depth=opts.max_depth)
        prover.advance_proof(
            proof,
            max_iterations=opts.max_iterations,
        )

    return proof


# ---------------------------------------------------------------------------
# Callee selection
# ---------------------------------------------------------------------------


def _find_summary_worthy_callees(smir_info: SMIRInfo, start_symbol: str) -> list[str]:
    """Find functions worth summarizing (non-trivial, non-stdlib callees)."""
    # For now, return empty — the caller specifies callees explicitly
    # TODO: implement call graph analysis and heuristic filtering
    return []
