from pathlib import Path
from typing import Optional

import pytest
from filelock import FileLock
from pyk.ktool.kprint import KAstInput, KAstOutput

from kmir import KMIR

from .utils import (
    COMPILETEST_PARSE_FAIL,
    COMPILETEST_TEST_DATA,
    HANDWRITTEN_PARSE_FAIL,
    HANDWRITTEN_PARSE_TEST_DATA,
    TEST_DATA_DIR,
)


@pytest.mark.parametrize(
    ('test_id', 'input_path'), 
    HANDWRITTEN_PARSE_TEST_DATA, 
    ids=[test_id for test_id, *_ in HANDWRITTEN_PARSE_TEST_DATA]
)
def test_handwritten_syntax(
    kmir: KMIR, test_id: str, input_path: Path, tmp_path: Path, allow_skip: bool, report_file: Optional[Path]
) -> None:
    if allow_skip and test_id in HANDWRITTEN_PARSE_FAIL:
        pytest.skip()

        # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    try:
        parse_result = kmir.parse_program_raw(
            input_path, temp_file=temp_file, input=KAstInput.PROGRAM, output=KAstOutput.KORE
        )
        assert not parse_result.returncode
    except ValueError:
        if report_file:
            lock = FileLock(f'{report_file.name}.lock')
            with lock:
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
    if allow_skip and test_id in COMPILETEST_PARSE_FAIL:
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    try:
        parse_result = kmir.parse_program_raw(
            input_path, temp_file=temp_file, input=KAstInput.PROGRAM, output=KAstOutput.KORE
        )
        assert not parse_result.returncode
    except ValueError:
        if report_file:
            lock = FileLock(f'{report_file.name}.lock')
            with lock:
                with report_file.open('a') as f:
                    f.write(f'{input_path.relative_to(TEST_DATA_DIR)}\t{1}\n')
        raise
