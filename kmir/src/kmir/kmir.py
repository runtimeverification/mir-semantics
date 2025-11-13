from __future__ import annotations

import logging
import tempfile
from contextlib import contextmanager
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.kast.inner import KApply, KLabel, KSequence, KSort, KToken, KVariable, Subst
from pyk.kast.manip import abstract_term_safely, split_config_from
from pyk.kast.outer import KFlatModule, KImport
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofNodePrinter

from .cargo import cargo_get_smir_json
from .kast import ConcreteMode, RandomMode, SymbolicMode, make_call_config
from .kparse import KParse
from .parse.parser import Parser
from .smir import SMIRInfo

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Final

    from pyk.cterm.show import CTermShow
    from pyk.kast.inner import KInner
    from pyk.kore.syntax import Pattern
    from pyk.utils import BugReport

    from .options import DisplayOpts, ProveRSOpts

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
    def cut_point_rules(
        break_on_calls: bool,
        break_on_function_calls: bool,
        break_on_intrinsic_calls: bool,
        break_on_thunk: bool,
        break_every_statement: bool,
        break_on_terminator_goto: bool,
        break_on_terminator_switch_int: bool,
        break_on_terminator_return: bool,
        break_on_terminator_call: bool,
        break_on_terminator_assert: bool,
        break_on_terminator_drop: bool,
        break_on_terminator_unreachable: bool,
        break_every_terminator: bool,
        break_every_step: bool,
    ) -> list[str]:
        cut_point_rules = []
        if break_on_thunk:
            cut_point_rules.append('RT-DATA.thunk')
        if break_every_statement or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.execStmt')
        if break_on_terminator_goto or break_every_terminator or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.termGoto')
        if break_on_terminator_switch_int or break_every_terminator or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.termSwitchInt')
        if break_on_terminator_return or break_every_terminator or break_every_step:
            cut_point_rules.extend(
                [
                    'KMIR-CONTROL-FLOW.termReturnSome',
                    'KMIR-CONTROL-FLOW.termReturnNone',
                    'KMIR-CONTROL-FLOW.endprogram-return',
                    'KMIR-CONTROL-FLOW.endprogram-no-return',
                ]
            )
        if (
            break_on_intrinsic_calls
            or break_on_calls
            or break_on_terminator_call
            or break_every_terminator
            or break_every_step
        ):
            cut_point_rules.append('KMIR-CONTROL-FLOW.termCallIntrinsic')
        if (
            break_on_function_calls
            or break_on_calls
            or break_on_terminator_call
            or break_every_terminator
            or break_every_step
        ):
            cut_point_rules.append('KMIR-CONTROL-FLOW.termCallFunction')
        if break_on_terminator_assert or break_every_terminator or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.termAssert')
        if break_on_terminator_drop or break_every_terminator or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.termDrop')
        if break_on_terminator_unreachable or break_every_terminator or break_every_step:
            cut_point_rules.append('KMIR-CONTROL-FLOW.termUnreachable')
        return cut_point_rules

    @staticmethod
    def from_kompiled_kore(
        smir_info: SMIRInfo, target_dir: Path, bug_report: Path | None = None, symbolic: bool = True
    ) -> KMIR:
        from .kompile import kompile_smir

        kompiled_smir = kompile_smir(
            smir_info=smir_info,
            target_dir=target_dir,
            bug_report=bug_report,
            symbolic=symbolic,
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

    def apr_proof_from_smir(
        self,
        id: str,
        smir_info: SMIRInfo,
        start_symbol: str = 'main',
        proof_dir: Path | None = None,
    ) -> APRProof:
        lhs_config, constraints = make_call_config(
            self.definition,
            smir_info=smir_info,
            start_symbol=start_symbol,
            mode=SymbolicMode(),
        )
        lhs = CTerm(lhs_config, constraints)

        var_config, var_subst = split_config_from(lhs_config)
        _rhs_subst: dict[str, KInner] = {
            v_name: abstract_term_safely(KVariable('_'), base_name=v_name) for v_name in var_subst
        }
        _rhs_subst['K_CELL'] = KSequence([KMIR.Symbols.END_PROGRAM])
        rhs = CTerm(Subst(_rhs_subst)(var_config))
        kcfg = KCFG()
        init_node = kcfg.create_node(lhs)
        target_node = kcfg.create_node(rhs)
        return APRProof(id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)

    @staticmethod
    def prove_rs(opts: ProveRSOpts) -> APRProof:
        if not opts.rs_file.is_file():
            raise ValueError(f'Input file does not exist: {opts.rs_file}')

        label = str(opts.rs_file.stem) + '.' + opts.start_symbol

        with tempfile.TemporaryDirectory() as tmp_dir:
            target_path = opts.proof_dir / label if opts.proof_dir is not None else Path(tmp_dir)

            if not opts.reload and opts.proof_dir is not None and APRProof.proof_data_exists(label, opts.proof_dir):
                _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
                apr_proof = APRProof.read_proof_data(opts.proof_dir, label)

                smir_info = SMIRInfo.from_file(target_path / 'smir.json')
                kmir = KMIR.from_kompiled_kore(
                    smir_info, symbolic=True, bug_report=opts.bug_report, target_dir=target_path
                )
            else:
                _LOGGER.info(f'Constructing initial proof: {label}')
                if opts.smir:
                    smir_info = SMIRInfo.from_file(opts.rs_file)
                else:
                    smir_info = SMIRInfo(cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir))

                smir_info = smir_info.reduce_to(opts.start_symbol)
                # Report whether the reduced call graph includes any functions without MIR bodies
                missing_body_syms = [
                    sym
                    for sym, item in smir_info.items.items()
                    if 'MonoItemFn' in item['mono_item_kind']
                    and item['mono_item_kind']['MonoItemFn'].get('body') is None
                ]
                has_missing = len(missing_body_syms) > 0
                _LOGGER.info(f'Reduced items table size {len(smir_info.items)}')
                if has_missing:
                    _LOGGER.info(f'missing-bodies-present={has_missing} count={len(missing_body_syms)}')
                    _LOGGER.debug(f'Missing-body function symbols (first 5): {missing_body_syms[:5]}')

                kmir = KMIR.from_kompiled_kore(
                    smir_info, symbolic=True, bug_report=opts.bug_report, target_dir=target_path
                )

                apr_proof = kmir.apr_proof_from_smir(
                    label, smir_info, start_symbol=opts.start_symbol, proof_dir=opts.proof_dir
                )
                if apr_proof.proof_dir is not None and (apr_proof.proof_dir / label).is_dir():
                    smir_info.dump(apr_proof.proof_dir / apr_proof.id / 'smir.json')

            if apr_proof.passed:
                return apr_proof

            cut_point_rules = KMIR.cut_point_rules(
                break_on_calls=opts.break_on_calls,
                break_on_function_calls=opts.break_on_function_calls,
                break_on_intrinsic_calls=opts.break_on_intrinsic_calls,
                break_on_thunk=opts.break_on_thunk or opts.terminate_on_thunk,  # must break for terminal rule
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
            )

            # produce a module for the lookup functions
            from .kompile import make_kore_rules

            equations = make_kore_rules(kmir, smir_info)
            _LOGGER.debug(f'Made {len(equations)} equations')
            prog_module = KFlatModule(name='KMIR-PROGRAM', sentences=equations, imports=(KImport('KMIR'),))

            with kmir.kcfg_explore(label, terminate_on_thunk=opts.terminate_on_thunk) as kcfg_explore:
                prover = APRProver(
                    kcfg_explore,
                    execute_depth=opts.max_depth,
                    cut_point_rules=cut_point_rules,
                    extra_module=prog_module,
                )
                prover.advance_proof(apr_proof, max_iterations=opts.max_iterations)
                return apr_proof


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
