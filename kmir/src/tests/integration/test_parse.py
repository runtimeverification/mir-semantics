from pathlib import Path

import pytest
from pyk.ktool.kprint import KAstInput, KAstOutput

from kmir import KMIR

from .utils import COMPILETEST_EXCLUDE, COMPILETEST_TEST_DATA, HANDWRITTEN_SYNTAX_FILES


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program_raw(input_path, input=KAstInput.PROGRAM, output=KAstOutput.KORE)


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(
    kmir: KMIR,
    test_id: str,
    input_path: Path,
    tmp_path: Path,
    allow_skip: bool,
) -> None:
    if allow_skip and test_id in COMPILETEST_EXCLUDE:
        pytest.skip()

    # Given
    temp_file = tmp_path / 'preprocessed.mir'

    # When
    kmir.parse_program_raw(input_path, temp_file=temp_file, input=KAstInput.PROGRAM, output=KAstOutput.KORE)
