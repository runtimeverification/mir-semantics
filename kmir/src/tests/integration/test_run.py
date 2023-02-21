from pathlib import Path

import pytest
from pyk.cli_utils import run_process

from kmir import KMIR

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines())
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)

COMPILETEST_RUN_PASS_FILE = TEST_DATA_DIR / 'compiletest-run-pass'
COMPILETEST_RUN_PASS = set(COMPILETEST_RUN_PASS_FILE.read_text().splitlines())
COMPILETEST_RUN_FAIL_FILE = TEST_DATA_DIR / 'compiletest-run-fail'
COMPILETEST_RUN_FAIL = set(COMPILETEST_RUN_FAIL_FILE.read_text().splitlines())


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(kmir: KMIR, test_id: str, input_path: Path) -> None:
    """
    1. Execute the program and grab the output in stdout and stderr
    2. Check the return code w.r.t. run-pass/run-fail condition
    3. Compare the output with the expected output
    """
    if test_id in COMPILETEST_EXCLUDE:
        pytest.skip()

    run_result = kmir.run_program(input_path, check=False)

    if input_path in COMPILETEST_RUN_PASS:
        assert not run_result.returncode
    elif input_path in COMPILETEST_RUN_FAIL:
        assert run_result.returncode

    stdout_path = input_path.parent / (input_path.stem + '.run.stdout')
    check_result('stdout', stdout_path, run_result.stdout)

    stderr_path = input_path.parent / (input_path.stem + '.run.stderr')
    check_result('stderr', stderr_path, run_result.stderr)


def check_result(name: str, expected_path: Path, result: bytes) -> None:
    """
    Compare 'result' and the file at 'expexted_path' using diff
    """
    if not expected_path.is_file():
        assert not result, f 'Unexpected output in {name}'
        return

    diff_args = ['diff', str(expected_path), '-']
    diff_result = run_process(diff_args, input=str(result), check=False)

    if diff_result.returncode:
        raise ValueError(f'Invalid output in {name}:\n{diff_result.stdout}')
