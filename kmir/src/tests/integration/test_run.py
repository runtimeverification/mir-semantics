import json
from pathlib import Path
from typing import Optional
import re

import pytest
from pyk.ktool.krun import KRunOutput
from pyk.kore.parser import KoreParser

from kmir import KMIR

from .utils import COMPILETEST_EXCLUDE, COMPILETEST_TEST_DATA, TEST_DATA_DIR, HANDWRITTEN_TEST_DATA

COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail.json'
COMPILETEST_RUN_FAIL = set(
    test['file'] for test in json.loads('[' + COMPILETEST_RUN_FAIL_FILE.read_text().rstrip('\n').rstrip(',') + ']')
)

COMPILETEST_RUN_EXCLUDE = {
    # macos only
    'backtrace-apple-no-dsymutil.mir',
    # requires special compilation
    'codegen/init-large-type.mir',
    'macros/macro-with-attrs1.mir',
    'macros/syntax-extension-cfg.mir',
    'mir/mir_overflow_off.mir',
    'numbers-arithmetic/next-power-of-two-overflow-ndebug.mir',
    'panic-runtime/abort.mir',
    'test-attrs/test-vs-cfg-test.mir',
    'codegen/issue-28950.mir',
    # takes too long
    'iterators/iter-count-overflow-debug.mir',
    'iterators/iter-count-overflow-ndebug.mir',
    'iterators/iter-position-overflow-debug.mir',
    'iterators/iter-position-overflow-ndebug.mir',
    # requires special run flags
    'test-attrs/test-filter-multiple.mir',
    # requires environment variables when running
    'exec-env.mir',
    # scanner error
    'new-unicode-escapes.mir',
    'multibyte.mir',
}


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    HANDWRITTEN_TEST_DATA,
    ids=[test_id for test_id, *_ in HANDWRITTEN_TEST_DATA],
)
def test_handwritten(kmir: KMIR, test_id: str, input_path: Path, tmp_path: Path, report_file: Optional[Path]) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Write to JSON report file if return code is non-zero
    """

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    run_result = kmir.run_program(input_path, output=KRunOutput.PRETTY, check=False, temp_file=temp_file)
    if report_file and run_result.returncode:
        k_cell = re.search(r'<k>(.*)</k>', run_result.stdout.replace('\n', ''))
        with report_file.open('a') as f:
            f.write(
                json.dumps(
                    {
                        'file': str(input_path.relative_to(TEST_DATA_DIR)),
                        'returncode': run_result.returncode,
                        'kcell': k_cell.group() if k_cell else None,
                    },
                    indent=2,
                )
            )
            f.write(',\n')
    assert not run_result.returncode


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
    if allow_skip and (
        test_id in COMPILETEST_EXCLUDE or test_id in COMPILETEST_RUN_EXCLUDE or test_id in COMPILETEST_RUN_FAIL
    ):
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # Then
    run_result = kmir.run_program(input_path, output=KRunOutput.PRETTY, check=False, temp_file=temp_file)
    if report_file and run_result.returncode:
        k_cell = re.search(r'<k>(.*)</k>', run_result.stdout.replace('\n', ''))
        with report_file.open('a') as f:
            f.write(
                json.dumps(
                    {
                        'file': str(input_path.relative_to(TEST_DATA_DIR)),
                        'returncode': run_result.returncode,
                        'kcell': k_cell.group() if k_cell else None,
                    },
                    indent=2,
                )
            )
            f.write(',\n')
    assert not run_result.returncode
