from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from pyk.cli.utils import bug_report_arg
from pyk.cterm import cterm_symbolic
from pyk.kast.inner import KApply, KSequence
from pyk.kcfg.explore import KCFGExplore
from pyk.kcfg.semantics import DefaultSemantics
from pyk.kcfg.show import NodePrinter
from pyk.ktool.kprove import KProve
from pyk.ktool.krun import KRun
from pyk.proof.show import APRProofNodePrinter

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from typing import Final

    from pyk.cterm import CTerm
    from pyk.proof.reachability import APRProof
    from pyk.utils import BugReport


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
