from pathlib import Path

import pytest

from kmir import KMIR

from .utils import COMPILETEST_EXCLUDE, COMPILETEST_TEST_DATA, TEST_DATA_DIR

COMPILETEST_RUN_PASS_FILE = TEST_DATA_DIR / 'compiletest-run-pass'
COMPILETEST_RUN_PASS = set(COMPILETEST_RUN_PASS_FILE.read_text().splitlines())
COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail'
COMPILETEST_RUN_FAIL = set(COMPILETEST_RUN_FAIL_FILE.read_text().splitlines())


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(kmir: KMIR, test_id: str, input_path: Path, allow_skip: bool) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Compare the output with the expected output
    """
    if allow_skip and test_id in COMPILETEST_EXCLUDE:
        pytest.skip()

    # Given
    stdout_file = input_path.parent / (input_path.stem + '.run.stdout')
    stderr_file = input_path.parent / (input_path.stem + '.run.stderr')
    expected_stdout = stdout_file.read_text() if stdout_file.exists() else ''
    expected_stderr = stderr_file.read_text() if stderr_file.exists() else ''

    # Then
    if input_path in COMPILETEST_RUN_PASS:
        run_result = kmir.run_program(input_path, check=False)
        assert not run_result.returncode
        assert run_result.stdout == expected_stdout
        assert run_result.stderr == expected_stderr

    # elif input_path in COMPILETEST_RUN_FAIL:
    #    assert run_result.returncode


