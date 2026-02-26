from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from kmir.options import ProveRSOpts

from .coverage_matrix import (
    adapted_kani_source,
    discover_suite_rs_files,
    external_kani_mode,
    external_max_depth,
    external_rustc_flags,
    integration_data_relative,
    kani_source_requires_runtime,
    load_coverage_matrix,
    run_all_external_enabled,
    suite_declared_entries,
)

if TYPE_CHECKING:
    from kmir.kmir import KMIR


SUITE = 'kani'
RS_FILES = discover_suite_rs_files(SUITE)
MATRIX = load_coverage_matrix()
TEST_SET, SKIP_SET = suite_declared_entries(MATRIX, SUITE)
MAX_DEPTH = external_max_depth(default=500)
KANI_MODE = external_kani_mode()
DECLARED = TEST_SET | SKIP_SET
UNDECLARED = sorted(integration_data_relative(path) for path in RS_FILES if integration_data_relative(path) not in DECLARED)

pytestmark = [pytest.mark.external_suite]
if not RS_FILES:
    pytestmark.append(pytest.mark.skip(reason='No imported Kani suite found. Run `make fetch-test-suites`.'))


def test_kani_suite_matrix_alignment() -> None:
    assert not UNDECLARED, f'Unmapped {SUITE} files in coverage-matrix.json: {UNDECLARED}'


@pytest.mark.parametrize('rs_file', RS_FILES, ids=[integration_data_relative(path) for path in RS_FILES])
def test_kani(rs_file: Path, kmir: KMIR, tmp_path: Path) -> None:
    rel = integration_data_relative(rs_file)
    if rel in SKIP_SET and not run_all_external_enabled():
        pytest.skip('Skipped by coverage-matrix.json')

    if KANI_MODE == 'deferred':
        pytest.skip('Kani suite is deferred by default (set KMIR_KANI_MODE=adapted to run adapted subset).')

    rustc_flags = external_rustc_flags(rs_file)
    source = rs_file
    if KANI_MODE == 'adapted':
        adapted = adapted_kani_source(rs_file)
        if kani_source_requires_runtime(adapted):
            pytest.skip('Adapted Kani mode only runs cases that do not require kani::* runtime API.')
        source = tmp_path / f'{rs_file.stem}.adapted.rs'
        source.write_text(adapted)

    proof = kmir.prove_rs(ProveRSOpts(source, max_depth=MAX_DEPTH, rustc_flags=rustc_flags))
    assert proof.passed
