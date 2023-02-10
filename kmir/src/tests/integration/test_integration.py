import subprocess
from pathlib import Path

import pytest



HANDWRITTEN_SYNTAX_DIR = Path('src') / 'tests' / 'integration' / 'test-data' / 'parsing' / 'handwritten-syntax'


def test_llvm(llvm_dir: Path) -> None:
    assert llvm_dir.is_dir()


def test_haskell(haskell_dir: Path) -> None:
    assert haskell_dir.is_dir()


def kast(definition_dir: Path, input_name: Path) -> None:
    args = ['kast', '--output', 'kore', '--sort', 'Mir', '--definition', str(definition_dir), str(input_name)]
    result = subprocess.run(args)
    if result.returncode != 0:
        raise Exception('%s returned %d' % (args, result.returncode))


@pytest.mark.parametrize('input_path', list(HANDWRITTEN_SYNTAX_DIR.glob('*.mir')))
def test_handwritten_syntax(haskell_dir: Path, input_path: Path) -> None:
    definition_dir = haskell_dir

    kast(definition_dir, input_path)
