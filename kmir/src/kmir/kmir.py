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
    through the callee's execution.
    """

    _callee_proofs: dict[int, APRProof]  # function Ty -> completed proof

    def __init__(self, callee_proofs: dict[int, APRProof] | None = None, terminate_on_thunk: bool = False) -> None:
        super().__init__(terminate_on_thunk=terminate_on_thunk)
        self._callee_proofs = callee_proofs or {}

    def _extract_call_info(self, k_cell: KInner) -> tuple[int, KInner, KInner, KInner] | None:
        """Extract (function_ty, args, dest, target) from a call terminator in <k> cell.

        Returns None if the K cell is not a function call terminator.
        """
        # Match: #execTerminator(terminator(terminatorKindCall(func, args, dest, target, unwind), span))
        # or the KSequence variant with continuation
        term = k_cell
        if isinstance(term, KSequence) and term.items:
            term = term.items[0]

        if not isinstance(term, KApply):
            return None
        if term.label.name != '#execTerminator(_)_KMIR-CONTROL-FLOW_KItem_Terminator':
            return None

        # term.args[0] is terminator(kind, span)
        terminator = term.args[0]
        if not isinstance(terminator, KApply) or len(terminator.args) < 1:
            return None

        kind = terminator.args[0]
        if not isinstance(kind, KApply) or kind.label.name != 'TerminatorKind::Call':
            return None

        # kind.args = (func, args, dest, target, unwind)
        func_operand, args_operand, dest, target, _unwind = kind.args

        # Extract function Ty from func operand
        # func is operandConstant(constOperand(span, userTy, mirConst(kind, ty(N), id)))
        func_ty = self._extract_func_ty(func_operand)
        if func_ty is None:
            return None

        return (func_ty, args_operand, dest, target)

    @staticmethod
    def _extract_func_ty(func_operand: KInner) -> int | None:
        """Extract the function Ty integer from a function operand."""
        try:
            # operandConstant(constOperand(span, userTy, mirConst(kind, ty(N), id)))
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
        return func_ty in self._callee_proofs

    def custom_step(self, c: CTerm, cs: CTermSymbolic) -> KCFGExtendResult | None:
        from pyk.kcfg.kcfg import Step

        k_cell = c.cell('K_CELL')
        call_info = self._extract_call_info(k_cell)
        if call_info is None:
            return None

        func_ty, _args, dest, target = call_info
        callee_proof = self._callee_proofs.get(func_ty)
        if callee_proof is None:
            return None
        if not callee_proof.passed:
            return None

        _LOGGER.info(f'CSE custom_step: applying cached proof for function ty({func_ty})')

        # Get the callee's final computed state (the node that covers the target)
        final_node = None
        for cover in callee_proof.kcfg.covers():
            if cover.target.id == callee_proof.target:
                final_node = cover.source
                break
        if final_node is None:
            _LOGGER.warning(f'CSE: no cover found for callee proof {callee_proof.id}')
            return None

        # Extract the return value from the callee's final RETVAL_CELL
        retval_cell = final_node.cterm.cell('RETVAL_CELL')

        # Build the post-return configuration:
        # - K_CELL: the caller continuation after the call
        # - RETVAL_CELL: updated with callee's return value
        # - All other cells: same as the caller's current state

        # Determine continuation based on target
        if isinstance(target, KApply) and 'someBasicBlockIdx' in target.label.name:
            # Normal call: continue at target basic block
            target_bb = target.args[0]  # basicBlockIdx(N)
            continuation = KSequence(
                [
                    KApply(
                        '#setLocalValue(_,_)_RT-DATA_KItem_Place_Evaluation',
                        (dest, self._extract_return_value(retval_cell)),
                    ),
                    KApply('#execBlockIdx(_)_KMIR-CONTROL-FLOW_KItem_BasicBlockIdx', (target_bb,)),
                ]
            )
        elif isinstance(target, KApply) and 'noBasicBlockIdx' in target.label.name:
            # Entry function call: end with #EndProgram
            continuation = KSequence([KMIR.Symbols.END_PROGRAM])
        else:
            _LOGGER.warning(f'CSE: unexpected target type: {target}')
            return None

        # Construct the post-return CTerm by substituting cells in the current config
        from pyk.kast.manip import set_cell

        post_config = c.config
        post_config = set_cell(post_config, 'K_CELL', continuation)
        post_config = set_cell(post_config, 'RETVAL_CELL', retval_cell)

        post_cterm = CTerm(post_config, c.constraints)

        _LOGGER.info(f'CSE custom_step: constructed post-return state for ty({func_ty})')
        return Step(cterm=post_cterm, depth=1, logs=(), rule_labels=['CSE-FUNCTION-SUMMARY'], info='cse-summary')

    @staticmethod
    def _extract_return_value(retval_cell: KInner) -> KInner:
        """Extract the Value from return(Value) in RETVAL_CELL."""
        if isinstance(retval_cell, KApply) and 'return' in retval_cell.label.name:
            return retval_cell.args[0]
        return retval_cell


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
