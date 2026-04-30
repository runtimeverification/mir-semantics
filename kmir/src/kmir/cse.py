from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cterm import CSubst, CTerm, cterm_build_rule
from pyk.kast.inner import KApply, KInner, KSequence, KToken, KVariable, Subst
from pyk.kast.manip import (
    abstract_term_safely,
    bool_to_ml_pred,
    bottom_up,
    extract_lhs,
    extract_rhs,
    flatten_label,
    ml_pred_to_bool,
    set_cell,
    split_config_from,
)
from pyk.kast.prelude.collections import list_empty
from pyk.kast.prelude.kbool import FALSE, TRUE, andBool, notBool
from pyk.kast.outer import KFlatModule, KImport, KRule
from pyk.kast.prelude.ml import is_top, mlAnd, mlEqualsFalse
from pyk.kcfg import KCFG
from pyk.kcfg.kcfg import Branch, NDBranch, Step, Stuck, Vacuous
from pyk.proof.reachability import APRProof, APRProver
from pyk.utils import shorten_hashes

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyk.cterm.symbolic import CTermSymbolic
    from pyk.kcfg.kcfg import KCFGExtendResult

    from .kmir import KMIR
    from .options import ProveOpts
    from .smir import SMIRInfo


_LOGGER = logging.getLogger(__name__)

_EXEC_BLOCK_IDX = '#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx'
_SET_LOCAL_VALUE = '#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation'
_DECREMENT_REF = '#decrementRef(_)_RT-DATA_Value_Value'
_INCREMENT_REF = '#incrementRef(_)_RT-DATA_Value_Value'
_CSE_WRITE_BACK = '#cseWriteBack(_,_)_RT-DATA_KItem_Value_Value'
_TRAVERSE_PROJECTION = (
    '#traverseProjection(_,_,_,_,_,_)_RT-DATA_ProjectionResult_WriteTo_Value_ProjectionElems_Contexts_FrameLocals_List'
)
_FRAME_LOCALS = '#frameLocals(_,_)_RT-DATA_FrameLocals_List_List'
_READ_PROJECTION = '#readProjection(_)_RT-DATA_KItem_Bool'
_TO_LOCAL = 'toLocal(_)_RT-DATA_WriteTo_Int'
_CONTEXTS_EMPTY = '.List{"___RT-DATA_Contexts_Context_Contexts"}_Contexts'
_PROJECTION_ELEMS_EMPTY = 'ProjectionElems::empty'
_PROJECTION_ELEMS_APPEND = 'ProjectionElems::append'
_PROJECTION_DEREF = 'ProjectionElem::Deref'
_REF_VALUE_LABELS = ('Value::Reference', 'Value::PtrLocal')
_DEREF_EVALUATION_DEPTH = 1
_REFERENCE_WRITEBACK_MAX_DEPTH = 4096


@dataclass(frozen=True)
class CSECallInfo:
    """Call-boundary data required to instantiate and apply a CSE summary."""

    function: str
    args: tuple[KInner, ...]
    destination: KInner
    target: KInner


@dataclass(frozen=True)
class CSEOutcome:
    """One possible result of applying a summary.

    guard: when this outcome is valid. Includes caller assumptions, branch
        path constraints, and residual post-state constraints.
    final: callee final config/effect. New summaries store constraints in guard.
    rule: backend-ready rewrite rule generated from this outcome, if supported.
    metadata: proof/debug data such as node id, path rules, depth, and kind.
    """

    guard: KInner
    final: CTerm
    metadata: dict[str, object]
    rule: KRule | None = None

    def to_dict(self) -> dict[str, object]:
        """Serialize a guarded summary outcome to the stable summary-store schema."""
        return {
            'guard': self.guard.to_dict(),
            'final': self.final.to_dict(),
            'metadata': self.metadata,
            'rule': self.rule.to_dict() if self.rule is not None else None,
        }

    @staticmethod
    def from_dict(dct: dict[str, object]) -> CSEOutcome:
        """Deserialize one guarded summary outcome from the summary-store schema."""
        return CSEOutcome(
            guard=KInner.from_dict(_expect_dict(dct['guard'])),
            final=CTerm.from_dict(_expect_dict(dct['final'])),
            metadata=dict(_expect_dict(dct.get('metadata', {}))),
            rule=KRule.from_dict(_expect_dict(rule)) if (rule := dct.get('rule')) is not None else None,
        )


@dataclass(frozen=True)
class CSESummary:
    """One reusable function summary.

    initial: callee-entry schema used to match future call sites.
        Persisted summaries keep initial.constraints empty.
    outcomes: guarded final effects under this schema. Supported outcomes carry
        already compiled K rules; apply never rebuilds rules from outcomes.
    source: proof id/status and update metadata.

    Flow:
        generate proof -> initial schema + guarded outcomes + K rules
        apply summary  -> add stored K rules and ask backend to step
        regenerate     -> merge new proof-generated rules into this summary
    """

    function: str
    initial: CTerm
    outcomes: tuple[CSEOutcome, ...]
    source: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        """Serialize a CSE summary without derived coverage metadata."""
        return {
            'schema': 1,
            'function': self.function,
            'initial': self.initial.to_dict(),
            'outcomes': [outcome.to_dict() for outcome in self.outcomes],
            'source': self.source,
        }

    @staticmethod
    def from_dict(dct: dict[str, object]) -> CSESummary:
        """Deserialize a schema-1 CSE summary and reject unsupported schemas."""
        schema = dct.get('schema')
        if schema != 1:
            raise ValueError(f'Unsupported CSE summary schema: {schema}')
        function = dct['function']
        if not isinstance(function, str):
            raise TypeError(f'Expected str, got {type(function).__name__}')
        outcomes = dct['outcomes']
        if not isinstance(outcomes, list):
            raise TypeError(f'Expected list, got {type(outcomes).__name__}')
        return CSESummary(
            function=function,
            initial=CTerm.from_dict(_expect_dict(dct['initial'])),
            outcomes=tuple(CSEOutcome.from_dict(_expect_dict(outcome)) for outcome in outcomes),
            source=dict(_expect_dict(dct.get('source', {}))),
        )


class CSESummaryStore:
    """Filesystem store for one JSON summary and one proof directory per function."""

    path: Path

    def __init__(self, path: Path | str) -> None:
        """Initialize the summary store directories and manifest at PATH."""
        self.path = Path(path).resolve()
        self.summaries_dir.mkdir(parents=True, exist_ok=True)
        self.proofs_dir.mkdir(parents=True, exist_ok=True)
        self._write_manifest()

    @property
    def summaries_dir(self) -> Path:
        """Return the directory that stores serialized summaries."""
        return self.path / 'summaries'

    @property
    def traces_dir(self) -> Path:
        """Return the directory that stores structure-preserving trace entries."""
        return self.path / 'traces'

    @property
    def subsumptions_dir(self) -> Path:
        """Return the directory that stores successful trace subsumption results."""
        return self.path / 'subsumptions'

    @property
    def proofs_dir(self) -> Path:
        """Return the directory that stores callee summary proof data."""
        return self.path / 'proofs'

    def load(self, function: str) -> CSESummary | None:
        """Load the single persisted summary for FUNCTION, if one exists."""
        summary_path = self._summary_path(function)
        if not summary_path.is_file():
            return None
        return CSESummary.from_dict(json.loads(summary_path.read_text()))

    def save(self, summary: CSESummary) -> None:
        """Persist SUMMARY under its function key and keep the manifest present."""
        summary_path = self._summary_path(summary.function)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        self._write_manifest()

    def load_trace(self, key: str) -> KCFGExtendResult | None:
        """Load a cached structure-preserving extension result."""
        trace_path = self._trace_path(key)
        if not trace_path.is_file():
            return None
        return _trace_result_from_dict(json.loads(trace_path.read_text()))

    def has_trace(self, key: str) -> bool:
        """Return whether KEY has a persisted structure-preserving trace entry."""
        return self._trace_path(key).is_file()

    def save_trace(self, key: str, result: KCFGExtendResult) -> None:
        """Persist one structure-preserving extension result if it is serializable."""
        trace_path = self._trace_path(key)
        if trace_path.is_file():
            return
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(json.dumps(_trace_result_to_dict(result), sort_keys=True, separators=(',', ':')))
        self._write_manifest()

    def load_subsumption(self, key: str) -> CSubst | None:
        """Load a cached successful subsumption result."""
        subsumption_path = self._subsumption_path(key)
        if not subsumption_path.is_file():
            return None
        return CSubst.from_dict(json.loads(subsumption_path.read_text()))

    def save_subsumption(self, key: str, csubst: CSubst) -> None:
        """Persist one successful subsumption result for trace replay."""
        subsumption_path = self._subsumption_path(key)
        if subsumption_path.is_file():
            return
        subsumption_path.parent.mkdir(parents=True, exist_ok=True)
        subsumption_path.write_text(json.dumps(csubst.to_dict(), sort_keys=True, separators=(',', ':')))
        self._write_manifest()

    def proof_id(self, function: str) -> str:
        """Return the deterministic APR proof id used for FUNCTION summaries."""
        return f'cse-callee.{_safe_function_id(function)}'

    def _summary_path(self, function: str) -> Path:
        """Return the filesystem path for FUNCTION's summary JSON."""
        return self.summaries_dir / f'{_safe_function_id(function)}.json'

    def _trace_path(self, key: str) -> Path:
        """Return the filesystem path for a cached trace entry."""
        return self.traces_dir / f'{key}.json'

    def _subsumption_path(self, key: str) -> Path:
        """Return the filesystem path for a cached subsumption entry."""
        return self.subsumptions_dir / f'{key}.json'

    def _write_manifest(self) -> None:
        """Create the summary-store manifest if it is not already present."""
        manifest_path = self.path / 'manifest.json'
        if manifest_path.is_file():
            return
        manifest_path.write_text(json.dumps({'schema': 1}, indent=2, sort_keys=True))


