from pathlib import Path

import pyk.ktool.kprint as kprint
import pytest
from pyk.ktool.kprint import KAstInput, KAstOutput

HANDWRITTEN_SYNTAX_DIR = Path(__file__).parent / 'test-data' / 'parsing' / 'handwritten-syntax'
HANDWRITTEN_SYNTAX_FILES = list(HANDWRITTEN_SYNTAX_DIR.glob('*.mir'))


def test_llvm(llvm_dir: Path) -> None:
    assert llvm_dir.is_dir()


def test_haskell(haskell_dir: Path) -> None:
    assert haskell_dir.is_dir()


@pytest.mark.parametrize('input_path', HANDWRITTEN_SYNTAX_FILES, ids=[str(f.name) for f in HANDWRITTEN_SYNTAX_FILES])
def test_handwritten_syntax(haskell_dir: Path, input_path: Path) -> None:
    pass

    kprint._kast(
        definition_dir=haskell_dir, input_file=input_path, input=KAstInput.PROGRAM, output=KAstOutput.KORE, sort='Mir'
    )
