from pathlib import Path

import pytest

from kmir import KMIR

HANDWRITTEN_SYNTAX_DIR = Path(__file__).parent / 'test-data' / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = list(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(kmir: KMIR, input_path: Path) -> None:
    kmir.parse_program(input_path)
