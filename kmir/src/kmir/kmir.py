from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

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


class KMIR(KProve, KRun):
    llvm_library_dir: Path | None

    def __init__(self, definition_dir: Path, llvm_library_dir: Path | None = None) -> None:
        KProve.__init__(self, definition_dir)
        KRun.__init__(self, definition_dir)
        self.llvm_library_dir = llvm_library_dir

    class Symbols:
        END_PROGRAM: Final = KApply('#EndProgram_KMIR_KItem')

    @contextmanager
    def _explore(self) -> Iterator[KCFGExplore]:
        with cterm_symbolic(self.definition, self.definition_dir, llvm_definition_dir=self.llvm_library_dir) as cts:
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
