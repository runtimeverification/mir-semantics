from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.cterm.symbolic import CTermSymbolic
from pyk.kast.inner import KApply, KLabel, KSequence, KSort, KToken, KVariable
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kore.rpc import BoosterServer, KoreClient, KoreExecLogFormat
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.show import APRProofNodePrinter

from .kast import ConcreteMode, RandomMode, make_call_config
from .kparse import KParse
from .parse.parser import Parser
from .smir import SMIRInfo

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Final

    from pyk.cterm import CTermSymbolic
    from pyk.cterm.show import CTermShow
    from pyk.kast.inner import KInner
    from pyk.kcfg import KCFG
    from pyk.kcfg.kcfg import KCFGExtendResult
    from pyk.kore.syntax import Pattern
    from pyk.proof.reachability import APRProof
    from pyk.utils import BugReport

    from .options import DisplayOpts, ProveOpts


_LOGGER: Final = logging.getLogger(__name__)

_BOOSTER_LOG_CONTEXT_PRESETS: dict[str, list[str]] = {
    'Aborts': [
        'request*,booster>rewrite*,detail.',
        'request*,booster>rewrite*,match|definedness|constraint,abort.',
        'request*,proxy.',
        'request*,proxy,abort.',
        'request*,booster>failure,abort',
    ],
    'Rewrite': [
        'request*,booster|kore>rewrite*,success|failure|abort|detail',
        'request*,booster|kore>rewrite*,match|definedness|constraint,failure|abort',
    ],
}


def _collect_variable_names(term: 'KInner') -> set[str]:
    names: set[str] = set()

    def _visit(node: 'KInner') -> None:
        if isinstance(node, KVariable):
            names.add(node.name)
        for child in node.terms:
            _visit(child)

    _visit(term)
    return names


def _freshen_quantifier_binders(term: 'KInner') -> 'KInner':
    used_names = _collect_variable_names(term)
    counter = 0

    def _fresh_name(base: str) -> str:
        nonlocal counter
        while True:
            candidate = f'{base}__kmir_q_{counter}'
            counter += 1
            if candidate not in used_names:
                used_names.add(candidate)
                return candidate

    def _visit(node: 'KInner', env: dict[str, KVariable]) -> 'KInner':
        if isinstance(node, KVariable):
            replacement = env.get(node.name)
            return replacement if replacement is not None else node

        if (
            isinstance(node, KApply)
            and node.label.name in ('#Exists', '#Forall')
            and len(node.args) == 2
            and isinstance(node.args[0], KVariable)
        ):
            binder = node.args[0]
            fresh_binder = binder.let(name=_fresh_name(binder.name))
            scoped_env = dict(env)
            scoped_env[binder.name] = fresh_binder
            fresh_body = _visit(node.args[1], scoped_env)
            return node.let(args=(fresh_binder, fresh_body))

        return node.map_inner(lambda child: _visit(child, env))

    return _visit(term, {})


class KMIRCTermSymbolic(CTermSymbolic):
    def kast_to_kore(self, kinner: 'KInner') -> 'Pattern':
        return super().kast_to_kore(_freshen_quantifier_binders(kinner))


def _parse_csv_env(name: str) -> list[str]:
    raw = os.getenv(name, '')
    return [item.strip() for item in raw.split(',') if item.strip()]


def _parse_context_env(name: str) -> list[str]:
    raw = os.getenv(name, '')
    if not raw:
        return []
    lines = raw.replace('\n', ';').split(';')
    return [item.strip() for item in lines if item.strip()]


def _parse_kore_log_format(raw: str | None) -> KoreExecLogFormat:
    if raw is None or not raw.strip():
        return KoreExecLogFormat.STANDARD
    normalized = raw.strip().lower()
    for candidate in KoreExecLogFormat:
        if candidate.value == normalized:
            return candidate
    _LOGGER.warning('Unknown KMIR_KORE_RPC_LOG_FORMAT=%s, defaulting to standard', raw)
    return KoreExecLogFormat.STANDARD


def kore_server_logging_args(label: str | None = None) -> dict[str, object]:
    log_path_raw = os.getenv('KMIR_KORE_RPC_LOG')
    if not log_path_raw:
        return {}

    log_path = Path(log_path_raw.replace('{label}', label or 'kmir'))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        'log_axioms_file': log_path,
        'haskell_log_format': _parse_kore_log_format(os.getenv('KMIR_KORE_RPC_LOG_FORMAT')),
        'haskell_log_entries': _parse_csv_env('KMIR_KORE_RPC_LOG_ENTRIES'),
    }


def booster_server_logging_args() -> dict[str, object]:
    entries = _parse_csv_env('KMIR_BOOSTER_LOG_ENTRIES')
    contexts = _parse_context_env('KMIR_BOOSTER_LOG_CONTEXTS')
    not_contexts = _parse_context_env('KMIR_BOOSTER_NOT_LOG_CONTEXTS')
    for entry in entries:
        contexts.extend(_BOOSTER_LOG_CONTEXT_PRESETS.get(entry, [entry]))
    if not contexts and not not_contexts:
        return {}
    return {
        'log_context': contexts,
        'not_log_context': not_contexts,
    }


@contextmanager
def kmir_cterm_symbolic(
    definition: 'KDefinition',
    definition_dir: Path,
    *,
    id: str | None = None,
    llvm_definition_dir: Path | None = None,
    bug_report: 'BugReport | None' = None,
    simplify_each: int | None = None,
    log_succ_rewrites: bool = True,
    log_fail_rewrites: bool = False,
) -> Iterator['CTermSymbolic']:
    booster_logging = booster_server_logging_args()
    if llvm_definition_dir is not None and booster_logging:
        with BoosterServer(
            {
                'kompiled_dir': definition_dir,
                'llvm_kompiled_dir': llvm_definition_dir,
                'module_name': definition.main_module_name,
                'bug_report': bug_report,
                'simplify_each': simplify_each,
                **booster_logging,
            }
        ) as server:
            with KoreClient('localhost', server.port, bug_report=bug_report, bug_report_id=id) as client:
                yield KMIRCTermSymbolic(
                    client,
                    definition,
                    log_succ_rewrites=log_succ_rewrites,
                    log_fail_rewrites=log_fail_rewrites,
                )
        return

    logging_args = kore_server_logging_args(id)
    with cterm_symbolic(
        definition,
        definition_dir,
        id=id,
        llvm_definition_dir=llvm_definition_dir,
        bug_report=bug_report,
        simplify_each=simplify_each,
        log_succ_rewrites=log_succ_rewrites,
        log_fail_rewrites=log_fail_rewrites,
        **logging_args,
    ) as cts:
        yield KMIRCTermSymbolic(
            cts._kore_client,
            definition,
            log_succ_rewrites=log_succ_rewrites,
            log_fail_rewrites=log_fail_rewrites,
        )


