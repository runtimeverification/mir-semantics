from pathlib import Path


def test_llvm(llvm_dir: Path) -> None:
    assert llvm_dir.is_dir()


def test_haskell(haskell_dir: Path) -> None:
    assert haskell_dir.is_dir()
