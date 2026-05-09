from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import cached_property
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import cterm_symbolic
from pyk.kast.inner import KApply, KLabel, KSequence, KSort, KToken
from pyk.kast.prelude.collections import map_of
from pyk.kast.prelude.kint import intToken
from pyk.kast.prelude.utils import token
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

    from pyk.cterm import CTerm
    from pyk.cterm.show import CTermShow
    from pyk.kast.inner import KInner
    from pyk.kcfg import KCFG
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
        extra_module: Path | str | None = None,
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
            extra_module=extra_module,
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
        cell_maps = self._make_smir_maps(smir_info)
        init_config, _ = make_call_config(
            self.definition,
            smir_info=smir_info,
            start_symbol=start_symbol,
            mode=mode,
            cell_maps=cell_maps,
        )
        init_kore = self.kast_to_kore(init_config, KSort('GeneratedTopCell'))
        result = self.run_pattern(init_kore, depth=depth)
        return result

    def _make_smir_maps(self, smir_info: SMIRInfo) -> dict[str, KInner]:
        """Build map cell substitutions for concrete execution."""
        from .kompile import _decode_alloc, _functions

        SOME_MAP = 'MaybeMap::someMap'

        # Functions map: ty(N) |-> MonoItemKind
        func_entries: dict[KInner, KInner] = {}
        for ty, body in _functions(self, smir_info).items():
            func_entries[KApply('ty', (token(ty),))] = body
        functions_map = KApply(SOME_MAP, (map_of(func_entries),))

        # Types map: ty(N) |-> TypeInfo
        type_entries: dict[KInner, KInner] = {}
        for type_json in smir_info._smir['types']:
            parse_result = self.parser.parse_mir_json(type_json, 'TypeMapping')
            if parse_result is not None:
                type_mapping, _ = parse_result
                if isinstance(type_mapping, KApply) and len(type_mapping.args) == 2:
                    ty, tyinfo = type_mapping.args
                    type_entries[ty] = tyinfo
        types_map = KApply(SOME_MAP, (map_of(type_entries),))

        # Allocs map: allocId(N) |-> Value
        alloc_entries: dict[KInner, KInner] = {}
        for raw_alloc in smir_info._smir['allocs']:
            alloc_id_term, value_term = _decode_alloc(smir_info=smir_info, raw_alloc=raw_alloc)
            alloc_entries[alloc_id_term] = value_term
        allocs_map = KApply(SOME_MAP, (map_of(alloc_entries),))

        return {
            'FUNCTIONS_CELL': functions_map,
            'TYPES_CELL': types_map,
            'MEMORY_CELL': allocs_map,
        }

    @staticmethod
    def prove_programs(opts: ProveOpts) -> list[APRProof]:
        from ._prove import prove

        return prove(opts)

    @staticmethod
    def prove_program(opts: ProveOpts) -> APRProof:
        proofs = KMIR.prove_programs(opts)
        assert len(proofs) == 1, f'Expected single proof, got {len(proofs)}'
        return proofs[0]

    @staticmethod
    def prove_program_with_kmir(kmir: KMIR, smir_info: SMIRInfo, opts: ProveOpts) -> APRProof:
        from ._prove import prove_with_kmir

        return prove_with_kmir(kmir, smir_info, opts)


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
        elif proof.proof_dir is not None:
            file_stem = proof.id.rsplit('.', 1)[0]
            # Single-symbol: smir.json in the proof's own directory
            label_smir = proof.proof_dir / proof.id / 'smir.json'
            # Multi-symbol: smir.json in the shared kompiled directory
            kompiled_smir = proof.proof_dir / f'{file_stem}.kompiled' / 'smir.json'
            if label_smir.is_file():
                self.smir_info = SMIRInfo.from_file(label_smir)
            elif kompiled_smir.is_file():
                self.smir_info = SMIRInfo.from_file(kompiled_smir)
            else:
                _LOGGER.warning('SMIR info not found, span/function annotations unavailable')
        else:
            _LOGGER.warning('No SMIR Info or proof dir found, span/function annotations unavailable')

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
