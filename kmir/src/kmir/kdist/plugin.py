from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from pyk.kdist.api import Target
from pyk.ktool.kompile import LLVMKompileType, PykBackend, kompile

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from typing import Any, Final


class SourceTarget(Target):
    SRC_DIR: Final = Path(__file__).parent

    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        shutil.copytree(self.SRC_DIR / 'mir-semantics', output_dir / 'mir-semantics')

    def source(self) -> tuple[Path, ...]:
        return (self.SRC_DIR,)

    def deps(self) -> tuple[()]:
        return ()


class KompileTarget(Target):
    _kompile_args: Callable[[Path], Mapping[str, Any]]

    def __init__(self, kompile_args: Callable[[Path], Mapping[str, Any]]):
        self._kompile_args = kompile_args

    def build(self, output_dir: Path, deps: dict[str, Path], args: dict[str, Any], verbose: bool) -> None:
        kompile_args = self._kompile_args(deps['mir-semantics.source'])
        kompile(output_dir=output_dir, verbose=verbose, **kompile_args)

    def deps(self) -> tuple[str, ...]:
        return ('mir-semantics.source',)


def _default_args(src_dir: Path) -> dict[str, Any]:
    return {
        'include_dirs': [src_dir],
        'md_selector': 'k',
        'warnings_to_errors': True,
        'syntax_module': 'KMIR-SYNTAX',
    }


__TARGETS__: Final = {
    'source': SourceTarget(),
    'llvm': KompileTarget(
        lambda src_dir: {
            'main_file': src_dir / 'mir-semantics/kmir.k',
            'backend': PykBackend.LLVM,
            **_default_args(src_dir),
        },
    ),
    'llvm-library': KompileTarget(
        lambda src_dir: {
            'main_file': src_dir / 'mir-semantics/kmir.k',
            'backend': PykBackend.LLVM,
            'llvm_kompile_type': LLVMKompileType.C,
            **_default_args(src_dir),
        },
    ),
    'haskell': KompileTarget(
        lambda src_dir: {
            'main_file': src_dir / 'mir-semantics/kmir.k',
            'backend': PykBackend.HASKELL,
            **_default_args(src_dir),
        },
    ),
}