class CSERuntime:
    """Custom-step runtime for CSE call boundaries.

    Handles only break-on-function states.

    Workflow:
        existing summary applies -> backend Step or Branch
        no applicable summary    -> generate callee proof
        existing summary exists  -> merge new guarded outcomes
        no existing summary      -> store generated summary
    """

    functions: frozenset[str]
    store: CSESummaryStore
    kmir: KMIR
    opts: ProveOpts
    proof_label: str
    main_cut_point_rules: tuple[str, ...]
    summary_cut_point_rules: tuple[str, ...]
    trace_function_tys: frozenset[int]
    _added_summary_modules: set[tuple[int, str]]
    _trace_output_keys: set[str]
    _active_summaries: set[str]

    def __init__(
        self,
        *,
        functions: Iterable[str],
        store: CSESummaryStore,
        kmir: KMIR,
        opts: ProveOpts,
        proof_label: str,
        smir_info: SMIRInfo | None = None,
        main_cut_point_rules: Iterable[str] = (),
        summary_cut_point_rules: Iterable[str] = (),
    ) -> None:
        """Configure CSE for selected functions, store, and proof-generation options."""
        self.functions = frozenset(functions)
        self.store = store
        self.kmir = kmir
        self.opts = opts
        self.proof_label = proof_label
        self.main_cut_point_rules = tuple(main_cut_point_rules)
        self.summary_cut_point_rules = tuple(summary_cut_point_rules)
        self.trace_function_tys = _trace_function_tys(self.functions, smir_info)
        self._added_summary_modules = set()
        self._trace_output_keys = set()
        self._active_summaries = set()

    @property
    def mode(self) -> str:
        """Return the configured CSE strategy."""
        return getattr(self.opts, 'cse_mode', 'summary')

    def can_make_custom_step(self, cterm: CTerm) -> bool:
        """Return whether this runtime wants to handle CTERM."""
        if self.mode == 'trace':
            key = _trace_key(cterm)
            return self._is_trace_target(cterm) or key in self._trace_output_keys or self.store.has_trace(key)
        return self.target_call_info(cterm) is not None

    def _is_trace_target(self, cterm: CTerm) -> bool:
        """Return whether trace mode should cache/replay this source state."""
        if self.target_call_info(cterm) is not None:
            return True
        current_ty = _current_function_ty(cterm)
        return current_ty is not None and current_ty in self.trace_function_tys

    def target_call_info(self, cterm: CTerm) -> CSECallInfo | None:
        """Extract supported target call metadata from a stopped call-boundary state."""
        k_item = _k_cell_head(cterm)
        if not isinstance(k_item, KApply):
            return None
        if not k_item.label.name.startswith('#execTerminatorCall'):
            return None

        function_idx = None
        for idx, arg in enumerate(k_item.args[:3]):
            if isinstance(arg, KToken) and arg.sort.name == 'String':
                function_idx = idx
                break
        if function_idx is None or len(k_item.args) <= function_idx + 5:
            return None

        function_token = k_item.args[function_idx]
        assert isinstance(function_token, KToken)
        function = function_token.token.strip('"')
        if function not in self.functions:
            return None

        args = tuple(_unwrap_injection(item) for item in _list_items(k_item.args[function_idx + 1]))
        return CSECallInfo(
            function=function,
            args=args,
            destination=k_item.args[function_idx + 4],
            target=k_item.args[function_idx + 5],
        )

    def custom_step(self, cterm: CTerm, cterm_symbolic: CTermSymbolic) -> KCFGExtendResult | None:
        """Apply an existing summary or generate one for the current CSE call boundary."""
        if self.mode == 'trace':
            return self._trace_step(cterm, cterm_symbolic)

        info = self.target_call_info(cterm)
        if info is None:
            return None

        summary = self.store.load(info.function)
        if summary is not None:
            applied = self._apply_summary(summary, cterm, info, cterm_symbolic)
            if applied is not None:
                return applied

        generated = self.generate_summary(cterm, info, cterm_symbolic)
        if generated is None:
            return self._fallback_call_step(cterm, info, cterm_symbolic)

        if summary is not None:
            # The store keeps one summary per function. If the current caller
            # exposes a missing case, merge that proof back into the existing
            # schema by moving caller-specific initial constraints into guards.
            generated = _update_summary(summary, generated, cterm_symbolic)
            if any(outcome.rule is None for outcome in generated.outcomes):
                generated = _compile_summary_rules(generated, cterm, info, cterm_symbolic)
        if not _has_applicable_rules(generated):
            _LOGGER.info('CSE summary for %s has no backend-applicable rules; falling back to normal step', info.function)
            return self._fallback_call_step(cterm, info, cterm_symbolic)
        self.store.save(generated)
        applied = self._apply_summary(generated, cterm, info, cterm_symbolic)
        if applied is not None:
            return applied
        return self._fallback_call_step(cterm, info, cterm_symbolic)

    def _trace_step(self, cterm: CTerm, cterm_symbolic: CTermSymbolic) -> KCFGExtendResult | None:
        """Replay or record the default proof extension without changing proof shape."""
        key = _trace_key(cterm)
        cached = self.store.load_trace(key)
        if cached is not None:
            _LOGGER.info('CSE trace cache hit: %s', key)
            self._remember_trace_outputs(cterm, cached)
            return cached

        if not self._is_trace_target(cterm) and key not in self._trace_output_keys:
            return None

        _LOGGER.info('CSE trace cache miss: %s', key)
        try:
            executed = cterm_symbolic.execute(
                cterm,
                depth=self.opts.max_depth,
                cut_point_rules=self.main_cut_point_rules,
            )
        except (ValueError, RuntimeError) as err:
            _LOGGER.info('CSE trace backend step failed: %s', err)
            return None

        result, pending = _trace_results_from_execute(executed)
        if result is None:
            return None

        self.store.save_trace(key, result)
        if pending is not None and executed.depth > 0:
            pending_key = _trace_key(executed.state)
            self.store.save_trace(pending_key, pending)
        self._remember_trace_outputs(cterm, result)
        if pending is not None:
            self._remember_trace_outputs(executed.state, pending)
        return result

    def _remember_trace_outputs(self, source: CTerm, *results: KCFGExtendResult | None) -> None:
        """Remember states produced by trace replay for scoped subsumption caching."""
        for result in results:
            if isinstance(result, Step):
                self._trace_output_keys.add(_trace_key(result.cterm))
            elif isinstance(result, Branch):
                self._trace_output_keys.update(_trace_key(source.add_constraint(constraint)) for constraint in result.constraints)
            elif isinstance(result, NDBranch):
                self._trace_output_keys.update(_trace_key(cterm) for cterm in result.cterms)

    def is_trace_output(self, cterm: CTerm) -> bool:
        """Return whether CTERM was produced by a trace step in this run."""
        return _trace_key(cterm) in self._trace_output_keys

    def _apply_summary(
        self,
        summary: CSESummary,
        cterm: CTerm,
        info: CSECallInfo,
        cterm_symbolic: CTermSymbolic,
    ) -> KCFGExtendResult | None:
        """Apply SUMMARY by asking the backend to use its stored rewrite rules.

        Stored outcomes already contain normalized K rules produced when the
        summary proof was generated. Apply only packages those rules into a
        temporary module and calls execute(depth=1, module_name=...); rule
        matching, guard selection, and split construction stay in the backend.
        """
        base_label = f'CSE.summary.{info.function}'
        rules = tuple(outcome.rule for outcome in summary.outcomes if outcome.rule is not None)
        if not rules:
            return None

        direct = _apply_summary_direct(rules, cterm, info.function)
        if direct is not None:
            return direct

        module_digest = hashlib.sha256(
            json.dumps([rule.to_dict() for rule in rules], sort_keys=True).encode()
        ).hexdigest()[:16]
        module_name = f'CSE-SUMMARY-{_safe_function_id(info.function).upper()}-{module_digest}'
        definition = getattr(cterm_symbolic, '_definition', None)
        imports = () if definition is None else (KImport(definition.main_module_name),)
        module = KFlatModule(module_name, rules, imports=imports)

        try:
            module_key = (id(cterm_symbolic), module_name)
            if module_key not in self._added_summary_modules:
                cterm_symbolic.add_module(module, name_as_id=True)
                self._added_summary_modules.add(module_key)
            executed = cterm_symbolic.execute(cterm, depth=1, module_name=module_name)
        except (ValueError, RuntimeError) as err:
            _LOGGER.info('CSE summary backend step failed for %s: %s', info.function, err)
            return None

        if executed.depth > 0:
            if not _is_summary_post_state(executed.state):
                return None
            return Step(
                executed.state,
                executed.depth,
                executed.logs,
                [base_label],
                cut=True,
                info=f'cse-summary:{info.function}',
            )

        if len(executed.next_states) == 1:
            if not _is_summary_post_state(executed.next_states[0].state):
                return None
            return Step(
                executed.next_states[0].state,
                1,
                executed.logs,
                [base_label],
                cut=True,
                info=f'cse-summary:{info.function}',
            )

        if len(executed.next_states) < 2 or not all(condition for _, condition in executed.next_states):
            return None
        if not all(_is_summary_post_state(next_state) for next_state, _ in executed.next_states):
            return None

        # Use the same Branch shape that KCFGExplore would have constructed
        # from backend rule predicates. This keeps CSE splits backend-derived
        # instead of rebuilding guard logic in Python.
        branch_preds = [flatten_label('#And', condition) for _, condition in executed.next_states if condition]
        common_preds: list[KInner] = []
        for pred in branch_preds[0]:
            if pred not in common_preds and all(pred in branch_pred for branch_pred in branch_preds):
                common_preds.append(pred)
        branches = [mlAnd(pred for pred in branch_pred if pred not in common_preds) for branch_pred in branch_preds]
        return Branch(tuple(branches), info=f'cse-summary-split:{info.function}')

    def _fallback_call_step(
        self,
        cterm: CTerm,
        info: CSECallInfo,
        cterm_symbolic: CTermSymbolic,
    ) -> KCFGExtendResult | None:
        """Execute one ordinary backend step when CSE cannot summarize/apply a call."""
        try:
            executed = cterm_symbolic.execute(cterm, depth=1)
        except (ValueError, RuntimeError) as err:
            _LOGGER.info('CSE fallback backend step failed for %s: %s', info.function, err)
            return None

        base_label = f'CSE.fallback.{info.function}'
        if executed.depth > 0:
            return Step(
                executed.state,
                executed.depth,
                executed.logs,
                [base_label],
                cut=True,
                info=f'cse-fallback:{info.function}',
            )

        if len(executed.next_states) == 1:
            return Step(
                executed.next_states[0].state,
                1,
                executed.logs,
                [base_label],
                cut=True,
                info=f'cse-fallback:{info.function}',
            )

        if len(executed.next_states) < 2 or not all(condition for _, condition in executed.next_states):
            return None

        branch_preds = [flatten_label('#And', condition) for _, condition in executed.next_states if condition]
        common_preds: list[KInner] = []
        for pred in branch_preds[0]:
            if pred not in common_preds and all(pred in branch_pred for branch_pred in branch_preds):
                common_preds.append(pred)
        branches = [mlAnd(pred for pred in branch_pred if pred not in common_preds) for branch_pred in branch_preds]
        return Branch(tuple(branches), info=f'cse-fallback-split:{info.function}')

    def generate_summary(
        self,
        call_boundary: CTerm,
        info: CSECallInfo,
        cterm_symbolic: CTermSymbolic,
    ) -> CSESummary | None:
        """Prove and extract a caller-derived callee summary for one call boundary."""
        if info.function in self._active_summaries:
            _LOGGER.info('CSE summary generation skipped recursive callee: %s', info.function)
            return None

        self._active_summaries.add(info.function)
        try:
            # Always enter the real callee from the current caller call boundary.
            # This keeps path assumptions and caller-owned reference structure in
            # the summary initial; later update logic generalizes reusable pieces
            # by moving caller-specific assumptions into guarded outcomes.
            try:
                callee_entry = cterm_symbolic.execute(call_boundary, depth=1).state
            except (ValueError, RuntimeError) as err:
                _LOGGER.info('CSE summary generation skipped: failed to enter callee %s: %s', info.function, err)
                return None

            # The entered callee still carries the caller return target. Clearing
            # it makes the summary proof stop at a callee terminal frontier, so
            # applying the summary can rebuild the caller continuation explicitly.
            callee_initial = CTerm.from_kast(
                set_cell(
                    callee_entry.kast,
                    'TARGET_CELL',
                    KApply('noBasicBlockIdx_BODY_MaybeBasicBlockIdx', ()),
                )
            )
            summary_proof = apr_proof_from_cterm(
                self.store.proof_id(info.function),
                callee_initial,
                proof_dir=self.store.proofs_dir,
            )

            with self.kmir.kcfg_explore(
                f'{self.proof_label}.{self.store.proof_id(info.function)}',
                terminate_on_thunk=self.opts.terminate_on_thunk,
                cse_runtime=self,
            ) as kcfg_explore:
                prover = APRProver(
                    kcfg_explore,
                    execute_depth=self.opts.max_depth,
                    cut_point_rules=self.summary_cut_point_rules,
                )
                prover.advance_proof(
                    summary_proof,
                    max_iterations=self.opts.max_iterations,
                    fail_fast=self.opts.fail_fast,
                    maintenance_rate=self.opts.maintenance_rate,
            )
            summary_proof.minimize_kcfg()
            summary_proof.write_proof_data()
            summary = summary_from_proof(info.function, summary_proof)
            if summary is None:
                return None
            return _compile_summary_rules(summary, call_boundary, info, cterm_symbolic)
        finally:
            self._active_summaries.remove(info.function)


