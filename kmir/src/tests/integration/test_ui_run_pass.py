from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.options import ProveRSOpts

from .coverage_matrix import discover_suite_rs_files, integration_data_relative, load_coverage_matrix, suite_declared_entries

if TYPE_CHECKING:
    from kmir.kmir import KMIR


SUITE = 'ui-run-pass'
RS_FILES = discover_suite_rs_files(SUITE)
MATRIX = load_coverage_matrix()
TEST_SET, SKIP_SET = suite_declared_entries(MATRIX, SUITE)
DECLARED = TEST_SET | SKIP_SET
UNDECLARED = sorted(integration_data_relative(path) for path in RS_FILES if integration_data_relative(path) not in DECLARED)

pytestmark = [pytest.mark.external_suite]
if not RS_FILES:
    pytestmark.append(pytest.mark.skip(reason='No imported ui-run-pass suite found. Run `make fetch-test-suites`.'))


def test_ui_run_pass_suite_matrix_alignment() -> None:
    assert not UNDECLARED, f'Unmapped {SUITE} files in coverage-matrix.json: {UNDECLARED}'


@pytest.mark.parametrize('rs_file', RS_FILES, ids=[integration_data_relative(path) for path in RS_FILES])
def test_ui_run_pass(rs_file: Path, kmir: KMIR) -> None:
    rel = integration_data_relative(rs_file)
    if rel in SKIP_SET:
        pytest.skip('Skipped by coverage-matrix.json')

    proof = kmir.prove_rs(ProveRSOpts(rs_file, max_depth=200))
    assert proof.passed
