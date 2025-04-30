from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyk.cterm import CTerm
from pyk.kast.inner import KInner, Subst
from pyk.kast.manip import split_config_from
from pyk.kcfg import KCFG
from pyk.proof.reachability import APRProof, APRProver

from kmir.kmir import KMIR
from kmir.parse.parser import Parser
from kmir.rust.cargo import cargo_get_smir_json

if TYPE_CHECKING:
    from kmir.tools import Tools


PROVING_DIR = (Path(__file__).parent / 'data' / 'prove-rs').resolve(strict=True)
PROVING_FILES = list(PROVING_DIR.glob('*.rs'))


@pytest.mark.parametrize(
    'rs_file',
    PROVING_FILES,
    ids=[spec.stem for spec in PROVING_FILES],
)
def test_prove_rs(rs_file: Path, tmp_path: Path, kmir: KMIR, tools: Tools) -> None:
    should_fail = rs_file.stem.endswith('fail')
    smir_json = cargo_get_smir_json(rs_file)

    parser = Parser(kmir.definition)
    parse_result = parser.parse_mir_json(smir_json, 'Pgm')
    assert parse_result is not None
    kmir_kast, _ = parse_result
    assert isinstance(kmir_kast, KInner)

    config = tools.make_init_config(kmir_kast, 'main')
    config_with_cell_vars, _ = split_config_from(config)

    lhs = CTerm(config)

    rhs_subst = Subst({'K_CELL': KMIR.Symbols.END_PROGRAM})
    rhs = CTerm(rhs_subst(config_with_cell_vars))
    kcfg = KCFG()
    init_node = kcfg.create_node(lhs)
    target_node = kcfg.create_node(rhs)
    apr_proof = APRProof('PROOF', kcfg, [], init_node.id, target_node.id, {})
    with kmir.kcfg_explore('PROOF-TEST') as kcfg_explore:
        prover = APRProver(kcfg_explore)
        prover.advance_proof(apr_proof)
        if not should_fail:
            assert apr_proof.passed
        else:
            assert apr_proof.failed
