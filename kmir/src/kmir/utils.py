import logging
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Final, TypeVar

from pyk.cterm import CTerm
from pyk.kast.inner import KInner, Subst
from pyk.kast.manip import set_cell
from pyk.kast.outer import KApply, KClaim, KRewrite, KSequence
from pyk.kcfg import KCFG, KCFGExplore

from .preprocessor import preprocess

T1 = TypeVar('T1')
T2 = TypeVar('T2')

NodeIdLike = int | str

_LOGGER: Final = logging.getLogger(__name__)


def preprocess_mir_file(program_file: Path, temp_file: Path) -> None:
    temp_file.write_text(preprocess(program_file.read_text()))


def is_functional(claim: KClaim) -> bool:
    claim_lhs = claim.body
    if type(claim_lhs) is KRewrite:
        claim_lhs = claim_lhs.lhs
    return not (type(claim_lhs) is KApply and claim_lhs.label.name == '<generatedTop>')


def ensure_ksequence_on_k_cell(cterm: CTerm) -> CTerm:
    k_cell = cterm.cell('K_CELL')
    if type(k_cell) is not KSequence:
        _LOGGER.info('Introducing artificial KSequence on <k> cell.')
        return CTerm.from_kast(set_cell(cterm.kast, 'K_CELL', KSequence([k_cell])))
    return cterm


def process_exception(err: Exception, curr_output: list[str], err_msg: str) -> None:
    curr_output.append(err_msg)
    print(err, flush=True, file=sys.stderr)
    print(traceback.format_exc(), flush=True, file=sys.stderr)


def print_model(node: KCFG.Node, kcfg_explore: KCFGExplore) -> list[str]:
    res_lines: list[str] = []
    result_subst = kcfg_explore.cterm_get_model(node.cterm)
    if type(result_subst) is Subst:
        res_lines.append('  Model:')
        for var, term in result_subst.to_dict().items():
            term_kast = KInner.from_dict(term)
            res_lines.append(f'    {var} = {kcfg_explore.kprint.pretty_print(term_kast)}')
    else:
        res_lines.append('  Failed to generate a model.')

    return res_lines


def node_id_like(s: str) -> NodeIdLike:
    try:
        return int(s)
    except ValueError:
        return s


def arg_pair_of(
    fst_type: Callable[[str], T1], snd_type: Callable[[str], T2], delim: str = ','
) -> Callable[[str], tuple[T1, T2]]:
    def parse(s: str) -> tuple[T1, T2]:
        elems = s.split(delim)
        length = len(elems)
        if length != 2:
            raise ValueError(f'Expected 2 elements, found {length}')
        return fst_type(elems[0]), snd_type(elems[1])

    return parse