class CSEAPRProver(APRProver):
    """APR prover that replays successful trace subsumptions when available."""

    cse_runtime: CSERuntime

    def __init__(self, cse_runtime: CSERuntime, *args, **kwargs) -> None:
        """Initialize with the active CSE runtime and APRProver arguments."""
        super().__init__(*args, **kwargs)
        self.cse_runtime = cse_runtime

    def _check_subsume(self, node: KCFG.Node, target_node: KCFG.Node, proof_id: str) -> CSubst | None:
        """Cache successful trace subsumptions to avoid repeating warm leaf implies."""
        if self.cse_runtime.mode != 'trace':
            return super()._check_subsume(node, target_node, proof_id)
        if not self.cse_runtime.is_trace_output(node.cterm):
            return super()._check_subsume(node, target_node, proof_id)

        target_cterm = target_node.cterm
        _LOGGER.debug(f'Checking subsumption into target state {proof_id}: {shorten_hashes((node.id, target_cterm))}')
        if self.fast_check_subsumption and not self._may_subsume(node, target_node):
            _LOGGER.info(f'Skipping full subsumption check because of fast may subsume check {proof_id}: {node.id}')
            return None

        key = _subsumption_key(node.cterm, target_cterm, assume_defined=self.assume_defined)
        cached = self.cse_runtime.store.load_subsumption(key)
        if cached is not None:
            _LOGGER.info('CSE trace subsumption cache hit: %s', key)
            _LOGGER.info(f'Subsumed into target node {proof_id}: {shorten_hashes((node.id, target_node.id))}')
            return cached

        _LOGGER.info('CSE trace subsumption cache miss: %s', key)
        result = self.kcfg_explore.cterm_symbolic.implies(
            node.cterm,
            target_cterm,
            assume_defined=self.assume_defined,
        )
        csubst = result.csubst
        if csubst is not None:
            _LOGGER.info(f'Subsumed into target node {proof_id}: {shorten_hashes((node.id, target_node.id))}')
            self.cse_runtime.store.save_subsumption(key, csubst)
        return csubst


class _UnsupportedReturnType:
    """Sentinel type for summary outcomes whose return shape CSE cannot apply."""

    pass


_UnsupportedReturn = _UnsupportedReturnType()


def apr_proof_from_cterm(
    id: str,
    lhs: CTerm,
    *,
    proof_dir: Path | None = None,
) -> APRProof:
    """Build an APR proof from an already materialized initial CTerm.

    This is intentionally independent from _prove.apr_proof_from_smir: CSE uses
    it for caller-derived callee entries, while normal proof construction owns
    the SMIR-to-initial-config path.
    """

    var_config, var_subst = split_config_from(lhs.config)
    rhs_subst: dict[str, KInner] = {
        v_name: abstract_term_safely(KVariable('_'), base_name=v_name) for v_name in var_subst
    }
    rhs_subst['K_CELL'] = KSequence([KApply('#EndProgram_KMIR-CONTROL-FLOW_KItem', ())])
    rhs = CTerm(Subst(rhs_subst)(var_config))
    kcfg = KCFG()
    init_node = kcfg.create_node(lhs)
    target_node = kcfg.create_node(rhs)
    return APRProof(id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)


