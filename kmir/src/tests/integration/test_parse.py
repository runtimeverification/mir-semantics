import tempfile
from pathlib import Path

import pytest

from kmir import KMIR
from kmir.preprocessor import preprocess

TEST_DATA_DIR = Path(__file__).parent / 'test-data'


HANDWRITTEN_SYNTAX_DIR = TEST_DATA_DIR / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = tuple(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program(input_path)


COMPILETEST_DIR = TEST_DATA_DIR / 'compiletest-rs' / 'ui'
COMPILETEST_FILES = tuple(COMPILETEST_DIR.rglob('*.mir'))
COMPILETEST_EXCLUDE_FILE = TEST_DATA_DIR / 'compiletest-exclude'
COMPILETEST_EXCLUDE = set(COMPILETEST_EXCLUDE_FILE.read_text().splitlines())
COMPILETEST_TEST_DATA = tuple(
    (str(input_path.relative_to(COMPILETEST_DIR)), input_path) for input_path in COMPILETEST_FILES
)


@pytest.mark.parametrize(
    ('test_id', 'input_path'),
    COMPILETEST_TEST_DATA,
    ids=[test_id for test_id, *_ in COMPILETEST_TEST_DATA],
)
def test_compiletest(kmir: KMIR, test_id: str, input_path: Path) -> None:
    if test_id in COMPILETEST_EXCLUDE:
        pytest.skip()

    with tempfile.NamedTemporaryFile() as tmp:
        preprocess(str(input_path), tmp.name)
        kmir.parse_program(Path(tmp.name))
