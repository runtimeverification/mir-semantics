from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.kast.inner import KApply, KLabel, KSequence, KSort, KToken
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
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
        with cterm_symbolic(
            self.definition,
            self.definition_dir,
            llvm_definition_dir=self.llvm_library_dir,
            bug_report=self.bug_report,
            id=label if self.bug_report is not None else None,  # NB bug report arg.s must be coherent
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

    def __init__(self, callee_proofs: dict[int, APRProof] | None = None, terminate_on_thunk: bool = False) -> None:
        super().__init__(terminate_on_thunk=terminate_on_thunk)
        self._callee_proofs = callee_proofs or {}
        self._failed_tys: set[int] = set()  # Track function Tys where CSE failed

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
        func_ty, _, _, _ = call_info
        if func_ty in self._failed_tys:
            return False
        return func_ty in self._callee_proofs

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
        # Operands::append builds right-to-left, so reverse
        result.reverse()
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
        """Extract local indices from call argument operands."""
        indices: list[int] = []
        current = args_operand
        while isinstance(current, KApply):
            if current.label.name in ('Operand::Copy', 'Operand::Move'):
                place = current.args[0]
                if isinstance(place, KApply) and place.label.name == 'place':
                    local = place.args[0]
                    if isinstance(local, KApply) and local.label.name == 'local':
                        idx_token = local.args[0]
                        if isinstance(idx_token, KToken):
                            indices.append(int(idx_token.token))
                return indices
            elif 'append' in current.label.name.lower():
                # Operands::append(rest, operand)
                rest, operand = current.args
                if isinstance(operand, KApply) and operand.label.name in ('Operand::Copy', 'Operand::Move'):
                    place = operand.args[0]
                    if isinstance(place, KApply) and place.label.name == 'place':
                        local = place.args[0]
                        if isinstance(local, KApply) and local.label.name == 'local':
                            idx_token = local.args[0]
                            if isinstance(idx_token, KToken):
                                indices.append(int(idx_token.token))
                current = rest
            else:
                break
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
            return None

        _LOGGER.info(f'CSE custom_step: applying cached proof for function ty({func_ty})')

        cover_nodes = [cover.source for cover in callee_proof.kcfg.covers() if cover.target.id == callee_proof.target]
        if not cover_nodes:
            _LOGGER.warning(f'CSE: no covers found for callee proof {callee_proof.id}')
            return None

        # Determine caller continuation based on target
        is_entry_call = isinstance(target, KApply) and 'noBasicBlockIdx' in target.label.name
        is_normal_call = isinstance(target, KApply) and 'someBasicBlockIdx' in target.label.name
        if not is_entry_call and not is_normal_call:
            _LOGGER.warning(f'CSE: unexpected target type: {target}')
            return None
        target_bb = target.args[0] if is_normal_call and isinstance(target, KApply) else None

        # Execute real call setup to get normalized callee entry state.
        # Then match callee proof's init locals against these to get sort-correct substitution.
        from pyk.kast.inner import Subst

        try:
            # Execute call setup step-by-step until #execBlock is in <k>
            normalized_entry = c
            setup_depth = 0
            for _step in range(30):
                r, _next, depth, _, _ = cs.execute(normalized_entry, depth=1)
                if depth == 0 and not _next:
                    break
                normalized_entry = r if depth > 0 else (_next[0].state if _next else r)
                setup_depth += 1
                k = normalized_entry.cell('K_CELL')
                first = k.items[0] if isinstance(k, KSequence) and k.items else k
                if isinstance(first, KApply) and '#execTerminatorCall(' in first.label.name:
                    break
            if setup_depth == 0:
                self._failed_tys.add(func_ty)
                return None
            _LOGGER.info(f'CSE: real call setup in {setup_depth} steps for ty({func_ty})')
        except Exception as e:
            _LOGGER.warning(f'CSE: call setup failed for ty({func_ty}): {e}')
            self._failed_tys.add(func_ty)
            return None

        # Match callee proof's init locals against normalized entry locals.
        # Use per-item partial matching: collect bindings from items that match,
        # leave unmatched variables as existentials (handled by simplify).
        callee_init = callee_proof.kcfg.node(callee_proof.init)
        callee_init_locals = callee_init.cterm.cell('LOCALS_CELL')
        entry_locals = normalized_entry.cell('LOCALS_CELL')

        # Per-item partial match on locals
        subst_map: dict[str, KInner] = {}
        callee_items = self._list_items(callee_init_locals)
        entry_items = self._list_items(entry_locals)
        for idx in range(min(len(callee_items), len(entry_items))):
            item_subst = callee_items[idx].match(entry_items[idx])
            if item_subst is not None:
                subst_map.update(item_subst)

        # Fallback: match K_CELL (both have #execTerminatorCall with call args)
        if not subst_map:
            callee_k = callee_init.cterm.cell('K_CELL')
            entry_k = normalized_entry.cell('K_CELL')
            k_subst = callee_k.match(entry_k)
            if k_subst is not None:
                subst_map.update(k_subst)
                _LOGGER.info(f'CSE: K_CELL match {len(k_subst)} vars for ty({func_ty})')

        subst = Subst(subst_map)
        if not subst_map:
            _LOGGER.info(f'CSE: no vars matched for ty({func_ty}), skipping CSE')
            self._failed_tys.add(func_ty)
            return None
        _LOGGER.info(f'CSE: matched {len(subst_map)} vars for ty({func_ty}): {list(subst_map.keys())}')

        # Check that ALL cover node RETVALs are fully concrete after substitution.
        # If any RETVAL still has free vars, skip CSE (would cause stuck projections).
        from pyk.kast.manip import free_vars as _fv

        all_concrete = True
        for cover_node in cover_nodes:
            retval = cover_node.cterm.cell('RETVAL_CELL')
            retval_subst = subst(retval)
            remaining_fvs = _fv(retval_subst)
            if remaining_fvs:
                _LOGGER.info(f'CSE: RETVAL has {len(remaining_fvs)} unresolved vars for ty({func_ty}), skipping')
                all_concrete = False
                break
        if not all_concrete:
            self._failed_tys.add(func_ty)
            return None

        # Build post-return states for each callee cover path
        post_return_cterms: list[CTerm] = []
        for i, cover_node in enumerate(cover_nodes):
            retval_cell = cover_node.cterm.cell('RETVAL_CELL')
            ret_value = self._extract_return_value(retval_cell)

            ret_value_subst = subst(ret_value)
            retval_cell_subst = subst(retval_cell)
            callee_constraints = tuple(subst(cst) for cst in cover_node.cterm.constraints)

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

            try:
                simplified, _logs = cs.simplify(candidate)
                if _is_bottom(simplified):
                    _LOGGER.info(f'CSE: branch {i} infeasible (simplified to bottom)')
                    continue
                post_return_cterms.append(simplified)
                _LOGGER.info(f'CSE: branch {i} feasible after simplification')
            except Exception as e:
                # Simplify failed (e.g., sort mismatch from unresolved symbolic vars).
                # Don't use the broken candidate — skip this branch.
                _LOGGER.warning(f'CSE: simplify failed for branch {i}, skipping: {e}')
                continue

        # Only add stuck fallback if NO CSE paths are feasible.
        # If we have feasible CSE paths, the stuck paths are likely unreachable
        # from the caller's actual arguments. Adding fallback for stuck paths
        # when CSE paths exist causes proof tree explosion (NDBranch everywhere).
        has_stuck_fallback = not post_return_cterms and any(
            callee_proof.kcfg.is_stuck(n.id) for n in callee_proof.kcfg.leaves
        )

        if not post_return_cterms and not has_stuck_fallback:
            _LOGGER.warning(f'CSE: all branches infeasible for ty({func_ty}), disabling CSE for this function')
            self._failed_tys.add(func_ty)
            return None

        if not post_return_cterms:
            _LOGGER.info(f'CSE: no cover paths feasible, falling back for ty({func_ty})')
            self._failed_tys.add(func_ty)
            return None

        if has_stuck_fallback:
            _LOGGER.info(f'CSE custom_step: {len(post_return_cterms)} CSE paths + 1 fallback for ty({func_ty})')
            all_cterms = tuple(post_return_cterms) + (c,)
            all_labels = ['CSE-SUMMARY'] * len(post_return_cterms) + ['CSE-FALLBACK']
            return NDBranch(cterms=all_cterms, logs=(), rule_labels=tuple(all_labels))

        if len(post_return_cterms) == 1:
            _LOGGER.info(f'CSE custom_step: single-path summary for ty({func_ty})')
            return Step(cterm=post_return_cterms[0], depth=1, logs=(), rule_labels=['CSE-SUMMARY'], info='cse-summary')

        _LOGGER.info(f'CSE custom_step: {len(post_return_cterms)}-branch summary for ty({func_ty})')
        return NDBranch(
            cterms=tuple(post_return_cterms),
            logs=(),
            rule_labels=tuple(['CSE-SUMMARY'] * len(post_return_cterms)),
        )


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