class KMIR(KProve, KRun, KParse):
    llvm_library_dir: Path | None
    bug_report: BugReport | None

    def __init__(
        self, definition_dir: Path, llvm_library_dir: Path | None = None, bug_report: Path | None = None
    ) -> None:
        self.bug_report = bug_report_arg(bug_report) if bug_report is not None else None
        KProve.__init__(self, definition_dir, bug_report=self.bug_report)
        KRun.__init__(self, definition_dir, bug_report=self.bug_report)
        KParse.__init__(self, definition_dir)
        self.llvm_library_dir = llvm_library_dir

    @staticmethod
    def from_kompiled_kore(
        smir_info: SMIRInfo,
        target_dir: Path,
        *,
        extra_modules: list[Path] | None = None,
        bug_report: Path | None = None,
        symbolic: bool = True,
        llvm_target: str | None = None,
        llvm_lib_target: str | None = None,
        haskell_target: str | None = None,
        break_on_function: list[str] | None = None,
    ) -> KMIR:
        from .kompile import kompile_smir

        kompiled_smir = kompile_smir(
            smir_info=smir_info,
            target_dir=target_dir,
            extra_modules=extra_modules,
            bug_report=bug_report,
            symbolic=symbolic,
            llvm_target=llvm_target,
            llvm_lib_target=llvm_lib_target,
            haskell_target=haskell_target,
            break_on_function=break_on_function,
        )
        return kompiled_smir.create_kmir(bug_report_file=bug_report)

    class Symbols:
        END_PROGRAM: Final = KApply('#EndProgram_KMIR-CONTROL-FLOW_KItem')
        THUNK: Final = KLabel('thunk(_)_RT-DATA_Value_Evaluation')

    @cached_property
    def parser(self) -> Parser:
        return Parser(self.definition)

    @contextmanager
    def kcfg_explore(self, label: str | None = None, terminate_on_thunk: bool = False) -> Iterator[KCFGExplore]:
        with kmir_cterm_symbolic(
            self.definition,
            self.definition_dir,
            id=label if self.bug_report is not None else None,  # NB bug report arg.s must be coherent
            llvm_definition_dir=self.llvm_library_dir,
            bug_report=self.bug_report,
            simplify_each=30,
        ) as cts:
            yield KCFGExplore(cts, kcfg_semantics=KMIRSemantics(terminate_on_thunk=terminate_on_thunk))

    def run_smir(
        self,
        smir_info: SMIRInfo,
        *,
        start_symbol: str = 'main',
        depth: int | None = None,
        seed: int | None = None,
    ) -> Pattern:
        smir_info = smir_info.reduce_to(start_symbol)
        mode = RandomMode(seed) if seed is not None else ConcreteMode()
        init_config, _ = make_call_config(
            self.definition,
            smir_info=smir_info,
            start_symbol=start_symbol,
            mode=mode,
        )
        init_kore = self.kast_to_kore(init_config, KSort('GeneratedTopCell'))
        result = self.run_pattern(init_kore, depth=depth)
        return result

    @staticmethod
    def prove_program(opts: ProveOpts) -> APRProof:
        from ._prove import prove

        return prove(opts)


class KMIRSemantics(DefaultSemantics):
    terminate_on_thunk: bool

    def __init__(self, terminate_on_thunk: bool = False) -> None:
        self.terminate_on_thunk = terminate_on_thunk

    def is_terminal(self, cterm: CTerm) -> bool:
        k_cell = cterm.cell('K_CELL')

        if self.terminate_on_thunk:  # terminate on `thunk ( ... )` rule
            match k_cell:
                case KApply(label, _) | KSequence((KApply(label, _), *_)) if label == KMIR.Symbols.THUNK:
                    return True

        # <k> #EndProgram </k>
        if k_cell == KMIR.Symbols.END_PROGRAM:
            return True
        elif type(k_cell) is KSequence:
            # <k> #EndProgram ~> .K </k>
            if k_cell.arity == 1 and k_cell[0] == KMIR.Symbols.END_PROGRAM:
                return True
        return False


