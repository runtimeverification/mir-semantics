from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kast.inner import KApply, KAs, KInner, KRewrite, KSequence, KSort, KToken, KVariable
from pyk.kast.manip import bottom_up, free_vars, remove_generated_cells
from pyk.kast.att import Atts
from pyk.kast.outer import KFlatModule, KRule
from pyk.proof.reachability import APRProof

from .kmir import KMIR, kmir_cterm_symbolic
from .smir import SMIRInfo, Ty

if TYPE_CHECKING:
    from typing import Final

    from pyk.cterm import CTerm

    from .options import ProveOpts


_LOGGER: Final = logging.getLogger(__name__)
_OBSERVED_HYGIENE_SUFFIX_RE = re.compile(r'^(?P<base>[A-Z][A-Z0-9_]*?)_[0-9a-f]{8}(?:__kmir_q_\d+)?$')


def _env_flag(name: str, *, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {'1', 'true', 'yes', 'on'}


def _env_int(name: str, *, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_csv(name: str) -> list[str]:
    value = os.getenv(name, '')
    return [item.strip() for item in value.split(',') if item.strip()]


@dataclass
class CalleeResult:
    summary_path: Path | None = None
    module_path: Path | None = None
    proof_id: str | None = None
    wall_time: float = 0.0
    prove_time: float = 0.0
    export_time: float = 0.0
    covers: int = 0
    stuck_nodes: int = 0
    frontier_nodes: int = 0
    cached: bool = False
    passed: bool = False
    skipped_reason: str | None = None
    summary_kind: str | None = None
    generated_online: bool = False

    @property
    def summarized(self) -> bool:
        return self.summary_path is not None and self.skipped_reason is None

    def to_dict(self) -> dict[str, object]:
        return {
            'summary_path': str(self.summary_path) if self.summary_path is not None else None,
            'module_path': str(self.module_path) if self.module_path is not None else None,
            'proof_id': self.proof_id,
            'wall_time': round(self.wall_time, 3),
            'prove_time': round(self.prove_time, 3),
            'export_time': round(self.export_time, 3),
            'covers': self.covers,
            'stuck_nodes': self.stuck_nodes,
            'frontier_nodes': self.frontier_nodes,
            'cached': self.cached,
            'passed': self.passed,
            'skipped_reason': self.skipped_reason,
            'summary_kind': self.summary_kind,
            'generated_online': self.generated_online,
        }


@dataclass
class CSEResult:
    """Result of a CSE (Compositional Symbolic Execution) pipeline run."""

    summaries: dict[str, Path] = field(default_factory=dict)
    exported_modules: dict[str, Path] = field(default_factory=dict)
    summary_times: dict[str, float] = field(default_factory=dict)
    skipped: dict[str, str] = field(default_factory=dict)
    callee_results: dict[str, CalleeResult] = field(default_factory=dict)
    final_proof: APRProof | None = None
    final_prove_time: float = 0.0
    final_proof_exec_time: float = 0.0
    start_symbol: str = ''
    summary_dir: Path | None = None
    output_path: Path | None = None
    observed_runtime_callees: list[int] = field(default_factory=list)
    online_generated_summaries: list[str] = field(default_factory=list)
    dynamic_summary_hits: dict[str, int] = field(default_factory=dict)

    @property
    def total_callee_time(self) -> float:
        return sum(detail.prove_time for detail in self.callee_results.values() if detail.summarized)

    @property
    def total_callee_wall_time(self) -> float:
        return sum(detail.wall_time for detail in self.callee_results.values() if detail.summarized)

    @property
    def total_export_time(self) -> float:
        return sum(detail.export_time for detail in self.callee_results.values() if detail.summarized)

    @property
    def total_time(self) -> float:
        return self.total_callee_time + self.final_prove_time

    def to_dict(self) -> dict[str, object]:
        final_status = None
        if self.final_proof is not None:
            final_status = {
                'id': self.final_proof.id,
                'passed': self.final_proof.passed,
                'failed': self.final_proof.failed,
                'status': str(self.final_proof.status),
                'exec_time': round(self.final_proof_exec_time, 3),
                'wall_time': round(self.final_prove_time, 3),
            }
        return {
            'start_symbol': self.start_symbol,
            'summary_dir': str(self.summary_dir) if self.summary_dir is not None else None,
            'output_path': str(self.output_path) if self.output_path is not None else None,
            'observed_runtime_callees': self.observed_runtime_callees,
            'online_generated_summaries': self.online_generated_summaries,
            'dynamic_summary_hits': self.dynamic_summary_hits,
            'summaries': {name: str(path) for name, path in self.summaries.items()},
            'exported_modules': {name: str(path) for name, path in self.exported_modules.items()},
            'summary_times': {name: round(value, 3) for name, value in self.summary_times.items()},
            'skipped': self.skipped,
            'callee_results': {name: detail.to_dict() for name, detail in self.callee_results.items()},
            'callee_times': {
                name: round(detail.prove_time, 3)
                for name, detail in self.callee_results.items()
                if detail.summarized
            },
            'callee_total_kore_time': round(self.total_callee_time, 3),
            'callee_total_wall_time': round(self.total_callee_wall_time, 3),
            'callee_total_export_time': round(self.total_export_time, 3),
            'final_proof': final_status,
            'final_proof_exec_time': round(self.final_proof_exec_time, 3),
            'final_proof_wall_time': round(self.final_prove_time, 3),
        }

    def write_json(self, output_path: Path) -> None:
        self.output_path = output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(self.to_dict(), indent=2))

    def summary_report(self) -> str:
        lines = ['=== CSE Summary ===']
        if self.summaries:
            lines.append(
                f'Callee summaries ({len(self.summaries)}, prove {self.total_callee_time:.1f}s, '
                f'export {self.total_export_time:.1f}s):'
            )
            for name, path in self.summaries.items():
                t = self.summary_times.get(name, 0.0)
                lines.append(f'  {name}: {t:.1f}s -> {path}')
        if self.skipped:
            lines.append(f'Skipped {len(self.skipped)} functions:')
            for name, reason in self.skipped.items():
                lines.append(f'  {name}: {reason}')
        if self.final_proof is not None:
            status = 'PASSED' if self.final_proof.passed else 'FAILED'
            lines.append(
                f'Main proof: {status} (exec {self.final_proof_exec_time:.1f}s, wall {self.final_prove_time:.1f}s)'
            )
            lines.append(
                f'Total: {self.total_time:.1f}s (callees {self.total_callee_time:.1f}s + main {self.final_prove_time:.1f}s)'
            )
        if self.output_path is not None:
            lines.append(f'Result JSON: {self.output_path}')
        return '\n'.join(lines)


def write_to_module(kmir: KMIR, proof: APRProof, to_module_path: Path) -> int:
    """Write proof KCFG as a K module to the specified path."""
    # Sanitize module name: K identifiers only allow alphanumeric + hyphen
    raw_name = proof.id.upper().replace('.', '-').replace('_', '-')
    module_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in raw_name) + '-SUMMARY'
    minimize_summary_rules = _env_flag('KMIR_CSE_MINIMIZE_SUMMARY_RULES', default=False)
    if minimize_summary_rules:
        rules = [
            edge.to_rule('BASIC-BLOCK', priority=20, defunc_with=kmir.definition, minimize=True)
            for edge in proof.kcfg.edges()
        ] + [merged.to_rule('BASIC-BLOCK', priority=20) for merged in proof.kcfg.merged_edges()]
        k_module = KFlatModule(module_name, rules)
    else:
        k_module = proof.kcfg.to_module(module_name=module_name, defunc_with=kmir.definition)

    push_prestate_ensures = _env_flag('KMIR_CSE_PUSH_PRESTATE_ENSURES_TO_REQUIRES', default=False)
    canonicalize_ptoken_key_guards = _env_flag('KMIR_CSE_CANONICALIZE_PTOKEN_KEY_GUARDS', default=False)
    summary_rule_priority = _env_int('KMIR_CSE_SUMMARY_RULE_PRIORITY', default=20)
    negative_requires_priority = _env_int('KMIR_CSE_NEGATIVE_REQUIRES_PRIORITY', default=30)
    exclude_negative_return_rules = _env_flag('KMIR_CSE_EXCLUDE_NEGATIVE_RETURN_RULES', default=False)

    def _iter_kinner_children(term: KInner) -> tuple[KInner, ...]:
        if isinstance(term, KApply):
            return term.args
        if isinstance(term, KRewrite):
            return (term.lhs, term.rhs)
        if isinstance(term, KSequence):
            return term.items
        if isinstance(term, KAs):
            return (term.pattern, term.alias)
        return ()

    def _collect_rule_lhs_vars(term: KInner) -> set[str]:
        vars_seen: set[str] = set()

        def visit(node: KInner) -> None:
            if isinstance(node, KRewrite):
                visit(node.lhs)
                return
            vars_seen.update(free_vars(node))
            for child in _iter_kinner_children(node):
                visit(child)

        visit(term)
        return vars_seen

    def _is_true_bool(term: KInner) -> bool:
        return isinstance(term, KToken) and term.token == 'true' and term.sort.name == 'Bool'

    def _and_bool(lhs: KInner, rhs: KInner) -> KInner:
        if _is_true_bool(lhs):
            return rhs
        if _is_true_bool(rhs):
            return lhs
        return KApply('_andBool_', (lhs, rhs))

    def _push_prestate_ensures(rule: KRule) -> KRule:
        if _is_true_bool(rule.ensures):
            return rule
        ensure_vars = set(free_vars(rule.ensures))
        if not ensure_vars:
            return rule.let(requires=_and_bool(rule.requires, rule.ensures), ensures=KToken('true', 'Bool'))
        lhs_vars = _collect_rule_lhs_vars(rule.body)
        if ensure_vars.issubset(lhs_vars):
            return rule.let(requires=_and_bool(rule.requires, rule.ensures), ensures=KToken('true', 'Bool'))
        return rule

    def _contains_not_bool(term: KInner) -> bool:
        if isinstance(term, KApply):
            return term.label.name == 'notBool_' or any(_contains_not_bool(arg) for arg in term.args)
        return any(_contains_not_bool(child) for child in _iter_kinner_children(term))

    def _contains_negative_guard(term: KInner) -> bool:
        if isinstance(term, KApply):
            if term.label.name in (
                'notBool_',
                '_=/=K_',
                '_=/=Int_',
                '#keyNe',
                '#keyNe(_,_)_KMIR-P-TOKEN_Bool_Key_Key',
            ):
                return True
            return any(_contains_negative_guard(arg) for arg in term.args)
        return any(_contains_negative_guard(child) for child in _iter_kinner_children(term))

    def _reprioritize_negative_rule(rule: KRule) -> KRule:
        if negative_requires_priority <= summary_rule_priority:
            return rule
        if not _contains_not_bool(rule.requires):
            return rule
        current_priority_raw = rule.att.get(Atts.PRIORITY)
        if current_priority_raw is None:
            current_priority = summary_rule_priority
        else:
            try:
                current_priority = int(current_priority_raw)
            except ValueError:
                return rule
        if current_priority != summary_rule_priority:
            return rule
        return rule.let(att=rule.att.update([Atts.PRIORITY(str(negative_requires_priority))]))

    def _mk_list(items: list[KInner]) -> KInner:
        result: KInner = KApply('.List')
        for item in reversed(items):
            result = KApply('_List_', (KApply('ListItem', (item,)), result))
        return result

    def _mk_byte_value(term: KInner) -> KInner:
        return KApply('Value::Integer', (term, KToken('8', 'Int'), KToken('false', 'Bool')))

    def _mk_and_bool(conjuncts: tuple[KInner, ...] | list[KInner]) -> KInner:
        items = tuple(conjuncts)
        if not items:
            return KToken('true', 'Bool')
        result = items[-1]
        for conjunct in reversed(items[:-1]):
            result = KApply('_andBool_', (conjunct, result))
        return result

    def _extract_range_list(term: KInner) -> KInner | None:
        if isinstance(term, KApply) and term.label.name == 'Value::Range' and len(term.args) == 1:
            return term.args[0]
        return None

    def _extract_range_sequence_list(term: KInner) -> KInner | None:
        if isinstance(term, KSequence) and len(term.items) == 1:
            return _extract_range_list(term.items[0])
        return None

    def _extract_range_like_list(term: KInner) -> KInner | None:
        direct = _extract_range_list(term)
        if direct is not None:
            return direct
        return _extract_range_sequence_list(term)

    def _mk_key(list_term: KInner) -> KInner:
        return KApply('Key(_)_KMIR-P-TOKEN_Key_List', (list_term,))

    def _mk_key_eq(lhs_list: KInner, rhs_list: KInner) -> KInner:
        return KApply('#keyEq(_,_)_KMIR-P-TOKEN_Bool_Key_Key', (_mk_key(lhs_list), _mk_key(rhs_list)))

    def _mk_key_ne(lhs_list: KInner, rhs_list: KInner) -> KInner:
        return KApply('#keyNe(_,_)_KMIR-P-TOKEN_Bool_Key_Key', (_mk_key(lhs_list), _mk_key(rhs_list)))

    def _flatten_k_list_items(term: KInner) -> tuple[KInner, ...] | None:
        items: list[KInner] = []
        current = term
        while True:
            if isinstance(current, KApply) and current.label.name == '.List' and len(current.args) == 0:
                return tuple(items)
            if isinstance(current, KApply) and current.label.name == '_List_' and len(current.args) == 2:
                head, tail = current.args
                if not isinstance(head, KApply) or head.label.name != 'ListItem' or len(head.args) != 1:
                    return None
                items.append(head.args[0])
                current = tail
                continue
            return None

    def _extract_byte_int_terms(list_term: KInner) -> tuple[KInner, ...] | None:
        items = _flatten_k_list_items(list_term)
        if items is None or len(items) != 32:
            return None
        ints: list[KInner] = []
        for item in items:
            if not isinstance(item, KApply) or item.label.name != 'Value::Integer' or len(item.args) != 3:
                return None
            width, signed = item.args[1], item.args[2]
            if width != KToken('8', 'Int') or signed != KToken('false', 'Bool'):
                return None
            ints.append(item.args[0])
        return tuple(ints)

    def _mk_byte_eq_conjunction(lhs_list: KInner, rhs_list: KInner) -> KInner | None:
        lhs_ints = _extract_byte_int_terms(lhs_list)
        rhs_ints = _extract_byte_int_terms(rhs_list)
        if lhs_ints is None or rhs_ints is None or len(lhs_ints) != len(rhs_ints):
            return None
        conjuncts = tuple(KApply('_==Int_', (lhs, rhs)) for lhs, rhs in zip(lhs_ints, rhs_ints, strict=True))
        return _mk_and_bool(conjuncts)

    def _flatten_and_bool(term: KInner) -> tuple[KInner, ...]:
        if isinstance(term, KApply) and term.label.name == '_andBool_' and len(term.args) == 2:
            return _flatten_and_bool(term.args[0]) + _flatten_and_bool(term.args[1])
        return (term,)

    def _extract_key_equality_from_byte_conjunction(term: KInner) -> KInner | None:
        conjuncts = _flatten_and_bool(term)
        byte_pairs: list[tuple[KInner, KInner]] = []
        for conjunct in conjuncts:
            if not isinstance(conjunct, KApply) or conjunct.label.name != '_==Int_' or len(conjunct.args) != 2:
                return None
            lhs, rhs = conjunct.args
            byte_pairs.append((lhs, rhs))
        if len(byte_pairs) != 32:
            return None
        lhs_list = _mk_list([_mk_byte_value(lhs) for lhs, _ in byte_pairs])
        rhs_list = _mk_list([_mk_byte_value(rhs) for _, rhs in byte_pairs])
        return _mk_key_eq(lhs_list, rhs_list)

    def _canonicalize_ptoken_key_guard_term(term: KInner) -> KInner:
        if isinstance(term, KApply) and term.label.name in ('_==K_', '_=/=K_') and len(term.args) == 2:
            lhs_list = _extract_range_like_list(term.args[0])
            rhs_list = _extract_range_like_list(term.args[1])
            if lhs_list is not None and rhs_list is not None:
                eq_conj = _mk_byte_eq_conjunction(lhs_list, rhs_list)
                if eq_conj is not None:
                    if term.label.name == '_==K_':
                        return eq_conj
                    return KApply('notBool_', (eq_conj,))
                if term.label.name == '_==K_':
                    return _mk_key_eq(lhs_list, rhs_list)
                return _mk_key_ne(lhs_list, rhs_list)
        if isinstance(term, KApply) and term.label.name == 'notBool_' and len(term.args) == 1:
            if isinstance(term.args[0], KApply) and term.args[0].label.name == '_==K_' and len(term.args[0].args) == 2:
                lhs_list = _extract_range_like_list(term.args[0].args[0])
                rhs_list = _extract_range_like_list(term.args[0].args[1])
                if lhs_list is not None and rhs_list is not None:
                    eq_conj = _mk_byte_eq_conjunction(lhs_list, rhs_list)
                    if eq_conj is not None:
                        return KApply('notBool_', (eq_conj,))
                    return _mk_key_ne(lhs_list, rhs_list)
            key_eq = _extract_key_equality_from_byte_conjunction(term.args[0])
            if isinstance(key_eq, KApply) and len(key_eq.args) == 2:
                lhs_key, rhs_key = key_eq.args
                return KApply('#keyNe(_,_)_KMIR-P-TOKEN_Bool_Key_Key', (lhs_key, rhs_key))
        return term

    def _canonicalize_ptoken_key_guards(rule: KRule) -> KRule:
        requires = bottom_up(_canonicalize_ptoken_key_guard_term, rule.requires)
        deduped: list[KInner] = []
        seen: set[str] = set()
        for conjunct in _flatten_and_bool(requires):
            key = repr(conjunct)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(conjunct)
        return rule.let(requires=_mk_and_bool(tuple(deduped)))

    if push_prestate_ensures:
        k_module = k_module.let(
            sentences=[
                _push_prestate_ensures(sent) if isinstance(sent, KRule) else sent for sent in k_module.sentences
            ]
        )

    if canonicalize_ptoken_key_guards:
        k_module = k_module.let(
            sentences=[
                _canonicalize_ptoken_key_guards(sent) if isinstance(sent, KRule) else sent
                for sent in k_module.sentences
            ]
        )

    if negative_requires_priority != summary_rule_priority:
        k_module = k_module.let(
            sentences=[
                _reprioritize_negative_rule(sent) if isinstance(sent, KRule) else sent for sent in k_module.sentences
            ]
        )

    if exclude_negative_return_rules:
        filtered_sentences: list[KSentence] = []
        excluded_labels: list[str] = []
        for sent in k_module.sentences:
            if isinstance(sent, KRule) and _contains_negative_guard(sent.requires):
                excluded_labels.append(sent.att.get(Atts.LABEL) or '<unknown>')
                continue
            filtered_sentences.append(sent)
        if excluded_labels:
            _LOGGER.info(
                'CSE: excluded %d negative exported return-summary rules from %s: %s',
                len(excluded_labels),
                proof.id,
                ', '.join(excluded_labels),
            )
        k_module = k_module.let(sentences=filtered_sentences)

    exported_rule_count = sum(1 for sent in k_module.sentences if isinstance(sent, KRule))

    if to_module_path.suffix == '.json':
        to_module_path.write_text(json.dumps(k_module.to_dict(), indent=2))
    else:

        def _process_sentence(sent):  # type: ignore[no-untyped-def]
            if isinstance(sent, KRule):
                sent = sent.let(att=sent.att.update([Atts.PRIORITY('200')]))
                sent = sent.let(body=remove_generated_cells(sent.body))
            return sent

        k_module_readable = k_module.let(sentences=[_process_sentence(sent) for sent in k_module.sentences])
        k_module_text = kmir.pretty_print(k_module_readable)
        to_module_path.write_text(k_module_text)
    _LOGGER.info(f'Module written to: {to_module_path}')
    return exported_rule_count


