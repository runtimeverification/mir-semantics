from pathlib import Path
from typing import Optional

import pytest
from filelock import FileLock

from kmir import KMIR, run

from .utils import (
    COMPILETEST_RUN_FAIL,
    COMPILETEST_TEST_DATA,
    HANDWRITTEN_RUN_FAIL,
    HANDWRITTEN_RUN_TEST_DATA,
    TEST_DATA_DIR,
)

@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    HANDWRITTEN_RUN_TEST_DATA,
    ids=[test_id for test_id, *_ in HANDWRITTEN_RUN_TEST_DATA],
)
def test_handwritten(
    kmir: KMIR, test_id: str, input_path: Path, tmp_path: Path, allow_skip: bool, report_file: Optional[Path]
) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Write to JSON report file if return code is non-zero
    """
    if allow_skip and (test_id in HANDWRITTEN_RUN_FAIL):
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    try:
        run(kmir, input_path, depth=None, output='none', temp_file=temp_file)
    except RuntimeError:
        if report_file:
            with FileLock(f'{report_file.name}.lock', timeout=1):
                with report_file.open('a') as f:
                    f.write(f'{input_path.relative_to(TEST_DATA_DIR)}\t{1}\n')
        raise


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(
    kmir: KMIR, test_id: str, input_path: Path, tmp_path: Path, allow_skip: bool, report_file: Optional[Path]
) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Compare the output with the expected output
    """
    if allow_skip and test_id in COMPILETEST_RUN_FAIL:
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    try:
        run(kmir, input_path, temp_file=temp_file)
    except RuntimeError:
        if report_file:
            lock = FileLock(f'{report_file.name}.lock')
            with lock:
                with report_file.open('a') as f:
                    f.write(f'{input_path.relative_to(TEST_DATA_DIR)}\t{1}\n')
        raise
    # assert not run_result.returncode
