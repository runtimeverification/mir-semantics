from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.options import ProveRSOpts

from .coverage_matrix import (
    discover_suite_rs_files,
    external_max_depth,
    external_rustc_flags,
    integration_data_relative,
    load_coverage_matrix,
    run_all_external_enabled,
    suite_declared_entries,
)

if TYPE_CHECKING:
    from kmir.kmir import KMIR


SUITE = 'rustlantis'
RS_FILES = discover_suite_rs_files(SUITE)
MATRIX = load_coverage_matrix()
TEST_SET, SKIP_SET = suite_declared_entries(MATRIX, SUITE)
MAX_DEPTH = external_max_depth(default=500)
DECLARED = TEST_SET | SKIP_SET
UNDECLARED = sorted(integration_data_relative(path) for path in RS_FILES if integration_data_relative(path) not in DECLARED)

pytestmark = [pytest.mark.external_suite]
if not RS_FILES:
    pytestmark.append(
        pytest.mark.skip(reason='No generated Rustlantis corpus found. Run `scripts/generate-rustlantis.sh`.')
    )


def test_rustlantis_suite_matrix_alignment() -> None:
    assert not UNDECLARED, f'Unmapped {SUITE} files in coverage-matrix.json: {UNDECLARED}'


@pytest.mark.parametrize('rs_file', RS_FILES, ids=[integration_data_relative(path) for path in RS_FILES])
def test_rustlantis(rs_file: Path, kmir: KMIR) -> None:
    rel = integration_data_relative(rs_file)
    if rel in SKIP_SET and not run_all_external_enabled():
        pytest.skip('Skipped by coverage-matrix.json')

    rustc_flags = external_rustc_flags(rs_file)
    proof = kmir.prove_rs(ProveRSOpts(rs_file, max_depth=MAX_DEPTH, rustc_flags=rustc_flags))
    assert proof.passed
