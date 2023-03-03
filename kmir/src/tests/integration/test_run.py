from pathlib import Path

import pytest
from pyk.ktool.krun import KRunOutput

from kmir import KMIR

from .utils import COMPILETEST_EXCLUDE, COMPILETEST_TEST_DATA, TEST_DATA_DIR

COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail'
COMPILETEST_RUN_FAIL = set(COMPILETEST_RUN_FAIL_FILE.read_text().splitlines())

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
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(kmir: KMIR, test_id: str, input_path: Path, tmp_path: Path, allow_skip: bool) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Compare the output with the expected output
    """
    if allow_skip and (test_id in COMPILETEST_EXCLUDE or test_id in COMPILETEST_RUN_EXCLUDE):
        pytest.skip()

    if test_id in COMPILETEST_RUN_FAIL:
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # TODO uncomment these lines when the semantics is implemented
    # stdout_file = input_path.parent / (input_path.stem + '.run.stdout')
    # stderr_file = input_path.parent / (input_path.stem + '.run.stderr')
    # expected_stdout = stdout_file.read_text() if stdout_file.exists() else ''
    # expected_stderr = stderr_file.read_text() if stderr_file.exists() else ''

    # Then
    if test_id not in COMPILETEST_RUN_FAIL:
        run_result = kmir.run_program(input_path, output=KRunOutput.NONE, check=False, temp_file=temp_file)
        assert not run_result.returncode
        # TODO uncomment these lines when the semantics is implemented
        # assert run_result.stdout == expected_stdout
        # assert run_result.stderr == expected_stderr

    # elif test_id in COMPILETEST_RUN_FAIL:
    #    assert run_result.returncode
