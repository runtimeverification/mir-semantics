import logging
import sys
from pathlib import Path
from typing import Final

import pytest
from pytest import LogCaptureFixture

from kmir.__main__ import exec_prove

from .utils import (
    PROVE_TEST_DATA,
    PROVE_FAIL,
)

sys.setrecursionlimit(10**8)

@pytest.mark.parametrize(
    ('test_id', 'spec_file'),
    PROVE_TEST_DATA,
    ids=[test_id for test_id, *_ in PROVE_TEST_DATA],
)
def test_handwritten(
    llvm_dir: str,
    haskell_dir: str,
    test_id: str,
    spec_file: Path,
    tmp_path: Path,
    caplog: LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)

    if test_id in PROVE_FAIL:
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
            spec_file=str(spec_file),
            save_directory=use_directory,
            smt_timeout=300,
            smt_retry_limit=10,
        )
    except BaseException:
        raise
    finally:
        log_file.write_text(caplog.text)
