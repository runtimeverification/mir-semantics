from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.kast.inner import KApply, KInner, KSequence, KSort, KToken, Subst
from pyk.kast.manip import split_config_from
from pyk.kast.prelude.string import stringToken
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofNodePrinter

from .cargo import cargo_get_smir_json
from .kparse import KParse
from .parse.parser import Parser

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Final

    from pyk.kore.syntax import Pattern
    from pyk.utils import BugReport

    from .options import ProveRSOpts

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

    class Symbols:
        END_PROGRAM: Final = KApply('#EndProgram_KMIR-CONTROL-FLOW_KItem')

    @contextmanager
    def kcfg_explore(self, label: str | None = None) -> Iterator[KCFGExplore]:
        with cterm_symbolic(
            self.definition,
            self.definition_dir,
            llvm_definition_dir=self.llvm_library_dir,
            bug_report=self.bug_report,
            id=label if self.bug_report is not None else None,  # NB bug report arg.s must be coherent
        ) as cts:
            yield KCFGExplore(cts, kcfg_semantics=KMIRSemantics())

    def make_init_config(
        self, parsed_smir: KInner, start_symbol: KInner | str = 'main', sort: str = 'GeneratedTopCell'
    ) -> KInner:
        if isinstance(start_symbol, str):
            start_symbol = stringToken(start_symbol)

        subst = Subst({'$PGM': parsed_smir, '$STARTSYM': start_symbol})
        init_config = subst.apply(self.definition.init_config(KSort(sort)))
        return init_config

    def run_parsed(self, parsed_smir: KInner, start_symbol: KInner | str = 'main', depth: int | None = None) -> Pattern:
        init_config = self.make_init_config(parsed_smir, start_symbol)
        init_kore = self.kast_to_kore(init_config, KSort('GeneratedTopCell'))
        result = self.run_pattern(init_kore, depth=depth)

        return result

    def apr_proof_from_kast(
        self, id: str, kmir_kast: KInner, sort: str = 'GeneratedTopCell', proof_dir: Path | None = None
    ) -> APRProof:
        config = self.make_init_config(kmir_kast, 'main', sort=sort)
        config_with_cell_vars, _ = split_config_from(config)

        lhs = CTerm(config)

        rhs_subst = Subst({'K_CELL': KMIR.Symbols.END_PROGRAM})
        rhs = CTerm(rhs_subst(config_with_cell_vars))
        kcfg = KCFG()
        init_node = kcfg.create_node(lhs)
        target_node = kcfg.create_node(rhs)
        return APRProof(id, kcfg, [], init_node.id, target_node.id, {}, proof_dir=proof_dir)

    def prove_rs(self, opts: ProveRSOpts) -> APRProof:
        if not opts.rs_file.is_file():
            raise ValueError(f'Rust spec file does not exist: {opts.rs_file}')

        label = str(opts.rs_file.stem)
        if not opts.reload and opts.proof_dir is not None and APRProof.proof_data_exists(label, opts.proof_dir):
            _LOGGER.info(f'Reading proof from disc: {opts.proof_dir}, {label}')
            apr_proof = APRProof.read_proof_data(opts.proof_dir, label)
        else:
            _LOGGER.info(f'Constructing initial proof: {label}')
            smir_json = cargo_get_smir_json(opts.rs_file, save_smir=opts.save_smir)
            parser = Parser(self.definition)
            parse_result = parser.parse_mir_json(smir_json, 'Pgm')
            assert parse_result is not None
            kmir_kast, _ = parse_result
            assert isinstance(kmir_kast, KInner)
            apr_proof = self.apr_proof_from_kast(label, kmir_kast, proof_dir=opts.proof_dir)
        if apr_proof.passed:
            return apr_proof
        with self.kcfg_explore(label) as kcfg_explore:
            prover = APRProver(kcfg_explore, execute_depth=opts.max_depth)
            prover.advance_proof(apr_proof, max_iterations=opts.max_iterations)
            return apr_proof


class KMIRSemantics(DefaultSemantics):
    def is_terminal(self, cterm: CTerm) -> bool:
        k_cell = cterm.cell('K_CELL')
        # <k> #EndProgram </k>
        if k_cell == KMIR.Symbols.END_PROGRAM:
            return True
        elif type(k_cell) is KSequence:
            # <k> #EndProgram ~> .K </k>
            if k_cell.arity == 1 and k_cell[0] == KMIR.Symbols.END_PROGRAM:
                return True
        return False


class KMIRNodePrinter(NodePrinter):
    kmir: KMIR

    def __init__(self, kmir: KMIR, full_printer: bool = False) -> None:
        NodePrinter.__init__(self, kmir, full_printer=full_printer)
        self.kmir = kmir


class KMIRAPRNodePrinter(KMIRNodePrinter, APRProofNodePrinter):
    def __init__(self, kmir: KMIR, proof: APRProof, full_printer: bool = False) -> None:
        KMIRNodePrinter.__init__(self, kmir, full_printer=full_printer)
        APRProofNodePrinter.__init__(self, proof, kmir, full_printer=full_printer)

    def _span(self, node: KCFG.Node) -> int | None:
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
        return curr_span

    def print_node(self, kcfg: KCFG, node: KCFG.Node) -> list[str]:
        ret_strs = super().print_node(kcfg, node)
        ret_strs.append(self.kmir.pretty_print(node.cterm.cell('K_CELL'))[0:80])
        curr_span = self._span(node)
        if curr_span is not None:
            ret_strs.append(f'span: {curr_span}')
        curr_func_ty_kast = node.cterm.cell('CURRENTFUNC_CELL')
        if (
            type(curr_func_ty_kast) is KApply
            and curr_func_ty_kast.label.name == 'ty'
            and type(curr_func_ty_kast.args[0]) is KToken
            and curr_func_ty_kast.args[0].sort.name
        ):
            curr_func_ty = int(curr_func_ty_kast.args[0].token)
            ret_strs.append(f'func: {curr_func_ty}')
        return ret_strs
