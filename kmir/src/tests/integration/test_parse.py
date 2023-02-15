from pathlib import Path

import pytest

from kmir import KMIR

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program(input_path)


COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))


@pytest.mark.parametrize(
    'input_path',
    COMPILETEST_FILES,
    ids=[str(f.relative_to(COMPILETEST_DIR)) for f in COMPILETEST_FILES],
)
def test_compiletest(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program(input_path)
