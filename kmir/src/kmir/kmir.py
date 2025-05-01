from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import CTerm, cterm_symbolic
from pyk.kast.inner import KApply, KInner, KSequence, Subst
from pyk.kast.manip import split_config_from
from pyk.kcfg import KCFG
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.reachability import APRProof, APRProver
from pyk.proof.show import APRProofNodePrinter

from .parse.parser import Parser
from .rust.cargo import cargo_get_smir_json
from .tools import Tools

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Final

    from pyk.utils import BugReport

    from .options import ProveRSOpts


class KMIR(KProve, KRun):
    llvm_library_dir: Path | None
    bug_report: BugReport | None

    def __init__(
        self, definition_dir: Path, llvm_library_dir: Path | None = None, bug_report: Path | None = None
    ) -> None:
        self.bug_report = bug_report_arg(bug_report) if bug_report is not None else None
        KProve.__init__(self, definition_dir, bug_report=self.bug_report)
        KRun.__init__(self, definition_dir, bug_report=self.bug_report)
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

    def apr_proof_from_kast(self, id: str, kmir_kast: KInner, sort: str = 'GeneratedTopCell') -> APRProof:
        tools = Tools(self.definition_dir)
        config = tools.make_init_config(kmir_kast, 'main', sort=sort)
        config_with_cell_vars, _ = split_config_from(config)

        lhs = CTerm(config)

        rhs_subst = Subst({'K_CELL': KMIR.Symbols.END_PROGRAM})
        rhs = CTerm(rhs_subst(config_with_cell_vars))
        kcfg = KCFG()
        init_node = kcfg.create_node(lhs)
        target_node = kcfg.create_node(rhs)
        return APRProof(id, kcfg, [], init_node.id, target_node.id, {})

    def prove_rs(self, opts: ProveRSOpts) -> APRProof:
        if not opts.rs_file.is_file():
            raise ValueError(f'Rust spec file does not exist: {opts.rs_file}')

        smir_json = cargo_get_smir_json(opts.rs_file)
        parser = Parser(self.definition)
        parse_result = parser.parse_mir_json(smir_json, 'Pgm')
        assert parse_result is not None
        kmir_kast, _ = parse_result
        assert isinstance(kmir_kast, KInner)

        apr_proof = self.apr_proof_from_kast(str(opts.rs_file.stem), kmir_kast)
        with self.kcfg_explore('PROOF-TEST') as kcfg_explore:
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

    def __init__(self, kmir: KMIR) -> None:
        NodePrinter.__init__(self, kmir)
        self.kmir = kmir


class KMIRAPRNodePrinter(KMIRNodePrinter, APRProofNodePrinter):
    def __init__(self, kmir: KMIR, proof: APRProof) -> None:
        KMIRNodePrinter.__init__(self, kmir)
        APRProofNodePrinter.__init__(self, proof, kmir)