def summary_from_proof(function: str, proof: APRProof) -> CSESummary | None:
    """Convert one callee proof into the persisted summary shape.

    proof init constraints + path constraints + final constraints -> guard
    proof init config                                            -> initial
    proof frontier config                                        -> final
    """
    initial = proof.kcfg.node(proof.init).cterm
    summary_initial = CTerm(initial.config, ())

    frontiers: list[tuple[KCFG.Node, str]] = []
    for node in proof.kcfg.nodes:
        if proof.is_target(node.id) or proof.is_refuted(node.id):
            continue

        # pyk treats cover edges as KCFG successors, but CSE covers are only an
        # APR proof relation to the target. Only ordinary execution successors
        # make a node non-frontier for summary extraction.
        if (
            proof.kcfg.general_edges(source_id=node.id)
            or proof.kcfg.splits(source_id=node.id)
            or proof.kcfg.ndbranches(source_id=node.id)
        ):
            continue

        if proof.kcfg.covers(source_id=node.id, target_id=proof.target):
            frontiers.append((node, 'covered'))
        elif proof.is_terminal(node.id):
            frontiers.append((node, 'terminal'))
        elif proof.kcfg.is_stuck(node.id):
            frontiers.append((node, 'stuck'))
        elif proof.kcfg.is_vacuous(node.id):
            frontiers.append((node, 'vacuous'))
        elif proof.is_bounded(node.id):
            frontiers.append((node, 'bounded'))
        elif proof.is_failing(node.id):
            frontiers.append((node, 'failing'))

    outcomes: list[CSEOutcome] = []
    for final_node, kind in frontiers:
        final_constraints = tuple(
            constraint for constraint in final_node.cterm.constraints if constraint not in initial.constraints
        )
        # Persisted summaries keep initial.constraints empty. Caller/path
        # assumptions from the proof initial and residual final constraints are
        # part of the outcome guard, which lets apply and merge reason about
        # coverage through one predicate per outcome.
        guard = _guard_with_constraints(
            proof.path_constraints(final_node.id),
            (*initial.constraints, *final_constraints),
        )
        rules: list[str] = []
        depth = 0
        for successor in proof.kcfg.shortest_path_between(proof.init, final_node.id) or ():
            if isinstance(successor, KCFG.Edge):
                rules.extend(successor.rules)
                depth += successor.depth
        outcomes.append(
            CSEOutcome(
                guard=guard,
                final=CTerm(final_node.cterm.config, ()),
                metadata={'node': final_node.id, 'rules': rules, 'depth': depth, 'kind': kind},
            )
        )

    if not outcomes:
        return None

    return CSESummary(
        function=function,
        initial=summary_initial,
        outcomes=tuple(outcomes),
        source={'proof_id': proof.id, 'proof_status': proof.status.value},
    )


def _compile_summary_rules(
    summary: CSESummary,
    call_boundary: CTerm,
    info: CSECallInfo,
    cterm_symbolic: CTermSymbolic,
) -> CSESummary:
    """Attach backend-ready call-boundary rewrite rules to SUMMARY outcomes.

    The proof extractor records semantic outcomes. This compiler turns each
    supported outcome into a K rule while the generating caller state is still
    available:

        call-boundary pattern + outcome guard => caller continuation

    Apply later uses these stored rules directly; it does not reconstruct
    guards, return writes, reference writebacks, or split conditions.
    """
    k_item = _k_cell_head(call_boundary)
    if not isinstance(k_item, KApply):
        return summary

    function_idx = None
    for idx, arg in enumerate(k_item.args[:3]):
        if isinstance(arg, KToken) and arg.sort.name == 'String':
            function_idx = idx
            break
    if function_idx is None or len(k_item.args) <= function_idx + 5:
        return summary

    target = info.target
    if not (
        isinstance(target, KApply)
        and target.label.name.startswith('someBasicBlockIdx')
        and len(target.args) == 1
    ):
        return summary

    arg_patterns = _summary_arg_patterns(summary.initial, len(info.args))
    if arg_patterns is None:
        return summary

    arg_subst: Subst | None = Subst({})
    for pattern, arg in zip(arg_patterns, info.args, strict=True):
        arg_subst = _match_summary_value(summary.initial, call_boundary, cterm_symbolic, pattern, arg, arg_subst)
        if arg_subst is None:
            return summary

    if _contains_ref_or_pointer((*info.args, *arg_patterns)):
        rule_config = call_boundary.config
    else:
        rule_config, _config_subst = split_config_from(call_boundary.config)
    destination = KVariable('CSE_DEST', 'Place')
    target_block = KVariable('CSE_TARGET', 'BasicBlockIdx')
    target_pattern = KApply(target.label, (target_block,))

    call_args = list(k_item.args)
    call_args[function_idx + 1] = _list_from_items(info.args)
    call_args[function_idx + 2] = KVariable('CSE_BODY', 'Body')
    call_args[function_idx + 3] = KVariable('CSE_FUNCTION_TY', 'Ty')
    call_args[function_idx + 4] = destination
    call_args[function_idx + 5] = target_pattern
    if len(call_args) > function_idx + 6:
        call_args[function_idx + 6] = KVariable('CSE_UNWIND', 'UnwindAction')
    if len(call_args) > function_idx + 7:
        call_args[function_idx + 7] = KVariable('CSE_SPAN', 'Span')
    call_pattern = KApply(k_item.label, tuple(call_args))
    lhs_config = set_cell(rule_config, 'K_CELL', KSequence([call_pattern]))

    deref_cache: dict[tuple[str, KInner], KInner | None] = {}
    compiled: list[CSEOutcome] = []
    for idx, outcome in enumerate(summary.outcomes):
        rule = _compile_summary_outcome_rule(
            summary,
            call_boundary,
            info,
            outcome,
            idx,
            lhs_config,
            rule_config,
            destination,
            target_block,
            arg_subst,
            cterm_symbolic,
            deref_cache,
        )
        compiled.append(
            CSEOutcome(
                guard=outcome.guard,
                final=outcome.final,
                metadata=outcome.metadata,
                rule=rule,
            )
        )

    return CSESummary(
        function=summary.function,
        initial=summary.initial,
        outcomes=tuple(compiled),
        source=summary.source,
    )


def _has_applicable_rules(summary: CSESummary) -> bool:
    """Return true if at least one outcome has a reusable backend rule."""
    return any(outcome.rule is not None for outcome in summary.outcomes)