def _topological_sort(call_edges: dict[Ty, set[Ty]], root: Ty) -> list[Ty]:
    """Return callees of root in reverse topological order (leaves first).

    Cycles are broken by skipping back-edges (the function in the cycle
    that causes the back-edge is simply omitted from the order).
    The root itself is excluded from the result.
    """
    order: list[Ty] = []
    visited: set[Ty] = set()
    in_stack: set[Ty] = set()

    def dfs(node: Ty) -> None:
        if node in visited:
            return
        visited.add(node)
        in_stack.add(node)
        for callee in call_edges.get(node, set()):
            if callee in in_stack:
                continue  # back-edge, skip to break cycle
            if callee not in visited:
                dfs(callee)
        in_stack.discard(node)
        order.append(node)

    dfs(root)
    # Remove root itself — we don't want to summarize the target function
    if order and order[-1] == root:
        order.pop()
    return order  # leaves first, which is what we want


def _reachable_from_roots(call_edges: dict[Ty, set[Ty]], roots: set[Ty]) -> set[Ty]:
    reachable: set[Ty] = set()

    def dfs(node: Ty) -> None:
        if node in reachable:
            return
        reachable.add(node)
        for callee in call_edges.get(node, set()):
            dfs(callee)

    for root in roots:
        dfs(root)
    return reachable


