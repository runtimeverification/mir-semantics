import logging
import re
from pathlib import Path
from typing import Callable, Final, TypeVar

from pyk.cterm import CTerm
from pyk.kast.manip import set_cell
from pyk.kast.outer import KApply, KClaim, KRewrite, KSequence

T1 = TypeVar('T1')
T2 = TypeVar('T2')

NodeIdLike = int | str

_LOGGER: Final = logging.getLogger(__name__)

ALLOC_REFERENCE = r'#\(-*alloc[0-9]+(?:\+0x[0-9a-fA-F]+)?-*\)#'
BYTE_VALUE = '[0-9a-fA-F][0-9a-fA-F]'
UNINITIALIZED_BYTE = '__'
ALLOC_ITEM = '|'.join([ALLOC_REFERENCE, BYTE_VALUE, UNINITIALIZED_BYTE])
ALLOC_VALUE = r'(\s*(?: (' + ALLOC_ITEM + '))+)'
ALLOC_SUFFIX = r'\s+│.*$'

HEX_CLEANUP_SUFFIX = re.compile(r'^' + ALLOC_VALUE + ALLOC_SUFFIX)
HEX_CLEANUP_SEPARATOR = re.compile(r'^(\s+0x[0-9a-fA-F]+\s+)│' + ALLOC_VALUE + ALLOC_SUFFIX)


def preprocess_mir_file(program_file: Path, temp_file: Path) -> None:
    def cleanup_hex_dump(line: str) -> str:
        line = line.replace('╾', '#(').replace('─', '-').replace('╼', ')#')
        m = HEX_CLEANUP_SUFFIX.match(line)
        if not m:
            m = HEX_CLEANUP_SEPARATOR.match(line)
            if not m:
                return line
            return '%s|%s' % (m.group(1), m.group(2))
        return m.group(1)

    def process_line(line: str) -> str:
        line = cleanup_hex_dump(line)
        return line

    def preprocess(program_text: str) -> str:
        return '\n'.join(process_line(line) for line in program_text.splitlines())

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