def _trace_key(cterm: CTerm) -> str:
    """Return a stable key for exact replay of a proof extension source state."""
    return hashlib.sha256(json.dumps(cterm.to_dict(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _subsumption_key(source: CTerm, target: CTerm, *, assume_defined: bool) -> str:
    """Return a stable key for one successful source => target subsumption."""
    data = {
        'schema': 1,
        'source': source.to_dict(),
        'target': target.to_dict(),
        'assume_defined': assume_defined,
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _trace_function_tys(functions: Iterable[str], smir_info: SMIRInfo | None) -> frozenset[int]:
    """Map selected CSE function names to SMIR function type IDs for trace scope."""
    if smir_info is None:
        return frozenset()
    return frozenset(
        int(ty)
        for function in functions
        if (ty := smir_info.function_tys.get(function)) is not None
    )


def _current_function_ty(cterm: CTerm) -> int | None:
    """Return the current function Ty ID from <currentFunc>, when concrete."""
    current_func = cterm.try_cell('CURRENTFUNC_CELL')
    if not (
        isinstance(current_func, KApply)
        and current_func.label.name == 'ty'
        and len(current_func.args) == 1
    ):
        return None

    ty = current_func.args[0]
    if not (isinstance(ty, KToken) and ty.sort.name == 'Int'):
        return None
    return int(ty.token)


def _trace_results_from_execute(executed) -> tuple[KCFGExtendResult | None, KCFGExtendResult | None]:
    """Mirror KCFGExplore's default execute-to-extension conversion.

    KCFGExplore can return two results for one backend execute: a Step to the
    branch/cut source plus a cached Branch/cut result at that source. Custom
    semantics can return only one result, so trace mode persists the second
    result under the intermediate state's key and replays it on the next proof
    iteration.
    """
    next_result = _trace_next_result(executed)
    if executed.depth > 0:
        return (
            Step(executed.state, executed.depth, (), [], info='cse-trace'),
            next_result,
        )
    return next_result, None


def _trace_next_result(executed) -> KCFGExtendResult | None:
    """Return the extension implied by execute.next_states, if any."""
    next_states = tuple(executed.next_states)
    if not next_states:
        if getattr(executed, 'vacuous', False):
            return Vacuous()
        if executed.depth == 0:
            return Stuck()
        return None

    if len(next_states) == 1:
        return Step(next_states[0].state, 1, (), [], cut=True, info='cse-trace-cut')

    if all(condition for _, condition in next_states):
        branch_preds = [flatten_label('#And', condition) for _, condition in next_states if condition]
        common_preds: list[KInner] = []
        for pred in branch_preds[0]:
            if pred not in common_preds and all(pred in branch_pred for branch_pred in branch_preds):
                common_preds.append(pred)
        branches = [mlAnd(pred for pred in branch_pred if pred not in common_preds) for branch_pred in branch_preds]
        return Branch(tuple(branches), info='cse-trace-branch')

    return NDBranch(tuple(next_state for next_state, _ in next_states), (), [])


def _trace_result_to_dict(result: KCFGExtendResult) -> dict[str, object]:
    """Serialize a trace replay result."""
    if isinstance(result, Step):
        return {
            'type': 'step',
            'cterm': result.cterm.to_dict(),
            'depth': result.depth,
            'cut': result.cut,
            'info': result.info,
        }
    if isinstance(result, Branch):
        return {
            'type': 'branch',
            'constraints': [constraint.to_dict() for constraint in result.constraints],
            'heuristic': result.heuristic,
            'info': result.info,
        }
    if isinstance(result, NDBranch):
        return {
            'type': 'ndbranch',
            'cterms': [cterm.to_dict() for cterm in result.cterms],
        }
    if isinstance(result, Stuck):
        return {'type': 'stuck'}
    if isinstance(result, Vacuous):
        return {'type': 'vacuous'}
    raise TypeError(f'Unsupported CSE trace result: {type(result).__name__}')


def _trace_result_from_dict(dct: dict[str, object]) -> KCFGExtendResult:
    """Deserialize a trace replay result."""
    result_type = dct.get('type')
    if result_type == 'step':
        return Step(
            CTerm.from_dict(_expect_dict(dct['cterm'])),
            int(dct['depth']),
            (),
            [],
            cut=bool(dct.get('cut', False)),
            info=str(dct.get('info', 'cse-trace')),
        )
    if result_type == 'branch':
        constraints = tuple(KInner.from_dict(_expect_dict(item)) for item in _expect_list(dct['constraints']))
        return Branch(constraints, heuristic=bool(dct.get('heuristic', False)), info=str(dct.get('info', 'cse-trace-branch')))
    if result_type == 'ndbranch':
        return NDBranch(tuple(CTerm.from_dict(_expect_dict(item)) for item in _expect_list(dct['cterms'])), (), [])
    if result_type == 'stuck':
        return Stuck()
    if result_type == 'vacuous':
        return Vacuous()
    raise ValueError(f'Unsupported CSE trace result type: {result_type}')


def _compile_summary_outcome_rule(
    summary: CSESummary,
    call_boundary: CTerm,
    info: CSECallInfo,
    outcome: CSEOutcome,
    idx: int,
    lhs_config: KInner,
    rule_config: KInner,
    destination: KInner,
    target_block: KInner,
    arg_subst: Subst,
    cterm_symbolic: CTermSymbolic,
    deref_cache: dict[tuple[str, KInner], KInner | None],
) -> KRule | None:
    """Compile one normal-return outcome into a reusable backend rule."""
    ret_val = outcome.final.try_cell('RETVAL_CELL')
    returned: KInner | None | _UnsupportedReturnType = _UnsupportedReturn
    if isinstance(ret_val, KApply):
        if ret_val.label.name.startswith('return') and len(ret_val.args) == 1:
            returned = ret_val.args[0]
        elif ret_val.label.name.startswith('noReturn'):
            returned = None
    if returned is _UnsupportedReturn:
        return None

    writebacks = _reference_writebacks(
        call_boundary,
        info.args,
        summary.initial,
        outcome,
        arg_subst,
        cterm_symbolic,
        deref_cache,
        final_context=f'final:{idx}',
    )
    if writebacks is None:
        return None
    writeback_items = tuple(KApply(_CSE_WRITE_BACK, (ref_value, new_value)) for ref_value, new_value in writebacks)

    if returned is None:
        k_items = [*writeback_items, KApply(_EXEC_BLOCK_IDX, (target_block,))]
    else:
        k_items = [
            *writeback_items,
            KApply(
                _SET_LOCAL_VALUE,
                (
                    destination,
                    KApply(_DECREMENT_REF, (arg_subst(returned),)),
                ),
            ),
            KApply(_EXEC_BLOCK_IDX, (target_block,)),
        ]

    post_config = set_cell(rule_config, 'K_CELL', KSequence(k_items))
    guard = arg_subst(outcome.guard)
    init_constraints = () if is_top(guard, weak=True) else (guard,)
    rule_digest = hashlib.sha256(
        json.dumps(
            {
                'lhs': lhs_config.to_dict(),
                'requires': [constraint.to_dict() for constraint in init_constraints],
                'rhs': post_config.to_dict(),
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()[:12]
    rule, _subst = cterm_build_rule(
        f'CSE.summary.{_safe_function_id(info.function)}.{idx}.{rule_digest}',
        CTerm(lhs_config, init_constraints),
        CTerm(post_config),
        priority=20,
    )
    return rule


def _reference_writebacks(
    caller: CTerm,
    args: tuple[KInner, ...],
    initial: CTerm,
    outcome: CSEOutcome,
    subst: Subst,
    cterm_symbolic: CTermSymbolic,
    deref_cache: dict[tuple[str, KInner], KInner | None],
    *,
    final_context: str,
) -> tuple[tuple[KInner, KInner], ...] | None:
    """Compute caller-side reference/PTR writebacks required by OUTCOME."""
    arg_patterns = _summary_arg_patterns(initial, len(args))
    if arg_patterns is None:
        return None

    writebacks: list[tuple[KInner, KInner]] = []
    for pattern, arg in zip(arg_patterns, args, strict=True):
        if _is_ref_or_pointer(pattern):
            if not _ref_chain_supported(initial, pattern, cterm_symbolic, deref_cache, context='initial'):
                _LOGGER.info('CSE reference outcome rejected: unsupported reference chain')
                return None

            before = pattern
            after = pattern
            caller_value = arg
        elif _contains_ref_or_pointer((pattern,)):
            before = after = pattern
            caller_value = arg
        else:
            continue

        nested = _nested_reference_writebacks(
            initial,
            outcome.final,
            caller,
            before,
            after,
            caller_value,
            subst,
            cterm_symbolic,
            deref_cache,
            final_context=final_context,
            depth=0,
        )
        if nested is None:
            return None
        writebacks.extend(nested)

    return tuple(writebacks)


def _nested_reference_writebacks(
    initial: CTerm,
    final: CTerm,
    caller: CTerm,
    before: KInner,
    after: KInner,
    caller_value: KInner,
    subst: Subst,
    cterm_symbolic: CTermSymbolic,
    deref_cache: dict[tuple[str, KInner], KInner | None],
    *,
    final_context: str,
    depth: int,
) -> tuple[tuple[KInner, KInner], ...] | None:
    """Recursively compare before/after/caller values and emit nested writebacks."""
    if depth > _REFERENCE_WRITEBACK_MAX_DEPTH:
        _LOGGER.info('CSE reference outcome rejected: writeback depth exceeded %s', _REFERENCE_WRITEBACK_MAX_DEPTH)
        return None

    if not _contains_ref_or_pointer((before, after, caller_value)):
        return ()

    if _is_ref_or_pointer(before):
        if not _is_ref_or_pointer(caller_value):
            return None
        # Walk references/PTRs one layer at a time. A single #cseWriteBack
        # also dereferences once, so collapsing &mut &mut T to T here would
        # write the leaf value into the outer reference slot.
        before_pointee = _deref_cached(initial, before, cterm_symbolic, deref_cache, context='initial')
        after_pointee = _deref_cached(final, before, cterm_symbolic, deref_cache, context=final_context)
        caller_pointee = _deref_cached(caller, caller_value, cterm_symbolic, deref_cache, context='caller')
        if before_pointee is None or after_pointee is None or caller_pointee is None:
            return None

        writebacks: list[tuple[KInner, KInner]] = []
        nested = _nested_reference_writebacks(
            initial,
            final,
            caller,
            before_pointee,
            after_pointee,
            caller_pointee,
            subst,
            cterm_symbolic,
            deref_cache,
            final_context=final_context,
            depth=depth + 1,
        )
        if nested is None:
            return None
        writebacks.extend(nested)

        before_value = subst(before_pointee)
        if before_value != subst(after_pointee):
            after_value = _restore_caller_refs(before_pointee, subst(after_pointee), caller_pointee)
            if after_value is None:
                return None
            writebacks.append((caller_value, after_value))
        return tuple(writebacks)

    if isinstance(before, KApply):
        if not (isinstance(after, KApply) and isinstance(caller_value, KApply)):
            return ()
        if before.label.name != after.label.name or before.label.name != caller_value.label.name:
            return ()
        if len(before.args) != len(after.args) or len(before.args) != len(caller_value.args):
            return None

        writebacks: list[tuple[KInner, KInner]] = []
        for before_arg, after_arg, caller_arg in zip(before.args, after.args, caller_value.args, strict=True):
            nested = _nested_reference_writebacks(
                initial,
                final,
                caller,
                before_arg,
                after_arg,
                caller_arg,
                subst,
                cterm_symbolic,
                deref_cache,
                final_context=final_context,
                depth=depth + 1,
            )
            if nested is None:
                return None
            writebacks.extend(nested)
        return tuple(writebacks)

    if isinstance(before, KSequence):
        if not (isinstance(after, KSequence) and isinstance(caller_value, KSequence)):
            return ()
        if len(before.items) != len(after.items) or len(before.items) != len(caller_value.items):
            return None

        writebacks: list[tuple[KInner, KInner]] = []
        for before_item, after_item, caller_item in zip(before.items, after.items, caller_value.items, strict=True):
            nested = _nested_reference_writebacks(
                initial,
                final,
                caller,
                before_item,
                after_item,
                caller_item,
                subst,
                cterm_symbolic,
                deref_cache,
                final_context=final_context,
                depth=depth + 1,
            )
            if nested is None:
                return None
            writebacks.extend(nested)
        return tuple(writebacks)

    return ()


def _restore_caller_refs(before: KInner, after: KInner, caller: KInner) -> KInner | None:
    """Translate summary-side AFTER back to caller-side reference identities."""
    if not _contains_ref_or_pointer((before, after, caller)):
        return after

    if _is_ref_or_pointer(before):
        if not (_is_ref_or_pointer(after) and _is_ref_or_pointer(caller)):
            return None
        if before != after:
            # Rewriting a stored reference to a different reference needs an
            # explicit summary-to-caller identity map. Until CSE stores that,
            # only preserve unchanged reference leaves.
            return None
        return KApply(_INCREMENT_REF, (caller,))

    if isinstance(before, KApply) and isinstance(after, KApply) and isinstance(caller, KApply):
        if before.label.name != after.label.name or before.label.name != caller.label.name:
            return None if _contains_ref_or_pointer((before, after)) else after
        if len(before.args) != len(after.args) or len(before.args) != len(caller.args):
            return None if _contains_ref_or_pointer((before, after)) else after

        args: list[KInner] = []
        for before_arg, after_arg, caller_arg in zip(before.args, after.args, caller.args, strict=True):
            restored = _restore_caller_refs(before_arg, after_arg, caller_arg)
            if restored is None:
                return None
            args.append(restored)
        return KApply(after.label, tuple(args))

    if isinstance(before, KSequence) and isinstance(after, KSequence) and isinstance(caller, KSequence):
        if len(before.items) != len(after.items) or len(before.items) != len(caller.items):
            return None if _contains_ref_or_pointer((before, after)) else after

        items: list[KInner] = []
        for before_item, after_item, caller_item in zip(before.items, after.items, caller.items, strict=True):
            restored = _restore_caller_refs(before_item, after_item, caller_item)
            if restored is None:
                return None
            items.append(restored)
        return KSequence(tuple(items))

    if _contains_ref_or_pointer((before, after)):
        return None
    return after


def _match_summary_value(
    summary_initial: CTerm,
    caller: CTerm,
    cterm_symbolic: CTermSymbolic,
    pattern: KInner,
    arg: KInner,
    subst: Subst,
) -> Subst | None:
    """Match one summary argument pattern against one caller argument value."""
    pattern = subst(pattern)
    if _is_ref_or_pointer(pattern) or _is_ref_or_pointer(arg):
        if not (_is_ref_or_pointer(pattern) and _is_ref_or_pointer(arg)):
            return None
        assert isinstance(pattern, KApply)
        assert isinstance(arg, KApply)
        if pattern.label.name != arg.label.name or len(pattern.args) < 4 or len(arg.args) < 4:
            return None

        for pattern_attr, arg_attr in ((pattern.args[2], arg.args[2]), (pattern.args[3], arg.args[3])):
            next_subst = subst(pattern_attr).match(arg_attr)
            if next_subst is None:
                return None
            merged = subst.union(next_subst)
            if merged is None:
                return None
            subst = merged

        # Reference identities are caller-specific, so matching only the raw
        # local id would make summaries non-reusable. Compare the values
        # obtained by dereferencing both sides through #traverseProjection.
        pattern_pointee = _deref_value(summary_initial, pattern, cterm_symbolic)
        arg_pointee = _deref_value(caller, arg, cterm_symbolic)
        if pattern_pointee is None or arg_pointee is None:
            return None

        return _match_summary_value(
            summary_initial,
            caller,
            cterm_symbolic,
            pattern_pointee,
            arg_pointee,
            subst,
        )

    if isinstance(pattern, KApply) and isinstance(arg, KApply):
        if pattern.label.name != arg.label.name or len(pattern.args) != len(arg.args):
            return None

        # Aggregates can contain references to other caller structures. Recurse
        # through the value shape so those nested references are matched by
        # their pointees instead of by callee/caller stack height.
        for pattern_arg, arg_arg in zip(pattern.args, arg.args, strict=True):
            subst = _match_summary_value(
                summary_initial,
                caller,
                cterm_symbolic,
                pattern_arg,
                arg_arg,
                subst,
            )
            if subst is None:
                return None
        return subst

    if isinstance(pattern, KSequence) and isinstance(arg, KSequence):
        if len(pattern.items) != len(arg.items):
            return None
        for pattern_item, arg_item in zip(pattern.items, arg.items, strict=True):
            subst = _match_summary_value(
                summary_initial,
                caller,
                cterm_symbolic,
                pattern_item,
                arg_item,
                subst,
            )
            if subst is None:
                return None
        return subst

    next_subst = pattern.match(arg)
    if next_subst is None:
        return None
    return subst.union(next_subst)


def _summary_arg_patterns(initial: CTerm, arg_count: int) -> tuple[KInner, ...] | None:
    """Read callee argument value patterns from summary initial locals 1..ARG_COUNT."""
    locals_ = _local_items(initial)
    if len(locals_) < arg_count + 1:
        return None

    patterns: list[KInner] = []
    for local in locals_[1 : arg_count + 1]:
        if not isinstance(local, KApply) or not local.label.name.startswith('typedValue') or len(local.args) < 1:
            return None
        patterns.append(local.args[0])
    return tuple(patterns)


def _update_summary(existing: CSESummary, new: CSESummary, cterm_symbolic: CTermSymbolic) -> CSESummary:
    """Merge NEW outcomes into EXISTING's single initial schema.

    same schema                 -> append/merge guarded outcomes
    alignable value-only schema -> rewrite NEW to EXISTING, then merge
    incompatible ref/PTR schema -> replace with NEW so this call can progress
    other schema                -> keep EXISTING
    """
    # Align the new proof to the existing summary's argument schema. Value-only
    # summaries can usually be generalized by substitution. Reference/PTR
    # summaries keep caller-owned local/stack structure in the rule lhs so the
    # backend can dereference pointees; if that structure is incompatible, the
    # current generated summary is the only version that can advance this
    # break-on-function node.
    if new.initial.config == existing.initial.config:
        aligned = new
    elif _contains_ref_or_pointer((*_local_items(new.initial), *_local_items(existing.initial))):
        outcomes = _deduplicate_outcomes(
            tuple(outcome for outcome in (*existing.outcomes, *new.outcomes) if outcome.rule is not None)
        )
        if not outcomes:
            outcomes = new.outcomes
        return CSESummary(
            function=existing.function,
            # Reference/PTR summaries are compiled against the caller-side
            # schema needed to dereference and write back through borrowed
            # values. Preserve every compiled variant instead of rewriting
            # older rules onto the current call boundary.
            initial=existing.initial,
            outcomes=outcomes,
            source={
                **existing.source,
                **new.source,
                'updated_summary': True,
                'merged_reference_variants': True,
                'previous_outcome_count': len(existing.outcomes),
                'new_outcome_count': len(new.outcomes),
                'merged_outcome_count': len(outcomes),
            },
        )
    else:
        source_values: list[KInner] = []
        for local in _local_items(new.initial)[1:]:
            if isinstance(local, KApply) and local.label.name.startswith('typedValue') and local.args:
                source_values.append(local.args[0])
        target_values: list[KInner] = []
        for local in _local_items(existing.initial)[1:]:
            if isinstance(local, KApply) and local.label.name.startswith('typedValue') and local.args:
                target_values.append(local.args[0])
        if len(source_values) != len(target_values):
            return existing

        subst: Subst | None = Subst({})
        for source_value, target_value in zip(source_values, target_values, strict=True):
            subst = _match_summary_value(
                new.initial,
                existing.initial,
                cterm_symbolic,
                source_value,
                target_value,
                subst,
            )
            if subst is None:
                return existing
        if subst is None:
            return existing

        aligned = CSESummary(
            function=new.function,
            initial=CTerm(
                existing.initial.config,
                (),
            ),
            outcomes=tuple(
                CSEOutcome(
                    guard=_guard_with_constraints(
                        subst(outcome.guard),
                        tuple(
                            subst(constraint)
                            for constraint in (*new.initial.constraints, *outcome.final.constraints)
                        ),
                    ),
                    final=CTerm(
                        subst(outcome.final.config),
                        (),
                    ),
                    metadata=outcome.metadata,
                    # The outcome has been rewritten onto EXISTING's schema.
                    # The compiled rule is tied to NEW's call-boundary shape,
                    # so custom_step recompiles merged summaries before saving.
                    rule=None,
                )
                for outcome in new.outcomes
            ),
            source=new.source,
        )

    base_initial = CTerm(existing.initial.config, ())
    no_reference_effects = not _contains_ref_or_pointer(_local_items(base_initial))
    outcomes: list[CSEOutcome] = []
    for source in (existing, aligned):
        for outcome in source.outcomes:
            # Normalize legacy or in-memory summaries that still carry
            # constraints outside guards. New summaries already satisfy this.
            guard = _guard_with_constraints(
                outcome.guard,
                (*source.initial.constraints, *outcome.final.constraints),
            )
            guard = _normalize_complement_guard(
                guard,
                tuple(item.guard for item in outcomes),
                base_initial,
                cterm_symbolic,
            )
            rule = outcome.rule.let(requires=ml_pred_to_bool(guard)) if outcome.rule is not None else None
            merged = CSEOutcome(
                guard=guard,
                final=CTerm(outcome.final.config, ()),
                metadata=outcome.metadata,
                rule=rule,
            )
            for idx, previous in enumerate(outcomes):
                # With no reference/PTR arguments, the caller-visible callee
                # effect is the return cell. Internal callee stack differences
                # should not keep two overlapping outcomes alive.
                same_effect = previous.final == merged.final or (
                    no_reference_effects
                    and previous.final.try_cell('RETVAL_CELL') == merged.final.try_cell('RETVAL_CELL')
                )
                if not same_effect:
                    continue
                if is_top(previous.guard, weak=True):
                    if previous.rule is None and merged.rule is not None:
                        outcomes[idx] = merged
                    break
                if is_top(merged.guard, weak=True):
                    outcomes[idx] = merged
                    break
                if previous.guard == merged.guard:
                    if previous.rule is None and merged.rule is not None:
                        outcomes[idx] = merged
                    break
                if _is_entailed(base_initial.add_constraint(previous.guard), merged.guard, cterm_symbolic):
                    outcomes[idx] = merged
                    break
                if _is_entailed(base_initial.add_constraint(merged.guard), previous.guard, cterm_symbolic):
                    break
                continue
            else:
                outcomes.append(merged)

    return CSESummary(
        function=existing.function,
        initial=base_initial,
        outcomes=tuple(outcomes),
        source={
            **existing.source,
            'updated_summary': True,
            'previous_outcome_count': len(existing.outcomes),
            'new_outcome_count': len(new.outcomes),
        },
    )


def _deduplicate_outcomes(outcomes: tuple[CSEOutcome, ...]) -> tuple[CSEOutcome, ...]:
    """Keep compiled summary outcomes in insertion order, dropping duplicate rules."""
    result: list[CSEOutcome] = []
    seen: set[str] = set()
    for outcome in outcomes:
        if outcome.rule is None:
            key_data = {
                'guard': outcome.guard.to_dict(),
                'final': outcome.final.to_dict(),
                'metadata': outcome.metadata,
            }
        else:
            key_data = {'rule': outcome.rule.to_dict()}
        key = hashlib.sha256(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        result.append(outcome)
    return tuple(result)


def _normalize_complement_guard(
    guard: KInner,
    previous_guards: tuple[KInner, ...],
    base_initial: CTerm,
    cterm_symbolic: CTermSymbolic,
) -> KInner:
    """Prefer common constraints plus not(previous branch) for complementary guards."""
    guard_bools = tuple(flatten_label('_andBool_', ml_pred_to_bool(guard)))
    for previous in previous_guards:
        previous_bools = tuple(flatten_label('_andBool_', ml_pred_to_bool(previous)))
        common_bools = tuple(item for item in guard_bools if item in previous_bools)
        common_preds = tuple(bool_to_ml_pred(item) for item in common_bools)
        for previous_bool in previous_bools:
            candidate = _guard_with_constraints(mlEqualsFalse(previous_bool), common_preds)
            if _is_entailed(base_initial.add_constraint(guard), candidate, cterm_symbolic) and _is_entailed(
                base_initial.add_constraint(candidate),
                guard,
                cterm_symbolic,
            ):
                return candidate
    return guard


def _guard_with_constraints(guard: KInner, constraints: tuple[KInner, ...]) -> KInner:
    """Conjoin GUARD with non-top constraints as one ML predicate."""
    guards = [constraint for constraint in constraints if not is_top(constraint, weak=True)]
    if not is_top(guard, weak=True):
        guards.append(guard)
    if not guards:
        return guard
    return bool_to_ml_pred(andBool(ml_pred_to_bool(item) for item in guards))

def _is_entailed(cterm: CTerm, constraint: KInner, cterm_symbolic: CTermSymbolic) -> bool:
    """Return whether CTERM entails CONSTRAINT, conservatively false on solver failure."""
    if is_top(constraint, weak=True):
        return True
    return _is_unsat(cterm.add_constraint(bool_to_ml_pred(notBool(ml_pred_to_bool(constraint)))), cterm_symbolic)


def _is_unsat(cterm: CTerm, cterm_symbolic: CTermSymbolic) -> bool:
    """Return whether CTERM implies bottom according to the symbolic backend."""
    try:
        return cterm_symbolic.implies(cterm, CTerm.bottom()).csubst is not None
    except (ValueError, RuntimeError) as err:
        _LOGGER.debug('CSE satisfiability check is inconclusive: %s', err)
        return False


def _apply_summary_direct(
    rules: tuple[KRule, ...],
    cterm: CTerm,
    function: str,
) -> KCFGExtendResult | None:
    """Apply compiled summary rules without a backend module when matching is syntactic.

    The compiled K rules remain the source of truth: this fast path only
    extracts their lhs/rhs and side condition. If more than one rule can apply
    on an unconstrained call boundary, return a Branch over the rule guards so
    the following per-branch custom step can instantiate exactly one rule.
    """
    matches: list[tuple[KInner, CTerm]] = []
    source_config = _normalize_k_list_units(cterm.config)
    for rule in rules:
        subst = _normalize_k_list_units(extract_lhs(rule.body)).match(source_config)
        if subst is None:
            continue

        condition = subst(rule.requires)
        if condition == FALSE:
            continue

        next_cterm = CTerm(
            _normalize_k_list_units(subst(extract_rhs(rule.body))),
            _constraints_with_condition(cterm.constraints, condition),
        )
        if not _is_summary_post_state(next_cterm):
            return None
        matches.append((condition, next_cterm))

    if not matches:
        return None

    selected = [match for match in matches if _condition_is_known(match[0], cterm.constraints)]
    if len(selected) == 1:
        return Step(
            selected[0][1],
            1,
            (),
            [f'CSE.summary.{function}'],
            cut=True,
            info=f'cse-summary:{function}',
        )
    if len(selected) > 1:
        return None

    if len(matches) == 1:
        return Step(
            matches[0][1],
            1,
            (),
            [f'CSE.summary.{function}'],
            cut=True,
            info=f'cse-summary:{function}',
        )

    branch_conditions = tuple(
        _condition_without_known_constraints(condition, cterm.constraints) for condition, _ in matches
    )
    if len(branch_conditions) < 2 or any(is_top(condition, weak=True) for condition in branch_conditions):
        return None
    return Branch(branch_conditions, info=f'cse-summary-split:{function}')


def _constraints_with_condition(constraints: tuple[KInner, ...], condition: KInner) -> tuple[KInner, ...]:
    if condition == TRUE or _condition_is_known(condition, constraints):
        return constraints
    return (*constraints, _condition_to_ml_pred(condition))


def _condition_is_known(condition: KInner, constraints: tuple[KInner, ...]) -> bool:
    if condition == TRUE:
        return True
    condition_conjuncts = _condition_ml_conjuncts(condition)
    known_conjuncts = _known_ml_conjuncts(constraints)
    return all(conjunct in known_conjuncts for conjunct in condition_conjuncts)


def _condition_without_known_constraints(condition: KInner, constraints: tuple[KInner, ...]) -> KInner:
    known_conjuncts = _known_ml_conjuncts(constraints)
    return mlAnd(conjunct for conjunct in _condition_ml_conjuncts(condition) if conjunct not in known_conjuncts)


def _condition_to_ml_pred(condition: KInner) -> KInner:
    return mlAnd(_condition_ml_conjuncts(condition))


def _condition_ml_conjuncts(condition: KInner) -> tuple[KInner, ...]:
    return tuple(bool_to_ml_pred(conjunct) for conjunct in _bool_conjuncts(condition))


def _known_ml_conjuncts(constraints: tuple[KInner, ...]) -> set[KInner]:
    return {
        conjunct
        for constraint in constraints
        for conjunct in flatten_label('#And', constraint)
        if not is_top(conjunct, weak=True)
    }


def _bool_conjuncts(condition: KInner) -> tuple[KInner, ...]:
    if condition == TRUE:
        return ()
    return tuple(flatten_label('_andBool_', condition))


def _normalize_k_list_units(term: KInner) -> KInner:
    """Normalize builtin K list units so Python-side matching mirrors backend matching."""

    def _normalize(_term: KInner) -> KInner:
        if not isinstance(_term, KApply) or _term.label.name != '_List_':
            return _term
        items = tuple(item for item in flatten_label('_List_', _term) if not _is_k_list_unit(item))
        if not items:
            return KApply('.List')

        result = items[-1]
        for item in reversed(items[:-1]):
            result = KApply('_List_', (item, result))
        return result

    return bottom_up(_normalize, term)


def _is_k_list_unit(term: KInner) -> bool:
    return isinstance(term, KApply) and term.label.name == '.List' and not term.args


def _is_summary_post_state(cterm: CTerm) -> bool:
    """Return whether CTERM begins with a CSE summary continuation item."""
    head = _k_cell_head(cterm)
    return (
        isinstance(head, KApply)
        and head.label.name in {_CSE_WRITE_BACK, _SET_LOCAL_VALUE, _EXEC_BLOCK_IDX}
    )


def _deref_value(cterm: CTerm, value: KInner, cterm_symbolic: CTermSymbolic) -> KInner | None:
    """Dereference a reference/PTR value using semantics first, then simple local fallback."""
    locals_cell = cterm.try_cell('LOCALS_CELL')
    stack_cell = cterm.try_cell('STACK_CELL')
    if locals_cell is not None and stack_cell is not None:
        # The main path asks KMIR itself to evaluate one #traverseProjection
        # deref. This keeps reference/PTR handling aligned with runtime rules.
        k_cell = KSequence(
            [
                KApply(
                    _TRAVERSE_PROJECTION,
                    (
                        KApply(_TO_LOCAL, (KToken('-1', 'Int'),)),
                        value,
                        KApply(
                            _PROJECTION_ELEMS_APPEND,
                            (
                                KApply(_PROJECTION_DEREF, ()),
                                KApply(_PROJECTION_ELEMS_EMPTY, ()),
                            ),
                        ),
                        KApply(_CONTEXTS_EMPTY, ()),
                        KApply(_FRAME_LOCALS, (locals_cell, stack_cell)),
                        list_empty(),
                    ),
                ),
                KApply(_READ_PROJECTION, (FALSE,)),
            ]
        )
        try:
            executed = cterm_symbolic.execute(
                CTerm.from_kast(set_cell(cterm.kast, 'K_CELL', k_cell)),
                depth=_DEREF_EVALUATION_DEPTH,
            )
            head = _k_cell_head(executed.state)
            if head != k_cell.items[0] and not _contains_label_fragment(head, ('projectionError',)):
                return head
        except (ValueError, RuntimeError) as err:
            _LOGGER.debug('CSE reference dereference via #traverseProjection failed: %s', err)

    # Fallback for simple local references when symbolic evaluation cannot make
    # progress. The semantic path above remains the primary implementation.
    if not _is_ref_or_pointer(value):
        return None
    assert isinstance(value, KApply)
    if len(value.args) < 2:
        return None

    offset, place = value.args[0], value.args[1]
    if not (isinstance(offset, KToken) and offset.token == '0'):
        return None
    if not isinstance(place, KApply) or place.label.name != 'place' or len(place.args) != 2:
        return None
    if place.args[1] != KApply(_PROJECTION_ELEMS_EMPTY, ()):
        return None
    local = place.args[0]
    if not isinstance(local, KApply) or local.label.name != 'local' or len(local.args) != 1:
        return None
    idx = local.args[0]
    if not isinstance(idx, KToken) or idx.sort.name != 'Int':
        return None

    locals_ = _local_items(cterm)
    local_idx = int(idx.token)
    if local_idx >= len(locals_):
        return None
    local_value = locals_[local_idx]
    if isinstance(local_value, KApply) and local_value.label.name.startswith('typedValue') and local_value.args:
        return local_value.args[0]
    return None


def _deref_cached(
    cterm: CTerm,
    value: KInner,
    cterm_symbolic: CTermSymbolic,
    cache: dict[tuple[str, KInner], KInner | None],
    *,
    context: str,
) -> KInner | None:
    """Dereference VALUE once, memoized per summary-rule compilation context."""
    key = (context, value)
    if key not in cache:
        cache[key] = _deref_value(cterm, value, cterm_symbolic)
    return cache[key]


def _fully_deref_value(cterm: CTerm, value: KInner, cterm_symbolic: CTermSymbolic) -> KInner | None:
    """Dereference nested reference/PTR values until a non-reference value is reached."""
    current = value
    for _ in range(8):
        if not _is_ref_or_pointer(current):
            return current
        next_value = _deref_value(cterm, current, cterm_symbolic)
        if next_value is None or next_value == current:
            return None
        current = next_value
    return None


def _ref_chain_supported(
    cterm: CTerm,
    value: KInner,
    cterm_symbolic: CTermSymbolic,
    deref_cache: dict[tuple[str, KInner], KInner | None],
    *,
    context: str,
) -> bool:
    """Return whether a reference/PTR chain can be dereferenced without stalling."""
    current = value
    for _ in range(8):
        if not isinstance(current, KApply):
            return True
        if current.label.name not in _REF_VALUE_LABELS:
            return True
        if len(current.args) < 3:
            return False
        next_value = _deref_cached(cterm, current, cterm_symbolic, deref_cache, context=context)
        if next_value is None or next_value == current:
            return False
        current = next_value
    return False


def _k_cell_head(cterm: CTerm) -> KInner:
    """Return the first item in <k>, or the whole <k> cell when it is not a sequence."""
    k_cell = cterm.cell('K_CELL')
    if isinstance(k_cell, KSequence):
        return k_cell.items[0] if k_cell.items else k_cell
    return k_cell


def _list_items(term: KInner) -> tuple[KInner, ...]:
    """Return concrete ListItem payloads from a K list, or empty tuple on unsupported shape."""
    if isinstance(term, KApply) and term.label.name == '.List':
        return ()
    items: list[KInner] = []
    for item in flatten_label('_List_', term):
        if isinstance(item, KApply) and item.label.name == 'ListItem' and len(item.args) == 1:
            items.append(item.args[0])
        elif isinstance(item, KApply) and item.label.name == '.List':
            continue
        else:
            return ()
    return tuple(items)


def _list_from_items(items: tuple[KInner, ...]) -> KInner:
    """Build a concrete K List term from ITEMS."""
    result: KInner = KApply('.List')
    for item in reversed(items):
        result = KApply('_List_', (KApply('ListItem', (item,)), result))
    return result


def _unwrap_injection(term: KInner) -> KInner:
    """Remove one K injection wrapper when TERM is a unary inj application."""
    if isinstance(term, KApply) and term.label.name.startswith('inj{') and len(term.args) == 1:
        return term.args[0]
    return term


def _local_items(cterm: CTerm) -> tuple[KInner, ...]:
    """Return unwrapped caller/callee local entries from LOCALS_CELL."""
    locals_cell = cterm.try_cell('LOCALS_CELL')
    if locals_cell is None:
        return ()
    return tuple(_unwrap_injection(item) for item in _list_items(locals_cell))


def _is_ref_or_pointer(term: KInner) -> bool:
    """Return whether TERM is a KMIR reference or pointer value."""
    return isinstance(term, KApply) and term.label.name in _REF_VALUE_LABELS


def _contains_ref_or_pointer(args: tuple[KInner, ...]) -> bool:
    """Return whether any term syntactically contains a reference or pointer label."""
    return any(_contains_label_fragment(arg, ('Reference', 'PtrLocal')) for arg in args)


def _contains_label_fragment(term: KInner, fragments: tuple[str, ...]) -> bool:
    """Return whether TERM or any child has a K label containing one fragment."""
    if isinstance(term, KApply):
        if any(fragment in term.label.name for fragment in fragments):
            return True
        return any(_contains_label_fragment(arg, fragments) for arg in term.args)
    if isinstance(term, KSequence):
        return any(_contains_label_fragment(item, fragments) for item in term.items)
    return False


def _safe_function_id(function: str) -> str:
    """Return a filesystem-safe, collision-resistant id for FUNCTION."""
    digest = hashlib.sha256(function.encode()).hexdigest()[:16]
    safe = ''.join(ch if ch.isalnum() else '-' for ch in function).strip('-')
    safe = safe[:48] or 'function'
    return f'{safe}-{digest}'


def _expect_dict(value: object) -> dict[str, object]:
    """Return VALUE as a dict or raise a type error for malformed summary data."""
    if not isinstance(value, dict):
        raise TypeError(f'Expected dict, got {type(value).__name__}')
    return value


def _expect_list(value: object) -> list[object]:
    """Return VALUE as a list or raise a type error for malformed trace data."""
    if not isinstance(value, list):
        raise TypeError(f'Expected list, got {type(value).__name__}')
    return value