def _reverse_reachable_to_targets(call_edges: dict[Ty, set[Ty]], targets: set[Ty]) -> set[Ty]:
    reverse_edges: dict[Ty, set[Ty]] = {}
    for caller, callees in call_edges.items():
        reverse_edges.setdefault(caller, set())
        for callee in callees:
            reverse_edges.setdefault(callee, set()).add(caller)

    reachable: set[Ty] = set()

    def dfs(node: Ty) -> None:
        if node in reachable:
            return
        reachable.add(node)
        for caller in reverse_edges.get(node, set()):
            dfs(caller)

    for target in targets:
        dfs(target)
    return reachable


def _runtime_related_callees(call_edges: dict[Ty, set[Ty]], observed_roots: set[Ty]) -> set[Ty]:
    return _reachable_from_roots(call_edges, observed_roots) | _reverse_reachable_to_targets(call_edges, observed_roots)


def _select_phase1_callees(
    callee_order: list[Ty],
    *,
    call_edges: dict[Ty, set[Ty]],
    observed_runtime_seen: set[int],
    observe_only_mode: bool,
    reuse_only_mode: bool,
    restrict_to_observed_runtime: bool,
) -> list[Ty]:
    if observe_only_mode:
        return []
    if reuse_only_mode:
        return callee_order
    if observed_runtime_seen and restrict_to_observed_runtime:
        observed_roots = {Ty(func_ty) for func_ty in observed_runtime_seen}
        phase1_allowed = _runtime_related_callees(call_edges, observed_roots)
        return [ty for ty in callee_order if ty in phase1_allowed]
    return callee_order


def _ty_to_name(smir_info: SMIRInfo, ty: Ty) -> str | None:
    """Map a Ty ID back to a human-readable function name."""
    sym = smir_info.function_symbols.get(int(ty))
    if sym is None:
        return None
    if 'NormalSym' in sym:
        normal_sym = sym['NormalSym']
        # Look up the item to get the short name
        if normal_sym in smir_info.items:
            item = smir_info.items[normal_sym]
            if SMIRInfo._is_func(item):
                return item['mono_item_kind']['MonoItemFn']['name']
        return normal_sym
    if 'IntrinsicSym' in sym:
        return sym['IntrinsicSym']
    return None


def _should_skip_cse_summary(name: str, *, start_symbol: str = '') -> str | None:
    """Return a skip reason for callees that should not be summarized."""
    stripped_name = name.lstrip('<')
    short_name = name.rsplit('::', 1)[-1]
    if short_name.startswith('cheatcode_'):
        return 'symbolic cheatcode helper'
    preserve_root_wrapper = _env_flag('KMIR_CSE_PRESERVE_ROOT_WRAPPER_SKIP', default=False)
    if preserve_root_wrapper and start_symbol:
        start_short_name = start_symbol.rsplit('::', 1)[-1]
        if start_short_name.startswith('test_') and short_name == start_short_name.removeprefix('test_'):
            return 'root_wrapper_target'
    summary_relevant_prefixes = (
        'pinocchio_token_program::',
        'pinocchio_token_interface::state::',
    )
    if stripped_name.startswith(summary_relevant_prefixes):
        return None
    if stripped_name.startswith(('core::', 'alloc::', 'std::', 'pinocchio::account_info::', 'pinocchio::program_error::')):
        return 'low_value_helper'
    if name.startswith('_ZN') or name in {'raw_eq', 'black_box', 'ctpop'}:
        return 'low_value_helper'
    if ' as core::' in name:
        return 'low_value_helper'
    low_value_markers = (
        '::eq',
        '::ne',
        '::spec_eq',
        '::spec_ne',
        '::is_err',
        '::is_ok',
        '::is_initialized',
        '::as_ptr',
        '::{closure#',
        '::unwrap',
        '::and_then',
        '::data_len',
        '::owner',
        '::from_residual',
    )
    if any(marker in name for marker in low_value_markers):
        return 'low_value_helper'
    # Default to summarizing crate-local and non-std functions unless they hit
    # one of the explicit low-value heuristics above.
    return None


def _has_body(smir_info: SMIRInfo, ty: Ty) -> bool:
    """Check if a function has a MIR body (not an intrinsic or extern)."""
    sym = smir_info.function_symbols.get(int(ty))
    if sym is None:
        return False
    if 'IntrinsicSym' in sym:
        return False
    if 'NormalSym' not in sym:
        return False
    normal_sym = sym['NormalSym']
    if normal_sym not in smir_info.items:
        return False
    item = smir_info.items[normal_sym]
    if not SMIRInfo._is_func(item):
        return False
    body = item['mono_item_kind']['MonoItemFn'].get('body')
    return body is not None


def _sanitize_filename(name: str) -> str:
    """Convert a function name to a safe filename, truncated to fit filesystem limits."""
    import hashlib

    safe = name.replace('::', '__').replace('<', '_').replace('>', '_').replace(' ', '_')
    safe = ''.join(c if c.isalnum() or c in '_-' else '_' for c in safe)
    # Filesystem limit is 255 bytes; leave room for .json extension + hash suffix
    max_base = 200
    if len(safe) > max_base:
        digest = hashlib.sha256(name.encode()).hexdigest()[:12]
        safe = safe[:max_base] + '_' + digest
    return safe


def _write_skip_marker(skip_marker_path: Path, *, reason: str) -> None:
    skip_marker_path.write_text(json.dumps({'skipped': True, 'reason': reason}, indent=2))


def _persist_callee_proof_to_summary_dir(
    proof: APRProof, callee_label: str, callee_proof_dir: Path | None, summary_dir: Path
) -> None:
    """Copy callee proof data to summary_dir/callee-proofs/ so reuse-only mode can load it."""
    if callee_proof_dir is None:
        return
    src = callee_proof_dir / callee_label
    if not src.exists():
        return
    import shutil

    dst = summary_dir / 'callee-proofs' / callee_label
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    _LOGGER.info('CSE: persisted callee proof %s to %s', callee_label, dst)


def _write_frontier_summary(
    frontier_summary_path: Path, *, proof: APRProof, frontier_node_ids: list[int], prove_time: float = 0.0
) -> None:
    frontier_summary_path.write_text(
        json.dumps(
            {
                'summary_kind': 'frontier',
                'proof_id': proof.id,
                'init': proof.init,
                'target': proof.target,
                'frontier_node_ids': frontier_node_ids,
                'prove_time': round(prove_time, 3),
            },
            indent=2,
        )
    )


