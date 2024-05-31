import logging
from typing import Final

from pyk.cterm import CTerm
from pyk.kast.inner import KApply, KInner, KSequence, KVariable

# from pyk.kcfg import KCFGExplore  # kcfg.__init__, import Semantics
from pyk.kcfg.kcfg import KCFGExtendResult
from pyk.kcfg.semantics import KCFGSemantics
from pyk.prelude.k import K

_LOGGER: Final = logging.getLogger(__name__)
_LOG_FORMAT: Final = '%(levelname)s %(asctime)s %(name)s - %(message)s'


class KMIRSemantics(KCFGSemantics):
    def is_terminal(self, cterm: CTerm) -> bool:
        k_cell = cterm.cell('K_CELL')
        # <k> #halt </k>
        if k_cell == halt():
            return True
        elif type(k_cell) is KSequence:
            # <k> . </k>
            if k_cell.arity == 0:
                return True
            # <k> #halt </k>
            elif k_cell.arity == 1 and k_cell[0] == halt():
                return True
            elif k_cell.arity == 2 and k_cell[0] == halt() and type(k_cell[1]) is KVariable and k_cell[1].sort == K:
                return True
        return False

    @staticmethod
    def terminal_rules() -> list[str]:
        terminal_rules = ['MIR.halt']

        # TODO: break every step and add to terminal rules. Semantics does not support this currently
        return terminal_rules

    @staticmethod
    def cut_point_rules() -> list[str]:
        return []

    def extract_branches(self, cterm: CTerm) -> list[KInner]:
        return []

    def same_loop(self, cterm1: CTerm, cterm2: CTerm) -> bool:
        return False

    def custom_step(self, c: CTerm) -> KCFGExtendResult | None:
        return None

    def abstract_node(self, cterm: CTerm) -> CTerm:
        return cterm


# @staticmethod
def halt() -> KApply:
    return KApply('#halt_MIR_KItem')
