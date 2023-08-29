import logging
import os
import sys

import pytest

from kmir.__main__ import exec_prove

from ..utils import REPO_ROOT

from pathlib import Path
from typing import Final

from pytest import LogCaptureFixture

sys.setrecursionlimit(10**8)

# -------------------
# Test specifications
# -------------------

TEST_DIR: Final = REPO_ROOT / 'kmir/src/tests'
SYMBOLIC_TEST_DIR: Final = TEST_DIR / 'integration/proofs'
INITIAL_SPECS: Final = SYMBOLIC_TEST_DIR / 'simple-spec.k'

ALL_TESTS: Final = [ INITIAL_SPECS ]

def exclude_list(exclude_file: Path) -> list[Path]:
    res = [REPO_ROOT / test_path for test_path in exclude_file.read_text().splitlines()]
    # assert res
    return res

SKIPPED_TESTS: Final = exclude_list(SYMBOLIC_TEST_DIR / 'symbolic-failing')


# ---------
# Pyk tests
# ---------

@pytest.mark.parametrize(
    'spec_file',
    ALL_TESTS,
    ids=[str(spec_file.relative_to(INITIAL_SPECS)) for spec_file in ALL_TESTS],
)
def test_pyk_prove(
    llvm_dir: Path,
    haskell_dir: Path,
    spec_file: Path,
    tmp_path: Path,
    caplog: LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    if spec_file in SKIPPED_TESTS:
        pytest.skip()

    # Given
    log_file = tmp_path / 'log.txt'
    use_directory = tmp_path / 'kprove'
    use_directory.mkdir()

    # When
    try:
        exec_prove(
            definition_dir=llvm_dir,
            haskell_dir=haskell_dir,
            spec_file=spec_file,
            save_directory=use_directory,
            smt_timeout=300,
            smt_retry_limit=10,
        )
    except BaseException:
        raise
    finally:
        log_file.write_text(caplog.text)