class KMIRCSESemantics(KMIRSemantics):
    """Extended semantics with Compositional Symbolic Execution support.

    When encountering a function call for which we have a cached proof,
    constructs the post-return configuration directly instead of stepping
    through the callee's execution. Handles multi-branch callee proofs
    by producing NDBranch results.
    """

    _callee_proofs: dict[int, APRProof]  # function Ty -> completed proof

    def __init__(
        self,
        callee_proofs: dict[int, APRProof] | None = None,
        terminate_on_thunk: bool = False,
        *,
        summary_dir: Path | None = None,
        learn_observed_calls: bool = False,
        online_callee_prover=None,
        dynamic_return_summaries: bool = False,
    ) -> None:
        super().__init__(terminate_on_thunk=terminate_on_thunk)
        self._callee_proofs = callee_proofs or {}
        self._failed_tys: set[int] = set()  # Track function Tys where CSE failed
        self._summary_dir = summary_dir
        self._learn_observed_calls = learn_observed_calls
        self._online_callee_prover = online_callee_prover
        self._learning_tys: set[int] = set()
        self._dynamic_return_summaries = dynamic_return_summaries
        self._summary_hit_counts: dict[int, int] = {}
        self._online_generated_tys: set[int] = set()

    @property
    def summary_hit_counts(self) -> dict[int, int]:
        return dict(self._summary_hit_counts)

    @property
    def online_generated_tys(self) -> set[int]:
        return set(self._online_generated_tys)

    @staticmethod
    def _sanitize_observation_value(value: object) -> object:
        if isinstance(value, dict):
            return {str(key): KMIRCSESemantics._sanitize_observation_value(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [KMIRCSESemantics._sanitize_observation_value(item) for item in value]
        return value

    def _observed_calls_dir(self) -> Path | None:
        summary_dir = self._summary_dir
        if summary_dir is None:
            env_summary_dir = os.getenv('KMIR_CSE_SUMMARY_DIR')
            if env_summary_dir:
                summary_dir = Path(env_summary_dir)
        if summary_dir is None:
            return None
        return summary_dir / 'observed-calls'

    def _record_observed_call(
        self,
        *,
        func_ty: int,
        args_operand: KInner,
        cterm: CTerm,
        outcome: str,
        target: KInner | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        if not self._learn_observed_calls:
            return
        observed_dir = self._observed_calls_dir()
        if observed_dir is None:
            return
        observed_dir.mkdir(parents=True, exist_ok=True)
        observed_path = observed_dir / f'ty-{func_ty}.json'
        cterm_path = observed_dir / f'ty-{func_ty}.cterm.json'
        existing: dict[str, object] = {}
        if observed_path.exists():
            try:
                loaded = json.loads(observed_path.read_text())
            except json.JSONDecodeError:
                loaded = None
            if isinstance(loaded, dict):
                existing = loaded
        count = int(existing.get('count', 0)) + 1
        outcomes = existing.get('outcomes', [])
        if not isinstance(outcomes, list):
            outcomes = []
        outcomes.append(outcome)
        payload: dict[str, object] = {
            'func_ty': func_ty,
            'count': count,
            'outcomes': outcomes[-20:],
            'latest_outcome': outcome,
            'arg_local_indices': self._extract_arg_local_indices(args_operand),
            'caller_var_names': sorted(self._cterm_var_names(cterm))[:50],
            'k_cell_head': cterm.cell('K_CELL').label.name if isinstance(cterm.cell('K_CELL'), KApply) else type(cterm.cell('K_CELL')).__name__,
            'target': str(target)[:400] if target is not None else None,
        }
        if details:
            payload['details'] = self._sanitize_observation_value(details)
        payload['cterm_path'] = str(cterm_path)
        observed_path.write_text(json.dumps(payload, indent=2))
        cterm_path.write_text(json.dumps(cterm.to_dict(), indent=2))

    def _extract_call_info(self, k_cell: KInner) -> tuple[int, KInner, KInner, KInner] | None:
        """Extract (function_ty, args_operand, dest, target) from a call.

        Matches two patterns:
        1. #execTerminator(terminator(terminatorKindCall(func, args, dest, target, unwind), span))
        2. #execTerminatorCall(Ty, FUNC, ARGS, DEST, TARGET, UNWIND, SPAN) ~> _
           (after call dispatch, at termCallFunction cut-point)
        """
        term = k_cell
        if isinstance(term, KSequence) and term.items:
            term = term.items[0]

        if not isinstance(term, KApply):
            return None

        # Pattern 1: #execTerminator(terminator(terminatorKindCall(...), span))
        if term.label.name == '#execTerminator(_)_KMIR-CONTROL-FLOW_KItem_Terminator':
            terminator = term.args[0]
            if not isinstance(terminator, KApply) or len(terminator.args) < 1:
                return None
            kind = terminator.args[0]
            if not isinstance(kind, KApply) or kind.label.name != 'TerminatorKind::Call':
                return None
            func_operand, args_operand, dest, target, _unwind = kind.args
            func_ty = self._extract_func_ty(func_operand)
            if func_ty is None:
                return None
            return (func_ty, args_operand, dest, target)

        # Pattern 2: #execTerminatorCall(Ty, FUNC, ARGS, DEST, TARGET, UNWIND, SPAN)
        if '#execTerminatorCall' in term.label.name and len(term.args) >= 5:
            ty_term = term.args[0]
            args_operand = term.args[2]
            dest = term.args[3]
            target = term.args[4]
            if isinstance(ty_term, KApply) and ty_term.label.name == 'ty' and isinstance(ty_term.args[0], KToken):
                return (int(ty_term.args[0].token), args_operand, dest, target)

        return None

    @staticmethod
    def _extract_func_ty(func_operand: KInner) -> int | None:
        """Extract the function Ty integer from a function operand."""
        try:
            if not isinstance(func_operand, KApply):
                return None
            const_operand = func_operand.args[0]
            if not isinstance(const_operand, KApply):
                return None
            mir_const = const_operand.args[2]
            if not isinstance(mir_const, KApply):
                return None
            ty_term = mir_const.args[1]
            if not isinstance(ty_term, KApply) or ty_term.label.name != 'ty':
                return None
            ty_token = ty_term.args[0]
            if not isinstance(ty_token, KToken):
                return None
            return int(ty_token.token)
        except (IndexError, ValueError, TypeError):
            return None

    def can_make_custom_step(self, c: CTerm) -> bool:
        k_cell = c.cell('K_CELL')
        call_info = self._extract_call_info(k_cell)
        if call_info is None:
            return False
        func_ty = call_info[0]
        _func_ty, args_operand, _dest, _target = call_info
        # Only intercept functions that are known to match (not in failed set)
        # AND have Operand::Copy/Move args (not Operand::Constant which we can't match)
        indices = self._extract_arg_local_indices(args_operand)
        if not any(idx >= 0 for idx in indices):
            if func_ty in self._callee_proofs and self._online_callee_prover is None:
                self._failed_tys.add(func_ty)
            return self._online_callee_prover is not None and func_ty not in self._failed_tys
        if func_ty not in self._callee_proofs and self._online_callee_prover is None:
            return False
        if func_ty in self._failed_tys:
            return False
        return True

    def _build_arg_substitution(
        self, caller_cterm: CTerm, args_operand: KInner, callee_proof: APRProof
    ) -> dict[str, KInner]:
        """Build substitution mapping callee symbolic vars to caller's actual values.

        Strategy: for each callee symbolic variable, find its sort, then search
        caller locals for a value of matching sort. Unwraps Value constructors
        (BoolVal→Bool, Integer→Int, Range→List) for sort-correct substitution.
        Also scans all caller locals to find pointee data for reference args.
        """
        from pyk.kast.inner import KVariable

        subst: dict[str, KInner] = {}

        callee_init = callee_proof.kcfg.node(callee_proof.init)
        callee_locals = callee_init.cterm.cell('LOCALS_CELL')
        callee_arg_items = self._list_items(callee_locals)

        caller_locals = caller_cterm.cell('LOCALS_CELL')
        caller_local_items = self._list_items(caller_locals)

        # Extract argument values from call operands
        actual_arg_values = self._extract_arg_values(args_operand, caller_local_items)

        # Phase 1: Map callee arg locals to caller operand values
        for i, caller_value in enumerate(actual_arg_values):
            callee_local_idx = i + 1
            if callee_local_idx >= len(callee_arg_items) or caller_value is None:
                continue
            callee_typed_val = callee_arg_items[callee_local_idx]
            for var_name, var_node in self._extract_free_vars(callee_typed_val):
                sort_name = var_node.sort.name if isinstance(var_node, KVariable) and var_node.sort else None
                unwrapped = self._unwrap_value_for_sort(caller_value, sort_name)
                # Only substitute if the unwrapped value has matching sort
                if self._sort_matches(unwrapped, sort_name):
                    subst[var_name] = unwrapped

        # Phase 2: For remaining vars (e.g., pointee data in separate locals),
        # scan ALL caller locals for matching-sort values
        all_callee_vars: dict[str, str | None] = {}
        for item in callee_arg_items:
            for vname, vnode in self._extract_free_vars(item):
                if vname not in subst:
                    sort_name = vnode.sort.name if isinstance(vnode, KVariable) and vnode.sort else None
                    all_callee_vars[vname] = sort_name

        for var_name, sort_name in all_callee_vars.items():
            if var_name in subst:
                continue
            if sort_name is None:
                continue  # Can't match without known sort
            for item in caller_local_items:
                caller_val = self._extract_value_from_typed(item)
                if caller_val is None:
                    continue
                unwrapped = self._unwrap_value_for_sort(caller_val, sort_name)
                if self._sort_matches(unwrapped, sort_name):
                    subst[var_name] = unwrapped
                    break

        return subst

    @staticmethod
    def _sort_matches(term: KInner, sort_name: str | None) -> bool:
        """Check if a term matches the expected sort (or any K sort if sort_name is None)."""
        if isinstance(term, KToken):
            if sort_name is None:
                return term.sort.name in ('Int', 'Bool', 'String')
            return term.sort.name == sort_name
        if isinstance(term, KApply):
            label = term.label.name
            if sort_name == 'List' or (sort_name is None and ('List' in label or 'ListItem' in label)):
                return 'List' in label or 'ListItem' in label
        return False

    def _extract_arg_values(self, args_operand: KInner, caller_locals: list[KInner]) -> list[KInner | None]:
        """Extract actual argument values from call operands.

        Handles:
        - Operand::Copy(place(local(I))) → value from caller's locals[I]
        - Operand::Move(place(local(I))) → value from caller's locals[I]
        - Operand::Constant(constOperand(..., mirConst(Allocated(alloc), ty, id))) → decoded constant
        """
        operands = self._flatten_operands(args_operand)
        values: list[KInner | None] = []

        for op in operands:
            if not isinstance(op, KApply):
                values.append(None)
                continue

            if op.label.name in ('Operand::Copy', 'Operand::Move'):
                # Reference to caller's local
                place = op.args[0]
                if isinstance(place, KApply) and place.label.name == 'place':
                    local = place.args[0]
                    if isinstance(local, KApply) and isinstance(local.args[0], KToken):
                        idx = int(local.args[0].token)
                        if idx < len(caller_locals):
                            val = self._extract_value_from_typed(caller_locals[idx])
                            values.append(val)
                            continue
                values.append(None)

            elif op.label.name == 'Operand::Constant':
                # Inline constant — try to decode
                decoded = self._decode_constant_operand(op)
                values.append(decoded)

            else:
                values.append(None)

        return values

    @staticmethod
    def _flatten_operands(args_operand: KInner) -> list[KInner]:
        """Flatten Operands::append chain into a list of individual operands."""
        result: list[KInner] = []
        current = args_operand
        while isinstance(current, KApply):
            if 'append' in current.label.name.lower() or current.label.name == 'Operands::append':
                if len(current.args) >= 2:
                    result.append(current.args[0])
                    current = current.args[1]
                else:
                    break
            elif 'empty' in current.label.name.lower():
                break
            else:
                result.append(current)
                break
        # NOTE: Do NOT reverse. Operands::append(first, append(second, empty))
        # builds left-to-right.  Extracting args[0] from each cons cell
        # yields operands in argument order.
        return result

    @staticmethod
    def _decode_constant_operand(op: KInner) -> KInner | None:
        """Decode a constant operand to a K Value term.

        Handles ConstantKind::Allocated with simple types (bool, small ints).
        """
        try:
            if not isinstance(op, KApply):
                return None
            const_operand = op.args[0]  # constOperand(span, userTy, mirConst)
            if not isinstance(const_operand, KApply):
                return None
            mir_const = const_operand.args[2]  # mirConst(kind, ty, id)
            if not isinstance(mir_const, KApply):
                return None
            kind = mir_const.args[0]  # ConstantKind::Allocated(allocation) or ZeroSized
            if not isinstance(kind, KApply):
                return None

            if kind.label.name == 'ConstantKind::Allocated':
                alloc = kind.args[0]  # allocation(bytes, provenance, align, mutability)
                if not isinstance(alloc, KApply):
                    return None
                bytes_token = alloc.args[0]
                if not isinstance(bytes_token, KToken) or bytes_token.sort.name != 'Bytes':
                    return None

                raw_bytes = bytes_token.token
                # Decode Python bytes literal: b"\x01" etc.
                if raw_bytes.startswith('b"') and raw_bytes.endswith('"'):
                    byte_str = raw_bytes[2:-1]
                    # Decode escape sequences
                    decoded = byte_str.encode('utf-8').decode('unicode_escape').encode('latin-1')
                elif raw_bytes.startswith("b'") and raw_bytes.endswith("'"):
                    byte_str = raw_bytes[2:-1]
                    decoded = byte_str.encode('utf-8').decode('unicode_escape').encode('latin-1')
                else:
                    return None

                # Check the type to determine how to interpret
                ty = mir_const.args[1]
                if isinstance(ty, KApply) and ty.label.name == 'ty' and isinstance(ty.args[0], KToken):
                    # For 1-byte values, try bool decode
                    if len(decoded) == 1:
                        val = decoded[0]
                        # Bool: 0=false, 1=true (ty is usually bool type)
                        return KApply(
                            'Value::BoolVal',
                            (KToken('true' if val != 0 else 'false', KSort('Bool')),),
                        )
            return None
        except (IndexError, ValueError, TypeError):
            return None

    @staticmethod
    def _list_items(list_term: KInner) -> list[KInner]:
        """Extract items from a K List term."""
        items: list[KInner] = []
        current = list_term
        while isinstance(current, KApply):
            if current.label.name == 'ListItem':
                items.append(current.args[0])
                return items
            elif current.label.name == '_List_':
                left, right = current.args
                if isinstance(left, KApply) and left.label.name == 'ListItem':
                    items.append(left.args[0])
                current = right
            else:
                break
        return items

    @staticmethod
    def _extract_arg_local_indices(args_operand: KInner) -> list[int]:
        """Extract local indices from call argument operands.

        Handles the Operands::append chain: append(op1, append(op2, empty)).
        Returns indices in argument order (op1 first, op2 second).
        """
        # First flatten the operand chain
        operands: list[KInner] = []
        current = args_operand
        while isinstance(current, KApply):
            if current.label.name in ('Operand::Copy', 'Operand::Move', 'Operand::Constant'):
                operands.append(current)
                break
            elif 'append' in current.label.name.lower():
                first_arg, rest = current.args
                operands.append(first_arg)
                current = rest
            elif 'empty' in current.label.name.lower():
                break
            else:
                break
        # NOTE: Do NOT reverse. Operands::append(first, append(second, empty))
        # builds left-to-right. Extracting first_arg from each cons cell
        # yields operands in argument order: [first, second, ...].

        # Extract local indices from Move/Copy operands
        indices: list[int] = []
        for op in operands:
            if isinstance(op, KApply) and op.label.name in ('Operand::Copy', 'Operand::Move'):
                place = op.args[0]
                if isinstance(place, KApply) and place.label.name == 'place':
                    local = place.args[0]
                    if isinstance(local, KApply) and local.label.name == 'local':
                        idx_token = local.args[0]
                        if isinstance(idx_token, KToken):
                            indices.append(int(idx_token.token))
                            continue
            indices.append(-1)  # placeholder for non-local operands
        return indices

    @staticmethod
    def _extract_free_vars(term: KInner) -> list[tuple[str, KInner]]:
        """Extract (name, node) pairs for free KVariables in a term."""
        from pyk.kast.inner import KVariable

        result: list[tuple[str, KInner]] = []
        worklist = [term]
        while worklist:
            t = worklist.pop()
            if isinstance(t, KVariable):
                result.append((t.name, t))
            elif isinstance(t, KApply):
                worklist.extend(t.args)
            elif isinstance(t, KSequence):
                worklist.extend(t.items)
        return result

    @classmethod
    def _free_var_names(cls, term: KInner) -> set[str]:
        return {name for name, _node in cls._extract_free_vars(term)}

    @classmethod
    def _cterm_var_names(cls, cterm: CTerm) -> set[str]:
        names = cls._free_var_names(cterm.config)
        for constraint in cterm.constraints:
            names.update(cls._free_var_names(constraint))
        return names

    @staticmethod
    def _extract_value_from_typed(typed_val: KInner) -> KInner | None:
        """Extract the Value from typedValue(Value, Ty, Mut)."""
        if isinstance(typed_val, KApply) and typed_val.label.name == 'typedValue':
            return typed_val.args[0]
        return None

    @staticmethod
    def _unwrap_value_for_sort(value: KInner, target_sort: str | None) -> KInner:
        """Unwrap Value constructors to match the callee variable's sort.

        BoolVal(x:Bool) → x:Bool       (for sort Bool)
        Integer(n:Int, ...) → n:Int     (for sort Int)
        Range(list:List) → list:List    (for sort List)
        Otherwise returns the value as-is.
        """
        if not isinstance(value, KApply):
            return value
        if 'BoolVal' in value.label.name and value.args:
            return value.args[0]
        if 'Integer' in value.label.name and value.args:
            return value.args[0]
        if 'Range' in value.label.name and value.args:
            return value.args[0]
        # For Aggregate, Reference etc: return as-is (sort Value)
        return value

    @staticmethod
    def _extract_return_value(retval_cell: KInner) -> KInner:
        """Extract the Value from return(Value) in RETVAL_CELL."""
        if isinstance(retval_cell, KApply) and 'return' in retval_cell.label.name:
            return retval_cell.args[0]
        return retval_cell

    @staticmethod
    def _extract_boundary_return_value(k_cell: KInner) -> KInner | None:
        if not isinstance(k_cell, KSequence) or len(k_cell.items) < 2:
            return None
        first = k_cell.items[0]
        second = k_cell.items[1]
        if not isinstance(first, KApply) or '#setLocalValue' not in first.label.name:
            return None
        if not isinstance(second, KApply) or '#execBlockIdx' not in second.label.name:
            return None
        return first.args[1]

    @staticmethod
    def _frontier_nodes(callee_proof: APRProof) -> list[KCFG.Node]:
        explicit_frontier_ids = getattr(callee_proof, '_cse_frontier_node_ids', None)
        if explicit_frontier_ids:
            return [callee_proof.kcfg.node(node_id) for node_id in explicit_frontier_ids]
        frontier_nodes = [node for node in callee_proof.kcfg.leaves if node.id != callee_proof.target]
        if frontier_nodes:
            return frontier_nodes
        if callee_proof.init != callee_proof.target:
            return [callee_proof.kcfg.node(callee_proof.init)]
        return []

    @staticmethod
    def _is_end_program_k(k_cell: KInner) -> bool:
        if k_cell == KMIR.Symbols.END_PROGRAM:
            return True
        if type(k_cell) is KSequence and k_cell.arity == 1 and k_cell[0] == KMIR.Symbols.END_PROGRAM:
            return True
        return False

    def custom_step(self, c: CTerm, cs: CTermSymbolic) -> KCFGExtendResult | None:
        """Apply cached callee proof to skip function execution.

        Uses the K backend's implies() to unify the caller's state with the
        callee proof's init state, producing a sort-correct substitution.
        This handles all types (bool, int, reference, aggregate, etc.).
        """
        from pyk.kast.manip import set_cell
        from pyk.kcfg.kcfg import NDBranch, Step

        k_cell = c.cell('K_CELL')
        call_info = self._extract_call_info(k_cell)
        if call_info is None:
            return None

        func_ty, _args_operand, dest, target = call_info
        callee_proof = self._callee_proofs.get(func_ty)
        if callee_proof is None:
            self._record_observed_call(
                func_ty=func_ty,
                args_operand=_args_operand,
                cterm=c,
                outcome='observed-no-cached-proof',
                target=target,
            )
            if cs is None or self._online_callee_prover is None or func_ty in self._learning_tys:
                return None
            self._learning_tys.add(func_ty)
            try:
                learned_proof = self._online_callee_prover(func_ty, c)
            except Exception as err:
                _LOGGER.warning('CSE: online callee proving failed for ty(%s): %s', func_ty, err, exc_info=True)
                self._failed_tys.add(func_ty)
                return None
            finally:
                self._learning_tys.discard(func_ty)
            if learned_proof is None:
                self._failed_tys.add(func_ty)
                return None
            callee_proof = learned_proof
            self._callee_proofs[func_ty] = learned_proof
            self._online_generated_tys.add(func_ty)
            _LOGGER.info('CSE: learned runtime summary for function ty(%s)', func_ty)

        _LOGGER.info(f'CSE custom_step: applying cached proof for function ty({func_ty})')

        cover_edges = [cover for cover in callee_proof.kcfg.covers() if cover.target.id == callee_proof.target]
        cover_nodes = [cover.source for cover in cover_edges]
        summary_mode = 'return'
        summary_target_node = callee_proof.kcfg.node(callee_proof.target)
        summary_target_k = summary_target_node.cterm.cell('K_CELL')
        use_direct_return_poststates = self._dynamic_return_summaries and not self._is_end_program_k(summary_target_k)
        summary_nodes: list[KCFG.Node] = cover_nodes
        summary_edges: list[KCFG.Cover] = cover_edges
        if not summary_nodes or not self._dynamic_return_summaries:
            summary_mode = 'frontier'
            summary_nodes = self._frontier_nodes(callee_proof)
            summary_edges = []
            if not summary_nodes:
                _LOGGER.warning(f'CSE: no reusable frontier found for callee proof {callee_proof.id}')
                return None
        frontier_boundary_returns: list[KInner | None] = []
        use_frontier_boundary_poststates = False
        if summary_mode == 'frontier':
            frontier_boundary_returns = [self._extract_boundary_return_value(node.cterm.cell('K_CELL')) for node in summary_nodes]
            use_frontier_boundary_poststates = all(ret_value is not None for ret_value in frontier_boundary_returns)

        # Determine caller continuation based on target
        is_entry_call = isinstance(target, KApply) and 'noBasicBlockIdx' in target.label.name
        is_normal_call = isinstance(target, KApply) and 'someBasicBlockIdx' in target.label.name
        if not is_entry_call and not is_normal_call:
            _LOGGER.warning(f'CSE: unexpected target type: {target}')
            return None
        target_bb = target.args[0] if is_normal_call and isinstance(target, KApply) else None

        # Match callee proof's init arg locals against the CALLER's locals directly.
        # NO call setup execution — use operand indices to find correct caller locals.
        # This avoids expensive backend execute() calls (~40s each).
        from pyk.kast.inner import Subst

        callee_init = callee_proof.kcfg.node(callee_proof.init)
        callee_init_locals = callee_init.cterm.cell('LOCALS_CELL')
        caller_locals = c.cell('LOCALS_CELL')

        subst_map: dict[str, KInner] = {}
        callee_items = self._list_items(callee_init_locals)
        caller_items = self._list_items(caller_locals)

        operand_indices = self._extract_arg_local_indices(_args_operand)
        for arg_num, caller_local_idx in enumerate(operand_indices):
            callee_local_idx = arg_num + 1
            if caller_local_idx < 0:
                continue  # Non-local operand (e.g., Constant)
            if callee_local_idx < len(callee_items) and caller_local_idx < len(caller_items):
                item_subst = callee_items[callee_local_idx].match(caller_items[caller_local_idx])
                if item_subst is not None:
                    subst_map.update(item_subst)
                    _LOGGER.info(
                        f'CSE: arg {arg_num}: callee[{callee_local_idx}].match(caller[{caller_local_idx}]) '
                        f'= {list(item_subst.keys())}'
                    )

        subst = Subst(subst_map)
        caller_var_names = self._cterm_var_names(c)
        required_var_names: set[str] = set()
        for i, summary_node in enumerate(summary_nodes):
            if summary_mode == 'return' and use_direct_return_poststates:
                target_cterm = summary_edges[i].csubst(summary_target_node.cterm)
                required_var_names.update(self._free_var_names(subst(target_cterm.config)))
                for constraint in target_cterm.constraints:
                    required_var_names.update(self._free_var_names(subst(constraint)))
            elif summary_mode == 'return' and not use_direct_return_poststates:
                retval = summary_node.cterm.cell('RETVAL_CELL')
                retval_subst = subst(retval)
                required_var_names.update(self._free_var_names(retval_subst))
                for constraint in summary_node.cterm.constraints:
                    required_var_names.update(self._free_var_names(subst(constraint)))
            elif summary_mode == 'frontier' and use_frontier_boundary_poststates:
                ret_value = frontier_boundary_returns[i]
                assert ret_value is not None
                required_var_names.update(self._free_var_names(subst(ret_value)))
                retval_subst = subst(summary_node.cterm.cell('RETVAL_CELL'))
                required_var_names.update(self._free_var_names(retval_subst))
                for constraint in summary_node.cterm.constraints:
                    required_var_names.update(self._free_var_names(subst(constraint)))
            else:
                required_var_names.update(self._free_var_names(subst(summary_node.cterm.config)))
                for constraint in summary_node.cterm.constraints:
                    required_var_names.update(self._free_var_names(subst(constraint)))

        missing_var_names = sorted(required_var_names - caller_var_names)
        if missing_var_names:
            self._record_observed_call(
                func_ty=func_ty,
                args_operand=_args_operand,
                cterm=c,
                outcome=f'{summary_mode}-summary-miss-missing-vars',
                target=target,
                details={'missing_var_names': missing_var_names[:20]},
            )
            _LOGGER.info(
                'CSE: %s terms introduce %d vars not present in caller context for ty(%s), skipping: %s',
                summary_mode,
                len(missing_var_names),
                func_ty,
                missing_var_names[:20],
            )
            self._failed_tys.add(func_ty)
            return None
        if subst_map:
            _LOGGER.info(f'CSE: matched {len(subst_map)} vars for ty({func_ty}): {list(subst_map.keys())}')
        else:
            _LOGGER.info(
                'CSE: no direct substitutions for ty(%s), reusing %d shared caller vars from constraints/config',
                func_ty,
                len(required_var_names),
            )

        # Build summary result states for each selected callee node.
        summary_cterms: list[CTerm] = []
        for i, summary_node in enumerate(summary_nodes):
            if summary_mode == 'return' and use_direct_return_poststates:
                target_cterm = summary_edges[i].csubst(summary_target_node.cterm)
                candidate = CTerm(
                    subst(target_cterm.config),
                    c.constraints + tuple(subst(cst) for cst in target_cterm.constraints),
                )
            elif summary_mode == 'return' and not use_direct_return_poststates:
                retval_cell = summary_node.cterm.cell('RETVAL_CELL')
                ret_value = self._extract_return_value(retval_cell)

                ret_value_subst = subst(ret_value)
                retval_cell_subst = subst(retval_cell)
                callee_constraints = tuple(subst(cst) for cst in summary_node.cterm.constraints)

                if is_entry_call:
                    continuation = KSequence([KMIR.Symbols.END_PROGRAM])
                else:
                    assert target_bb is not None
                    continuation = KSequence(
                        [
                            KApply('#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation', (dest, ret_value_subst)),
                            KApply('#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx', (target_bb,)),
                        ]
                    )

                post_config = set_cell(c.config, 'K_CELL', continuation)
                post_config = set_cell(post_config, 'RETVAL_CELL', retval_cell_subst)
                candidate = CTerm(post_config, c.constraints + callee_constraints)
            elif summary_mode == 'frontier' and use_frontier_boundary_poststates:
                retval_cell = summary_node.cterm.cell('RETVAL_CELL')
                ret_value = frontier_boundary_returns[i]
                assert ret_value is not None

                ret_value_subst = subst(ret_value)
                retval_cell_subst = subst(retval_cell)
                callee_constraints = tuple(subst(cst) for cst in summary_node.cterm.constraints)

                if is_entry_call:
                    continuation = KSequence([KMIR.Symbols.END_PROGRAM])
                else:
                    assert target_bb is not None
                    continuation = KSequence(
                        [
                            KApply('#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation', (dest, ret_value_subst)),
                            KApply('#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx', (target_bb,)),
                        ]
                    )

                post_config = set_cell(c.config, 'K_CELL', continuation)
                post_config = set_cell(post_config, 'RETVAL_CELL', retval_cell_subst)
                candidate = CTerm(post_config, c.constraints + callee_constraints)
            else:
                candidate = CTerm(subst(summary_node.cterm.config), c.constraints + tuple(subst(cst) for cst in summary_node.cterm.constraints))

            # Fast path: cheap structural contradiction check before any backend call
            if _is_trivially_bottom(candidate):
                _LOGGER.info(f'CSE: {summary_mode} branch {i} trivially infeasible (structural contradiction)')
                continue

            # For frontier summaries, skip expensive backend simplify — the trivial check above
            # handles the common vacuous cases (flag AND notBool flag), and the backend will
            # detect true vacuous nodes when it executes them.
            if summary_mode == 'frontier':
                summary_cterms.append(candidate)
                _LOGGER.info(f'CSE: {summary_mode} branch {i} added (skipping backend simplify)')
                continue

            try:
                simplified, _logs = cs.simplify(candidate)
                if _is_bottom(simplified):
                    _LOGGER.info(f'CSE: {summary_mode} branch {i} infeasible (simplified to bottom)')
                    continue
                summary_cterms.append(simplified)
                _LOGGER.info(f'CSE: {summary_mode} branch {i} feasible after simplification')
            except Exception as e:
                # Simplify failed (e.g., sort mismatch from unresolved symbolic vars).
                # Don't use the broken candidate — skip this branch.
                _LOGGER.warning(f'CSE: simplify failed for {summary_mode} branch {i}, skipping: {e}')
                continue

        # Only add stuck fallback if NO CSE paths are feasible.
        # If we have feasible CSE paths, the stuck paths are likely unreachable
        # from the caller's actual arguments. Adding fallback for stuck paths
        # when CSE paths exist causes proof tree explosion (NDBranch everywhere).
        has_stuck_fallback = summary_mode == 'return' and not summary_cterms and any(
            callee_proof.kcfg.is_stuck(n.id) for n in callee_proof.kcfg.leaves
        )

        if not summary_cterms and not has_stuck_fallback:
            self._record_observed_call(
                func_ty=func_ty,
                args_operand=_args_operand,
                cterm=c,
                outcome=f'{summary_mode}-summary-miss-no-feasible-branches',
                target=target,
            )
            _LOGGER.warning(
                'CSE: all %s branches infeasible for ty(%s), disabling CSE for this function',
                summary_mode,
                func_ty,
            )
            self._failed_tys.add(func_ty)
            return None

        # For return summaries, different cover paths can simplify to equivalent
        # post-return states under the caller's constraints — collapse them to
        # avoid redundant proof splits.
        #
        # For frontier summaries, skip dedup: frontier nodes represent genuinely
        # distinct execution paths from the callee's proof tree.  Callee-internal
        # variables (e.g. ?INITIALISED) are not substituted into the caller
        # context, so cs.implies() can incorrectly treat structurally different
        # branches as equivalent when those variables appear only in constraints.
        if summary_mode == 'return':
            deduped_cterms: list[CTerm] = []
            for candidate in summary_cterms:
                merged = False
                for idx, existing in enumerate(deduped_cterms):
                    cand_implies_existing = cs.implies(candidate, existing)
                    existing_implies_cand = cs.implies(existing, candidate)
                    equivalent = (
                        not cand_implies_existing.failing_cells
                        and cand_implies_existing.remaining_implication is None
                        and not existing_implies_cand.failing_cells
                        and existing_implies_cand.remaining_implication is None
                    )
                    if equivalent:
                        chosen = candidate if len(candidate.constraints) < len(existing.constraints) else existing
                        deduped_cterms[idx] = chosen
                        _LOGGER.info(f'CSE: merged equivalent summary branches for ty({func_ty})')
                        merged = True
                        break
                if not merged:
                    deduped_cterms.append(candidate)
            summary_cterms = deduped_cterms

        if not summary_cterms:
            self._record_observed_call(
                func_ty=func_ty,
                args_operand=_args_operand,
                cterm=c,
                outcome=f'{summary_mode}-summary-miss-no-reusable-paths',
                target=target,
            )
            _LOGGER.info(f'CSE: no {summary_mode} paths feasible, falling back for ty({func_ty})')
            self._failed_tys.add(func_ty)
            return None

        if has_stuck_fallback:
            _LOGGER.info(f'CSE custom_step: {len(summary_cterms)} CSE paths + 1 fallback for ty({func_ty})')
            all_cterms = tuple(summary_cterms) + (c,)
            all_labels = ['CSE-SUMMARY'] * len(summary_cterms) + ['CSE-FALLBACK']
            return NDBranch(cterms=all_cterms, logs=(), rule_labels=tuple(all_labels))

        if len(summary_cterms) == 1:
            self._summary_hit_counts[func_ty] = self._summary_hit_counts.get(func_ty, 0) + 1
            self._record_observed_call(
                func_ty=func_ty,
                args_operand=_args_operand,
                cterm=c,
                outcome=f'{summary_mode}-summary-hit-single-path',
                target=target,
            )
            label = 'CSE-SUMMARY' if summary_mode == 'return' else 'CSE-FRONTIER'
            info = 'cse-summary' if summary_mode == 'return' else 'cse-frontier'
            _LOGGER.info(f'CSE custom_step: single-path {summary_mode} summary for ty({func_ty})')
            return Step(cterm=summary_cterms[0], depth=1, logs=(), rule_labels=[label], info=info)

        self._record_observed_call(
            func_ty=func_ty,
            args_operand=_args_operand,
            cterm=c,
            outcome=f'{summary_mode}-summary-hit-branching',
            target=target,
            details={'branch_count': len(summary_cterms)},
        )
        self._summary_hit_counts[func_ty] = self._summary_hit_counts.get(func_ty, 0) + 1

        # NOTE: Branch(constraints) approach causes infinite splits on complex
        # callees (solana-token) because _is_trivially_bottom can't detect all
        # contradictions.  Use NDBranch which provides complete cterms.
        _LOGGER.info(f'CSE custom_step: {len(summary_cterms)}-branch {summary_mode} NDBranch for ty({func_ty})')
        branch_label = 'CSE-SUMMARY' if summary_mode == 'return' else 'CSE-FRONTIER'
        return NDBranch(
            cterms=tuple(summary_cterms),
            logs=(),
            rule_labels=tuple([branch_label] * len(summary_cterms)),
        )


def _extract_bool_pos_neg(constraints: tuple[KInner, ...]) -> tuple[frozenset[KInner], frozenset[KInner]]:
    """Extract positive and negative bool-typed subterms from constraints.

    Handles both:
    - ML constraints: #Equals(true, T) and #Equals(true, notBool T)
    - Raw Bool constraints: T and notBool T (from split_on_constraints)

    Returns (positive, negative) where P in both sets → contradiction.
    """
    positive: list[KInner] = []
    negative: list[KInner] = []
    for c in constraints:
        if not isinstance(c, KApply):
            continue
        if c.label.name.startswith('#Equals') and len(c.args) == 2:
            # ML constraint: #Equals(true, EXPR) or #Equals(EXPR, true)
            lhs, rhs = c.args
            if isinstance(rhs, KToken) and rhs.token == 'true' and not (isinstance(lhs, KToken) and lhs.token == 'true'):
                lhs, rhs = rhs, lhs
            if not (isinstance(lhs, KToken) and lhs.token == 'true'):
                continue
            if isinstance(rhs, KApply) and 'notBool' in rhs.label.name and len(rhs.args) == 1:
                negative.append(rhs.args[0])
            else:
                positive.append(rhs)
        elif 'notBool' in c.label.name and len(c.args) == 1:
            # Raw Bool: notBool T
            negative.append(c.args[0])
        else:
            # Raw Bool: T (any other KApply treated as positive)
            positive.append(c)
    return (frozenset(positive), frozenset(negative))


def _is_trivially_bottom(cterm: CTerm) -> bool:
    """Cheap syntactic check for unsatisfiable constraints — no backend call.

    Returns True if:
    - Any constraint is literally KToken('false') or a #Bottom apply, OR
    - Constraints contain both #Equals(true, P) and #Equals(true, notBool P)
      for the same term P, OR
    - Constraints contain #Equals(true, false) — direct contradiction, OR
    - Constraints contain #Equals(true, notBool true) — direct contradiction
    """
    for c in cterm.constraints:
        if isinstance(c, KToken) and c.token == 'false':
            return True
        if isinstance(c, KApply) and '#Bottom' in c.label.name:
            return True
    pos, neg = _extract_bool_pos_neg(cterm.constraints)
    # Direct contradictions: pos contains false, or neg contains true
    _false = KToken('false', KSort('Bool'))
    _true = KToken('true', KSort('Bool'))
    if _false in pos or _true in neg:
        return True
    return bool(pos & neg)


def _is_bottom(cterm: CTerm) -> bool:
    """Check if a CTerm has been simplified to #Bottom (unsatisfiable constraints)."""
    from pyk.kast.inner import KToken

    # After simplify, vacuous terms may have config = #Bottom or constraints containing #Bottom
    config = cterm.config
    if isinstance(config, KApply) and 'Bottom' in config.label.name:
        return True
    # Check if any constraint is literally 'false'
    for c in cterm.constraints:
        if isinstance(c, KToken) and c.token == 'false':
            return True
        if isinstance(c, KApply) and '#Bottom' in c.label.name:
            return True
    return False


class KMIRNodePrinter(NodePrinter):
    def __init__(self, cterm_show: CTermShow, full_printer: bool = False) -> None:
        NodePrinter.__init__(self, cterm_show, full_printer=full_printer)


class KMIRAPRNodePrinter(KMIRNodePrinter, APRProofNodePrinter):
    smir_info: SMIRInfo | None

    def __init__(self, cterm_show: CTermShow, proof: APRProof, opts: DisplayOpts) -> None:
        KMIRNodePrinter.__init__(self, cterm_show, full_printer=opts.full_printer)
        APRProofNodePrinter.__init__(self, proof, cterm_show, full_printer=opts.full_printer)
        self.smir_info = None
        if opts.smir_info:
            self.smir_info = SMIRInfo.from_file(opts.smir_info)
        elif (
            proof.proof_dir is not None
            and (proof.proof_dir / proof.id).is_dir()
            and (proof.proof_dir / proof.id / 'smir.json').is_file()
        ):
            self.smir_info = SMIRInfo.from_file(proof.proof_dir / proof.id / 'smir.json')

    def _span(self, node: KCFG.Node) -> str | None:
        curr_span: int | None = None
        span_worklist: list[KInner] = [node.cterm.cell('K_CELL')]
        while span_worklist:
            next_item = span_worklist.pop(0)
            if type(next_item) is KApply:
                if (
                    next_item.label.name == 'span'
                    and type(next_item.args[0]) is KToken
                    and next_item.args[0].sort.name == 'Int'
                ):
                    curr_span = int(next_item.args[0].token)
                    break
                span_worklist = list(next_item.args) + span_worklist
            if type(next_item) is KSequence:
                span_worklist = list(next_item.items) + span_worklist
        if self.smir_info is not None and curr_span is not None and curr_span in self.smir_info.spans:
            path, start_row, _start_column, _end_row, _end_column = self.smir_info.spans[curr_span]
            return f'{str(path)[-30:]}:{start_row}'
        if curr_span is not None:
            return f'{curr_span}'
        return None

    def _function_name(self, node: KCFG.Node) -> str | None:
        curr_func_ty_kast = node.cterm.cell('CURRENTFUNC_CELL')
        if (
            type(curr_func_ty_kast) is KApply
            and curr_func_ty_kast.label.name == 'ty'
            and type(curr_func_ty_kast.args[0]) is KToken
            and curr_func_ty_kast.args[0].sort.name
        ):
            curr_func_ty = int(curr_func_ty_kast.args[0].token)
            if curr_func_ty == -1:
                return 'main'
            if self.smir_info is not None:
                if curr_func_ty in self.smir_info.function_symbols:
                    _sym = self.smir_info.function_symbols[curr_func_ty]
                    if 'NormalSym' in _sym:
                        sym = _sym['NormalSym']
                        if sym in self.smir_info.items:
                            name = self.smir_info.items[sym]['mono_item_kind']['MonoItemFn']['name']
                            assert type(name) is str
                            return name
        return None

    def print_node(self, kcfg: KCFG, node: KCFG.Node) -> list[str]:
        ret_strs = super().print_node(kcfg, node)
        ret_strs.append(self.cterm_show._printer(node.cterm.cell('K_CELL'))[0:80])
        curr_func = self._function_name(node)
        if curr_func is not None:
            ret_strs.append(f'function: {curr_func}')
        curr_span = self._span(node)
        if curr_span is not None:
            ret_strs.append(f'span: {curr_span}')
        return ret_strs
