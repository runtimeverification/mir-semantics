from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.options import ProveRSOpts

from .coverage_matrix import (
    external_rustc_flags,
    integration_data_relative,
    run_all_external_enabled,
    setup_external_suite,
)

if TYPE_CHECKING:
    from kmir.kmir import KMIR

SUITE = 'rustlantis'
RS_FILES, TEST_SET, SKIP_SET, MAX_DEPTH, UNDECLARED, pytestmark = setup_external_suite(
    SUITE, 'No generated Rustlantis corpus found. Run `scripts/generate-rustlantis.sh`.'
)


def test_rustlantis_suite_matrix_alignment() -> None:
    assert not UNDECLARED, f'Unmapped {SUITE} files in coverage-matrix.json: {UNDECLARED}'


@pytest.mark.parametrize('rs_file', RS_FILES, ids=[integration_data_relative(p) for p in RS_FILES])
def test_rustlantis(rs_file: Path, kmir: KMIR) -> None:
    rel = integration_data_relative(rs_file)
    if rel in SKIP_SET and not run_all_external_enabled():
        pytest.skip('Skipped by coverage-matrix.json')

    rustc_flags = external_rustc_flags(rs_file)
    proof = kmir.prove_rs(ProveRSOpts(rs_file, max_depth=MAX_DEPTH, rustc_flags=rustc_flags))
    assert proof.passed