def _load_frontier_summary_node_ids(frontier_summary_path: Path) -> list[int] | None:
    if not frontier_summary_path.exists():
        return None
    try:
        data = json.loads(frontier_summary_path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    frontier_node_ids = data.get('frontier_node_ids')
    if not isinstance(frontier_node_ids, list):
        return None
    normalized_ids = [node_id for node_id in frontier_node_ids if isinstance(node_id, int)]
    return normalized_ids or None


def _read_skip_marker(skip_marker_path: Path) -> str | None:
    if not skip_marker_path.exists():
        return None
    try:
        data = json.loads(skip_marker_path.read_text())
    except json.JSONDecodeError:
        return 'cached skip'
    if isinstance(data, dict):
        reason = data.get('reason')
        if isinstance(reason, str) and reason:
            return reason
    return 'cached skip'


def _load_observed_runtime_callee_counts(summary_dir: Path) -> dict[int, int]:
    observed_dir = summary_dir / 'observed-calls'
    if not observed_dir.exists():
        return {}
    observed_counts: dict[int, int] = {}
    for observed_path in sorted(observed_dir.glob('ty-*.json')):
        try:
            data = json.loads(observed_path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        func_ty = data.get('func_ty')
        if isinstance(func_ty, int):
            count = data.get('count')
            observed_counts[func_ty] = int(count) if isinstance(count, int) else 1
    return observed_counts


def _list_exported_summary_modules(summary_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in summary_dir.glob('*.json')
        if not path.name.endswith('.skip.json') and not path.name.endswith('.frontier.json')
    )


def _canonicalize_observed_var_name(name: str) -> str:
    match = _OBSERVED_HYGIENE_SUFFIX_RE.match(name)
    if match is None:
        return name
    return match.group('base')


def _canonicalize_observed_cterm_vars(cterm: CTerm) -> CTerm:
    from pyk.cterm import CTerm

    rename_count = 0

    def _rename(term: KInner) -> KInner:
        nonlocal rename_count
        if isinstance(term, KVariable):
            canonical_name = _canonicalize_observed_var_name(term.name)
            if canonical_name != term.name:
                rename_count += 1
                return KVariable(canonical_name, sort=term.sort)
        return term

    config = bottom_up(_rename, cterm.config)
    constraints = tuple(bottom_up(_rename, constraint) for constraint in cterm.constraints)
    if rename_count:
        _LOGGER.info('CSE: canonicalized %d observed call-site vars', rename_count)
    return CTerm(config, constraints)


def _load_observed_call_cterm(summary_dir: Path, func_ty: int) -> CTerm | None:
    from pyk.cterm import CTerm

    observed_path = summary_dir / 'observed-calls' / f'ty-{func_ty}.cterm.json'
    if not observed_path.exists():
        return None
    try:
        data = json.loads(observed_path.read_text())
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        return _canonicalize_observed_cterm_vars(CTerm.from_dict(data))
    except Exception:
        return None


def _build_call_summary_target_k_cell(observed_call_cterm: CTerm) -> KInner | None:
    from .kmir import KMIRCSESemantics

    semantics = KMIRCSESemantics(callee_proofs={}, summary_dir=Path('/tmp'))
    call_info = semantics._extract_call_info(observed_call_cterm.cell('K_CELL'))
    if call_info is None:
        return None

    _func_ty, _args_operand, dest, target = call_info
    is_entry_call = isinstance(target, KApply) and 'noBasicBlockIdx' in target.label.name
    is_normal_call = isinstance(target, KApply) and 'someBasicBlockIdx' in target.label.name

    if is_entry_call:
        return KSequence([KMIR.Symbols.END_PROGRAM])
    if is_normal_call:
        target_bb = target.args[0]
        return KSequence(
            [
                KApply(
                    '#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation',
                    (dest, KVariable('CSE_SUMMARY_RETVAL', sort=KSort('Evaluation'))),
                ),
                KApply('#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx', (target_bb,)),
            ]
        )
    return None


def _generate_frontier_summary_rules(
    *,
    proof: APRProof,
    frontier_node_ids: list[int],
    func_ty: int,
    rule_label_prefix: str,
    priority: int = 15,
) -> list[KRule]:
    """Generate K rewrite rules that skip a callee function body using frontier summary.

    Interception point: #execBlock inside the callee, AFTER the normal call
    mechanism has pushed the stack frame and set up callee locals.  This is
    more localized than intercepting at #execTerminatorCall because:

    - <currentFunc> identifies the callee (ty(N))
    - <locals> has the callee's arguments (set up by #setArgsFromStack)
    - Return uses standard terminatorKindReturn (K handles stack pop)
    - No coupling with the caller's state

    Each frontier branch produces one rule.  The requires clause uses
    getLocal(LOCALS, idx) to test argument values, encoding the full
    input-output relationship.  The RHS sets local[0] (return slot) and
    executes terminatorKindReturn.
    """
    from pyk.kast.att import EMPTY_ATT
    from pyk.kast.manip import free_vars as _free_vars
    from pyk.kast.inner import Subst as _Subst

    rules: list[KRule] = []

    # Build variable-to-local-index mapping from the callee proof's init node.
    # After normalization, the init node's LOCALS has symbolic variables at each
    # argument position: local[0]=return slot, local[1]=arg1, local[2]=arg2, ...
    init_node = proof.kcfg.node(proof.init)
    var_to_local_idx: dict[str, int] = {}
    try:
        init_locals = init_node.cterm.cell('LOCALS_CELL')
        from .kmir import KMIRCSESemantics
        init_local_items = KMIRCSESemantics._list_items(init_locals)
        for idx, item in enumerate(init_local_items):
            for var_name, _var_node in KMIRCSESemantics._extract_free_vars(item):
                if var_name not in var_to_local_idx:
                    var_to_local_idx[var_name] = idx
    except Exception:
        _LOGGER.info('CSE rule gen: could not extract init locals for variable mapping')

    _LOGGER.info('CSE rule gen: var_to_local_idx = %s', var_to_local_idx)

    for branch_idx, node_id in enumerate(frontier_node_ids):
        node = proof.kcfg.node(node_id)
        k_cell = node.cterm.cell('K_CELL')

        # Extract return value from frontier node's K_CELL:
        # Expected: KSequence([#setLocalValue(dest, ret_value), #execBlockIdx(bb), ...])
        raw_ret_value = _extract_boundary_return_value_static(k_cell)
        if raw_ret_value is None:
            _LOGGER.warning('CSE rule gen: frontier node %d has no extractable return value, skipping', node_id)
            continue

        # Substitute callee variables in the return value with valueOf(getLocal(LOCALS, idx)).
        # This binds the return value to the callee's actual argument values.
        locals_var = KVariable('LOCALS', sort=KSort('List'))
        ret_free_vars = _free_vars(raw_ret_value)
        if ret_free_vars:
            ret_subst: dict[str, KInner] = {}
            for var_name in sorted(ret_free_vars):
                if var_name in var_to_local_idx:
                    idx = var_to_local_idx[var_name]
                    # valueOf({getLocal(LOCALS, idx)}:>TypedValue)
                    get_local = KApply(
                        'getLocal(_,_)_RT-DATA_TypedLocal_List_Int',
                        (locals_var, KToken(str(idx), KSort('Int'))),
                    )
                    cast_to_typed = KApply(
                        '#SemanticCastToTypedValue',
                        (get_local,),
                    )
                    ret_subst[var_name] = KApply(
                        'valueOf(_)_RT-VALUE_Value_TypedValue',
                        (cast_to_typed,),
                    )
                else:
                    # Variable not in init locals — abstract to fresh symbolic var
                    ret_subst[var_name] = KVariable(f'CSE_RET_{branch_idx}_{var_name}')
            ret_value = _Subst(ret_subst)(raw_ret_value)
        else:
            ret_value = raw_ret_value

        # Build requires clause from frontier node constraints.
        # Substitute callee variables with valueOf(getLocal(LOCALS, idx)) so the
        # booster can evaluate them against the callee's actual argument values.
        requires_terms: list[KInner] = []
        for constraint in node.cterm.constraints:
            constraint_vars = _free_vars(constraint)
            # Only include constraints where ALL variables can be mapped to locals
            if constraint_vars and all(v in var_to_local_idx for v in constraint_vars):
                subst_map: dict[str, KInner] = {}
                for v in constraint_vars:
                    idx = var_to_local_idx[v]
                    get_local = KApply(
                        'getLocal(_,_)_RT-DATA_TypedLocal_List_Int',
                        (locals_var, KToken(str(idx), KSort('Int'))),
                    )
                    cast_to_typed = KApply('#SemanticCastToTypedValue', (get_local,))
                    subst_map[v] = KApply('valueOf(_)_RT-VALUE_Value_TypedValue', (cast_to_typed,))
                substituted = _Subst(subst_map)(constraint)
                # Unwrap #Equals(true, EXPR) → EXPR
                if isinstance(substituted, KApply) and substituted.label.name == '#Equals' and len(substituted.args) == 2:
                    lhs_c, rhs_c = substituted.args
                    if isinstance(lhs_c, KToken) and lhs_c.token == 'true' and lhs_c.sort.name == 'Bool':
                        requires_terms.append(rhs_c)
                    elif isinstance(rhs_c, KToken) and rhs_c.token == 'true' and rhs_c.sort.name == 'Bool':
                        requires_terms.append(lhs_c)
                    # Skip #Equals with non-Bool args
                elif isinstance(substituted, KApply) and substituted.label.name == '#Ceil':
                    pass  # Skip #Ceil constraints
                else:
                    requires_terms.append(substituted)

        if requires_terms:
            requires: KInner = requires_terms[0]
            for rt in requires_terms[1:]:
                requires = KApply('_andBool_', (requires, rt))
        else:
            requires = KToken('true', KSort('Bool'))

        # Build rule LHS: match #execBlock(_) inside the callee function.
        # After the normal call mechanism pushes the stack frame and sets up
        # callee locals via #setArgsFromStack, the K cell has #execBlock(BB).
        # We match on <currentFunc> ty(N) to identify the callee.
        block_var = KVariable('_CSE_BLOCK', sort=KSort('BasicBlock'))
        rest_var = KVariable('_CSE_REST', sort=KSort('K'))

        lhs_k = KSequence([KApply('#execBlock(_)_KMIR-CONTROL-FLOW_KItem_BasicBlock', (block_var,)), rest_var])

        # Build rule RHS: set local[0] (return slot) and execute terminatorKindReturn.
        # The standard K return mechanism pops the stack, writes dest, and jumps to target.
        return_place = KApply(
            'place',
            (
                KApply('local', (KToken('0', KSort('Int')),)),
                KApply('ProjectionElems::empty', ()),
            ),
        )
        rhs_k = KSequence(
            [
                KApply('#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation', (return_place, ret_value)),
                KApply(
                    '#execTerminator(_)_KMIR-CONTROL-FLOW_KItem_Terminator',
                    (
                        KApply(
                            'terminator(_,_)_BODY_Terminator_TerminatorKind_Span',
                            (
                                KApply('TerminatorKind::Return', ()),
                                KApply('span', (KToken('0', KSort('Int')),)),
                            ),
                        ),
                    ),
                ),
                rest_var,
            ]
        )

        # Build full configuration: <generatedTop>(<kmir>(<k>, <currentFunc>, <locals>, ...), ...)
        k_cell_rule = KApply('<k>', (KRewrite(lhs_k, rhs_k),))
        current_func_cell = KApply('<currentFunc>', (KApply('ty', (KToken(str(func_ty), KSort('Int')),)),))
        locals_cell = KApply('<locals>', (locals_var,))

        # <currentFrame> wraps <locals> and other cells
        current_frame = KApply(
            '<currentFrame>',
            (
                KVariable(f'_CSE_BODY_{branch_idx}', sort=KSort('CurrentBodyCell')),
                KVariable(f'_CSE_CALLER_{branch_idx}', sort=KSort('CallerCell')),
                KVariable(f'_CSE_DEST_{branch_idx}', sort=KSort('DestCell')),
                KVariable(f'_CSE_TARGET_{branch_idx}', sort=KSort('TargetCell')),
                KVariable(f'_CSE_UNWIND_{branch_idx}', sort=KSort('UnwindCell')),
                locals_cell,
            ),
        )
        kmir_cell = KApply(
            '<kmir>',
            (
                k_cell_rule,
                KVariable(f'_CSE_RETVAL_{branch_idx}', sort=KSort('RetValCell')),
                current_func_cell,
                current_frame,
                KVariable(f'_CSE_STACK_{branch_idx}', sort=KSort('StackCell')),
            ),
        )
        body = KApply(
            '<generatedTop>',
            (
                kmir_cell,
                KVariable(f'_CSE_GENCTR_{branch_idx}', sort=KSort('GeneratedCounterCell')),
            ),
        )

        rule = KRule(
            body=body,
            requires=requires,
            ensures=KToken('true', KSort('Bool')),
            att=EMPTY_ATT.update([Atts.PRIORITY(str(priority))]),
        )
        rules.append(rule)
        _LOGGER.info(
            'CSE rule gen: generated rule %s-branch-%d for ty(%d) frontier node %d',
            rule_label_prefix,
            branch_idx,
            func_ty,
            node_id,
        )

    return rules


def _extract_boundary_return_value_static(k_cell: KInner) -> KInner | None:
    """Extract the return value from a frontier node's K_CELL (static version)."""
    if not isinstance(k_cell, KSequence) or len(k_cell.items) < 2:
        return None
    first = k_cell.items[0]
    second = k_cell.items[1]
    if not isinstance(first, KApply) or '#setLocalValue' not in first.label.name:
        return None
    if not isinstance(second, KApply) or '#execBlockIdx' not in second.label.name:
        return None
    return first.args[1]


def _write_summary_rules_module(
    module_path: Path,
    rules: list[KRule],
    module_name: str,
) -> int:
    """Write a list of K rules as a JSON K module."""
    k_module = KFlatModule(module_name, rules)
    module_path.write_text(json.dumps(k_module.to_dict(), indent=2))
    return len(rules)


def _is_end_program_k(k_cell: KInner) -> bool:
    if k_cell == KMIR.Symbols.END_PROGRAM:
        return True
    if type(k_cell) is KSequence and k_cell.arity == 1 and k_cell[0] == KMIR.Symbols.END_PROGRAM:
        return True
    return False


def _call_boundary_frontier_node_ids(proof: APRProof, target_k_cell: KInner | None) -> list[int]:
    if not isinstance(target_k_cell, KSequence) or len(target_k_cell.items) < 2:
        return []

    target_first = target_k_cell.items[0]
    target_second = target_k_cell.items[1]
    if not isinstance(target_first, KApply) or '#setLocalValue' not in target_first.label.name:
        return []
    if not isinstance(target_second, KApply) or '#execBlockIdx' not in target_second.label.name:
        return []

    target_dest = target_first.args[0]
    target_bb = target_second.args[0]

    predecessor_ids: dict[int, set[int]] = {node.id: set() for node in proof.kcfg.nodes}
    for edge in proof.kcfg.edges():
        predecessor_ids.setdefault(edge.target.id, set()).add(edge.source.id)
    for split in proof.kcfg.splits():
        for split_target in split.targets:
            target_id = split_target.target.id if hasattr(split_target, 'target') else split_target.id
            predecessor_ids.setdefault(target_id, set()).add(split.source.id)

    matching_ids: set[int] = set()
    for node in proof.kcfg.nodes:
        if node.id == proof.target:
            continue
        k_cell = node.cterm.cell('K_CELL')
        if not isinstance(k_cell, KSequence) or len(k_cell.items) < 2:
            continue
        node_first = k_cell.items[0]
        node_second = k_cell.items[1]
        if not isinstance(node_first, KApply) or '#setLocalValue' not in node_first.label.name:
            continue
        if not isinstance(node_second, KApply) or '#execBlockIdx' not in node_second.label.name:
            continue
        if node_first.args[0] != target_dest or node_second.args[0] != target_bb:
            continue
        matching_ids.add(node.id)

    if not matching_ids:
        return []

    def has_matching_ancestor(node_id: int) -> bool:
        worklist = list(predecessor_ids.get(node_id, ()))
        seen: set[int] = set()
        while worklist:
            predecessor = worklist.pop()
            if predecessor in seen:
                continue
            seen.add(predecessor)
            if predecessor in matching_ids:
                return True
            worklist.extend(predecessor_ids.get(predecessor, ()))
        return False

    return [node_id for node_id in sorted(matching_ids) if not has_matching_ancestor(node_id)]


def _backfill_observed_calls_from_kcfg(summary_dir: Path, proof: APRProof, *, interesting_tys: set[int]) -> None:
    if not interesting_tys:
        return

    from .kmir import KMIRCSESemantics

    semantics = KMIRCSESemantics(callee_proofs={}, summary_dir=summary_dir, learn_observed_calls=True)
    candidate_nodes_by_ty: dict[int, list[object]] = {}
    for node in proof.kcfg.nodes:
        try:
            call_info = semantics._extract_call_info(node.cterm.cell('K_CELL'))
        except Exception:
            call_info = None
        if call_info is None:
            continue
        func_ty = call_info[0]
        if func_ty not in interesting_tys:
            continue
        candidate_nodes_by_ty.setdefault(func_ty, []).append(node)

    if not candidate_nodes_by_ty:
        return

    for func_ty, nodes in candidate_nodes_by_ty.items():
        # Record more constrained callsites first so the final stored cterm is
        # the least-constrained runtime entry we actually saw.
        ordered_nodes = sorted(nodes, key=lambda node: (len(node.cterm.constraints), node.id), reverse=True)
        for node in ordered_nodes:
            semantics.custom_step(node.cterm, None)

    _LOGGER.info(
        'CSE: backfilled observed callsites for %d callees from proof %s',
        len(candidate_nodes_by_ty),
        proof.id,
    )


def _prove_callee_summary(
    *,
    ty: Ty,
    name: str,
    opts: ProveOpts,
    smir_info: SMIRInfo,
    main_smir: SMIRInfo,
    summary_dir: Path,
    result: CSEResult,
    observed_call_cterm: CTerm | None = None,
) -> APRProof | None:
    from pyk.cterm import CTerm

    safe_name = _sanitize_filename(name)
    summary_path = summary_dir / f'{safe_name}.json'
    frontier_summary_path = summary_dir / f'{safe_name}.frontier.json'
    skip_marker_path = summary_dir / f'{safe_name}.skip.json'

    print(f'[CSE] {name}: proving (normalized entry)...', flush=True)
    t0 = time.time()

    try:
        available_summaries = [p for p in result.exported_modules.values() if p.exists()]

        callee_proof_dir = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
        if callee_proof_dir:
            callee_proof_dir.mkdir(parents=True, exist_ok=True)

        callee_target = callee_proof_dir / safe_name if callee_proof_dir else Path(f'/tmp/cse-{safe_name}')
        kmir_callee = KMIR.from_kompiled_kore(
            main_smir,
            target_dir=callee_target,
            extra_modules=available_summaries or None,
            bug_report=opts.bug_report,
            symbolic=True,
            haskell_target=opts.haskell_target,
            llvm_lib_target=opts.llvm_lib_target,
        )

        if observed_call_cterm is not None:
            init_cterm = _canonicalize_observed_cterm_vars(observed_call_cterm)
            observed_call_cterm = init_cterm
            _LOGGER.info('CSE: using observed call-site cterm for %s', name)
        else:
            observed_call_cterm = _load_observed_call_cterm(summary_dir, int(ty))
            if observed_call_cterm is not None:
                init_cterm = observed_call_cterm
                _LOGGER.info('CSE: using observed call-site cterm for %s', name)
            else:
                from .kast import SymbolicMode, make_call_config

                init_config, init_constraints = make_call_config(
                    kmir_callee.definition,
                    smir_info=main_smir,
                    start_symbol=name,
                    mode=SymbolicMode(),
                )
                init_cterm = CTerm(init_config, init_constraints)

        target_k_cell = _build_call_summary_target_k_cell(observed_call_cterm) if observed_call_cterm is not None else None

        with kmir_cterm_symbolic(
            kmir_callee.definition,
            kmir_callee.definition_dir,
            llvm_definition_dir=kmir_callee.llvm_library_dir,
            bug_report=kmir_callee.bug_report,
            id=f'{name}-normalize',
        ) as cts:
            normalized = init_cterm
            setup_depth = 0
            for _step in range(30):
                result_cterm, _next, depth, _vacuous, _logs = cts.execute(normalized, depth=1)
                if depth == 0:
                    if _next:
                        normalized = _next[0].state
                        setup_depth += 1
                    else:
                        break
                else:
                    normalized = result_cterm
                    setup_depth += 1

                k = normalized.cell('K_CELL')
                from pyk.kast.inner import KApply as _KApp
                from pyk.kast.inner import KSequence as _KSeq

                first = k.items[0] if isinstance(k, _KSeq) and k.items else k
                if isinstance(first, _KApp) and '#execBlock(' in first.label.name:
                    break

            if setup_depth == 0:
                _LOGGER.warning(f'CSE: call setup made no progress for {name}')
                result.skipped[name] = 'setup stuck'
                result.callee_results[name] = CalleeResult(skipped_reason='setup stuck')
                _write_skip_marker(skip_marker_path, reason='setup stuck')
                return None

        _LOGGER.info(f'CSE: normalized entry in {setup_depth} steps for {name}')

        from ._prove import _prove_sequential, apr_proof_from_smir

        callee_label = f'{opts.rs_file.stem}.{name}'
        import hashlib as _hashlib

        raw_label = callee_label
        callee_label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
        if len(callee_label) > 200:
            digest = _hashlib.sha256(raw_label.encode()).hexdigest()[:12]
            callee_label = callee_label[:200] + '_' + digest

        proof = apr_proof_from_smir(
            kmir_callee,
            callee_label,
            main_smir,
            start_symbol=name,
            proof_dir=callee_proof_dir,
            init_cterm=normalized,
            target_k_cell=target_k_cell,
        )
        if callee_proof_dir:
            main_smir.dump(callee_proof_dir / callee_label / 'smir.json')

        cse_callee_max_iterations = _env_int('KMIR_CSE_CALLEE_MAX_ITERATIONS', default=100)
        if not proof.passed:
            from .options import ProveOpts as ProveOptsClass

            callee_opts = ProveOptsClass(
                rs_file=opts.rs_file,
                max_depth=opts.max_depth,
                max_iterations=cse_callee_max_iterations,
            )
            callee_cut_points: list[str] = []
            if target_k_cell is not None and not _is_end_program_k(target_k_cell):
                callee_cut_points.extend(
                    [
                        'KMIR-CONTROL-FLOW.termReturnSome',
                        'KMIR-CONTROL-FLOW.termReturnNone',
                        'KMIR-CONTROL-FLOW.endprogram-return',
                        'KMIR-CONTROL-FLOW.endprogram-no-return',
                        'RT-DATA.#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation2-heat',
                        'RT-DATA.#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation2-cool',
                    ]
                )
            _prove_sequential(
                kmir_callee,
                proof,
                opts=callee_opts,
                label=callee_label,
                cut_point_rules=callee_cut_points,
            )

        elapsed = time.time() - t0
        covers = [c for c in proof.kcfg.covers() if c.target.id == proof.target]
        stuck_nodes = [n for n in proof.kcfg.leaves if proof.kcfg.is_stuck(n.id)]
        boundary_frontier_node_ids = _call_boundary_frontier_node_ids(proof, target_k_cell)
        if boundary_frontier_node_ids:
            setattr(proof, '_cse_frontier_node_ids', tuple(boundary_frontier_node_ids))
            frontier_nodes = [proof.kcfg.node(node_id) for node_id in boundary_frontier_node_ids]
        else:
            frontier_nodes = [n for n in proof.kcfg.leaves if n.id != proof.target]
        if not frontier_nodes and proof.init != proof.target:
            frontier_nodes = [proof.kcfg.node(proof.init)]

        if not covers:
            if not frontier_nodes:
                print(f'[CSE] {name}: no successful paths in {elapsed:.1f}s, skipping summary')
                reason = f'no covers ({elapsed:.1f}s)'
                result.skipped[name] = reason
                _write_skip_marker(skip_marker_path, reason=reason)
                result.callee_results[name] = CalleeResult(
                    proof_id=proof.id,
                    wall_time=elapsed,
                    prove_time=proof.exec_time,
                    covers=0,
                    stuck_nodes=len(stuck_nodes),
                    passed=proof.passed,
                    skipped_reason=reason,
                )
                return None

            if summary_path.exists():
                summary_path.unlink()
            export_started = time.perf_counter()
            _write_frontier_summary(
                frontier_summary_path,
                proof=proof,
                frontier_node_ids=[node.id for node in frontier_nodes],
                prove_time=proof.exec_time,
            )
            export_time = time.perf_counter() - export_started
            if skip_marker_path.exists():
                skip_marker_path.unlink()

            # Persist callee proof to summary_dir so reuse-only mode can load it
            _persist_callee_proof_to_summary_dir(proof, callee_label, callee_proof_dir, summary_dir)

            # Generate synthetic summary rules (one per frontier branch)
            summary_rules = _generate_frontier_summary_rules(
                proof=proof,
                frontier_node_ids=[node.id for node in frontier_nodes],
                func_ty=int(ty),
                rule_label_prefix=f'cse-{safe_name}',
            )
            summary_rule_module_path = summary_dir / f'{safe_name}.summary-rules.json'
            if summary_rules:
                rule_module_name = ''.join(c if c.isalnum() or c == '-' else '-' for c in safe_name.upper()) + '-CSE-RULES'
                rule_count = _write_summary_rules_module(summary_rule_module_path, summary_rules, rule_module_name)
                result.exported_modules[name] = summary_rule_module_path
                _LOGGER.info('CSE: exported %d summary rules for %s to %s', rule_count, name, summary_rule_module_path)
            else:
                rule_count = 0

            print(
                f'[CSE] {name}: FRONTIER ({len(frontier_nodes)} nodes, {len(stuck_nodes)} stuck) '
                f'in {elapsed:.1f}s, {rule_count} summary rules',
                flush=True,
            )
            result.summaries[name] = frontier_summary_path
            result.summary_times[name] = proof.exec_time
            result.callee_results[name] = CalleeResult(
                summary_path=frontier_summary_path,
                module_path=summary_rule_module_path if summary_rules else None,
                proof_id=proof.id,
                wall_time=elapsed,
                prove_time=proof.exec_time,
                export_time=export_time,
                covers=0,
                stuck_nodes=len(stuck_nodes),
                frontier_nodes=len(frontier_nodes),
                passed=proof.passed,
                summary_kind='frontier',
            )
            return proof

        status_str = 'PASSED' if proof.passed else f'PARTIAL ({len(covers)} paths ok, {len(stuck_nodes)} stuck)'
        print(f'[CSE] {name}: {status_str} in {elapsed:.1f}s', flush=True)

        if _env_flag('KMIR_CSE_MINIMIZE_SUMMARY_EXPORT', default=False):
            proof.minimize_kcfg()

        from pyk.kdist import kdist

        kmir = KMIR(
            definition_dir=kdist.which(opts.haskell_target or 'mir-semantics.haskell'),
            llvm_library_dir=kdist.which(opts.llvm_lib_target or 'mir-semantics.llvm-library'),
        )
        export_started = time.perf_counter()
        exported_rule_count = write_to_module(kmir, proof, summary_path)
        export_time = time.perf_counter() - export_started
        if frontier_summary_path.exists():
            frontier_summary_path.unlink()
        if skip_marker_path.exists():
            skip_marker_path.unlink()

        # Persist callee proof to summary_dir so reuse-only mode can load it
        _persist_callee_proof_to_summary_dir(proof, callee_label, callee_proof_dir, summary_dir)

        result.summaries[name] = summary_path
        result.exported_modules[name] = summary_path
        result.summary_times[name] = proof.exec_time
        result.callee_results[name] = CalleeResult(
            summary_path=summary_path,
            module_path=summary_path,
            proof_id=proof.id,
            wall_time=elapsed,
            prove_time=proof.exec_time,
            export_time=export_time,
            covers=exported_rule_count,
            stuck_nodes=len(stuck_nodes),
            passed=proof.passed,
            summary_kind='return',
        )
        print(
            f'[CSE] {name}: exported {exported_rule_count} path summaries to {summary_path}'
            f' (from {len(covers)} covers)'
        )
        return proof

    except Exception as e:
        elapsed = time.time() - t0
        _LOGGER.warning(f'CSE: failed to prove {name}: {e}', exc_info=True)
        result.skipped[name] = f'error: {e}'
        _write_skip_marker(skip_marker_path, reason=result.skipped[name])
        result.callee_results[name] = CalleeResult(
            wall_time=elapsed,
            skipped_reason=result.skipped[name],
        )
        print(f'[CSE] {name}: ERROR in {elapsed:.1f}s — {e}')
        return None


def cse_prove(opts: ProveOpts) -> CSEResult:
    """Compositional Symbolic Execution pipeline.

    1. Parse SMIR, extract call graph
    2. Topologically sort callees (bottom-up)
    3. For each callee: prove, minimize, export summary
    4. Re-prove target with all summaries
    """
    from .cargo import cargo_get_smir_json

    result = CSEResult()

    # Parse SMIR
    if opts.parsed_smir is not None:
        smir_info = SMIRInfo(opts.parsed_smir)
    elif opts.smir:
        smir_info = SMIRInfo.from_file(opts.rs_file)
    else:
        smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

    # Determine summary directory
    summary_dir = opts.summary_dir
    if summary_dir is None:
        if opts.proof_dir is not None:
            summary_dir = opts.proof_dir / 'summaries'
        else:
            summary_dir = Path.cwd() / 'summaries'
    summary_dir.mkdir(parents=True, exist_ok=True)
    result.summary_dir = summary_dir
    learn_observed_calls = _env_flag('KMIR_CSE_SUMMARY_GENERATION', default=False)
    observe_only_mode = learn_observed_calls and _env_flag('KMIR_CSE_OBSERVE_ONLY', default=False)
    reuse_only_mode = _env_flag('KMIR_CSE_REUSE_ONLY', default=False)
    generate_only_mode = _env_flag('KMIR_CSE_GENERATE_ONLY', default=False)
    online_autoreuse_mode = _env_flag(
        'KMIR_CSE_ONLINE_AUTOREUSE',
        default=learn_observed_calls and not observe_only_mode and not reuse_only_mode and not generate_only_mode,
    )
    if online_autoreuse_mode:
        observe_only_mode = False
    autoreuse_mode = online_autoreuse_mode
    observed_min_count = max(_env_int('KMIR_CSE_OBSERVED_MIN_COUNT', default=2), 1)
    observed_runtime_counts = _load_observed_runtime_callee_counts(summary_dir) if learn_observed_calls else {}
    observed_runtime_seen = set(observed_runtime_counts)
    observed_runtime_promoted = {
        func_ty for func_ty, count in observed_runtime_counts.items() if count >= observed_min_count
    }
    restrict_phase1_to_observed_runtime = _env_flag('KMIR_CSE_RESTRICT_PHASE1_TO_OBSERVED_RUNTIME', default=False)
    if observed_runtime_counts:
        _LOGGER.info(
            'CSE: loaded %d observed runtime callees from %s (%d eligible at threshold=%d)',
            len(observed_runtime_counts),
            summary_dir / 'observed-calls',
            len(observed_runtime_promoted),
            observed_min_count,
        )

    # Get root function Ty
    start_name = opts.start_symbol
    result.start_symbol = start_name
    if start_name not in smir_info.function_tys:
        raise ValueError(
            f'Start symbol {start_name!r} not found in SMIR. Available: {list(smir_info.function_tys.keys())[:10]}'
        )
    root_ty = Ty(smir_info.function_tys[start_name])
    observed_runtime_seen.discard(int(root_ty))
    observed_runtime_promoted.discard(int(root_ty))
    result.observed_runtime_callees = sorted(observed_runtime_seen)

    # Topological sort of callees
    callee_order = _topological_sort(smir_info.call_edges, root_ty)
    _LOGGER.info(f'CSE: {len(callee_order)} callees to summarize for {start_name}')

    # Phase 1: Generate summaries for each callee
    # Use the same SMIR subset (reduce_to(start_name)) for ALL proofs.
    # This ensures callee normalized entries match the main proof's call setup.
    main_smir = smir_info.reduce_to(start_name)

    phase1_callee_order = _select_phase1_callees(
        callee_order,
        call_edges=smir_info.call_edges,
        observed_runtime_seen=observed_runtime_seen,
        observe_only_mode=observe_only_mode,
        reuse_only_mode=reuse_only_mode,
        restrict_to_observed_runtime=restrict_phase1_to_observed_runtime,
    )
    phase1_only_names = set(_env_csv('KMIR_CSE_PHASE1_ONLY_NAMES'))
    if phase1_only_names:
        phase1_callee_order = [
            ty for ty in phase1_callee_order if (name := _ty_to_name(smir_info, ty)) is not None and name in phase1_only_names
        ]
        _LOGGER.info(
            'CSE: filtered phase-1 to %d callees via KMIR_CSE_PHASE1_ONLY_NAMES',
            len(phase1_callee_order),
        )
    if observe_only_mode:
        _LOGGER.info('CSE: observe-only mode active, skipping phase-1 callee proving for %s', start_name)
    elif online_autoreuse_mode:
        _LOGGER.info(
            'CSE: observe-generate-autoreuse mode active for %s; reusing cache and deferring uncached callee proving to runtime call-sites',
            start_name,
        )
    elif reuse_only_mode:
        _LOGGER.info('CSE: reuse-only mode active, loading cached summaries/skips without new callee proving')
    elif observed_runtime_seen and restrict_phase1_to_observed_runtime:
        _LOGGER.info(
            'CSE: restricted phase-1 to %d/%d runtime-related callees',
            len(phase1_callee_order),
            len(callee_order),
        )
    elif observed_runtime_seen:
        _LOGGER.info(
            'CSE: keeping all %d phase-1 callees reachable from root; observed runtime calls only relax skip heuristics',
            len(phase1_callee_order),
        )

    use_summary_cache = online_autoreuse_mode or reuse_only_mode or not opts.reload

    for ty in phase1_callee_order:
        name = _ty_to_name(smir_info, ty)
        if name is None:
            _LOGGER.debug(f'CSE: skipping Ty({ty}) — cannot resolve name')
            continue

        if not _has_body(smir_info, ty):
            _LOGGER.debug(f'CSE: skipping {name} — no MIR body (intrinsic or extern)')
            result.skipped[name] = 'no MIR body'
            continue

        skip_reason = (
            None if int(ty) in observed_runtime_promoted else _should_skip_cse_summary(name, start_symbol=start_name)
        )
        if skip_reason is not None:
            _LOGGER.debug(f'CSE: skipping {name} — {skip_reason}')
            result.skipped[name] = skip_reason
            result.callee_results[name] = CalleeResult(skipped_reason=skip_reason)
            continue

        safe_name = _sanitize_filename(name)
        summary_path = summary_dir / f'{safe_name}.json'
        frontier_summary_path = summary_dir / f'{safe_name}.frontier.json'
        skip_marker_path = summary_dir / f'{safe_name}.skip.json'

        # Check cache
        if summary_path.exists() and use_summary_cache:
            print(f'[CSE] {name}: using cached summary {summary_path}')
            result.summaries[name] = summary_path
            result.exported_modules[name] = summary_path
            result.summary_times[name] = 0.0
            result.callee_results[name] = CalleeResult(
                summary_path=summary_path,
                module_path=summary_path,
                cached=True,
                passed=True,
                summary_kind='return',
            )
            continue
        if frontier_summary_path.exists() and use_summary_cache:
            print(f'[CSE] {name}: using cached frontier summary {frontier_summary_path}')
            cached_prove_time = 0.0
            try:
                frontier_data = json.loads(frontier_summary_path.read_text())
                cached_prove_time = float(frontier_data.get('prove_time', 0.0))
            except (json.JSONDecodeError, ValueError, TypeError):
                pass
            summary_rule_module_path = summary_dir / f'{safe_name}.summary-rules.json'
            result.summaries[name] = frontier_summary_path
            if summary_rule_module_path.exists():
                result.exported_modules[name] = summary_rule_module_path
            result.summary_times[name] = cached_prove_time
            result.callee_results[name] = CalleeResult(
                summary_path=frontier_summary_path,
                module_path=summary_rule_module_path if summary_rule_module_path.exists() else None,
                cached=True,
                passed=False,
                prove_time=cached_prove_time,
                summary_kind='frontier',
            )
            continue
        cached_skip_reason = _read_skip_marker(skip_marker_path) if use_summary_cache else None
        if cached_skip_reason is not None:
            print(f'[CSE] {name}: using cached skip ({cached_skip_reason})')
            result.skipped[name] = cached_skip_reason
            result.callee_results[name] = CalleeResult(
                cached=True,
                skipped_reason=cached_skip_reason,
            )
            continue
        if reuse_only_mode:
            result.skipped[name] = 'reuse_only_missing_cache'
            result.callee_results[name] = CalleeResult(skipped_reason='reuse_only_missing_cache')
            continue

        # Check if the function is provable (exists in function_tys)
        if name not in smir_info.function_tys:
            _LOGGER.debug(f'CSE: skipping {name} — not in function_tys')
            result.skipped[name] = 'not in function_tys'
            continue

        if online_autoreuse_mode:
            _LOGGER.debug('CSE: deferring uncached callee %s to runtime online generation', name)
            continue

        _prove_callee_summary(
            ty=ty,
            name=name,
            opts=opts,
            smir_info=smir_info,
            main_smir=main_smir,
            summary_dir=summary_dir,
            result=result,
        )

    # Phase 2: Prove the main target with cached callee proofs.
    #
    # The K-module summaries are still exported for inspection/debugging, but the
    # fast path should use KMIRCSESemantics directly. The old control flow only
    # enabled custom_step as a fallback after a normal proof had already passed,
    # which meant reuse timings never reflected actual CSE interception.
    all_summary_paths = [p for p in result.exported_modules.values() if p.exists()]
    user_modules = list(opts.add_modules)

    if generate_only_mode:
        print(f'[CSE] Summary-generation-only mode active, skipping main proof for {start_name}', flush=True)
        result_path = (opts.proof_dir / 'cse_result.json') if opts.proof_dir is not None else (summary_dir / 'cse_result.json')
        result.write_json(result_path)
        return result

    # Build callee_proofs map: function Ty -> APRProof (for CSE semantics)
    callee_proofs: dict[int, APRProof] = {}
    dynamic_summary_names: set[str] = set()
    for callee_name, detail in result.callee_results.items():
        if not detail.summarized:
            continue
        # Load the callee proof if it exists
        callee_proof_dir_path = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
        # Also check summary_dir/callee-proofs as fallback (for reuse-only mode)
        summary_callee_proof_dir = summary_dir / 'callee-proofs'
        if callee_proof_dir_path or summary_callee_proof_dir.exists():
            import hashlib as _hashlib

            raw_label = f'{opts.rs_file.stem}.{callee_name}'
            callee_label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
            if len(callee_label) > 200:
                digest = _hashlib.sha256(raw_label.encode()).hexdigest()[:12]
                callee_label = callee_label[:200] + '_' + digest
            # Try local proof_dir first, then summary_dir/callee-proofs as fallback
            effective_proof_dir = None
            if callee_proof_dir_path and APRProof.proof_data_exists(callee_label, callee_proof_dir_path):
                effective_proof_dir = callee_proof_dir_path
            elif summary_callee_proof_dir.exists() and APRProof.proof_data_exists(callee_label, summary_callee_proof_dir):
                effective_proof_dir = summary_callee_proof_dir
            if effective_proof_dir is not None:
                callee_proof = APRProof.read_proof_data(effective_proof_dir, callee_label)
                if detail.summary_kind == 'frontier' and detail.summary_path is not None:
                    frontier_node_ids = _load_frontier_summary_node_ids(detail.summary_path)
                    if frontier_node_ids:
                        setattr(callee_proof, '_cse_frontier_node_ids', tuple(frontier_node_ids))
                if detail.summary_kind == 'frontier' or ((online_autoreuse_mode or reuse_only_mode) and detail.summary_kind == 'return'):
                    if callee_name in smir_info.function_tys:
                        func_ty = smir_info.function_tys[callee_name]
                        callee_proofs[func_ty] = callee_proof
                        dynamic_summary_names.add(callee_name)
                        _LOGGER.info(
                            'CSE: loaded %s callee proof for %s (ty=%s)',
                            detail.summary_kind or 'dynamic',
                            callee_name,
                            func_ty,
                        )

    online_generation_attempted_tys: set[int] = set()

    def _online_callee_prover(func_ty: int, observed_cterm: CTerm) -> APRProof | None:
        if not online_autoreuse_mode:
            return None
        if func_ty == int(root_ty):
            return None
        if func_ty in online_generation_attempted_tys:
            return None
        online_generation_attempted_tys.add(func_ty)
        ty = Ty(func_ty)
        name = _ty_to_name(smir_info, ty)
        if name is None:
            return None
        if not _has_body(smir_info, ty):
            result.skipped[name] = 'no MIR body'
            result.callee_results[name] = CalleeResult(skipped_reason='no MIR body')
            return None
        if name.rsplit('::', 1)[-1].startswith('cheatcode_'):
            result.skipped[name] = 'symbolic cheatcode helper'
            result.callee_results[name] = CalleeResult(skipped_reason='symbolic cheatcode helper')
            return None
        skip_reason = _should_skip_cse_summary(name, start_symbol=start_name)
        if skip_reason is not None:
            result.skipped[name] = skip_reason
            result.callee_results[name] = CalleeResult(skipped_reason=skip_reason)
            return None
        detail = result.callee_results.get(name)
        if detail is not None and detail.summarized:
            safe_name = _sanitize_filename(name)
            callee_proof_dir_path = opts.proof_dir / 'cse-callee-proofs' if opts.proof_dir else None
            if callee_proof_dir_path:
                import hashlib as _hashlib

                raw_label = f'{opts.rs_file.stem}.{name}'
                callee_label = ''.join(c if c.isalnum() or c in '._-' else '_' for c in raw_label)
                if len(callee_label) > 200:
                    digest = _hashlib.sha256(raw_label.encode()).hexdigest()[:12]
                    callee_label = callee_label[:200] + '_' + digest
                if APRProof.proof_data_exists(callee_label, callee_proof_dir_path):
                    return APRProof.read_proof_data(callee_proof_dir_path, callee_label)
        proof = _prove_callee_summary(
            ty=ty,
            name=name,
            opts=opts,
            smir_info=smir_info,
            main_smir=main_smir,
            summary_dir=summary_dir,
            result=result,
            observed_call_cterm=observed_cterm,
        )
        detail = result.callee_results.get(name)
        if detail is not None and detail.summarized:
            detail.generated_online = True
        if proof is not None and name not in result.online_generated_summaries:
            result.online_generated_summaries.append(name)
        return proof

    # Determine whether to use dynamic (Python-level) interception or compiled rules.
    # When summary-rules.json modules are available, prefer compiled rules (no overhead).
    has_compiled_rules = bool(all_summary_paths)
    use_dynamic_cse = (bool(callee_proofs) or learn_observed_calls) and not (reuse_only_mode and has_compiled_rules)
    observed_runtime_names = [name for func_ty in observed_runtime_seen if (name := _ty_to_name(smir_info, Ty(func_ty))) is not None]
    dynamic_break_targets = {*opts.break_on_function, *dynamic_summary_names, *observed_runtime_names}
    if observe_only_mode:
        dynamic_break_targets.update(
            name for ty in callee_order if (name := _ty_to_name(smir_info, ty)) is not None
        )
    if online_autoreuse_mode:
        dynamic_break_targets.update(
            name for ty in callee_order if (name := _ty_to_name(smir_info, ty)) is not None
        )
    if reuse_only_mode and has_compiled_rules:
        # In reuse-only mode with compiled summary rules, no break targets needed.
        # The booster applies rules natively during execution.
        dynamic_break_targets = set(opts.break_on_function)
    dynamic_break_on_function = sorted(dynamic_break_targets)
    # Keep exported summary modules available even when dynamic CSE is enabled.
    # The rule-level summaries can still help simplification around the dynamic
    # fast path, and empirical runs are worse without them.
    main_extra_modules = user_modules + all_summary_paths

    print(
        f'[CSE] Proving {start_name} with {len(callee_proofs)} dynamic summaries '
        f'+ {len(all_summary_paths)} exported summaries'
        f'{" (observe-only)" if observe_only_mode else ""}'
        f'{" (autoreuse)" if online_autoreuse_mode else ""}'
        f'{" (reuse-only)" if reuse_only_mode else ""}...',
        flush=True,
    )
    t0 = time.time()

    # Build the proof with CSE semantics for dynamic interception
    from ._prove import apr_proof_from_smir

    main_smir = smir_info.reduce_to(start_name)
    kmir = KMIR.from_kompiled_kore(
        main_smir,
        target_dir=opts.proof_dir / f'{opts.rs_file.stem}.{start_name}' if opts.proof_dir else Path('/tmp/cse-main'),
        extra_modules=main_extra_modules or None,
        bug_report=opts.bug_report,
        symbolic=True,
        haskell_target=opts.haskell_target,
        llvm_lib_target=opts.llvm_lib_target,
        break_on_function=dynamic_break_on_function or None,
    )

    final_proof = apr_proof_from_smir(
        kmir,
        f'{opts.rs_file.stem}.{start_name}',
        main_smir,
        start_symbol=start_name,
        proof_dir=opts.proof_dir,
    )
    if opts.proof_dir:
        main_smir.dump(opts.proof_dir / final_proof.id / 'smir.json')

    if use_dynamic_cse:
        from .kmir import KMIRCSESemantics
        from ._prove import _cut_point_rules

        # Use CSE semantics with callee proofs for dynamic function call interception
        cse_semantics = KMIRCSESemantics(
            callee_proofs=callee_proofs,
            terminate_on_thunk=opts.terminate_on_thunk,
            summary_dir=summary_dir,
            learn_observed_calls=learn_observed_calls,
            online_callee_prover=_online_callee_prover if online_autoreuse_mode else None,
            dynamic_return_summaries=online_autoreuse_mode,
        )

        from pyk.kcfg.explore import KCFGExplore
        from pyk.proof.reachability import APRProver

        with kmir_cterm_symbolic(
            kmir.definition,
            kmir.definition_dir,
            id=final_proof.id,
            llvm_definition_dir=kmir.llvm_library_dir,
            bug_report=kmir.bug_report,
            simplify_each=30,
        ) as cts:
            kcfg_explore = KCFGExplore(cts, kcfg_semantics=cse_semantics)
            cse_cut_points = _cut_point_rules(
                break_on_calls=opts.break_on_calls,
                break_on_function_calls=opts.break_on_function_calls,
                break_on_intrinsic_calls=opts.break_on_intrinsic_calls,
                break_on_thunk=opts.break_on_thunk or opts.terminate_on_thunk,
                break_every_statement=opts.break_every_statement,
                break_on_terminator_goto=opts.break_on_terminator_goto,
                break_on_terminator_switch_int=opts.break_on_terminator_switch_int,
                break_on_terminator_return=opts.break_on_terminator_return,
                break_on_terminator_call=opts.break_on_terminator_call,
                break_on_terminator_assert=opts.break_on_terminator_assert,
                break_on_terminator_drop=opts.break_on_terminator_drop,
                break_on_terminator_unreachable=opts.break_on_terminator_unreachable,
                break_every_terminator=opts.break_every_terminator,
                break_every_step=opts.break_every_step,
                break_on_function=dynamic_break_on_function,
            )
            prover = APRProver(
                kcfg_explore,
                execute_depth=opts.max_depth,
                cut_point_rules=cse_cut_points,
            )
            started_at = time.perf_counter()
            try:
                prover.advance_proof(
                    final_proof,
                    max_iterations=opts.max_iterations or 1000,
                    fail_fast=opts.fail_fast,
                    maintenance_rate=opts.maintenance_rate,
                )
            finally:
                final_proof.add_exec_time(time.perf_counter() - started_at)
                final_proof.write_proof_data()
    else:
        # Compiled-rules path: summary rules are baked into the K definition
        # via extra_modules. The booster applies them natively — no cut-points,
        # no custom_step, no Python overhead.
        from ._prove import _prove_sequential
        from .kmir import KMIRSemantics

        _LOGGER.info(
            'CSE: using compiled-rules path with %d exported summary modules',
            len(all_summary_paths),
        )
        _prove_sequential(
            kmir,
            final_proof,
            opts=opts,
            label=final_proof.id,
            cut_point_rules=[],
        )

    if learn_observed_calls:
        _backfill_observed_calls_from_kcfg(
            summary_dir,
            final_proof,
            interesting_tys={int(ty) for ty in callee_order},
        )
        observed_runtime_counts = _load_observed_runtime_callee_counts(summary_dir)
        observed_runtime_seen = set(observed_runtime_counts)
        result.observed_runtime_callees = sorted(observed_runtime_seen)
    if use_dynamic_cse:
        result.dynamic_summary_hits = {
            name: count
            for func_ty, count in cse_semantics.summary_hit_counts.items()
            if (name := _ty_to_name(smir_info, Ty(func_ty))) is not None
        }
        for func_ty in cse_semantics.online_generated_tys:
            if (name := _ty_to_name(smir_info, Ty(func_ty))) is not None and name not in result.online_generated_summaries:
                result.online_generated_summaries.append(name)

    result.final_prove_time = time.time() - t0
    result.final_proof = final_proof
    result.final_proof_exec_time = final_proof.exec_time
    print(f'[CSE] {start_name}: {"PASSED" if final_proof.passed else "FAILED"} in {result.final_prove_time:.1f}s')

    result_path = (opts.proof_dir / 'cse_result.json') if opts.proof_dir is not None else (summary_dir / 'cse_result.json')
    result.write_json(result_path)

    return result
